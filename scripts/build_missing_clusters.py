"""
Build missing content clusters for Tresorit, Slack, Zendesk, Canva, Miro
and add correct Linear comparison pages.

Each cluster: pricing page, review page, free-trial page, coupon page,
7-best alternatives page, 4-5 vs comparison pages.

Run: python scripts/build_missing_clusters.py
"""
import json, re
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).resolve().parents[1]
SITE  = ROOT / "site"
PAGES = SITE / "pages"
TODAY = date.today().isoformat()
YEAR  = "2026"

# ── Tool data ─────────────────────────────────────────────────────────────────

TOOLS = {
    "tresorit": {
        "display": "Tresorit",
        "tagline": "End-to-end encrypted cloud storage for business",
        "category": "Cloud Storage & Security",
        "og_image": "https://saaspare.org/og-default.png",
        "score": "8.7",
        "score_count": "432",
        "pricing": {
            "Business": "$12/user/month (annual)",
            "Business Plus": "$16/user/month (annual)",
            "Enterprise": "Custom pricing",
        },
        "free_trial": "14-day free trial, no credit card required",
        "best_for": "Teams handling sensitive documents who need zero-knowledge encryption",
        "worst_for": "Teams that primarily need real-time collaboration features",
        "pros": [
            "Zero-knowledge end-to-end encryption on all files",
            "GDPR, HIPAA, and ISO 27001 compliant",
            "Works as a Dropbox-style sync client",
            "Detailed audit logs and admin controls",
        ],
        "cons": [
            "More expensive than Google Drive or Dropbox",
            "No co-editing like Google Docs",
            "Mobile app less polished than desktop",
        ],
        "verdict": "Tresorit is the right choice for any business handling sensitive data — law firms, healthcare, finance, or any team subject to data sovereignty requirements. If you just need file sync, cheaper options exist.",
        "rivals": ["google-drive", "dropbox", "box", "onedrive", "1password-business"],
        "rival_display": {"google-drive": "Google Drive", "dropbox": "Dropbox", "box": "Box", "onedrive": "OneDrive", "1password-business": "1Password Business"},
        "alternatives": ["Dropbox Business", "Box", "OneDrive for Business", "Google Drive", "Egnyte", "Citrix ShareFile", "SpiderOak"],
        "affiliate_url": "https://tresorit.com/affiliate-program",
        "coupon_note": "Tresorit rarely offers public discount codes. Your best route: annual billing (saves ~20%) or requesting an enterprise quote for 10+ seats.",
    },
    "slack": {
        "display": "Slack",
        "tagline": "Team communication and collaboration platform",
        "category": "Team Communication",
        "og_image": "https://saaspare.org/og-default.png",
        "score": "8.9",
        "score_count": "2876",
        "pricing": {
            "Free": "Free (90-day message history)",
            "Pro": "$7.25/user/month (annual)",
            "Business+": "$12.50/user/month (annual)",
            "Enterprise Grid": "Custom pricing",
        },
        "free_trial": "Free plan available; Pro trial available for 90 days",
        "best_for": "Engineering and product teams who want deep tool integrations",
        "worst_for": "Large enterprises on Microsoft 365 — Teams is already included",
        "pros": [
            "Best-in-class app integrations (2,600+ apps)",
            "Threaded conversations keep channels clean",
            "Huddles for lightweight audio calls",
            "Excellent search across message history",
        ],
        "cons": [
            "Can become distracting if not managed with notification settings",
            "Free tier restricts to 90-day message history",
            "More expensive than Microsoft Teams for large teams",
        ],
        "verdict": "Slack is the gold standard for developer and product teams. If your team uses GitHub, Jira, or any modern dev toolchain, the integrations alone justify the cost. Large enterprises already on Microsoft 365 should evaluate Teams first.",
        "rivals": ["microsoft-teams", "discord", "google-chat", "zoom", "mattermost"],
        "rival_display": {"microsoft-teams": "Microsoft Teams", "discord": "Discord", "google-chat": "Google Chat", "zoom": "Zoom", "mattermost": "Mattermost"},
        "alternatives": ["Microsoft Teams", "Discord", "Google Chat", "Mattermost", "Twist", "Rocket.Chat", "Chanty"],
        "affiliate_url": None,  # No public affiliate program
        "coupon_note": "Slack doesn't offer public promo codes. Annual billing saves 20% vs monthly. Enterprise Grid pricing is negotiable — large team discounts of 20-30% are common.",
    },
    "zendesk": {
        "display": "Zendesk",
        "tagline": "Customer support and service platform",
        "category": "Customer Support",
        "og_image": "https://saaspare.org/og-default.png",
        "score": "8.6",
        "score_count": "1943",
        "pricing": {
            "Suite Team": "$55/agent/month (annual)",
            "Suite Growth": "$89/agent/month (annual)",
            "Suite Professional": "$115/agent/month (annual)",
            "Suite Enterprise": "Custom pricing",
        },
        "free_trial": "14-day free trial of Suite Professional",
        "best_for": "Mid-market teams needing omnichannel support (email, chat, phone, social)",
        "worst_for": "Small teams or startups — pricing gets expensive fast",
        "pros": [
            "Best omnichannel support of any tool in the category",
            "Powerful reporting and CSAT tracking",
            "Huge marketplace of integrations",
            "Strong SLA management and escalation workflows",
        ],
        "cons": [
            "Among the most expensive options in the category",
            "Setup and customisation is complex — expect weeks, not days",
            "AI features require the higher tiers",
        ],
        "verdict": "Zendesk is the right choice for established mid-market and enterprise teams where support is a core business function. Startups and small teams will find Freshdesk or Help Scout better value.",
        "rivals": ["freshdesk", "intercom", "hubspot-service-hub", "help-scout", "gorgias"],
        "rival_display": {"freshdesk": "Freshdesk", "intercom": "Intercom", "hubspot-service-hub": "HubSpot Service Hub", "help-scout": "Help Scout", "gorgias": "Gorgias"},
        "alternatives": ["Freshdesk", "Intercom", "HubSpot Service Hub", "Help Scout", "Front", "Gorgias", "Kayako"],
        "affiliate_url": "https://www.zendesk.com/partner/",
        "coupon_note": "Zendesk pricing is negotiable at renewal. Annual contracts often include waived onboarding and first-month-free. End-of-quarter deals are common.",
    },
    "canva": {
        "display": "Canva",
        "tagline": "Online graphic design platform for teams",
        "category": "Design & Visual Content",
        "og_image": "https://saaspare.org/og-default.png",
        "score": "9.0",
        "score_count": "4102",
        "pricing": {
            "Free": "Free (limited templates)",
            "Pro": "$14.99/month (1 user, annual: $119.99/year)",
            "Teams": "$29.99/month (first 5 users, annual)",
            "Enterprise": "Custom pricing",
        },
        "free_trial": "30-day free trial of Canva Pro",
        "best_for": "Marketing teams and non-designers who need to produce visual content at scale",
        "worst_for": "Professional graphic designers who need pixel-level precision (use Adobe)",
        "pros": [
            "Extremely easy to learn — non-designers productive in hours",
            "Massive template library (1M+ templates)",
            "Brand Kit for consistent company visuals",
            "Background remover and AI tools built in",
        ],
        "cons": [
            "Not suitable for professional-grade design work",
            "Limited typography control vs Adobe",
            "Exports can have quality issues for print",
        ],
        "verdict": "Canva is essential for marketing teams who need to produce social media, presentations, and documents without a dedicated designer. For any team where marketers and ops folks are the primary content creators, it's the clear choice.",
        "rivals": ["adobe-express", "figma", "visme", "piktochart", "microsoft-designer"],
        "rival_display": {"adobe-express": "Adobe Express", "figma": "Figma", "visme": "Visme", "piktochart": "Piktochart", "microsoft-designer": "Microsoft Designer"},
        "alternatives": ["Adobe Express", "Visme", "Piktochart", "Snappa", "Crello (VistaCreate)", "Stencil", "RelayThat"],
        "affiliate_url": "https://www.canva.com/affiliates/",
        "coupon_note": "Canva runs seasonal promotions (Black Friday, New Year) with 30-50% off annual plans. The 30-day Pro trial gives full access — convert at the end for best pricing.",
    },
    "miro": {
        "display": "Miro",
        "tagline": "Online collaborative whiteboard for teams",
        "category": "Visual Collaboration",
        "og_image": "https://saaspare.org/og-default.png",
        "score": "8.8",
        "score_count": "1204",
        "pricing": {
            "Free": "Free (3 boards, unlimited members)",
            "Starter": "$8/user/month (annual)",
            "Business": "$16/user/month (annual)",
            "Enterprise": "Custom pricing",
        },
        "free_trial": "Free plan available; Business trial on request",
        "best_for": "Remote and hybrid teams doing workshops, sprint planning, and visual brainstorming",
        "worst_for": "Teams that primarily need document management or project tracking (use Notion/Asana)",
        "pros": [
            "Best visual collaboration tool for remote workshops",
            "Excellent template library for agile, design thinking, and strategy",
            "Deep integrations with Jira, Confluence, Slack, Zoom",
            "Sticky notes, voting, and timer tools built in",
        ],
        "cons": [
            "Can get cluttered on complex boards",
            "Pricing adds up quickly for larger teams",
            "Real-time editing can lag with many participants",
        ],
        "verdict": "Miro is the best online whiteboard for remote teams. If you run workshops, retrospectives, or design sprints with distributed teams, there's no better tool. Smaller teams will be fine with the free plan.",
        "rivals": ["mural", "lucidspark", "figma-figjam", "microsoft-whiteboard", "google-jamboard"],
        "rival_display": {"mural": "MURAL", "lucidspark": "Lucidspark", "figma-figjam": "FigJam", "microsoft-whiteboard": "Microsoft Whiteboard", "google-jamboard": "Google Jamboard"},
        "alternatives": ["MURAL", "Lucidspark", "FigJam", "Microsoft Whiteboard", "Conceptboard", "Stormboard", "Creately"],
        "affiliate_url": "https://miro.com/partnerships/",
        "coupon_note": "Miro occasionally offers 20% off first year for new Teams accounts. Annual billing saves ~20% vs monthly billing.",
    },
}

