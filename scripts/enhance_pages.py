"""
Adds SEO/monetisation enhancements to all site/pages/*.html files:
  1. og:image meta tag (for Google Discover & social sharing)
  2. FAQPage JSON-LD structured data (for Google FAQ rich results)
  3. Internal cluster links in the .related section
  4. Removes the OTTO pixel so hard-coded SEO tags cannot be overridden
  5. Organization schema (SaaSpare entity for Knowledge Graph)
  6. Organization-only schema with no personal contact details
Idempotent via marker: <!-- enhanced-v2 -->
Run: .venv/Scripts/python scripts/enhance_pages.py
"""
import re, json
from pathlib import Path

PAGES = Path("site/pages")
DOMAIN = "https://saaspare.org"
MARKER = "<!-- enhanced-v2 -->"
OG_IMAGE = f"{DOMAIN}/og-default.png"
OTTO_PIXEL_RE = re.compile(r'\s*<script[^>]*id="sa-dynamic-optimization"[^>]*></script>', re.IGNORECASE)

ORG_SCHEMA = json.dumps({
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "SaaSpare",
    "url": DOMAIN,
    "logo": f"{DOMAIN}/og-default.png",
    "description": "Unbiased B2B SaaS comparisons, real pricing, and expert recommendations.",
    "foundingDate": "2026-04-18",
    "identifier": {
        "@type": "PropertyValue",
        "propertyID": "ABN",
        "value": "20602197525"
    },
    "sameAs": [
        "https://abr.business.gov.au/ABN/View?abn=20602197525"
    ]
}, ensure_ascii=False, indent=2)

# ---------------------------------------------------------------------------
# Cluster definitions for internal linking
# Each cluster: list of (slug, anchor_text) tuples
# ---------------------------------------------------------------------------
SEO_CLUSTER = [
    ("ahrefs-vs-semrush-which-is-better-in-2026", "Ahrefs vs Semrush"),
    ("ahrefs-pricing-2026-plans-costs-what-you-actually-pay", "Ahrefs Pricing"),
    ("ahrefs-review-2026-is-it-worth-it-honest-verdict", "Ahrefs Review"),
    ("ahrefs-free-trial-2026-how-to-get-it-step-by-step", "Ahrefs Free Trial"),
    ("semrush-pricing-2026-plans-costs-what-you-actually-pay", "Semrush Pricing"),
    ("semrush-review-2026-is-it-worth-it-honest-verdict", "Semrush Review"),
    ("surfer-seo-pricing-2026-plans-costs-what-you-actually-pay", "Surfer SEO Pricing"),
    ("surfer-seo-review-2026-is-it-worth-it-honest-verdict", "Surfer SEO Review"),
    ("best-seo-tools-for-small-business-2026", "Best SEO Tools"),
]

PM_CLUSTER = [
    ("notion-alternatives-2026-best-tools-compared", "Notion Alternatives"),
    ("notion-pricing-2026-plans-costs-what-you-actually-pay", "Notion Pricing"),
    ("notion-review-2026-is-it-worth-it-honest-verdict", "Notion Review"),
    ("asana-pricing-2026-plans-costs-what-you-actually-pay", "Asana Pricing"),
    ("asana-review-2026-is-it-worth-it-honest-verdict", "Asana Review"),
    ("clickup-pricing-2026-plans-costs-what-you-actually-pay", "ClickUp Pricing"),
    ("clickup-review-2026-is-it-worth-it-honest-verdict", "ClickUp Review"),
    ("best-project-management-software-for-startups-2026", "Best PM Tools for Startups"),
]

CRM_CLUSTER = [
    ("hubspot-alternatives-2026-best-tools-compared", "HubSpot Alternatives"),
    ("hubspot-pricing-2026-plans-costs-what-you-actually-pay", "HubSpot Pricing"),
    ("hubspot-review-2026-is-it-worth-it-honest-verdict", "HubSpot Review"),
    ("pipedrive-pricing-2026-plans-costs-what-you-actually-pay", "Pipedrive Pricing"),
    ("pipedrive-review-2026-is-it-worth-it-honest-verdict", "Pipedrive Review"),
    ("best-crm-for-startups-2026", "Best CRM for Startups"),
]

ECOMM_CLUSTER = [
    ("shopify-pricing-2026-plans-costs-what-you-actually-pay", "Shopify Pricing"),
    ("shopify-review-2026-is-it-worth-it-honest-verdict", "Shopify Review"),
    ("shopify-free-trial-2026-how-to-get-it-step-by-step", "Shopify Free Trial"),
    ("shopify-promo-code-2026-discounts-deals-that-actually-work", "Shopify Promo Code"),
]

