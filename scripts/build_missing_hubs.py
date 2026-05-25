"""
Build 3 missing category hub pages:
  - best-finance-software-2026.html
  - best-ecommerce-platform-2026.html
  - best-cloud-hosting-2026.html

Each hub:
  - ItemList schema (rich result eligible)
  - Internal links to all cluster pages
  - Speakable + FAQPage schema
  - AEO-optimised featured answer

Run: uv run python scripts/build_missing_hubs.py
"""
import json
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).resolve().parents[1]
SITE  = ROOT / "site"
TODAY = date.today().isoformat()
YEAR  = "2026"

GA_TAG = """<script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-RLYVYV8WQJ');</script>"""

HUBS = [
    {
        "slug": "best-finance-software-2026",
        "title": f"Best Finance & Spend Management Software {YEAR}: Ranked & Compared",
        "meta": f"The best finance software for {YEAR}: corporate cards, expense management, accounting, and payment processing — ranked by real pricing and features.",
        "h1": f"Best Finance & Spend Management Software {YEAR}",
        "intro": f"From corporate cards to accounting tools, the right finance software stack can save a 50-person company $50,000+ per year in time and fees. Here are the top tools in {YEAR}, ranked by value.",
        "featured_answer": f"The best finance software in {YEAR} is Ramp for corporate cards and spend management (free for core features), Stripe for payment processing (2.9%+30c per transaction), and Xero or FreshBooks for accounting ($13-$42/month). For expense management, Expensify and Ramp are both strong. The right stack depends on whether you need US-only payroll (Gusto) or global payments (Stripe).",
        "tools": [
            {"rank": 1, "name": "Ramp", "slug": "ramp", "tag": "Corporate Cards", "score": "9.4/10", "blurb": "Free corporate cards + spend management with automatic receipt matching. Best for US businesses wanting zero-fee corporate cards."},
            {"rank": 2, "name": "Stripe", "slug": "stripe", "tag": "Payment Processing", "score": "9.3/10", "blurb": "The developer's payment stack. 2.9%+30c per transaction, 180+ currencies, excellent fraud tooling. Default for SaaS."},
            {"rank": 3, "name": "Xero", "slug": "xero", "tag": "Accounting", "score": "9.0/10", "blurb": "Cloud accounting with bank reconciliation, invoicing, and strong integration ecosystem. Best for SMBs outside the US."},
            {"rank": 4, "name": "FreshBooks", "slug": "freshbooks", "tag": "Invoicing & Accounting", "score": "8.7/10", "blurb": "Built for service businesses and freelancers. Best invoicing UI in the market, starting at $19/mo."},
            {"rank": 5, "name": "Gusto", "slug": "gusto", "tag": "Payroll & HR", "score": "8.9/10", "blurb": "Best US payroll + benefits platform. Automatic tax filings, integrated benefits, starting at $46/mo base + $6/person."},
            {"rank": 6, "name": "Brex", "slug": "brex", "tag": "Corporate Cards", "score": "8.5/10", "blurb": "Corporate cards + spend management for startups and scale-ups. Strong reward programme, free for basic use."},
        ],
        "faq": [
            (f"What is the best finance software for small business in {YEAR}?", f"FreshBooks ($19/mo) for service businesses, Xero ($13/mo) for product businesses, and Ramp (free) for corporate cards. For US payroll, Gusto ($46/mo base) is the most complete small-business solution."),
            ("What is the best free finance software?", "Ramp offers genuinely free corporate cards and spend management with no monthly fee. Wave is free for invoicing and basic accounting (revenue comes from payment processing). Both are suitable for small teams."),
            (f"How much does business finance software cost in {YEAR}?", f"Accounting tools: $13-$150/month depending on features. Corporate cards: free (Ramp, Brex) to $15/user/month for premium. Payment processing: 2.9%+30c per transaction (Stripe) or negotiable at high volume."),
        ],
        "og_image": "/og/finance.svg",
        "vertical": "finance",
        "cluster_links": [
            ("/pages/ramp-pricing-2026-plans-costs-what-you-actually-pay", "Ramp Pricing"),
            ("/pages/ramp-review-2026-is-it-worth-it-honest-verdict", "Ramp Review"),
            ("/pages/stripe-review-2026-is-it-worth-it-honest-verdict", "Stripe Review"),
            ("/pages/stripe-coupon-2026-discount-codes-promo", "Stripe Discounts"),
            ("/pages/xero-pricing-2026-plans-costs-what-you-actually-pay", "Xero Pricing"),
            ("/pages/freshbooks-pricing-2026-plans-costs-what-you-actually-pay", "FreshBooks Pricing"),
            ("/pages/freshbooks-coupon-2026-discount-codes-promo", "FreshBooks Coupons"),
            ("/pages/gusto-pricing-2026-plans-costs-what-you-actually-pay", "Gusto Pricing"),
            ("/pages/gusto-review-2026-is-it-worth-it-honest-verdict", "Gusto Review"),
            ("/pages/ramp-vs-brex-which-is-better-in-2026", "Ramp vs Brex"),
            ("/pages/ramp-vs-mercury-which-is-better-in-2026", "Ramp vs Mercury"),
        ],
    },
    {
        "slug": "best-ecommerce-platform-2026",
        "title": f"Best Ecommerce Platform {YEAR}: Shopify vs BigCommerce vs WooCommerce Compared",
        "meta": f"The best ecommerce platforms in {YEAR}: Shopify, BigCommerce, WooCommerce, Wix, and Squarespace — ranked by real pricing, transaction fees, and scalability.",
        "h1": f"Best Ecommerce Platform {YEAR}: Ranked & Compared",
        "intro": f"Choosing the wrong ecommerce platform in {YEAR} can cost you thousands in transaction fees and months of migration pain later. Here's a clear-eyed comparison of every major option — with real pricing, not marketing claims.",
        "featured_answer": f"The best ecommerce platform in {YEAR} is Shopify for most businesses ($29-$299/month, 0% transaction fees with Shopify Payments). BigCommerce is better for high-volume B2B ($39-$399/month, no GMV transaction fees). WooCommerce is best for WordPress users who want full control (free plugin, hosting from $10/month). For simple stores and creators, Squarespace ($23-$65/month) and Wix ($17-$35/month) are easier to set up.",
        "tools": [
            {"rank": 1, "name": "Shopify", "slug": "shopify", "tag": "Best Overall", "score": "9.5/10", "blurb": "The market leader. Best app ecosystem (8,000+ apps), 0% transaction fees with Shopify Payments, and the most powerful theme system. Scales from side-hustle to $1B GMV."},
            {"rank": 2, "name": "BigCommerce", "slug": "bigcommerce", "tag": "Best for B2B", "score": "9.0/10", "blurb": "Strongest B2B features (customer-specific pricing, bulk ordering, multi-storefront). No transaction fees on any plan. Better for high-volume wholesale."},
            {"rank": 3, "name": "WooCommerce", "slug": "woocommerce", "tag": "Best Open-Source", "score": "8.7/10", "blurb": "Free plugin for WordPress. Maximum flexibility and ownership — but you manage hosting, security, and plugins yourself. Best if you already run WordPress."},
            {"rank": 4, "name": "Squarespace", "slug": "squarespace", "tag": "Best for Creators", "score": "8.3/10", "blurb": "Most beautiful templates. Best for creators, artists, and small-catalogue stores. Commerce plans from $23/mo with 0% transaction fees."},
            {"rank": 5, "name": "Wix", "slug": "wix", "tag": "Easiest Setup", "score": "8.1/10", "blurb": "Fastest to launch. Drag-and-drop builder with no coding. Best for small product catalogues (under 100 SKUs) where speed of setup matters most."},
        ],
        "faq": [
            (f"What is the best ecommerce platform for small businesses in {YEAR}?", "Shopify is the best overall ($29/month). If you're starting very small, Wix eCommerce ($17/month) or Squarespace Commerce ($23/month) are easier to set up. WooCommerce is best if you already have a WordPress site."),
            ("Which ecommerce platform has no transaction fees?", "Shopify charges 0% transaction fees when using Shopify Payments. BigCommerce charges 0% on all plans regardless of payment processor. WooCommerce charges 0% but you pay payment gateway fees (typically 2.9%+30c via Stripe)."),
            (f"Shopify vs BigCommerce in {YEAR} — which is better?", f"Shopify is better for B2C, DTC, and most retail businesses. BigCommerce is better for B2B, wholesale, and businesses with complex pricing rules. See our full Shopify vs BigCommerce comparison for a detailed breakdown."),
        ],
        "og_image": "/og/ecommerce.svg",
        "vertical": "ecommerce",
        "cluster_links": [
            ("/pages/shopify-pricing-2026-plans-costs-what-you-actually-pay", "Shopify Pricing"),
            ("/pages/shopify-review-2026-is-it-worth-it-honest-verdict", "Shopify Review"),
            ("/pages/bigcommerce-review-2026-is-it-worth-it-honest-verdict", "BigCommerce Review"),
            ("/pages/bigcommerce-pricing-2026-plans-costs-what-you-actually-pay", "BigCommerce Pricing"),
            ("/pages/shopify-vs-bigcommerce-which-is-better-in-2026", "Shopify vs BigCommerce"),
            ("/pages/shopify-vs-wix-which-is-better-in-2026", "Shopify vs Wix"),
            ("/pages/shopify-vs-squarespace-which-is-better-in-2026", "Shopify vs Squarespace"),
            ("/pages/bigcommerce-free-trial-2026-how-to-start-what-you-get", "BigCommerce Free Trial"),
        ],
    },
    {
        "slug": "best-cloud-hosting-2026",
        "title": f"Best Cloud Hosting {YEAR}: AWS vs Hetzner vs DigitalOcean vs Vultr Compared",
        "meta": f"The best cloud hosting providers in {YEAR}: AWS, Hetzner, DigitalOcean, Vultr, and Contabo — ranked by price-performance ratio and developer experience.",
        "h1": f"Best Cloud Hosting {YEAR}: Ranked by Price-Performance",
        "intro": f"Cloud hosting pricing varies by 10-20x between providers for identical specs. The right choice in {YEAR} depends on your workload, region requirements, and tolerance for self-management. Here's who wins where.",
        "featured_answer": f"The best cloud hosting in {YEAR} by use case: Hetzner (best price-performance, EU workloads, from $4.15/mo), DigitalOcean (best developer experience, from $4/mo with $200 free credit), Vultr (best global coverage, 32 locations, from $2.50/mo), Contabo (absolute cheapest, from $5.50/mo for 4GB RAM), AWS (best for enterprise and complex managed services, pay-as-you-go). For most indie developers and startups, Hetzner or DigitalOcean deliver the best value.",
        "tools": [
            {"rank": 1, "name": "Hetzner", "slug": "hetzner", "tag": "Best Value (EU)", "score": "9.4/10", "blurb": "Best price-performance ratio in the market. EU and US locations, green energy, from €3.79/month for a 2vCPU/4GB server. Unbeatable for GDPR-compliant workloads."},
            {"rank": 2, "name": "DigitalOcean", "slug": "digitalocean", "tag": "Best Developer Experience", "score": "9.2/10", "blurb": "$200 free credit for 60 days. Simplest control panel, excellent documentation, App Platform PaaS option. Best starting point for developers new to cloud."},
            {"rank": 3, "name": "Vultr", "slug": "vultr", "tag": "Best Global Coverage", "score": "8.8/10", "blurb": "32 data centre locations including Asia-Pacific markets where Hetzner and DO lack coverage. $100 free credit for new accounts. From $2.50/mo."},
            {"rank": 4, "name": "Contabo", "slug": "contabo", "tag": "Absolute Cheapest", "score": "8.2/10", "blurb": "Best raw specs per dollar. 4GB RAM server from $5.50/mo. No frills, basic support, but genuinely reliable for dev/staging environments."},
            {"rank": 5, "name": "Supabase", "slug": "supabase", "tag": "Best Managed Backend", "score": "9.1/10", "blurb": "Not just hosting — full Postgres + auth + storage + edge functions. Free for 2 projects, $25/mo Pro. Best for developers who don't want to manage infrastructure."},
        ],
        "faq": [
            (f"What is the cheapest cloud hosting in {YEAR}?", f"Contabo offers the cheapest raw compute: 4GB RAM VPS from $5.50/month. Hetzner offers the best price-to-performance: 4GB RAM from $4.15/month with better network and support. Both are significantly cheaper than AWS, GCP, or Azure."),
            ("Is Hetzner better than DigitalOcean?", "Hetzner is cheaper (40-60% less for equivalent specs) and better for EU-regulated workloads. DigitalOcean has a better developer experience, more managed services (Kubernetes, databases), and $200 free credit for new users. Most teams choose DigitalOcean to start and Hetzner to scale."),
            (f"What cloud hosting does Supabase use?", f"Supabase runs on AWS infrastructure but abstracts it away with a managed Postgres + auth + storage layer. For most developers, Supabase ($25/mo Pro) replaces the need for a separate cloud hosting provider for backend needs."),
        ],
        "og_image": "/og/infra.svg",
        "vertical": "infra",
        "cluster_links": [
            ("/pages/hetzner-pricing-2026-plans-costs-what-you-actually-pay", "Hetzner Pricing"),
            ("/pages/hetzner-review-2026-is-it-worth-it-honest-verdict", "Hetzner Review"),
            ("/pages/digitalocean-review-2026-is-it-worth-it-honest-verdict", "DigitalOcean Review"),
            ("/pages/digitalocean-free-trial-2026-how-to-start-what-you-get", "DigitalOcean Free Trial"),
            ("/pages/vultr-review-2026-is-it-worth-it-honest-verdict", "Vultr Review"),
            ("/pages/vultr-free-trial-2026-how-to-start-what-you-get", "Vultr Free Trial"),
            ("/pages/contabo-review-2026-is-it-worth-it-honest-verdict", "Contabo Review"),
            ("/pages/supabase-review-2026-is-it-worth-it-honest-verdict", "Supabase Review"),
            ("/pages/supabase-pricing-2026-plans-costs-what-you-actually-pay", "Supabase Pricing"),
        ],
    },
]


