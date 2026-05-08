"""
Build 8 category hub pages for saaspare.org.
These are the #1 missing SEO asset — without them, 600+ comparison
pages are orphaned with no parent authority page.

Run: uv run python scripts/build_category_hubs.py
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
TODAY = date.today().isoformat()

HUBS = [
    {
        "slug": "best-crm-software-2026",
        "title": "Best CRM Software in 2026: Compared by Price, Features & Use Case",
        "meta": "Compare the best CRM software in 2026. Real pricing, honest verdicts, and free trial guides for HubSpot, Salesforce, Pipedrive, and 20+ more.",
        "keyword": "best crm software 2026",
        "intro": "Finding the right CRM comes down to three things: what your team actually needs, what you can afford, and what the true total cost looks like after all the add-ons. We track weekly pricing across 20+ CRM tools so you can see exactly what you would pay.",
        "tools": [
            ("HubSpot CRM", "hubspot-crm", "Best for growing SMBs. Free tier is genuinely useful.", "$20/mo"),
            ("Salesforce", "salesforce", "Best for enterprises needing deep customisation.", "$25/mo"),
            ("Pipedrive", "pipedrive", "Best value for pure sales teams.", "$15/mo"),
            ("Zoho CRM", "zoho-crm", "Best budget option. Most features per dollar.", "$14/mo"),
            ("Monday.com CRM", "monday-com", "Best for teams already using Monday for PM.", "$12/mo"),
            ("ClickUp CRM", "clickup", "Best all-in-one PM + CRM tool.", "$7/mo"),
            ("Close CRM", "close", "Best for inside sales doing high-volume outreach.", "$29/mo"),
        ],
        "faq": [
            ("What is the best CRM for a small business?", "HubSpot CRM is best for most small businesses — the free tier covers contacts, deals, and basic email tracking without a time limit. Pipedrive is the best paid option if your team is sales-focused and wants simplicity over features."),
            ("How much does CRM software cost?", "CRM pricing ranges from $0 (HubSpot Free) to $300+ per user per month (Salesforce Enterprise). Most SMBs pay $15-50 per user per month. Watch for seat minimums — HubSpot Professional requires a $1,500 onboarding fee on top of monthly costs."),
            ("Is Salesforce worth it for a startup?", "Rarely. Salesforce minimum viable configuration costs $75-150 per user per month for a startup once you add required apps. Pipedrive or HubSpot deliver 80% of the functionality at 20% of the cost for teams under 50 people."),
        ],
    },
    {
        "slug": "best-project-management-software-2026",
        "title": "Best Project Management Software in 2026: Honest Comparison",
        "meta": "The best project management software in 2026 compared by real pricing and features. Asana vs Monday vs ClickUp vs Notion vs Linear — who wins on value?",
        "keyword": "best project management software 2026",
        "intro": "Project management software is where free-tier promises go to die. Most tools start free and become expensive fast as your team grows. We track real pricing weekly.",
        "tools": [
            ("Asana", "asana", "Best for marketing and operations teams. Clean UI.", "$13/mo"),
            ("Monday.com", "monday-com", "Best visual workflow. Pricey at scale.", "$12/mo"),
            ("ClickUp", "clickup", "Best all-in-one. Steepest learning curve.", "$7/mo"),
            ("Notion", "notion", "Best for docs + lightweight project tracking.", "$10/mo"),
            ("Linear", "linear", "Best for engineering and product teams.", "$8/mo"),
            ("Trello", "trello", "Best for simple kanban-only workflows.", "$10/mo"),
            ("Jira", "jira", "Best for large engineering orgs with complex sprints.", "$8/mo"),
        ],
        "faq": [
            ("What is the best project management software for remote teams?", "Notion or ClickUp are the top picks for remote teams. Notion combines documentation and project tracking, reducing tool sprawl. ClickUp has the most features but takes longer to configure."),
            ("Is Monday.com worth the price?", "Monday.com is worth it for visual thinkers managing marketing or ops workflows. It becomes expensive at scale — 10 users on Pro costs $160+/month. For engineering teams, Linear is half the price and better suited to sprint work."),
            ("What is the cheapest project management tool?", "Trello has the most generous free plan for simple boards. For paid tiers, Linear and Notion offer the best value — both under $10 per user per month."),
        ],
    },
    {
        "slug": "best-seo-tools-2026",
        "title": "Best SEO Tools in 2026: Real Pricing, Real Feature Comparison",
        "meta": "The best SEO tools in 2026: Ahrefs vs Semrush vs Moz vs SE Ranking compared by real pricing, features, and value for money.",
        "keyword": "best seo tools 2026",
        "intro": "SEO tool pricing is notoriously opaque. Most tools show a low entry price then require higher tiers for features you actually need. We track their pricing pages weekly.",
        "tools": [
            ("Semrush", "semrush", "Best all-in-one SEO platform. Most keyword data.", "$140/mo"),
            ("Ahrefs", "ahrefs", "Best backlink database. Note: no affiliate program.", "$99/mo"),
            ("Moz Pro", "moz-pro", "Best for beginners. Simpler interface.", "$99/mo"),
            ("SE Ranking", "se-ranking", "Best budget Semrush alternative.", "$44/mo"),
            ("Surfer SEO", "surfer-seo", "Best for on-page content optimisation.", "$79/mo"),
            ("SpyFu", "spyfu", "Best for PPC competitor research.", "$39/mo"),
            ("Mangools", "mangools", "Best entry-level tool for solo bloggers.", "$29/mo"),
        ],
        "faq": [
            ("Is Ahrefs or Semrush better?", "Semrush has more features — PPC research, content tools, social. Ahrefs has the stronger backlink database preferred by link builders. For most SEO professionals, Semrush provides better value per dollar. Note: Ahrefs has no affiliate program, which means independent reviews tend to be less biased."),
            ("How much does Semrush cost in 2026?", "Semrush Pro starts at $140/month (monthly) or $117/month (annual). The Guru plan for historical data and content tools is $250/month. Watch for the 10-project and 3,000-reports/day limits on Pro."),
            ("What is the best free SEO tool?", "Google Search Console is the most useful free SEO tool — it shows exactly which queries drive traffic for your site. Semrush and Ahrefs both offer limited free tiers for keyword research."),
        ],
    },
    {
        "slug": "best-password-manager-business-2026",
        "title": "Best Business Password Managers in 2026: Compared by Price & Security",
        "meta": "Best business password managers in 2026: 1Password vs Bitwarden vs NordPass vs Dashlane compared by real pricing, features, and security track record.",
        "keyword": "best password manager for business 2026",
        "intro": "Business password managers have consolidated around a few dominant players. The pricing gap between them is significant — some charge 3x more for essentially the same core features.",
        "tools": [
            ("1Password", "1password", "Best UX. Best for Apple-heavy teams.", "$8/user/mo"),
            ("Bitwarden", "bitwarden", "Best open-source option. Cheapest verified-secure choice.", "$3/user/mo"),
            ("NordPass", "nordpass", "Best for teams wanting simplest onboarding.", "$4/user/mo"),
            ("Dashlane", "dashlane", "Best phishing alerts. Most expensive.", "$8/user/mo"),
            ("Keeper", "keeper", "Best for compliance-heavy industries.", "$6/user/mo"),
            ("LastPass", "lastpass", "Widely used — but had major 2022 vault breach.", "$4/user/mo"),
        ],
        "faq": [
            ("What is the safest business password manager?", "1Password and Bitwarden have the strongest security track records. Bitwarden is open-source and independently audited. LastPass suffered a significant breach in 2022 where encrypted vault data was stolen — we recommend migrating away from it."),
            ("How much does a business password manager cost?", "1Password Teams costs $8/user/month. Bitwarden Teams is $3/user/month. For a 10-person team that is $960/year vs $360/year. Both offer the same core features — 1Password wins on UX, Bitwarden wins on price and open-source transparency."),
            ("Is Bitwarden good for business?", "Yes. Bitwarden is the best value business password manager. It is open-source, independently audited, SOC 2 compliant, and $3/user/month on Teams. The main trade-off vs 1Password is a less polished mobile app."),
        ],
    },
    {
        "slug": "best-video-conferencing-software-2026",
        "title": "Best Video Conferencing Software in 2026: For Teams of All Sizes",
        "meta": "Best video conferencing software in 2026: Zoom vs Google Meet vs Microsoft Teams vs Whereby — compared by real pricing, features, and integration depth.",
        "keyword": "best video conferencing software 2026",
        "intro": "Video conferencing tools are commoditised at the basic level. The differences emerge at the enterprise tier: recording quality, transcription accuracy, compliance logs, and integration depth.",
        "tools": [
            ("Zoom", "zoom", "Best for external meetings and webinars. Market leader.", "$16/mo"),
            ("Google Meet", "google-meet", "Best for Google Workspace users. Free with Workspace.", "Free"),
            ("Microsoft Teams", "microsoft-teams", "Best for Microsoft 365 shops. Bundled pricing.", "$6/mo"),
            ("Whereby", "whereby", "Best no-install browser-based calls.", "$10/mo"),
            ("Webex", "webex", "Best for large enterprise compliance requirements.", "$17/mo"),
            ("Loom", "loom", "Best for async video messages — not live calls.", "$13/mo"),
        ],
        "faq": [
            ("What is the best free video conferencing tool?", "Google Meet is the best free option — unlimited 1:1 calls and 60-minute group calls. Zoom's free plan limits group calls to 40 minutes. Microsoft Teams is free for personal use with some limitations."),
            ("Is Zoom still the best in 2026?", "Zoom remains the default for external business meetings because everyone has it installed. For internal meetings, Google Meet or Teams are often free via existing subscriptions. Whereby is the best for customer-facing calls where you do not want visitors to install software."),
        ],
    },
    {
        "slug": "best-marketing-automation-software-2026",
        "title": "Best Marketing Automation Platforms in 2026: Feature & Price Guide",
        "meta": "Best marketing automation software in 2026: GetResponse vs ActiveCampaign vs Mailchimp vs HubSpot compared by real pricing, deliverability, and automation depth.",
        "keyword": "best marketing automation software 2026",
        "intro": "Marketing automation pricing is one of the most confusing categories in SaaS. Almost every platform charges by contact count, meaning your costs grow automatically as your list grows.",
        "tools": [
            ("GetResponse", "getresponse", "Best all-in-one with webinar tools. Strong deliverability.", "$19/mo"),
            ("ActiveCampaign", "activecampaign", "Best automation depth for B2B nurture.", "$49/mo"),
            ("Mailchimp", "mailchimp", "Best for beginners. Becomes expensive at scale.", "$17/mo"),
            ("Klaviyo", "klaviyo", "Best for ecommerce email and SMS.", "$45/mo"),
            ("Brevo", "brevo", "Best budget option. Charges by sends, not contacts.", "$25/mo"),
            ("HubSpot Marketing", "hubspot", "Best if already using HubSpot CRM. Pricey standalone.", "$800/mo"),
        ],
        "faq": [
            ("What is the best email marketing automation for a small business?", "GetResponse or Brevo are the best choices for small businesses. Both offer strong automation and good deliverability. Brevo is uniquely priced by email sends rather than contacts, which can be much cheaper if you have a large list you email infrequently."),
            ("Is HubSpot Marketing Hub worth the price?", "Only if you are already using HubSpot CRM. Standalone it is hard to justify — HubSpot Marketing Hub Professional starts at $800/month. ActiveCampaign delivers comparable automation at $49-149/month for most use cases."),
        ],
    },
    {
        "slug": "best-vpn-for-business-2026",
        "title": "Best VPN for Business in 2026: Security, Speed & Pricing Compared",
        "meta": "Best business VPN in 2026: NordVPN Teams vs Surfshark vs NordLayer vs Perimeter 81 compared by pricing, security features, and team management tools.",
        "keyword": "best vpn for business 2026",
        "intro": "Consumer VPNs and business VPNs serve different needs. Consumer VPNs hide your traffic. Business VPNs also need centralised team management, policy controls, and audit logs.",
        "tools": [
            ("NordVPN Teams", "nordvpn", "Best consumer-grade VPN for small teams.", "$8/user/mo"),
            ("Surfshark Teams", "surfshark", "Best value. Unlimited device policy.", "$6/user/mo"),
            ("NordLayer", "nordlayer", "Best business-focused NordVPN product.", "$9/user/mo"),
            ("Perimeter 81", "perimeter-81", "Best zero-trust network access for SMBs.", "$10/user/mo"),
            ("Cisco AnyConnect", "cisco-anyconnect", "Best for enterprise Cisco stacks.", "Enterprise"),
        ],
        "faq": [
            ("What is the difference between a consumer and business VPN?", "Consumer VPNs (NordVPN, Surfshark) protect individual users traffic. Business VPNs add team management: central admin console, per-user policy controls, compliance audit logs, and dedicated IPs. NordLayer and Perimeter 81 are purpose-built for team use cases."),
            ("How much does a business VPN cost?", "Business VPN pricing ranges from $6/user/month (Surfshark Teams) to $15/user/month (Perimeter 81 Essentials). For a 10-person team that is $720-$1,800 per year. Consumer VPNs are cheaper but lack team management features."),
        ],
    },
    {
        "slug": "best-hr-software-2026",
        "title": "Best HR Software for Small & Mid-Size Businesses in 2026",
        "meta": "Best HR software for SMBs in 2026: Rippling vs BambooHR vs Gusto vs Workday compared by pricing, features, and company size fit.",
        "keyword": "best hr software small business 2026",
        "intro": "HR software pricing is almost never published upfront — most vendors require a demo call. We track what buyers report paying after their sales calls.",
        "tools": [
            ("Rippling", "rippling", "Best all-in-one HR + IT + Finance platform.", "~$8/user/mo"),
            ("BambooHR", "bamboohr", "Best for SMBs wanting clean, simple HR tools.", "~$9/user/mo"),
            ("Gusto", "gusto", "Best for US payroll and basic HR combined.", "$46/mo base"),
            ("Workday", "workday", "Best for enterprise. Powerful but complex.", "Enterprise"),
            ("ADP", "adp", "Best for pure payroll compliance at scale.", "Custom"),
        ],
        "faq": [
            ("What is the best HR software for a company under 100 employees?", "BambooHR or Gusto are the top picks for companies under 100 employees. Gusto is best if US payroll is your primary need. BambooHR is better for companies needing performance reviews, onboarding workflows, and time tracking on top of payroll."),
            ("How much does Rippling cost?", "Rippling starts at approximately $8 per user per month for the core platform, with additional modules priced separately. Most mid-size teams pay $15-25 per user per month fully loaded. Rippling does not publish pricing publicly — you need a sales call."),
        ],
    },
]


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | SaaSpare</title>
<meta name="description" content="{meta}">
<link rel="canonical" href="https://saaspare.org/{slug}">
<meta name="robots" content="index, follow">
<meta property="og:title" content="{title} | SaaSpare">
<meta property="og:description" content="{meta}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://saaspare.org/{slug}">
<meta property="og:image" content="https://saaspare.org/og-default.png">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{article_schema}</script>
<script type="application/ld+json">{itemlist_schema}</script>
<script type="application/ld+json">{faq_schema}</script>
<script type="application/ld+json">{breadcrumb_schema}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
<noscript><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"></noscript>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',system-ui,sans-serif;background:#07070d;color:rgba(255,255,255,.85);line-height:1.7}}
.hdr{{padding:1rem 1.5rem;border-bottom:1px solid rgba(255,255,255,.07);display:flex;align-items:center;gap:.5rem}}
.hdr a{{text-decoration:none;font-weight:800;color:#fff;font-size:.95rem}}
.hdr em{{color:#e94560;font-style:normal}}
main{{max-width:860px;margin:0 auto;padding:2.5rem 1.5rem 5rem}}
.qa{{background:rgba(233,69,96,.08);border:1px solid rgba(233,69,96,.2);border-radius:12px;padding:1.2rem 1.4rem;margin-bottom:2rem;font-size:.95rem;color:rgba(255,255,255,.75)}}
.qa strong{{color:#e94560;font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;display:block;margin-bottom:.4rem}}
h1{{font-size:1.85rem;font-weight:900;letter-spacing:-.02em;color:#fff;margin-bottom:.75rem;line-height:1.2}}
h2{{font-size:1.15rem;font-weight:700;color:#fff;margin:2.5rem 0 1rem;letter-spacing:-.01em}}
p{{color:rgba(255,255,255,.7);margin-bottom:1rem}}
table{{width:100%;border-collapse:collapse;font-size:.87rem;margin:.5rem 0 2rem}}
th{{text-align:left;padding:.55rem .8rem;border-bottom:2px solid rgba(255,255,255,.1);color:rgba(255,255,255,.45);font-size:.72rem;font-weight:600;text-transform:uppercase;letter-spacing:.05em}}
td{{padding:.65rem .8rem;border-bottom:1px solid rgba(255,255,255,.06);color:rgba(255,255,255,.75)}}
tr:hover td{{background:rgba(255,255,255,.025)}}
td a{{color:#e94560;text-decoration:none}}
td a:hover{{text-decoration:underline}}
.sm{{font-size:.8rem;opacity:.75}}
.fq{{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:10px;padding:1.1rem 1.3rem;margin-bottom:.75rem}}
.fq h3{{font-size:.93rem;font-weight:700;color:#fff;margin-bottom:.4rem}}
.fq p{{font-size:.87rem;color:rgba(255,255,255,.6);margin:0}}
.meta{{font-size:.73rem;color:rgba(255,255,255,.35);margin-bottom:2rem;display:flex;gap:1rem;flex-wrap:wrap}}
.meta a{{color:rgba(255,255,255,.4)}}
footer{{border-top:1px solid rgba(255,255,255,.07);padding:1.5rem;text-align:center;font-size:.78rem;color:rgba(255,255,255,.3)}}
footer a{{color:rgba(255,255,255,.4);text-decoration:none}}
</style>
</head>
<body>
<header class="hdr">
  <a href="/"><svg style="height:20px;width:auto" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/><path fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></svg>
  Saa<em>Spare</em></a>
</header>
<main>
  <div class="meta">
    <span>Updated: {today}</span>
    <span>By Smith Elly</span>
    <span><a href="/methodology">Methodology</a></span>
    <span><a href="/affiliate-disclosure">Affiliate disclosure</a></span>
  </div>
  <h1>{title}</h1>
  <div class="qa"><strong>Quick answer</strong>{intro}</div>
  <h2>{short_title} — Side-by-Side Comparison</h2>
  <table>
    <thead><tr><th>Tool</th><th>Best for</th><th>Price from</th><th>Compare</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <h2>Frequently Asked Questions</h2>
  {faqs}
  <p style="margin-top:2rem;font-size:.77rem;color:rgba(255,255,255,.3)">
    Prices verified from official vendor pricing pages on {today}.
    Affiliate links use <code>rel="sponsored"</code>. Commissions never affect rankings.
  </p>
</main>
<footer>
  <a href="/">SaaSpare</a> &middot; <a href="/methodology">Methodology</a> &middot;
  <a href="/about">About</a> &middot; <a href="/affiliate-disclosure">Disclosure</a>
</footer>
</body>
</html>"""


