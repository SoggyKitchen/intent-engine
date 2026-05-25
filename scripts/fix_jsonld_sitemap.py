"""
Fix two failing CI tests:
  1. 10 invalid JSON-LD blocks  - ratingCount has a thousands-comma e.g. "42",847"
  2. 25 pages missing from sitemap - blog + new pages not indexed

Run: uv run python scripts/fix_jsonld_sitemap.py
"""
import re, json
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).resolve().parents[1]
SITE  = ROOT / "site"
TODAY = date.today().isoformat()

# ── 1. Fix broken ratingCount in JSON-LD ─────────────────────────────────
#
# The bug: "ratingCount":"42",847"
#   - number like 42,847 was serialised with thousands separator
#   - comma was treated as JSON key-value separator → syntax error
# Fix: merge the fragments → "ratingCount": 42847  (numeric, not string)

RATING_FIX = re.compile(
    r'"ratingCount"\s*:\s*"(\d+)",(\d+)"',
    re.IGNORECASE
)

def fix_jsonld_files():
    fixed_files = 0
    for p in sorted(SITE.glob("pages/*.html")):
        try:
            html = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        new_html = RATING_FIX.sub(
            lambda m: f'"ratingCount": {m.group(1)}{m.group(2)}',
            html
        )
        if new_html != html:
            p.write_text(new_html, encoding="utf-8")
            fixed_files += 1
            print(f"  [JSON-LD fixed] {p.name}")
    print(f"JSON-LD: fixed {fixed_files} files")

# ── 2. Rebuild sitemap to include all indexable pages ─────────────────────

SITEMAP     = SITE / "sitemap.xml"
BASE_URL    = "https://saaspare.org"
SKIP_FRAGS  = ["404", "privacy", "terms", "cookie", "thank-you"]


def is_indexable(p: Path) -> bool:
    name = p.name.lower()
    for frag in SKIP_FRAGS:
        if frag in name:
            return False
    try:
        head = p.read_text(encoding="utf-8", errors="replace")[:4000]
    except Exception:
        return False
    if "noindex" in head.lower():
        return False
    return True


def path_to_url(p: Path) -> str:
    rel   = p.relative_to(SITE)
    parts = list(rel.parts)
    if parts[-1].endswith(".html"):
        stem = parts[-1][:-5]
        parts[-1] = stem
    if parts == ["index"]:
        return BASE_URL + "/"
    return BASE_URL + "/" + "/".join(parts)


def rebuild_sitemap():
    # Existing lastmod values
    existing: dict[str, str] = {}
    if SITEMAP.exists():
        for m in re.finditer(
            r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>",
            SITEMAP.read_text(encoding="utf-8")
        ):
            existing[m.group(1)] = m.group(2)

    all_html = list(SITE.glob("**/*.html"))
    indexable = sorted(p for p in all_html if is_indexable(p))

    new_count = 0
    entries   = []
    for p in indexable:
        url     = path_to_url(p)
        lastmod = existing.get(url, TODAY)
        if url not in existing:
            new_count += 1
        priority = "0.9" if url == BASE_URL + "/" else "0.8" if "/blog/" in url or "/best-" in url else "0.7"
        entries.append(
            f"  <url>\n"
            f"    <loc>{url}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>weekly</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            f"  </url>"
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    SITEMAP.write_text(xml, encoding="utf-8")
    print(f"Sitemap: {len(entries)} total URLs, {new_count} newly added -> site/sitemap.xml")

# ── 3. Verify JSON-LD all clean ───────────────────────────────────────────

JSONLD_PAT = re.compile(
    r'type="application/ld\+json"[^>]*>([\s\S]*?)</script>',
    re.IGNORECASE
)

def verify_jsonld():
    bad = []
    for p in SITE.glob("**/*.html"):
        try:
            raw = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in JSONLD_PAT.finditer(raw):
            pl = m.group(1).strip()
            if not pl:
                continue
            try:
                json.loads(pl)
            except json.JSONDecodeError as e:
                bad.append((p.name, str(e)))
    if bad:
        print(f"\n⚠  Still {len(bad)} invalid JSON-LD blocks:")
        for f, e in bad:
            print(f"  {f}: {e}")
    else:
        print("OK  All JSON-LD blocks valid")
    return len(bad)

# ── main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== 1. Fix JSON-LD ratingCount bug ===")
    fix_jsonld_files()

    print("\n=== 2. Rebuild sitemap ===")
    rebuild_sitemap()

    print("\n=== 3. Verify JSON-LD ===")
    remaining = verify_jsonld()

    print("\n=== Done ===")
    print("Run: uv run pytest --tb=short -q")
