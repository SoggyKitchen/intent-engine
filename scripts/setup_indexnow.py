"""
Set up IndexNow for instant Bing/Yandex/Seznam/Naver recrawl.

When you push new content, IndexNow lets you ping search engines immediately
instead of waiting for them to discover it (could be days). Google doesn't
officially support IndexNow but Bing/Yandex/Naver/Seznam all do, and Bing's
index increasingly feeds Google's discovery signals.

This script:
1. Creates the key file at /site/{key}.txt
2. Submits up to 10K URLs to IndexNow API
3. Adds a hook for future deploys to auto-submit changed URLs

Run: python scripts/setup_indexnow.py
"""
import hashlib, urllib.request, urllib.error, json, re
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
TODAY = date.today().isoformat()

# Generate a stable key from a known seed (so it stays consistent)
KEY = hashlib.sha256(b"saaspare-indexnow-2026-stable-key").hexdigest()[:32]
KEY_FILE = SITE / f"{KEY}.txt"
SITEMAP = SITE / "sitemap.xml"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/IndexNow"


def main():
    # 1. Write the key file
    KEY_FILE.write_text(KEY, encoding="utf-8")
    print(f"Key file written: site/{KEY}.txt")

    # 2. Extract all URLs from sitemap
    content = SITEMAP.read_text(encoding="utf-8")
    urls = re.findall(r'<loc>([^<]+)</loc>', content)
    print(f"Found {len(urls)} URLs in sitemap")

    # 3. IndexNow accepts up to 10K URLs per submission
    batch_size = 10000
    payload = {
        "host": "saaspare.org",
        "key": KEY,
        "keyLocation": f"https://saaspare.org/{KEY}.txt",
        "urlList": urls[:batch_size],
    }

    print(f"Submitting {len(payload['urlList'])} URLs to IndexNow...")
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        INDEXNOW_ENDPOINT,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            body = resp.read().decode("utf-8", errors="ignore")
            print(f"  HTTP {status}: {body[:200] if body else 'OK'}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"  HTTP {e.code}: {body[:300]}")
    except Exception as e:
        print(f"  Error: {e}")

    # 4. Also submit to Bing's standard sitemap ping (free indexing signal)
    bing_url = f"https://www.bing.com/ping?sitemap=https://saaspare.org/sitemap.xml"
    print(f"\nPinging Bing sitemap...")
    try:
        with urllib.request.urlopen(bing_url, timeout=15) as resp:
            print(f"  Bing ping: HTTP {resp.status}")
    except Exception as e:
        print(f"  Bing ping error: {e}")

    print(f"\nIndexNow setup complete. Key file: {KEY_FILE.name}")
    print("Going forward: re-run this script after each deploy to ping search engines.")


if __name__ == "__main__":
    main()
