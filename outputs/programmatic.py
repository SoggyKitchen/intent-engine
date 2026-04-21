"""
Programmatic SEO — generates all page types for all known tool combinations.
7 page types x 16 verticals x ~90 pairs each = 6000+ pages/month potential.
Uses ThreadPoolExecutor(5) to run 5 LLM providers in parallel.
"""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import combinations
from pathlib import Path

from core.db import db
from core.logger import log
from llm.router import complete_json
from outputs.seo_page import _render_and_save
from core.secrets import get
from publisher.affiliate_registry import get_all_redirects

TOOLS_BY_VERTICAL = {
    "devtools": [
        "GitHub Copilot", "JetBrains", "Linear", "Retool", "Vercel",
        "Netlify", "Sentry", "Datadog", "PagerDuty", "Terraform",
    ],
    "saas_analytics": [
        "Amplitude", "Mixpanel", "Databox", "Tableau", "Looker",
        "Power BI", "Heap", "FullStory", "Hotjar", "Segment",
    ],
    "marketing_automation": [
        "HubSpot", "ActiveCampaign", "Mailchimp", "Lemlist", "Brevo",
        "Klaviyo", "Marketo", "Pardot", "ConvertKit", "Drip",
    ],
    "cloud_infra": [
        "AWS", "DigitalOcean", "Vultr", "Hetzner", "Render",
        "Supabase", "Railway", "Fly.io", "Linode", "Google Cloud",
    ],
    "cybersecurity": [
        "NordLayer", "1Password Business", "Okta", "CrowdStrike", "Snyk",
        "Cloudflare", "Qualys", "Tenable", "SentinelOne", "Duo Security",
    ],
    "hr_recruiting": [
        "BambooHR", "Rippling", "Workable", "Greenhouse", "Lever",
        "Gusto", "Deel", "Remote.com", "Lattice", "Culture Amp",
    ],
    "ecommerce_tools": [
        "Shopify", "BigCommerce", "WooCommerce", "Gumroad", "Paddle",
        "Stripe", "Chargebee", "Recurly", "Recharge", "Bold Commerce",
    ],
    "ai_ml_tools": [
        "Jasper AI", "Copy.ai", "Writesonic", "Pinecone", "Weaviate",
        "OpenAI API", "Anthropic Claude", "Cohere", "Hugging Face", "Weights & Biases",
    ],
    "legal_compliance": [
        "DocuSign", "PandaDoc", "Ironclad", "Contractbook", "Docusign CLM",
        "Juro", "Concord", "Conga", "Agiloft", "Icertis",
    ],
    "finance_ops": [
        "FreshBooks", "Xero", "Expensify", "Ramp", "Brex",
        "QuickBooks", "Netsuite", "Sage", "Airbase", "Divvy",
    ],
    "project_management": [
        "Asana", "Monday.com", "ClickUp", "Notion", "Jira",
        "Trello", "Basecamp", "Wrike", "Smartsheet", "Todoist",
    ],
    "crm": [
        "Salesforce", "HubSpot CRM", "Pipedrive", "Zoho CRM", "Close",
        "Freshsales", "Copper", "Keap", "Nutshell", "Insightly",
    ],
    "password_managers": [
        "1Password", "LastPass", "Bitwarden", "Dashlane", "Keeper",
        "NordPass", "RoboForm", "Sticky Password", "Enpass", "Password Boss",
    ],
    "video_conferencing": [
        "Zoom", "Microsoft Teams", "Google Meet", "Webex", "Whereby",
        "Around", "Loom", "Riverside.fm", "StreamYard", "Descript",
    ],
    "vpn_business": [
        "NordLayer", "Perimeter 81", "Cisco AnyConnect", "ExpressVPN Business",
        "Twingate", "Cloudflare Access", "Tailscale", "WireGuard", "Zscaler", "OpenVPN",
    ],
    "seo_tools": [
        "Ahrefs", "Semrush", "Moz Pro", "Surfer SEO", "SE Ranking", "Mangools",
        "SpyFu", "Clearscope", "Frase.io", "Rankmath Pro",
    ],
}

ALTERNATIVE_TARGETS = {
    "marketing_automation": ["HubSpot", "Salesforce", "Marketo", "Mailchimp"],
    "cloud_infra": ["AWS", "Heroku", "Google Cloud"],
    "hr_recruiting": ["BambooHR", "Workday", "ADP"],
    "ecommerce_tools": ["Shopify", "BigCommerce", "WooCommerce"],
    "finance_ops": ["QuickBooks", "Xero", "FreshBooks"],
    "devtools": ["GitHub Copilot", "Jira", "Datadog"],
    "saas_analytics": ["Tableau", "Power BI", "Google Analytics"],
    "cybersecurity": ["Okta", "CrowdStrike", "Splunk"],
    "project_management": ["Asana", "Monday.com", "Jira", "ClickUp"],
    "crm": ["Salesforce", "HubSpot CRM", "Zoho CRM"],
    "password_managers": ["LastPass", "1Password", "Dashlane"],
    "video_conferencing": ["Zoom", "Microsoft Teams", "Google Meet"],
    "vpn_business": ["NordLayer", "Cisco AnyConnect", "Perimeter 81"],
    "seo_tools": ["Semrush", "Ahrefs", "Moz Pro", "Surfer SEO"],
}

