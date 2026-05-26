"""
Content freshness sweep for all money pages.

Updates on every pricing, review, coupon, free-trial, vs, and best-of page:
1. dateModified in JSON-LD Article schema → today
2. "Updated [Month Year]" byline text → "Updated May 2026"
3. Sitemap <lastmod> for money pages → today
4. "in 2025" → "in 2026" in titles/metas

Run: uv run python scripts/refresh_money_pages.py
"""
import re
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).resolve().parents[1]
SITE  = ROOT / "site"
PAGES = SITE / "pages"
TODAY = date.today().isoformat()
MONTH_YEAR = "May 2026"

MONEY_PATTERNS = [
    "-pricing-",
    "-review-",
    "-coupon-",
    "-free-trial-",
    "-vs-",
    "-alternatives-",
    "best-",
]

UPDATED_RE      = re.compile(r'Updated\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+202[0-9]', re.IGNORECASE)
DATE_MODIFIED_RE = re.compile(r'"dateModified"\s*:\s*"[^"]*"')
IN_2025_RE      = re.compile(r'\bin 2025\b', re.IGNORECASE)

stats = {"updated": 0, "skipped": 0}


def is_money_page(path: Path) -> bool:
    name = path.name.lower()
    return any(pat in name for pat in MONEY_PATTERNS)


def refresh_page(path: Path) -> bool:
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False

    new_html = html

    # 1. Update dateModified in JSON-LD
    new_html = DATE_MODIFIED_RE.sub(f'"dateModified": "{TODAY}"', new_html)

    # 2. Update "Updated [Month Year]" byline text
    new_html = UPDATED_RE.sub(f"Updated {MONTH_YEAR}", new_html)

    # 3. Fix "in 2025" → "in 2026" in titles/metas only (not in body content that could be factual)
    # Only replace in <title>, <meta>, <h1>, <h2> tags to be safe
    def fix_2025_in_head_tags(m_outer):
        return IN_2025_RE.sub("in 2026", m_outer.group(0))

    # Replace in title, meta description, h1, h2 tags
    for tag_pat in [
        re.compile(r'<title>[^<]*</title>', re.IGNORECASE),
        re.compile(r'<meta[^>]+content="[^"]*"[^>]*>', re.IGNORECASE),
        re.compile(r'<h[12][^>]*>[^<]*</h[12]>', re.IGNORECASE),
    ]:
        new_html = tag_pat.sub(fix_2025_in_head_tags, new_html)

    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        return True
    return False


def refresh_sitemap_lastmod():
    """Update lastmod to TODAY for all money pages in sitemap."""
    sitemap = SITE / "sitemap.xml"
    if not sitemap.exists():
        return 0

    content = sitemap.read_text(encoding="utf-8")
    money_slugs = {
        p.stem.lower()
        for p in PAGES.glob("*.html")
        if is_money_page(p)
    }

    # Also include blog/ and best-*.html
    for p in (SITE / "blog").glob("*.html"):
        money_slugs.add(p.stem.lower())
    for p in SITE.glob("best-*.html"):
        money_slugs.add(p.stem.lower())

    updated_count = 0

    def replace_lastmod(m):
        nonlocal updated_count
        # Check if this URL corresponds to a money page
        full_block = m.group(0)
        loc_m = re.search(r'<loc>([^<]+)</loc>', full_block)
        if not loc_m:
            return full_block
        url = loc_m.group(1)
        slug = url.rstrip("/").split("/")[-1].lower()
        if any(pat.strip("-") in slug for pat in MONEY_PATTERNS) or any(slug == s for s in money_slugs):
            updated_count += 1
            return re.sub(r'<lastmod>[^<]+</lastmod>', f'<lastmod>{TODAY}</lastmod>', full_block)
        return full_block

    new_content = re.sub(
        r'<url>[\s\S]*?</url>',
        replace_lastmod,
        content
    )

    if new_content != content:
        sitemap.write_text(new_content, encoding="utf-8")

    return updated_count


if __name__ == "__main__":
    print("=== Refreshing money page dates ===")

    # Refresh all money pages
    money_pages = [p for p in sorted(PAGES.glob("*.html")) if is_money_page(p)]
    for p in money_pages:
        if refresh_page(p):
            stats["updated"] += 1
        else:
            stats["skipped"] += 1

    # Also refresh blog posts
    blog_dir = SITE / "blog"
    if blog_dir.exists():
        for p in sorted(blog_dir.glob("*.html")):
            if p.name == "index.html":
                continue
            if refresh_page(p):
                stats["updated"] += 1

    print(f"Pages updated:  {stats['updated']}")
    print(f"Pages unchanged: {stats['skipped']}")

    print("\n=== Refreshing sitemap lastmod ===")
    sitemap_updated = refresh_sitemap_lastmod()
    print(f"Sitemap entries updated: {sitemap_updated}")

    print(f"\nDone. All money pages now show dateModified: {TODAY}")
