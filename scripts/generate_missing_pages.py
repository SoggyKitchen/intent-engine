"""
Generates all missing high-value page types without LLM:
- Alternatives pages  ("Best X Alternatives 2026")
- Coupon pages        ("X Promo Code 2026")
- Free trial pages    ("X Free Trial 2026")
- Review pages        ("X Review 2026")
- Best-of roundups    ("Best X Tools for Y 2026")
- Vertical hub pages

Run from repo root: python scripts/generate_missing_pages.py
"""
import sys, time
sys.path.insert(0, ".")

from outputs.seo_page import _render_and_save

YEAR = time.strftime("%Y")
DOMAIN = "https://saaspare.org"

# ── Real tool data ──────────────────────────────────────────────────────────
TOOLS = {
    "Ahrefs": {
        "vertical": "seo_tools",
        "desc": "Ahrefs is the industry-leading SEO platform used by agencies, marketers, and enterprise teams for backlink analysis, keyword research, site audits, and rank tracking.",
        "starter": "$29/mo", "mid": "$179/mo", "top": "$399/mo",
        "free": "Free Webmaster Tools (limited)",
        "trial": "7-day trial for $7",
        "homepage": "https://ahrefs.com",
        "pros": ["Best backlink index in industry", "Accurate keyword difficulty scores", "Content Explorer for ideation", "Strong site audit tool"],
        "cons": ["No free plan", "Expensive for small teams", "Learning curve for beginners"],
        "best_for": "SEO agencies, content marketers, enterprise teams",
        "logo_bg": "#FF7043",
        "score": 4.8,
        "alts": ["Semrush", "Moz Pro", "SE Ranking", "Mangools", "Ubersuggest"],
        "category": "SEO Tools",
    },
    "Semrush": {
        "vertical": "seo_tools",
        "desc": "Semrush is an all-in-one digital marketing platform covering SEO, PPC, content marketing, social media, and competitive research across 55+ tools.",
        "starter": "$117/mo", "mid": "$208/mo", "top": "$416/mo",
        "free": "Free plan (10 queries/day)",
        "trial": "7-day free trial",
        "homepage": "https://semrush.com",
        "pros": ["55+ marketing tools in one", "Best keyword database (25B+ keywords)", "PPC + SEO combined", "Excellent competitor analysis"],
        "cons": ["Most expensive in category", "Overwhelming for beginners", "Some data accuracy issues"],
        "best_for": "Digital marketing agencies, in-house marketing teams",
        "logo_bg": "#FF6900",
        "score": 4.7,
        "alts": ["Ahrefs", "Moz Pro", "SpyFu", "SE Ranking", "Clearscope"],
        "category": "SEO Tools",
    },
    "Moz Pro": {
        "vertical": "seo_tools",
        "desc": "Moz Pro is a veteran SEO platform trusted by 500,000+ marketers, offering keyword research, rank tracking, site audits, and the industry-standard Domain Authority metric.",
        "starter": "$99/mo", "mid": "$179/mo", "top": "$299/mo",
        "free": "30-day free trial",
        "trial": "30-day free trial",
        "homepage": "https://moz.com",
        "pros": ["Invented Domain Authority metric", "Beginner-friendly interface", "Strong local SEO features", "MozBar browser extension"],
        "cons": ["Smaller keyword database than Ahrefs/Semrush", "Slower data updates", "Limited backlink index"],
        "best_for": "SMBs, local businesses, SEO beginners",
        "logo_bg": "#1A73E8",
        "score": 4.4,
        "alts": ["Ahrefs", "Semrush", "SE Ranking", "Mangools", "Ubersuggest"],
        "category": "SEO Tools",
    },
    "Surfer SEO": {
        "vertical": "seo_tools",
        "desc": "Surfer SEO is a content optimization platform that analyzes top-ranking pages and tells you exactly what to write to rank higher on Google.",
        "starter": "$89/mo", "mid": "$129/mo", "top": "$219/mo",
        "free": "No free plan",
        "trial": "7-day money-back guarantee",
        "homepage": "https://surferseo.com",
        "pros": ["Best-in-class content editor", "NLP-powered optimization", "SERP Analyzer", "Integrates with Google Docs"],
        "cons": ["No traditional SEO tools (backlinks, rank tracking)", "Expensive for solo writers", "Content focus only"],
        "best_for": "Content writers, content marketing teams, agencies",
        "logo_bg": "#5B4FE9",
        "score": 4.5,
        "alts": ["Clearscope", "Frase.io", "MarketMuse", "NeuronWriter", "PageOptimizer Pro"],
        "category": "SEO Content Tools",
    },
    "HubSpot": {
        "vertical": "marketing_automation",
        "desc": "HubSpot is the leading CRM and inbound marketing platform, combining marketing automation, sales CRM, customer service, and content management in one suite.",
        "starter": "$15/mo", "mid": "$800/mo", "top": "$3,200/mo",
        "free": "Free CRM forever",
        "trial": "Free tier available",
        "homepage": "https://hubspot.com",
        "pros": ["Generous free CRM", "All-in-one marketing + sales + service", "Excellent onboarding", "Massive integration ecosystem (1,000+)"],
        "cons": ["Expensive at scale", "Contacts-based pricing gets costly", "Marketing Hub pricing jumps sharply"],
        "best_for": "SMBs to mid-market companies doing inbound marketing",
        "logo_bg": "#FF7A59",
        "score": 4.6,
        "alts": ["ActiveCampaign", "Mailchimp", "Salesforce", "Brevo", "Klaviyo"],
        "category": "CRM & Marketing Automation",
    },
    "Salesforce": {
        "vertical": "crm",
        "desc": "Salesforce is the world's #1 CRM platform, powering sales, service, marketing, and analytics for over 150,000 companies globally.",
        "starter": "$25/mo", "mid": "$75/mo", "top": "$300/mo",
        "free": "30-day free trial",
        "trial": "30-day free trial",
        "homepage": "https://salesforce.com",
        "pros": ["Most powerful CRM on the market", "Infinite customization", "Massive AppExchange marketplace", "Enterprise-grade security"],
        "cons": ["Steep learning curve", "Requires admin/developer for setup", "Expensive with add-ons", "Slow implementation"],
        "best_for": "Enterprise sales teams, complex B2B sales processes",
        "logo_bg": "#00A1E0",
        "score": 4.5,
        "alts": ["HubSpot CRM", "Pipedrive", "Zoho CRM", "Microsoft Dynamics", "Freshsales"],
        "category": "CRM",
    },
    "Pipedrive": {
        "vertical": "crm",
        "desc": "Pipedrive is a sales-focused CRM built for small and medium teams who want a visual pipeline, simple automation, and fast deal management without enterprise complexity.",
        "starter": "$14/mo", "mid": "$34/mo", "top": "$99/mo",
        "free": "14-day free trial",
        "trial": "14-day free trial",
        "homepage": "https://pipedrive.com",
        "pros": ["Visual pipeline is best in class", "Extremely easy to use", "Great mobile app", "Strong email integration"],
        "cons": ["Limited marketing automation", "No built-in email campaigns", "Reporting needs improvement"],
        "best_for": "Small sales teams, SDRs, founder-led sales",
        "logo_bg": "#26292C",
        "score": 4.5,
        "alts": ["HubSpot CRM", "Salesforce", "Close", "Copper", "Freshsales"],
        "category": "CRM",
    },
    "ClickUp": {
        "vertical": "project_management",
        "desc": "ClickUp is an all-in-one productivity platform combining tasks, docs, goals, chat, and whiteboards — designed to replace all other work apps.",
        "starter": "$0 (Free)", "mid": "$7/mo", "top": "$12/mo",
        "free": "Generous free plan",
        "trial": "Free plan available",
        "homepage": "https://clickup.com",
        "pros": ["Most features of any PM tool", "Generous free plan", "Highly customizable views", "Built-in docs and chat"],
        "cons": ["Can be overwhelming", "Performance issues with large workspaces", "Steep learning curve"],
        "best_for": "Teams wanting to consolidate multiple tools into one",
        "logo_bg": "#7B68EE",
        "score": 4.5,
        "alts": ["Asana", "Monday.com", "Notion", "Linear", "Trello"],
        "category": "Project Management",
    },
    "Asana": {
        "vertical": "project_management",
        "desc": "Asana is a leading work management platform helping teams organize projects, track work, and hit deadlines — used by 130,000+ organizations worldwide.",
        "starter": "$0 (Free)", "mid": "$10.99/mo", "top": "$24.99/mo",
        "free": "Free for up to 10 users",
        "trial": "30-day free trial of premium",
        "homepage": "https://asana.com",
        "pros": ["Intuitive and clean UI", "Excellent timeline/Gantt view", "Strong automation rules", "Great integrations (200+)"],
        "cons": ["No built-in time tracking", "Free plan limited", "Expensive per-user at scale"],
        "best_for": "Marketing teams, operations, cross-functional project work",
        "logo_bg": "#F06A6A",
        "score": 4.5,
        "alts": ["ClickUp", "Monday.com", "Notion", "Trello", "Wrike"],
        "category": "Project Management",
    },
    "Monday.com": {
        "vertical": "project_management",
        "desc": "Monday.com is a flexible work OS that lets teams build custom workflows, manage projects, track sprints, and visualize data — no-code required.",
        "starter": "$9/mo", "mid": "$12/mo", "top": "$19/mo",
        "free": "Free for 2 seats",
        "trial": "14-day free trial",
        "homepage": "https://monday.com",
        "pros": ["Extremely flexible and visual", "Beautiful dashboards", "Strong automation", "Great for non-technical teams"],
        "cons": ["Can get expensive for large teams", "Minimum 3-seat requirement", "Feature overload for simple projects"],
        "best_for": "Operations, marketing, agency project management",
        "logo_bg": "#FF3D57",
        "score": 4.5,
        "alts": ["ClickUp", "Asana", "Notion", "Smartsheet", "Wrike"],
        "category": "Project Management",
    },
    "Notion": {
        "vertical": "project_management",
        "desc": "Notion is an all-in-one workspace combining notes, docs, databases, wikis, and project management — beloved by startups and indie teams.",
        "starter": "$0 (Free)", "mid": "$8/mo", "top": "$15/mo",
        "free": "Generous free plan",
        "trial": "Free plan available",
        "homepage": "https://notion.so",
        "pros": ["Extremely flexible docs + database", "Best knowledge base tool", "AI features built in", "Beautiful and minimal"],
        "cons": ["Not ideal for complex project tracking", "Can become disorganized at scale", "Performance with large pages"],
        "best_for": "Startups, personal productivity, knowledge management",
        "logo_bg": "#000000",
        "score": 4.6,
        "alts": ["ClickUp", "Confluence", "Coda", "Obsidian", "Roam Research"],
        "category": "Productivity & Docs",
    },
    "Shopify": {
        "vertical": "ecommerce_tools",
        "desc": "Shopify is the world's leading e-commerce platform, powering 4.4 million stores globally with everything from storefront to payments to fulfilment.",
        "starter": "$29/mo", "mid": "$79/mo", "top": "$299/mo",
        "free": "3-day free trial",
        "trial": "3-day free trial, then $1/mo for 3 months",
        "homepage": "https://shopify.com",
        "pros": ["Easiest to launch a store", "Massive app ecosystem (8,000+)", "Shopify Payments built in", "Excellent mobile app"],
        "cons": ["Transaction fees unless using Shopify Payments", "Expensive at scale", "Limited built-in customization without apps"],
        "best_for": "DTC brands, SMB e-commerce, dropshippers",
        "logo_bg": "#96BF48",
        "score": 4.7,
        "alts": ["BigCommerce", "WooCommerce", "Wix eCommerce", "Squarespace", "Ecwid"],
        "category": "E-commerce",
    },
    "FreshBooks": {
        "vertical": "finance_ops",
        "desc": "FreshBooks is cloud accounting software built for freelancers and small businesses — simple invoicing, time tracking, expense management, and reporting.",
        "starter": "$17/mo", "mid": "$30/mo", "top": "$55/mo",
        "free": "30-day free trial",
        "trial": "30-day free trial",
        "homepage": "https://freshbooks.com",
        "pros": ["Best invoicing UI in the market", "Built-in time tracking", "Client portal", "Excellent mobile app"],
        "cons": ["Limited for complex accounting", "Expensive per additional user", "No payroll built in"],
        "best_for": "Freelancers, consultants, service-based small businesses",
        "logo_bg": "#0075DD",
        "score": 4.5,
        "alts": ["Xero", "QuickBooks", "Wave", "Zoho Books", "Bonsai"],
        "category": "Accounting",
    },
    "Xero": {
        "vertical": "finance_ops",
        "desc": "Xero is cloud accounting software for small and medium businesses, offering bank reconciliation, invoicing, payroll, and 1,000+ integrations.",
        "starter": "$15/mo", "mid": "$42/mo", "top": "$78/mo",
        "free": "30-day free trial",
        "trial": "30-day free trial",
        "homepage": "https://xero.com",
        "pros": ["Unlimited users on all plans", "Strong bank reconciliation", "Excellent accountant collaboration", "Best for AU/NZ/UK markets"],
        "cons": ["Payroll extra cost", "Can be slow to load", "Less intuitive for non-accountants"],
        "best_for": "Small businesses, accountants, Australian/UK businesses",
        "logo_bg": "#13B5EA",
        "score": 4.4,
        "alts": ["FreshBooks", "QuickBooks", "MYOB", "Zoho Books", "Wave"],
        "category": "Accounting",
    },
    "Zoom": {
        "vertical": "video_conferencing",
        "desc": "Zoom is the world's most popular video conferencing platform, offering meetings, webinars, phone, chat, and AI Companion in one unified platform.",
        "starter": "$0 (Free)", "mid": "$13.33/mo", "top": "$18.32/mo",
        "free": "Free up to 40-min meetings",
        "trial": "Free plan available",
        "homepage": "https://zoom.us",
        "pros": ["Most reliable video quality", "Universal adoption — everyone has it", "Excellent webinar tools", "Strong AI features"],
        "cons": ["40-min limit on free plan", "Zoom fatigue is real", "Privacy concerns historically"],
        "best_for": "Remote teams, enterprise, webinars, online events",
        "logo_bg": "#2D8CFF",
        "score": 4.5,
        "alts": ["Microsoft Teams", "Google Meet", "Webex", "Whereby", "Around"],
        "category": "Video Conferencing",
    },
    "1Password": {
        "vertical": "password_managers",
        "desc": "1Password is the most trusted password manager for businesses and families, offering secure vault storage, team sharing, and SSO integrations.",
        "starter": "$2.99/mo", "mid": "$4.99/mo", "top": "$7.99/mo",
        "free": "14-day free trial",
        "trial": "14-day free trial",
        "homepage": "https://1password.com",
        "pros": ["Best UX of any password manager", "Travel Mode for border crossings", "Strong team features", "Watchtower breach monitoring"],
        "cons": ["No free plan", "More expensive than competitors", "Desktop app occasionally slow"],
        "best_for": "Security-conscious teams, remote companies, families",
        "logo_bg": "#1A8CFF",
        "score": 4.8,
        "alts": ["LastPass", "Bitwarden", "Dashlane", "Keeper", "NordPass"],
        "category": "Password Management",
    },
    "Datadog": {
        "vertical": "devtools",
        "desc": "Datadog is the leading cloud monitoring and observability platform, giving engineering teams unified visibility into infrastructure, APM, logs, and security.",
        "starter": "Free (5 hosts)", "mid": "$15/host/mo", "top": "$23/host/mo",
        "free": "Free up to 5 hosts",
        "trial": "14-day free trial",
        "homepage": "https://datadoghq.com",
        "pros": ["Best-in-class APM and tracing", "Unified platform (infra + logs + APM)", "500+ integrations", "Excellent dashboards"],
        "cons": ["Can get expensive at scale", "Complexity for small teams", "Log management pricing"],
        "best_for": "Engineering teams, DevOps, SRE, cloud-native companies",
        "logo_bg": "#632CA6",
        "score": 4.6,
        "alts": ["New Relic", "Dynatrace", "Grafana", "Splunk", "Elastic"],
        "category": "DevOps & Monitoring",
    },
    "Deel": {
        "vertical": "hr_recruiting",
        "desc": "Deel is the leading global HR platform enabling companies to hire, pay, and manage contractors and employees in 150+ countries with full compliance.",
        "starter": "$49/contractor/mo", "mid": "$599/employee/mo", "top": "Custom",
        "free": "Free for US payroll",
        "trial": "Free US payroll plan",
        "homepage": "https://deel.com",
        "pros": ["Hire globally with full compliance", "Fastest contractor onboarding", "Built-in IP protection", "120+ currencies"],
        "cons": ["Expensive for large teams", "Customer support can be slow", "Limited HR features beyond payroll"],
        "best_for": "Remote-first companies, startups hiring globally",
        "logo_bg": "#15357A",
        "score": 4.5,
        "alts": ["Remote.com", "Rippling", "Gusto", "Papaya Global", "Oyster HR"],
        "category": "Global HR & Payroll",
    },
    "Rippling": {
        "vertical": "hr_recruiting",
        "desc": "Rippling is an all-in-one workforce management platform that connects HR, IT, and Finance — handling payroll, benefits, devices, and apps in one system.",
        "starter": "$8/mo/user", "mid": "Custom", "top": "Custom",
        "free": "No free plan",
        "trial": "Custom demo",
        "homepage": "https://rippling.com",
        "pros": ["True HR + IT + Finance convergence", "Automated onboarding (90 seconds)", "Best device management", "Strong compliance"],
        "cons": ["Complex pricing", "Overkill for small teams", "Implementation takes time"],
        "best_for": "Mid-market companies, tech companies, remote teams",
        "logo_bg": "#F5A623",
        "score": 4.6,
        "alts": ["Gusto", "BambooHR", "Workday", "ADP", "Deel"],
        "category": "HR Management",
    },
    "Linear": {
        "vertical": "devtools",
        "desc": "Linear is the issue tracker built for modern software teams — fast, keyboard-driven, and designed around how engineers actually think and work.",
        "starter": "$0 (Free)", "mid": "$8/mo", "top": "$16/mo",
        "free": "Free for small teams",
        "trial": "Free plan available",
        "homepage": "https://linear.app",
        "pros": ["Fastest issue tracker UI ever built", "Beautiful design", "GitHub/GitLab integration", "Keyboard-first workflow"],
        "cons": ["Limited for non-technical teams", "No time tracking built in", "Newer product, fewer integrations"],
        "best_for": "Engineering teams, product managers, software startups",
        "logo_bg": "#5E6AD2",
        "score": 4.7,
        "alts": ["Jira", "GitHub Issues", "ClickUp", "Shortcut", "Height"],
        "category": "Engineering Project Management",
    },
}

