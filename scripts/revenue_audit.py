"""
Revenue Acceleration Audit
Audits every indexable page for monetization gaps, CRO weaknesses, and schema holes.
Outputs a prioritised opportunity report.

Run: uv run python scripts/revenue_audit.py
"""
from __future__ import annotations
import json, re, pathlib, sys
from collections import defaultdict

ROOT  = pathlib.Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
OUT   = ROOT / "outputs" / "revenue_audit.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

# ── Tracked affiliate programs (actually earn money per click) ────────────────
TRACKED_SLUGS = {
    "nordvpn", "nordvpn-kr", "nordpass", "surfshark", "surfshark-vpn",
    "sucuri", "sucuri-728x80", "contabo", "hostpapa",
    "semrush", "semrush-one", "semrush-seo", "semrush-trial",
    "shopify", "shopify-ecommerce", "shopify-plus", "shopify-store",
    "elevenlabs", "elevenlabs-ai", "elevenlabs-voice", "eleven-labs",
}

def get_tracked_links(html: str) -> int:
    """Count links to tracked affiliate programs."""
    links = re.findall(r'href="/go/([^"?]+)', html)
    return sum(1 for l in links if l.split("?")[0] in TRACKED_SLUGS)


def get_all_aff_links(html: str) -> int:
    return len(re.findall(r'href="/go/', html))


def has_schema(html: str, schema_type: str) -> bool:
    return f'"{schema_type}"' in html


def has_comparison_table(html: str) -> bool:
    return bool(re.search(r"<table", html, re.I))


def has_sticky_cta(html: str) -> bool:
    return "sticky-cta" in html or "sticky_cta" in html


def has_author_signal(html: str) -> bool:
    return "smith-elly" in html or "Smith Elly" in html


def has_exit_intent(html: str) -> bool:
    return "exit-intent" in html or "exit_intent" in html


def has_reading_progress(html: str) -> bool:
    return "progress-bar" in html or "reading-progress" in html


def has_social_proof(html: str) -> bool:
    return bool(re.search(r"(verified|reviews|rating|users|customers)", html, re.I))


def get_cta_count(html: str) -> int:
    """Count primary CTA buttons."""
    return len(re.findall(r'class="cta-btn|cta-primary|tbl-cta', html))


def text_length(html: str) -> int:
    return len(re.sub(r"<[^>]+>", " ", html).split())


def extract_title(html: str) -> str:
    m = re.search(r"<title>([^<]+)</title>", html, re.I)
    return m.group(1).strip()[:90] if m else "NO TITLE"


def page_type(fname: str) -> str:
    n = fname.lower()
    if "-vs-" in n:               return "vs"
    if "review" in n:             return "review"
    if "pricing" in n:            return "pricing"
    if "free-trial" in n:         return "free-trial"
    if "coupon" in n or "promo" in n: return "coupon"
    if "alternative" in n:        return "alternatives"
    if n.startswith("best-"):     return "best-hub"
    if "comparison" in n:         return "comparison"
    return "other"


# ── Audit every page ──────────────────────────────────────────────────────────

records = []
for f in sorted(PAGES.glob("*.html")):
    try:
        html = f.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue

    if 'content="noindex' in html or 'noindex, nofollow' in html:
        continue

    ptype = page_type(f.name)
    tracked = get_tracked_links(html)
    all_aff = get_all_aff_links(html)
    words = text_length(html)

    rec = {
        "file": f.name,
        "title": extract_title(html),
        "type": ptype,
        "tracked_aff": tracked,
        "all_aff": all_aff,
        "words": words,
        "has_faq": has_schema(html, "FAQPage"),
        "has_review_schema": has_schema(html, "Review"),
        "has_howto": has_schema(html, "HowTo"),
        "has_article": has_schema(html, "Article"),
        "has_itemlist": has_schema(html, "ItemList"),
        "has_table": has_comparison_table(html),
        "has_sticky": has_sticky_cta(html),
        "has_author": has_author_signal(html),
        "has_exit_intent": has_exit_intent(html),
        "has_progress": has_reading_progress(html),
        "has_social_proof": has_social_proof(html),
        "cta_count": get_cta_count(html),
    }

    # Scoring: issues found = revenue leaks
    issues = []
    score = 0  # higher = more urgent

    if ptype in ("review", "pricing", "free-trial", "coupon"):
        if tracked == 0 and all_aff == 0:
            issues.append("NO_AFFILIATE_LINKS")
            score += 50
        if tracked == 0 and all_aff > 0:
            issues.append("UNTRACKED_AFFILIATE_ONLY")
            score += 30
        if not rec["has_faq"]:
            issues.append("MISSING_FAQ_SCHEMA")
            score += 15
        if not rec["has_table"]:
            issues.append("MISSING_COMPARISON_TABLE")
            score += 10
        if not rec["has_sticky"]:
            issues.append("MISSING_STICKY_CTA")
            score += 20
        if not rec["has_author"]:
            issues.append("MISSING_AUTHOR_EEAT")
            score += 8
        if rec["cta_count"] < 2:
            issues.append("WEAK_CTA_DENSITY")
            score += 15
        if words < 400:
            issues.append("THIN_PAGE")
            score += 25

    elif ptype == "vs":
        if tracked == 0 and all_aff == 0:
            issues.append("NO_AFFILIATE_LINKS")
            score += 40
        if tracked == 0 and all_aff > 0:
            issues.append("UNTRACKED_AFFILIATE_ONLY")
            score += 20
        if not rec["has_faq"]:
            issues.append("MISSING_FAQ_SCHEMA")
            score += 12
        if not rec["has_table"]:
            issues.append("MISSING_COMPARISON_TABLE")
            score += 15
        if not rec["has_sticky"]:
            issues.append("MISSING_STICKY_CTA")
            score += 15
        if rec["cta_count"] < 1:
            issues.append("WEAK_CTA_DENSITY")
            score += 12
        if words < 300:
            issues.append("THIN_PAGE")
            score += 20

    elif ptype == "best-hub":
        if tracked == 0:
            issues.append("NO_TRACKED_AFFILIATE")
            score += 35
        if not rec["has_faq"]:
            issues.append("MISSING_FAQ_SCHEMA")
            score += 10
        if not rec["has_itemlist"]:
            issues.append("MISSING_ITEMLIST_SCHEMA")
            score += 12
        if not rec["has_sticky"]:
            issues.append("MISSING_STICKY_CTA")
            score += 12

    elif ptype == "alternatives":
        if tracked == 0 and all_aff == 0:
            issues.append("NO_AFFILIATE_LINKS")
            score += 30
        if not rec["has_faq"]:
            issues.append("MISSING_FAQ_SCHEMA")
            score += 10

    rec["issues"] = issues
    rec["priority_score"] = score
    records.append(rec)

