"""
The scoreboard for one goal: overtake saaspare.com on every measured axis.

Written because "we will dominate" is not a plan until it is a number you can
fail. Every run re-measures, prints PASS/FAIL per target, and refuses to call
the goal met while any target is outstanding.

Two tiers of metric:

  AUTOMATED  - measured from this repo and the live GSC export on every run.
               These are the leading indicators. They move first.
  MANUAL     - Search Atlas has no API on our plan, so DR / brand signal /
               competitor movement are typed into data/dominance_targets.json
               after each check. Stale entries are reported as stale, never
               silently carried forward as if fresh.

The headline metric is NON-BRANDED impressions. As of the 2026-09-01 baseline,
every single GSC impression we had came from the query "saaspare.org" - people
typing our domain. Non-branded impressions were zero, which is the honest
statement of the problem: we are not absent from page one, we are absent from
the index's topical understanding entirely.
"""
import json
import re
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
REPORTS = ROOT / "seo" / "reports"
TARGETS = ROOT / "data" / "dominance_targets.json"
OUT = REPORTS / "dominance.md"

BRAND_RE = re.compile(r"saas\s*pare", re.I)
STALE_DAYS = 21


def load(p, default=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def gsc_split():
    """Return (branded_impressions, nonbranded_impressions, nonbranded_queries)."""
    d = load(REPORTS / "gsc-opportunities.json", {})
    branded = nonbranded = 0.0
    nb_queries = set()
    for o in d.get("opportunities", []):
        q = (o.get("query") or "").strip()
        impr = float(o.get("impressions") or 0)
        if not q:
            continue          # anonymised/aggregate row, not attributable
        if BRAND_RE.search(q):
            branded += impr
        else:
            nonbranded += impr
            nb_queries.add(q)
    return branded, nonbranded, nb_queries, d.get("startDate"), d.get("endDate")


def site_facts():
    pages = list((SITE / "pages").glob("*.html"))
    indexable = 0
    for p in pages:
        if "noindex" not in p.read_text(encoding="utf-8", errors="replace"):
            indexable += 1

    sitemap = SITE / "sitemap.xml"
    sm = len(re.findall(r"<loc>", sitemap.read_text(encoding="utf-8", errors="replace"))) \
        if sitemap.exists() else 0

    same_as = set()
    for p in SITE.rglob("*.html"):
        for m in re.findall(r'"sameAs"\s*:\s*(\[[^\]]*\])',
                            p.read_text(encoding="utf-8", errors="replace")):
            same_as.add(m)

    return {
        "total_pages": len(pages),
        "indexable": indexable,
        "noindexed": len(pages) - indexable,
        "sitemap_urls": sm,
        "distinct_sameAs_arrays": len(same_as),
    }


def check(label, actual, target, cmp="ge", note=""):
    if actual is None:
        return {"label": label, "actual": "not measured", "target": target,
                "state": "UNKNOWN", "note": note}
    ok = actual >= target if cmp == "ge" else actual <= target
    return {"label": label, "actual": actual, "target": target,
            "state": "PASS" if ok else "FAIL", "note": note}


def main():
    t = load(TARGETS)
    comp, base, cur = t["competitor"], t["us_baseline"], t["us_current"]
    branded, nonbranded, nb_queries, d0, d1 = gsc_split()
    f = site_facts()

    auto = [
        check("Non-branded GSC impressions (28d)", nonbranded, 1,
              note="THE headline metric. Baseline was 0 - every impression was our own domain name."),
        check("Distinct non-branded queries", len(nb_queries), comp["organic_keywords"],
              note=f"beat saaspare.com's {comp['organic_keywords']} organic keywords"),
        check("Indexable pages >= competitor page count", f["indexable"], comp["indexed_pages_est"]),
        check("Entity consistency: one sameAs array", f["distinct_sameAs_arrays"], 1, cmp="le",
              note="conflicting identity claims break entity resolution"),
        check("Sitemap matches indexable set (+/-10%)",
              1 if abs(f["sitemap_urls"] - f["indexable"]) <= max(10, f["indexable"] * 0.1) else 0,
              1, note=f"sitemap {f['sitemap_urls']} vs indexable {f['indexable']}"),
    ]

    manual = [
        check("Organic keywords", cur["organic_keywords"], comp["organic_keywords"]),
        check("Organic traffic / mo", cur["organic_traffic"], comp["organic_traffic"]),
        check("Brand signal", cur["brand_signal"], comp["brand_signal"]),
        check("Spam score", cur["spam_score"], 2, cmp="le",
              note=f"baseline {base['spam_score']}, competitor {comp['spam_score']}"),
    ]

    stale = ""
    if cur.get("measured"):
        age = (date.today() - datetime.fromisoformat(cur["measured"]).date()).days
        if age > STALE_DAYS:
            stale = f"\n> **Manual numbers are {age} days old.** Re-measure in Search Atlas.\n"
    else:
        stale = "\n> **Manual numbers have never been recorded.** " \
                "Measure both domains in Search Atlas and fill `data/dominance_targets.json`.\n"

    rows = auto + manual
    outstanding = [r for r in rows if r["state"] != "PASS"]

    def table(items):
        out = ["| Metric | Now | Target | |", "|---|---|---|---|"]
        for r in items:
            icon = {"PASS": "PASS", "FAIL": "FAIL", "UNKNOWN": "?"}[r["state"]]
            out.append(f"| {r['label']} | {r['actual']} | {r['target']} | {icon} |")
            if r["note"]:
                out.append(f"| <sub>{r['note']}</sub> | | | |")
        return "\n".join(out)

    md = f"""# Dominance scoreboard — saaspare.org vs saaspare.com

Generated {date.today().isoformat()}. GSC window {d0} to {d1}.

**Goal:** beat saaspare.com on every axis below. Not "improve". Beat.
{stale}
## Automated (re-measured every run)

{table(auto)}

## Manual (Search Atlas, typed into data/dominance_targets.json)

{table(manual)}

## Where the traffic actually comes from

| Source | Impressions (28d) |
|---|---|
| Branded (`saaspare.org` typed as a query) | {branded:.0f} |
| **Non-branded (real topical demand)** | **{nonbranded:.0f}** |

Non-branded impressions are the whole game. Branded impressions only prove
that people who already know the domain can find it.

## Corpus

- Total pages: {f['total_pages']}
- Indexable: {f['indexable']}
- Noindexed (pruned {date.fromisoformat('2026-09-01').isoformat()}): {f['noindexed']}
- Sitemap URLs: {f['sitemap_urls']}
- Distinct `sameAs` arrays: {f['distinct_sameAs_arrays']}

## Verdict

**{len(outstanding)} of {len(rows)} targets outstanding.**
"""
    if outstanding:
        md += "\nNot done. Outstanding:\n\n"
        md += "\n".join(f"- {r['label']} — {r['actual']} vs target {r['target']}"
                        for r in outstanding)
        md += "\n"
    else:
        md += "\nEvery target met. Re-measure before declaring it.\n"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
