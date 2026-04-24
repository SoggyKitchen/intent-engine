"""
Rebuilds sitemap.xml from all pages in site/pages/ and site/,
then submits all new URLs to IndexNow for fast Google indexing.
Run: .venv/Scripts/python scripts/update_sitemap_and_index.py
"""
import pathlib, time, urllib.request, urllib.parse, json, sys

DOMAIN = "https://saaspare.org"
INDEXNOW_KEY = "f8fe5282236748eda9fa6a1f13d1afe8"
TODAY = time.strftime("%Y-%m-%d")

def get_all_urls():
    urls = []
    pages_dir = pathlib.Path("site/pages")
    site_dir = pathlib.Path("site")

    skip = {"thanks", "verification", "index"}

    for f in sorted(pages_dir.glob("*.html")):
        if f.stem in skip:
            continue
        urls.append(f"{DOMAIN}/pages/{f.name}")

    for f in sorted(site_dir.glob("*.html")):
        if f.stem in skip:
            continue
        urls.append(f"{DOMAIN}/{f.name}")

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