HIGH_VALUE_PRICING_TARGETS = [
    ("HubSpot", "marketing_automation"),
    ("Salesforce", "crm"),
    ("ActiveCampaign", "marketing_automation"),
    ("Shopify", "ecommerce_tools"),
    ("BigCommerce", "ecommerce_tools"),
    ("BambooHR", "hr_recruiting"),
    ("Rippling", "hr_recruiting"),
    ("Workable", "hr_recruiting"),
    ("DigitalOcean", "cloud_infra"),
    ("Vultr", "cloud_infra"),
    ("Amplitude", "saas_analytics"),
    ("Mixpanel", "saas_analytics"),
    ("Linear", "devtools"),
    ("Datadog", "devtools"),
    ("PandaDoc", "legal_compliance"),
    ("DocuSign", "legal_compliance"),
    ("Xero", "finance_ops"),
    ("FreshBooks", "finance_ops"),
    ("Ramp", "finance_ops"),
    ("Jasper AI", "ai_ml_tools"),
    ("Copy.ai", "ai_ml_tools"),
    ("Asana", "project_management"),
    ("Monday.com", "project_management"),
    ("ClickUp", "project_management"),
    ("Notion", "project_management"),
    ("Pipedrive", "crm"),
    ("Zoom", "video_conferencing"),
    ("1Password", "password_managers"),
    ("NordLayer", "vpn_business"),
    ("Deel", "hr_recruiting"),
    ("Gusto", "hr_recruiting"),
    ("Ahrefs", "seo_tools"),
    ("Semrush", "seo_tools"),
    ("Surfer SEO", "seo_tools"),
    ("Clearscope", "seo_tools"),
    ("Moz Pro", "seo_tools"),
    ("SE Ranking", "seo_tools"),
]

BEST_OF_QUERIES = [
    ("marketing_automation", "small business", ["HubSpot", "ActiveCampaign", "Brevo", "Mailchimp", "ConvertKit"]),
    ("marketing_automation", "ecommerce", ["Klaviyo", "Mailchimp", "ActiveCampaign", "Drip", "Brevo"]),
    ("cloud_infra", "startups", ["Render", "Railway", "DigitalOcean", "Supabase", "Fly.io"]),
    ("cloud_infra", "enterprise", ["AWS", "Google Cloud", "DigitalOcean", "Vultr", "Hetzner"]),
    ("devtools", "startups", ["Linear", "GitHub Copilot", "Vercel", "Sentry", "Retool"]),
    ("saas_analytics", "small business", ["Databox", "Hotjar", "Mixpanel", "Heap", "Segment"]),
    ("hr_recruiting", "startups", ["Rippling", "Gusto", "Deel", "Remote.com", "BambooHR"]),
    ("hr_recruiting", "enterprise", ["Workday", "Greenhouse", "Lattice", "Culture Amp", "Lever"]),
    ("finance_ops", "small business", ["FreshBooks", "Xero", "QuickBooks", "Wave", "Zoho Books"]),
    ("ecommerce_tools", "small business", ["Shopify", "WooCommerce", "Gumroad", "Paddle", "Stripe"]),
    ("cybersecurity", "small business", ["1Password Business", "NordLayer", "Cloudflare", "Snyk", "Duo Security"]),
    ("ai_ml_tools", "content teams", ["Jasper AI", "Copy.ai", "Writesonic", "Notion AI", "Grammarly"]),
    ("legal_compliance", "startups", ["PandaDoc", "DocuSign", "Contractbook", "Juro", "HelloSign"]),
    ("finance_ops", "B2B SaaS", ["Ramp", "Brex", "Airbase", "Divvy", "Expensify"]),
    ("project_management", "remote teams", ["Notion", "ClickUp", "Asana", "Monday.com", "Basecamp"]),
    ("project_management", "startups", ["Linear", "Notion", "Trello", "ClickUp", "Todoist"]),
    ("crm", "small business", ["HubSpot CRM", "Pipedrive", "Zoho CRM", "Close", "Freshsales"]),
    ("crm", "B2B SaaS", ["Salesforce", "HubSpot CRM", "Close", "Pipedrive", "Keap"]),
    ("password_managers", "business", ["1Password", "LastPass", "Bitwarden", "Dashlane", "Keeper"]),
    ("video_conferencing", "remote teams", ["Zoom", "Google Meet", "Microsoft Teams", "Whereby", "Loom"]),
    ("vpn_business", "startups", ["NordLayer", "Twingate", "Cloudflare Access", "Perimeter 81", "Tailscale"]),
    ("seo_tools", "small business", ["Mangools", "SE Ranking", "SpyFu", "Surfer SEO", "Frase.io"]),
    ("seo_tools", "enterprise", ["Semrush", "Moz Pro", "Clearscope", "Surfer SEO", "SE Ranking"]),
    ("seo_tools", "content teams", ["Surfer SEO", "Clearscope", "Frase.io", "Semrush", "Rankmath Pro"]),
    ("seo_tools", "bloggers", ["Rankmath Pro", "Surfer SEO", "Frase.io", "Mangools", "SE Ranking"]),
    ("seo_tools", "agencies", ["Semrush", "Moz Pro", "SE Ranking", "SpyFu", "Screaming Frog"]),
]

