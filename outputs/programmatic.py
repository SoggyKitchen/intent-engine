"""
Programmatic SEO — generates pages for ALL known tool combinations upfront.
Doesn't need signal clusters. Runs daily for 2100+ pages/month.
"""
import json
import time
from pathlib import Path
from itertools import combinations

from core.db import db
from core.logger import log
from llm.router import complete_json
from outputs.seo_page import _render_and_save
from core.secrets import get

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
}


def _already_generated(slug_hint: str) -> bool:
    try:
        with db() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM outputs WHERE title LIKE ?",
                (f"%{slug_hint}%",)
            ).fetchone()
        return row[0] > 0
    except Exception:
        return False


def _generate_comparison_page(tool_a: str, tool_b: str, vertical: str) -> bool:
    if _already_generated(f"{tool_a} vs {tool_b}"):
        return False

    prompt = f"""You are an expert B2B software analyst writing for buyers.

Write a detailed comparison of {tool_a} vs {tool_b} for {vertical.replace('_',' ')} buyers.

Return JSON exactly:
{{
  "page_title": "{tool_a} vs {tool_b}: Which is Better in {time.strftime('%Y')}?",
  "meta_description": "Detailed {tool_a} vs {tool_b} comparison. Pricing, features, pros, cons and which to choose for your business.",
  "subtitle": "An unbiased, data-driven comparison for {vertical.replace('_',' ')} teams",
  "tldr": "<2 sentences: who should pick each tool>",
  "tools": [
    {{
      "name": "{tool_a}",
      "description": "<2-3 sentence accurate description>",
      "pros": ["<pro1>", "<pro2>", "<pro3>"],
      "cons": ["<con1>", "<con2>"],
      "pricing": "<real pricing tier summary>",
      "homepage": "<official URL>",
      "winner": true
    }},
    {{
      "name": "{tool_b}",
      "description": "<2-3 sentence accurate description>",
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
    path = _render_and_save(result, vertical)
    return bool(path)


def _generate_alternatives_page(target_tool: str, vertical: str) -> bool:
    if _already_generated(f"alternatives to {target_tool}"):
        return False

    programs = TOOLS_BY_VERTICAL.get(vertical, [])
    alternatives = [t for t in programs if t != target_tool][:5]
    alt_list = ", ".join(alternatives)

    prompt = f"""You are an expert B2B software analyst writing for buyers who want to leave {target_tool}.

Write a "Best Alternatives to {target_tool}" page for buyers in {vertical.replace('_',' ')}.
The top alternatives to cover: {alt_list}

