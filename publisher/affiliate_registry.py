from slugify import slugify

PROGRAMS = {
    "devtools": [
        {"name": "GitHub Copilot", "homepage": "https://github.com/features/copilot",
         "affiliate_url": "https://github.com/features/copilot", "network": "direct",
         "commission": "flat $20/referral", "commission_pct": 0, "recurring": False},
        {"name": "JetBrains", "homepage": "https://www.jetbrains.com",
         "affiliate_url": "https://www.jetbrains.com/store/affiliate/", "network": "partnerstack",
         "commission": "25% recurring", "commission_pct": 25, "recurring": True, "avg_plan_usd": 25},
        {"name": "Linear", "homepage": "https://linear.app",
         "affiliate_url": "https://linear.app/affiliates", "network": "direct",
         "commission": "30% for 12 months", "commission_pct": 30, "recurring": True, "avg_plan_usd": 8},
        {"name": "Retool", "homepage": "https://retool.com",
         "affiliate_url": "https://retool.com/affiliates", "network": "partnerstack",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 50},
        {"name": "Datadog", "homepage": "https://www.datadoghq.com",
         "affiliate_url": "https://www.datadoghq.com/partner/", "network": "partnerstack",
         "commission": "20% for 12 months", "commission_pct": 20, "recurring": True, "avg_plan_usd": 120},
        {"name": "Sentry", "homepage": "https://sentry.io",
         "affiliate_url": "https://sentry.io/affiliates/", "network": "partnerstack",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 26},
    ],

    "saas_analytics": [
        {"name": "Amplitude", "homepage": "https://amplitude.com",
         "affiliate_url": "https://amplitude.com/partners", "network": "partnerstack",
         "commission": "25% recurring", "commission_pct": 25, "recurring": True, "avg_plan_usd": 100},
        {"name": "Mixpanel", "homepage": "https://mixpanel.com",
         "affiliate_url": "https://mixpanel.com/partners/", "network": "partnerstack",
         "commission": "20% for 12 months", "commission_pct": 20, "recurring": True, "avg_plan_usd": 79},
        {"name": "Databox", "homepage": "https://databox.com",
         "affiliate_url": "https://databox.com/affiliate-program", "network": "partnerstack",
         "commission": "20% recurring lifetime", "commission_pct": 20, "recurring": True, "avg_plan_usd": 59},
        {"name": "Hotjar", "homepage": "https://www.hotjar.com",
         "affiliate_url": "https://www.hotjar.com/affiliates/", "network": "partnerstack",
         "commission": "25% recurring", "commission_pct": 25, "recurring": True, "avg_plan_usd": 39},
        {"name": "FullStory", "homepage": "https://www.fullstory.com",
         "affiliate_url": "https://www.fullstory.com/partners/", "network": "partnerstack",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 300},
    ],

    "marketing_automation": [
        {"name": "HubSpot", "homepage": "https://www.hubspot.com",
         "affiliate_url": "https://www.hubspot.com/partners/affiliates", "network": "impact",
         "commission": "30% recurring for 12 months", "commission_pct": 30, "recurring": True, "avg_plan_usd": 50},
        {"name": "ActiveCampaign", "homepage": "https://www.activecampaign.com",
         "affiliate_url": "https://www.activecampaign.com/partner/affiliate", "network": "partnerstack",
         "commission": "30% recurring", "commission_pct": 30, "recurring": True, "avg_plan_usd": 49},
        {"name": "Mailchimp", "homepage": "https://mailchimp.com",
         "affiliate_url": "https://mailchimp.com/referral-program/", "network": "direct",
         "commission": "$30 per paid signup", "commission_pct": 0, "recurring": False, "avg_plan_usd": 30},
        {"name": "Lemlist", "homepage": "https://lemlist.com",
         "affiliate_url": "https://lemlist.com/affiliate", "network": "partnerstack",
         "commission": "25% recurring for 12 months", "commission_pct": 25, "recurring": True, "avg_plan_usd": 59},
        {"name": "Brevo", "homepage": "https://www.brevo.com",
         "affiliate_url": "https://www.brevo.com/partners/become-an-affiliate/", "network": "impact",
         "commission": "5 EUR free + 100 EUR paid", "commission_pct": 0, "recurring": False, "avg_plan_usd": 100},
        {"name": "Klaviyo", "homepage": "https://www.klaviyo.com",
         "affiliate_url": "https://www.klaviyo.com/partners/affiliate", "network": "partnerstack",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 100},
        {"name": "ConvertKit", "homepage": "https://convertkit.com",
         "affiliate_url": "https://convertkit.com/affiliates", "network": "partnerstack",
         "commission": "30% recurring for 24 months", "commission_pct": 30, "recurring": True, "avg_plan_usd": 29},
    ],

    "cloud_infra": [
        {"name": "DigitalOcean", "homepage": "https://www.digitalocean.com",
         "affiliate_url": "https://www.digitalocean.com/referral-program", "network": "impact",
         "commission": "$25 per new paying customer", "commission_pct": 0, "recurring": False, "avg_plan_usd": 25},
        {"name": "Vultr", "homepage": "https://www.vultr.com",
         "affiliate_url": "https://www.vultr.com/promo/affiliate/", "network": "impact",
         "commission": "35% of revenue for 12 months", "commission_pct": 35, "recurring": True, "avg_plan_usd": 40},
        {"name": "Hetzner", "homepage": "https://www.hetzner.com",
         "affiliate_url": "https://www.hetzner.com/legal/affiliate/", "network": "direct",
         "commission": "20 EUR per referral", "commission_pct": 0, "recurring": False},
        {"name": "Render", "homepage": "https://render.com",
         "affiliate_url": "https://render.com/affiliates", "network": "partnerstack",
         "commission": "20% recurring for 12 months", "commission_pct": 20, "recurring": True, "avg_plan_usd": 25},
        {"name": "Supabase", "homepage": "https://supabase.com",
         "affiliate_url": "https://supabase.com/affiliates", "network": "partnerstack",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 25},
    ],

    "cybersecurity": [
        {"name": "NordLayer", "homepage": "https://nordlayer.com",
         "affiliate_url": "https://nordlayer.com/affiliates/", "network": "impact",
         "commission": "30% per sale", "commission_pct": 30, "recurring": False, "avg_plan_usd": 99},
        {"name": "1Password Business", "homepage": "https://1password.com",
         "affiliate_url": "https://1password.com/partners/", "network": "partnerstack",
         "commission": "25% recurring", "commission_pct": 25, "recurring": True, "avg_plan_usd": 7.99},
        {"name": "Snyk", "homepage": "https://snyk.io",
         "affiliate_url": "https://snyk.io/partners/", "network": "partnerstack",
         "commission": "20% for 12 months", "commission_pct": 20, "recurring": True, "avg_plan_usd": 98},
        {"name": "CrowdStrike", "homepage": "https://www.crowdstrike.com",
         "affiliate_url": "https://www.crowdstrike.com/partners/", "network": "partnerstack",
         "commission": "10% per sale", "commission_pct": 10, "recurring": False, "avg_plan_usd": 299},
        {"name": "Malwarebytes", "homepage": "https://www.malwarebytes.com",
         "affiliate_url": "https://www.malwarebytes.com/business/partner", "network": "impact",
         "commission": "up to 30%", "commission_pct": 30, "recurring": False, "avg_plan_usd": 60},
    ],

    "hr_recruiting": [
        {"name": "BambooHR", "homepage": "https://www.bamboohr.com",
         "affiliate_url": "https://www.bamboohr.com/partners/", "network": "partnerstack",
         "commission": "20% for 12 months", "commission_pct": 20, "recurring": True, "avg_plan_usd": 99},
        {"name": "Rippling", "homepage": "https://www.rippling.com",
         "affiliate_url": "https://www.rippling.com/partners", "network": "partnerstack",
         "commission": "flat fee per hire", "commission_pct": 0, "recurring": False},
        {"name": "Workable", "homepage": "https://www.workable.com",
         "affiliate_url": "https://www.workable.com/partners", "network": "partnerstack",
         "commission": "20% for 12 months", "commission_pct": 20, "recurring": True, "avg_plan_usd": 189},
        {"name": "Deel", "homepage": "https://www.deel.com",
         "affiliate_url": "https://www.deel.com/partners", "network": "partnerstack",
         "commission": "$500 per customer", "commission_pct": 0, "recurring": False, "avg_plan_usd": 500},
        {"name": "Gusto", "homepage": "https://gusto.com",
         "affiliate_url": "https://gusto.com/refer-a-business", "network": "direct",
         "commission": "$300 per referral", "commission_pct": 0, "recurring": False, "avg_plan_usd": 300},
    ],

    "ecommerce_tools": [
        {"name": "Shopify", "homepage": "https://www.shopify.com",
         "affiliate_url": "https://www.shopify.com/affiliates", "network": "impact",
         "commission": "$150 per merchant referral", "commission_pct": 0, "recurring": False, "avg_plan_usd": 150},
        {"name": "BigCommerce", "homepage": "https://www.bigcommerce.com",
         "affiliate_url": "https://www.bigcommerce.com/partners/affiliates/", "network": "impact",
         "commission": "200% of first month (up to $1500)", "commission_pct": 200, "recurring": False, "avg_plan_usd": 79},
        {"name": "Gumroad", "homepage": "https://gumroad.com",
         "affiliate_url": "https://gumroad.com/affiliates", "network": "direct",
         "commission": "10% of referral sales", "commission_pct": 10, "recurring": True, "avg_plan_usd": 50},
        {"name": "Chargebee", "homepage": "https://www.chargebee.com",
         "affiliate_url": "https://www.chargebee.com/partners/", "network": "partnerstack",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 249},
    ],

    "legal_compliance": [
        {"name": "DocuSign", "homepage": "https://www.docusign.com",
         "affiliate_url": "https://www.docusign.com/partners/affiliate", "network": "impact",
         "commission": "20% per sale", "commission_pct": 20, "recurring": False, "avg_plan_usd": 45},
        {"name": "PandaDoc", "homepage": "https://www.pandadoc.com",
         "affiliate_url": "https://www.pandadoc.com/partners/affiliate-program/", "network": "partnerstack",
         "commission": "35% recurring for 12 months", "commission_pct": 35, "recurring": True, "avg_plan_usd": 49},
        {"name": "Ironclad", "homepage": "https://ironcladapp.com",
         "affiliate_url": "https://ironcladapp.com/partners/", "network": "partnerstack",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 250},
        {"name": "Contractbook", "homepage": "https://contractbook.com",
         "affiliate_url": "https://contractbook.com/affiliate", "network": "partnerstack",
         "commission": "30% recurring", "commission_pct": 30, "recurring": True, "avg_plan_usd": 79},
    ],

    "finance_ops": [
        {"name": "FreshBooks", "homepage": "https://www.freshbooks.com",
         "affiliate_url": "https://www.freshbooks.com/partners/affiliate", "network": "shareasale",
         "commission": "$10 trial + $200 paid", "commission_pct": 0, "recurring": False, "avg_plan_usd": 200},
        {"name": "Brex", "homepage": "https://www.brex.com",
         "affiliate_url": "https://www.brex.com/referral", "network": "direct",
         "commission": "$250 per approved account", "commission_pct": 0, "recurring": False, "avg_plan_usd": 250},
        {"name": "Ramp", "homepage": "https://ramp.com",
         "affiliate_url": "https://ramp.com/partners", "network": "direct",
         "commission": "$500 per referral", "commission_pct": 0, "recurring": False, "avg_plan_usd": 500},
        {"name": "Expensify", "homepage": "https://www.expensify.com",
         "affiliate_url": "https://use.expensify.com/accountants", "network": "direct",
         "commission": "0.5% of referred spend", "commission_pct": 0, "recurring": True, "avg_plan_usd": 36},
        {"name": "Xero", "homepage": "https://www.xero.com",
         "affiliate_url": "https://www.xero.com/partners/become-a-partner/", "network": "partnerstack",
         "commission": "30% recurring for 12 months", "commission_pct": 30, "recurring": True, "avg_plan_usd": 65},
    ],

    "ai_ml_tools": [
        {"name": "Jasper AI", "homepage": "https://www.jasper.ai",
         "affiliate_url": "https://www.jasper.ai/affiliates", "network": "partnerstack",
         "commission": "30% recurring", "commission_pct": 30, "recurring": True, "avg_plan_usd": 49},
        {"name": "Copy.ai", "homepage": "https://www.copy.ai",
         "affiliate_url": "https://www.copy.ai/affiliates", "network": "partnerstack",
         "commission": "45% for 12 months", "commission_pct": 45, "recurring": True, "avg_plan_usd": 49},
        {"name": "Writesonic", "homepage": "https://writesonic.com",
         "affiliate_url": "https://writesonic.com/affiliates", "network": "partnerstack",
         "commission": "30% recurring", "commission_pct": 30, "recurring": True, "avg_plan_usd": 19},
        {"name": "Pinecone", "homepage": "https://www.pinecone.io",
         "affiliate_url": "https://www.pinecone.io/partners/", "network": "partnerstack",
         "commission": "20% for 12 months", "commission_pct": 20, "recurring": True, "avg_plan_usd": 70},
    ],

    "project_management": [
        {"name": "Asana", "homepage": "https://asana.com",
         "affiliate_url": "https://asana.com/partners", "network": "partnerstack",
         "commission": "10% per referral", "commission_pct": 10, "recurring": False, "avg_plan_usd": 130},
        {"name": "Monday.com", "homepage": "https://monday.com",
         "affiliate_url": "https://monday.com/affiliates", "network": "impact",
         "commission": "$200 CPA", "commission_pct": 0, "recurring": False, "avg_plan_usd": 200},
        {"name": "ClickUp", "homepage": "https://clickup.com",
         "affiliate_url": "https://clickup.com/affiliates", "network": "partnerstack",
         "commission": "20% recurring for 12 months", "commission_pct": 20, "recurring": True, "avg_plan_usd": 12},
        {"name": "Notion", "homepage": "https://www.notion.so",
         "affiliate_url": "https://www.notion.so/affiliates", "network": "partnerstack",
         "commission": "50% for first year", "commission_pct": 50, "recurring": True, "avg_plan_usd": 16},
        {"name": "Wrike", "homepage": "https://www.wrike.com",
         "affiliate_url": "https://www.wrike.com/partners/affiliate-program/", "network": "partnerstack",
         "commission": "20% per sale", "commission_pct": 20, "recurring": False, "avg_plan_usd": 130},
        {"name": "Smartsheet", "homepage": "https://www.smartsheet.com",
         "affiliate_url": "https://www.smartsheet.com/partners", "network": "partnerstack",
         "commission": "20% per sale", "commission_pct": 20, "recurring": False, "avg_plan_usd": 200},
    ],

    "crm": [
        {"name": "Pipedrive", "homepage": "https://www.pipedrive.com",
         "affiliate_url": "https://www.pipedrive.com/en/partners/affiliate", "network": "partnerstack",
         "commission": "20% recurring for 12 months", "commission_pct": 20, "recurring": True, "avg_plan_usd": 49},
        {"name": "Zoho CRM", "homepage": "https://www.zoho.com/crm/",
         "affiliate_url": "https://www.zoho.com/affiliates.html", "network": "direct",
         "commission": "15% per sale", "commission_pct": 15, "recurring": False, "avg_plan_usd": 50},
        {"name": "Close", "homepage": "https://close.com",
         "affiliate_url": "https://close.com/affiliates/", "network": "partnerstack",
         "commission": "25% recurring for 12 months", "commission_pct": 25, "recurring": True, "avg_plan_usd": 99},
        {"name": "Freshsales", "homepage": "https://www.freshworks.com/crm/sales/",
         "affiliate_url": "https://www.freshworks.com/partners/affiliate/", "network": "partnerstack",
         "commission": "15% per sale", "commission_pct": 15, "recurring": False, "avg_plan_usd": 71},
        {"name": "Copper", "homepage": "https://www.copper.com",
         "affiliate_url": "https://www.copper.com/partners", "network": "partnerstack",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 59},
        {"name": "Keap", "homepage": "https://keap.com",
         "affiliate_url": "https://keap.com/partners/affiliate", "network": "partnerstack",
         "commission": "20% recurring for 12 months", "commission_pct": 20, "recurring": True, "avg_plan_usd": 199},
    ],

    "password_managers": [
        {"name": "1Password", "homepage": "https://1password.com",
         "affiliate_url": "https://1password.com/partners/", "network": "partnerstack",
         "commission": "25% recurring", "commission_pct": 25, "recurring": True, "avg_plan_usd": 7.99},
        {"name": "LastPass", "homepage": "https://www.lastpass.com",
         "affiliate_url": "https://www.lastpass.com/partners", "network": "partnerstack",
         "commission": "20% per sale", "commission_pct": 20, "recurring": False, "avg_plan_usd": 48},
        {"name": "Dashlane", "homepage": "https://www.dashlane.com",
         "affiliate_url": "https://www.dashlane.com/business/partners", "network": "partnerstack",
         "commission": "20% per sale", "commission_pct": 20, "recurring": False, "avg_plan_usd": 60},
        {"name": "Keeper", "homepage": "https://www.keepersecurity.com",
         "affiliate_url": "https://www.keepersecurity.com/affiliates.html", "network": "impact",
         "commission": "20% per sale", "commission_pct": 20, "recurring": False, "avg_plan_usd": 45},
        {"name": "NordPass", "homepage": "https://nordpass.com",
         "affiliate_url": "https://nordpass.com/affiliates/", "network": "impact",
         "commission": "30% per sale", "commission_pct": 30, "recurring": False, "avg_plan_usd": 35},
    ],

    "video_conferencing": [
        {"name": "Zoom", "homepage": "https://zoom.us",
         "affiliate_url": "https://zoom.us/partners/affiliate", "network": "partnerstack",
         "commission": "Referral credits", "commission_pct": 0, "recurring": False, "avg_plan_usd": 150},
        {"name": "Loom", "homepage": "https://www.loom.com",
         "affiliate_url": "https://www.loom.com/affiliates", "network": "partnerstack",
         "commission": "15% recurring for 12 months", "commission_pct": 15, "recurring": True, "avg_plan_usd": 12.50},
        {"name": "Riverside.fm", "homepage": "https://riverside.fm",
         "affiliate_url": "https://riverside.fm/affiliates", "network": "partnerstack",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 24},
        {"name": "Whereby", "homepage": "https://whereby.com",
         "affiliate_url": "https://whereby.com/partners/affiliates/", "network": "partnerstack",
         "commission": "20% per upgrade", "commission_pct": 20, "recurring": False, "avg_plan_usd": 59},
    ],

    "vpn_business": [
        {"name": "NordLayer", "homepage": "https://nordlayer.com",
         "affiliate_url": "https://nordlayer.com/affiliates/", "network": "impact",
         "commission": "30% per sale", "commission_pct": 30, "recurring": False, "avg_plan_usd": 99},
        {"name": "Perimeter 81", "homepage": "https://www.perimeter81.com",
         "affiliate_url": "https://www.perimeter81.com/partners", "network": "partnerstack",
         "commission": "20% per sale", "commission_pct": 20, "recurring": False, "avg_plan_usd": 299},
        {"name": "Twingate", "homepage": "https://www.twingate.com",
         "affiliate_url": "https://www.twingate.com/partners", "network": "partnerstack",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 10},
        {"name": "ExpressVPN Business", "homepage": "https://www.expressvpn.com",
         "affiliate_url": "https://www.expressvpn.com/affiliates", "network": "impact",
         "commission": "$13–36 per sale", "commission_pct": 0, "recurring": False, "avg_plan_usd": 25},
    ],
}