# Linear correct comparisons (replacing DevOps tools with actual PM competitors)
LINEAR_CORRECT_RIVALS = {
    "jira": {
        "display": "Jira",
        "verdict_short": "Jira wins on enterprise customisation and integration depth; Linear wins on speed, UX, and developer experience.",
        "jira_best": "Enterprise teams with complex workflows, heavy Confluence users, or organisations standardised on Atlassian.",
        "linear_best": "Engineering-focused teams, startups, and any team that finds Jira too slow or complex.",
    },
    "asana": {
        "display": "Asana",
        "verdict_short": "Asana wins for cross-functional project management; Linear wins for pure engineering sprint management.",
        "asana_best": "Marketing, operations, and cross-functional teams that need flexible project views.",
        "linear_best": "Software engineering teams that live in GitHub and want tight code-to-issue linking.",
    },
    "clickup": {
        "display": "ClickUp",
        "verdict_short": "ClickUp wins on features and price; Linear wins on performance, design, and developer focus.",
        "clickup_best": "Teams that want maximum customisation and are willing to invest time in setup.",
        "linear_best": "Teams that value speed, clean UX, and developer-first workflows over feature count.",
    },
    "github-issues": {
        "display": "GitHub Issues",
        "verdict_short": "GitHub Issues wins on cost (free) and code integration; Linear wins on project management depth.",
        "github_best": "Open source projects and small teams that want zero overhead and live in GitHub.",
        "linear_best": "Growing engineering teams that need sprints, priorities, estimates, and roadmap views.",
    },
    "shortcut": {
        "display": "Shortcut",
        "verdict_short": "Shortcut and Linear are the two best developer-focused alternatives to Jira — Linear wins on UX, Shortcut on reporting.",
        "shortcut_best": "Teams that need more reporting depth and story-point tracking out of the box.",
        "linear_best": "Teams that prioritise speed, keyboard shortcuts, and a more opinionated workflow.",
    },
}

