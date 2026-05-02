#!/usr/bin/env python3
"""Build site/categories.html — browse-by-category hub page."""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES_DIR = ROOT / "site" / "pages"
OUT = ROOT / "site" / "categories.html"

GA4 = """<script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-RLYVYV8WQJ');</script>"""

CATEGORIES = {
    "CRM & Sales": {
        "color": "#3B82F6",
        "emoji": "💼",
        "tools": ["hubspot", "salesforce", "pipedrive", "zoho-crm", "close", "copper", "freshsales", "nutshell", "keap", "insightly"],
    },
    "Project Management": {
        "color": "#8B5CF6",
        "emoji": "📋",
        "tools": ["monday-com", "asana", "clickup", "notion", "linear", "basecamp", "wrike", "smartsheet", "airtable", "jira"],
    },
    "SEO & Content": {
        "color": "#10B981",
        "emoji": "🔍",
        "tools": ["semrush", "ahrefs", "moz", "surfer-seo", "clearscope", "frase-io", "se-ranking", "mangools", "rankmath", "spyfu"],
    },
    "HR & Payroll": {
        "color": "#F59E0B",
        "emoji": "👥",
        "tools": ["rippling", "deel", "bamboohr", "gusto", "adp", "remote-com", "workable", "greenhouse", "lever", "lattice"],
    },
    "Finance & Accounting": {
        "color": "#EF4444",
        "emoji": "💰",
        "tools": ["xero", "quickbooks", "freshbooks", "ramp", "brex", "chargebee", "recurly", "stripe", "paddle", "maxio"],
    },
    "Dev Tools & Cloud": {
        "color": "#06B6D4",
        "emoji": "⚙️",
        "tools": ["datadog", "sentry", "vercel", "netlify", "cloudflare", "aws", "digitalocean", "vultr", "supabase", "github"],
    },
    "Security & Identity": {
        "color": "#6366F1",
        "emoji": "🔒",
        "tools": ["1password", "bitwarden", "okta", "nordlayer", "nordpass", "crowdstrike", "snyk", "zscaler", "sentinelone", "duo-security"],
    },
    "AI & Writing Tools": {
        "color": "#EC4899",
        "emoji": "🤖",
        "tools": ["jasper-ai", "copy-ai", "anthropic-claude", "chatgpt", "perplexity", "frase-io", "clearscope", "surfer-seo", "writesonic", "rytr"],
    },
    "E-Signature & Legal": {
        "color": "#84CC16",
        "emoji": "✍️",
        "tools": ["docusign", "pandadoc", "ironclad", "concord", "adobe-sign", "hellosign", "contractbook", "juro", "agiloft", "icertis"],
    },
    "Video & Communication": {
        "color": "#F97316",
        "emoji": "🎬",
        "tools": ["loom", "riverside-fm", "streamyard", "descript", "zoom", "microsoft-teams", "google-meet", "slack", "discord", "around"],
    },
    "Email & Marketing": {
        "color": "#14B8A6",
        "emoji": "📧",
        "tools": ["mailchimp", "brevo", "activecampaign", "klaviyo", "hubspot", "convertkit", "drip", "moosend", "omnisend", "campaign-monitor"],
    },
    "Analytics & Data": {
        "color": "#A855F7",
        "emoji": "📊",
        "tools": ["mixpanel", "amplitude", "hotjar", "fullstory", "segment", "heap", "posthog", "june", "june-so", "clearbit"],
    },
}


def get_tool_pages(tool_slug):
    """Get all page types for a tool slug."""
    pages = []
    all_pages = {f[:-5] for f in os.listdir(PAGES_DIR) if f.endswith(".html") and f != "index.html"}
    for page in all_pages:
        if tool_slug in page:
            pages.append(page)
    return pages


def slug_to_label(slug):
    """Convert slug to display name."""
    from publisher.seo_tags import _title_case_slug
    return _title_case_slug(slug)