Return JSON exactly:
{{
  "page_title": "7 Best {target_tool} Alternatives in {time.strftime('%Y')} (Free & Paid)",
  "meta_description": "Looking for {target_tool} alternatives? We reviewed the top options by price, features and ease of switching. Find your best match.",
  "subtitle": "The best {target_tool} alternatives ranked by value, features and migration ease",
  "tldr": "If you're tired of {target_tool}, here are the top alternatives worth trying in {time.strftime('%Y')}.",
  "tools": [
    {{
      "name": "<alternative name>",
      "description": "<why it beats {target_tool} for certain buyers>",
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
    {{"question": "What is the best free alternative to {target_tool}?", "answer": "<answer with specific tool>"}},
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
    path = _render_and_save(result, vertical)
    return bool(path)


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
]


def _generate_bestof_page(vertical: str, audience: str, tools: list[str]) -> bool:
    key = f"best {vertical.replace('_',' ')} {audience}"
    if _already_generated(key):
        return False

    tool_list = ", ".join(tools)
    prompt = f"""You are an expert B2B software analyst. Write a "Best {vertical.replace('_',' ')} tools for {audience}" buyer guide.

Tools to rank and review: {tool_list}

Return JSON:
{{
  "page_title": "Best {vertical.replace('_',' ').title()} Software for {audience.title()} in {time.strftime('%Y')} (Ranked)",
  "meta_description": "The {len(tools)} best {vertical.replace('_',' ')} tools for {audience} — reviewed by pricing, features and ROI. Find the right fit fast.",
  "subtitle": "Ranked by value, ease of use and ROI for {audience} teams",
  "tldr": "For most {audience} teams, tools 1-2 on this list are the best starting point. Here's why.",
  "tools": [
    {{
      "name": "<tool>",
      "description": "<why it's great for {audience}>",
      "pros": ["<pro1>", "<pro2>", "<pro3>"],
      "cons": ["<con1>"],
      "pricing": "<starting price or free tier>",
      "homepage": "<url>",
      "winner": <true for #1 only>
    }}
  ],
  "comparison_features": [
    {{"name": "Starting Price", "values": ["<price per tool>"]}},
    {{"name": "Free Trial", "values": ["<yes/no per tool>"]}},
    {{"name": "Best For", "values": ["<use case per tool>"]}}
  ],
  "verdict": "For {audience}, our top pick delivers the best balance of features and price. Start with the free trial to validate before committing.",
  "faqs": [
    {{"question": "What is the best {vertical.replace('_',' ')} software for {audience}?", "answer": "<specific recommendation with reasoning>"}},
    {{"question": "How much does {vertical.replace('_',' ')} software cost for {audience}?", "answer": "<pricing range overview>"}},
    {{"question": "Is there a free {vertical.replace('_',' ')} tool for {audience}?", "answer": "<free options available>"}}
  ],
  "cta_text": "Start with our top pick — free trial, no credit card required.",
  "cta_button": "Start Free Trial",
  "primary_keyword": "best {vertical.replace('_',' ')} software for {audience}",
  "secondary_keywords": ["top {vertical.replace('_',' ')} tools {audience}", "{vertical.replace('_',' ')} software {audience} {time.strftime('%Y')}"]
}}"""
    result = complete_json(prompt)
    if not result:
        return False
    path = _render_and_save(result, vertical)
    return bool(path)


def _generate_pricing_page(tool: str, vertical: str) -> bool:
    key = f"{tool} pricing"
    if _already_generated(key):
        return False

    prompt = f"""Write a detailed "{tool} Pricing" page for B2B buyers evaluating {tool}.

Return JSON:
{{
  "page_title": "{tool} Pricing {time.strftime('%Y')}: Plans, Costs & What You Actually Pay",
  "meta_description": "{tool} pricing breakdown for {time.strftime('%Y')}. All plans, hidden costs, free trial info and whether it's worth it for your team size.",
  "subtitle": "Every {tool} plan explained — plus what buyers actually pay after negotiation",
  "tldr": "{tool} pricing starts from a free or low-cost tier. Most B2B teams land on the mid-tier plan. Here's the full breakdown.",
  "tools": [
    {{
      "name": "{tool}",
      "description": "<what {tool} does and who it's for>",
      "pros": ["<value pro1>", "<value pro2>", "<pricing pro>"],
      "cons": ["<pricing con1>", "<pricing con2>"],
      "pricing": "<detailed pricing with plan names and prices>",
      "homepage": "<url>",
      "winner": true
    }},
    {{
      "name": "Best {tool} Alternative",
      "description": "<cheaper or better-value alternative for budget-conscious buyers>",
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
    path = _render_and_save(result, vertical)
    return bool(path)


HIGH_VALUE_PRICING_TARGETS = [
    ("HubSpot", "marketing_automation"),
    ("Salesforce", "marketing_automation"),
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
]


def _ping_google_sitemap():
    try:
        import httpx
        domain = get("SITE_DOMAIN", "https://saaspare.org")
        httpx.get(f"https://www.google.com/ping?sitemap={domain}/sitemap.xml", timeout=10)
        httpx.get(f"https://www.bing.com/ping?sitemap={domain}/sitemap.xml", timeout=10)
        log.info("Pinged Google + Bing sitemap endpoints")
    except Exception as e:
        log.warning(f"Sitemap ping failed: {e}")


def run_programmatic(max_pages: int = 500) -> int:
    """Generate comparison + alternatives + pricing + best-of pages."""
    from core.db import migrate
    migrate()

    generated = 0
    domain = get("SITE_DOMAIN", "https://saaspare.org")
    log.info(f"Starting programmatic SEO run — target {max_pages} pages for {domain}")

    for vertical, tools in TOOLS_BY_VERTICAL.items():
        if generated >= max_pages:
            break
        for tool_a, tool_b in combinations(tools, 2):
            if generated >= max_pages:
                break
            try:
                ok = _generate_comparison_page(tool_a, tool_b, vertical)
                if ok:
                    generated += 1
                    log.info(f"[{generated}] {tool_a} vs {tool_b} ({vertical})")
                time.sleep(1.5)
            except Exception as e:
                log.warning(f"Failed {tool_a} vs {tool_b}: {e}")

    for vertical, targets in ALTERNATIVE_TARGETS.items():
        if generated >= max_pages:
            break
        for target in targets:
            if generated >= max_pages:
                break
            try:
                ok = _generate_alternatives_page(target, vertical)
                if ok:
                    generated += 1
                    log.info(f"[{generated}] alternatives to {target} ({vertical})")
                time.sleep(1.5)
            except Exception as e:
                log.warning(f"Failed alternatives {target}: {e}")

    for tool, vertical in HIGH_VALUE_PRICING_TARGETS:
        if generated >= max_pages:
            break
        try:
            ok = _generate_pricing_page(tool, vertical)
            if ok:
                generated += 1
                log.info(f"[{generated}] pricing: {tool}")
            time.sleep(1.5)
        except Exception as e:
            log.warning(f"Failed pricing {tool}: {e}")

    for vertical, audience, tools in BEST_OF_QUERIES:
        if generated >= max_pages:
            break
        try:
            ok = _generate_bestof_page(vertical, audience, tools)
            if ok:
                generated += 1
                log.info(f"[{generated}] best-of: {vertical} for {audience}")
            time.sleep(1.5)
        except Exception as e:
            log.warning(f"Failed best-of {vertical}/{audience}: {e}")

    if generated > 0:
        _ping_google_sitemap()

    log.info(f"Programmatic run complete: {generated} pages generated")
    return generated
