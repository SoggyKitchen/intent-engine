"""Sample current title/desc patterns on money pages."""
from pathlib import Path
import re

PAGES = Path(__file__).resolve().parents[1] / "site" / "pages"
samples = {"pricing": [], "review": [], "coupon": [], "vs": [], "free-trial": []}

for p in sorted(PAGES.glob("*.html")):
    try:
        html = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    m = re.search(r"<title>([^<]+)</title>", html)
    if not m:
        continue
    title = m.group(1)
    desc_m = re.search(r'<meta name="description" content="([^"]+)"', html)
    desc = desc_m.group(1)[:100] if desc_m else ""
    name = p.name
    if "-pricing-" in name and len(samples["pricing"]) < 4:
        samples["pricing"].append((name, title, desc))
    elif "-review-" in name and len(samples["review"]) < 4:
        samples["review"].append((name, title, desc))
    elif "-coupon-" in name and len(samples["coupon"]) < 4:
        samples["coupon"].append((name, title, desc))
    elif "-vs-" in name and len(samples["vs"]) < 4:
        samples["vs"].append((name, title, desc))
    elif "-free-trial-" in name and len(samples["free-trial"]) < 4:
        samples["free-trial"].append((name, title, desc))
    if all(len(v) == 4 for v in samples.values()):
        break

for kind, items in samples.items():
    print(f"\n=== {kind} ===")
    for name, title, desc in items:
        print(f"  TITLE: {title}")
        print(f"  DESC:  {desc}")
        print()
