"""
Fix two failing tests:
1. test_every_jsonld_block_parses  - 10 review pages have malformed JSON-LD
2. test_every_indexable_page_in_sitemap - 25 new pages missing from sitemap

Run: python scripts/fix_jsonld_and_sitemap.py
"""
import re, json
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).resolve().parents[1]
SITE  = ROOT / "site"
TODAY = date.today().isoformat()

JSONLD_PAT = re.compile(
    r'(<script[^>]+type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
    re.DOTALL | re.IGNORECASE
)

# ── 1. Find & fix invalid JSON-LD ──────────────────────────────────────────

def fix_jsonld_in_file(path: Path) -> bool:
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False

    changed = False
    result = html

    for m in JSONLD_PAT.finditer(html):
        open_tag, payload, close_tag = m.group(1), m.group(2).strip(), m.group(3)
        if not payload:
            continue
        try:
            json.loads(payload)
            continue          # already valid
        except json.JSONDecodeError:
            pass

        # Common fix: trailing commas before } or ]
        fixed = re.sub(r',\s*([}\]])', r'\1', payload)
        # Fix single-quoted strings -> double-quoted (careful not to break HTML)
        # Only attempt if payload still invalid after trailing-comma fix
        try:
            json.loads(fixed)
        except json.JSONDecodeError:
            # Try stripping JS comments  // ...
            fixed = re.sub(r'//[^\n]*', '', fixed)
            try:
                json.loads(fixed)
            except json.JSONDecodeError:
                print(f"  [SKIP] Can't auto-fix: {path.name}")
                continue

        old_block = m.group(0)
        new_block = open_tag + "\n  " + fixed + "\n  " + close_tag
        result = result.replace(old_block, new_block, 1)
        changed = True
        print(f"  [FIXED JSON-LD] {path.name}")

    if changed:
        path.write_text(result, encoding="utf-8")
    return changed


def fix_all_jsonld():
    fixed = 0
    for p in sorted(SITE.glob("**/*.html")):
        if fix_jsonld_in_file(p):
            fixed += 1
    print(f"\nJSON-LD: fixed {fixed} files")
    return fixed


# ── 2. Update sitemap to include all indexable pages ───────────────────────

SITEMAP = SITE / "sitemap.xml"
BASE_URL = "https://saaspare.org"

# Pages we deliberately exclude from sitemap
NOINDEX_FRAGMENTS = ["404", "privacy", "terms", "cookie", "thank-you"]


def is_indexable(p: Path) -> bool:
    name = p.name.lower()
    for frag in NOINDEX_FRAGMENTS:
        if frag in name:
            return False
    # Check for actual noindex meta tag
    try:
        head = p.read_text(encoding="utf-8", errors="replace")[:3000]
    except Exception:
        return False
    if 'noindex' in head.lower():
        return False
    return True


def path_to_url(p: Path) -> str:
    rel = p.relative_to(SITE)
    parts = list(rel.parts)
    # Remove .html extension
    if parts[-1].endswith(".html"):
        parts[-1] = parts[-1][:-5]
    # site/index -> site/
    if parts == ["index"]:
        return BASE_URL + "/"
    return BASE_URL + "/" + "/".join(parts)


def rebuild_sitemap():
    # Collect all indexable HTML pages
    all_pages = list(SITE.glob("**/*.html"))
    indexable = [p for p in all_pages if is_indexable(p)]

    # Build URL -> lastmod dict from existing sitemap
    existing_lastmod: dict[str, str] = {}
    if SITEMAP.exists():
        content = SITEMAP.read_text(encoding="utf-8")
        for m in re.finditer(r'<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>', content):
            existing_lastmod[m.group(1)] = m.group(2)

    # Generate entries
    entries = []
    new_count = 0
    for p in sorted(indexable):
        url = path_to_url(p)
        lastmod = existing_lastmod.get(url, TODAY)
        if url not in existing_lastmod:
            new_count += 1
        entries.append(f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.7</priority>\n  </url>")

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap_xml += "\n".join(entries)
    sitemap_xml += "\n</urlset>\n"

    SITEMAP.write_text(sitemap_xml, encoding="utf-8")
    print(f"\nSitemap: {len(entries)} URLs total ({new_count} newly added), written to site/sitemap.xml")


# ── 3. Rebuild /pages/index.html and site/index.html page lists ─────────────

def rebuild_pages_index():
    """Add newly created pages to /pages/index.html so they're discoverable."""
    index_file = SITE / "pages" / "index.html"
    if not index_file.exists():
        print("  [SKIP] pages/index.html not found")
        return

    html = index_file.read_text(encoding="utf-8", errors="replace")

    # Find all pages currently linked
    linked_hrefs = set(re.findall(r'href=["\']([^"\']+\.html)["\']', html))
    linked_hrefs |= set(re.findall(r'href=["\']([^"\'?#]+)["\']', html))

    # Find all .html files in /pages/
    all_page_files = sorted((SITE / "pages").glob("*.html"))
    missing_from_index = []
    for p in all_page_files:
        if p.name == "index.html":
            continue
        if p.name not in linked_hrefs and p.stem not in linked_hrefs:
            href_check = "/" + p.name
            rel_check  = p.name
            if href_check not in linked_hrefs and rel_check not in linked_hrefs:
                missing_from_index.append(p)

    if not missing_from_index:
        print("  pages/index.html: all pages already linked")
        return

    # Build link items
    new_items = []
    for p in missing_from_index:
        title = p.stem.replace("-", " ").title()
        new_items.append(f'      <li><a href="/pages/{p.name}">{title}</a></li>')

    # Inject before </ul> of the main page list (first </ul>)
    inject = "\n".join(new_items)
    new_html = html.replace("</ul>", inject + "\n    </ul>", 1)
    if new_html != html:
        index_file.write_text(new_html, encoding="utf-8")
        print(f"  pages/index.html: added {len(missing_from_index)} missing page links")
    else:
        print("  pages/index.html: could not inject (no </ul> found?)")


# ── main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Step 1: Fix invalid JSON-LD ===")
    fix_all_jsonld()

    print("\n=== Step 2: Rebuild sitemap ===")
    rebuild_sitemap()

    print("\n=== Step 3: Update pages index ===")
    rebuild_pages_index()

    print("\nDone. Re-run: uv run pytest --tb=short -q")
