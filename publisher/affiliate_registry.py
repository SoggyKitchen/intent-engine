import json
from functools import lru_cache
from pathlib import Path

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
        {"name": "Linode", "homepage": "https://www.linode.com",
         "affiliate_url": "/pages/linode-vs-google-cloud-which-is-better-in-2026", "network": "internal-fallback",
         "commission": "$100 per new customer", "commission_pct": 0, "recurring": False, "avg_plan_usd": 100,
         "aliases": ["akamai cloud", "akamai linode"]},
        {"name": "Render", "homepage": "https://render.com",
         "affiliate_url": "https://render.com/affiliates", "network": "partnerstack",
         "commission": "20% recurring for 12 months", "commission_pct": 20, "recurring": True, "avg_plan_usd": 25},
        {"name": "Supabase", "homepage": "https://supabase.com",
         "affiliate_url": "https://supabase.com/affiliates", "network": "partnerstack",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 25},
    ],

    "cybersecurity": [
        {"name": "Tresorit", "homepage": "https://tresorit.com",
         "affiliate_url": "https://click.linksynergy.com/fs-bin/click?id=BkjK9id55Qs&offerid=1878376.9&type=3&subid=0",
         "network": "rakuten", "commission": "up to 40% per sale", "commission_pct": 40,
         "recurring": False, "avg_plan_usd": 24,
         "go_slug": "tresorit",
         "offers": [
             {"name": "Tresorit Personal", "click_url": "https://click.linksynergy.com/fs-bin/click?id=BkjK9id55Qs&offerid=1878376.9&type=3&subid=0"},
             {"name": "Tresorit Individual (DE)", "click_url": "https://click.linksynergy.com/fs-bin/click?id=BkjK9id55Qs&offerid=1878376.21&type=3&subid=0"},
             {"name": "Tresorit DE", "click_url": "https://click.linksynergy.com/fs-bin/click?id=BkjK9id55Qs&offerid=1878376.11&type=3&subid=0"},
         ]},
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
         "affiliate_url": "/pages/gusto-pricing-2026-plans-costs-what-you-actually-pay", "network": "internal-fallback",
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
         "affiliate_url": "https://www.expensify.com", "network": "direct",
         "commission": "0.5% of referred spend", "commission_pct": 1, "recurring": False, "avg_plan_usd": 5},
        {"name": "Xero", "homepage": "https://www.xero.com/us/pricing-plans/",
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
        {"name": "ElevenLabs", "homepage": "https://elevenlabs.io",
         "affiliate_url": "https://try.elevenlabs.io/i2it5u0kkasf", "network": "partnerstack",
         "commission": "PartnerStack affiliate program", "commission_pct": 0, "recurring": False, "avg_plan_usd": 22,
         "aliases": ["Eleven Labs", "ElevenLabs AI", "ElevenLabs Voice"]},
        {"name": "Pinecone", "homepage": "https://www.pinecone.io",
         "affiliate_url": "https://www.pinecone.io/partners/", "network": "partnerstack",
         "commission": "20% for 12 months", "commission_pct": 20, "recurring": True, "avg_plan_usd": 70},
    ],

    "project_management": [
        {"name": "Trello", "homepage": "https://trello.com",
         "affiliate_url": "https://trello.com/pricing", "network": "direct",
         "commission": "no affiliate — direct pricing link", "commission_pct": 0, "recurring": False, "avg_plan_usd": 0,
         "aliases": ["trello boards", "atlassian trello"]},
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
        {"name": "HubSpot CRM", "homepage": "https://www.hubspot.com/products/crm",
         "affiliate_url": "https://www.hubspot.com/partners/affiliates", "network": "impact",
         "commission": "30% recurring for 12 months", "commission_pct": 30, "recurring": True, "avg_plan_usd": 50,
         "aliases": ["HubSpot", "hubspot crm", "hubspot free crm"]},
        {"name": "Salesforce", "homepage": "https://www.salesforce.com/crm/",
         "affiliate_url": "https://www.salesforce.com/form/signup/freetrial-sales/", "network": "direct",
         "commission": "no affiliate — direct trial link", "commission_pct": 0, "recurring": False, "avg_plan_usd": 0,
         "aliases": ["Salesforce CRM", "salesforce sales cloud", "sfdc"]},
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
        {"name": "Bitwarden", "homepage": "https://bitwarden.com",
         "affiliate_url": "https://bitwarden.com/pricing/", "network": "direct",
         "commission": "no affiliate — direct pricing link", "commission_pct": 0, "recurring": False, "avg_plan_usd": 0,
         "aliases": ["bitwarden business", "bitwarden teams"]},
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
        {"name": "Whereby", "homepage": "https://whereby.com",
         "affiliate_url": "https://whereby.com/partners/affiliates/", "network": "partnerstack",
         "commission": "20% per upgrade", "commission_pct": 20, "recurring": False, "avg_plan_usd": 59},
        {"name": "Riverside.fm", "homepage": "https://riverside.fm",
         "affiliate_url": "https://riverside.fm/affiliates", "network": "partnerstack",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 24},
        {"name": "Loom", "homepage": "https://www.loom.com",
         "affiliate_url": "https://www.loom.com/affiliates", "network": "partnerstack",
         "commission": "15% recurring for 12 months", "commission_pct": 15, "recurring": True, "avg_plan_usd": 12.50},
        {"name": "Riverside.fm", "homepage": "https://riverside.fm",
         "affiliate_url": "https://riverside.fm/affiliates", "network": "partnerstack",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 24},
        {"name": "Zoom", "homepage": "https://zoom.us",
         "affiliate_url": "https://zoom.us/partners/affiliate", "network": "partnerstack",
         "commission": "Referral credits", "commission_pct": 0, "recurring": False, "avg_plan_usd": 0},
    ],

    "vpn_business": [
        {"name": "Cloudflare Access", "homepage": "https://www.cloudflare.com/products/zero-trust/",
         "affiliate_url": "https://www.cloudflare.com/plans/zero-trust-services/", "network": "direct",
         "commission": "no affiliate — direct pricing link", "commission_pct": 0, "recurring": False, "avg_plan_usd": 0,
         "aliases": ["cloudflare zero trust", "cloudflare teams", "cloudflare ztna"]},
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

    "affiliate_management": [
        {"name": "impact.com", "homepage": "https://impact.com",
         "affiliate_url": "https://goto.impact.com/c/7250237/2014517/24933",
         "network": "impact", "go_slug": "impact",
         "commission": "custom — CPA on new brand signups", "commission_pct": 0, "recurring": False,
         "avg_plan_usd": 500,
         "aliases": ["impact", "impact radius", "impact affiliate", "impact.com platform"]},
        {"name": "PartnerStack", "homepage": "https://partnerstack.com",
         "affiliate_url": "https://partnerstack.com/become-a-partner", "network": "direct",
         "commission": "25% recurring", "commission_pct": 25, "recurring": True, "avg_plan_usd": 500},
        {"name": "Tapfiliate", "homepage": "https://tapfiliate.com",
         "affiliate_url": "https://tapfiliate.com/affiliate-program/", "network": "partnerstack",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 89},
        {"name": "Rewardful", "homepage": "https://www.rewardful.com",
         "affiliate_url": "https://www.rewardful.com/affiliates", "network": "direct",
         "commission": "25% recurring for 12 months", "commission_pct": 25, "recurring": True, "avg_plan_usd": 49},
        {"name": "FirstPromoter", "homepage": "https://firstpromoter.com",
         "affiliate_url": "https://firstpromoter.com/affiliate-program", "network": "direct",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 49},
        {"name": "Refersion", "homepage": "https://www.refersion.com",
         "affiliate_url": "https://www.refersion.com/affiliates", "network": "direct",
         "commission": "20% per sale", "commission_pct": 20, "recurring": False, "avg_plan_usd": 99},
    ],

    "seo_tools": [
        {"name": "Ahrefs", "homepage": "https://ahrefs.com",
         "affiliate_url": "https://ahrefs.com/affiliates", "network": "direct",
         "commission": "$20 per trial + recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 99},
        {"name": "Semrush", "homepage": "https://www.semrush.com",
         "affiliate_url": "https://www.semrush.com/partner/", "network": "impact",
         "commission": "$200 per new subscription", "commission_pct": 0, "recurring": False, "avg_plan_usd": 200},
        {"name": "Moz Pro", "homepage": "https://moz.com",
         "affiliate_url": "https://moz.com/affiliate", "network": "shareasale",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 99},
        {"name": "Surfer SEO", "homepage": "https://surferseo.com",
         "affiliate_url": "https://surferseo.com/affiliate/", "network": "partnerstack",
         "commission": "25% recurring", "commission_pct": 25, "recurring": True, "avg_plan_usd": 89},
        {"name": "SE Ranking", "homepage": "https://seranking.com",
         "affiliate_url": "https://seranking.com/partners.html", "network": "partnerstack",
         "commission": "30% recurring", "commission_pct": 30, "recurring": True, "avg_plan_usd": 55},
        {"name": "Mangools", "homepage": "https://mangools.com",
         "affiliate_url": "https://mangools.com/affiliate-program", "network": "direct",
         "commission": "30% recurring", "commission_pct": 30, "recurring": True, "avg_plan_usd": 49},
        {"name": "SpyFu", "homepage": "https://www.spyfu.com",
         "affiliate_url": "https://www.spyfu.com/affiliate", "network": "shareasale",
         "commission": "40% per sale", "commission_pct": 40, "recurring": False, "avg_plan_usd": 39},
        {"name": "Ubersuggest", "homepage": "https://neilpatel.com/ubersuggest/",
         "affiliate_url": "https://neilpatel.com/ubersuggest/", "network": "direct",
         "commission": "30% recurring", "commission_pct": 30, "recurring": True, "avg_plan_usd": 29,
         "aliases": ["ubersuggest neil patel", "neil patel seo"]},
        {"name": "Clearscope", "homepage": "https://www.clearscope.io",
         "affiliate_url": "https://www.clearscope.io/partners", "network": "direct",
         "commission": "20% recurring", "commission_pct": 20, "recurring": True, "avg_plan_usd": 189},
        {"name": "Screaming Frog", "homepage": "https://www.screamingfrog.co.uk",
         "affiliate_url": "https://www.screamingfrog.co.uk/seo-spider/", "network": "direct",
         "commission": "direct traffic only", "commission_pct": 0, "recurring": False, "avg_plan_usd": 18},
        {"name": "Frase.io", "homepage": "https://www.frase.io",
         "affiliate_url": "https://www.frase.io/affiliates/", "network": "partnerstack",
         "commission": "30% recurring", "commission_pct": 30, "recurring": True, "avg_plan_usd": 45},
        {"name": "Rankmath Pro", "homepage": "https://rankmath.com",
         "affiliate_url": "https://rankmath.com/affiliate/", "network": "shareasale",
         "commission": "30% per sale", "commission_pct": 30, "recurring": False, "avg_plan_usd": 59},
    ],
}

OVERRIDES_PATH = Path("data/affiliate_overrides.json")
IMPORTED_AFFILIATE_PATH = Path("data/affiliate_links.json")
SAFE_IMPORTED_ALIAS_SLUGS = {
    "aomei-anyviewer": {"aomei", "pc-transfer", "todo-pctrans", "windows-migration"},
}


def _normalize_aliases(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        value = [value]
    aliases = []
    seen: set[str] = set()
    for alias in value:
        text = str(alias).strip()
        if not text:
            continue
        slug = slugify(text)
        if not slug or slug in seen:
            continue
        seen.add(slug)
        aliases.append(text)
    return aliases


def _load_overrides() -> list[dict]:
    if not OVERRIDES_PATH.exists():
        return []
    try:
        raw = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

    if not isinstance(raw, list):
        return []

    overrides: list[dict] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        affiliate_url = str(item.get("affiliate_url", "")).strip()
        if not name or not affiliate_url:
            continue
        override = dict(item)
        aliases = _normalize_aliases(item.get("aliases"))
        if item.get("network") == "cj" and item.get("source_file"):
            advertiser_slug = slugify(str(item.get("advertiser", "")).strip() or name)
            name_slug = slugify(name)
            safe_allowlist = SAFE_IMPORTED_ALIAS_SLUGS.get(advertiser_slug, set()) | SAFE_IMPORTED_ALIAS_SLUGS.get(name_slug, set())
            brand_tokens = {
                token
                for slug in (advertiser_slug, name_slug)
                for token in slug.split("-")
                if token
            }
            aliases = [
                alias
                for alias in aliases
                if slugify(alias) in safe_allowlist
                or bool({token for token in slugify(alias).split("-") if token} & brand_tokens)
            ]
        override["aliases"] = aliases
        overrides.append(override)
    return overrides


def _merge_program(base: dict, override: dict) -> dict:
    merged = dict(base)
    merged.update({k: v for k, v in override.items() if v not in (None, "")})
    merged["aliases"] = _normalize_aliases(
        [*base.get("aliases", []), *override.get("aliases", [])]
    )
    return merged


def _build_programs() -> dict[str, list[dict]]:
    programs = {vertical: [dict(p) for p in items] for vertical, items in PROGRAMS.items()}
    overrides = _load_overrides()
    if not overrides:
        return programs

    for override in overrides:
        vertical = str(override.get("vertical", "imported_misc")).strip() or "imported_misc"
        bucket = programs.setdefault(vertical, [])
        target_slug = slugify(override["name"])
        matched = False
        for idx, program in enumerate(bucket):
            if slugify(program.get("name", "")) == target_slug:
                bucket[idx] = _merge_program(program, override)
                matched = True
                break
        if not matched:
            bucket.append(_merge_program({
                "name": override["name"],
                "homepage": override.get("homepage", ""),
                "affiliate_url": override["affiliate_url"],
                "network": override.get("network", "direct"),
                "commission": override.get("commission", "Unknown"),
                "commission_pct": override.get("commission_pct", 0),
                "recurring": bool(override.get("recurring", False)),
            }, override))
    return programs


PROGRAMS = _build_programs()


def _program_alias_slugs(program: dict, redirect_only: bool = False) -> list[str]:
    slugs: list[str] = []
    candidates = [program.get("name")]
    if not (redirect_only and program.get("source_file")):
        candidates.extend(program.get("aliases", []))
    for candidate in candidates:
        slug = slugify(str(candidate or ""))
        if slug and slug not in slugs:
            slugs.append(slug)
    return slugs


def _build_program_index() -> dict[str, dict]:
    index: dict[str, dict] = {}
    for programs in PROGRAMS.values():
        for program in programs:
            for slug in _program_alias_slugs(program):
                index.setdefault(slug, program)
    return index


def _build_redirect_targets() -> dict[str, str]:
    redirects: dict[str, str] = {}
    for programs in PROGRAMS.values():
        for program in programs:
            url = _best_url(program, "comparison")
            if not url:
                continue
            for slug in _program_alias_slugs(program, redirect_only=True):
                redirects[slug] = url
    return redirects


_PROGRAM_INDEX = _build_program_index()

_ALL_HOMEPAGES: dict[str, str] = {
    slug: program.get("homepage", "")
    for slug, program in _PROGRAM_INDEX.items()
    if program.get("homepage")
}


@lru_cache(maxsize=1)
def _load_imported_affiliates() -> dict[str, dict]:
    if not IMPORTED_AFFILIATE_PATH.exists():
        return {}
    try:
        raw = json.loads(IMPORTED_AFFILIATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

    advertisers = raw.get("advertisers", {})
    if not isinstance(advertisers, dict):
        return {}
    return advertisers


def clear_imported_affiliate_cache():
    _load_imported_affiliates.cache_clear()


def _get_imported_affiliate(tool_name: str) -> dict | None:
    return _load_imported_affiliates().get(slugify(tool_name))


_PROGRAM_PAGE_PATTERNS = (
    "affiliate",
    "affiliates",
    "affiliate-program",
    "partner",
    "partners",
    "partner-program",
    "referral",
    "refer-a-business",
    "become-an-affiliate",
    "store/affiliate",
    "promo/affiliate",
)


def _is_program_page(url: str) -> bool:
    """True if URL points to an affiliate/partner program signup, not a product page."""
    from urllib.parse import urlparse
    if not url:
        return False
    parsed = urlparse(url if "://" in url else f"https://{url}")
    path = (parsed.path or "").lower().rstrip("/")
    host = (parsed.netloc or "").lower()
    combined = f"{host}{path}"
    return any(token in combined for token in _PROGRAM_PAGE_PATTERNS)


def _find_program(tool_name: str, vertical: str = "") -> dict | None:
    slug = slugify(tool_name)
    program = _PROGRAM_INDEX.get(slug)
    if program:
        return program
    if vertical:
        for candidate in PROGRAMS.get(vertical, []):
            if slug in _program_alias_slugs(candidate):
                return candidate
    return None


def _best_url(program: dict, page_type: str) -> str | None:
    """Return the best visitor-facing URL: real tracking link > product homepage."""
    affiliate = program.get("affiliate_url", "")
    homepage = program.get("homepage", "")
    if affiliate and not _is_program_page(affiliate):
        return affiliate
    if homepage and not _is_program_page(homepage):
        return homepage
    return None


def resolve_click_target(tool_name: str, vertical: str = "", page_type: str = "comparison") -> str | None:
    imported = _get_imported_affiliate(tool_name)
    if imported:
        if page_type == "coupon" and imported.get("coupon_click_url"):
            return imported["coupon_click_url"]
        if imported.get("default_click_url"):
            return imported["default_click_url"]
        if imported.get("homepage_url"):
            return imported["homepage_url"]
        if imported.get("homepage"):
            return imported["homepage"]

    program = _find_program(tool_name, vertical=vertical)
    if program:
        return _best_url(program, page_type)
    return None


_ALL_CLICK_TARGETS: dict[str, str] = {
    **_build_redirect_targets()
}


def get_affiliate_url_for_tool(tool_name: str, vertical: str = "", page_type: str = "comparison") -> str | None:
    return resolve_click_target(tool_name, vertical=vertical, page_type=page_type)


def get_homepage_for_tool(tool_name: str) -> str | None:
    imported = _get_imported_affiliate(tool_name)
    if imported:
        if imported.get("homepage_url"):
            return imported.get("homepage_url")
        if imported.get("homepage"):
            return imported.get("homepage")
    program = _PROGRAM_INDEX.get(slugify(tool_name))
    if program:
        return program.get("homepage")
    return None


def get_go_url(tool_name: str, page_type: str = "comparison") -> str | None:
    slug = slugify(tool_name)
    imported = _get_imported_affiliate(tool_name)
    if page_type == "coupon" and imported and imported.get("coupon_click_url"):
        return f"/go/{slug}-coupon"
    if not resolve_click_target(tool_name, page_type=page_type):
        return None
    redirects = get_all_redirects()
    if slug in redirects:
        return f"/go/{slug}"
    program = _find_program(tool_name)
    if program:
        canonical_slug = slugify(program.get("name", ""))
        if canonical_slug in redirects:
            return f"/go/{canonical_slug}"
    return None


def get_all_redirects() -> dict[str, str]:
    redirects = dict(_ALL_CLICK_TARGETS)
    for slug, item in _load_imported_affiliates().items():
        default_url = item.get("default_click_url")
        coupon_url = item.get("coupon_click_url")
        if default_url:
            redirects[slug] = default_url
        if coupon_url:
            redirects[f"{slug}-coupon"] = coupon_url
    return redirects


def write_redirects_file(path: str | Path = "site/_redirects") -> int:
    path = Path(path)
    preserved = []
    if path.exists():
        preserved = [
            line
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
            if line.strip() and not line.strip().startswith("/go/")
        ]
    lines = preserved + ([] if not preserved else [""])
    redirects = get_all_redirects()
    for slug, url in sorted(redirects.items()):
        sep = "&" if "?" in url else "?"
        tracked_url = f"{url}{sep}utm_source=saaspare&utm_medium=affiliate&utm_campaign=go"
        lines.append(f"/go/{slug} {tracked_url} 302")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(redirects)


def get_links_for_vertical(vertical: str, tool_names: list[str]) -> dict[str, str]:
    result = {}
    for tool in tool_names:
        click_target = resolve_click_target(tool, vertical=vertical)
        if click_target:
            result[tool] = click_target
        else:
            result[tool] = (
                _ALL_CLICK_TARGETS.get(slugify(tool))
                or _ALL_HOMEPAGES.get(slugify(tool))
                or "#"
            )
    return result


NETWORK_SIGNUPS = {
    "impact": {
        "name": "Impact.com Marketplace",
        "signup_url": "https://impact.com/affiliates/",
        "description": "Single signup — access HubSpot, Brevo, Shopify, Semrush, DocuSign, NordLayer, Monday.com, ExpressVPN and 2000+ others",
        "link_format": "https://impact.sjv.io/[PROGRAM_ID]?irgwc=1",
    },
    "partnerstack": {
        "name": "PartnerStack Marketplace",
        "signup_url": "https://app.partnerstack.com/",
        "description": "Single signup — access JetBrains, Retool, ActiveCampaign, Klaviyo, ClickUp, Notion, Pipedrive, 1Password, Jasper AI and most SaaS tools",
        "link_format": "https://partnerstack.com/[PROGRAM_SLUG]?via=[YOUR_REF_CODE]",
    },
    "shareasale": {
        "name": "ShareASale",
        "signup_url": "https://www.shareasale.com/",
        "description": "Easy approval — access FreshBooks, Moz Pro, SpyFu, Rankmath and many SaaS tools",
        "link_format": "https://shareasale.com/r.cfm?b=[BANNER_ID]&u=[USER_ID]&m=[MERCHANT_ID]",
    },
}


def get_network_signups() -> list[dict]:
    networks_used: set[str] = set()
    for programs in PROGRAMS.values():
        for p in programs:
            net = p.get("network", "direct")
            if net in NETWORK_SIGNUPS:
                networks_used.add(net)
    result = []
    for net_key in ("impact", "partnerstack", "shareasale"):
        if net_key in networks_used:
            entry = dict(NETWORK_SIGNUPS[net_key])
            entry["key"] = net_key
            tools_on_network = [
                p["name"]
                for programs in PROGRAMS.values()
                for p in programs
                if p.get("network") == net_key
            ]
            entry["tools"] = sorted(set(tools_on_network))
            result.append(entry)
    return result


for _programs in PROGRAMS.values():
    for _p in _programs:
        _net = _p.get("network", "direct")
        _p["network_signup"] = NETWORK_SIGNUPS[_net]["signup_url"] if _net in NETWORK_SIGNUPS else None


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
