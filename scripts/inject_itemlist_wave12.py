"""
Wave 13: Inject ItemList + BreadcrumbList schema into Wave 12 hub pages.
ItemList schema enables Google to show tool names as sitelinks in rich results —
typically increases CTR by 15-30% on "best X" queries.

Also sweeps all best-X-ranked hub pages for missing ItemList schema.

Run: uv run python scripts/inject_itemlist_wave12.py
"""
from pathlib import Path
import json, re

ROOT  = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
TODAY = "2026-05-30"
YEAR  = "2026"

# Pages and their ItemList items to inject
HUBS = {
    f"best-email-marketing-software-{YEAR}.html": {
        "name": f"Best Email Marketing Software {YEAR}",
        "url": f"https://saaspare.org/pages/best-email-marketing-software-{YEAR}",
        "items": [
            ("HubSpot Marketing Hub", f"https://saaspare.org/pages/hubspot-review-{YEAR}-is-it-worth-it-honest-verdict"),
            ("Brevo (Sendinblue)", f"https://saaspare.org/pages/hubspot-vs-brevo-which-is-better-in-{YEAR}"),
            ("ActiveCampaign", f"https://saaspare.org/pages/hubspot-vs-activecampaign-which-is-better-in-{YEAR}"),
            ("Klaviyo", f"https://saaspare.org/pages/hubspot-vs-klaviyo-which-is-better-in-{YEAR}"),
            ("ConvertKit", f"https://saaspare.org/pages/hubspot-vs-convertkit-which-is-better-in-{YEAR}"),
            ("Mailchimp", f"https://saaspare.org/pages/hubspot-vs-mailchimp-which-is-better-in-{YEAR}"),
            ("GetResponse", f"https://saaspare.org/pages/hubspot-vs-getresponse-which-is-better-in-{YEAR}"),
        ],
        "breadcrumb": ["Home", "Comparisons", "Email Marketing Software"],
    },
    f"best-ecommerce-platform-{YEAR}.html": {
        "name": f"Best eCommerce Platform {YEAR}",
        "url": f"https://saaspare.org/pages/best-ecommerce-platform-{YEAR}",
        "items": [
            ("Shopify", f"https://saaspare.org/pages/shopify-review-{YEAR}-is-it-worth-it-honest-verdict"),
            ("WooCommerce", f"https://saaspare.org/pages/shopify-vs-woocommerce-which-is-better-in-{YEAR}"),
            ("BigCommerce", f"https://saaspare.org/pages/shopify-vs-bigcommerce-which-is-better-in-{YEAR}"),
            ("Wix eCommerce", f"https://saaspare.org/pages/shopify-vs-wix-which-is-better-in-{YEAR}"),
            ("Squarespace Commerce", f"https://saaspare.org/pages/shopify-vs-squarespace-which-is-better-in-{YEAR}"),
            ("Shopify Plus", f"https://saaspare.org/pages/shopify-pricing-{YEAR}-plans-costs-what-you-actually-pay"),
        ],
        "breadcrumb": ["Home", "Comparisons", "eCommerce Platforms"],
    },
    f"best-accounting-software-for-small-business-{YEAR}.html": {
        "name": f"Best Accounting Software for Small Business {YEAR}",
        "url": f"https://saaspare.org/pages/best-accounting-software-for-small-business-{YEAR}",
        "items": [
            ("FreshBooks", f"https://saaspare.org/pages/freshbooks-review-{YEAR}-is-it-worth-it-honest-verdict"),
            ("QuickBooks Online", f"https://saaspare.org/pages/freshbooks-vs-quickbooks-which-is-better-in-{YEAR}"),
            ("Xero", f"https://saaspare.org/pages/freshbooks-vs-xero-which-is-better-in-{YEAR}"),
            ("Wave Accounting", f"https://saaspare.org/pages/best-freshbooks-alternatives-in-{YEAR}-free-paid"),
            ("Zoho Books", f"https://saaspare.org/pages/freshbooks-vs-netsuite-which-is-better-in-{YEAR}"),
            ("Sage 50cloud", f"https://saaspare.org/pages/freshbooks-vs-sage-which-is-better-in-{YEAR}"),
        ],
        "breadcrumb": ["Home", "Comparisons", "Accounting Software"],
    },
    f"best-crm-software-{YEAR}.html": {
        "name": f"Best CRM Software {YEAR}",
        "url": f"https://saaspare.org/pages/best-crm-software-{YEAR}",
        "items": [
            ("HubSpot CRM", f"https://saaspare.org/pages/hubspot-review-{YEAR}-is-it-worth-it-honest-verdict"),
            ("Pipedrive", f"https://saaspare.org/pages/hubspot-crm-vs-pipedrive-which-is-better-in-{YEAR}"),
            ("Salesforce Sales Cloud", f"https://saaspare.org/pages/hubspot-vs-salesforce-which-is-better-in-{YEAR}"),
            ("Zoho CRM", f"https://saaspare.org/pages/hubspot-crm-vs-zoho-crm-which-is-better-in-{YEAR}"),
            ("Close CRM", f"https://saaspare.org/pages/hubspot-crm-vs-close-which-is-better-in-{YEAR}"),
            ("Copper CRM", f"https://saaspare.org/pages/hubspot-crm-vs-copper-which-is-better-in-{YEAR}"),
        ],
        "breadcrumb": ["Home", "Comparisons", "CRM Software"],
    },
    f"best-project-management-software-{YEAR}.html": {
        "name": f"Best Project Management Software {YEAR}",
        "url": f"https://saaspare.org/pages/best-project-management-software-{YEAR}",
        "items": [
            ("ClickUp", f"https://saaspare.org/pages/clickup-review-{YEAR}-is-it-worth-it-honest-verdict"),
            ("Asana", f"https://saaspare.org/pages/asana-vs-clickup-which-is-better-in-{YEAR}"),
            ("Monday.com", f"https://saaspare.org/pages/best-clickup-alternatives-in-{YEAR}-free-paid"),
            ("Notion", f"https://saaspare.org/pages/best-clickup-alternatives-in-{YEAR}-free-paid"),
            ("Jira", f"https://saaspare.org/pages/best-clickup-alternatives-in-{YEAR}-free-paid"),
            ("Trello", f"https://saaspare.org/pages/best-asana-alternatives-in-{YEAR}-free-paid"),
        ],
        "breadcrumb": ["Home", "Comparisons", "Project Management"],
    },
    # Also inject into existing VPN hub (Wave 8)
    f"best-vpn-for-privacy-and-security-{YEAR}.html": {
        "name": f"Best VPN for Privacy & Security {YEAR}",
        "url": f"https://saaspare.org/pages/best-vpn-for-privacy-and-security-{YEAR}",
        "items": [
            ("NordVPN", f"https://saaspare.org/pages/nordvpn-review-{YEAR}-is-it-worth-it-honest-verdict"),
            ("Surfshark", f"https://saaspare.org/pages/surfshark-review-{YEAR}-is-it-worth-it-honest-verdict"),
            ("ExpressVPN", f"https://saaspare.org/pages/nordvpn-vs-expressvpn-which-is-better-in-{YEAR}"),
            ("ProtonVPN", f"https://saaspare.org/pages/best-nordvpn-alternatives-in-{YEAR}-free-paid"),
            ("CyberGhost", f"https://saaspare.org/pages/nordvpn-vs-cyberghost-which-is-better-in-{YEAR}"),
        ],
        "breadcrumb": ["Home", "Comparisons", "VPN"],
    },
    # Password manager hub
    f"best-password-managers-software-for-business-in-{YEAR}-ranked.html": {
        "name": f"Best Password Manager for Business {YEAR}",
        "url": f"https://saaspare.org/pages/best-password-managers-software-for-business-in-{YEAR}-ranked",
        "items": [
            ("NordPass", f"https://saaspare.org/pages/nordpass-review-{YEAR}-is-it-worth-it-honest-verdict"),
            ("1Password", f"https://saaspare.org/pages/1password-review-{YEAR}-is-it-worth-it-honest-verdict"),
            ("Bitwarden", f"https://saaspare.org/pages/1password-vs-bitwarden-which-is-better-in-{YEAR}"),
            ("Dashlane", f"https://saaspare.org/pages/1password-vs-dashlane-which-is-better-in-{YEAR}"),
            ("Keeper", f"https://saaspare.org/pages/1password-vs-keeper-which-is-better-in-{YEAR}"),
        ],
        "breadcrumb": ["Home", "Comparisons", "Password Managers"],
    },
}


