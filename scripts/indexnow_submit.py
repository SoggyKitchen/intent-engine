"""Submit all sitemap URLs to IndexNow (Bing + Yandex + DuckDuckGo + Seznam).

Runs after each deploy. Free, no login, no API key management — uses the file-hosted key.
"""
import json
import urllib.request
import urllib.error
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
HOST = "saaspare.org"
KEY = "aaf9b8574ce84402f84eee6e76237d19"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/IndexNow"
BATCH = 10000  # IndexNow allows up to 10k URLs per request


def gather_urls() -> list[str]:
    smap = SITE / "sitemap.xml"
    if not smap.exists():
        return []
    text = smap.read_text(encoding="utf-8")
    return re.findall(r"<loc>([^<]+)</loc>", text)


def submit(urls: list[str]) -> tuple[int, str]:
    body = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return 0, str(e)


def main():
    urls = gather_urls()
    if not urls:
        print("no URLs in sitemap")
        return
    print(f"submitting {len(urls)} URLs to IndexNow...")
    for i in range(0, len(urls), BATCH):
        chunk = urls[i:i + BATCH]
        status, body = submit(chunk)
        print(f"  batch {i // BATCH + 1}: HTTP {status} ({len(chunk)} urls)  {body[:120]}")
    print("Done. 200/202 = accepted, 400 = bad request, 403 = key mismatch, 422 = invalid URLs.")


if __name__ == "__main__":
    main()
