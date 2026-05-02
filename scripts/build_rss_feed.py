"""Generate /feed.xml from the latest strategic + comparison pages.
Picks up the 50 most recently modified pages under site/ (excluding internal files)."""
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
import re

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DOMAIN = "https://saaspare.org"
MAX_ITEMS = 50

SKIP_DIRS = {"assets", "data", ".well-known"}
SKIP_NAMES = {"sitemap.xml", "robots.txt", "ads.txt", "llms.txt", "feed.xml"}


def pick_pages():
    pages = []
    for p in SITE.rglob("*.html"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.name in SKIP_NAMES:
            continue
        pages.append(p)
    pages.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return pages[:MAX_ITEMS]


def extract(html: str, tag: str) -> str:
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def extract_meta(html: str, name: str) -> str:
    m = re.search(
        rf'<meta\s+name=["\']{name}["\']\s+content=["\']([^"\']+)["\']',
        html, re.IGNORECASE,
    )
    return m.group(1).strip() if m else ""


def path_to_url(p: Path) -> str:
    rel = p.relative_to(SITE).as_posix()
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    elif rel == "index.html":
        rel = ""
    return f"{DOMAIN}/{rel}"


def build_item(p: Path) -> str:
    try:
        html = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    title = extract(html, "title") or p.stem.replace("-", " ").title()
    desc = extract_meta(html, "description") or ""
    url = path_to_url(p)
    mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
    pub = mtime.strftime("%a, %d %b %Y %H:%M:%S +0000")
    return (
        "    <item>\n"
        f"      <title>{escape(title)}</title>\n"
        f"      <link>{escape(url)}</link>\n"
        f"      <guid isPermaLink=\"true\">{escape(url)}</guid>\n"
        f"      <pubDate>{pub}</pubDate>\n"
        f"      <description>{escape(desc)}</description>\n"
        "    </item>"
    )


def main():
    pages = pick_pages()
    items = "\n".join(filter(None, (build_item(p) for p in pages)))
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>SaaSpare — Independent B2B SaaS Comparisons</title>
    <link>{DOMAIN}/</link>
    <atom:link href="{DOMAIN}/feed.xml" rel="self" type="application/rss+xml" />
    <description>Honest pricing guides, comparisons, free-trial checks, and alternatives for B2B SaaS buyers.</description>
    <language>en-AU</language>
    <lastBuildDate>{now}</lastBuildDate>
    <ttl>1440</ttl>
{items}
  </channel>
</rss>
"""
    (SITE / "feed.xml").write_text(feed, encoding="utf-8")
    print(f"wrote feed.xml with {len(pages)} items")


if __name__ == "__main__":
    main()