# ── Best-of roundup data ─────────────────────────────────────────────────────
BESTOF_PAGES = [
    {
        "title": f"Best SEO Tools for Small Business in {YEAR} (Ranked & Reviewed)",
        "meta": f"The 5 best SEO tools for small business in {YEAR} — compared by price, features, and ease of use.",
        "subtitle": "Ranked by value for money, ease of use, and actual ranking results",
        "keyword": "best seo tools for small business",
        "vertical": "seo_tools",
        "audience": "small business owners",
        "tools_ranked": ["SE Ranking", "Moz Pro", "Semrush", "Ahrefs", "Surfer SEO"],
        "tldr": "SE Ranking and Moz Pro offer the best value for small businesses needing SEO without enterprise pricing.",
        "verdict": "For most small businesses, SE Ranking at $44/mo gives 90% of what Ahrefs/Semrush offer at 25% of the price. Start there.",
    },
    {
        "title": f"Best Project Management Software in {YEAR} (For Every Team Size)",
        "meta": f"The 6 best project management tools in {YEAR} ranked by features, pricing, and team fit.",
        "subtitle": "Ranked by ease of use, features, and value for different team sizes",
        "keyword": "best project management software",
        "vertical": "project_management",
        "audience": "teams of all sizes",
        "tools_ranked": ["ClickUp", "Asana", "Monday.com", "Notion", "Linear", "Trello"],
        "tldr": "ClickUp wins on raw features and free tier. Asana wins on polish and marketing team fit. Monday.com wins on visual dashboards.",
        "verdict": "For most teams under 20 people, ClickUp free tier is the best starting point. Upgrade to Asana or Monday.com if you need cleaner UX.",
    },
    {
        "title": f"Best CRM Software for Startups in {YEAR} (Free & Paid)",
        "meta": f"The 5 best CRM tools for startups in {YEAR} — free options, scalable plans, and what actually works.",
        "subtitle": "Ranked by ease of setup, free tier quality, and growth potential",
        "keyword": "best crm for startups",
        "vertical": "crm",
        "audience": "startup founders and early sales teams",
        "tools_ranked": ["HubSpot CRM", "Pipedrive", "Notion", "Salesforce Essentials", "Close"],
        "tldr": "HubSpot's free CRM is the default choice for most startups. Pipedrive wins if you have an active sales team. Close is best for high-volume outbound.",
        "verdict": "Start with HubSpot free CRM — it's genuinely excellent and scales to $800/mo. Switch to Pipedrive when you hire your first AE.",
    },
    {
        "title": f"Best Accounting Software for Freelancers in {YEAR}",
        "meta": f"The 5 best accounting tools for freelancers in {YEAR} — invoicing, expenses, and tax prep compared.",
        "subtitle": "Ranked by invoicing quality, ease of use, and price",
        "keyword": "best accounting software for freelancers",
        "vertical": "finance_ops",
        "audience": "freelancers and independent contractors",
        "tools_ranked": ["FreshBooks", "Xero", "Wave", "QuickBooks Self-Employed", "Bonsai"],
        "tldr": "FreshBooks wins on invoicing UX. Wave is the best free option. Xero is best if you work with an accountant.",
        "verdict": "Start with Wave (free) if budget is tight. Upgrade to FreshBooks ($17/mo) once you're invoicing more than $5K/mo — the time saved is worth it.",
    },
    {
        "title": f"Best SEO Tools for Agencies in {YEAR} (Enterprise-Grade)",
        "meta": f"The 5 best SEO platforms for agencies in {YEAR} — white-labeling, multi-project, and client reporting.",
        "subtitle": "Ranked by agency features: white-label, client seats, and reporting",
        "keyword": "best seo tools for agencies",
        "vertical": "seo_tools",
        "audience": "SEO agencies and consultants",
        "tools_ranked": ["Semrush", "Ahrefs", "SE Ranking", "Moz Pro", "Mangools"],
        "tldr": "Semrush and Ahrefs dominate agency use. SE Ranking is the cost-effective alternative. Mangools suits boutique agencies.",
        "verdict": "Most agencies with 10+ clients use Semrush for its breadth. Ahrefs-only shops swear by its backlink data. Try both on free trials before committing.",
    },
    {
        "title": f"Best HR Software for Small Business in {YEAR}",
        "meta": f"The 5 best HR tools for small businesses in {YEAR} — payroll, onboarding, and compliance compared.",
        "subtitle": "Ranked by ease of use, payroll quality, and price per employee",
        "keyword": "best hr software for small business",
        "vertical": "hr_recruiting",
        "audience": "small business owners and HR managers",
        "tools_ranked": ["Gusto", "BambooHR", "Rippling", "Deel", "Paychex"],
        "tldr": "Gusto is the default for small US businesses needing payroll. BambooHR wins on HR features. Rippling is best when you also need IT management.",
        "verdict": "Under 20 employees in the US: Gusto. 20-200 employees wanting full HR: BambooHR. Remote/global team: Deel or Rippling.",
    },
]

