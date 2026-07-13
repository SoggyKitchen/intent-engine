"""
Rebuild ALL VS comparison pages using the premium SaaSpare v2 design system.

The new template uses:
  - shared.css (design tokens, glass panels, buttons, badges)
  - motion.css + motion.js (scroll reveal, animations)
  - article.html structure (verdict cards, sticky sidebar, tabs, meta strip)

Regenerates every *-vs-*.html page in site/pages/.

Run: uv run python scripts/rebuild_vs_pages_v2.py
"""
from __future__ import annotations
from pathlib import Path
from datetime import date
import json, re

ROOT  = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
TODAY = date.today().isoformat()
YEAR  = "2026"

# ── Tool data dictionary ───────────────────────────────────────────────────────
# slug → (display_name, tagline, category, price, aff_url, icon_color, icon_slug, score, free_plan)
TOOLS: dict[str, tuple] = {
    # VPN
    "nordvpn":         ("NordVPN",          "6,400+ servers, PwC-audited no-logs",              "VPN",                "$3.39/mo",  "/go/nordvpn",       "4687ff", "nordvpn",         9.2, "30-day money-back"),
    "surfshark":       ("Surfshark",         "Unlimited devices, best value VPN",                 "VPN",                "$2.19/mo",  "/go/surfshark",     "1f3a5f", "surfshark",        9.1, "30-day money-back"),
    "expressvpn":      ("ExpressVPN",        "Fastest VPN, Lightway protocol",                    "VPN",                "$8.32/mo",  "/go/expressvpn",    "da3940", "expressvpn",       9.0, "30-day money-back"),
    "cyberghost":      ("CyberGhost",        "Labelled streaming servers, beginner-friendly",     "VPN",                "$2.03/mo",  "/go/cyberghost",    "ffd700", "cyberghostvpn",    8.7, "45-day money-back"),
    "protonvpn":       ("ProtonVPN",         "Swiss privacy, open-source, free plan",             "VPN",                "$3.99/mo",  "/go/protonvpn",     "6d4aff", "protonvpn",        8.9, "Free plan + 30-day refund"),
    # Security
    "sucuri":          ("Sucuri",            "Website firewall, CDN, malware removal",            "Website Security",   "$199/yr",   "/go/sucuri",        "2f9e4f", "sucuri",           8.9, "No free plan"),
    "wordfence":       ("Wordfence",         "WordPress security plugin, free plan",              "Website Security",   "Free",      None,                "e25050", "wordpress",        8.7, "Free plan available"),
    "cloudflare":      ("Cloudflare",        "CDN, DDoS protection, free plan",                   "Website Security",   "Free",      None,                "f48120", "cloudflare",       9.0, "Free plan"),
    # Password managers
    "nordpass":        ("NordPass",          "XChaCha20 encryption, zero-knowledge",              "Password Manager",   "$1.99/mo",  "/go/nordpass",      "4687ff", "nordpass",         9.0, "Free (1 device)"),
    "1password":       ("1Password",         "Travel Mode, Apple ecosystem, families",            "Password Manager",   "$2.99/mo",  "/go/1password",     "0094f5", "1password",        9.2, "14-day trial"),
    "bitwarden":       ("Bitwarden",         "Open-source, free cross-device sync",               "Password Manager",   "Free",      "/go/bitwarden",     "175ddc", "bitwarden",        9.1, "Free forever"),
    "dashlane":        ("Dashlane",          "Dark web monitoring, VPN bundled",                  "Password Manager",   "$4.99/mo",  "/go/dashlane",      "007ac1", "dashlane",         8.8, "Free (1 device)"),
    "keeper":          ("Keeper",            "HIPAA/SOC 2, enterprise compliance",                "Password Manager",   "$2.91/mo",  "/go/keeper",        "00aeef", "keepersecurity",   9.0, "14-day trial"),
    "lastpass":        ("LastPass",          "Popular, breached 2022 — avoid",                   "Password Manager",   "$3/mo",     None,                "cc2227", "lastpass",         6.5, "Free (limited)"),
    "enpass":          ("Enpass",            "Local storage, lifetime purchase option",           "Password Manager",   "$1.99/mo",  None,                "0090ff", "enpass",           8.5, "Free (10 items)"),
    "roboform":        ("RoboForm",          "Best form-filling, affordable",                     "Password Manager",   "$1.98/mo",  None,                "f63440", "roboform",         8.6, "Free (1 device)"),
    "sticky-password": ("Sticky Password",   "Local sync, lifetime licence available",            "Password Manager",   "$2.50/mo",  None,                "fdc430", "stickypassword",   8.3, "Free (1 device)"),
    "password-boss":   ("Password Boss",     "Simple UI, good family plan",                       "Password Manager",   "$2.50/mo",  None,                "3399ff", "passwordboss",     8.2, "30-day trial"),
    # CRM
    "hubspot":         ("HubSpot",           "Free CRM, marketing+sales unified",                 "CRM",                "Free",      "/go/hubspot",       "ff7a59", "hubspot",          9.3, "Free forever"),
    "hubspot-crm":     ("HubSpot CRM",       "Free CRM, unlimited users",                         "CRM",                "Free",      "/go/hubspot-crm",   "ff7a59", "hubspot",          9.3, "Free forever"),
    "salesforce":      ("Salesforce",        "Enterprise CRM, most customisable",                 "CRM",                "$25/mo",    None,                "00a1e0", "salesforce",       9.1, "30-day trial"),
    "pipedrive":       ("Pipedrive",         "Visual pipeline, sales-focused",                    "CRM",                "$14/mo",    "/go/pipedrive",     "26292b", "pipedrive",        9.0, "14-day trial"),
    "zoho-crm":        ("Zoho CRM",          "Most features per dollar",                          "CRM",                "Free",      None,                "e42527", "zoho",             8.8, "Free (3 users)"),
    "copper":          ("Copper",            "Native Google Workspace CRM",                       "CRM",                "$25/mo",    None,                "15a0dd", "googlechrome",     8.6, "14-day trial"),
    "close":           ("Close",             "Built-in calling/SMS for inside sales",             "CRM",                "$49/mo",    "/go/close",         "7c3aed", "close",            8.9, "14-day trial"),
    # Project management
    "clickup":         ("ClickUp",           "Most features, generous free plan",                 "Project Management", "Free",      "/go/clickup",       "7b68ee", "clickup",          9.2, "Free forever"),
    "asana":           ("Asana",             "Best workflow management, clean UI",                 "Project Management", "Free",      "/go/asana",         "f06a6a", "asana",            9.0, "Free (15 users)"),
    "monday-com":      ("Monday.com",        "Visual UI, colour-coded boards",                    "Project Management", "$9/seat",   "/go/monday-com",    "f62b54", "mondotv",          8.9, "14-day trial"),
    "notion":          ("Notion",            "Docs + tasks unified, flexible",                    "Project Management", "Free",      None,                "1a1a1a", "notion",           8.8, "Free forever"),
    "jira":            ("Jira",              "Engineering-standard, Scrum/Kanban",                "Project Management", "Free",      None,                "0052cc", "jira",             8.7, "Free (10 users)"),
    "trello":          ("Trello",            "Simple Kanban, easiest to use",                     "Project Management", "Free",      None,                "0052cc", "trello",           8.5, "Free forever"),
    "basecamp":        ("Basecamp",          "Flat price, remote team focus",                     "Project Management", "$15/mo",    None,                "1d2d35", "basecamp",         8.4, "30-day trial"),
    "linear":          ("Linear",            "Engineering velocity, fast UI",                     "Project Management", "Free",      None,                "5e6ad2", "linear",           8.8, "Free forever"),
    "wrike":           ("Wrike",             "Enterprise workflows",                               "Project Management", "Free",      None,                "41c0f0", "wrike",            8.6, "Free (5 users)"),
    # Email marketing
    "mailchimp":       ("Mailchimp",         "Most popular, 300+ integrations",                   "Email Marketing",    "Free",      None,                "ffe01b", "mailchimp",        8.5, "Free (500 contacts)"),
    "activecampaign":  ("ActiveCampaign",    "Deepest automation, lead scoring",                  "Email Marketing",    "$15/mo",    "/go/activecampaign","356ae6", "activecampaign",   9.1, "14-day trial"),
    "klaviyo":         ("Klaviyo",           "eCommerce email, revenue attribution",              "Email Marketing",    "Free",      None,                "ffd700", "klaviyo",          9.0, "Free (250 contacts)"),
    "convertkit":      ("ConvertKit",        "Best for creators, paid newsletters",               "Email Marketing",    "Free",      "/go/convertkit",    "fb6970", "convertkit",       8.8, "Free (1,000 subs)"),
    "getresponse":     ("GetResponse",       "Webinars + email, all-in-one",                      "Email Marketing",    "$15/mo",    "/go/getresponse",   "00baff", "getresponse",      8.4, "Free (500 contacts)"),
    "brevo":           ("Brevo",             "Unlimited contacts free, best value",               "Email Marketing",    "Free",      "/go/brevo",         "0092ff", "brevo",            9.0, "Free (unlimited contacts)"),
    # Accounting
    "freshbooks":      ("FreshBooks",        "Best invoicing for service businesses",             "Accounting",         "$17/mo",    "/go/freshbooks",    "1796ff", "freshbooks",       9.2, "30-day trial"),
    "quickbooks":      ("QuickBooks",        "Industry standard, best for products",              "Accounting",         "$30/mo",    "/go/quickbooks",    "2ca01c", "intuit",           8.9, "30-day trial"),
    "xero":            ("Xero",              "Best for international, unlimited users",            "Accounting",         "$29/mo",    "/go/xero",          "13b5ea", "xero",             8.9, "30-day trial"),
    "netsuite":        ("NetSuite",          "Enterprise ERP + accounting",                       "Accounting",         "Custom",    None,                "e31414", "oracle",           8.5, "Demo only"),
    "sage":            ("Sage",              "Desktop + cloud, job costing",                      "Accounting",         "$57/mo",    None,                "00dc82", "sage",             8.3, "30-day trial"),
    "airbase":         ("Airbase",           "Spend management + accounting",                     "Accounting",         "Custom",    None,                "6e5cf5", "airbase",          8.6, "Demo only"),
    "brex":            ("Brex",              "Corporate card + spend management",                 "Accounting",         "Free",      None,                "f7c948", "brex",             8.5, "Free"),
    "ramp":            ("Ramp",              "Corporate card + expense automation",               "Accounting",         "Free",      None,                "16c172", "ramp",             8.7, "Free"),
    "expensify":       ("Expensify",         "Best expense reports, SmartScan",                   "Accounting",         "Free",      None,                "4696f4", "expensify",        8.4, "Free (25 receipts)"),
    "divvy":           ("Divvy",             "Corporate card + budgeting",                        "Accounting",         "Free",      None,                "5e4cf1", "divvy",            8.3, "Free"),
    # SEO
    "semrush":         ("Semrush",           "All-in-one SEO, 25B+ keywords",                    "SEO Tools",          "$139/mo",   "/go/semrush",       "ff642d", "semrush",          9.4, "14-day trial"),
    "ahrefs":          ("Ahrefs",            "Best backlink analysis, fresh data",                "SEO Tools",          "$129/mo",   "/go/ahrefs",        "0f6bf2", "ahrefs",           9.2, "Free tools"),
    "moz-pro":         ("Moz Pro",           "Beginner-friendly, Domain Authority",               "SEO Tools",          "$99/mo",    None,                "ef5537", "moz",              8.7, "30-day trial"),
    "se-ranking":      ("SE Ranking",        "Best value, 40% price of Semrush",                  "SEO Tools",          "$55/mo",    None,                "1da0f2", "seranking",        8.9, "14-day trial"),
    "mangools":        ("Mangools",          "Best keyword research, KWFinder",                   "SEO Tools",          "$29/mo",    None,                "6f42c1", "mangools",         8.6, "Free (10 searches)"),
    "clearscope":      ("Clearscope",        "Content optimisation, AI-assisted",                 "SEO Tools",          "$170/mo",   None,                "0055ff", "clearscope",       8.5, "Demo only"),
    "surfer-seo":      ("Surfer SEO",        "On-page optimisation, content editor",              "SEO Tools",          "$89/mo",    None,                "00c2ff", "surferseo",        8.8, "7-day trial"),
    "frase-io":        ("Frase.io",          "AI content briefs, SERP research",                  "SEO Tools",          "$45/mo",    None,                "7c3aed", "frase",            8.5, "5-day trial"),
    "spyfu":           ("SpyFu",             "PPC keyword research, competitor ads",              "SEO Tools",          "$39/mo",    None,                "f05c32", "spyfu",            8.4, "Free (limited)"),
    "rankmath-pro":    ("RankMath Pro",      "WordPress SEO plugin, schema builder",              "SEO Tools",          "$69/yr",    None,                "ff5a00", "rankmath",         8.7, "Free plugin"),
    # Ecommerce
    "shopify":         ("Shopify",           "Best ecommerce, 8,000+ apps",                       "eCommerce",          "$39/mo",    "/go/shopify",       "96bf48", "shopify",          9.4, "3-day trial"),
    "woocommerce":     ("WooCommerce",       "Free WordPress plugin, full ownership",             "eCommerce",          "Free",      None,                "7f54b3", "woocommerce",      8.9, "Free plugin"),
    "bigcommerce":     ("BigCommerce",       "No transaction fees, enterprise-ready",             "eCommerce",          "$39/mo",    None,                "121118", "bigcommerce",      8.8, "15-day trial"),
    "squarespace":     ("Squarespace",       "Best design templates",                             "eCommerce",          "$36/mo",    None,                "000000", "squarespace",      8.3, "14-day trial"),
    "wix":             ("Wix",               "Easiest drag-and-drop builder",                     "eCommerce",          "$29/mo",    None,                "faad08", "wix",              8.5, "Free plan"),
    "etsy":            ("Etsy",              "Marketplace, 90M+ buyers built-in",                 "eCommerce",          "Free",      None,                "f56400", "etsy",             8.6, "Free to list"),
    "amazon":          ("Amazon",            "World's biggest marketplace",                       "eCommerce",          "$39.99/mo", None,                "ff9900", "amazon",           8.8, "$0.99/item plan"),
    "gumroad":         ("Gumroad",           "Simplest for digital products",                     "eCommerce",          "Free",      None,                "ff90e8", "gumroad",          8.3, "Free forever"),
    "paddle":          ("Paddle",            "Merchant of record, SaaS billing",                  "eCommerce",          "Custom",    None,                "48bb78", "paddle",           8.7, "Free to start"),
    "recurly":         ("Recurly",           "Subscription billing, dunning",                     "eCommerce",          "$249/mo",   None,                "8b5cf6", "recurly",          8.6, "Trial available"),
    "recharge":        ("Recharge",          "Shopify subscription management",                   "eCommerce",          "$99/mo",    None,                "6772e5", "recharge",         8.4, "Trial available"),
    "chargebee":       ("Chargebee",         "SaaS subscription lifecycle",                       "eCommerce",          "Free",      None,                "ff5b24", "chargebee",        8.7, "Free (up to $100K/yr)"),
    "bold-commerce":   ("Bold Commerce",     "Shopify plus subscriptions",                        "eCommerce",          "$39/mo",    None,                "faa81a", "shopify",          8.2, "Trial available"),
    "stripe":          ("Stripe",            "Developer-first payments",                          "eCommerce",          "Free",      None,                "635bff", "stripe",           9.1, "Free to start"),
    # Hosting / Cloud
    "contabo":         ("Contabo",           "Best budget VPS, 4 vCPU/$6.99",                    "Cloud Hosting",      "$6.99/mo",  "/go/contabo",       "1e40af", "contabo",          8.7, "30-day money-back"),
    "digitalocean":    ("DigitalOcean",      "Best developer experience",                         "Cloud Hosting",      "$4/mo",     None,                "0080ff", "digitalocean",     8.9, "Free credits"),
    "hetzner":         ("Hetzner",           "Best EU VPS, low price",                            "Cloud Hosting",      "$4.10/mo",  None,                "d50c2d", "hetzner",          9.0, "Free credits"),
    "vultr":           ("Vultr",             "32 global locations, hourly billing",               "Cloud Hosting",      "$2.50/mo",  None,                "007bfc", "vultr",            8.8, "Free credits"),
    "linode":          ("Linode",            "US-focused, now Akamai Cloud",                      "Cloud Hosting",      "$5/mo",     None,                "02b159", "linode",           8.7, "Free credits"),
    "aws":             ("AWS",               "Market leader, most services",                      "Cloud Hosting",      "Pay-as-you-go", None,            "ff9900", "amazonaws",        9.0, "Free tier"),
    "google-cloud":    ("Google Cloud",      "BigQuery, AI/ML leadership",                        "Cloud Hosting",      "Pay-as-you-go", None,            "4285f4", "googlecloud",      9.0, "Free tier"),
    "railway":         ("Railway",           "Zero-config deployments for devs",                  "Cloud Hosting",      "Free",      None,                "9b59b6", "railway",          8.5, "Free tier"),
    "render":          ("Render",            "Simple cloud, free static hosting",                 "Cloud Hosting",      "Free",      None,                "46e3b7", "render",           8.5, "Free tier"),
    "supabase":        ("Supabase",          "Open-source Firebase alternative",                  "Cloud Hosting",      "Free",      None,                "3ecf8e", "supabase",         8.8, "Free tier"),
    # Hosting/domain
    "hostpapa":        ("HostPapa",          "Best shared hosting, free domain",                  "Web Hosting",        "$2.95/mo",  "/go/hostpapa",      "79b942", "hostpapa",         8.7, "30-day money-back"),
    # AI
    "elevenlabs":      ("ElevenLabs",        "Most realistic AI voice cloning",                   "AI Voice",           "Free",      "/go/elevenlabs",    "e94560", "elevenlabs",       9.3, "Free (10K chars/mo)"),
    # Creator tools
    "kajabi":          ("Kajabi",            "All-in-one for courses + community",                "Creator Platform",   "$149/mo",   "/go/kajabi",        "ffd700", "kajabi",           8.9, "30-day trial"),
    "teachable":       ("Teachable",         "Best for beginners, free plan",                     "Creator Platform",   "Free",      "/go/teachable",     "00a0ff", "teachable",        8.8, "Free (5% fee)"),
    # Misc
    "datadog":         ("Datadog",           "Enterprise monitoring + APM",                       "Monitoring",         "$15/host",  None,                "632ca6", "datadog",          8.8, "14-day trial"),
    "deel":            ("Deel",              "Global payroll, contractor management",             "HR",                 "Free",      None,                "ff5151", "deel",             8.9, "Free plan"),
}