def render_hub(hub: dict) -> str:
    # ItemList schema
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": hub["title"],
        "description": hub["meta"],
        "numberOfItems": len(hub["tools"]),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": t["rank"],
                "name": t["name"],
                "url": f"https://saaspare.org/pages/{t['slug']}-review-2026-is-it-worth-it-honest-verdict",
            }
            for t in hub["tools"]
        ],
    }
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in hub["faq"]
        ],
    }
    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": hub["title"],
        "datePublished": TODAY,
        "dateModified": TODAY,
        "author": {"@type": "Person", "name": "Smith Elly", "url": "https://saaspare.org/about"},
        "publisher": {"@type": "Organization", "name": "SaaSpare", "url": "https://saaspare.org"},
        "description": hub["meta"],
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://saaspare.org/"},
            {"@type": "ListItem", "position": 2, "name": hub["title"], "item": f"https://saaspare.org/{hub['slug']}"},
        ],
    }

    schemas = [item_list, faq_schema, article_schema, breadcrumb]
    schema_html = "\n".join(
        f'  <script type="application/ld+json">\n  {json.dumps(s, separators=(",",":"))}\n  </script>'
        for s in schemas
    )

    tools_html = ""
    for t in hub["tools"]:
        tools_html += f"""
    <div class="tool-card" style="border:1px solid #e2e8f0;border-radius:12px;padding:1.25rem;margin-bottom:1rem;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
          <span style="background:#0ea5e9;color:#fff;font-size:.7rem;font-weight:700;padding:.2rem .6rem;border-radius:100px;margin-bottom:.5rem;display:inline-block;">#{t['rank']} {t['tag']}</span>
          <h3 style="margin:.25rem 0;">{t['name']}</h3>
          <p style="color:#475569;margin:.5rem 0;">{t['blurb']}</p>
        </div>
        <div style="font-weight:700;color:#16a34a;font-size:1.1rem;white-space:nowrap;margin-left:1rem;">{t['score']}</div>
      </div>
      <div style="margin-top:.75rem;">
        <a href="/pages/{t['slug']}-review-2026-is-it-worth-it-honest-verdict" style="color:#0ea5e9;font-weight:600;font-size:.9rem;">Read full review &rarr;</a>
        &nbsp;&middot;&nbsp;
        <a href="/pages/{t['slug']}-pricing-2026-plans-costs-what-you-actually-pay" style="color:#64748b;font-size:.9rem;">See pricing</a>
      </div>
    </div>"""

    faq_html = ""
    for q, a in hub["faq"]:
        faq_html += f'    <div class="faq-item"><h3 class="faq-q">{q}</h3><p class="faq-a">{a}</p></div>\n'

    cluster_links_html = " &middot;\n        ".join(
        f'<a href="{url}">{label}</a>' for url, label in hub.get("cluster_links", [])
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{hub['title']} | SaaSpare</title>
  <meta name="description" content="{hub['meta']}">
  <link rel="canonical" href="https://saaspare.org/{hub['slug']}">
  <meta property="og:title" content="{hub['title']}">
  <meta property="og:description" content="{hub['meta']}">
  <meta property="og:image" content="https://saaspare.org{hub['og_image']}">
  <meta property="og:url" content="https://saaspare.org/{hub['slug']}">
  <link rel="stylesheet" href="/assets/style.css">
{schema_html}
  {GA_TAG}
</head>
<body>
  <header>
    <nav><a href="/">SaaSpare</a> &rsaquo; Best Software {YEAR}</nav>
  </header>
  <main>
    <article>
      <h1>{hub['h1']}</h1>
      <p class="byline">By Smith Elly &middot; Updated {TODAY} &middot; <a href="/about#methodology">Methodology</a></p>

      <div class="quick-answer" style="background:#eff6ff;border-left:4px solid #3b82f6;padding:1rem 1.25rem;margin:1.5rem 0;border-radius:4px;">
        <strong>Quick answer:</strong> {hub['featured_answer']}
      </div>

      <p>{hub['intro']}</p>

      <h2>Top {len(hub['tools'])} Tools — Ranked</h2>
      {tools_html}

      <h2>Frequently Asked Questions</h2>
      <div class="faq-block">
{faq_html}      </div>

      <aside style="background:#f8fafc;border:1px solid #e2e8f0;padding:1rem 1.25rem;border-radius:8px;margin-top:2rem;">
        <strong>All {hub['h1'].split(':')[0].replace('Best ','').replace(' '+YEAR,'')} pages:</strong><br>
        <div style="margin-top:.5rem;line-height:2;">
        {cluster_links_html}
        </div>
      </aside>
    </article>
  </main>
  <footer><p>&copy; {YEAR} SaaSpare &middot; <a href="/">Home</a> &middot; <a href="/blog/">Blog</a> &middot; <a href="/sitemap.xml">Sitemap</a></p></footer>
</body>
</html>"""


if __name__ == "__main__":
    built = 0
    for hub in HUBS:
        out = SITE / f"{hub['slug']}.html"
        if out.exists():
            print(f"  [skip] {hub['slug']}.html")
            continue
        out.write_text(render_hub(hub), encoding="utf-8")
        built += 1
        print(f"  + {hub['slug']}.html")
    print(f"\nBuilt {built}/{len(HUBS)} category hubs")