# Sort by priority
records.sort(key=lambda r: r["priority_score"], reverse=True)

# ── Aggregate stats ───────────────────────────────────────────────────────────

total = len(records)
by_type = defaultdict(list)
for r in records:
    by_type[r["type"]].append(r)

issue_counts = defaultdict(int)
for r in records:
    for i in r["issues"]:
        issue_counts[i] += 1

# ── Print report ──────────────────────────────────────────────────────────────

print("=" * 70)
print("SAASPARE REVENUE ACCELERATION AUDIT")
print("=" * 70)
print()
print(f"Total indexable pages audited: {total}")
print()

print("── PAGE TYPE BREAKDOWN ──────────────────────────────────────")
for ptype, pages in sorted(by_type.items()):
    tracked_pct = sum(1 for p in pages if p["tracked_aff"] > 0)
    faq_pct = sum(1 for p in pages if p["has_faq"])
    sticky_pct = sum(1 for p in pages if p["has_sticky"])
    print(f"  {ptype:<15} {len(pages):4d} pages | tracked aff: {tracked_pct:3d} ({100*tracked_pct//len(pages):2d}%) | FAQ: {faq_pct:3d} | sticky CTA: {sticky_pct:3d}")

print()
print("── ISSUE FREQUENCY (revenue leaks) ─────────────────────────")
for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
    print(f"  {issue:<40} affects {count:4d} pages")

print()
print("── TOP 50 PRIORITY OPPORTUNITIES (by urgency score) ─────────")
print(f"  {'#':>3}  {'Score':>5}  {'Type':<15}  {'Issues':<45}  File")
print("  " + "-" * 110)
for i, r in enumerate(records[:50], 1):
    issues_str = ", ".join(r["issues"])[:45]
    fname = r["file"][:55]
    print(f"  {i:>3}.  [{r['priority_score']:>3}]  {r['type']:<15}  {issues_str:<45}  {fname}")

print()
print("── PAGES WITH UNTRACKED AFFILIATES (DIRECT URL LINKS) ───────")
untracked = [r for r in records if r["all_aff"] > 0 and r["tracked_aff"] == 0]
print(f"  Total: {len(untracked)} pages earning $0/click")
by_aff_count = sorted(untracked, key=lambda r: -r["all_aff"])
for r in by_aff_count[:20]:
    print(f"  [{r['all_aff']:3d} untracked links] {r['file'][:70]}")

print()
print("── REVIEW PAGES MISSING STICKY CTA ─────────────────────────")
review_no_sticky = [r for r in by_type.get("review", []) if not r["has_sticky"]]
print(f"  {len(review_no_sticky)} review pages missing sticky CTA")
for r in review_no_sticky[:10]:
    print(f"  {r['file'][:70]}")

print()
print("── VS PAGES MISSING COMPARISON TABLE ────────────────────────")
vs_no_table = [r for r in by_type.get("vs", []) if not r["has_table"]]
print(f"  {len(vs_no_table)} VS pages missing comparison table")
for r in vs_no_table[:10]:
    print(f"  {r['file'][:70]}")

# Save full JSON
OUT.write_text(json.dumps(records, indent=2))
print()
print(f"Full audit saved to: {OUT}")