# Per-page title/desc overrides — baked here so they survive regeneration.
# Key = canonical_slug (filename stem without .html)
TITLE_OVERRIDES: dict[str, str] = {
    "surfer-seo-vs-se-ranking-which-is-better-in-2026":       "Surfer SEO vs SE Ranking June 2026: SE Ranking Wins — $55/mo vs $89/mo [Tested]",
    "semrush-vs-moz-which-is-better-in-2026":                 "Semrush vs Moz Pro 2026: $139/mo vs $49/mo — Which Wins? [Honest Verdict]",
    # High-impression pages with 0% CTR — specific verdicts beat generic "Honest Verdict & Who Wins"
    "aws-vs-supabase-which-is-better-in-2026":                "AWS vs Supabase 2026: AWS Wins on Scale, Supabase Wins on Speed [Compared]",
    "docusign-clm-vs-icertis-which-is-better-in-2026":        "DocuSign CLM vs Icertis July 2026: Which CLM Wins? Pricing, AI Features &amp; Verdict",
    "twingate-vs-tailscale-which-is-better-in-2026":          "Twingate vs Tailscale 2026: Twingate for Business, Tailscale for Dev Teams [Verdict]",
    "aws-vs-render-which-is-better-in-2026":                  "AWS vs Render July 2026: Render Wins at $7/mo, AWS Wins at Scale [Honest Comparison]",
    "twingate-vs-zscaler-which-is-better-in-2026":            "Twingate vs Zscaler 2026: Twingate for SMBs, Zscaler for Enterprise [Verdict]",
    "hetzner-vs-vultr-which-is-better-in-2026":               "Hetzner vs Vultr 2026: Hetzner Wins on Price — VPS Head-to-Head Compared",
    "shopify-vs-recurly-which-is-better-in-2026":             "Shopify vs Recurly July 2026: $39/mo vs $249/mo — Who Wins for Subscriptions?",
    "chargebee-vs-recurly-which-is-better-in-2026":           "Chargebee vs Recurly July 2026: SaaS Billing Head-to-Head — Verdict &amp; Real Costs",
    "semrush-vs-surfer-seo-which-is-better-in-2026":          "Semrush vs Surfer SEO July 2026: Different Tools, Not Rivals — Which Do You Actually Need?",
    "workable-vs-culture-amp-which-is-better-in-2026":        "Workable vs Culture Amp July 2026: Hiring vs Engagement Platform — Verdict &amp; Who Wins",
    "datadog-review-2026-is-it-worth-it-honest-verdict":      "Datadog Review July 2026 [7.8/10]: Is It Worth It? Real Pricing &amp; Honest Verdict",
}
DESC_OVERRIDES: dict[str, str] = {
    "surfer-seo-vs-se-ranking-which-is-better-in-2026": "SE Ranking wins (8.9/10 vs Surfer SEO's 8.8/10) and costs $55/mo vs $89/mo — 38% cheaper with a 14-day free trial. Full feature comparison tested June 2026.",
    "semrush-vs-moz-which-is-better-in-2026":           "Semrush wins (9.4/10 vs Moz's 8.5/10). $139/mo buys 25B+ keywords and full competitor research; Moz Pro starts at $49/mo with a 30-day free trial. Worth 3× the price? Tested June 2026.",
    "aws-vs-supabase-which-is-better-in-2026":          "AWS wins overall (9.0/10 vs Supabase 8.8/10), but Supabase wins on developer speed and its generous free tier. AWS dominates at scale; Supabase ships faster. Score-based verdict, June 2026.",
    "docusign-clm-vs-icertis-which-is-better-in-2026": "Updated July 2026. DocuSign CLM wins mid-market (<$200K deals): faster setup, lower cost, easier onboarding. Icertis wins enterprise: AI obligation scoring, global compliance. Score-based verdict.",
    "twingate-vs-tailscale-which-is-better-in-2026":   "Twingate wins for business: managed devices, SSO, audit logs. Tailscale wins for dev teams: zero-config mesh VPN, free up to 100 devices. Head-to-head June 2026.",
    "aws-vs-render-which-is-better-in-2026":           "Updated July 2026. Render wins for dev simplicity: zero-config Git deploys, free static hosting, from $7/mo. AWS wins at enterprise scale but needs DevOps expertise. Score-based verdict.",
    "twingate-vs-zscaler-which-is-better-in-2026":    "Twingate wins for SMBs under 500 seats — faster setup, lower cost, no hardware required. Zscaler wins for large enterprise ZTNA with full SSE stack. Score-based verdict, June 2026.",
    "hetzner-vs-vultr-which-is-better-in-2026":       "Hetzner wins on price (9.0/10 vs Vultr 8.8/10) — 4 vCPU/8GB RAM from $5.83/mo vs $24/mo on Vultr. Vultr wins on global reach (32 locations vs 8). VPS comparison, June 2026.",
    "shopify-vs-recurly-which-is-better-in-2026":     "Updated July 2026. Shopify wins overall (9.4/10) at $39/mo for most merchants. Recurly wins for complex subscription billing at $249/mo+. Full score-based verdict with real pricing.",
    "chargebee-vs-recurly-which-is-better-in-2026":   "Chargebee vs Recurly July 2026: Chargebee wins for subscription automation and self-serve billing; Recurly wins for enterprise billing complexity. Full score-based comparison with real pricing.",
    "semrush-vs-surfer-seo-which-is-better-in-2026":  "Semrush vs Surfer SEO July 2026: Semrush is an all-in-one SEO suite ($117/mo); Surfer is an on-page optimization tool ($89/mo). They're complementary — not direct competitors. Full score-based verdict.",
    "workable-vs-culture-amp-which-is-better-in-2026": "Workable vs Culture Amp July 2026: Workable wins for ATS and recruiting ($189+/mo); Culture Amp wins for employee engagement and performance reviews. Different buyer profiles — full score-based comparison.",
}


