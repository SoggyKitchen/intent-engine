"""
Adds a real Product/AggregateOffer JSON-LD block to every *-pricing-2026-*
page, built ONLY from prices already rendered on that page (the
price-at-a-glance sidebar). No aggregateRating/reviewCount — we have no
verified review data to back one, and fabricating it is a Google
structured-data policy violation, not a real trust signal.

Idempotent: skips any page that already has a Product schema block.
Run: uv run python scripts/add_pricing_product_schema.py
"""
import json
import re
from pathlib import Path

PAGES = Path("site/pages")
PRICE_RE = re.compile(r'pag-plan-price[^>]*>\$?([\d.]+)')
TITLE_RE = re.compile(r'<title>([^<]+)')
CANONICAL_RE = re.compile(r'<link rel="canonical" href="([^"]+)"')
OG_IMAGE_RE = re.compile(r'og:image" content="([^"]+)"')


def tool_name_from_title(title: str) -> str:
    # "1Password Pricing 2026 (Verified August 2026) — Real Costs..." -> "1Password"
    m = re.match(r'^(.*?)\s+Pricing\s+2026', title)
    return m.group(1).strip() if m else title.split(" Pricing")[0].strip()


def build_schema(name: str, canonical: str, image: str, prices: list[float]) -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": name,
        "description": f"Verified, un-sponsored pricing breakdown for {name} — every plan, hidden fee, and real cost by team size.",
        "image": image,
        "offers": {
            "@type": "AggregateOffer",
            "url": canonical,
            "priceCurrency": "USD",
            "lowPrice": min(prices),
            "highPrice": max(prices),
            "offerCount": len(prices)
        }
    }
    return f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'


def main():
    pages = sorted(PAGES.glob("*-pricing-2026-plans-costs-what-you-actually-pay.html"))
    added = skipped_has = skipped_noprice = 0
    for f in pages:
        html = f.read_text(encoding="utf-8")
        if '"@type": "Product"' in html or '"@type":"Product"' in html:
            skipped_has += 1
            continue
        prices = [float(p) for p in PRICE_RE.findall(html)]
        if not prices:
            skipped_noprice += 1
            continue
        title_m = TITLE_RE.search(html)
        canon_m = CANONICAL_RE.search(html)
        img_m = OG_IMAGE_RE.search(html)
        if not title_m or not canon_m:
            skipped_noprice += 1
            continue
        name = tool_name_from_title(title_m.group(1))
        schema = build_schema(name, canon_m.group(1), img_m.group(1) if img_m else "", prices)
        html = html.replace("</head>", schema + "\n</head>", 1)
        f.write_text(html, encoding="utf-8")
        added += 1
    print(f"add_pricing_product_schema: added={added} already_had={skipped_has} no_price_found={skipped_noprice} total={len(pages)}")


if __name__ == "__main__":
    main()
