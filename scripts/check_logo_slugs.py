"""Check which simpleicons slugs used on the site actually exist on the CDN."""
import concurrent.futures as cf
import json
import re
import sys
import urllib.request
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"
RX = re.compile(r"cdn\.simpleicons\.org/([a-z0-9\-\.#%]+)")


def collect():
    slugs = set()
    for p in SITE.rglob("*.html"):
        slugs.update(RX.findall(p.read_text(encoding="utf-8", errors="ignore")))
    return sorted(slugs)


def check(slug):
    url = f"https://cdn.simpleicons.org/{slug}"
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return slug, r.status == 200
    except Exception:
        return slug, False


def main():
    slugs = collect()
    out = {}
    with cf.ThreadPoolExecutor(20) as ex:
        for slug, ok in ex.map(check, slugs):
            out[slug] = ok
    broken = sorted(s for s, ok in out.items() if not ok)
    Path("seo/reports/broken-logo-slugs.json").write_text(json.dumps(broken, indent=1))
    print(f"total={len(slugs)} broken={len(broken)}")
    print("\n".join(broken))


if __name__ == "__main__":
    sys.exit(main())