HIGH_VALUE_COUPON_TARGETS = [
    ("HubSpot", "marketing_automation"),
    ("Shopify", "ecommerce_tools"),
    ("Monday.com", "project_management"),
    ("Asana", "project_management"),
    ("ClickUp", "project_management"),
    ("Notion", "project_management"),
    ("Pipedrive", "crm"),
    ("ActiveCampaign", "marketing_automation"),
    ("Jasper AI", "ai_ml_tools"),
    ("Copy.ai", "ai_ml_tools"),
    ("NordLayer", "vpn_business"),
    ("1Password", "password_managers"),
    ("Datadog", "devtools"),
    ("BambooHR", "hr_recruiting"),
    ("DocuSign", "legal_compliance"),
    ("PandaDoc", "legal_compliance"),
    ("Xero", "finance_ops"),
    ("Zoom", "video_conferencing"),
    ("Deel", "hr_recruiting"),
    ("Rippling", "hr_recruiting"),
    ("Ahrefs", "seo_tools"),
    ("Semrush", "seo_tools"),
    ("Surfer SEO", "seo_tools"),
]

HIGH_VALUE_REVIEW_TARGETS = [
    ("HubSpot", "marketing_automation"),
    ("Shopify", "ecommerce_tools"),
    ("Monday.com", "project_management"),
    ("Asana", "project_management"),
    ("ClickUp", "project_management"),
    ("Notion", "project_management"),
    ("Salesforce", "crm"),
    ("Pipedrive", "crm"),
    ("Zoom", "video_conferencing"),
    ("1Password", "password_managers"),
    ("NordLayer", "vpn_business"),
    ("Datadog", "devtools"),
    ("BambooHR", "hr_recruiting"),
    ("Deel", "hr_recruiting"),
    ("Xero", "finance_ops"),
    ("Ramp", "finance_ops"),
    ("Jasper AI", "ai_ml_tools"),
    ("ActiveCampaign", "marketing_automation"),
    ("DocuSign", "legal_compliance"),
    ("Amplitude", "saas_analytics"),
    ("Ahrefs", "seo_tools"),
    ("Semrush", "seo_tools"),
    ("Surfer SEO", "seo_tools"),
    ("Moz Pro", "seo_tools"),
]

FREE_PLAN_TARGETS = [
    ("HubSpot", "marketing_automation"),
    ("Notion", "project_management"),
    ("ClickUp", "project_management"),
    ("Trello", "project_management"),
    ("Zoom", "video_conferencing"),
    ("Bitwarden", "password_managers"),
    ("Asana", "project_management"),
    ("Brevo", "marketing_automation"),
    ("Supabase", "cloud_infra"),
    ("Sentry", "devtools"),
    ("Hotjar", "saas_analytics"),
    ("Amplitude", "saas_analytics"),
    ("Pipedrive", "crm"),
    ("HubSpot CRM", "crm"),
    ("Freshsales", "crm"),
    ("Monday.com", "project_management"),
    ("Loom", "video_conferencing"),
    ("Cloudflare Access", "vpn_business"),
    ("Snyk", "cybersecurity"),
    ("Linear", "devtools"),
    ("Ubersuggest", "seo_tools"),
    ("SE Ranking", "seo_tools"),
    ("Mangools", "seo_tools"),
]


VERTICAL_PRIORITY = {
    "seo_tools": 1,
    "finance_ops": 2,
    "hr_recruiting": 3,
    "ai_ml_tools": 4,
    "legal_compliance": 5,
    "marketing_automation": 6,
    "crm": 7,
    "devtools": 8,
    "saas_analytics": 9,
    "project_management": 10,
    "ecommerce_tools": 11,
    "cybersecurity": 12,
    "cloud_infra": 13,
    "password_managers": 14,
    "video_conferencing": 15,
    "vpn_business": 16,
}

PAGE_TYPE_PRIORITY = {
    "_generate_pricing_page": 1,
    "_generate_comparison_page": 2,
    "_generate_review_page": 3,
    "_generate_alternatives_page": 4,
    "_generate_coupon_page": 5,
    "_generate_free_plan_page": 6,
    "_generate_bestof_page": 7,
}


def _task_priority(task: tuple) -> tuple:
    fn, args = task
    page_p = PAGE_TYPE_PRIORITY.get(fn.__name__, 99)
    if fn.__name__ == "_generate_comparison_page":
        vertical = args[2]
    elif fn.__name__ == "_generate_bestof_page":
        vertical = args[0]
    elif len(args) > 1:
        vertical = args[1]
    else:
        vertical = ""
    vert_p = VERTICAL_PRIORITY.get(vertical, 99)
    return (page_p, vert_p)


def _already_generated(slug_hint: str) -> bool:
    try:
        with db() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM outputs WHERE title LIKE ?",
                (f"%{slug_hint}%",)
            ).fetchone()
        if row[0] > 0:
            return True
    except Exception:
        pass
    try:
        pages_dir = Path("site/pages")
        if pages_dir.exists():
            words = [w.lower() for w in slug_hint.split() if len(w) > 1]
            for f in pages_dir.glob("*.html"):
                name = f.stem.lower()
                if all(w in name for w in words):
                    return True
    except Exception:
        pass
    return False


