"""
Add Offer schema with actual $ prices to all 44 pricing pages.

Without Offer+price schema, Google can't show pricing in rich results.
This unlocks the price annotation in SERPs that significantly boosts CTR
for "X pricing" queries.

Run: python scripts/enrich_offer_schema.py
"""
import re, json
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
TODAY = date.today().isoformat()

stats = {"added": 0, "skipped_existing": 0, "skipped_no_prices": 0}


def extract_prices_from_html(html: str) -> list[tuple[str, str]]:
    """Extract plan name + price pairs from the HTML body."""
    pairs = []
    # Match table rows like: <tr><td><strong>Pro</strong></td><td>$129.95/month</td></tr>
    table_pattern = re.compile(
        r'<tr>\s*<td>\s*<strong>([^<]+)</strong>\s*</td>\s*<td>([^<]+)</td>',
        re.IGNORECASE
    )
    for m in table_pattern.finditer(html):
        plan = m.group(1).strip()
        raw = m.group(2).strip()
        # Extract first $ or € amount
        price_m = re.search(r'\$([0-9]+(?:\.[0-9]+)?)', raw)
        if not price_m:
            price_m = re.search(r'€([0-9]+(?:\.[0-9]+)?)', raw)
        if price_m:
            pairs.append((plan, price_m.group(1)))
    return pairs


def patch_pricing_page(path: Path) -> bool:
    try:
        html = path.read_text(encoding="utf-8")
    except Exception:
        return False

    # Skip if already has Offer schema with price
    if '"@type":"Offer"' in html and '"price":' in html:
        stats["skipped_existing"] += 1
        return False

    prices = extract_prices_from_html(html)
    if len(prices) < 2:
        stats["skipped_no_prices"] += 1
        return False

    # Get tool name from filename
    m = re.match(r'(.+?)-pricing-\d{4}', path.stem)
    if not m:
        return False
    tool_slug = m.group(1)
    tool_display = " ".join(w.capitalize() for w in tool_slug.split("-"))

    # Build Offer array
    offers = []
    for plan, price in prices[:6]:  # cap at 6 offers
        offers.append({
            "@type": "Offer",
            "name": plan[:60],
            "price": price,
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "priceValidFrom": TODAY,
        })

    product_schema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": tool_display,
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web",
        "offers": offers,
    }

    schema_block = f'\n  <script type="application/ld+json">\n  {json.dumps(product_schema, separators=(",", ":"))}\n  </script>\n'

    # Inject before </head>
    if "</head>" in html:
        html = html.replace("</head>", schema_block + "</head>", 1)
        path.write_text(html, encoding="utf-8")
        stats["added"] += 1
        return True
    return False


def main():
    pricing_pages = list(PAGES.glob("*-pricing-2026-*.html"))
    print(f"Processing {len(pricing_pages)} pricing pages...")
    for p in pricing_pages:
        patch_pricing_page(p)
    print()
    print("=== RESULTS ===")
    print(f"  Offer+price schema added:    {stats['added']}")
    print(f"  Skipped (already had):       {stats['skipped_existing']}")
    print(f"  Skipped (no prices found):   {stats['skipped_no_prices']}")


if __name__ == "__main__":
    main()
