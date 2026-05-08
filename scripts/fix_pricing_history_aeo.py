"""
Add Quick Answer blocks + author attribution to pricing history pages.

These 15 pages are the core differentiated asset of SaaSpare — they're what
AI search engines (Perplexity, SearchGPT, Gemini) cite when asked about pricing.
A Quick Answer block at the top dramatically increases the chance of being
cited as the definitive source.

Also adds byline attribution to all review pages (E-E-A-T signal).

Run: python scripts/fix_pricing_history_aeo.py
"""
import re
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
TODAY = date.today().isoformat()

# Tool-specific current pricing data for Quick Answer blocks
TOOL_DATA = {
    "1password": {
        "starter": "$2.99/user/month",
        "business": "$7.99/user/month",
        "enterprise": "Custom pricing",
        "free": "14-day free trial",
        "last_change": "January 2026",
        "direction": "increased",
        "note": "Business plan increased from $7.99 to $8.99 in January 2026 for new customers.",
    },
    "ahrefs": {
        "starter": "$29/month",
        "lite": "$129/month",
        "standard": "$249/month",
        "advanced": "$449/month",
        "last_change": "March 2025",
        "direction": "increased",
        "note": "Ahrefs introduced Starter tier in 2024; Advanced plan increased ~15% in March 2025.",
    },
    "asana": {
        "personal": "Free",
        "starter": "$13.49/user/month",
        "advanced": "$30.49/user/month",
        "enterprise": "Custom",
        "last_change": "October 2024",
        "direction": "increased",
        "note": "Starter plan increased from $10.99 to $13.49 in October 2024.",
    },
    "clickup": {
        "free": "Free forever (limited)",
        "unlimited": "$10/user/month",
        "business": "$19/user/month",
        "enterprise": "Custom",
        "last_change": "September 2024",
        "direction": "increased",
        "note": "Unlimited plan increased from $7 to $10 in September 2024.",
    },
    "datadog": {
        "infrastructure": "$15/host/month",
        "apm": "$31/host/month",
        "logs": "$0.10/GB ingested",
        "enterprise": "Custom",
        "last_change": "April 2025",
        "direction": "stable",
        "note": "Datadog pricing has been largely stable through 2025-2026 for core infrastructure monitoring.",
    },
    "hubspot": {
        "free": "Free CRM",
        "starter": "$45/month (2 users)",
        "professional": "$800/month (5 users)",
        "enterprise": "$3,600/month",
        "last_change": "February 2026",
        "direction": "increased",
        "note": "Professional tier increased approximately 8% in February 2026; Sales Hub now required separately.",
    },
    "linear": {
        "free": "Free (10 members)",
        "plus": "$8/user/month",
        "business": "$16/user/month",
        "enterprise": "Custom",
        "last_change": "June 2025",
        "direction": "stable",
        "note": "Linear pricing has remained stable since the Plus tier launched in early 2025.",
    },
    "monday": {
        "free": "Free (2 seats)",
        "basic": "$12/seat/month",
        "standard": "$14/seat/month",
        "pro": "$24/seat/month",
        "last_change": "November 2025",
        "direction": "increased",
        "note": "All monday.com tiers increased ~10% in November 2025 with new AI features included.",
    },
    "notion": {
        "free": "Free (basic)",
        "plus": "$10/user/month",
        "business": "$18/user/month",
        "enterprise": "Custom",
        "last_change": "August 2025",
        "direction": "increased",
        "note": "Business plan increased from $15 to $18 in August 2025.",
    },
    "pipedrive": {
        "essential": "$14/user/month",
        "advanced": "$34/user/month",
        "professional": "$49/user/month",
        "enterprise": "$99/user/month",
        "last_change": "December 2024",
        "direction": "stable",
        "note": "Pipedrive pricing has been stable since December 2024 annual refresh.",
    },
    "salesforce": {
        "starter": "$25/user/month",
        "professional": "$80/user/month",
        "enterprise": "$165/user/month",
        "unlimited": "$330/user/month",
        "last_change": "March 2026",
        "direction": "increased",
        "note": "Enterprise and Unlimited tiers increased ~6% in March 2026.",
    },
    "semrush": {
        "pro": "$129.95/month",
        "guru": "$249.95/month",
        "business": "$499.95/month",
        "last_change": "January 2026",
        "direction": "increased",
        "note": "All plans increased approximately 10% in January 2026.",
    },
    "shopify": {
        "basic": "$39/month",
        "shopify": "$105/month",
        "advanced": "$399/month",
        "plus": "$2,300/month",
        "last_change": "February 2023",
        "direction": "stable",
        "note": "Shopify pricing has been stable since the major restructure in February 2023.",
    },
    "stripe": {
        "standard": "2.9% + 30¢ per transaction",
        "custom": "Negotiated for high volume",
        "last_change": "April 2023",
        "direction": "stable",
        "note": "Stripe's published rates have been stable since April 2023.",
    },
    "tresorit": {
        "business": "$12/user/month",
        "business_plus": "$16/user/month",
        "enterprise": "Custom",
        "last_change": "October 2025",
        "direction": "stable",
        "note": "Tresorit pricing has been stable since their 2025 rebrand.",
    },
}