_ALL_AFFILIATE_URLS: dict[str, str] = {
    slugify(p["name"]): p["affiliate_url"]
    for programs in PROGRAMS.values()
    for p in programs
}


def get_go_url(tool_name: str) -> str | None:
    s = slugify(tool_name)
    if s in _ALL_AFFILIATE_URLS:
        return f"/go/{s}"
    return None


def get_all_redirects() -> dict[str, str]:
    return dict(_ALL_AFFILIATE_URLS)


def get_links_for_vertical(vertical: str, tool_names: list[str]) -> dict[str, str]:
    programs = PROGRAMS.get(vertical, [])
    result = {}
    for tool in tool_names:
        tool_lower = tool.lower()
        for prog in programs:
            if prog["name"].lower() in tool_lower or tool_lower in prog["name"].lower():
                result[tool] = prog["affiliate_url"]
                break
        if tool not in result:
            result[tool] = f"https://www.google.com/search?q={tool.replace(' ', '+')}+pricing"
    return result


def get_best_programs_for_vertical(vertical: str, top_n: int = 3) -> list[dict]:
    programs = PROGRAMS.get(vertical, [])
    def score(p):
        pct = p.get("commission_pct", 0)
        avg = p.get("avg_plan_usd", 30)
        recurring = 12 if p.get("recurring") else 1
        return (pct / 100) * avg * recurring
    return sorted(programs, key=score, reverse=True)[:top_n]


def estimate_monthly_revenue(vertical: str, monthly_visitors: int,
                              conversion_rate: float = 0.025) -> dict:
    programs = get_best_programs_for_vertical(vertical, top_n=1)
    if not programs:
        return {"monthly_est": 0}
    prog = programs[0]
    conversions = int(monthly_visitors * conversion_rate)
    pct = prog.get("commission_pct", 0) / 100
    avg = prog.get("avg_plan_usd", 30)
    recurring_months = 12 if prog.get("recurring") else 1
    monthly_est = conversions * pct * avg * (recurring_months / 12)
    return {
        "program": prog["name"],
        "commission": prog["commission"],
        "conversions_est": conversions,
        "monthly_est": round(monthly_est, 2),
        "yearly_est": round(monthly_est * 12, 2),
    }