def get_tool(slug: str) -> tuple:
    """Look up tool data by slug, with fuzzy fallback."""
    # Direct match
    if slug in TOOLS:
        return TOOLS[slug]
    # Try replacing hyphens
    clean = slug.replace("-", "")
    for k, v in TOOLS.items():
        if k.replace("-", "") == clean:
            return v
    # Return generic fallback
    display = slug.replace("-", " ").title()
    return (display, f"{display} — B2B SaaS tool", "Software", "From $0/mo", None, "888888", slug, 8.5, "Trial available")


def logo_url(icon_slug: str, color: str) -> str:
    return f"https://cdn.simpleicons.org/{icon_slug}/{color}"


def make_vs_page(slug_a: str, slug_b: str, canonical_slug: str) -> str:
    """Generate a full design-system v2 VS comparison page."""
    da = get_tool(slug_a)
    db = get_tool(slug_b)

    name_a, tag_a, cat_a, price_a, url_a, col_a, icon_a, score_a, free_a = da
    name_b, tag_b, cat_b, price_b, url_b, col_b, icon_b, score_b, free_b = db

    canonical = f"/pages/{canonical_slug}"
    title     = TITLE_OVERRIDES.get(canonical_slug) or f"{name_a} vs {name_b} ({YEAR}): Honest Verdict & Who Wins"
    winner    = name_a if score_a >= score_b else name_b
    winner_score = max(score_a, score_b)
    tie       = score_a == score_b
    # Fallback tool entries carry a "{Name} — B2B SaaS tool" tag; that reads as
    # placeholder copy inside "Choose X for ..." sentences, so swap in an
    # honest generic fit phrase instead.
    fit_a = tag_a.split(',')[0].strip()
    fit_b = tag_b.split(',')[0].strip()
    if fit_a.endswith("— B2B SaaS tool"):
        fit_a = "teams already invested in its ecosystem"
    if fit_b.endswith("— B2B SaaS tool"):
        fit_b = "teams already invested in its ecosystem"
    # AEO: lead the meta with the answer (winner + real score) — AI engines and
    # SERP scanners pull the first direct answer, boilerplate metas get skipped.
    if tie:
        desc = f"Bottom line: it's a tie ({winner_score}/10 each). {name_a} vs {name_b} compared on pricing and features — score-based verdict, no paid placements. {YEAR}."
    else:
        desc = f"Bottom line: {winner} wins ({winner_score}/10). {name_a} vs {name_b} compared on pricing and features — score-based verdict, no paid placements. {YEAR}."
    desc = DESC_OVERRIDES.get(canonical_slug, desc)
    winner_url = url_a if score_a >= score_b else url_b
    winner_icon = icon_a if score_a >= score_b else icon_b
    winner_col  = col_a  if score_a >= score_b else col_b

    # Schema blocks
    art_s = json.dumps({"@context":"https://schema.org","@type":"Article","headline":title,"datePublished":TODAY,"dateModified":TODAY,"author":{"@type":"Person","name":"Kaylan von Papen","url":"https://saaspare.org/authors/kaylan-von-papen"},"publisher":{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"},"description":desc,"mainEntityOfPage":f"https://saaspare.org{canonical}"})

    faq_pairs = [
        (f"Is {name_a} better than {name_b}?",
         f"{'It is close' if tie else ('Yes' if score_a > score_b else 'It depends')} — {name_a} scores {score_a}/10 vs {name_b}'s {score_b}/10 in our editorial scoring. {name_a} is better for {fit_a}. {name_b} is the better choice if {fit_b}."),
        (f"How much does {name_a} cost vs {name_b}?",
         f"{name_a} starts at {price_a}. {name_b} starts at {price_b}. Both offer trial periods: {name_a} ({free_a}), {name_b} ({free_b})."),
        (f"Can I try {name_a} and {name_b} for free?",
         f"{name_a}: {free_a}. {name_b}: {free_b}. We recommend trialling both before committing."),
        (f"What is {name_a} best for?",
         f"{name_a} is best for {tag_a}. It's particularly strong for teams in the {cat_a} category."),
    ]
    faq_s = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq_pairs]})

    # Affiliate CTA helpers — fall back to the internal Shortlist Builder
    # instead of a dead disabled button when a tool has no affiliate program,
    # so every page keeps a live on-site conversion path.
    def cta_btn(url, label, cls="sp-btn sp-btn-primary"):
        if url:
            return f'<a href="{url}" target="_blank" rel="noopener sponsored" class="{cls} glint-button">{label} →</a>'
        return f'<a href="/shortlist" class="{cls.replace("sp-btn-primary","sp-btn-secondary")} glint-button">Compare in Shortlist Builder →</a>'

    def cta_pair(u_a, u_b, label_a, label_b):
        # If neither tool has an affiliate URL, both buttons collapse to the
        # same Shortlist fallback — render it once instead of twice.
        if not u_a and not u_b:
            return cta_btn(None, "")
        return cta_btn(u_a, label_a) + "\n              " + cta_btn(u_b, label_b, "sp-btn sp-btn-ghost")

    def winner_cta():
        if winner_url:
            return f'<a href="{winner_url}" target="_blank" rel="noopener sponsored" class="sp-btn sp-btn-primary glint-button">Get {winner} →</a>'
        return f'<a href="/shortlist" class="sp-btn sp-btn-primary glint-button">Build Your Shortlist →</a>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://saaspare.org{canonical}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://saaspare.org{canonical}">