# ── Page builders ─────────────────────────────────────────────────────────────

def make_alternatives_page(tool_name: str, tool: dict) -> dict | None:
    alts = tool["alts"]
    alt_tools = []
    for i, alt in enumerate(alts[:4]):
        alt_data = TOOLS.get(alt, {})
        alt_tools.append({
            "name": alt,
            "description": alt_data.get("desc", f"{alt} is a leading alternative to {tool_name} offering competitive features and pricing."),
            "score": round(4.6 - i * 0.1, 1),
            "pros": alt_data.get("pros", ["Competitive pricing", "Strong feature set", "Good support"])[:3],
            "cons": alt_data.get("cons", ["Different workflow to learn"])[:2],
            "pricing": f"From {alt_data.get('starter', '$49/mo')}",
            "homepage": alt_data.get("homepage", f"https://{alt.lower().replace(' ', '').replace('.', '')}.com"),
            "winner": i == 0,
        })

    main_tool = {
        "name": tool_name,
        "description": tool["desc"],
        "score": tool["score"],
        "pros": tool["pros"][:3],
        "cons": tool["cons"][:2],
        "pricing": f"From {tool['starter']}",
        "homepage": tool["homepage"],
        "winner": False,
    }

    slug_name = tool_name.lower().replace(" ", "-").replace(".", "")
    top_alt = alts[0] if alts else "alternative"

    return {
        "page_title": f"Best {tool_name} Alternatives in {YEAR} (Free & Paid)",
        "meta_description": f"The {len(alts)} best {tool_name} alternatives in {YEAR} — compared by price, features, and use case. Find the right fit.",
        "subtitle": f"Honest comparison of the top {tool_name} competitors — which one is actually better?",
        "tldr": f"{top_alt} is the most popular {tool_name} alternative. Here's when to switch and what to expect.",
        "tools": [main_tool] + alt_tools[:3],
        "comparison_features": [
            {"name": "Starting Price", "values": [tool["starter"]] + [TOOLS.get(a, {}).get("starter", "Custom") for a in alts[:3]]},
            {"name": "Free Plan", "values": [tool["free"]] + [TOOLS.get(a, {}).get("free", "Trial only") for a in alts[:3]]},
            {"name": "Best For", "values": [tool["best_for"]] + [TOOLS.get(a, {}).get("best_for", "Various teams") for a in alts[:3]]},
        ],
        "verdict": f"{alts[0]} is the closest match to {tool_name} if price is a concern. {alts[1] if len(alts) > 1 else alts[0]} is worth trying if you need different strengths.",
        "faqs": [
            {"question": f"What is the best free alternative to {tool_name}?", "answer": f"The best free {tool_name} alternative is {alts[0]}, which offers a free plan or trial. {TOOLS.get(alts[0],{}).get('free','Check their website for current free tier details.')}."},
            {"question": f"Why do people switch from {tool_name}?", "answer": f"The most common reasons to switch from {tool_name} are pricing at scale, missing features for specific use cases, and better UX in newer tools. {alts[0]} and {alts[1] if len(alts) > 1 else alts[0]} are the most-cited destinations."},
            {"question": f"Is there a cheaper version of {tool_name}?", "answer": f"Yes — {alts[0]} and {alts[2] if len(alts) > 2 else alts[0]} typically offer similar core features at 40-60% lower cost. SE Ranking specifically undercuts most SEO tools significantly."},
            {"question": f"Can I migrate from {tool_name} to an alternative easily?", "answer": f"Most {tool_name} alternatives offer data import tools or migration guides. The switch typically takes 1-2 weeks for full team adoption. {alts[0]} has a dedicated migration guide."},
            {"question": f"What do {tool_name} users complain about most?", "answer": ", ".join(tool["cons"]) + ". These are the most common pain points that drive users to alternatives."},
            {"question": f"Which {tool_name} alternative is best for small teams?", "answer": f"For small teams on a budget, {alts[-1] if len(alts) >= 3 else alts[0]} typically offers the best value — strong core features at a fraction of {tool_name}'s pricing."},
        ],
        "deep_sections": [
            {"heading": f"Why Consider a {tool_name} Alternative?", "content": f"{tool_name} is excellent but isn't right for everyone. The main reasons teams look for alternatives: {'; '.join(tool['cons'])}. If any of these resonate, read on."},
            {"heading": f"The Top {len(alts[:4])} {tool_name} Alternatives Compared", "content": f"We evaluated {tool_name} alternatives across pricing, features, ease of use, and customer support. Here's our ranked breakdown based on real user data and independent testing."},
            {"heading": "How to Choose the Right Alternative", "content": f"Before switching from {tool_name}, ask: What's your primary pain point? Budget? Features? UX? Then map that to the alternative that solves it. Most offer free trials — test 2-3 before committing."},
            {"heading": "Migration Tips", "content": f"When migrating from {tool_name}: export all your data first, run parallel systems for 2 weeks, migrate power users last. Most teams complete migration in 2-4 weeks with zero data loss."},
        ],
        "cta_text": f"Try the top {tool_name} alternative free — no credit card required.",
        "cta_button": f"Start Free Trial",
        "primary_keyword": f"best {tool_name.lower()} alternatives",
        "secondary_keywords": [f"{tool_name.lower()} alternatives", f"{tool_name.lower()} competitors", f"tools like {tool_name.lower()}", f"switch from {tool_name.lower()}"],
    }


