"""
Autonomous-operator auto-revert system.

The cloud operator ships on-page changes with no human in the loop. This is the
safety net that closes the loop: it remembers what each operator change looked
like before it shipped, waits ~21 days for Google to react, and ROLLS BACK any
change whose page lost a meaningful share of its clicks. A change that helps is
kept; a change that hurts is undone automatically.

Two phases:

  record    (run after apply-safe, before commit)
            For every site page the operator just modified, store a baseline:
            the page's current clicks + the pre-change file content (as a git
            blob sha). Appended to seo/snapshots/operator-baselines.json.

  evaluate  (run daily, before commit)
            For every baseline at least MAX_AGE_DAYS old, compare current
            clicks to the baseline. If clicks dropped by more than
            DROP_THRESHOLD on a page that had at least MIN_CLICKS to begin
            with, restore the pre-change content. Low-traffic pages and pages
            with no current data are left untouched (too noisy to judge).

Click data comes from seo/reports/gsc-page-clicks.json, which the daily SEO
agent writes from the GSC page-dimension pull. No live credentials are needed
here — this module only reads that file, so its decision logic is fully
testable offline.

Circuit breaker: if a single evaluate run would revert more than MAX_REVERTS
pages, something systemic is wrong (a bad GSC pull, a sitewide regression).
We abort WITHOUT reverting anything and exit non-zero for human review.

Exit codes:
  0  normal (reverted 0+ pages within budget)
  2  circuit breaker tripped — too many reverts, nothing changed, human review
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINES_PATH = ROOT / "seo" / "snapshots" / "operator-baselines.json"
PAGE_CLICKS_PATH = ROOT / "seo" / "reports" / "gsc-page-clicks.json"
SITE_BASE_URL = "https://saaspare.org"

# ── Thresholds (conservative on purpose — reverting live pages is heavy) ──────
MIN_CLICKS = 15.0       # ignore pages too small to judge from click noise
DROP_THRESHOLD = 0.10   # revert only if clicks fell >10% vs baseline
MAX_AGE_DAYS = 21       # wait for Google to react before judging
MAX_REVERTS = 25        # circuit breaker: more than this = systemic, abort

# Baseline status values
PENDING = "pending"
KEPT = "kept"
REVERTED = "reverted"
LOW_TRAFFIC = "skipped_low_traffic"
INCONCLUSIVE = "inconclusive"  # no current click data; re-check next run


# ── Pure helpers (no I/O — unit tested) ──────────────────────────────────────
def path_to_url(path: str, base: str = SITE_BASE_URL) -> str:
    """site/pages/foo.html -> https://saaspare.org/pages/foo"""
    p = path.replace("\\", "/")
    if p.startswith("site/"):
        p = p[len("site/"):]
    if p.endswith(".html"):
        p = p[: -len(".html")]
    if p.endswith("/index"):
        p = p[: -len("/index")]
    if p == "index":
        p = ""
    return f"{base.rstrip('/')}/{p}".rstrip("/")


def _url_variants(url: str) -> list[str]:
    u = url.rstrip("/")
    return [u, u + "/", u.replace("https://", "https://www."), u.replace("https://", "https://www.") + "/"]


def lookup_clicks(url: str, page_clicks: dict[str, float]) -> float | None:
    """Find a page's clicks, tolerating trailing-slash / www variants."""
    for candidate in _url_variants(url):
        if candidate in page_clicks:
            return float(page_clicks[candidate])
    return None


def _age_days(baseline_date: str, today: _dt.date) -> int:
    d = _dt.date.fromisoformat(baseline_date)
    return (today - d).days


def decide(
    baseline: dict,
    page_clicks: dict[str, float],
    today: _dt.date,
    *,
    min_clicks: float = MIN_CLICKS,
    drop_threshold: float = DROP_THRESHOLD,
    max_age_days: int = MAX_AGE_DAYS,
) -> dict:
    """Return a decision dict for one pending baseline. Does not mutate input.

    Keys: action in {"wait","revert","keep","low_traffic","inconclusive"},
    plus diagnostic numbers.
    """
    age = _age_days(baseline["baseline_date"], today)
    if age < max_age_days:
        return {"action": "wait", "age": age}

    baseline_clicks = float(baseline.get("baseline_clicks", 0) or 0)
    current = lookup_clicks(baseline["url"], page_clicks)

    if current is None:
        return {"action": "inconclusive", "age": age, "baseline_clicks": baseline_clicks}
    if baseline_clicks < min_clicks:
        return {"action": "low_traffic", "age": age, "baseline_clicks": baseline_clicks, "current_clicks": current}

    floor = baseline_clicks * (1.0 - drop_threshold)
    if current < floor:
        return {
            "action": "revert", "age": age,
            "baseline_clicks": baseline_clicks, "current_clicks": current,
            "drop_pct": round((baseline_clicks - current) / baseline_clicks * 100, 1),
        }
    return {
        "action": "keep", "age": age,
        "baseline_clicks": baseline_clicks, "current_clicks": current,
    }