def build_tool_card(tool_slug, color):
    # Find associated pages
    all_pages = {f[:-5] for f in os.listdir(PAGES_DIR) if f.endswith(".html") and f != "index.html"}
    page_types = {}
    for page in all_pages:
        if tool_slug not in page:
            continue
        if f"-vs-" in page and tool_slug in page.split("-vs-")[0]:
            page_types.setdefault("compare", page)
        elif "pricing-2026" in page or "pricing-20" in page:
            page_types.setdefault("pricing", page)
        elif "coupon-code" in page or "promo-code" in page:
            page_types.setdefault("coupon", page)
        elif "alternatives" in page:
            page_types.setdefault("alternatives", page)
        elif "review-2026" in page:
            page_types.setdefault("review", page)
        elif "free-trial" in page:
            page_types.setdefault("trial", page)
        elif "free-plan" in page or page.startswith("does-"):
            page_types.setdefault("free-plan", page)

    label = slug_to_label(tool_slug)
    links_html = ""
    tag_map = {
        "pricing": ("💲", "Pricing"),
        "compare": ("⚖️", "Compare"),
        "review": ("⭐", "Review"),
        "trial": ("🆓", "Free Trial"),
        "free-plan": ("🎁", "Free Plan"),
        "coupon": ("🏷️", "Coupon"),
        "alternatives": ("🔄", "Alternatives"),
    }
    for key, (icon, name) in tag_map.items():
        if key in page_types:
            links_html += f'<a href="/pages/{page_types[key]}" class="tag" aria-label="{name} for {label}">{icon} {name}</a>\n'

    if not links_html:
        return ""

    return f"""<div class="tool-card" style="border-top:3px solid {color}">
  <div class="tool-name">{label}</div>
  <div class="tags">{links_html}</div>
</div>"""