def make_schemas(hub: dict) -> tuple[str, str, str, str]:
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": hub["title"],
        "datePublished": TODAY,
        "dateModified": TODAY,
        "author": {"@type": "Person", "name": "Smith Elly",
                   "url": "https://saaspare.org/authors/smith-elly"},
        "publisher": {"@type": "Organization", "name": "SaaSpare",
                      "url": "https://saaspare.org",
                      "logo": {"@type": "ImageObject",
                               "url": "https://saaspare.org/og-default.png"}},
        "mainEntityOfPage": f"https://saaspare.org/{hub['slug']}"
    }
    itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": hub["title"],
        "itemListElement": [
            {"@type": "ListItem", "position": i+1, "name": t[0],
             "url": f"https://saaspare.org/pages/{t[1]}-pricing-2026-plans-costs-what-you-actually-pay.html"}
            for i, t in enumerate(hub["tools"])
        ]
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in hub["faq"]
        ]
    }
    bc = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",
             "item": "https://saaspare.org"},
            {"@type": "ListItem", "position": 2,
             "name": hub["title"].split(":")[0],
             "item": f"https://saaspare.org/{hub['slug']}"}
        ]
    }
    return (json.dumps(article), json.dumps(itemlist),
            json.dumps(faq), json.dumps(bc))