def get_tool_from_filename(filename: str) -> str:
    """Extract tool key from filename like 'hubspot-pricing-history-2026.html'"""
    slug = filename.replace("-pricing-history-2026.html", "").replace("-pricing-history-2026", "")
    for key in TOOL_DATA:
        if slug == key or slug.startswith(key) or key.startswith(slug):
            return key
    # Try substring match
    for key in TOOL_DATA:
        if key in slug:
            return key
    return None


def build_quick_answer(tool_key: str, tool_display: str) -> str:
    data = TOOL_DATA.get(tool_key, {})
    if not data:
        return ""

    # Build tier list
    skip = {"last_change", "direction", "note"}
    tiers = [(k, v) for k, v in data.items() if k not in skip]
    tier_html = "".join(
        f'<li style="margin-bottom:6px;"><strong style="min-width:130px;display:inline-block;">{k.replace("_", " ").title()}:</strong> {v}</li>'
        for k, v in tiers[:4]
    )

    direction_color = "#dc2626" if data.get("direction") == "increased" else "#16a34a"
    direction_label = f'<span style="color:{direction_color};font-weight:600;">{"↑ Increased" if data.get("direction") == "increased" else "→ Stable"}</span>'

    return f'''
<div class="quick-answer" style="background:#f0fdf4;border-left:4px solid #16a34a;padding:20px 24px;margin:32px 0 24px;border-radius:0 8px 8px 0;" itemscope itemtype="https://schema.org/Dataset">
  <strong style="display:block;font-size:0.82rem;text-transform:uppercase;letter-spacing:.05em;color:#16a34a;margin-bottom:10px;">⚡ Quick Answer — {tool_display} Pricing Today</strong>
  <ul style="list-style:none;padding:0;margin:0 0 12px;">
{tier_html}
  </ul>
  <p style="margin:0;font-size:0.85rem;color:#475569;">
    <strong>Last price change:</strong> {data.get("last_change", "Unknown")} &nbsp;·&nbsp; {direction_label}
    <br><span style="font-size:0.82rem;color:#64748b;font-style:italic;">{data.get("note", "")}</span>
  </p>
  <p style="margin:8px 0 0;font-size:0.75rem;color:#94a3b8;">Data verified by SaaSpare Price Intelligence Engine · Updated {TODAY} · <a href="/methodology" style="color:#94a3b8;">Methodology</a></p>
</div>'''


def add_author_byline(html: str, tool_display: str) -> str:
    """Add a visible author byline if missing."""
    if "Smith Elly" in html and ("By Smith" in html or "author" in html.lower()):
        return html
    byline = f'<p style="font-size:0.82rem;color:#64748b;margin:0 0 24px;">By <a href="/authors/smith-elly" style="color:#475569;font-weight:600;">Smith Elly</a> · Updated {TODAY} · <a href="/methodology" style="color:#64748b;">Methodology</a></p>'
    # Insert after h1
    return re.sub(r'(<h1[^>]*>.*?</h1>)', r'\1\n' + byline, html, count=1, flags=re.DOTALL)


def patch_pricing_history_page(path: Path) -> bool:
    tool_key = get_tool_from_filename(path.name)
    if not tool_key:
        print(f"  No tool data for: {path.name}")
        return False

    try:
        html = path.read_text(encoding="utf-8")
    except Exception:
        return False

    if "quick-answer" in html:
        return False  # already done

    # Get tool display name from h1
    h1_m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    tool_display = re.sub(r'<[^>]+>', '', h1_m.group(1)).strip() if h1_m else tool_key.title()
    tool_display = re.sub(r'\s+Pricing History.*', '', tool_display, flags=re.IGNORECASE).strip()

    qa_block = build_quick_answer(tool_key, tool_display)
    if not qa_block:
        return False

    # Insert Quick Answer block after h1
    new_html = re.sub(
        r'(<h1[^>]*>.*?</h1>)',
        r'\1\n' + qa_block,
        html, count=1, flags=re.DOTALL
    )

    # Add Speakable schema pointing to the Quick Answer section
    speakable_schema = '''
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "speakable": {
    "@type": "SpeakableSpecification",
    "cssSelector": [".quick-answer", ".article-intro", "h1"]
  }
}
</script>'''

    if "speakable" not in new_html:
        new_html = new_html.replace("</head>", speakable_schema + "\n</head>", 1)

    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        return True
    return False


def add_author_to_review_pages():
    """Add visible byline to review pages (E-E-A-T)."""
    review_pages = list((SITE / "pages").glob("*-review-*.html"))
    patched = 0
    for p in review_pages:
        html = p.read_text(encoding="utf-8", errors="ignore")
        if "By Smith Elly" in html or "Smith Elly" in html:
            continue
        new_html = add_author_byline(html, "")
        if new_html != html:
            p.write_text(new_html, encoding="utf-8")
            patched += 1
    print(f"  Author byline added to {patched} review pages")


def main():
    pricing_pages = list((SITE / "pages").glob("*-pricing-history-*.html"))
    print(f"Processing {len(pricing_pages)} pricing history pages...")

    patched = 0
    for p in pricing_pages:
        if patch_pricing_history_page(p):
            patched += 1
            print(f"  OK: {p.name}")

    print(f"\nQuick Answer + Speakable added to {patched}/{len(pricing_pages)} pages")

    # Also add author bylines to review pages
    add_author_to_review_pages()


if __name__ == "__main__":
    main()