def _generate_comparison_page(tool_a: str, tool_b: str, vertical: str) -> bool:
    if _already_generated(f"{tool_a} vs {tool_b}"):
        return False

    prompt = f"""You are an expert B2B software analyst writing for buyers.

Write a detailed comparison of {tool_a} vs {tool_b} for {vertical.replace('_',' ')} buyers.

Return JSON exactly:
{{
  "page_title": "{tool_a} vs {tool_b}: Which is Better in {time.strftime('%Y')}?",
  "meta_description": "Detailed {tool_a} vs {tool_b} comparison. Pricing, features, pros, cons and which to choose.",
  "subtitle": "An unbiased, data-driven comparison for {vertical.replace('_',' ')} teams",
  "tldr": "<2 sentences: who should pick each tool>",
  "tools": [
    {{
      "name": "{tool_a}",
      "description": "<2-3 sentence accurate description>",
      "score": <4.0-5.0>,
      "logo_url": "https://saaspare.org/assets/logos/<tool-slug>.png",
      "logo_bg": "<brand hex color e.g. #FF5500>",
      "pros": ["<pro1>", "<pro2>", "<pro3>"],
      "cons": ["<con1>", "<con2>"],
      "pricing": "<real pricing tier summary>",
      "homepage": "<official URL>",
      "winner": true
    }},
    {{
      "name": "{tool_b}",
      "description": "<2-3 sentence accurate description>",
      "score": <3.0-4.5>,
      "logo_url": "https://saaspare.org/assets/logos/<tool-slug>.png",
      "logo_bg": "<brand hex color>",
      "pros": ["<pro1>", "<pro2>", "<pro3>"],
      "cons": ["<con1>", "<con2>"],
      "pricing": "<real pricing tier summary>",
      "homepage": "<official URL>",
      "winner": false
    }}
  ],
  "comparison_features": [
    {{"name": "Pricing", "values": ["<a price>", "<b price>"]}},
    {{"name": "Free Trial", "values": ["<yes/no>", "<yes/no>"]}},
    {{"name": "Best For", "values": ["<a use case>", "<b use case>"]}},
    {{"name": "Integrations", "values": ["<a count>", "<b count>"]}},
    {{"name": "Support", "values": ["<a support>", "<b support>"]}}
  ],
  "verdict": "<3 sentences: clear recommendation based on company size/use case>",
  "faqs": [
    {{"question": "Is {tool_a} better than {tool_b}?", "answer": "<balanced answer>"}},
    {{"question": "Which is cheaper, {tool_a} or {tool_b}?", "answer": "<pricing comparison>"}},
    {{"question": "Can I switch from {tool_b} to {tool_a}?", "answer": "<migration answer>"}}
  ],
  "cta_text": "Ready to try the winner? Start with a free trial and see the difference yourself.",
  "cta_button": "Start Free Trial",
  "primary_keyword": "{tool_a} vs {tool_b}",
  "secondary_keywords": ["{tool_a} alternative", "{tool_b} alternative", "best {vertical.replace('_',' ')} software"]
}}"""

    result = complete_json(prompt)
    if not result:
        return False
    return bool(_render_and_save(result, vertical))


def _generate_alternatives_page(target_tool: str, vertical: str) -> bool:
    if _already_generated(f"alternatives to {target_tool}"):
        return False

    programs = TOOLS_BY_VERTICAL.get(vertical, [])
    alternatives = [t for t in programs if t != target_tool][:5]
    alt_list = ", ".join(alternatives)

    prompt = f"""You are an expert B2B software analyst writing for buyers who want to leave {target_tool}.

Write a "Best Alternatives to {target_tool}" page for {vertical.replace('_',' ')} buyers.
Top alternatives to cover: {alt_list}

Return JSON exactly:
{{
  "page_title": "7 Best {target_tool} Alternatives in {time.strftime('%Y')} (Free & Paid)",
  "meta_description": "Looking for {target_tool} alternatives? Top options reviewed by price, features and migration ease.",
  "subtitle": "The best {target_tool} alternatives ranked by value, features and migration ease",
  "tldr": "If you're tired of {target_tool}, here are the top alternatives worth trying in {time.strftime('%Y')}.",
  "tools": [
    {{
      "name": "<alternative name>",
      "description": "<why it beats {target_tool} for certain buyers>",
      "score": <4.0-5.0>,
      "logo_url": "https://saaspare.org/assets/logos/<tool-slug>.png",
      "logo_bg": "<brand hex color e.g. #FF5500>",
      "pros": ["<pro1>", "<pro2>", "<pro3>"],
      "cons": ["<con1>", "<con2>"],
      "pricing": "<starting price>",
      "homepage": "<official URL>",
      "winner": true
    }}
  ],
  "comparison_features": [
    {{"name": "Price vs {target_tool}", "values": ["<cheaper/same/expensive>"]}},
    {{"name": "Migration Difficulty", "values": ["<easy/medium/hard>"]}},
    {{"name": "Best For", "values": ["<use case>"]}}
  ],
  "verdict": "The best {target_tool} alternative depends on your budget and team size. Our top pick is the first option above for most businesses.",
  "faqs": [
    {{"question": "What is the best free alternative to {target_tool}?", "answer": "<specific tool>"}},
    {{"question": "Why are people switching from {target_tool}?", "answer": "<honest answer>"}},
    {{"question": "How hard is it to migrate from {target_tool}?", "answer": "<migration tips>"}}
  ],
  "cta_text": "Try the top alternative free for 14 days — no credit card required.",
  "cta_button": "Try Free for 14 Days",
  "primary_keyword": "{target_tool} alternatives",
  "secondary_keywords": ["best {target_tool} alternative", "{target_tool} competitors", "switch from {target_tool}"]
}}"""

    result = complete_json(prompt)
    if not result:
        return False
    return bool(_render_and_save(result, vertical))