def build_categories_html():
    import sys
    sys.path.insert(0, str(ROOT))

    # Gather all pages for stats
    all_pages = {f[:-5] for f in os.listdir(PAGES_DIR) if f.endswith(".html") and f != "index.html"}
    total = len(all_pages)

    category_sections = ""
    for cat_name, cat_data in CATEGORIES.items():
        color = cat_data["color"]
        emoji = cat_data["emoji"]
        tools = cat_data["tools"]
        cards = ""
        for tool in tools:
            card = build_tool_card(tool, color)
            if card:
                cards += card + "\n"
        if not cards:
            # Generate placeholder cards for tools without pages
            for tool in tools[:5]:
                lbl = slug_to_label(tool)
                cards += f'<div class="tool-card" style="border-top:3px solid {color}"><div class="tool-name">{lbl}</div><div class="tags"><span class="tag-placeholder">Coming soon</span></div></div>\n'

        category_sections += f"""
<section class="category-section" id="{cat_name.lower().replace(' & ', '-').replace(' ', '-')}">
  <h2 class="category-heading" style="color:{color}">{emoji} {cat_name}</h2>
  <div class="tool-grid">
{cards}  </div>
</section>
"""

    # Build A-Z tool index
    tools_all = sorted(set(t for c in CATEGORIES.values() for t in c["tools"]))
    az_links = " ".join(
        f'<a href="/pages/{t}-pricing-2026-plans-costs" class="az-link">{slug_to_label(t)}</a>'
        for t in tools_all
        if f"{t}-pricing-2026-plans-costs" in all_pages
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Browse SaaS Tools by Category 2026 | SaaSpare</title>
<meta name="description" content="Browse {total}+ SaaS comparison pages by category. Find pricing, reviews, free trials, coupons, and alternatives for every major B2B tool in 2026.">
<link rel="canonical" href="https://saaspare.org/categories">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{GA4}
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "SaaS Tool Categories | SaaSpare",
  "description": "Browse {total}+ SaaS comparison, pricing, review, and alternative pages by category.",
  "url": "https://saaspare.org/categories",
  "publisher": {{"@type": "Organization", "name": "SaaSpare", "url": "https://saaspare.org"}}
}}
</script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:system-ui,sans-serif;background:#f8fafc;color:#1e293b;line-height:1.6}}
a{{color:inherit;text-decoration:none}}
header{{background:#fff;border-bottom:1px solid #e2e8f0;padding:1rem 2rem;display:flex;align-items:center;justify-content:space-between}}
.logo{{font-weight:800;font-size:1.25rem;color:#1e293b}}.logo span{{color:#6366f1}}
nav a{{margin-left:1.5rem;color:#64748b;font-size:.9rem}}
nav a:hover{{color:#6366f1}}
.hero{{background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 100%);color:#fff;text-align:center;padding:3rem 2rem}}
.hero h1{{font-size:2.2rem;font-weight:800;margin-bottom:.75rem}}
.hero p{{font-size:1.1rem;opacity:.9;max-width:600px;margin:0 auto 1.5rem}}
.stats{{display:flex;gap:2rem;justify-content:center;flex-wrap:wrap}}
.stat{{background:rgba(255,255,255,.15);border-radius:8px;padding:.5rem 1.25rem;font-weight:700}}
.cat-nav{{background:#fff;border-bottom:1px solid #e2e8f0;padding:1rem 2rem;display:flex;gap:1rem;flex-wrap:wrap;position:sticky;top:0;z-index:100}}
.cat-nav a{{background:#f1f5f9;border-radius:20px;padding:.35rem .85rem;font-size:.85rem;color:#475569;transition:all .2s}}
.cat-nav a:hover{{background:#6366f1;color:#fff}}
main{{max-width:1400px;margin:0 auto;padding:2rem}}
.category-section{{margin-bottom:3rem}}
.category-heading{{font-size:1.5rem;font-weight:700;margin-bottom:1.25rem;display:flex;align-items:center;gap:.5rem}}
.tool-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem}}
.tool-card{{background:#fff;border-radius:10px;padding:1rem;box-shadow:0 1px 3px rgba(0,0,0,.08);transition:transform .2s,box-shadow .2s}}
.tool-card:hover{{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.12)}}
.tool-name{{font-weight:700;font-size:.95rem;margin-bottom:.6rem;color:#1e293b}}
.tags{{display:flex;flex-wrap:wrap;gap:.35rem}}
.tag{{display:inline-block;background:#f1f5f9;border-radius:12px;padding:.2rem .6rem;font-size:.75rem;color:#475569;transition:background .15s}}
.tag:hover{{background:#6366f1;color:#fff}}
.tag-placeholder{{display:inline-block;background:#f1f5f9;border-radius:12px;padding:.2rem .6rem;font-size:.75rem;color:#94a3b8}}
.az-section{{background:#fff;border-radius:12px;padding:2rem;margin-top:2rem;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
.az-section h2{{font-size:1.25rem;font-weight:700;margin-bottom:1rem;color:#1e293b}}
.az-links{{display:flex;flex-wrap:wrap;gap:.5rem}}
.az-link{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:.35rem .75rem;font-size:.85rem;color:#475569;transition:all .15s}}
.az-link:hover{{background:#6366f1;color:#fff;border-color:#6366f1}}
footer{{background:#1e293b;color:#94a3b8;text-align:center;padding:2rem;margin-top:2rem;font-size:.875rem}}
footer a{{color:#cbd5e1}}
@media(max-width:640px){{.hero h1{{font-size:1.5rem}}.tool-grid{{grid-template-columns:1fr 1fr}}}}
</style>
</head>
<body>
<header>
  <a href="/" class="logo">SaaS<span>pare</span></a>
  <nav>
    <a href="/pages">Library</a>
    <a href="/categories">Categories</a>
    <a href="/deal-radar.html">Deal Radar</a>
    <a href="/shortlist.html">Shortlist</a>
  </nav>
</header>
<div class="hero">
  <h1>Browse SaaS Tools by Category</h1>
  <p>Compare pricing, reviews, free trials, coupons, and alternatives for {total}+ B2B tools in 2026.</p>
  <div class="stats">
    <div class="stat">{total}+ Pages</div>
    <div class="stat">12 Categories</div>
    <div class="stat">160+ Tools</div>
    <div class="stat">Free to use</div>
  </div>
</div>
<nav class="cat-nav" aria-label="Jump to category">
{"".join(f'<a href="#{n.lower().replace(" & ", "-").replace(" ", "-")}">{d["emoji"]} {n}</a>' for n, d in CATEGORIES.items())}
</nav>
<main>
{category_sections}
<div class="az-section">
  <h2>🔤 Browse All Tools A–Z</h2>
  <div class="az-links">{az_links}</div>
</div>
</main>
<footer>
  <p>
    <a href="/">SaaSpare</a> &middot;
    <a href="/pages">Library</a> &middot;
    <a href="/methodology.html">Methodology</a> &middot;
    <a href="/affiliate-disclosure.html">Affiliate Disclosure</a> &middot;
    <a href="/privacy.html">Privacy</a>
  </p>
  <p style="margin-top:.5rem">&copy; 2026 SaaSpare. All affiliate links disclosed.</p>
</footer>
</body>
</html>"""
    return html


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(ROOT))
    html = build_categories_html()
    OUT.write_text(html, encoding="utf-8")
    print(f"Written: {OUT} ({len(html):,} chars)")