def select_reverts(
    baselines: list[dict],
    page_clicks: dict[str, float],
    today: _dt.date,
    **thresholds,
) -> tuple[list[dict], list[dict]]:
    """Evaluate all PENDING baselines.

    Returns (decisions, updated_baselines). decisions is one dict per evaluated
    pending baseline (includes the baseline under "baseline"). updated_baselines
    is the full list with statuses updated for non-waiting decisions.
    """
    decisions: list[dict] = []
    updated = [dict(b) for b in baselines]
    by_id = {id(orig): upd for orig, upd in zip(baselines, updated)}

    for orig in baselines:
        if orig.get("status", PENDING) != PENDING:
            continue
        d = decide(orig, page_clicks, today, **thresholds)
        d = {**d, "baseline": orig}
        decisions.append(d)
        upd = by_id[id(orig)]
        if d["action"] == "revert":
            upd["status"] = REVERTED
        elif d["action"] == "keep":
            upd["status"] = KEPT
        elif d["action"] == "low_traffic":
            upd["status"] = LOW_TRAFFIC
        # "wait" and "inconclusive" stay PENDING for re-check next run
    return decisions, updated


# ── Git / file I/O (thin) ────────────────────────────────────────────────────
def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", errors="ignore",
    )


def head_blob_sha(path: str) -> str | None:
    """Blob sha of the file as it is in HEAD (its pre-change content)."""
    out = _git("rev-parse", f"HEAD:{path}")
    sha = (out.stdout or "").strip()
    return sha if out.returncode == 0 and sha else None


def blob_bytes(sha: str) -> bytes | None:
    out = subprocess.run(
        ["git", "cat-file", "blob", sha], cwd=ROOT, capture_output=True,
    )
    return out.stdout if out.returncode == 0 else None


def changed_site_pages() -> list[str]:
    """Site .html files modified in the working tree (unstaged + staged)."""
    out = _git("diff", "--name-only", "HEAD", "--", "site/")
    files = [ln.strip() for ln in (out.stdout or "").splitlines() if ln.strip().endswith(".html")]
    return sorted(set(files))


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def load_baselines() -> list[dict]:
    data = load_json(BASELINES_PATH, [])
    return data if isinstance(data, list) else []


def save_baselines(records: list[dict]) -> None:
    BASELINES_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINES_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")


def load_page_clicks() -> dict[str, float]:
    data = load_json(PAGE_CLICKS_PATH, {})
    if isinstance(data, dict):
        if data.get("skipped"):
            return {}
        pc = data.get("pageClicks", {})
        return {k: float(v) for k, v in pc.items()} if isinstance(pc, dict) else {}
    return {}


# ── Commands ─────────────────────────────────────────────────────────────────
def cmd_record(today: _dt.date) -> int:
    page_clicks = load_page_clicks()
    if not page_clicks:
        print("[autorevert/record] no GSC page-click data — skipping baseline capture.")
        return 0

    changed = changed_site_pages()
    if not changed:
        print("[autorevert/record] no site pages changed — nothing to baseline.")
        return 0

    baselines = load_baselines()
    pending_paths = {b["path"] for b in baselines if b.get("status") == PENDING}
    added = 0
    for path in changed:
        if path in pending_paths:
            continue  # already watching this page; don't double-baseline
        url = path_to_url(path)
        clicks = lookup_clicks(url, page_clicks)
        if clicks is None:
            continue  # page has no GSC footprint yet — nothing to protect
        pre_blob = head_blob_sha(path)
        if not pre_blob:
            continue  # brand-new file (no HEAD version to roll back to)
        baselines.append({
            "path": path,
            "url": url,
            "baseline_clicks": clicks,
            "baseline_date": today.isoformat(),
            "pre_blob": pre_blob,
            "status": PENDING,
        })
        added += 1

    save_baselines(baselines)
    print(f"[autorevert/record] captured {added} new baseline(s); {len(baselines)} total tracked.")
    return 0


def cmd_evaluate(today: _dt.date) -> int:
    baselines = load_baselines()
    page_clicks = load_page_clicks()
    if not page_clicks:
        print("[autorevert/evaluate] no GSC page-click data — cannot judge, no reverts.")
        return 0

    decisions, updated = select_reverts(baselines, page_clicks, today)
    to_revert = [d for d in decisions if d["action"] == "revert"]

    # Circuit breaker — a mass revert means something systemic, not 25 honest losers.
    if len(to_revert) > MAX_REVERTS:
        print(
            f"[autorevert/evaluate] ABORT — {len(to_revert)} pages would revert "
            f"(budget {MAX_REVERTS}). Likely a bad GSC pull or sitewide regression. "
            "Reverting nothing; human review required."
        )
        return 2

    reverted_ok = 0
    for d in to_revert:
        b = d["baseline"]
        content = blob_bytes(b["pre_blob"])
        if content is None:
            print(f"[autorevert/evaluate] WARN — lost pre-change blob for {b['path']}, leaving as-is.")
            # keep it pending so we notice next run
            for u in updated:
                if u["path"] == b["path"] and u.get("status") == REVERTED:
                    u["status"] = PENDING
            continue
        target = ROOT / b["path"]
        target.write_bytes(content)
        reverted_ok += 1
        print(f"[autorevert/evaluate] REVERTED {b['path']} "
              f"({b['url']}) — {d['baseline_clicks']:.0f} -> {d['current_clicks']:.0f} clicks "
              f"(-{d['drop_pct']}%)")

    save_baselines(updated)
    kept = sum(1 for d in decisions if d["action"] == "keep")
    waiting = sum(1 for d in decisions if d["action"] in ("wait", "inconclusive"))
    print(f"[autorevert/evaluate] reverted={reverted_ok} kept={kept} pending/inconclusive={waiting} "
          f"tracked={len(updated)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Autonomous-operator auto-revert")
    ap.add_argument("command", choices=["record", "evaluate"])
    args = ap.parse_args(argv)
    today = _dt.datetime.now(_dt.timezone.utc).date()
    if args.command == "record":
        return cmd_record(today)
    return cmd_evaluate(today)


if __name__ == "__main__":
    sys.exit(main())
