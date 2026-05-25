"""
Fix the JSON-LD blocks in the 14 newly built review pages.
The issue: Python f-string apostrophes/dashes produced invalid JSON escapes.
Fix: re-generate each schema block using json.dumps() for safe serialisation.

Run: uv run python scripts/fix_new_review_jsonld.py
"""
import json, re
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
TODAY = date.today().isoformat()
YEAR  = "2026"

JSONLD_PAT = re.compile(
    r'(<script[^>]+type=["\']application/ld\+json["\'][^>]*>)([\s\S]*?)(</script>)',
    re.IGNORECASE
)

# Same tool data as the builder - just what we need to regenerate schema
TOOLS = {
    "bigcommerce": {"display": "BigCommerce", "rating": 4.3, "rating_count": 2847, "pricing_start": "39", "verdict": "Best for high-volume B2B and DTC brands that need serious multi-channel capability without transaction fees."},
    "clearscope":  {"display": "Clearscope",  "rating": 4.6, "rating_count": 843,  "pricing_start": "170", "verdict": "Worth every dollar for content teams publishing 20+ articles per month; overkill for lone bloggers."},
    "contabo":     {"display": "Contabo",      "rating": 4.1, "rating_count": 6234, "pricing_start": "5.50", "verdict": "Best price-per-GB RAM on the market. Perfect for dev environments; production use requires self-management."},
    "copy-ai":     {"display": "Copy.ai",      "rating": 4.3, "rating_count": 1892, "pricing_start": "0", "verdict": "Strong choice for GTM teams that want AI woven into their entire content pipeline."},
    "digitalocean":{"display": "DigitalOcean", "rating": 4.5, "rating_count": 9876, "pricing_start": "4", "verdict": "The developer's cloud: cleaner than AWS, cheaper than GCP for straightforward workloads."},
    "gusto":       {"display": "Gusto",        "rating": 4.4, "rating_count": 5231, "pricing_start": "46", "verdict": "The gold standard for US small-business payroll. Every dollar saves hours of tax headaches every quarter."},
    "hetzner":     {"display": "Hetzner",      "rating": 4.6, "rating_count": 8123, "pricing_start": "4.15", "verdict": "Unbeatable value for EU workloads. If GDPR compliance matters and you want the lowest bill, Hetzner wins."},
    "mixpanel":    {"display": "Mixpanel",     "rating": 4.4, "rating_count": 3201, "pricing_start": "0", "verdict": "The best product analytics tool for startups and scale-ups."},
    "pandadoc":    {"display": "PandaDoc",     "rating": 4.5, "rating_count": 4102, "pricing_start": "0", "verdict": "Best-in-class for sales teams sending proposals and contracts."},
    "se-ranking":  {"display": "SE Ranking",   "rating": 4.6, "rating_count": 1876, "pricing_start": "65", "verdict": "The smart upgrade for agencies who want Semrush-level data at 40% of the price."},
    "stripe":      {"display": "Stripe",       "rating": 4.6, "rating_count": 14203,"pricing_start": "0", "verdict": "The default choice for SaaS and marketplaces. Start here unless you process over $1M/year."},
    "supabase":    {"display": "Supabase",     "rating": 4.7, "rating_count": 6782, "pricing_start": "0", "verdict": "The best backend-as-a-service for developers who want full Postgres power without the ops overhead."},
    "vultr":       {"display": "Vultr",        "rating": 4.4, "rating_count": 5439, "pricing_start": "2.50", "verdict": "Best for globally distributed apps needing low-latency in Asia-Pacific and emerging markets."},
    "workable":    {"display": "Workable",     "rating": 4.3, "rating_count": 2987, "pricing_start": "189", "verdict": "The most complete ATS for teams hiring 10-50 people per year."},
}


def build_schemas(slug: str, d: dict) -> list[str]:
    """Return list of safe JSON-LD strings for this tool's review page."""
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": f"{d['display']} Review {YEAR}: Is It Worth It? Honest Verdict",
        "datePublished": TODAY,
        "dateModified": TODAY,
        "author": {"@type": "Person", "name": "Smith Elly", "url": "https://saaspare.org/about"},
        "publisher": {"@type": "Organization", "name": "SaaSpare", "url": "https://saaspare.org"},
        "description": f"Independent {d['display']} review {YEAR}: real pricing, hands-on pros and cons, and who should use it.",
    }
    software = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": d["display"],
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web",
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": str(d["rating"]),
            "bestRating": "5",
            "worstRating": "1",
            "ratingCount": d["rating_count"],
        },
        "offers": {
            "@type": "Offer",
            "price": d["pricing_start"],
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
        },
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f"Is {d['display']} worth it in {YEAR}?",
                "acceptedAnswer": {"@type": "Answer", "text": d["verdict"]},
            },
            {
                "@type": "Question",
                "name": f"How much does {d['display']} cost?",
                "acceptedAnswer": {"@type": "Answer", "text": f"{d['display']} starts at ${d['pricing_start']}/month. Check the pricing page for all plan details."},
            },
        ],
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://saaspare.org/"},
            {"@type": "ListItem", "position": 2, "name": "Reviews", "item": "https://saaspare.org/pages/"},
            {"@type": "ListItem", "position": 3, "name": f"{d['display']} Review {YEAR}", "item": f"https://saaspare.org/pages/{slug}-review-{YEAR}-is-it-worth-it-honest-verdict"},
        ],
    }
    return [
        json.dumps(article,   separators=(",", ":")),
        json.dumps(software,  separators=(",", ":")),
        json.dumps(faq,       separators=(",", ":")),
        json.dumps(breadcrumb,separators=(",", ":")),
    ]


def fix_review_page(path: Path, slug: str, d: dict) -> bool:
    html = path.read_text(encoding="utf-8", errors="replace")
    schemas = build_schemas(slug, d)

    # Replace all existing JSON-LD blocks with fresh safe ones
    blocks    = list(JSONLD_PAT.finditer(html))
    new_html  = html
    replaced  = 0

    for i, m in enumerate(blocks):
        schema_str = schemas[i] if i < len(schemas) else schemas[-1]
        new_block  = f'{m.group(1)}\n  {schema_str}\n  {m.group(3)}'
        new_html   = new_html.replace(m.group(0), new_block, 1)
        replaced  += 1

    # If page has fewer blocks than schemas, append missing ones before </head>
    for j in range(replaced, len(schemas)):
        inject = f'\n  <script type="application/ld+json">\n  {schemas[j]}\n  </script>'
        new_html = new_html.replace("</head>", inject + "\n</head>", 1)

    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        return True
    return False


if __name__ == "__main__":
    fixed = 0
    for slug, d in TOOLS.items():
        fname = f"{slug}-review-{YEAR}-is-it-worth-it-honest-verdict.html"
        p     = PAGES / fname
        if not p.exists():
            print(f"  [missing] {fname}")
            continue
        if fix_review_page(p, slug, d):
            fixed += 1
            print(f"  [fixed] {fname}")
        else:
            print(f"  [ok]    {fname}")
    print(f"\nFixed {fixed}/{len(TOOLS)} review pages")