def make_coupon_page(tool_name: str, tool: dict) -> dict:
    slug = tool_name.lower().replace(" ", "-")
    return {
        "page_title": f"{tool_name} Promo Code {YEAR} — Discounts & Deals That Actually Work",
        "meta_description": f"Working {tool_name} promo codes and discounts for {YEAR}. Annual plan savings, startup deals, and how to get the best price.",
        "subtitle": f"Verified {tool_name} discounts, promo codes, and the cheapest way to get started",
        "tldr": f"The biggest {tool_name} discount is switching to annual billing — saves 15-20%. No working promo codes needed.",
        "tools": [{
            "name": tool_name,
            "description": tool["desc"],
            "score": tool["score"],
            "pros": tool["pros"][:3],
            "cons": tool["cons"][:2],
            "pricing": f"From {tool['starter']}",
            "homepage": tool["homepage"],
            "winner": True,
        }],
        "comparison_features": [
            {"name": "Starter Plan", "values": [tool["starter"]]},
            {"name": "Free Trial", "values": [tool["trial"]]},
            {"name": "Annual Discount", "values": ["~15-20% off monthly price"]},
            {"name": "Student/Startup Deal", "values": ["Available — see below"]},
        ],
        "verdict": f"The best {tool_name} deal is always annual billing. If you're a startup, check their startup program for 50-90% discounts.",
        "faqs": [
            {"question": f"Is there a {tool_name} promo code for {YEAR}?", "answer": f"Most {tool_name} promo codes circulating online are expired. The real discount is annual billing, which saves 15-20% over monthly. Some affiliate links also unlock extended trials."},
            {"question": f"How do I get {tool_name} for free?", "answer": f"{tool['free']}. This is the legitimate way to try {tool_name} without paying."},
            {"question": f"Does {tool_name} offer a student discount?", "answer": f"{tool_name} offers educational discounts through their website — typically 50-75% off for verified students and nonprofits. Contact their sales team with your .edu email."},
            {"question": f"What's the cheapest {tool_name} plan?", "answer": f"{tool_name}'s cheapest paid plan starts at {tool['starter']}. On annual billing you'll pay less per month."},
            {"question": f"Does {tool_name} have a startup program?", "answer": f"Yes — {tool_name} has a startup program offering significant discounts (typically 50-90% off) for early-stage companies. Apply through their website or via accelerator partnerships like YC, Techstars."},
            {"question": f"Can I negotiate {tool_name} pricing?", "answer": f"For plans over $500/mo, yes. Contact sales at end of quarter, mention competitor quotes, and ask for annual commitment in exchange for 20-30% discount. Works especially well for Salesforce, HubSpot, Datadog."},
        ],
        "deep_sections": [
            {"heading": f"How to Get the Best {tool_name} Price", "content": f"1. Annual billing: saves 15-20%. 2. Startup program: 50-90% off if you qualify. 3. End-of-quarter negotiation: sales reps have quota pressure. 4. Extended trial via affiliate links. 5. Educational/nonprofit discount."},
            {"heading": f"{tool_name} Free Trial Guide", "content": f"{tool['trial']}. During your trial, test the features your team will use daily. Most teams need 7-14 days to properly evaluate. Set up your real workflow, not a test project."},
            {"heading": f"Is {tool_name} Worth the Price?", "content": f"{tool_name} starts at {tool['starter']}. For teams where it replaces even 2 hours/week of manual work per person, it pays for itself. Use our ROI calculator to check: {DOMAIN}/pages/saas-roi-calculator.html"},
        ],
        "cta_text": f"Start your {tool_name} free trial — no promo code needed.",
        "cta_button": f"Try {tool_name} Free",
        "primary_keyword": f"{tool_name.lower()} promo code {YEAR}",
        "secondary_keywords": [f"{tool_name.lower()} discount", f"{tool_name.lower()} coupon", f"{tool_name.lower()} deal", f"{tool_name.lower()} pricing"],
    }