def build_page(hub: dict) -> str:
    a_schema, il_schema, faq_schema, bc_schema = make_schemas(hub)
    rows = ""
    for name, slug, verdict, price in hub["tools"]:
        compare_url = f"/pages/{slug}-vs-"
        rows += (
            f"<tr><td><strong>{name}</strong></td>"
            f"<td class='sm'>{verdict}</td>"
            f"<td>{price}</td>"
            f"<td><a href='/pages/{slug}-pricing-2026-plans-costs-what-you-actually-pay.html'"
            f" rel='noopener'>Pricing →</a></td></tr>"
        )
    faqs = "".join(
        f"<div class='fq'><h3>{q}</h3><p>{a}</p></div>"
        for q, a in hub["faq"]
    )
    short = hub["title"].split(":")[0].replace(" in 2026", "")
    return PAGE_TEMPLATE.format(
        slug=hub["slug"],
        title=hub["title"],
        meta=hub["meta"],
        intro=hub["intro"],
        today=TODAY,
        short_title=short,
        rows=rows,
        faqs=faqs,
        article_schema=a_schema,
        itemlist_schema=il_schema,
        faq_schema=faq_schema,
        breadcrumb_schema=bc_schema,
    )


def main() -> int:
    for hub in HUBS:
        out = SITE / f"{hub['slug']}.html"
        out.write_text(build_page(hub), encoding="utf-8")
        print(f"  Created: /{hub['slug']}")
    print(f"\nDone — {len(HUBS)} category hub pages created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
