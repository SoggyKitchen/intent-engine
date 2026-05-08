"""
Add category hub pages and new blog posts to sitemap.xml.
Run once after build_category_hubs.py and create_missing_blog_posts.py.
"""
from pathlib import Path
from datetime import date
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
TODAY = date.today().isoformat()

def url_entry(loc: str, priority: str = "0.8", freq: str = "monthly") -> str:
    return f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>"""

def main():
    sitemap_path = SITE / "sitemap.xml"
    content = sitemap_path.read_text(encoding="utf-8")

    new_entries = []

    # Category hub pages
    hub_pages = list(SITE.glob("best-*-2026.html"))
    for p in hub_pages:
        loc = f"https://saaspare.org/{p.stem}"
        if loc not in content:
            new_entries.append(url_entry(loc, "0.9", "monthly"))
            print(f"  + hub: {p.name}")

    # New blog posts
    blog_pages = list((SITE / "blog").glob("*.html"))
    for p in blog_pages:
        if p.name == "index.html":
            continue
        loc = f"https://saaspare.org/blog/{p.stem}"
        if loc not in content:
            new_entries.append(url_entry(loc, "0.7", "monthly"))
            print(f"  + blog: {p.name}")

    if not new_entries:
        print("No new URLs to add.")
        return

    # Insert before </urlset>
    insertion = "\n" + "\n".join(new_entries) + "\n"
    new_content = content.replace("</urlset>", insertion + "</urlset>")
    sitemap_path.write_text(new_content, encoding="utf-8")
    print(f"\nAdded {len(new_entries)} URLs to sitemap.xml")

if __name__ == "__main__":
    main()