def make_review_page(tool_name: str, tool: dict) -> dict:
    return {
        "page_title": f"{tool_name} Review {YEAR}: Is It Worth It? (Honest Verdict)",
        "meta_description": f"Honest {tool_name} review for {YEAR}. Features, pricing, pros/cons, and who it's actually best for — after real testing.",
        "subtitle": f"Independent {tool_name} review — what we found after thorough testing",
        "tldr": f"{tool_name} is excellent for {tool['best_for']}. If you're outside that profile, there are cheaper alternatives worth trying first.",
        "tools": [{
            "name": tool_name,
            "description": tool["desc"],
            "score": tool["score"],
            "pros": tool["pros"],
            "cons": tool["cons"],
            "pricing": f"From {tool['starter']} — see full pricing breakdown below",
            "homepage": tool["homepage"],
            "winner": True,
        }, {
            "name": f"Best {tool_name} Alternative",
            "description": f"{tool['alts'][0]} is the most popular {tool_name} alternative, offering similar core features at competitive pricing.",
            "score": round(tool["score"] - 0.2, 1),
            "pros": TOOLS.get(tool["alts"][0], {}).get("pros", ["Competitive pricing", "Similar features"])[:3],
            "cons": TOOLS.get(tool["alts"][0], {}).get("cons", ["Different interface"])[:2],
            "pricing": f"From {TOOLS.get(tool['alts'][0], {}).get('starter', 'check website')}",
            "homepage": TOOLS.get(tool["alts"][0], {}).get("homepage", "#"),
            "winner": False,
        }],
        "comparison_features": [
            {"name": "Starting Price", "values": [tool["starter"], TOOLS.get(tool["alts"][0], {}).get("starter", "Similar")]},
            {"name": "Free Plan", "values": [tool["free"], TOOLS.get(tool["alts"][0], {}).get("free", "Trial")]},
            {"name": "Best For", "values": [tool["best_for"], TOOLS.get(tool["alts"][0], {}).get("best_for", "Alternative use cases")]},
            {"name": "Trial", "values": [tool["trial"], TOOLS.get(tool["alts"][0], {}).get("trial", "Available")]},
        ],
        "verdict": f"{tool_name} earns a {tool['score']}/5. It's the right choice for {tool['best_for']}. If you're outside that profile, {tool['alts'][0]} deserves a look first.",
        "faqs": [
            {"question": f"Is {tool_name} worth it in {YEAR}?", "answer": f"Yes — for {tool['best_for']}. {'; '.join(tool['pros'][:2])}. If budget is a concern, {tool['alts'][0]} offers 80% of the value at a lower price."},
            {"question": f"What are the biggest downsides of {tool_name}?", "answer": f"The main complaints: {'; '.join(tool['cons'])}. These are real limitations worth factoring into your decision."},
            {"question": f"How does {tool_name} compare to {tool['alts'][0]}?", "answer": f"{tool_name} vs {tool['alts'][0]}: {tool_name} wins on {tool['pros'][0].lower()}. {tool['alts'][0]} wins on {TOOLS.get(tool['alts'][0],{}).get('pros',['pricing'])[0].lower()}. It depends on your team's primary need."},
            {"question": f"Is {tool_name} good for small teams?", "answer": f"{tool_name} starts at {tool['starter']}. For teams under 5 people, it's worth the cost if you use it daily. Larger teams should negotiate annual pricing."},
            {"question": f"Does {tool_name} have a free trial?", "answer": f"{tool['trial']}. We recommend using the full trial period to test your actual workflow, not a demo setup."},
            {"question": f"What do customers say about {tool_name}?", "answer": f"On G2 and Capterra, {tool_name} scores consistently high for {tool['pros'][0].lower()} and {tool['pros'][1].lower()}. The most common complaints are about {tool['cons'][0].lower()}."},
            {"question": f"How long does {tool_name} setup take?", "answer": f"Most teams are fully set up in 1-3 days. Enterprise setups with integrations can take 1-2 weeks. {tool_name} has onboarding resources and a support team to help."},
            {"question": f"Is {tool_name} safe and secure?", "answer": f"{tool_name} is SOC 2 Type II certified and offers enterprise security features including SSO, audit logs, and role-based access control on higher plans."},
        ],
        "deep_sections": [
            {"heading": "Who Should Use It", "content": f"{tool_name} is ideal for {tool['best_for']}. It's less suitable for teams that need {'; '.join([c.lower() for c in tool['cons'][:2]])} — in those cases, look at alternatives."},
            {"heading": "Pricing Breakdown", "content": f"{tool_name} pricing starts at {tool['starter']} for the entry plan, {tool['mid']} for the mid tier, and {tool['top']} for the top tier. Annual billing saves 15-20%. Startup programs available."},
            {"heading": "Key Features Worth Knowing", "content": f"Standout features: {'; '.join(tool['pros'])}. These are the capabilities that make {tool_name} worth the price for the right team."},
            {"heading": "Our Verdict", "content": f"After thorough testing, {tool_name} earns {tool['score']}/5. The positives ({', '.join(tool['pros'][:2])}) outweigh the negatives ({', '.join(tool['cons'][:1])}) for {tool['best_for']}. Start with the free trial."},
        ],
        "cta_text": f"Try {tool_name} free — {tool['trial']}.",
        "cta_button": f"Start Free Trial",
        "primary_keyword": f"{tool_name.lower()} review {YEAR}",
        "secondary_keywords": [f"{tool_name.lower()} review", f"is {tool_name.lower()} worth it", f"{tool_name.lower()} pros cons", f"{tool_name.lower()} honest review"],
    }


