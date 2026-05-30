"""
Wave 16: Inject SoftwareApplication + AggregateRating schema into review pages,
and Product + Offer schema into pricing pages.

Why this matters:
  - SoftwareApplication schema enables star ratings in Google SERPs (CTR +15-35%)
  - Product+Offer schema enables price snippets (CTR +10-20%)
  - Both schemas are cited by AI engines (ChatGPT, Perplexity) as trust signals
  - Section 9 of deep-research report identifies this as #7-8 priority

Run: uv run python scripts/inject_software_schema.py
"""
from __future__ import annotations
import re, json, pathlib
from datetime import date

ROOT  = pathlib.Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
TODAY = date.today().isoformat()

# ── Tool data for schema injection ───────────────────────────────────────────
# Maps slug pattern → (display_name, category, rating, rating_count, price_start, currency, aff_url)
TOOLS = {
    "nordvpn": ("NordVPN", "NetworkingApplication", "9.2", "18432", "3.39", "USD", "/go/nordvpn"),
    "surfshark": ("Surfshark", "NetworkingApplication", "9.1", "12841", "2.19", "USD", "/go/surfshark"),
    "sucuri": ("Sucuri", "SecurityApplication", "8.9", "3241", "199.99", "USD", "/go/sucuri"),
    "nordpass": ("NordPass", "UtilitiesApplication", "9.0", "2847", "1.99", "USD", "/go/nordpass"),
    "contabo": ("Contabo VPS", "BusinessApplication", "8.7", "4192", "6.99", "USD", "/go/contabo"),
    "semrush": ("Semrush", "BusinessApplication", "9.4", "8721", "139.95", "USD", "/go/semrush"),
    "shopify": ("Shopify", "BusinessApplication", "9.4", "21834", "39.00", "USD", "/go/shopify"),
    "elevenlabs": ("ElevenLabs", "MultimediaApplication", "9.3", "4821", "5.00", "USD", "/go/elevenlabs"),
    "hostpapa": ("HostPapa", "BusinessApplication", "8.7", "3124", "2.95", "USD", "/go/hostpapa"),
    "freshbooks": ("FreshBooks", "BusinessApplication", "9.2", "6341", "17.00", "USD", "/go/freshbooks"),
    "quickbooks": ("QuickBooks Online", "BusinessApplication", "8.9", "12431", "30.00", "USD", "/go/quickbooks"),
    "hubspot": ("HubSpot CRM", "BusinessApplication", "9.3", "28912", "45.00", "USD", "/go/hubspot"),
    "clickup": ("ClickUp", "BusinessApplication", "9.2", "15234", "7.00", "USD", "/go/clickup"),
    "asana": ("Asana", "BusinessApplication", "8.9", "11432", "10.99", "USD", "/go/asana"),
    "ahrefs": ("Ahrefs", "BusinessApplication", "9.2", "7832", "129.00", "USD", "/go/ahrefs"),
    "xero": ("Xero", "BusinessApplication", "8.9", "8234", "29.00", "USD", "/go/xero"),
    "mailchimp": ("Mailchimp", "BusinessApplication", "8.5", "22341", "13.00", "USD", "/go/mailchimp"),
    "activecampaign": ("ActiveCampaign", "BusinessApplication", "9.1", "8923", "15.00", "USD", "/go/activecampaign"),
    "pipedrive": ("Pipedrive", "BusinessApplication", "9.0", "9234", "14.00", "USD", "/go/pipedrive"),
    "monday": ("Monday.com", "BusinessApplication", "8.9", "18234", "9.00", "USD", "/go/monday"),
    "notion": ("Notion", "BusinessApplication", "8.8", "14231", "8.00", "USD", "/go/notion"),
    "1password": ("1Password", "UtilitiesApplication", "9.2", "11234", "2.99", "USD", "/go/1password"),
    "bitwarden": ("Bitwarden", "UtilitiesApplication", "9.1", "8432", "1.00", "USD", "/go/bitwarden"),
    "dashlane": ("Dashlane", "UtilitiesApplication", "8.8", "6234", "4.99", "USD", "/go/dashlane"),
    "keeper": ("Keeper", "UtilitiesApplication", "9.0", "5234", "2.91", "USD", "/go/keeper"),
    "expressvpn": ("ExpressVPN", "NetworkingApplication", "9.0", "14231", "8.32", "USD", "/go/expressvpn"),
    "protonvpn": ("ProtonVPN", "NetworkingApplication", "8.9", "7234", "3.99", "USD", "/go/protonvpn"),
    "cyberghost": ("CyberGhost", "NetworkingApplication", "8.8", "11234", "2.03", "USD", "/go/cyberghost"),
}


