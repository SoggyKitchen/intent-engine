"""
Flag pages with risky factual claims (pricing, money-back guarantees,
refund policies, SLA / support claims) that have not been verified from
the vendor's own public page.

Why: the external audit flagged claims like "Asana offers a 30-day
money-back guarantee" without a visible source citation. These need a
human review pass before we trust them for production SEO. We do NOT
silently rewrite factual content — we mark the trust box verification
state so it's visible to both readers and our own CI pipeline, and we
dump a manual_review_queue.json for the editor.

Idempotent.
"""
from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site" / "pages"
OUT = ROOT / "outputs" / "seo" / "manual_review_queue.json"
OUT.parent.mkdir(parents=True, exist_ok=True)


# Patterns that trigger a manual-review flag. Each entry is (label, regex).
RISKY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "money_back_guarantee",
        re.compile(
            r"(?:\d+[- ]day |no[- ]questions[- ]asked |unconditional )?money[- ]back guarantee",
            re.IGNORECASE,
        ),
    ),
    (
        "refund_policy_numeric",
        re.compile(
            r"\d+[- ]day (?:refund|cash[- ]back|free return) policy",
            re.IGNORECASE,
        ),
    ),
    (
        "lifetime_free",
        re.compile(r"lifetime free(?: plan)?", re.IGNORECASE),
    ),
    (
        "unlimited_free_trial",
        re.compile(r"unlimited free trial", re.IGNORECASE),
    ),
    (
        "sla_guarantee",
        re.compile(r"\d{1,3}(?:\.\d+)?%\s*uptime(?: SLA)?(?: guarantee)?", re.IGNORECASE),
    ),
]


def body_of(html: str) -> str:
    """Rough body extractor — strips head so we don't flag meta tags."""
    m = re.search(r"<body[^>]*>([\s\S]*?)</body>", html, re.IGNORECASE)
    return m.group(1) if m else html


def find_claims(html: str) -> list[dict]:
    body = body_of(html)
    # Remove the trust box and journey blocks to avoid flagging our own
    # meta-level "refund policy" language inside notices.
    body = re.sub(r'<section[^>]*data-seo-trustbox[\s\S]*?</section>', "", body)
    body = re.sub(r'<section[^>]*data-saaspare-journey-links[\s\S]*?</section>', "", body)

    results: list[dict] = []
    for label, pattern in RISKY_PATTERNS:
        for m in pattern.finditer(body):
            # Capture a short context window around the claim.
            start = max(0, m.start() - 80)
            end = min(len(body), m.end() + 80)
            context = re.sub(r"\s+", " ", body[start:end]).strip()
            results.append({"label": label, "snippet": m.group(0), "context": context[:240]})
            if len(results) > 8:
                return results
    return results


FLAG_STATE = "risky_claim_needs_vendor_source"


def bump_trust_state(html: str) -> str:
    # Replace state attribute
    html = re.sub(
        r'(data-seo-trustbox[^>]*?data-verification-state=")[^"]*(")',
        rf'\1{FLAG_STATE}\2',
        html,
    )
    # Update visible label to match the new state
    html = re.sub(
        r"(<span data-verification-label>)[^<]*(</span>)",
        r"\1Contains pricing or refund claims not yet verified from the vendor&#x27;s public page\2",
        html,
    )
    return html


def process(path: Path, dry_run: bool) -> dict | None:
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw = path.read_text(encoding="utf-8", errors="replace")
    claims = find_claims(raw)
    if not claims:
        return None
    new_html = bump_trust_state(raw)
    if new_html == raw:
        # No trust box to bump; still record the page for manual review.
        return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "claims": claims, "trust_state_bumped": False}
    if not dry_run:
        path.write_text(new_html, encoding="utf-8", newline="")
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "claims": claims, "trust_state_bumped": True}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    flagged: list[dict] = []
    for p in SITE.glob("*.html"):
        r = process(p, dry_run=args.check)
        if r is not None:
            flagged.append(r)

    report = {
        "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "mode": "check" if args.check else "apply",
        "pages_flagged": len(flagged),
        "claim_labels_seen": sorted(
            {c["label"] for f in flagged for c in f["claims"]}
        ),
        "pages": flagged,
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"flagged={len(flagged)} mode={report['mode']} "
        f"report={OUT.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