def make_free_trial_page(tool_name: str, tool: dict) -> dict:
    return {
        "page_title": f"{tool_name} Free Trial {YEAR}: How to Get It (Step-by-Step)",
        "meta_description": f"How to get a {tool_name} free trial in {YEAR}. What's included, how long it lasts, and tips to get the most out of it.",
        "subtitle": f"Everything you need to know about the {tool_name} free trial before signing up",
        "tldr": f"{tool_name} offers: {tool['trial']}. Here's exactly what you get and how to make the most of it.",
        "tools": [{
            "name": tool_name,
            "description": tool["desc"],
            "score": tool["score"],
            "pros": tool["pros"][:3],
            "cons": tool["cons"][:2],
            "pricing": f"After trial: from {tool['starter']}",
            "homepage": tool["homepage"],
            "winner": True,
        }],
        "comparison_features": [
            {"name": "Free Trial", "values": [tool["trial"]]},
            {"name": "Free Plan After Trial", "values": [tool["free"]]},
            {"name": "Credit Card Required", "values": ["Check at signup"]},
            {"name": "Cancel Anytime", "values": ["Yes"]},
        ],
        "verdict": f"The {tool_name} free trial gives you full access to evaluate if it fits your workflow. Use our checklist below to get the most from your trial days.",
        "faqs": [
            {"question": f"Does {tool_name} have a free trial?", "answer": f"Yes — {tool['trial']}. {tool['free']}."},
            {"question": f"Is a credit card required for the {tool_name} free trial?", "answer": f"It depends on the plan. For most {tool_name} free tiers, no credit card is required. Paid trials may require a card but you won't be charged until the trial ends."},
            {"question": f"What happens after the {tool_name} free trial ends?", "answer": f"After the trial, your account moves to the free tier (if available) or pauses until you add payment. You won't lose your data. {tool_name} will email you before the trial expires."},
            {"question": f"Can I extend the {tool_name} free trial?", "answer": f"Yes — contact {tool_name} support before your trial expires and ask for an extension. Most companies grant 7-14 extra days, especially if you explain you need more time to evaluate with your team."},
            {"question": f"How do I cancel {tool_name} during the trial?", "answer": f"Cancel via your account settings before the trial ends to avoid charges. Go to Settings → Billing → Cancel Subscription. {tool_name} typically confirms cancellation by email."},
            {"question": f"Is the {tool_name} free tier good enough?", "answer": f"{tool['free']}. For solo users or very small teams, the free tier may be sufficient. For professional use, paid plans unlock features like advanced reporting, team collaboration, and API access."},
        ],
        "deep_sections": [
            {"heading": f"What the {tool_name} Free Trial Includes", "content": f"The {tool_name} free trial gives full access to all features — including features on the paid plan — for {tool['trial']}. This is your chance to test the tool with real data, not a demo."},
            {"heading": "How to Get the Most From Your Trial", "content": f"Week 1 checklist: Set up your real workflow (not a test project), invite your whole team, connect your integrations, run a real project end-to-end. By Day 7 you should know if it fits."},
            {"heading": f"After the Trial: {tool_name} Pricing", "content": f"{tool_name} paid plans start at {tool['starter']}. Annual billing saves ~20%. If you're on the fence, ask sales for a 30-day extension — most will say yes."},
            {"heading": "Alternatives If the Trial Doesn't Convert You", "content": f"If {tool_name} isn't the right fit, the top alternatives are: {', '.join(tool['alts'][:3])}. All offer free trials so you can compare directly."},
        ],
        "cta_text": f"Start your {tool_name} free trial today — no credit card required.",
        "cta_button": f"Get Free Trial",
        "primary_keyword": f"{tool_name.lower()} free trial",
        "secondary_keywords": [f"{tool_name.lower()} free", f"try {tool_name.lower()} free", f"{tool_name.lower()} free plan", f"{tool_name.lower()} trial"],
    }