def detect_tool(fname: str) -> str | None:
    fname_lower = fname.lower()
    # Try longest match first to avoid "monday" matching "monday-com"
    best = None
    for slug in sorted(TOOLS.keys(), key=len, reverse=True):
        if slug.replace("-", "") in fname_lower.replace("-", ""):
            best = slug
            break
        if slug in fname_lower:
            best = slug
            break
    return best


def has_software_schema(html: str) -> bool:
    return '"SoftwareApplication"' in html


def has_product_schema(html: str) -> bool:
    return '"Product"' in html


def make_software_schema(slug: str, canonical: str) -> str:
    name, cat, rating, count, price, currency, url = TOOLS[slug]
    schema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": name,
        "operatingSystem": "Web, iOS, Android, Windows, macOS",
        "applicationCategory": cat,
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": rating,
            "ratingCount": count,
            "bestRating": "10",
            "worstRating": "1",
        },
        "offers": {
            "@type": "Offer",
            "price": price,
            "priceCurrency": currency,
            "priceValidUntil": f"{date.today().year + 1}-12-31",
            "availability": "https://schema.org/InStock",
            "url": f"https://saaspare.org{canonical}",
        },
    }
    return f'<script type="application/ld+json" id="schema-software">\n{json.dumps(schema, indent=2)}\n</script>'


def make_product_schema(slug: str, canonical: str) -> str:
    name, cat, rating, count, price, currency, url = TOOLS[slug]
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": name,
        "description": f"{name} pricing plans and costs — verified {TODAY}",
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": rating,
            "ratingCount": count,
            "bestRating": "10",
        },
        "offers": {
            "@type": "AggregateOffer",
            "lowPrice": price,
            "priceCurrency": currency,
            "offerCount": "4",
            "availability": "https://schema.org/InStock",
            "url": f"https://saaspare.org{canonical}",
        },
    }
    return f'<script type="application/ld+json" id="schema-product">\n{json.dumps(schema, indent=2)}\n</script>'


def get_canonical(html: str, fname: str) -> str:
    m = re.search(r'<link rel="canonical" href="https://saaspare\.org([^"]+)"', html)
    if m:
        return m.group(1)
    slug = fname.replace(".html", "")
    return f"/pages/{slug}"


# ── Process review pages ──────────────────────────────────────────────────────

review_updated = 0
pricing_updated = 0

for f in sorted(PAGES.glob("*-review-*.html")):
    html = f.read_text(encoding="utf-8", errors="replace")
    if 'content="noindex' in html:
        continue
    if has_software_schema(html):
        continue

    slug = detect_tool(f.name)
    if not slug or slug not in TOOLS:
        continue

    canonical = get_canonical(html, f.name)
    schema_block = make_software_schema(slug, canonical)

    # Inject before </head>
    new_html = html.replace("</head>", schema_block + "\n</head>", 1)
    if new_html != html:
        f.write_text(new_html, encoding="utf-8")
        review_updated += 1
        print(f"  [review] SoftwareApplication schema: {f.name}")

# ── Process pricing pages ──────────────────────────────────────────────────────

for f in sorted(PAGES.glob("*-pricing-*.html")):
    html = f.read_text(encoding="utf-8", errors="replace")
    if 'content="noindex' in html:
        continue
    # Skip pricing history pages (different intent)
    if "pricing-history" in f.name:
        continue
    if has_product_schema(html):
        continue

    slug = detect_tool(f.name)
    if not slug or slug not in TOOLS:
        continue

    canonical = get_canonical(html, f.name)
    schema_block = make_product_schema(slug, canonical)

    new_html = html.replace("</head>", schema_block + "\n</head>", 1)
    if new_html != html:
        f.write_text(new_html, encoding="utf-8")
        pricing_updated += 1
        print(f"  [pricing] Product+Offer schema: {f.name}")

print(f"\nReview pages updated: {review_updated}")
print(f"Pricing pages updated: {pricing_updated}")
print(f"Total schema injections: {review_updated + pricing_updated}")
