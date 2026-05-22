"""
Generate per-vertical OG images so social shares don't all show the same image.

Per the SEO auditor: identical og:image on 1,012 pages kills social CTR.
This script creates lightweight SVG-based OG images per category and routes
each page to the appropriate one based on URL pattern.

Run: python scripts/generate_og_images.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
OG_DIR = SITE / "og"
OG_DIR.mkdir(exist_ok=True)

# Category -> URL fragment patterns -> SVG color & label
CATEGORIES = {
    "crm": {
        "patterns": ["hubspot", "salesforce", "pipedrive", "zoho-crm", "monday-sales"],
        "color": "#0ea5e9", "label": "B2B CRM Comparison",
    },
    "pm": {
        "patterns": ["asana", "monday", "clickup", "trello", "linear", "jira", "notion", "basecamp", "wrike", "smartsheet"],
        "color": "#8b5cf6", "label": "Project Management",
    },
    "seo": {
        "patterns": ["semrush", "ahrefs", "moz", "surfer-seo", "se-ranking", "frase", "spyfu", "rankmath", "clearscope"],
        "color": "#16a34a", "label": "SEO Tools",
    },
    "security": {
        "patterns": ["1password", "bitwarden", "lastpass", "dashlane", "keeper", "nordpass", "tresorit", "okta", "duo", "cloudflare-access"],
        "color": "#dc2626", "label": "Security & Privacy",
    },
    "video": {
        "patterns": ["zoom", "webex", "google-meet", "ms-teams", "microsoft-teams", "around", "whereby", "riverside-fm", "streamyard", "loom"],
        "color": "#f97316", "label": "Video & Communication",
    },
    "marketing": {
        "patterns": ["mailchimp", "activecampaign", "klaviyo", "getresponse", "brevo", "marketo", "intercom"],
        "color": "#ec4899", "label": "Marketing Automation",
    },
    "vpn": {
        "patterns": ["nordvpn", "nordlayer", "expressvpn", "tailscale", "twingate", "zscaler", "perimeter-81", "wireguard", "openvpn"],
        "color": "#3b82f6", "label": "VPN & Network Security",
    },
    "hr": {
        "patterns": ["bamboohr", "gusto", "rippling", "deel", "remote", "workday", "adp", "lattice", "culture-amp", "lever", "greenhouse", "workable"],
        "color": "#10b981", "label": "HR & Payroll",
    },
    "finance": {
        "patterns": ["ramp", "brex", "mercury", "stripe", "expensify", "xero", "quickbooks", "freshbooks", "wave", "chargebee", "recurly", "bill-com"],
        "color": "#0f766e", "label": "Finance & Spend",
    },
    "ecommerce": {
        "patterns": ["shopify", "bigcommerce", "woocommerce", "magento", "wix"],
        "color": "#a855f7", "label": "Ecommerce Platforms",
    },
    "infra": {
        "patterns": ["aws", "supabase", "hetzner", "vercel", "netlify", "heroku", "render", "vultr", "linode", "digitalocean", "datadog", "sentry", "google-cloud"],
        "color": "#ea580c", "label": "Cloud & DevOps",
    },
    "ai": {
        "patterns": ["openai", "anthropic", "claude", "cohere", "jasper", "copy-ai", "writesonic", "pinecone", "weaviate", "hugging-face"],
        "color": "#7c3aed", "label": "AI Tools",
    },
    "design": {
        "patterns": ["canva", "figma", "miro", "mural", "lucidspark", "adobe-express"],
        "color": "#f59e0b", "label": "Design & Collaboration",
    },
}

SVG_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="{color}"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect x="60" y="60" width="1080" height="510" rx="20" fill="none" stroke="rgba(255,255,255,0.18)" stroke-width="2"/>
  <text x="100" y="160" font-family="Inter, Arial, sans-serif" font-weight="800" font-size="38" fill="#ffffff" opacity="0.85">SaaSpare</text>
  <text x="100" y="200" font-family="Inter, Arial, sans-serif" font-weight="500" font-size="20" fill="#ffffff" opacity="0.6">{label}</text>
  <text x="100" y="370" font-family="Inter, Arial, sans-serif" font-weight="800" font-size="56" fill="#ffffff">{title}</text>
  <text x="100" y="430" font-family="Inter, Arial, sans-serif" font-weight="500" font-size="24" fill="#ffffff" opacity="0.75">{subtitle}</text>
  <text x="100" y="520" font-family="Inter, Arial, sans-serif" font-weight="600" font-size="18" fill="#ffffff" opacity="0.5">Independent B2B SaaS Comparisons . No paid rankings</text>
  <circle cx="1080" cy="100" r="30" fill="#ffffff" opacity="0.1"/>
  <text x="1080" y="108" font-family="Inter, Arial, sans-serif" font-weight="800" font-size="24" fill="#ffffff" text-anchor="middle">{year}</text>
</svg>"""


def get_category(filename: str) -> str:
    name = filename.lower()
    for cat, data in CATEGORIES.items():
        for pat in data["patterns"]:
            if pat in name:
                return cat
    return "default"


def gen_category_svg(cat: str, data: dict):
    """Generate one default SVG per category."""
    svg = SVG_TEMPLATE.format(
        color=data["color"],
        label=data["label"],
        title=data["label"],
        subtitle="Real pricing. Honest comparisons. 2026 data.",
        year="2026",
    )
    (OG_DIR / f"{cat}.svg").write_text(svg, encoding="utf-8")


def main():
    # 1. Generate one SVG per category
    for cat, data in CATEGORIES.items():
        gen_category_svg(cat, data)
        print(f"  + og/{cat}.svg")

    # 2. Default fallback
    gen_category_svg("default", {"color": "#475569", "label": "B2B SaaS Comparisons"})

    # 3. Update og:image meta tag on every page to point to the category SVG
    pages = list((SITE / "pages").glob("*.html")) + list(SITE.glob("best-*.html"))
    updated = 0
    for p in pages:
        try:
            html = p.read_text(encoding="utf-8")
        except Exception:
            continue
        cat = get_category(p.name)
        new_og = f"https://saaspare.org/og/{cat}.svg"
        # Only replace if currently the generic /og-default.png
        new_html = re.sub(
            r'(<meta property="og:image" content=")https://saaspare\.org/og-default\.png(")',
            rf'\1{new_og}\2',
            html, count=1
        )
        if new_html != html:
            p.write_text(new_html, encoding="utf-8")
            updated += 1

    print(f"\n  Updated og:image on {updated} pages with category-specific SVGs")


if __name__ == "__main__":
    main()