def _generate_pricing_page(tool: str, vertical: str) -> bool:
    if _already_generated(f"{tool} pricing"):
        return False

    prompt = f"""Write a detailed "{tool} Pricing" page for B2B buyers evaluating {tool}.

Return JSON:
{{
  "page_title": "{tool} Pricing {time.strftime('%Y')}: Plans, Costs & What You Actually Pay",
  "meta_description": "{tool} pricing breakdown for {time.strftime('%Y')}. All plans, hidden costs, free trial info and whether it's worth it.",
  "subtitle": "Every {tool} plan explained — plus what buyers actually pay after negotiation",
  "tldr": "{tool} pricing starts from a free or low-cost tier. Most B2B teams land on the mid-tier plan.",
  "tools": [
    {{
      "name": "{tool}",
      "description": "<what {tool} does and who it's for>",
      "score": <4.0-5.0>,
      "logo_url": "https://saaspare.org/assets/logos/<tool-slug>.png",
      "logo_bg": "<brand hex color e.g. #FF5500>",
      "pros": ["<value pro1>", "<value pro2>", "<pricing pro>"],
      "cons": ["<pricing con1>", "<pricing con2>"],
      "pricing": "<detailed pricing with plan names and prices>",
      "homepage": "<url>",
      "winner": true
    }},
    {{
      "name": "Best {tool} Alternative",
      "description": "<cheaper or better-value alternative>",
      "score": <3.5-4.5>,
      "logo_url": "https://saaspare.org/assets/logos/<tool-slug>.png",
      "logo_bg": "<brand hex color>",
      "pros": ["<cheaper>", "<comparable features>"],
      "cons": ["<less brand recognition>"],
      "pricing": "<starting price>",
      "homepage": "<url>",
      "winner": false
    }}
  ],
  "comparison_features": [
    {{"name": "Starter Plan", "values": ["<price>", "<alt price>"]}},
    {{"name": "Pro Plan", "values": ["<price>", "<alt price>"]}},
    {{"name": "Enterprise", "values": ["Custom", "Custom"]}},
    {{"name": "Free Trial", "values": ["<days>", "<days>"]}}
  ],
  "verdict": "{tool} is worth it for teams that need <use case>. If budget is tight, try the alternative first.",
  "faqs": [
    {{"question": "How much does {tool} cost per month?", "answer": "<specific pricing>"}},
    {{"question": "Does {tool} have a free plan?", "answer": "<free tier details>"}},
    {{"question": "Is {tool} worth the price?", "answer": "<honest ROI assessment>"}}
  ],
  "cta_text": "Try {tool} free for 14 days — no credit card required.",
  "cta_button": "Start Free Trial",
  "primary_keyword": "{tool} pricing",
  "secondary_keywords": ["{tool} cost", "{tool} plans", "how much does {tool} cost"]
}}"""

    result = complete_json(prompt)
    if not result:
        return False
    return bool(_render_and_save(result, vertical))


def _generate_bestof_page(vertical: str, audience: str, tools: list[str]) -> bool:
    key = f"best {vertical.replace('_',' ')} {audience}"
    if _already_generated(key):
        return False

    tool_list = ", ".join(tools)
    prompt = f"""You are an expert B2B software analyst. Write a buyer guide for {vertical.replace('_',' ')} tools.

Tools to rank: {tool_list}
Audience: {audience}

Return JSON:
{{
  "page_title": "Best {vertical.replace('_',' ').title()} Software for {audience.title()} in {time.strftime('%Y')} (Ranked)",
  "meta_description": "The {len(tools)} best {vertical.replace('_',' ')} tools for {audience} — reviewed by pricing, features and ROI.",
  "subtitle": "Ranked by value, ease of use and ROI for {audience} teams",
  "tldr": "For most {audience} teams, tools 1-2 on this list are the best starting point.",
  "tools": [
    {{
      "name": "<tool>",
      "description": "<why it's great for {audience}>",
      "score": <3.8-5.0>,
      "logo_url": "https://saaspare.org/assets/logos/<tool-slug>.png",
      "logo_bg": "<brand hex color>",
      "pros": ["<pro1>", "<pro2>", "<pro3>"],
      "cons": ["<con1>"],
      "pricing": "<starting price or free tier>",
      "homepage": "<url>",
      "winner": false
    }}
  ],
  "comparison_features": [
    {{"name": "Starting Price", "values": ["<price per tool>"]}},
    {{"name": "Free Trial", "values": ["<yes/no per tool>"]}},
    {{"name": "Best For", "values": ["<use case per tool>"]}}
  ],
  "verdict": "For {audience}, our top pick delivers the best balance of features and price.",
  "faqs": [
    {{"question": "What is the best {vertical.replace('_',' ')} software for {audience}?", "answer": "<recommendation>"}},
    {{"question": "How much does {vertical.replace('_',' ')} software cost for {audience}?", "answer": "<pricing range>"}},
    {{"question": "Is there a free {vertical.replace('_',' ')} tool for {audience}?", "answer": "<free options>"}}
  ],
  "cta_text": "Start with our top pick — free trial, no credit card required.",
  "cta_button": "Start Free Trial",
  "primary_keyword": "best {vertical.replace('_',' ')} software for {audience}",
  "secondary_keywords": ["top {vertical.replace('_',' ')} tools {audience}", "{vertical.replace('_',' ')} {audience} {time.strftime('%Y')}"]
}}"""

    result = complete_json(prompt)
    if not result:
        return False
    return bool(_render_and_save(result, vertical))