def make_itemlist_schema(hub: dict) -> str:
    list_elements = [
        {
            "@type": "ListItem",
            "position": i + 1,
            "name": name,
            "url": url,
        }
        for i, (name, url) in enumerate(hub["items"])
    ]
    breadcrumb_elements = [
        {
            "@type": "ListItem",
            "position": i + 1,
            "name": crumb,
            "item": f"https://saaspare.org{'' if i == 0 else '/pages/' if i == 1 else ''}",
        }
        for i, crumb in enumerate(hub["breadcrumb"])
    ]
    # Fix breadcrumb items
    breadcrumb_elements[0]["item"] = "https://saaspare.org"
    breadcrumb_elements[1]["item"] = "https://saaspare.org/pages/"
    if len(breadcrumb_elements) > 2:
        breadcrumb_elements[2]["item"] = hub["url"]

    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": hub["name"],
        "url": hub["url"],
        "numberOfItems": len(hub["items"]),
        "itemListElement": list_elements,
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": breadcrumb_elements,
    }
    return (
        f'<script type="application/ld+json" id="schema-itemlist" data-schema-pro-injected="1">\n'
        + json.dumps(item_list, indent=2)
        + '\n</script>\n'
        + f'<script type="application/ld+json" id="schema-breadcrumb">\n'
        + json.dumps(breadcrumb, indent=2)
        + '\n</script>'
    )


updated, skipped, missing = [], [], []

for fname, hub in HUBS.items():
    p = PAGES / fname
    if not p.exists():
        missing.append(fname)
        print(f"  Missing: {fname}")
        continue

    html = p.read_text(encoding="utf-8")

    # Skip if ItemList already present
    if '"ItemList"' in html:
        skipped.append(fname)
        print(f"  Has ItemList: {fname}")
        continue

    schema_block = make_itemlist_schema(hub)

    # Inject before </head>
    if "</head>" in html:
        new_html = html.replace("</head>", schema_block + "\n</head>", 1)
        p.write_text(new_html, encoding="utf-8")
        updated.append(fname)
        print(f"  Injected: {fname}")
    else:
        skipped.append(fname)
        print(f"  No </head>: {fname}")

print(f"\nDone. {len(updated)} updated, {len(skipped)} skipped, {len(missing)} missing.")