ACCT_CLUSTER = [
    ("freshbooks-pricing-2026-plans-costs-what-you-actually-pay", "FreshBooks Pricing"),
    ("freshbooks-review-2026-is-it-worth-it-honest-verdict", "FreshBooks Review"),
    ("freshbooks-free-trial-2026-how-to-get-it-step-by-step", "FreshBooks Free Trial"),
    ("xero-pricing-2026-plans-costs-what-you-actually-pay", "Xero Pricing"),
    ("xero-review-2026-is-it-worth-it-honest-verdict", "Xero Review"),
]

SECURITY_CLUSTER = [
    ("1password-pricing-2026-plans-costs-what-you-actually-pay", "1Password Pricing"),
    ("1password-review-2026-is-it-worth-it-honest-verdict", "1Password Review"),
    ("1password-free-trial-2026-how-to-get-it-step-by-step", "1Password Free Trial"),
    ("best-devops-tools-for-security-compliance-in-2025", "Best DevOps Security Tools"),
]

ALL_CLUSTERS = [SEO_CLUSTER, PM_CLUSTER, CRM_CLUSTER, ECOMM_CLUSTER, ACCT_CLUSTER, SECURITY_CLUSTER]

def get_cluster_links(slug: str) -> list[tuple[str, str]]:
    for cluster in ALL_CLUSTERS:
        slugs = [s for s, _ in cluster]
        if slug in slugs:
            return [(s, t) for s, t in cluster if s != slug][:6]
    return []


# ---------------------------------------------------------------------------
# FAQ extraction
# ---------------------------------------------------------------------------
def extract_faqs(html: str) -> list[dict]:
    faqs = []
    for m in re.finditer(
        r'<details[^>]*class="faq-item"[^>]*>\s*<summary>(.*?)</summary>\s*<(?:p|div)>(.*?)</(?:p|div)>',
        html, re.DOTALL
    ):
        q = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        a = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if q and a:
            faqs.append({"q": q, "a": a})
    return faqs[:8]


def build_faq_schema(faqs: list[dict], page_url: str) -> str:
    if not faqs:
        return ""
    items = [
        {
            "@type": "Question",
            "name": f["q"],
            "acceptedAnswer": {"@type": "Answer", "text": f["a"]}
        }
        for f in faqs
    ]
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": items
    }
    return f'<script type="application/ld+json">\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n</script>'


# ---------------------------------------------------------------------------
# Patch one file
# ---------------------------------------------------------------------------
def patch(f: Path, html: str) -> str | None:
    html = OTTO_PIXEL_RE.sub("", html)
    if MARKER in html:
        return html

    slug = f.stem
    page_url = f"{DOMAIN}/pages/{f.name}"

    # 1. og:image
    if 'og:image' not in html:
        html = html.replace(
            '<meta property="og:type"',
            f'<meta property="og:image" content="{OG_IMAGE}">\n<meta property="og:type"',
            1
        )

    # 2. FAQPage JSON-LD
    faqs = extract_faqs(html)
    faq_schema = build_faq_schema(faqs, page_url)
    if faq_schema and 'FAQPage' not in html:
        html = html.replace('</head>', f'{faq_schema}\n</head>', 1)

    # 3. Internal cluster links
    cluster_links = get_cluster_links(slug)
    if cluster_links:
        link_html = "".join(
            f'<a href="{DOMAIN}/pages/{s}.html">{t}</a>'
            for s, t in cluster_links
        )
        # Strip any prior injected block first so re-runs (even without the
        # <head> marker surviving a regen) can never duplicate this section.
        html = re.sub(
            r'\s*<div class="related section">\s*<h3>Related Comparisons</h3>.*?</div>',
            '', html, flags=re.DOTALL
        )
        # Append to existing .related section if present, else inject before </body>
        if 'class="related"' in html:
            html = re.sub(
                r'(class="related"[^>]*>.*?<div[^>]*>)(.*?)(</div>\s*</div>)',
                lambda m: m.group(1) + m.group(2) + link_html + m.group(3),
                html, count=1, flags=re.DOTALL
            )
        else:
            related_section = f'''<div class="related section">
<h3>Related Comparisons</h3>
{link_html}
</div>'''
            html = html.replace('</body>', f'{related_section}\n</body>', 1)

    # 4. Organization schema
    if '"@type":"Organization"' not in html and '"@type": "Organization"' not in html:
        org_script = f'<script type="application/ld+json">\n{ORG_SCHEMA}\n</script>'
        html = html.replace('</head>', f'{org_script}\n</head>', 1)

    # 6. Marker
    html = html.replace('</head>', f'{MARKER}\n</head>', 1)
    return html


def main():
    enhanced = skipped = errors = 0
    for f in sorted(PAGES.glob("*.html")):
        try:
            src = f.read_text(encoding="utf-8", errors="ignore")
            out = patch(f, src)
            if out is None:
                skipped += 1
                continue
            f.write_text(out, encoding="utf-8")
            enhanced += 1
        except Exception as e:
            print(f"  ERROR {f.name}: {e}")
            errors += 1
    print(f"Enhanced: {enhanced} | Skipped: {skipped} | Errors: {errors}")


if __name__ == "__main__":
    main()