def _generate_coupon_page(tool: str, vertical: str) -> bool:
    if _already_generated(f"{tool} coupon"):
        return False

    prompt = f"""Write a "{tool} Coupon Codes" page for buyers about to purchase {tool}.

Return JSON:
{{
  "page_title": "{tool} Coupon Code & Promo Codes {time.strftime('%Y')} — Verified Discounts",
  "meta_description": "Get verified {tool} promo codes for {time.strftime('%Y')}. Save on {tool} with our updated discount list — free trial, annual discount and more.",
  "subtitle": "All working {tool} discounts, promo codes and free trial offers in one place",
  "tldr": "The best way to save on {tool} is to start with the free trial, then ask for an annual discount. Here's how.",
  "tools": [
    {{
      "name": "{tool}",
      "description": "<what {tool} does, who it's for, why buyers search for discounts>",
      "score": <4.0-5.0>,
      "logo_url": "https://saaspare.org/assets/logos/<tool-slug>.png",
      "logo_bg": "<brand hex color e.g. #FF5500>",
      "pros": ["<free trial available>", "<annual plan discount>", "<nonprofit/startup pricing>"],
      "cons": ["<no public promo codes>", "<limited discount windows>"],
      "pricing": "<starter plan price and annual savings>",
      "homepage": "<url>",
      "winner": true
    }},
    {{
      "name": "Best {tool} Alternative",
      "description": "<cheaper alternative if {tool} is over budget>",
      "score": <3.5-4.5>,
      "logo_url": "https://saaspare.org/assets/logos/<tool-slug>.png",
      "logo_bg": "<brand hex color>",
      "pros": ["<lower price>", "<similar features>", "<free plan available>"],
      "cons": ["<smaller ecosystem>"],
      "pricing": "<starting price>",
      "homepage": "<url>",
      "winner": false
    }}
  ],
  "comparison_features": [
    {{"name": "Free Trial", "values": ["<days>", "<days>"]}},
    {{"name": "Annual Discount", "values": ["<% saving>", "<% saving>"]}},
    {{"name": "Starting Price", "values": ["<price/mo>", "<price/mo>"]}},
    {{"name": "Money-Back", "values": ["<days/none>", "<days/none>"]}}
  ],
  "verdict": "The best way to save on {tool} is the annual plan — you save 20-40% vs monthly. No working promo codes exist but the free trial is genuinely risk-free.",
  "faqs": [
    {{"question": "Is there a {tool} promo code?", "answer": "<honest answer about coupon availability>"}},
    {{"question": "How do I get {tool} for free?", "answer": "<free trial details>"}},
    {{"question": "Does {tool} offer a discount for startups or nonprofits?", "answer": "<program details if any>"}}
  ],
  "cta_text": "Start {tool} free — no promo code needed. Most plans include a 14-day free trial.",
  "cta_button": "Claim Free Trial",
  "primary_keyword": "{tool} coupon code",
  "secondary_keywords": ["{tool} promo code", "{tool} discount", "{tool} free trial"]
}}"""

    result = complete_json(prompt)
    if not result:
        return False
    return bool(_render_and_save(result, vertical))


