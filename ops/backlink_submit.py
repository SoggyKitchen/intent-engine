"""
Backlink & directory submitter.
Submits new comparison pages to free directories and resource lists.
More backlinks = higher Google rankings = more traffic = more revenue.

All submissions are to legitimate directories. No spam, no link farms.
"""
import time
from pathlib import Path

import httpx

from core.db import db
from core.logger import log
from core.secrets import get, DRY_RUN

SUBMITTED_FILE = Path("data/submitted_backlinks.txt")

FREE_DIRECTORIES = [
    {"name": "AlternativeTo",  "url": "https://alternativeto.net/", "type": "manual"},
    {"name": "G2",             "url": "https://www.g2.com/",        "type": "manual"},
    {"name": "Capterra",       "url": "https://www.capterra.com/",  "type": "manual"},
    {"name": "Product Hunt",   "url": "https://www.producthunt.com/", "type": "manual"},
    {"name": "Slant",          "url": "https://www.slant.co/",      "type": "manual"},
    {"name": "StackShare",     "url": "https://stackshare.io/",     "type": "manual"},
    {"name": "Indie Hackers",  "url": "https://www.indiehackers.com/", "type": "manual"},
    {"name": "Hacker News",    "url": "https://news.ycombinator.com/submit", "type": "manual"},
    {"name": "Bing Webmaster", "url": "https://www.bing.com/indexnow", "type": "api"},
    {"name": "IndexNow",       "url": "https://api.indexnow.org/IndexNow", "type": "api"},
]

NICHE_DIRECTORIES = {
    "devtools": [
        {"name": "DevHunt",       "url": "https://devhunt.org/", "type": "manual"},
        {"name": "Awesome Lists", "url": "https://github.com/sindresorhus/awesome", "type": "manual"},
    ],
    "cybersecurity": [
        {"name": "Kali Tools", "url": "https://www.kali.org/tools/", "type": "manual"},
    ],
    "saas_analytics": [
        {"name": "SaaS Radar", "url": "https://www.saasradar.io/", "type": "manual"},
    ],
    "marketing_automation": [
        {"name": "MarTech Alliance", "url": "https://martechalliance.com/", "type": "manual"},
    ],
}


def _already_submitted(page_url: str, directory: str) -> bool:
    SUBMITTED_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not SUBMITTED_FILE.exists():
        return False
    key = f"{page_url}|{directory}"
    import hashlib
    uid = hashlib.sha256(key.encode()).hexdigest()[:12]
    return uid in SUBMITTED_FILE.read_text()


def _mark_submitted(page_url: str, directory: str):
    import hashlib
    key = f"{page_url}|{directory}"
    uid = hashlib.sha256(key.encode()).hexdigest()[:12]
    with open(SUBMITTED_FILE, "a") as f:
        f.write(uid + "\n")


def submit_to_indexnow(urls: list[str]):
    """Submit new URLs to IndexNow (Bing + others). Near-instant indexing."""
    key = get("INDEXNOW_KEY", "")
    domain = get("SITE_DOMAIN", "https://yourdomain.com")
    if not key or not urls:
        return
    try:
        resp = httpx.post("https://api.indexnow.org/IndexNow", json={
            "host": domain.replace("https://", "").replace("http://", ""),
            "key": key,
            "urlList": urls[:100],
        }, timeout=15)
        log.info(f"IndexNow: submitted {len(urls)} URLs, status={resp.status_code}")
    except Exception as e:
        log.warning(f"IndexNow submit failed: {e}")


def ping_google_sitemap():
    """Ping Google to re-crawl sitemap. No auth needed — public endpoint."""
    domain = get("SITE_DOMAIN", "https://yourdomain.com").rstrip("/")
    sitemap_url = f"{domain}/sitemap.xml"
    try:
        resp = httpx.get(
            f"https://www.google.com/ping",
            params={"sitemap": sitemap_url},
            timeout=15,
        )
        log.info(f"Google sitemap ping: status={resp.status_code} for {sitemap_url}")
    except Exception as e:
        log.warning(f"Google sitemap ping failed: {e}")

    try:
        resp = httpx.get(
            f"https://www.bing.com/ping",
            params={"sitemap": sitemap_url},
            timeout=15,
        )
        log.info(f"Bing sitemap ping: status={resp.status_code}")
    except Exception as e:
        log.warning(f"Bing sitemap ping failed: {e}")


def run():
    """Submit recent pages to directories and IndexNow."""
    since_ts = int(time.time()) - 7 * 86400
    domain = get("SITE_DOMAIN", "https://yourdomain.com")

    with db() as conn:
        pages = conn.execute("""
            SELECT title, published_url, vertical, file_path
            FROM outputs
            WHERE type = 'seo_page' AND created_at >= ?
        """, (since_ts,)).fetchall()

    if not pages:
        log.info("No new pages to submit")
        return

    urls = [p["published_url"] for p in pages if p["published_url"]]
    if urls:
        submit_to_indexnow(urls)
        ping_google_sitemap()

    manual_queue = []
    for page in pages:
        vertical = page["vertical"]
        url = page["published_url"] or domain
        title = page["title"]

        dirs_to_check = FREE_DIRECTORIES + NICHE_DIRECTORIES.get(vertical, [])
        for d in dirs_to_check:
            if d["type"] != "manual":
                continue
            if _already_submitted(url, d["name"]):
                continue
            manual_queue.append({
                "directory": d["name"],
                "directory_url": d["url"],
                "page_title": title,
                "page_url": url,
                "vertical": vertical,
            })
            _mark_submitted(url, d["name"])

    if manual_queue:
        queue_path = Path("data/backlink_queue.md")
        with open(queue_path, "w", encoding="utf-8") as f:
            f.write(f"# Backlink Submission Queue — {time.strftime('%Y-%m-%d')}\n\n")
            f.write(f"These take 5 min each. Do 2-3 per day for best SEO effect.\n\n")
            for item in manual_queue:
                f.write(
                    f"- [ ] **{item['directory']}** ({item['directory_url']})\n"
                    f"  Submit: [{item['page_title']}]({item['page_url']})\n\n"
                )
        log.info(f"Backlink queue written: {queue_path} ({len(manual_queue)} items)")