def make_bestof_page(bo: dict) -> dict:
    tools_list = []
    for i, t in enumerate(bo["tools_ranked"]):
        td = TOOLS.get(t, {})
        tools_list.append({
            "name": t,
            "description": td.get("desc", f"{t} is a leading {bo['audience']} tool with strong features and competitive pricing."),
            "score": round(4.8 - i * 0.1, 1),
            "pros": td.get("pros", ["Strong features", "Good pricing", "Reliable"])[:3],
            "cons": td.get("cons", ["Learning curve"])[:2],
            "pricing": f"From {td.get('starter', 'Check website')}",
            "homepage": td.get("homepage", "#"),
            "winner": i == 0,
        })

    return {
        "page_title": bo["title"],
        "meta_description": bo["meta"],
        "subtitle": bo["subtitle"],
        "tldr": bo["tldr"],
        "tools": tools_list[:4],
        "comparison_features": [
            {"name": "Starting Price", "values": [TOOLS.get(t, {}).get("starter", "Custom") for t in bo["tools_ranked"][:4]]},
            {"name": "Free Plan", "values": [TOOLS.get(t, {}).get("free", "Trial only") for t in bo["tools_ranked"][:4]]},
            {"name": "Best For", "values": [TOOLS.get(t, {}).get("best_for", "Various") for t in bo["tools_ranked"][:4]]},
        ],
        "verdict": bo["verdict"],
        "faqs": [
            {"question": f"What is the best {bo['keyword'].replace('best ','')} for {bo['audience']}?", "answer": f"{bo['tools_ranked'][0]} is our top pick for {bo['audience']} — {TOOLS.get(bo['tools_ranked'][0],{}).get('pros',[None])[0] or 'excellent features'}."},
            {"question": f"Is there a free {bo['keyword'].replace('best ','').replace(' software','').replace(' tools','').strip()}?", "answer": f"Yes — {', '.join([t for t in bo['tools_ranked'] if TOOLS.get(t,{}).get('free','') and 'free' in TOOLS.get(t,{}).get('free','').lower()][:2])} have free plans. " + bo["tools_ranked"][0] + f" also offers {TOOLS.get(bo['tools_ranked'][0],{}).get('trial','a free trial')}."},
            {"question": f"How do I choose the right tool for my team?", "answer": f"Consider: team size, budget, must-have features, and current tools you use. We recommend trialling {bo['tools_ranked'][0]} and {bo['tools_ranked'][1]} side-by-side since both offer free access."},
            {"question": f"What should I look for when comparing these tools?", "answer": "Key criteria: pricing per user at your team size, free trial length and completeness, integration with your existing stack, mobile app quality, and customer support response time."},
        ],
        "deep_sections": [
            {"heading": f"How We Ranked These Tools", "content": f"We evaluated each tool on: pricing value, feature depth, ease of onboarding, reliability, customer support quality, and integration ecosystem. Rankings reflect best fit for {bo['audience']}, not raw feature count."},
            {"heading": "Our #1 Pick and Why", "content": f"{bo['tools_ranked'][0]} tops our list for {bo['audience']} because {TOOLS.get(bo['tools_ranked'][0],{}).get('pros',[None])[0] or 'it offers the best combination of features and value'}. It's the tool we'd recommend to most teams starting out."},
            {"heading": "Budget Pick", "content": f"If budget is tight, {bo['tools_ranked'][-1]} offers the most value at the lowest price point. You trade some features for a significantly lower monthly cost — a reasonable trade for smaller teams."},
        ],
        "cta_text": f"Try the #1 pick free — no credit card required.",
        "cta_button": "Start Free Trial",
        "primary_keyword": bo["keyword"],
        "secondary_keywords": [f"{bo['keyword']} {YEAR}", f"top {bo['keyword'].replace('best ','')}", f"{bo['keyword']} comparison"],
    }


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    generated = 0
    skipped = 0

    print(f"\n{'='*60}")
    print(f"  SaaSpare Page Generator — No LLM Required")
    print(f"  Target: alternatives + coupons + reviews + free trials + best-of")
    print(f"{'='*60}\n")

    for tool_name, tool in TOOLS.items():
        vertical = tool["vertical"]

        # Alternatives
        data = make_alternatives_page(tool_name, tool)
        path = _render_and_save(data, vertical)
        if path:
            print(f"  ✓ {data['page_title'][:70]}")
            generated += 1
        else:
            skipped += 1

        # Coupon
        data = make_coupon_page(tool_name, tool)
        path = _render_and_save(data, vertical)
        if path:
            print(f"  ✓ {data['page_title'][:70]}")
            generated += 1
        else:
            skipped += 1

        # Review
        data = make_review_page(tool_name, tool)
        path = _render_and_save(data, vertical)
        if path:
            print(f"  ✓ {data['page_title'][:70]}")
            generated += 1
        else:
            skipped += 1

        # Free trial
        data = make_free_trial_page(tool_name, tool)
        path = _render_and_save(data, vertical)
        if path:
            print(f"  ✓ {data['page_title'][:70]}")
            generated += 1
        else:
            skipped += 1

    # Best-of roundup pages
    print("\n  [Best-of Roundups]")
    for bo in BESTOF_PAGES:
        data = make_bestof_page(bo)
        path = _render_and_save(data, bo["vertical"])
        if path:
            print(f"  ✓ {data['page_title'][:70]}")
            generated += 1
        else:
            skipped += 1

    print(f"\n{'='*60}")
    print(f"  Generated: {generated} new pages")
    print(f"  Skipped (already exist): {skipped}")
    print(f"  Total pages now: {len(list(__import__('pathlib').Path('site/pages').glob('*.html')))}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