def _generate_review_page(tool: str, vertical: str) -> bool:
    if _already_generated(f"{tool} review"):
        return False

    prompt = f"""Write an in-depth "{tool} Review" for B2B buyers evaluating {tool} for {vertical.replace('_',' ')}.

Return JSON:
{{
  "page_title": "{tool} Review {time.strftime('%Y')}: Is It Worth It? (Honest Verdict)",
  "meta_description": "Honest {tool} review for {time.strftime('%Y')}. Real pricing, features, pros, cons and who it's actually best for.",
  "subtitle": "An unbiased {tool} review based on real user feedback and hands-on testing",
  "tldr": "{tool} is a strong choice for <specific use case> but overkill for <other use case>. Here's the full picture.",
  "tools": [
    {{
      "name": "{tool}",
      "description": "<comprehensive 2-3 sentence description of what it does and its market position>",
      "score": <4.0-5.0>,
      "logo_url": "https://saaspare.org/assets/logos/<tool-slug>.png",
      "logo_bg": "<brand hex color e.g. #FF5500>",
      "pros": ["<pro1>", "<pro2>", "<pro3>", "<pro4>"],
      "cons": ["<con1>", "<con2>", "<con3>"],
      "pricing": "<full pricing breakdown>",
      "homepage": "<url>",
      "winner": true
    }},
    {{
      "name": "Best {tool} Alternative",
      "description": "<main competitor and when to pick it instead>",
      "score": <3.5-4.5>,
      "logo_url": "https://saaspare.org/assets/logos/<tool-slug>.png",
      "logo_bg": "<brand hex color>",
      "pros": ["<why it wins in some cases>", "<better price>"],
      "cons": ["<where it loses to {tool}>"],
      "pricing": "<starting price>",
      "homepage": "<url>",
      "winner": false
    }}
  ],
  "comparison_features": [
    {{"name": "Overall Rating", "values": ["4.5/5", "4.2/5"]}},
    {{"name": "Ease of Use", "values": ["<rating>", "<rating>"]}},
    {{"name": "Value for Money", "values": ["<rating>", "<rating>"]}},
    {{"name": "Customer Support", "values": ["<rating>", "<rating>"]}},
    {{"name": "Starting Price", "values": ["<price>", "<price>"]}}
  ],
  "verdict": "<honest 3-sentence verdict on who should buy {tool} and who should look elsewhere>",
  "faqs": [
    {{"question": "Is {tool} worth it in {time.strftime('%Y')}?", "answer": "<honest answer>"}},
    {{"question": "What are the main complaints about {tool}?", "answer": "<real pain points>"}},
    {{"question": "Who should NOT use {tool}?", "answer": "<honest fit assessment>"}}
  ],
  "cta_text": "Try {tool} free — judge it yourself with zero risk.",
  "cta_button": "Start Free Trial",
  "primary_keyword": "{tool} review",
  "secondary_keywords": ["{tool} review {time.strftime('%Y')}", "is {tool} worth it", "{tool} pros and cons"]
}}"""

    result = complete_json(prompt)
    if not result:
        return False
    return bool(_render_and_save(result, vertical))


def _generate_free_plan_page(tool: str, vertical: str) -> bool:
    if _already_generated(f"{tool} free plan"):
        return False

    prompt = f"""Write a "Does {tool} Have a Free Plan?" page for buyers who want to try {tool} without paying.

Return JSON:
{{
  "page_title": "Does {tool} Have a Free Plan? ({time.strftime('%Y')} Full Breakdown)",
  "meta_description": "Does {tool} offer a free plan in {time.strftime('%Y')}? Yes/no plus free tier limits, free trial details and the best free alternatives.",
  "subtitle": "Everything you need to know about {tool}'s free tier, free trial and how to get started without paying",
  "tldr": "<yes/no answer on whether {tool} has a free plan, and what the limits are in 2 sentences>",
  "tools": [
    {{
      "name": "{tool} Free",
      "description": "<exactly what is and isn't included in the free tier or trial>",
      "score": <4.0-5.0>,
      "logo_url": "https://saaspare.org/assets/logos/<tool-slug>.png",
      "logo_bg": "<brand hex color e.g. #FF5500>",
      "pros": ["<what you get free>", "<free trial length>", "<no credit card required or not>"],
      "cons": ["<limits of free plan>", "<what's locked behind paid>"],
      "pricing": "Free tier available — paid plans from <price>/mo",
      "homepage": "<url>",
      "winner": true
    }},
    {{
      "name": "Best Free {tool} Alternative",
      "description": "<a genuinely free alternative with a more generous free tier>",
      "score": <3.5-4.5>,
      "logo_url": "https://saaspare.org/assets/logos/<tool-slug>.png",
      "logo_bg": "<brand hex color>",
      "pros": ["<more generous free plan>", "<no credit card>", "<open source if applicable>"],
      "cons": ["<fewer integrations>"],
      "pricing": "Free forever plan available",
      "homepage": "<url>",
      "winner": false
    }}
  ],
  "comparison_features": [
    {{"name": "Free Plan", "values": ["<yes/no + limits>", "<yes/no + limits>"]}},
    {{"name": "Free Trial", "values": ["<days or none>", "<days or none>"]}},
    {{"name": "Credit Card Required", "values": ["<yes/no>", "<yes/no>"]}},
    {{"name": "Paid Starts At", "values": ["<price>", "<price>"]}}
  ],
  "verdict": "<honest recommendation on whether to use free tier, upgrade, or switch to a more generous free alternative>",
  "faqs": [
    {{"question": "Is {tool} free forever?", "answer": "<accurate answer>"}},
    {{"question": "What do you get with {tool}'s free plan?", "answer": "<specific features and limits>"}},
    {{"question": "What happens when the {tool} free trial ends?", "answer": "<what happens and how to avoid being charged>"}}
  ],
  "cta_text": "Start {tool} free today — no credit card required.",
  "cta_button": "Try Free",
  "primary_keyword": "does {tool} have a free plan",
  "secondary_keywords": ["{tool} free plan", "{tool} free tier", "{tool} free trial"]
}}"""

    result = complete_json(prompt)
    if not result:
        return False
    return bool(_render_and_save(result, vertical))


