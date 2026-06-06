"""
Rebuilds sitemap.xml from all indexable pages in site/pages/, site/,
and content subdirectories (blog/, authors/), then submits new URLs to
IndexNow for fast Google indexing.
Run: .venv/Scripts/python scripts/update_sitemap_and_index.py
"""
import pathlib, time, urllib.request, urllib.parse, json, sys, re

DOMAIN = "https://saaspare.org"
INDEXNOW_KEY = "f8fe5282236748eda9fa6a1f13d1afe8"
TODAY = time.strftime("%Y-%m-%d")

# Content subdirectories whose pages should be indexed (E-E-A-T + content depth)
CONTENT_SUBDIRS = ("blog", "authors", "research")
NOINDEX_RE = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]*noindex', re.IGNORECASE)
CANONICAL_RE = re.compile(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', re.IGNORECASE)


def _is_noindex(path: pathlib.Path) -> bool:
    try:
        return bool(NOINDEX_RE.search(path.read_text(encoding="utf-8", errors="replace")))
    except OSError:
        return False


def _url_has_backing_file(url: str) -> bool:
    """True if a sitemap URL maps to a real HTML file on disk.

    Guards against phantom entries: a page may declare a canonical that points to
    a slug with no corresponding file (e.g. `best-adp-...` when only
    `7-best-adp-...html` exists). Such URLs must NOT enter the sitemap, or the
    content-QA HARD gate ('sitemap references non-existent pages') fails the build.
    """
    path = url[len(DOMAIN):] if url.startswith(DOMAIN) else url
    path = path.split("#")[0].split("?")[0].rstrip("/")
    if path in ("", "/"):
        return True  # homepage
    if path == "/pages":
        return (pathlib.Path("site/pages") / "index.html").exists()
    slug = path.lstrip("/")
    site = pathlib.Path("site")
    return (site / f"{slug}.html").exists() or (site / slug / "index.html").exists()


def _canonical_url(path: pathlib.Path, fallback: str) -> str:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
        m = CANONICAL_RE.search(raw)
        if m:
            canonical = m.group(1).split("#")[0].rstrip("/")
            # Only trust the canonical if it resolves to a real file. If a page
            # canonicalises to a slug with no backing file, fall back to this
            # file's own path — which exists by construction (we are iterating it).
            if _url_has_backing_file(canonical):
                return canonical
    except OSError:
        pass
    return fallback


def get_all_urls():
    urls = []
    pages_dir = pathlib.Path("site/pages")
    site_dir = pathlib.Path("site")

    skip = {"thanks", "verification", "index", "fo-verify", "fo-verify-c0ceba67-f661-491b-9895-78e0a0a9eb9f"}
    skip_prefixes = ("ph-preview-",)

    if (pages_dir / "index.html").exists():
        urls.append(f"{DOMAIN}/pages")

    seen = set()

    for f in sorted(pages_dir.glob("*.html")):
        if f.stem in skip or f.stem.startswith(skip_prefixes):
            continue
        if _is_noindex(f):
            continue
        url = _canonical_url(f, f"{DOMAIN}/pages/{f.stem}")
        if url not in seen:
            seen.add(url)
            urls.append(url)

    for f in sorted(site_dir.glob("*.html")):
        if f.stem in skip or f.stem.startswith(skip_prefixes):
            continue
        if _is_noindex(f):
            continue
        url = _canonical_url(f, f"{DOMAIN}/{f.stem}")
        if url not in seen:
            seen.add(url)
            urls.append(url)

    # Content subdirectories (blog posts, author bio pages) — these carry the
    # E-E-A-T and topical-depth signals Google rewards, so they MUST be indexed.
    for sub in CONTENT_SUBDIRS:
        sub_dir = site_dir / sub
        if not sub_dir.is_dir():
            continue
        for f in sorted(sub_dir.glob("*.html")):
            if f.stem in skip or f.stem.startswith(skip_prefixes):
                continue
            if _is_noindex(f):
                continue
            url = _canonical_url(f, f"{DOMAIN}/{sub}/{f.stem}")
            if url not in seen:
                seen.add(url)
                urls.append(url)

    urls.insert(0, DOMAIN + "/")
    return urls


def build_sitemap(urls):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        freq = "weekly" if "/pages/" in url else "monthly"
        priority = "0.8" if "/pages/" in url else "0.6"
        if url in (DOMAIN + "/", DOMAIN):
            priority = "1.0"
            freq = "daily"
        lines.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>""")
    lines.append("</urlset>")
    return "\n".join(lines)


def submit_indexnow(urls):
    host = "saaspare.org"
    endpoint = "https://api.indexnow.org/indexnow"
    batch = urls[:200]
    payload = json.dumps({
        "host": host,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{DOMAIN}/{INDEXNOW_KEY}.txt",
        "urlList": batch
    }).encode()
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            status = r.status
        print(f"  IndexNow: submitted {len(batch)} URLs — HTTP {status}")
        return status
    except Exception as e:
        print(f"  IndexNow error: {e}")
        return 0


def main():
    urls = get_all_urls()
    print(f"\nFound {len(urls)} URLs to include in sitemap")

    sitemap = build_sitemap(urls)
    pathlib.Path("site/sitemap.xml").write_text(sitemap, encoding="utf-8")
    print(f"Sitemap written: site/sitemap.xml ({len(sitemap)} bytes, {len(urls)} URLs)")

    print(f"\nSubmitting to IndexNow...")
    status = submit_indexnow(urls)

    print(f"\nDone. Next steps:")
    print(f"  1. Go to Google Search Console -> Sitemaps -> Submit: {DOMAIN}/sitemap.xml")
    print(f"  2. Request indexing on your top 10 pages manually")
    print(f"  3. Check back in 48h for indexing status\n")


if __name__ == "__main__":
    main()