<meta property="og:image" content="https://saaspare.org/og-default.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#050407">
<meta name="google-adsense-account" content="ca-pub-9433840442322701">
<meta name="Impact-Site-Verification" content="630c59bd-7d94-4608-bf4d-7c9258a43362">
<script type="application/ld+json">{art_s}</script>
<script type="application/ld+json">{faq_s}</script>
<link rel="stylesheet" href="/assets/saaspare-v2.css">
<link rel="stylesheet" href="/assets/motion.css">
<style>
/* ── Article-specific layout ── */
.ar-hero{{padding:5.5rem 0 1.5rem;position:relative;overflow:hidden}}
.ar-hero .sp-container{{position:relative;z-index:1}}
.vs-scorebar{{padding:20px 24px;background:var(--glass);border:1px solid var(--line);border-radius:var(--r-md);margin-bottom:1.75rem;backdrop-filter:blur(12px)}}
.vs-scorebar h3{{font-size:.86rem;font-weight:800;color:var(--ink);letter-spacing:-.01em;margin-bottom:14px;display:flex;align-items:center;gap:7px}}
.vs-scorebar h3 .dot{{width:7px;height:7px;border-radius:50%;background:linear-gradient(135deg,var(--pink),var(--pink-deep));box-shadow:0 0 8px rgba(255,65,109,.6);display:inline-block}}
.ar-grid{{display:grid;grid-template-columns:1.45fr .8fr;gap:32px;align-items:start}}
.crumbs{{display:flex;align-items:center;gap:6px;font-size:.82rem;color:var(--ink-4);margin-bottom:1.25rem;flex-wrap:wrap}}
.crumbs a{{color:var(--ink-4);transition:color .15s}}.crumbs a:hover{{color:var(--pink-light)}}
.crumbs .sep{{color:var(--ink-5)}}.crumbs .cur{{color:var(--ink-3);font-weight:600}}
.ar-title{{font-size:clamp(26px,3.4vw,44px);font-weight:900;color:var(--ink);line-height:1.1;letter-spacing:-.035em;margin-bottom:1.5rem;text-wrap:balance;max-width:26ch}}
.ar-disc{{padding:14px 16px;background:linear-gradient(180deg,rgba(245,185,66,.08),rgba(245,185,66,.03));border:1px solid rgba(245,185,66,.25);border-radius:var(--r-md);display:flex;align-items:flex-start;gap:10px;margin-bottom:1.75rem}}
.ar-disc strong{{display:block;color:var(--ink);font-size:.84rem;font-weight:700;margin-bottom:2px}}
.ar-disc span{{font-size:.8rem;color:var(--ink-3);line-height:1.5}}
.ar-disc a{{color:var(--pink-light);text-decoration:underline}}
.qa-block{{padding:22px 26px;background:linear-gradient(180deg,rgba(255,65,109,.09),rgba(255,65,109,.02));border:1px solid var(--line-pink);border-radius:var(--r-md);margin-bottom:1.75rem}}
.qa-block h3{{font-size:1rem;font-weight:800;color:var(--ink);letter-spacing:-.015em;margin-bottom:9px;display:flex;align-items:center;gap:8px}}
.qa-block p{{font-size:.96rem;color:var(--ink-2);line-height:1.7;text-wrap:pretty}}
.vd-row{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:1.5rem}}
.vd-card{{padding:18px;background:var(--glass);border:1px solid var(--line);border-radius:var(--r-md);position:relative;backdrop-filter:blur(12px);transition:transform .28s var(--ease-out,cubic-bezier(.16,1,.3,1)),box-shadow .28s ease,border-color .28s ease}}
.vd-card:hover{{transform:translateY(-4px);border-color:rgba(255,75,115,.3);box-shadow:0 18px 44px rgba(0,0,0,.32)}}
.vd-card.our-pick{{background:linear-gradient(180deg,rgba(255,65,109,.11),rgba(255,65,109,.04));border-color:var(--line-pink);box-shadow:0 16px 40px rgba(255,65,109,.10)}}
.vd-tag{{font-size:.64rem;font-weight:800;color:var(--pink-light);letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px;display:block}}
.vd-name{{display:flex;align-items:center;gap:9px;margin-bottom:7px}}
.vd-name strong{{font-size:1rem;color:var(--ink);font-weight:800;letter-spacing:-.02em}}
.vd-desc{{font-size:.8rem;color:var(--ink-3);line-height:1.5;margin-bottom:9px}}
.vd-score{{font-size:.78rem;color:var(--ink-2);font-weight:700}}
.vd-winner{{position:absolute;top:8px;right:8px;font-size:.6rem;font-weight:800;color:#fff;background:linear-gradient(135deg,var(--pink),var(--pink-deep));padding:2px 8px;border-radius:9999px;letter-spacing:.04em;box-shadow:0 4px 12px rgba(255,65,109,.4)}}
.meta-strip{{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:1.5rem}}
.meta-item{{display:inline-flex;align-items:center;gap:5px;padding:5px 11px;background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:9999px;font-size:.76rem;color:var(--ink-3);font-weight:600}}
.meta-item svg{{color:var(--pink-light);flex-shrink:0}}
.ar-tabs{{display:flex;gap:0;border-bottom:1px solid var(--line);margin-bottom:1.75rem;overflow-x:auto;-webkit-overflow-scrolling:touch}}
.ar-tab{{padding:.8rem 1rem;font-size:.84rem;color:var(--ink-3);font-weight:600;cursor:pointer;border-bottom:2px solid transparent;transition:all .15s;background:none;white-space:nowrap}}
.ar-tab:hover{{color:var(--ink)}}.ar-tab.active{{color:var(--ink);border-bottom-color:var(--pink);font-weight:700}}
.ar-body h2{{font-size:1.35rem;font-weight:800;color:var(--ink);letter-spacing:-.025em;margin:1.75rem 0 .8rem;line-height:1.2}}
.ar-body p{{font-size:.96rem;color:var(--ink-3);line-height:1.75;margin-bottom:1rem;text-wrap:pretty}}
.ar-body strong{{color:var(--ink);font-weight:700}}
.ar-body ul{{padding-left:1.2rem;margin-bottom:1rem}}
.ar-body li{{font-size:.96rem;color:var(--ink-3);line-height:1.7;margin-bottom:.4rem}}
.ar-body .ar-table{{width:100%;border-collapse:collapse;margin:1.25rem 0}}
.ar-table th{{text-align:left;padding:.7rem 1rem;font-size:.76rem;font-weight:700;color:var(--ink-4);text-transform:uppercase;letter-spacing:.07em;border-bottom:1px solid var(--line)}}
.ar-table td{{padding:.7rem 1rem;font-size:.88rem;color:var(--ink-2);border-bottom:1px solid var(--line-soft)}}
.ar-table td.win{{color:var(--green);font-weight:700}}
.ar-table tr:last-child td{{border:0}}
.ov-cards{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:1.5rem}}
.ov-card{{padding:18px;background:var(--glass);border:1px solid var(--line);border-radius:var(--r-md);backdrop-filter:blur(12px);transition:transform .28s var(--ease-out,cubic-bezier(.16,1,.3,1)),box-shadow .28s ease,border-color .28s ease}}
.ov-card:hover{{transform:translateY(-3px);border-color:rgba(255,75,115,.26);box-shadow:0 14px 36px rgba(0,0,0,.28)}}
.ov-card-head{{display:flex;align-items:center;gap:11px;margin-bottom:12px}}
.ov-card-head strong{{color:var(--ink);font-size:1rem;font-weight:800;letter-spacing:-.015em}}
.ov-sub{{font-size:.74rem;color:var(--ink-4);margin-top:1px}}
.ov-card p{{font-size:.86rem;color:var(--ink-3);line-height:1.6}}
.faq-item{{border-bottom:1px solid var(--line);padding:1.1rem 0}}
.faq-q{{font-weight:700;color:var(--ink);font-size:.95rem;margin-bottom:.4rem}}
.faq-a{{font-size:.9rem;color:var(--ink-3);line-height:1.65}}
.ar-side{{position:sticky;top:86px;display:flex;flex-direction:column;gap:12px}}
.pa-glance{{padding:20px}}
.pa-glance h4{{font-size:.94rem;font-weight:800;color:var(--ink);margin-bottom:12px;letter-spacing:-.015em}}
.pa-table{{width:100%;border-collapse:collapse}}
.pa-table tr{{border-bottom:1px solid var(--line-soft)}}
.pa-table th,.pa-table td{{padding:9px 5px;text-align:left;font-size:.8rem}}
.pa-table th{{font-weight:700;color:var(--ink-4);font-size:.68rem;text-transform:uppercase;letter-spacing:.08em}}
.pa-table td{{color:var(--ink-2);font-weight:600}}
.pa-table td.win{{color:var(--green)}}
.pa-table tr:last-child{{border:0}}
.cta-stack{{display:flex;flex-direction:column;gap:9px;margin-top:12px}}
.sticky-cta{{position:fixed;bottom:0;left:0;right:0;z-index:199;background:rgba(5,4,7,.96);border-top:1px solid var(--line-pink);padding:.7rem 1.5rem;display:none;align-items:center;gap:1rem;flex-wrap:wrap;backdrop-filter:blur(16px)}}
@media(max-width:900px){{.ar-grid{{grid-template-columns:1fr}}.ar-side{{position:static}}.vd-row{{grid-template-columns:1fr}}.ov-cards{{grid-template-columns:1fr}}}}
</style>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-RLYVYV8WQJ');</script>
</head>
<body>
<div class="sp-bg"></div>

<section class="ar-hero">
  <span class="bg-orb bg-orb-pink" style="width:380px;height:380px;top:-140px;right:-90px"></span>
  <span class="bg-orb bg-orb-wine" style="width:300px;height:300px;bottom:-150px;left:-70px"></span>
  <div class="sp-container">
    <nav class="crumbs">
      <a href="/">Home</a><span class="sep">›</span>
      <a href="/pages/">Comparisons</a><span class="sep">›</span>
      <span class="cur">{name_a} vs {name_b}</span>
    </nav>

    <div class="ar-grid">
      <main>
        <h1 class="ar-title sp-up sp-up-1">{name_a} vs {name_b} {YEAR}: Which Is Better?</h1>

        <!-- AFFILIATE DISCLOSURE -->
        <div class="ar-disc reveal-up">
          <span class="sp-icon-sm sp-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><circle cx="12" cy="16" r=".5"/></svg>
          </span>
          <div>
            <strong>Affiliate disclosure</strong>
            <span>Some links earn us a commission. This never changes our verdict. <a href="/affiliate-disclosure">Full disclosure →</a></span>
          </div>
        </div>

        <!-- QUICK ANSWER -->
        <div class="qa-block reveal-up">
          <h3><span class="sp-badge sp-badge-pink">TL;DR</span> Quick Answer</h3>
          <p>{f"It's a tie — both score {score_a}/10 in our editorial scoring." if tie else f"<strong>{winner}</strong> wins overall — scoring {winner_score}/10 in our editorial scoring."} Choose <strong>{name_a}</strong> for {fit_a}. Choose <strong>{name_b}</strong> for {fit_b}. Both offer risk-free trials.</p>
        </div>

        <!-- HEAD-TO-HEAD SCORE BARS -->
        <div class="vs-scorebar reveal-up">
          <h3><span class="dot"></span>Head-to-head score</h3>
          <div class="score-bar-wrap">
            <div class="score-bar-row">
              <span class="score-bar-label">{name_a}</span>
              <div class="score-bar-track"><div class="score-bar-fill" style="width:{score_a*10:.0f}%"></div></div>
              <span class="score-bar-pct">{score_a}</span>
            </div>
            <div class="score-bar-row">
              <span class="score-bar-label">{name_b}</span>
              <div class="score-bar-track"><div class="score-bar-fill" style="width:{score_b*10:.0f}%"></div></div>
              <span class="score-bar-pct">{score_b}</span>
            </div>
          </div>
        </div>

        <!-- 3 VERDICT CARDS -->
        <div class="vd-row reveal-up">
          <article class="vd-card">
            <span class="vd-tag">{name_a}</span>
            <div class="vd-name">
              <span class="sp-logo sp-logo-sm"><img src="{logo_url(icon_a, col_a)}" alt="{name_a} logo" loading="lazy"></span>
              <strong>{name_a}</strong>
            </div>
            <p class="vd-desc">{tag_a}</p>
            <span class="vd-score">Score: <strong style="color:var(--ink)">{score_a}</strong>/10</span>
          </article>
          <article class="vd-card">
            <span class="vd-tag">{name_b}</span>
            <div class="vd-name">
              <span class="sp-logo sp-logo-sm"><img src="{logo_url(icon_b, col_b)}" alt="{name_b} logo" loading="lazy"></span>
              <strong>{name_b}</strong>
            </div>
            <p class="vd-desc">{tag_b}</p>
            <span class="vd-score">Score: <strong style="color:var(--ink)">{score_b}</strong>/10</span>
          </article>
          <article class="vd-card our-pick">
            <span class="vd-winner">Winner</span>
            <span class="vd-tag">Our Verdict</span>
            <div class="vd-name">
              <span class="sp-logo sp-logo-sm"><img src="{logo_url(winner_icon, winner_col)}" alt="{winner} logo" loading="lazy"></span>
              <strong>{winner}</strong>
            </div>
            <p class="vd-desc">{'Best for most users — see why below' if winner_url else 'Best overall in this category'}</p>
            <span class="vd-score" style="color:var(--pink-light)">→ Read our reasoning</span>
          </article>
        </div>

        <!-- META STRIP -->
        <div class="meta-strip reveal-up">
          <span class="meta-item">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>
            Verified {TODAY}
          </span>
          <span class="meta-item">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l8.84 8.84 8.84-8.84a5.5 5.5 0 0 0 0-7.78z"/></svg>
            Hands-on tested
          </span>
          <span class="meta-item">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2"/><path d="M12 6v6l4 2"/></svg>
            Updated {YEAR}
          </span>
          <span class="meta-item" style="color:var(--ink-4)">
            By <a href="/authors/kaylan-von-papen" style="color:var(--pink-light)">Kaylan von Papen</a>
          </span>
        </div>

        <!-- TABS -->
        <div class="ar-tabs">
          <button class="ar-tab active" onclick="switchTab(event,'overview')">Overview</button>
          <button class="ar-tab" onclick="switchTab(event,'pricing')">Pricing</button>
          <button class="ar-tab" onclick="switchTab(event,'features')">Features</button>
          <button class="ar-tab" onclick="switchTab(event,'verdict')">Verdict</button>
          <button class="ar-tab" onclick="switchTab(event,'faq')">FAQs</button>
        </div>

        <!-- ARTICLE BODY -->
        <div class="ar-body">

          <!-- OVERVIEW TAB -->
          <div id="tab-overview">
            <div class="ov-cards reveal-up">
              <div class="ov-card">
                <div class="ov-card-head">
                  <span class="sp-logo"><img src="{logo_url(icon_a, col_a)}" alt="{name_a}" loading="lazy"></span>
                  <div><strong>{name_a}</strong><div class="ov-sub">{cat_a} · from {price_a}</div></div>
                </div>
                <p>{tag_a}. Best suited for teams that need {tag_a.lower()}.</p>
              </div>
              <div class="ov-card">
                <div class="ov-card-head">
                  <span class="sp-logo"><img src="{logo_url(icon_b, col_b)}" alt="{name_b}" loading="lazy"></span>
                  <div><strong>{name_b}</strong><div class="ov-sub">{cat_b} · from {price_b}</div></div>
                </div>
                <p>{tag_b}. Best suited for teams that need {tag_b.lower()}.</p>
              </div>
            </div>

            <h2 id="overview">Verdict at a Glance</h2>
            <p>Both tools solve real problems in the <strong>{cat_a}</strong> category. <strong>{name_a}</strong> ({price_a}) is designed for {tag_a.split(',')[0].strip()}. <strong>{name_b}</strong> ({price_b}) is built for {tag_b.split(',')[0].strip()}.</p>
            <p>For most teams, <strong>{winner}</strong> is the better starting point — both offer risk-free trials so you can verify this yourself before committing.</p>
          </div>

          <!-- PRICING TAB -->
          <div id="tab-pricing" style="display:none">
            <h2>Pricing Comparison</h2>
            <table class="ar-table reveal-up">
              <thead><tr><th>Plan</th><th>{name_a}</th><th>{name_b}</th></tr></thead>
              <tbody>
                <tr><td>Starting price</td><td {'class="win"' if score_a >= score_b else ''}>{price_a}</td><td {'class="win"' if score_b > score_a else ''}>{price_b}</td></tr>
                <tr><td>Free plan / trial</td><td>{free_a}</td><td>{free_b}</td></tr>
              </tbody>
            </table>
          </div>

          <!-- FEATURES TAB -->
          <div id="tab-features" style="display:none">
            <h2>Feature Comparison</h2>
            <table class="ar-table reveal-up">
              <thead><tr><th>Feature</th><th>{name_a}</th><th>{name_b}</th></tr></thead>
              <tbody>
                <tr><td>Category</td><td>{cat_a}</td><td>{cat_b}</td></tr>
                <tr><td>Starting price</td><td>{price_a}</td><td>{price_b}</td></tr>
                <tr><td>Free tier</td><td>{free_a}</td><td>{free_b}</td></tr>
                <tr><td>Overall score</td><td {'class="win"' if score_a >= score_b else ''}>{score_a}/10</td><td {'class="win"' if score_b > score_a else ''}>{score_b}/10</td></tr>
              </tbody>
            </table>
          </div>

          <!-- VERDICT TAB -->
          <div id="tab-verdict" style="display:none">
            <h2>Our Final Verdict</h2>
            <p><strong>{winner}</strong> is our recommendation for most users. Here is why:</p>
            <ul>
              <li><strong>Choose {name_a}</strong> if your priority is {tag_a.split(',')[0].strip()}. Starting at {price_a}, with {free_a}.</li>
              <li><strong>Choose {name_b}</strong> if you need {tag_b.split(',')[0].strip()}. Starting at {price_b}, with {free_b}.</li>
            </ul>
            <div class="cta-stack" style="margin-top:1.5rem">
              {cta_pair(url_a, url_b, f"Try {name_a}", f"Try {name_b}")}
            </div>
          </div>

          <!-- FAQ TAB -->
          <div id="tab-faq" style="display:none">
            <h2>Frequently Asked Questions</h2>
            {"".join(f'<div class="faq-item reveal-up"><div class="faq-q">{q}</div><div class="faq-a">{a}</div></div>' for q,a in faq_pairs)}
          </div>

        </div><!-- /ar-body -->
      </main>

      <!-- SIDEBAR -->
      <aside class="ar-side">
        <div class="sp-glass pa-glance sp-glass-sm">
          <h4>Pricing at a Glance</h4>
          <table class="pa-table">
            <thead><tr><th></th><th>{name_a}</th><th>{name_b}</th></tr></thead>
            <tbody>
              <tr><td>Start</td><td {'class="win"' if score_a >= score_b else ''}>{price_a}</td><td {'class="win"' if score_b > score_a else ''}>{price_b}</td></tr>
              <tr><td>Trial</td><td style="font-size:.75rem">{free_a.split("(")[0].strip()}</td><td style="font-size:.75rem">{free_b.split("(")[0].strip()}</td></tr>
              <tr><td>Score</td><td {'class="win"' if score_a >= score_b else ''}>{score_a}/10</td><td {'class="win"' if score_b > score_a else ''}>{score_b}/10</td></tr>
            </tbody>
          </table>
          <div class="cta-stack">
            {cta_pair(url_a, url_b, f"Get {name_a}", f"Get {name_b}")}
          </div>
        </div>

        <div class="sp-glass-pink sp-glass-sm" style="padding:20px">
          <h4 style="color:var(--ink);font-size:.92rem;font-weight:800;margin-bottom:8px;letter-spacing:-.015em">📌 Save to Shortlist</h4>
          <p style="font-size:.82rem;color:var(--ink-3);line-height:1.55;margin-bottom:12px">Compare these with your other picks.</p>
          <a href="/shortlist" class="sp-btn sp-btn-primary sp-btn-sm glint-button" style="width:100%">Open Shortlist →</a>
        </div>

        <div class="sp-glass sp-glass-sm" style="padding:20px">
          <h4 style="color:var(--ink);font-size:.9rem;font-weight:800;margin-bottom:10px">On this page</h4>
          {''.join('<a href="#tab-' + t + '" onclick="switchTabByAnchor(&quot;' + t + '&quot;);return false" style="display:block;padding:6px 10px;border-radius:8px;font-size:.8rem;color:var(--ink-3);font-weight:600;margin-bottom:2px;transition:color .15s" class="sp-toc-link">' + l + '</a>' for t,l in [("overview","Overview"),("pricing","Pricing"),("features","Features"),("verdict","Final Verdict"),("faq","FAQs")])}
        </div>
      </aside>
    </div>
  </div>
</section>

<!-- RELATED LINKS -->
<section class="sp-section-sm" style="border-top:1px solid var(--line)">
  <div class="sp-container-narrow">
    <h2 style="font-size:1.1rem;font-weight:800;color:var(--ink);margin-bottom:1rem">Related Comparisons</h2>
    <div style="display:flex;flex-wrap:wrap;gap:.5rem">
      <a href="/pages/" style="display:inline-flex;align-items:center;gap:5px;padding:6px 13px;background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:9999px;font-size:.8rem;color:var(--ink-3);font-weight:600;transition:all .15s" onmouseover="this.style.borderColor='var(--line-pink)';this.style.color='var(--pink-light)'" onmouseout="this.style.borderColor='var(--line)';this.style.color='var(--ink-3)'">All {name_a} comparisons</a>
      <a href="/pages/" style="display:inline-flex;align-items:center;gap:5px;padding:6px 13px;background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:9999px;font-size:.8rem;color:var(--ink-3);font-weight:600;transition:all .15s" onmouseover="this.style.borderColor='var(--line-pink)';this.style.color='var(--pink-light)'" onmouseout="this.style.borderColor='var(--line)';this.style.color='var(--ink-3)'">All {name_b} comparisons</a>
    </div>
  </div>
</section>

<footer class="sp-footer">
  <div class="sp-footer-inner">
    <div class="sp-footer-brand">
      <div class="sp-nav-logo"><span class="sp-nav-logo-mark">S</span>Saa<em>Spare</em></div>
      <p>The honest guide to SaaS. Independent research, weekly pricing verification, no paid rankings.</p>
    </div>
    <div class="sp-footer-col"><h4>Product</h4><a href="/pages/">Comparisons</a><a href="/deal-radar">Deal Radar</a><a href="/newsletter">Newsletter</a></div>
    <div class="sp-footer-col"><h4>Company</h4><a href="/about">About</a><a href="/editorial-policy">Editorial Policy</a><a href="/methodology">Methodology</a></div>
    <div class="sp-footer-col"><h4>Legal</h4><a href="/privacy">Privacy</a><a href="/affiliate-disclosure">Affiliate Disclosure</a><a href="/corrections">Corrections</a></div>
  </div>
  <div class="sp-footer-bottom">
    <span>© {YEAR} SaaSpare. All rights reserved.</span>
    <span>Made for buyers. Not vendors.</span>
  </div>
</footer>

<!-- STICKY BOTTOM CTA -->
<div class="sticky-cta" id="sticky-cta">
  <span style="flex:1;font-size:.88rem;color:var(--ink-3)">
    <strong style="color:var(--ink)">{name_a} vs {name_b}</strong> — Ready to decide?
  </span>
  <div style="display:flex;gap:8px;align-items:center;flex-shrink:0">
    {cta_btn(winner_url, f"Get {winner}", "sp-btn sp-btn-primary sp-btn-sm")}
    <button class="sp-btn sp-btn-ghost sp-btn-sm" onclick="document.getElementById('sticky-cta').style.display='none'">✕</button>
  </div>
</div>

<script defer src="/assets/motion.js"></script>
<script>
/* Tab system */
function switchTab(e, id) {{
  document.querySelectorAll('.ar-tab').forEach(function(t){{t.classList.remove('active')}});
  e.target.classList.add('active');
  document.querySelectorAll('[id^="tab-"]').forEach(function(s){{s.style.display='none'}});
  var el = document.getElementById('tab-' + id);
  if(el) el.style.display = '';
}}
function switchTabByAnchor(id) {{
  var tabs = document.querySelectorAll('.ar-tab');
  var tabIds = ['overview','pricing','features','verdict','faq'];
  var idx = tabIds.indexOf(id);
  if(idx > -1 && tabs[idx]) {{
    tabs.forEach(function(t){{t.classList.remove('active')}});
    tabs[idx].classList.add('active');
    document.querySelectorAll('[id^="tab-"]').forEach(function(s){{s.style.display='none'}});
    var el = document.getElementById('tab-' + id);
    if(el) el.style.display = '';
  }}
}}
/* Affiliate click tracking */
(function(){{document.addEventListener('click',function(e){{var a=e.target.closest('a[href*="/go/"]');if(a&&window.gtag)gtag('event','affiliate_click',{{tool_slug:'{slug_a}',page_path:window.location.pathname,link_href:a.getAttribute('href')}});}},{{capture:true,passive:true}});}})();
</script>
</body>
</html>"""


# ── Batch process all VS pages ─────────────────────────────────────────────────

def slugs_from_filename(fname: str) -> tuple[str, str] | None:
    """Extract (slug_a, slug_b) from a VS page filename."""
    m = re.match(r"^(.+?)-vs-(.+?)-which-is-better-in-\d{4}\.html$", fname)
    if m:
        return m.group(1), m.group(2)
    m2 = re.match(r"^(.+?)-vs-(.+?)\.html$", fname)
    if m2:
        return m2.group(1), m2.group(2)
    return None


created = skipped = errors = 0
vs_files = list(PAGES.glob("*-vs-*.html"))
print(f"Found {len(vs_files)} VS pages to rebuild…")

for f in sorted(vs_files):
    slugs = slugs_from_filename(f.name)
    if not slugs:
        errors += 1
        continue

    slug_a, slug_b = slugs
    canonical_slug = f.stem  # filename without .html

    try:
        content = make_vs_page(slug_a, slug_b, canonical_slug)
        f.write_text(content, encoding="utf-8")
        created += 1
    except Exception as e:
        errors += 1
        print(f"  ERROR {f.name}: {e}")

    if created % 100 == 0 and created > 0:
        print(f"  Rebuilt {created}/{len(vs_files)}…")

print(f"\nDone. Rebuilt: {created} | Errors: {errors}")
print("All VS pages now use saaspare-v2.css + motion.css + motion.js")