def _write_sitemap():
    try:
        domain = get("SITE_DOMAIN", "https://saaspare.org")
        site_dir = Path("site/pages")
        pages_path = Path("site/sitemap.xml")
        pages_path.parent.mkdir(parents=True, exist_ok=True)
        urls = [f"{domain}/"]
        if site_dir.exists():
            for f in sorted(site_dir.glob("*.html")):
                if f.stem not in ("thanks", "verification"):
                    urls.append(f"{domain}/pages/{f.name}")
        lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for url in urls:
            priority = "1.0" if url == f"{domain}/" else "0.8"
            lines.append(f'  <url><loc>{url}</loc><changefreq>weekly</changefreq><priority>{priority}</priority></url>')
        lines.append('</urlset>')
        pages_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        log.info(f"Sitemap updated: {len(urls)} URLs written")
    except Exception as e:
        log.warning(f"Sitemap write failed: {e}")


def _ping_google_sitemap():
    try:
        import httpx
        domain = get("SITE_DOMAIN", "https://saaspare.org")
        httpx.get(f"https://www.google.com/ping?sitemap={domain}/sitemap.xml", timeout=10)
        httpx.get(f"https://www.bing.com/ping?sitemap={domain}/sitemap.xml", timeout=10)
        log.info("Pinged Google + Bing sitemap endpoints")
    except Exception as e:
        log.warning(f"Sitemap ping failed: {e}")


def _write_redirects_file():
    try:
        redirects = get_all_redirects()
        lines = []
        for slug, url in redirects.items():
            sep = "&" if "?" in url else "?"
            tracked_url = f"{url}{sep}utm_source=saaspare&utm_medium=affiliate&utm_campaign=go"
            lines.append(f"/go/{slug} {tracked_url} 302")
        path = Path("site/_redirects")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        log.info(f"Written {len(lines)} /go/ redirects to site/_redirects")
    except Exception as e:
        log.warning(f"Failed to write _redirects: {e}")


def _sync_db_from_filesystem():
    try:
        import re
        pages_dir = Path("site/pages")
        if not pages_dir.exists():
            return
        with db() as conn:
            existing = {row[0] for row in conn.execute("SELECT title FROM outputs").fetchall()}
            inserted = 0
            for f in pages_dir.glob("*.html"):
                html = f.read_text(encoding="utf-8", errors="ignore")
                m = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
                if not m:
                    continue
                title = m.group(1).strip()
                if title and title not in existing:
                    conn.execute(
                        "INSERT OR IGNORE INTO outputs (id, type, vertical, title, file_path, created_at) VALUES (?, ?, ?, ?, ?, strftime('%s','now'))",
                        (f.stem, "programmatic", "unknown", title, str(f))
                    )
                    existing.add(title)
                    inserted += 1
            conn.commit()
        if inserted:
            log.info(f"_sync_db_from_filesystem: synced {inserted} existing HTML pages into DB")
    except Exception as e:
        log.warning(f"_sync_db_from_filesystem failed: {e}")


def run_programmatic(max_pages: int = 500) -> int:
    from core.db import migrate
    migrate()

    _sync_db_from_filesystem()
    _write_redirects_file()

    domain = get("SITE_DOMAIN", "https://saaspare.org")
    log.info(f"Starting programmatic SEO run — target {max_pages} pages for {domain}")

    tasks: list[tuple] = []

    for vertical, tools in TOOLS_BY_VERTICAL.items():
        for tool_a, tool_b in combinations(tools, 2):
            tasks.append((_generate_comparison_page, (tool_a, tool_b, vertical)))

    for vertical, targets in ALTERNATIVE_TARGETS.items():
        for target in targets:
            tasks.append((_generate_alternatives_page, (target, vertical)))

    for tool, vertical in HIGH_VALUE_PRICING_TARGETS:
        tasks.append((_generate_pricing_page, (tool, vertical)))

    for vertical, audience, tools in BEST_OF_QUERIES:
        tasks.append((_generate_bestof_page, (vertical, audience, tools)))

    for tool, vertical in HIGH_VALUE_COUPON_TARGETS:
        tasks.append((_generate_coupon_page, (tool, vertical)))

    for tool, vertical in HIGH_VALUE_REVIEW_TARGETS:
        tasks.append((_generate_review_page, (tool, vertical)))

    for tool, vertical in FREE_PLAN_TARGETS:
        tasks.append((_generate_free_plan_page, (tool, vertical)))

    tasks.sort(key=_task_priority)

    generated = 0
    consecutive_failures = 0
    MAX_CONSECUTIVE_FAILURES = 5

    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = {
            executor.submit(fn, *args): args
            for fn, args in tasks
        }
        for future in as_completed(futures):
            if generated >= max_pages or consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                for f in futures:
                    f.cancel()
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    log.warning("5 consecutive LLM failures — quota exhausted, stopping run early")
                break
            args = futures[future]
            try:
                ok = future.result()
                if ok:
                    generated += 1
                    consecutive_failures = 0
                    log.info(f"[{generated}/{max_pages}] Generated: {args}")
                else:
                    consecutive_failures += 1
            except Exception as e:
                consecutive_failures += 1
                log.warning(f"Page gen failed {args}: {e}")

    from pathlib import Path as _Path
    from publisher.pages_deploy import _rebuild_sitemap, _rebuild_homepage
    _rebuild_sitemap(_Path("site"))
    _rebuild_homepage(_Path("site"))
    if generated > 0:
        _ping_google_sitemap()

    log.info(f"Programmatic run complete: {generated} pages generated")
    return generated
