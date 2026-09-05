"""
Make SaaSpare resolve as ONE entity, everywhere, with only verifiable claims.

Three defects this repairs (audit 2026-09-06):

  1. Four conflicting `sameAs` arrays across 447 pages, whose primary entry
     (linkedin.com/company/saaspare) returns HTTP 404 and whose entries are
     simultaneously claimed by the competitor saaspare.com. Replaced with the
     verified-only array in scripts/seo/brand_identity.py.

  2. "1,000+ tools" copy. After the 2026-09-01 prune the site has 492
     indexable pages. The claim is no longer true, and an inflated corpus
     claim is exactly the signal a scaled-content demotion looks for.
     Rewritten from the live indexable count.

  3. A bare WebPage JSON-LD block on the homepage that names the site
     "SaaSpare" with no @id, competing with the @graph's WebSite/Organization
     nodes for the same identity. Given an @id so it joins the graph instead
     of contradicting it.

Idempotent. Safe to run as a final pass after the generators.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "seo"))
import brand_identity as BI  # noqa: E402

SITE = ROOT / "site"

SAME_AS_ANY = re.compile(r'"sameAs"\s*:\s*\[[^\]]*\]')
CANON = '"sameAs": ' + json.dumps(BI.ORG_SAME_AS)


def indexable_count() -> int:
    n = 0
    for p in (SITE / "pages").glob("*.html"):
        if "noindex" not in p.read_text(encoding="utf-8", errors="replace"):
            n += 1
    return n


def fix_same_as(html: str) -> str:
    # Only inside JSON-LD; sameAs does not legitimately appear elsewhere.
    return SAME_AS_ANY.sub(CANON, html)


def fix_counts(html: str, n: int) -> str:
    # Rounded DOWN to the nearest ten so the published number can never
    # exceed reality between a prune and the next regeneration.
    safe = (n // 10) * 10
    html = html.replace("1,000+ B2B SaaS tools", f"{safe}+ B2B SaaS comparisons")
    html = html.replace("1,000+ unbiased B2B SaaS comparisons",
                        f"{safe}+ unbiased B2B SaaS comparisons")
    html = html.replace("1,000+ tools.", f"{safe}+ comparisons.")
    return html


def fix_homepage_webpage_id(html: str) -> str:
    stray = ('{"@context":"https://schema.org","@type":"WebPage",'
             '"name":"SaaSpare","url":"https://saaspare.org",')
    joined = ('{"@context":"https://schema.org","@type":"WebPage",'
              '"@id":"https://saaspare.org/#webpage",'
              '"name":"SaaSpare","url":"https://saaspare.org",'
              '"isPartOf":{"@id":"' + BI.SITE_ID + '"},')
    return html.replace(stray, joined)


def main() -> None:
    n = indexable_count()
    print(f"Indexable pages: {n}")

    same_as_fixed = counts_fixed = 0
    for p in SITE.rglob("*.html"):
        html = original = p.read_text(encoding="utf-8", errors="replace")
        after = fix_same_as(html)
        if after != html:
            same_as_fixed += 1
            html = after
        after = fix_counts(html, n)
        if after != html:
            counts_fixed += 1
            html = after
        if p.name == "index.html" and p.parent == SITE:
            html = fix_homepage_webpage_id(html)
        if html != original:
            p.write_text(html, encoding="utf-8")

    print(f"sameAs normalised on: {same_as_fixed} pages -> {BI.ORG_SAME_AS}")
    print(f"Inflated tool-count copy fixed on: {counts_fixed} pages")

    leftovers = sum(
        1 for p in SITE.rglob("*.html")
        if "1,000+ B2B SaaS tools" in p.read_text(encoding="utf-8", errors="replace")
    )
    bad = sum(
        1 for p in SITE.rglob("*.html")
        if "company/saaspare" in p.read_text(encoding="utf-8", errors="replace")
    )
    print(f"VERIFY  stale count claims remaining: {leftovers}")
    print(f"VERIFY  unverified profile claims remaining: {bad}")
    if leftovers or bad:
        raise SystemExit("fix_brand_entity: did not converge")


if __name__ == "__main__":
    main()