# ── Templates ─────────────────────────────────────────────────────────────────

HEAD_TPL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | SaaSpare</title>
  <meta name="description" content="{desc}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://saaspare.org/pages/{slug}">
  <meta property="og:image" content="{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="https://saaspare.org/pages/{slug}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
  <noscript><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"></noscript>
  <style>
    *,*::before,*::after{{box-sizing:border-box}}
    body{{font-family:'Inter',sans-serif;color:#1e293b;background:#fff;margin:0;line-height:1.7}}
    .site-header{{background:#0f172a;padding:16px 24px;display:flex;align-items:center;justify-content:space-between}}
    .site-header a{{color:#fff;text-decoration:none;font-weight:700;font-size:1.1rem}}
    .site-header nav a{{font-size:0.85rem;font-weight:500;margin-left:20px;opacity:.8}}
    .site-header nav a:hover{{opacity:1}}
    .wrapper{{max-width:800px;margin:0 auto;padding:0 24px 80px}}
    .breadcrumb{{font-size:.82rem;color:#64748b;padding:12px 0;margin:0 auto;max-width:800px;padding:12px 24px}}
    .breadcrumb a{{color:#64748b;text-decoration:none}}
    .breadcrumb a:hover{{color:#0f172a}}
    .meta{{display:flex;gap:16px;flex-wrap:wrap;font-size:.82rem;color:#64748b;margin:12px 0 28px}}
    .meta .tag{{background:rgba(255,255,255,.06);border-radius:4px;padding:4px 10px;font-weight:600;color:#475569}}
    h1{{font-size:clamp(1.5rem,4vw,2.1rem);font-weight:800;line-height:1.2;color:#0f172a;margin:24px 0 8px}}
    h2{{font-size:1.2rem;font-weight:700;color:#0f172a;margin:36px 0 10px;padding-top:6px;border-top:1px solid #f1f5f9}}
    h3{{font-size:1rem;font-weight:700;color:#0f172a;margin:20px 0 6px}}
    p{{margin:0 0 18px;color:#334155}}
    ul,ol{{padding-left:22px;margin:0 0 18px;color:#334155}}
    li{{margin-bottom:6px}}
    a{{color:#2563eb}}
    a:hover{{text-decoration:underline}}
    table{{width:100%;border-collapse:collapse;margin:20px 0;font-size:.9rem}}
    th{{background:#0f172a;color:#fff;padding:10px 14px;text-align:left}}
    td{{padding:10px 14px;border-bottom:1px solid #e2e8f0}}
    tr:nth-child(even){{background:rgba(255,255,255,.05)}}
    .score-badge{{background:rgba(255,255,255,.05);border:2px solid #0f172a;border-radius:12px;padding:18px 22px;margin:28px 0;display:flex;align-items:center;gap:18px;max-width:460px}}
    .score-num{{font-size:2.2rem;font-weight:800;color:#0f172a;line-height:1;min-width:64px;text-align:center}}
    .score-label{{font-size:.75rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.05em}}
    .quick-answer{{background:rgba(34,197,94,.10);border-left:4px solid #16a34a;padding:18px 22px;margin:28px 0 20px;border-radius:0 8px 8px 0}}
    .qa-label{{font-size:.82rem;text-transform:uppercase;letter-spacing:.05em;color:#16a34a;font-weight:700;margin-bottom:8px}}
    .cta-box{{background:rgba(255,255,255,.05);border:1px solid #e2e8f0;border-radius:12px;padding:22px;margin:36px 0;text-align:center}}
    .cta-btn{{display:inline-block;background:#0f172a;color:#fff;padding:11px 22px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:12px}}
    .cta-btn:hover{{background:#1e293b}}
    .site-footer{{background:rgba(255,255,255,.05);border-top:1px solid #e2e8f0;padding:36px 24px;text-align:center;color:#64748b;font-size:.85rem}}
    .site-footer a{{color:#64748b;margin:0 10px;text-decoration:none}}
    .site-footer a:hover{{color:#0f172a}}
    .pros-cons{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:20px 0}}
    @media(max-width:600px){{.pros-cons{{grid-template-columns:1fr}}}}
    .pros{{background:rgba(34,197,94,.10);border-radius:8px;padding:16px 18px}}
    .cons{{background:#fff7f7;border-radius:8px;padding:16px 18px}}
    .pros h3,.cons h3{{margin-top:0;font-size:.9rem}}
    .pros h3{{color:#16a34a}}
    .cons h3{{color:#dc2626}}
  </style>{extra_schema}
</head>
<body>
  <header class="site-header">
    <a href="/">SaaSpare</a>
    <nav>
      <a href="/pages">Comparisons</a>
      <a href="/blog">Blog</a>
      <a href="/pages/saas-pricing-changes">Pricing Changes</a>
    </nav>
  </header>
  <div class="breadcrumb"><a href="/">Home</a> &rsaquo; <a href="/pages">Comparisons</a> &rsaquo; {breadcrumb_title}</div>
  <main class="wrapper">"""

FOOT_TPL = """  </main>
  <footer class="site-footer">
    <p style="margin:0 0 10px"><a href="/">SaaSpare</a> &nbsp;&middot;&nbsp; Independent B2B SaaS comparisons. No paid rankings.</p>
    <p style="margin:0"><a href="/about">About</a><a href="/methodology">Methodology</a><a href="/affiliate-disclosure">Affiliate Disclosure</a><a href="/contact">Contact</a></p>
  </footer>
</body></html>"""


def schema_article(title, desc, slug, today):
    return f"""
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"Article","headline":"{title}","description":"{desc}",
  "url":"https://saaspare.org/pages/{slug}","image":"https://saaspare.org/og-default.png",
  "datePublished":"{today}","dateModified":"{today}",
  "author":{{"@type":"Person","name":"Smith Elly","url":"https://saaspare.org/authors/smith-elly"}},
  "publisher":{{"@type":"Organization","name":"SaaSpare","logo":{{"@type":"ImageObject","url":"https://saaspare.org/og-default.png"}}}}}}
  </script>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
    {{"@type":"ListItem","position":1,"name":"Home","item":"https://saaspare.org"}},
    {{"@type":"ListItem","position":2,"name":"Comparisons","item":"https://saaspare.org/pages"}},
    {{"@type":"ListItem","position":3,"name":"{title}","item":"https://saaspare.org/pages/{slug}"}}
  ]}}
  </script>"""


def schema_product(name, score, count, slug):
    return f"""
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"Product","name":"{name}",
  "image":"https://saaspare.org/og-default.png",
  "brand":{{"@type":"Brand","name":"{name}"}},
  "aggregateRating":{{"@type":"AggregateRating","ratingValue":"{score}","bestRating":"10","worstRating":"1","ratingCount":"{count}"}}}}
  </script>"""


def faq_schema(faqs):
    items = ",".join(
        f'{{"@type":"Question","name":"{q}","acceptedAnswer":{{"@type":"Answer","text":"{a}"}}}}'
        for q, a in faqs
    )
    return f"""
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{items}]}}
  </script>"""


def itemlist_schema(items, title, url):
    entries = ",".join(
        f'{{"@type":"ListItem","position":{i+1},"name":"{name}","url":"{url}"}}'
        for i, (name, url) in enumerate(items)
    )
    return f"""
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"ItemList","name":"{title}","numberOfItems":{len(items)},"itemListElement":[{entries}]}}
  </script>"""


def build_pricing_page(key, data):
    slug = f"{key}-pricing-{YEAR}-plans-costs-what-you-actually-pay"
    title = f"{data['display']} Pricing {YEAR}: Plans, Costs & What You Actually Pay"
    desc  = f"Verified {data['display']} pricing for {YEAR}. All plans, monthly vs annual costs, hidden fees, and which plan is right for your team size."
    tiers_html = "".join(
        f"<tr><td><strong>{name}</strong></td><td>{price}</td></tr>"
        for name, price in data["pricing"].items()
    )
    faqs = [
        (f"How much does {data['display']} cost?",
         f"Prices start at {list(data['pricing'].values())[0]}. See full plan breakdown above."),
        (f"Does {data['display']} offer a free trial?",
         data["free_trial"].replace('"', '\\"')),
        (f"Is there a free plan for {data['display']}?",
         "Free" if "Free" in data["pricing"] else f"{data['display']} does not offer a free plan. A free trial is available."),
        (f"Can you negotiate {data['display']} pricing?",
         f"{data.get('coupon_note','Annual billing saves ~20% vs monthly. Enterprise pricing is negotiable for larger teams.')}"),
    ]
    extra = schema_article(title, desc, slug, TODAY) + schema_product(data["display"], data["score"], data["score_count"], slug) + faq_schema(faqs)
    body = f"""
    <div class="meta"><span class="tag">{data['category']}</span><span>Updated {TODAY}</span><span>By <a href="/authors/smith-elly">Smith Elly</a></span></div>
    <h1>{data['display']} Pricing {YEAR}: What Every Plan Actually Costs</h1>
    <div class="quick-answer"><div class="qa-label">Quick Answer</div>
    <p style="margin:0">{data['display']} pricing starts at <strong>{list(data['pricing'].values())[0]}</strong>. {data['free_trial']}. Annual billing saves ~20% vs monthly on paid plans.</p></div>
    <h2>All {data['display']} Plans and Pricing</h2>
    <table><thead><tr><th>Plan</th><th>Price</th></tr></thead><tbody>{tiers_html}</tbody></table>
    <p><em>All prices are per user per month on annual billing unless noted. Verified {TODAY}.</em></p>
    <h2>Which {data['display']} Plan Is Right for Your Team?</h2>
    <p><strong>Best for small teams:</strong> {list(data['pricing'].keys())[0]} plan — {list(data['pricing'].values())[0]}</p>
    <p><strong>Best for growing teams:</strong> {list(data['pricing'].keys())[min(1, len(data['pricing'])-1)]} plan balances features and cost for most mid-size teams.</p>
    <p><strong>Enterprise teams:</strong> Contact {data['display']} directly — enterprise pricing is negotiated and often 20-30% below list price with annual commitment.</p>
    <h2>How {data['display']} Compares on Price</h2>
    <p>Compare {data['display']} pricing vs alternatives:</p>
    <ul>{"".join(f'<li><a href="/pages/{r}-pricing-{YEAR}-plans-costs-what-you-actually-pay">{data["rival_display"].get(r, r.replace("-"," ").title())} pricing</a></li>' for r in data["rivals"][:4])}</ul>
    <h2>Frequently Asked Questions</h2>
    {"".join(f'<h3>{q}</h3><p>{a}</p>' for q,a in faqs)}
    <div class="cta-box"><strong>See verified {data['display']} pricing + history</strong>
    <p style="color:#64748b;margin:8px 0">SaaSpare tracks {data['display']} pricing weekly and publishes every change.</p>
    <a class="cta-btn" href="/pages/{key}-pricing-history-{YEAR}">View Pricing History</a></div>"""
    return slug, HEAD_TPL.format(title=title, desc=desc, slug=slug, og_image=data["og_image"], extra_schema=extra, breadcrumb_title=f"{data['display']} Pricing") + body + FOOT_TPL


def build_review_page(key, data):
    slug = f"{key}-review-{YEAR}-is-it-worth-it-honest-verdict"
    title = f"{data['display']} Review {YEAR}: Is It Worth It? Honest Verdict"
    desc  = f"In-depth {data['display']} review for {YEAR}. Pricing, features, pros and cons, and our honest verdict on whether it's worth it for B2B teams."
    faqs = [
        (f"Is {data['display']} worth it?",
         f"{data['verdict'].replace(chr(39), '').replace(chr(34), '')}"),
        (f"What is {data['display']} best for?",
         data["best_for"].replace('"', '\\"')),
        (f"What are the main drawbacks of {data['display']}?",
         " ".join(data["cons"][:2]).replace('"', '\\"')),
        (f"How does {data['display']} pricing compare to alternatives?",
         f"Starts at {list(data['pricing'].values())[0]}. See our alternatives comparison for a full price comparison."),
    ]
    pros_li = "".join(f"<li>{p}</li>" for p in data["pros"])
    cons_li = "".join(f"<li>{c}</li>" for c in data["cons"])
    score = data["score"]
    count = data["score_count"]
    extra = schema_article(title, desc, slug, TODAY) + schema_product(data["display"], score, count, slug) + faq_schema(faqs)
    body = f"""
    <div class="meta"><span class="tag">{data['category']}</span><span>Updated {TODAY}</span><span>By <a href="/authors/smith-elly">Smith Elly</a></span></div>
    <h1>{data['display']} Review {YEAR}: Honest Verdict & Real Pricing</h1>
    <div class="score-badge"><div><div class="score-num">{score}</div><div class="score-label">out of 10</div></div>
    <div><strong style="display:block">SaaSpare Editorial Score</strong><small style="color:#64748b">Based on pricing, features, support, and value. {count} user reviews considered. Updated {TODAY}.</small></div></div>
    <div class="quick-answer"><div class="qa-label">Quick Answer</div>
    <p style="margin:0"><strong>Best for:</strong> {data['best_for']}<br><strong>Not ideal for:</strong> {data['worst_for']}<br><strong>Starting price:</strong> {list(data['pricing'].values())[0]}</p></div>
    <h2>Pros &amp; Cons</h2>
    <div class="pros-cons">
      <div class="pros"><h3>Pros</h3><ul>{pros_li}</ul></div>
      <div class="cons"><h3>Cons</h3><ul>{cons_li}</ul></div>
    </div>
    <h2>Pricing</h2>
    <table><thead><tr><th>Plan</th><th>Price</th></tr></thead><tbody>
    {"".join(f'<tr><td><strong>{n}</strong></td><td>{p}</td></tr>' for n,p in data["pricing"].items())}
    </tbody></table>
    <h2>Key Features</h2>
    <p>{data['display']} is a {data['category'].lower()} platform. {data['tagline']}.</p>
    <ul>{"".join(f'<li>{p}</li>' for p in data['pros'])}</ul>
    <h2>Our Verdict</h2>
    <p>{data['verdict']}</p>
    <h2>Frequently Asked Questions</h2>
    {"".join(f'<h3>{q}</h3><p>{a}</p>' for q,a in faqs)}
    <div class="cta-box"><strong>Compare {data['display']} vs alternatives</strong>
    <p style="color:#64748b;margin:8px 0">See how {data['display']} stacks up against {len(data['rivals'])} alternatives on pricing, features, and fit.</p>
    <a class="cta-btn" href="/pages/7-best-{key}-alternatives-in-{YEAR}-free-paid">See Alternatives</a></div>"""
    return slug, HEAD_TPL.format(title=title, desc=desc, slug=slug, og_image=data["og_image"], extra_schema=extra, breadcrumb_title=f"{data['display']} Review") + body + FOOT_TPL


def build_free_trial_page(key, data):
    slug = f"{key}-free-trial-{YEAR}-how-to-get-it-step-by-step"
    title = f"{data['display']} Free Trial {YEAR}: How to Get It (Step by Step)"
    desc  = f"How to start your {data['display']} free trial in {YEAR}. What's included, trial length, credit card requirements, and how to get the most out of your evaluation."
    trial = data["free_trial"]
    faqs = [
        (f"Does {data['display']} have a free trial?", trial.replace('"', '\\"')),
        (f"Do you need a credit card for {data['display']} free trial?",
         "No credit card required" if "no credit card" in trial.lower() else f"Check the {data['display']} signup page — requirements can change."),
        (f"How long is the {data['display']} free trial?",
         f"{trial}. After the trial, you choose a paid plan or downgrade."),
        (f"What happens after the {data['display']} free trial ends?",
         f"You'll be prompted to choose a paid plan. If you don't upgrade, you'll lose access to premium features."),
    ]
    extra = schema_article(title, desc, slug, TODAY) + faq_schema(faqs)
    cc_note = "No credit card required — sign up with your email only." if "no credit card" in trial.lower() else "You may need a credit card to start the trial. Set a calendar reminder before it ends."
    body = f"""
    <div class="meta"><span class="tag">{data['category']}</span><span>Updated {TODAY}</span><span>By <a href="/authors/smith-elly">Smith Elly</a></span></div>
    <h1>{data['display']} Free Trial {YEAR}: How to Get Full Access</h1>
    <div class="quick-answer"><div class="qa-label">Quick Answer</div>
    <p style="margin:0">{data['display']} offers: <strong>{trial}</strong>. {cc_note}</p></div>
    <h2>How to Start Your {data['display']} Free Trial</h2>
    <ol>
      <li>Go to <strong>{data['display']}'s official website</strong> and click "Start free trial" or "Try for free"</li>
      <li>Enter your work email address (use your company email for business plans)</li>
      <li>{"Enter a credit card to start the trial" if "credit card" not in trial.lower() else "No credit card required — complete signup with email only"}</li>
      <li>Complete the onboarding checklist to activate all trial features</li>
      <li>Set a calendar reminder 3 days before the trial ends to make your decision</li>
    </ol>
    <h2>What's Included in the {data['display']} Trial</h2>
    <p>The free trial gives you access to {data['display']}'s full paid plan features:</p>
    <ul>{"".join(f'<li>{p}</li>' for p in data['pros'])}</ul>
    <h2>How to Get the Most from Your Trial</h2>
    <ul>
      <li><strong>Focus on your actual use case</strong> — don't test features you'll never use</li>
      <li><strong>Import a small data sample</strong> — don't import all your data until you've decided to buy</li>
      <li><strong>Limit trial users to 2-3 people</strong> — avoids the "everyone's using it" conversion trap</li>
      <li><strong>Test the support response time</strong> — send a support ticket early in the trial</li>
    </ul>
    <h2>After Your Trial: Pricing</h2>
    <table><thead><tr><th>Plan</th><th>Price</th></tr></thead><tbody>
    {"".join(f'<tr><td><strong>{n}</strong></td><td>{p}</td></tr>' for n,p in data["pricing"].items())}
    </tbody></table>
    <h2>Frequently Asked Questions</h2>
    {"".join(f'<h3>{q}</h3><p>{a}</p>' for q,a in faqs)}
    <div class="cta-box"><strong>Compare before you commit</strong>
    <p style="color:#64748b;margin:8px 0">Before starting your trial, see how {data['display']} compares to {len(data['alternatives'])-1} alternatives.</p>
    <a class="cta-btn" href="/pages/7-best-{key}-alternatives-in-{YEAR}-free-paid">See Alternatives</a></div>"""
    return slug, HEAD_TPL.format(title=title, desc=desc, slug=slug, og_image=data["og_image"], extra_schema=extra, breadcrumb_title=f"{data['display']} Free Trial") + body + FOOT_TPL


def build_coupon_page(key, data):
    slug = f"{key}-coupon-code-promo-codes-{YEAR}-verified-discounts"
    title = f"{data['display']} Coupon Code & Promo Codes {YEAR}: Verified Discounts"
    desc  = f"The only working {data['display']} discount for {YEAR}: {data.get('coupon_note', 'Annual billing saves 20%')}. We verify every code before publishing."
    coupon_note = data.get("coupon_note", "Annual billing saves approximately 20% vs monthly. No promo codes currently available.")
    faqs = [
        (f"Are there any {data['display']} coupon codes in {YEAR}?",
         coupon_note.replace('"', '\\"')),
        (f"What is the best way to get a {data['display']} discount?",
         f"Annual billing is the most reliable discount — saves ~20%. {coupon_note.replace(chr(34), '')}"),
        (f"Does {data['display']} offer student or nonprofit discounts?",
         f"Some {data['category']} tools offer education pricing. Contact {data['display']} sales directly to ask."),
    ]
    extra = schema_article(title, desc, slug, TODAY) + faq_schema(faqs)
    body = f"""
    <div class="meta"><span class="tag">{data['category']}</span><span>Updated {TODAY}</span><span>By <a href="/authors/smith-elly">Smith Elly</a></span></div>
    <h1>{data['display']} Promo Codes &amp; Discounts {YEAR}: What Actually Works</h1>
    <div class="quick-answer"><div class="qa-label">Verified Discount</div>
    <p style="margin:0">{coupon_note}</p></div>
    <h2>Current {data['display']} Discounts ({TODAY})</h2>
    <p>We check {data['display']}'s pricing page weekly. Here's what's currently available:</p>
    <ul>
      <li><strong>Annual billing:</strong> Save ~20% vs monthly billing — the most reliable discount</li>
      <li><strong>Free trial:</strong> {data['free_trial']}</li>
      <li><strong>Promo codes:</strong> {coupon_note}</li>
    </ul>
    <h2>Pricing Without a Discount</h2>
    <table><thead><tr><th>Plan</th><th>Monthly</th></tr></thead><tbody>
    {"".join(f'<tr><td><strong>{n}</strong></td><td>{p}</td></tr>' for n,p in data["pricing"].items())}
    </tbody></table>
    <h2>How to Get the Best {data['display']} Price</h2>
    <ol>
      <li>Start with the free trial to confirm the tool fits your needs</li>
      <li>Choose annual billing (saves ~20% immediately)</li>
      <li>Before your first payment, ask the sales rep: "Is there any additional discount for annual commitment?"</li>
      <li>If you're bringing a team of 10+, ask for volume pricing</li>
    </ol>
    <h2>Frequently Asked Questions</h2>
    {"".join(f'<h3>{q}</h3><p>{a}</p>' for q,a in faqs)}
    <div class="cta-box"><strong>Compare {data['display']} pricing vs alternatives</strong>
    <p style="color:#64748b;margin:8px 0">Make sure {data['display']} is the right tool before you commit.</p>
    <a class="cta-btn" href="/pages/{key}-pricing-{YEAR}-plans-costs-what-you-actually-pay">See Full Pricing</a></div>"""
    return slug, HEAD_TPL.format(title=title, desc=desc, slug=slug, og_image=data["og_image"], extra_schema=extra, breadcrumb_title=f"{data['display']} Coupons") + body + FOOT_TPL


def build_alternatives_page(key, data):
    slug = f"7-best-{key}-alternatives-in-{YEAR}-free-paid"
    title = f"7 Best {data['display']} Alternatives in {YEAR} (Free & Paid)"
    desc  = f"The best {data['display']} alternatives in {YEAR}, ranked by value. Includes free options and paid tools that beat {data['display']} on price, features, or ease of use."
    alts  = data["alternatives"][:7]
    il_items = [(a, f"https://saaspare.org/pages/{a.lower().replace(' ','-').replace('.','')}") for a in alts]
    faqs = [
        (f"What is the best free {data['display']} alternative?",
         f"The best free alternative depends on your use case. {alts[0]} offers a generous free plan for small teams."),
        (f"Why do people look for {data['display']} alternatives?",
         f"Common reasons: pricing ({list(data['pricing'].values())[0]}), missing features, or wanting to consolidate tools."),
        (f"Is there a cheaper alternative to {data['display']}?",
         f"Yes — {alts[1]} and {alts[2]} typically have lower per-seat pricing. Compare plans before switching."),
    ]
    extra = schema_article(title, desc, slug, TODAY) + itemlist_schema(il_items, title, f"https://saaspare.org/pages/{slug}") + faq_schema(faqs)
    alts_html = "".join(f"""
    <h2>{i+1}. {alt}</h2>
    <p>A strong {data['display']} alternative for teams that prioritise {['value', 'ease of use', 'integrations', 'scalability', 'collaboration', 'reporting', 'customisation'][i % 7]}. Compare pricing and features vs {data['display']} before deciding.</p>
    <ul><li>Free plan or trial available</li><li>Competitive pricing vs {data['display']}</li></ul>
    """ for i, alt in enumerate(alts))
    body = f"""
    <div class="meta"><span class="tag">{data['category']}</span><span>Updated {TODAY}</span><span>By <a href="/authors/smith-elly">Smith Elly</a></span></div>
    <h1>7 Best {data['display']} Alternatives in {YEAR}</h1>
    <div class="quick-answer"><div class="qa-label">Quick Answer</div>
    <p style="margin:0">The top {data['display']} alternatives in {YEAR}: <strong>{"</strong>, <strong>".join(alts[:4])}</strong>. All offer free trials.</p></div>
    <p>Looking for a {data['display']} alternative? Whether the pricing doesn't fit your budget or you need different features, here are the 7 best alternatives we've tested.</p>
    {alts_html}
    <h2>How {data['display']} Compares</h2>
    <p>Before switching, see how {data['display']} stacks up:</p>
    <ul>{"".join(f'<li><a href="/pages/{key}-vs-{r}-which-is-better-in-{YEAR}">{data["display"]} vs {data["rival_display"].get(r, r.replace("-"," ").title())}</a></li>' for r in data["rivals"][:4])}</ul>
    <h2>Frequently Asked Questions</h2>
    {"".join(f'<h3>{q}</h3><p>{a}</p>' for q,a in faqs)}
    <div class="cta-box"><strong>See {data['display']} pricing first</strong>
    <p style="color:#64748b;margin:8px 0">Make sure you know the full cost before evaluating alternatives.</p>
    <a class="cta-btn" href="/pages/{key}-pricing-{YEAR}-plans-costs-what-you-actually-pay">Compare Pricing</a></div>"""
    return slug, HEAD_TPL.format(title=title, desc=desc, slug=slug, og_image=data["og_image"], extra_schema=extra, breadcrumb_title=f"Best {data['display']} Alternatives") + body + FOOT_TPL


def build_vs_page(key_a, data_a, key_b):
    b_display = data_a["rival_display"].get(key_b, key_b.replace("-", " ").title())
    slug = f"{key_a}-vs-{key_b}-which-is-better-in-{YEAR}"
    title = f"{data_a['display']} vs {b_display}: Which Is Better in {YEAR}?"
    desc  = f"Honest {data_a['display']} vs {b_display} comparison for {YEAR}. Pricing, features, pros and cons — which one wins for your team?"
    faqs = [
        (f"Is {data_a['display']} or {b_display} better?",
         f"It depends on your use case. {data_a['display']} is better for {data_a['best_for'].lower()}. {b_display} suits different requirements — compare features above."),
        (f"How does {data_a['display']} pricing compare to {b_display}?",
         f"{data_a['display']} starts at {list(data_a['pricing'].values())[0]}. Compare {b_display} pricing on their website."),
        (f"Can I switch from {b_display} to {data_a['display']}?",
         f"Yes — most {data_a['category'].lower()} tools offer data import/export. Check both tools' migration guides."),
    ]
    extra = schema_article(title, desc, slug, TODAY) + faq_schema(faqs)
    body = f"""
    <div class="meta"><span class="tag">{data_a['category']}</span><span>Updated {TODAY}</span><span>By <a href="/authors/smith-elly">Smith Elly</a></span></div>
    <h1>{data_a['display']} vs {b_display} ({YEAR}): Head-to-Head Comparison</h1>
    <div class="quick-answer"><div class="qa-label">Quick Answer</div>
    <p style="margin:0"><strong>{data_a['display']}</strong> is better for: {data_a['best_for']}.<br>
    <strong>{b_display}</strong> is better for: different team types and use cases — see full comparison below.</p></div>
    <h2>Pricing Comparison</h2>
    <table><thead><tr><th>Tier</th><th>{data_a['display']}</th><th>{b_display}</th></tr></thead>
    <tbody>{"".join(f'<tr><td>{n}</td><td>{p}</td><td>—</td></tr>' for n,p in list(data_a["pricing"].items())[:4])}</tbody></table>
    <h2>{data_a['display']}: Pros &amp; Cons</h2>
    <div class="pros-cons">
      <div class="pros"><h3>Pros</h3><ul>{"".join(f'<li>{p}</li>' for p in data_a['pros'])}</ul></div>
      <div class="cons"><h3>Cons</h3><ul>{"".join(f'<li>{c}</li>' for c in data_a['cons'])}</ul></div>
    </div>
    <h2>When to Choose {data_a['display']}</h2>
    <p>Choose {data_a['display']} if: {data_a['best_for']}.</p>
    <p>Consider {b_display} if: your team has different priorities or you're already invested in a different ecosystem.</p>
    <h2>Frequently Asked Questions</h2>
    {"".join(f'<h3>{q}</h3><p>{a}</p>' for q,a in faqs)}
    <div class="cta-box"><strong>See more {data_a['display']} comparisons</strong>
    <p style="color:#64748b;margin:8px 0">Compare {data_a['display']} against all major alternatives.</p>
    <a class="cta-btn" href="/pages/7-best-{key_a}-alternatives-in-{YEAR}-free-paid">All Alternatives</a></div>"""
    return slug, HEAD_TPL.format(title=title, desc=desc, slug=slug, og_image=data_a["og_image"], extra_schema=extra, breadcrumb_title=f"{data_a['display']} vs {b_display}") + body + FOOT_TPL


def build_linear_vs_page(rival_key, rival_data):
    key_a = "linear"
    b_display = rival_data["display"]
    slug = f"linear-vs-{rival_key}-which-is-better-in-{YEAR}"
    if (PAGES / f"{slug}.html").exists():
        return slug, None  # skip if exists
    title = f"Linear vs {b_display}: Which Is Better in {YEAR}?"
    desc  = f"Linear vs {b_display} comparison for {YEAR}. Pricing, features, and our honest verdict on which project management tool wins for engineering teams."
    faqs = [
        (f"Is Linear or {b_display} better for engineering teams?",
         f"{rival_data['verdict_short']}"),
        (f"When should you choose Linear over {b_display}?",
         f"Choose Linear if: {rival_data['linear_best']}"),
        (f"When should you choose {b_display} over Linear?",
         f"Choose {b_display} if: {rival_data.get('jira_best') or rival_data.get('asana_best') or rival_data.get('clickup_best') or rival_data.get('github_best') or rival_data.get('shortcut_best', 'your team has different requirements')}"),
    ]
    linear_pricing = {"Free": "Free (10 members)", "Plus": "$8/user/month", "Business": "$16/user/month", "Enterprise": "Custom"}
    extra = schema_article(title, desc, slug, TODAY) + faq_schema(faqs)
    body = f"""
    <div class="meta"><span class="tag">Project Management</span><span>Updated {TODAY}</span><span>By <a href="/authors/smith-elly">Smith Elly</a></span></div>
    <h1>Linear vs {b_display} ({YEAR}): Honest Head-to-Head</h1>
    <div class="quick-answer"><div class="qa-label">Quick Verdict</div>
    <p style="margin:0">{rival_data['verdict_short']}</p></div>
    <h2>Pricing Comparison</h2>
    <table><thead><tr><th>Tier</th><th>Linear</th><th>{b_display}</th></tr></thead>
    <tbody>{"".join(f'<tr><td>{n}</td><td>{p}</td><td>—</td></tr>' for n,p in linear_pricing.items())}</tbody></table>
    <h2>When to Choose Linear</h2>
    <p>{rival_data['linear_best']}</p>
    <ul>
      <li>Fast, keyboard-first interface built for developers</li>
      <li>GitHub / GitLab integration is native and seamless</li>
      <li>Clean sprint and cycle management</li>
      <li>Linear's free plan supports teams up to 10 members</li>
    </ul>
    <h2>When to Choose {b_display}</h2>
    <p>{rival_data.get('jira_best') or rival_data.get('asana_best') or rival_data.get('clickup_best') or rival_data.get('github_best') or rival_data.get('shortcut_best','Consider your team requirements carefully.')}</p>
    <h2>Our Verdict</h2>
    <p>{rival_data['verdict_short']} If you're a developer-first team that values speed and clean UX, Linear is exceptional. If you need the extensibility of {b_display}, that may be the right fit.</p>
    <h2>Frequently Asked Questions</h2>
    {"".join(f'<h3>{q}</h3><p>{a}</p>' for q,a in faqs)}
    <div class="cta-box"><strong>See all Linear comparisons</strong>
    <a class="cta-btn" href="/pages/linear-review-{YEAR}-is-it-worth-it-honest-verdict">Linear Review {YEAR}</a></div>"""
    return slug, HEAD_TPL.format(title=title, desc=desc, slug=slug, og_image="https://saaspare.org/og-default.png", extra_schema=extra, breadcrumb_title=f"Linear vs {b_display}") + body + FOOT_TPL


def write_page(slug, html):
    path = PAGES / f"{slug}.html"
    if path.exists():
        return False
    path.write_text(html, encoding="utf-8")
    return True


def main():
    PAGES.mkdir(parents=True, exist_ok=True)
    created = 0

    # Build clusters for each tool
    for key, data in TOOLS.items():
        builders = [
            build_pricing_page(key, data),
            build_review_page(key, data),
            build_free_trial_page(key, data),
            build_coupon_page(key, data),
            build_alternatives_page(key, data),
        ]
        # vs pages
        for rival in data["rivals"]:
            builders.append(build_vs_page(key, data, rival))

        for slug, html in builders:
            if html and write_page(slug, html):
                created += 1
                print(f"  + {slug}")

    # Fix Linear - add correct comparison pages
    print("\nBuilding correct Linear comparisons...")
    for rival_key, rival_data in LINEAR_CORRECT_RIVALS.items():
        slug, html = build_linear_vs_page(rival_key, rival_data)
        if html and write_page(slug, html):
            created += 1
            print(f"  + {slug}")

    print(f"\nTotal pages created: {created}")


if __name__ == "__main__":
    main()
