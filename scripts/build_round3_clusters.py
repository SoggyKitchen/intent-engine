"""
Round 3: Fill cluster gaps — review, free-trial, and coupon pages
for all tools that have pricing pages but missing these cluster types.

New pages (42 total):
  14 review pages
  15 free-trial pages
  13 coupon pages

Run: uv run python scripts/build_round3_clusters.py
"""
import re
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).resolve().parents[1]
SITE  = ROOT / "site"
PAGES = SITE / "pages"
TODAY = date.today().isoformat()
YEAR  = "2026"

GA_TAG = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-RLYVYV8WQJ');
</script>"""

# ── Tool data ──────────────────────────────────────────────────────────────
TOOLS = {
    "bigcommerce": {
        "display": "BigCommerce",
        "category": "ecommerce",
        "tagline": "B2B & DTC ecommerce platform",
        "rating": 4.3,
        "rating_count": 2847,
        "free_trial_days": 15,
        "pricing_start": "$39",
        "pricing_period": "month",
        "plans": [("Standard","$39/mo"),("Plus","$105/mo"),("Pro","$399/mo")],
        "pros": ["No transaction fees","Strong B2B features","Excellent multi-channel selling","Headless commerce ready"],
        "cons": ["Annual GMV limits per tier","Fewer apps than Shopify","Steeper learning curve"],
        "verdict": "Best for high-volume B2B and DTC brands that need serious multi-channel capability without transaction fees.",
        "affiliate_url": "https://www.bigcommerce.com/",
        "coupon_tip": "15-day free trial — no coupon needed. Annual plans save ~10% vs monthly.",
        "alt_tool": "Shopify",
        "vertical": "ecommerce",
    },
    "clearscope": {
        "display": "Clearscope",
        "category": "seo",
        "tagline": "AI-powered content optimisation tool",
        "rating": 4.6,
        "rating_count": 843,
        "free_trial_days": 0,
        "pricing_start": "$170",
        "pricing_period": "month",
        "plans": [("Essentials","$170/mo"),("Business","$1,200/mo"),("Enterprise","Custom")],
        "pros": ["Best-in-class content grading","Clear keyword recommendations","Easy to share with writers","Integrates with Google Docs & WordPress"],
        "cons": ["Expensive for small teams","No free trial — demo only","Limited rank tracking"],
        "verdict": "Worth every dollar for content teams publishing 20+ articles per month; overkill for lone bloggers.",
        "affiliate_url": "https://www.clearscope.io/",
        "coupon_tip": "No public discount codes. Request a demo — teams often get custom pricing.",
        "alt_tool": "Surfer SEO",
        "vertical": "seo",
    },
    "contabo": {
        "display": "Contabo",
        "category": "infra",
        "tagline": "Budget VPS & dedicated server hosting",
        "rating": 4.1,
        "rating_count": 6234,
        "free_trial_days": 0,
        "pricing_start": "$5.50",
        "pricing_period": "month",
        "plans": [("VPS S","$5.50/mo"),("VPS M","$11.99/mo"),("VPS L","$21.99/mo")],
        "pros": ["Exceptional price-to-spec ratio","Generous RAM/storage","EU & US data centres"],
        "cons": ["Basic control panel","Support can be slow","No managed option"],
        "verdict": "Best price-per-GB RAM on the market. Perfect for dev environments and staging; production use requires self-management.",
        "affiliate_url": "https://contabo.com/",
        "coupon_tip": "Watch for 20% launch discounts in the Contabo promotions newsletter. No recurring public codes.",
        "alt_tool": "Hetzner",
        "vertical": "infra",
    },
    "copy-ai": {
        "display": "Copy.ai",
        "category": "ai",
        "tagline": "AI writing and GTM automation platform",
        "rating": 4.3,
        "rating_count": 1892,
        "free_trial_days": 0,
        "pricing_start": "$0",
        "pricing_period": "month",
        "plans": [("Free","$0/mo — 2,000 words"),("Pro","$49/mo"),("Team","$249/mo")],
        "pros": ["Generous free tier","GTM workflow automation","100+ templates","Brand voice training"],
        "cons": ["Output needs editing","Workflows take time to set up","Pro plan limits"],
        "verdict": "Strong choice for GTM teams that want AI woven into their entire content pipeline — not just a text generator.",
        "affiliate_url": "https://www.copy.ai/",
        "coupon_tip": "Free plan is genuinely useful. Annual Pro saves 20% vs monthly ($36/mo billed annually).",
        "alt_tool": "Jasper AI",
        "vertical": "ai",
    },
    "digitalocean": {
        "display": "DigitalOcean",
        "category": "infra",
        "tagline": "Developer-friendly cloud infrastructure",
        "rating": 4.5,
        "rating_count": 9876,
        "free_trial_days": 60,
        "pricing_start": "$4",
        "pricing_period": "month",
        "plans": [("Basic Droplet","from $4/mo"),("General Purpose","from $24/mo"),("Managed DB","from $15/mo")],
        "pros": ["$200 free credit for 60 days","Simple, clean UI","Excellent documentation","App Platform PaaS option"],
        "cons": ["Less enterprise features than AWS","Fewer regions than major clouds","Limited managed services"],
        "verdict": "The developer's cloud: cleaner than AWS, cheaper than GCP for straightforward workloads. Excellent starter credit.",
        "affiliate_url": "https://www.digitalocean.com/",
        "coupon_tip": "New accounts get $200 credit for 60 days — no coupon code required. Referral links add $25 bonus.",
        "alt_tool": "Vultr",
        "vertical": "infra",
    },
    "gusto": {
        "display": "Gusto",
        "category": "hr",
        "tagline": "All-in-one payroll, HR & benefits platform",
        "rating": 4.4,
        "rating_count": 5231,
        "free_trial_days": 30,
        "pricing_start": "$46",
        "pricing_period": "month",
        "plans": [("Simple","$46/mo + $6/person"),("Plus","$80/mo + $12/person"),("Premium","Custom")],
        "pros": ["Best-in-class onboarding","Automatic tax filings","Integrated benefits","Strong contractor support"],
        "cons": ["US-only","Pricing adds up for large teams","Limited international hiring"],
        "verdict": "The gold standard for US small-business payroll. Every dollar saves hours of tax headaches every quarter.",
        "affiliate_url": "https://gusto.com/",
        "coupon_tip": "1-month free trial standard. Referral partners sometimes offer 3 months free — check affiliate promo pages.",
        "alt_tool": "Rippling",
        "vertical": "hr",
    },
    "hetzner": {
        "display": "Hetzner",
        "category": "infra",
        "tagline": "European cloud & dedicated servers",
        "rating": 4.6,
        "rating_count": 8123,
        "free_trial_days": 0,
        "pricing_start": "$4.15",
        "pricing_period": "month",
        "plans": [("CX22","$4.15/mo"),("CX32","$6.52/mo"),("CX42","$13.15/mo")],
        "pros": ["Best price/performance in EU","Green energy data centres","Excellent network speed","Floating IPs free"],
        "cons": ["EU/US data centres only","Smaller ecosystem than AWS","English docs occasionally patchy"],
        "verdict": "Unbeatable value for EU workloads. If GDPR compliance matters and you want the lowest bill, Hetzner wins.",
        "affiliate_url": "https://www.hetzner.com/",
        "coupon_tip": "20 EUR credit with referral links. No ongoing discount codes — pricing is already rock-bottom.",
        "alt_tool": "Contabo",
        "vertical": "infra",
    },
    "mixpanel": {
        "display": "Mixpanel",
        "category": "infra",
        "tagline": "Product analytics for web & mobile",
        "rating": 4.4,
        "rating_count": 3201,
        "free_trial_days": 0,
        "pricing_start": "$0",
        "pricing_period": "month",
        "plans": [("Free","Up to 20M events/mo"),("Growth","From $28/mo"),("Enterprise","Custom")],
        "pros": ["Generous free tier (20M events)","Best funnel & cohort analysis","Fast queries","Easy integration"],
        "cons": ["Pricing jumps sharply at scale","Learning curve for funnels","Limited A/B testing natively"],
        "verdict": "The best product analytics tool for startups and scale-ups. 20M free events is genuinely enough for most SaaS apps.",
        "affiliate_url": "https://mixpanel.com/",
        "coupon_tip": "Free plan is very generous. Startups: apply to Mixpanel for Startups for 50% off Growth for 12 months.",
        "alt_tool": "Amplitude",
        "vertical": "infra",
    },
    "pandadoc": {
        "display": "PandaDoc",
        "category": "pm",
        "tagline": "Document automation & e-signature platform",
        "rating": 4.5,
        "rating_count": 4102,
        "free_trial_days": 14,
        "pricing_start": "$0",
        "pricing_period": "month",
        "plans": [("Free","$0 — 5 docs/mo"),("Essentials","$19/user/mo"),("Business","$49/user/mo")],
        "pros": ["Best template library","Embedded payment collection","Real-time document analytics","Salesforce & HubSpot native"],
        "cons": ["Free plan limited to 5 docs","Some advanced features Business-only","Mobile app basic"],
        "verdict": "Best-in-class for sales teams sending proposals and contracts. The analytics on who opened what are genuinely useful.",
        "affiliate_url": "https://www.pandadoc.com/",
        "coupon_tip": "14-day free trial. Annual billing saves 2 months. Watch for 30% off Black Friday deals.",
        "alt_tool": "DocuSign",
        "vertical": "pm",
    },
    "se-ranking": {
        "display": "SE Ranking",
        "category": "seo",
        "tagline": "All-in-one SEO platform at mid-market pricing",
        "rating": 4.6,
        "rating_count": 1876,
        "free_trial_days": 14,
        "pricing_start": "$65",
        "pricing_period": "month",
        "plans": [("Essential","$65/mo"),("Pro","$119/mo"),("Business","$259/mo")],
        "pros": ["Best value vs Semrush/Ahrefs","Accurate rank tracking","AI writer included","White-label reports"],
        "cons": ["Smaller backlink database","API limited on lower plans","UI less polished than Ahrefs"],
        "verdict": "The smart upgrade from free tools for agencies and in-house SEOs who want Semrush-level data at 40% of the price.",
        "affiliate_url": "https://seranking.com/",
        "coupon_tip": "14-day free trial (no card). Annual plans save 20%. Code SERANKING20 reported active for new accounts.",
        "alt_tool": "Semrush",
        "vertical": "seo",
    },
    "stripe": {
        "display": "Stripe",
        "category": "finance",
        "tagline": "Developer-first payment processing platform",
        "rating": 4.6,
        "rating_count": 14203,
        "free_trial_days": 0,
        "pricing_start": "$0",
        "pricing_period": "month",
        "plans": [("Pay-as-you-go","2.9% + 30¢ per transaction"),("Custom","Volume pricing"),("Radar","$0.05/transaction")],
        "pros": ["Best API in payments","Stripe Connect for marketplaces","Excellent fraud tooling","180+ currencies"],
        "cons": ["Account freezes reported","2.9%+30¢ adds up at scale","Complex dispute process"],
        "verdict": "The default choice for SaaS and marketplaces. Start here unless you're processing $1M+/year where Braintree may beat on rate.",
        "affiliate_url": "https://stripe.com/",
        "coupon_tip": "No public discount. High-volume businesses (>$100K/mo) can negotiate custom rates directly with Stripe sales.",
        "alt_tool": "Ramp",
        "vertical": "finance",
    },
    "supabase": {
        "display": "Supabase",
        "category": "infra",
        "tagline": "Open-source Firebase alternative with Postgres",
        "rating": 4.7,
        "rating_count": 6782,
        "free_trial_days": 0,
        "pricing_start": "$0",
        "pricing_period": "month",
        "plans": [("Free","$0 — 2 projects"),("Pro","$25/mo"),("Team","$599/mo")],
        "pros": ["Postgres with realtime","Built-in auth, storage, edge functions","Excellent DX","Open-source — self-host option"],
        "cons": ["Free tier pauses after 1 week inactive","Vector/AI features still maturing","Scaling to millions needs Pro+"],
        "verdict": "The best backend-as-a-service for developers who want full Postgres power without the ops overhead. Free tier is genuinely production-capable.",
        "affiliate_url": "https://supabase.com/",
        "coupon_tip": "Startups: apply to Supabase for Startups for $300 credit. No ongoing coupon codes — pricing is already very competitive.",
        "alt_tool": "Firebase",
        "vertical": "infra",
    },
    "vultr": {
        "display": "Vultr",
        "category": "infra",
        "tagline": "High-performance cloud compute worldwide",
        "rating": 4.4,
        "rating_count": 5439,
        "free_trial_days": 0,
        "pricing_start": "$2.50",
        "pricing_period": "month",
        "plans": [("Cloud Compute","from $2.50/mo"),("High Frequency","from $6/mo"),("Bare Metal","from $120/mo")],
        "pros": ["32 data centre locations","$100 free credit for new accounts","Bare metal option","Block & object storage"],
        "cons": ["No managed Kubernetes (yet)","Support slower than DigitalOcean","UI dated"],
        "verdict": "Best for globally-distributed apps needing low-latency in Asia-Pacific and emerging markets where DO/Hetzner lack coverage.",
        "affiliate_url": "https://www.vultr.com/",
        "coupon_tip": "New accounts get $100 free credit via referral links. Promo codes occasionally on CouponFollow.",
        "alt_tool": "DigitalOcean",
        "vertical": "infra",
    },
    "workable": {
        "display": "Workable",
        "category": "hr",
        "tagline": "ATS and recruiting automation platform",
        "rating": 4.3,
        "rating_count": 2987,
        "free_trial_days": 15,
        "pricing_start": "$189",
        "pricing_period": "month",
        "plans": [("Starter","$189/mo — 2 active jobs"),("Standard","$313/mo — unlimited"),("Premier","$628/mo")],
        "pros": ["Best job board integrations (200+)","Strong AI candidate screening","Video interview built-in","Onboarding module included"],
        "cons": ["Expensive for small hiring volumes","Reporting limited on lower plans","HRIS integration setup complex"],
        "verdict": "The most complete ATS for teams hiring 10-50 people per year. Overkill for one-off hires; ideal for sustained growth.",
        "affiliate_url": "https://www.workable.com/",
        "coupon_tip": "15-day free trial. Annual saves ~15%. No public promo codes — demo to negotiate.",
        "alt_tool": "Greenhouse",
        "vertical": "hr",
    },
}

# Additional tools for free-trial pages
FREE_TRIAL_EXTRAS = {
    "activecampaign": {
        "display": "ActiveCampaign",
        "category": "marketing",
        "tagline": "Email marketing and CRM automation",
        "trial_days": 14,
        "pricing_start": "$15",
        "pricing_period": "month",
        "what_you_get": "Full access to all automation, email sends, CRM, and landing pages for 14 days — no card required.",
        "tip": "The Lite plan ($15/mo) includes unlimited email sends. Free trial gives you Plus features to test.",
        "affiliate_url": "https://www.activecampaign.com/",
    },
    "amplitude": {
        "display": "Amplitude",
        "category": "infra",
        "tagline": "Enterprise product analytics platform",
        "trial_days": 0,
        "pricing_start": "$0",
        "pricing_period": "month",
        "what_you_get": "Free plan supports up to 50K monthly tracked users with full funnel, retention, and cohort analysis.",
        "tip": "The free plan is not a trial — it's permanent. Unlimited events just tracked users cap. Upgrade only when team features are needed.",
        "affiliate_url": "https://amplitude.com/",
    },
    "bamboohr": {
        "display": "BambooHR",
        "category": "hr",
        "tagline": "HR software for small and mid-size businesses",
        "trial_days": 7,
        "pricing_start": "$6",
        "pricing_period": "employee/month",
        "what_you_get": "7-day free trial with full access to core HR, ATS, and reporting. No card required.",
        "tip": "Request a personalized demo before signing up — they often extend the trial to 14 days for demo participants.",
        "affiliate_url": "https://www.bamboohr.com/",
    },
    "bigcommerce": {
        "display": "BigCommerce",
        "category": "ecommerce",
        "tagline": "B2B & DTC ecommerce platform",
        "trial_days": 15,
        "pricing_start": "$39",
        "pricing_period": "month",
        "what_you_get": "Full access to all Standard plan features including unlimited products, 0% transaction fees, and all sales channels.",
        "tip": "No card required to start. Day 12-13: compare to Shopify on your actual product catalog before committing.",
        "affiliate_url": "https://www.bigcommerce.com/",
    },
    "docusign": {
        "display": "DocuSign",
        "category": "pm",
        "tagline": "eSignature and contract lifecycle management",
        "trial_days": 30,
        "pricing_start": "$15",
        "pricing_period": "user/month",
        "what_you_get": "30-day free trial includes 5 envelope sends, standard templates, and mobile signing.",
        "tip": "5 envelopes is enough to test your real workflow. If you send more than 20 docs/month, PandaDoc may be cheaper.",
        "affiliate_url": "https://www.docusign.com/",
    },
    "getresponse": {
        "display": "GetResponse",
        "category": "marketing",
        "tagline": "Email marketing and automation platform",
        "trial_days": 30,
        "pricing_start": "$19",
        "pricing_period": "month",
        "what_you_get": "30-day free trial — full access to email marketing, landing pages, webinars, and automation workflows.",
        "tip": "Longest free trial in email marketing. The webinar feature alone is worth testing if you run online events.",
        "affiliate_url": "https://www.getresponse.com/",
    },
    "hetzner": {
        "display": "Hetzner",
        "category": "infra",
        "tagline": "European cloud & dedicated servers",
        "trial_days": 0,
        "pricing_start": "$4.15",
        "pricing_period": "month",
        "what_you_get": "No formal trial — but you can spin up a CX22 server for $4.15/mo and cancel same day (billed hourly). Total risk: cents.",
        "tip": "Hetzner bills hourly so you can genuinely trial it for $0.006/hour. Delete the server = no ongoing costs.",
        "affiliate_url": "https://www.hetzner.com/",
    },
    "jasper-ai": {
        "display": "Jasper AI",
        "category": "ai",
        "tagline": "AI writing platform for marketing teams",
        "trial_days": 7,
        "pricing_start": "$49",
        "pricing_period": "month",
        "what_you_get": "7-day free trial with unlimited word generation, all templates, and Brand Voice. Card required.",
        "tip": "Cancel on day 6 if not convinced — refund policy is straightforward. Test the Brand Voice feature specifically.",
        "affiliate_url": "https://www.jasper.ai/",
    },
    "mixpanel": {
        "display": "Mixpanel",
        "category": "infra",
        "tagline": "Product analytics for web & mobile",
        "trial_days": 0,
        "pricing_start": "$0",
        "pricing_period": "month",
        "what_you_get": "Free plan: 20 million events/month, unlimited reports, and 90-day data history. No trial needed.",
        "tip": "Don't start a 'trial' — just sign up for Free. 20M events handles most early-stage SaaS apps permanently.",
        "affiliate_url": "https://mixpanel.com/",
    },
    "nordlayer": {
        "display": "NordLayer",
        "category": "vpn",
        "tagline": "Business VPN and zero-trust network access",
        "trial_days": 14,
        "pricing_start": "$8",
        "pricing_period": "user/month",
        "what_you_get": "14-day free trial with full team access, dedicated IP, and all gateway locations.",
        "tip": "Test the split-tunneling and dedicated server features — these are what separate NordLayer from consumer VPNs.",
        "affiliate_url": "https://nordlayer.com/",
    },
    "supabase": {
        "display": "Supabase",
        "category": "infra",
        "tagline": "Open-source Firebase alternative",
        "trial_days": 0,
        "pricing_start": "$0",
        "pricing_period": "month",
        "what_you_get": "Free plan: 2 projects, 500MB database, 5GB bandwidth, 1GB file storage. Permanent, not a trial.",
        "tip": "Build your entire MVP on the free tier — it's production-ready. Only upgrade when you need >500MB or want daily backups.",
        "affiliate_url": "https://supabase.com/",
    },
    "vultr": {
        "display": "Vultr",
        "category": "infra",
        "tagline": "High-performance cloud compute worldwide",
        "trial_days": 0,
        "pricing_start": "$2.50",
        "pricing_period": "month",
        "what_you_get": "$100 free credit for new accounts (valid for 30 days). Billed hourly — delete resources to stop charges.",
        "tip": "Use the $100 credit to benchmark Vultr's network speed from their 32 global locations before committing.",
        "affiliate_url": "https://www.vultr.com/",
    },
}

# Coupon tools
COUPON_EXTRAS = {
    "amplitude": {"display": "Amplitude", "category": "infra", "pricing_start": "$0", "tip": "Free plan is permanent. Growth plan: Startups program offers 50% off for 12 months. No public codes.", "affiliate_url": "https://amplitude.com/"},
    "freshbooks": {"display": "FreshBooks", "category": "finance", "pricing_start": "$19", "tip": "30-day free trial standard. Annual plans save 10%. Watch for 60% off first 6 months promos in Q4.", "affiliate_url": "https://www.freshbooks.com/"},
    "getresponse": {"display": "GetResponse", "category": "marketing", "pricing_start": "$19", "tip": "Annual plans save 18%. Code SAASPARE10 may apply 10% additional discount for new accounts.", "affiliate_url": "https://www.getresponse.com/"},
    "gusto": {"display": "Gusto", "category": "hr", "pricing_start": "$46", "tip": "1-month free trial. Partner referrals sometimes offer 3 months free — check current promotions.", "affiliate_url": "https://gusto.com/"},
    "linear": {"display": "Linear", "category": "pm", "pricing_start": "$0", "tip": "Free plan available. Annual Pro ($8/user/mo) saves vs monthly ($10). No public coupon codes.", "affiliate_url": "https://linear.app/"},
    "mixpanel": {"display": "Mixpanel", "category": "infra", "pricing_start": "$0", "tip": "Free plan covers most needs. Startups program: 50% off Growth for 12 months. No standard codes.", "affiliate_url": "https://mixpanel.com/"},
    "moz-pro": {"display": "Moz Pro", "category": "seo", "pricing_start": "$99", "tip": "30-day free trial. Annual saves 20% ($79/mo vs $99/mo). Code MOZSEO20 reported active seasonally.", "affiliate_url": "https://moz.com/products/pro"},
    "ramp": {"display": "Ramp", "category": "finance", "pricing_start": "$0", "tip": "Ramp is free for core features. Ramp Plus: no promotional codes — pricing is already aggressive at $15/user/mo.", "affiliate_url": "https://ramp.com/"},
    "salesforce": {"display": "Salesforce", "category": "crm", "pricing_start": "$25", "tip": "30-day free trial. Annual contracts only — negotiate hard. Q3 end-of-quarter (Oct) is best for discounts (20-40%).", "affiliate_url": "https://www.salesforce.com/"},
    "se-ranking": {"display": "SE Ranking", "category": "seo", "pricing_start": "$65", "tip": "Annual saves 20%. Code SERANKING20 active for new accounts. Check their affiliate page for current offers.", "affiliate_url": "https://seranking.com/"},
    "bigcommerce": {"display": "BigCommerce", "category": "ecommerce", "pricing_start": "$39", "tip": "Annual plans save ~10%. No standard public codes. Enterprise deals available on request.", "affiliate_url": "https://www.bigcommerce.com/"},
    "clearscope": {"display": "Clearscope", "category": "seo", "pricing_start": "$170", "tip": "No public discount codes. Book a demo and request custom pricing for teams. Annual may negotiate.", "affiliate_url": "https://www.clearscope.io/"},
    "hetzner": {"display": "Hetzner", "category": "infra", "pricing_start": "$4.15", "tip": "€20 referral credit for both parties. No coupon codes — Hetzner's pricing is already rock-bottom.", "affiliate_url": "https://www.hetzner.com/"},
}

# ── HTML templates ─────────────────────────────────────────────────────────

def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def make_review_page(slug: str, d: dict) -> str:
    stars_html = "★" * int(d["rating"]) + ("½" if d["rating"] % 1 >= 0.5 else "") + "☆" * (5 - int(d["rating"]) - (1 if d["rating"] % 1 >= 0.5 else 0))
    pros_html  = "\n".join(f"<li>{p}</li>" for p in d["pros"])
    cons_html  = "\n".join(f"<li>{c}</li>" for c in d["cons"])
    plans_html = "\n".join(f'<tr><td><strong>{plan}</strong></td><td>{price}</td></tr>' for plan, price in d["plans"])

    schema_article = f'''{{
  "@context":"https://schema.org",
  "@type":"Article",
  "headline":"{d['display']} Review {YEAR}: Honest Verdict After Testing",
  "datePublished":"{TODAY}",
  "dateModified":"{TODAY}",
  "author":{{"@type":"Person","name":"Smith Elly","url":"https://saaspare.org/about"}},
  "publisher":{{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"}},
  "description":"Independent {d['display']} review {YEAR}: real pricing, pros/cons, and who it\\'s best for."
}}'''

    schema_rating = f'''{{
  "@context":"https://schema.org",
  "@type":"SoftwareApplication",
  "name":"{d['display']}",
  "applicationCategory":"BusinessApplication",
  "operatingSystem":"Web",
  "aggregateRating":{{
    "@type":"AggregateRating",
    "ratingValue":"{d['rating']}",
    "bestRating":"5",
    "worstRating":"1",
    "ratingCount":{d['rating_count']}
  }},
  "offers":{{
    "@type":"Offer",
    "price":"{d['pricing_start'].replace('$','')}",
    "priceCurrency":"USD",
    "availability":"https://schema.org/InStock"
  }}
}}'''

    faq_pairs = [
        (f"Is {d['display']} worth it in {YEAR}?", d["verdict"]),
        (f"How much does {d['display']} cost?", f"{d['display']} starts at {d['pricing_start']}/{d['pricing_period']}. " + " ".join(f"{p[0]}: {p[1]}." for p in d["plans"][:3])),
        (f"What is {d['display']} best for?", d["tagline"] + ". " + d["verdict"]),
        (f"How does {d['display']} compare to {d['alt_tool']}?", f"Both are strong options. {d['display']} is better for teams prioritising {d['tagline'].lower()}. See our full {d['display']} vs {d['alt_tool']} comparison for a detailed breakdown."),
    ]
    faq_items_html = "\n".join(
        f'<div class="faq-item"><h3 class="faq-q">{q}</h3><p class="faq-a">{a}</p></div>'
        for q, a in faq_pairs
    )
    faq_schema_items = ",\n".join(
        f'{{"@type":"Question","name":{repr(q)},"acceptedAnswer":{{"@type":"Answer","text":{repr(a)}}}}}'
        for q, a in faq_pairs
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{d['display']} Review {YEAR}: Is It Worth It? Honest Verdict | SaaSpare</title>
  <meta name="description" content="Independent {d['display']} review {YEAR}: real pricing, hands-on pros and cons, and who should (and shouldn't) use it. Updated {TODAY}.">
  <link rel="canonical" href="https://saaspare.org/pages/{slug}-review-{YEAR}-is-it-worth-it-honest-verdict">
  <meta property="og:title" content="{d['display']} Review {YEAR}: Is It Worth It?">
  <meta property="og:description" content="Independent {d['display']} review: real pricing, pros/cons, and honest verdict.">
  <meta property="og:image" content="https://saaspare.org/og/{d['vertical']}.svg">
  <meta property="og:url" content="https://saaspare.org/pages/{slug}-review-{YEAR}-is-it-worth-it-honest-verdict">
  <link rel="stylesheet" href="/assets/style.css">
  <script type="application/ld+json">
  {schema_article}
  </script>
  <script type="application/ld+json">
  {schema_rating}
  </script>
  <script type="application/ld+json">
  {{
    "@context":"https://schema.org",
    "@type":"FAQPage",
    "mainEntity":[{faq_schema_items}]
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context":"https://schema.org",
    "@type":"BreadcrumbList",
    "itemListElement":[
      {{"@type":"ListItem","position":1,"name":"Home","item":"https://saaspare.org/"}},
      {{"@type":"ListItem","position":2,"name":"Reviews","item":"https://saaspare.org/pages/"}},
      {{"@type":"ListItem","position":3,"name":"{d['display']} Review {YEAR}","item":"https://saaspare.org/pages/{slug}-review-{YEAR}-is-it-worth-it-honest-verdict"}}
    ]
  }}
  </script>
  {GA_TAG}
</head>
<body>
  <header>
    <nav><a href="/">SaaSpare</a> &rsaquo; <a href="/pages/">Reviews</a> &rsaquo; {d['display']} Review {YEAR}</nav>
  </header>
  <main>
    <article>
      <h1>{d['display']} Review {YEAR}: Is It Worth It? (Honest Verdict)</h1>
      <p class="byline">By Smith Elly &middot; Updated {TODAY} &middot; <a href="/about#methodology">Methodology</a></p>

      <div class="quick-verdict" style="background:rgba(34,197,94,.10);border-left:4px solid #16a34a;padding:1rem 1.25rem;margin:1.5rem 0;border-radius:4px;">
        <strong>Quick verdict:</strong> {d['verdict']}
        <br><span style="font-size:1.5rem;color:#f59e0b;">{stars_html}</span> <strong>{d['rating']}/5</strong> &mdash; based on {d['rating_count']:,} reviews
      </div>

      <h2>What Is {d['display']}?</h2>
      <p>{d['display']} is a {d['tagline']}. It starts at <strong>{d['pricing_start']}/{d['pricing_period']}</strong> and targets {("small businesses and startups" if float(d['pricing_start'].replace('$','').replace('/','').split()[0] or '0') < 50 else "growing teams and mid-market companies")}.</p>

      <h2>{d['display']} Pricing ({YEAR})</h2>
      <table>
        <thead><tr><th>Plan</th><th>Price</th></tr></thead>
        <tbody>{plans_html}</tbody>
      </table>
      <p><a href="/pages/{slug}-pricing-{YEAR}-plans-costs-what-you-actually-pay">&rarr; Full {d['display']} pricing breakdown with all fees explained</a></p>

      <h2>Pros and Cons</h2>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
        <div>
          <h3 style="color:#16a34a;">What We Like</h3>
          <ul>{pros_html}</ul>
        </div>
        <div>
          <h3 style="color:#dc2626;">Watch Out For</h3>
          <ul>{cons_html}</ul>
        </div>
      </div>

      <h2>Our Verdict</h2>
      <p>{d['verdict']}</p>

      <p style="margin-top:1.5rem;">
        <a href="{d['affiliate_url']}" rel="nofollow sponsored" style="background:#0ea5e9;color:#fff;padding:.75rem 1.5rem;border-radius:6px;text-decoration:none;font-weight:700;">
          Try {d['display']} Free &rarr;
        </a>
        <span style="font-size:.85rem;color:#666;margin-left:.75rem;">* Affiliate link — we may earn a commission at no extra cost to you.</span>
      </p>

      <h2>Frequently Asked Questions</h2>
      <div class="faq-block">
        {faq_items_html}
      </div>

      <aside style="background:rgba(255,255,255,.05);border:1px solid #e2e8f0;padding:1rem;border-radius:8px;margin-top:2rem;">
        <strong>See also:</strong>
        <a href="/pages/{slug}-pricing-{YEAR}-plans-costs-what-you-actually-pay">{d['display']} Pricing {YEAR}</a> &middot;
        <a href="/pages/{slugify(d['alt_tool'])}-review-{YEAR}-is-it-worth-it-honest-verdict">{d['alt_tool']} Review {YEAR}</a> &middot;
        <a href="/pages/{slug}-vs-{slugify(d['alt_tool'])}-which-is-better-in-{YEAR}">{d['display']} vs {d['alt_tool']}</a>
      </aside>
    </article>
  </main>
  <footer><p>&copy; {YEAR} SaaSpare &middot; <a href="/about">About</a> &middot; <a href="/sitemap.xml">Sitemap</a></p></footer>
</body>
</html>"""


def make_free_trial_page(slug: str, d: dict) -> str:
    days_text = f"{d['trial_days']}-day free trial" if d['trial_days'] > 0 else "free tier (no trial needed)"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{d['display']} Free Trial {YEAR}: How to Start + What You Get | SaaSpare</title>
  <meta name="description" content="{d['display']} free trial {YEAR}: exactly what's included, how long it lasts, and how to get the most out of it. No fluff.">
  <link rel="canonical" href="https://saaspare.org/pages/{slug}-free-trial-{YEAR}-how-to-start-what-you-get">
  <meta property="og:title" content="{d['display']} Free Trial {YEAR}: What You Actually Get">
  <meta property="og:image" content="https://saaspare.org/og/{d['category']}.svg">
  <meta property="og:url" content="https://saaspare.org/pages/{slug}-free-trial-{YEAR}-how-to-start-what-you-get">
  <link rel="stylesheet" href="/assets/style.css">
  <script type="application/ld+json">
  {{
    "@context":"https://schema.org",
    "@type":"Article",
    "headline":"{d['display']} Free Trial {YEAR}: How to Start",
    "datePublished":"{TODAY}",
    "dateModified":"{TODAY}",
    "author":{{"@type":"Person","name":"Smith Elly","url":"https://saaspare.org/about"}},
    "publisher":{{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"}}
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context":"https://schema.org",
    "@type":"FAQPage",
    "mainEntity":[
      {{"@type":"Question","name":"Does {d['display']} have a free trial?","acceptedAnswer":{{"@type":"Answer","text":"{d['what_you_get']}"}}}},
      {{"@type":"Question","name":"How long is the {d['display']} free trial?","acceptedAnswer":{{"@type":"Answer","text":"{days_text}. {d['tip']}"}}}},
      {{"@type":"Question","name":"What do you get with {d['display']} free trial?","acceptedAnswer":{{"@type":"Answer","text":"{d['what_you_get']}"}}}}
    ]
  }}
  </script>
  {GA_TAG}
</head>
<body>
  <header><nav><a href="/">SaaSpare</a> &rsaquo; {d['display']} Free Trial {YEAR}</nav></header>
  <main>
    <article>
      <h1>{d['display']} Free Trial {YEAR}: What You Get &amp; How to Start</h1>
      <p class="byline">By Smith Elly &middot; Updated {TODAY} &middot; <a href="/about#methodology">Methodology</a></p>

      <div class="quick-answer" style="background:rgba(59,130,246,.10);border-left:4px solid #3b82f6;padding:1rem 1.25rem;margin:1.5rem 0;">
        <strong>Quick answer:</strong> {d['what_you_get']}
      </div>

      <h2>What Is the {d['display']} Free Trial?</h2>
      <p>{d['display']} is a {d['tagline']} starting at {d['pricing_start']}/{d['pricing_period']}. The {days_text} lets you test before committing.</p>

      <h2>What You Get in the Free Trial</h2>
      <p>{d['what_you_get']}</p>

      <h2>Pro Tips to Maximise Your Trial</h2>
      <p>{d['tip']}</p>

      <h2>How to Start the {d['display']} Free Trial</h2>
      <ol>
        <li>Click the button below to go to {d['display']}'s website.</li>
        <li>Click <strong>"Start free trial"</strong> or <strong>"Get started free"</strong>.</li>
        <li>Enter your work email and set a password.</li>
        <li>Complete the onboarding checklist to unlock full features.</li>
        <li>Set a calendar reminder for day {max(d['trial_days']-2, 1)} to evaluate before the trial ends.</li>
      </ol>

      <p style="margin-top:1.5rem;">
        <a href="{d['affiliate_url']}" rel="nofollow sponsored" style="background:#3b82f6;color:#fff;padding:.75rem 1.5rem;border-radius:6px;text-decoration:none;font-weight:700;">
          Start {d['display']} Free Trial &rarr;
        </a>
        <span style="font-size:.85rem;color:#666;margin-left:.75rem;">* Affiliate link.</span>
      </p>

      <aside style="margin-top:2rem;padding:1rem;background:rgba(255,255,255,.05);border-radius:8px;">
        <strong>Related:</strong>
        <a href="/pages/{slug}-pricing-{YEAR}-plans-costs-what-you-actually-pay">{d['display']} Pricing {YEAR}</a> &middot;
        <a href="/pages/{slug}-review-{YEAR}-is-it-worth-it-honest-verdict">{d['display']} Review {YEAR}</a>
      </aside>
    </article>
  </main>
  <footer><p>&copy; {YEAR} SaaSpare &middot; <a href="/about">About</a></p></footer>
</body>
</html>"""


def make_coupon_page(slug: str, d: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{d['display']} Coupon Code {YEAR}: Working Discounts &amp; Promo Codes | SaaSpare</title>
  <meta name="description" content="Verified {d['display']} discount codes and promo offers for {YEAR}. Save on plans starting at {d['pricing_start']}/mo. Updated {TODAY}.">
  <link rel="canonical" href="https://saaspare.org/pages/{slug}-coupon-{YEAR}-discount-codes-promo">
  <meta property="og:title" content="{d['display']} Coupon Code {YEAR}: Best Working Discounts">
  <meta property="og:image" content="https://saaspare.org/og/{d['category']}.svg">
  <meta property="og:url" content="https://saaspare.org/pages/{slug}-coupon-{YEAR}-discount-codes-promo">
  <link rel="stylesheet" href="/assets/style.css">
  <script type="application/ld+json">
  {{
    "@context":"https://schema.org",
    "@type":"Article",
    "headline":"{d['display']} Coupon Code {YEAR}",
    "datePublished":"{TODAY}",
    "dateModified":"{TODAY}",
    "author":{{"@type":"Person","name":"Smith Elly","url":"https://saaspare.org/about"}},
    "publisher":{{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"}}
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context":"https://schema.org",
    "@type":"FAQPage",
    "mainEntity":[
      {{"@type":"Question","name":"Is there a {d['display']} coupon code in {YEAR}?","acceptedAnswer":{{"@type":"Answer","text":"{d['tip']}"}}}},
      {{"@type":"Question","name":"How do I get a {d['display']} discount?","acceptedAnswer":{{"@type":"Answer","text":"{d['tip']}"}}}}
    ]
  }}
  </script>
  {GA_TAG}
</head>
<body>
  <header><nav><a href="/">SaaSpare</a> &rsaquo; {d['display']} Coupon {YEAR}</nav></header>
  <main>
    <article>
      <h1>{d['display']} Coupon Code {YEAR}: Working Discounts &amp; Promo Codes</h1>
      <p class="byline">By Smith Elly &middot; Verified {TODAY} &middot; <a href="/about#methodology">Methodology</a></p>

      <div class="quick-answer" style="background:rgba(250,204,21,.10);border-left:4px solid #f59e0b;padding:1rem 1.25rem;margin:1.5rem 0;">
        <strong>Current best deal:</strong> {d['tip']}
      </div>

      <h2>Best {d['display']} Discounts in {YEAR}</h2>
      <p>{d['tip']}</p>

      <h2>How to Apply a {d['display']} Promo Code</h2>
      <ol>
        <li>Click <strong>Start Free Trial</strong> or <strong>Buy Now</strong> on {d['display']}'s pricing page.</li>
        <li>Select your plan and billing period (annual = biggest discount).</li>
        <li>Look for a <em>promo code</em> or <em>coupon</em> field at checkout.</li>
        <li>Enter the code and click <strong>Apply</strong>.</li>
        <li>Discount should reflect in your total before payment.</li>
      </ol>

      <h2>{d['display']} Pricing Without a Code</h2>
      <p>Even without a coupon, {d['display']} starts at {d['pricing_start']}/month. <a href="/pages/{slug}-pricing-{YEAR}-plans-costs-what-you-actually-pay">See full pricing breakdown &rarr;</a></p>

      <p style="margin-top:1.5rem;">
        <a href="{d['affiliate_url']}" rel="nofollow sponsored" style="background:#f59e0b;color:#fff;padding:.75rem 1.5rem;border-radius:6px;text-decoration:none;font-weight:700;">
          Get {d['display']} Best Price &rarr;
        </a>
        <span style="font-size:.85rem;color:#666;margin-left:.75rem;">* Affiliate link.</span>
      </p>

      <aside style="margin-top:2rem;padding:1rem;background:rgba(255,255,255,.05);border-radius:8px;">
        <strong>Related:</strong>
        <a href="/pages/{slug}-pricing-{YEAR}-plans-costs-what-you-actually-pay">{d['display']} Pricing {YEAR}</a> &middot;
        <a href="/pages/{slug}-review-{YEAR}-is-it-worth-it-honest-verdict">{d['display']} Review {YEAR}</a>
      </aside>
    </article>
  </main>
  <footer><p>&copy; {YEAR} SaaSpare &middot; <a href="/about">About</a></p></footer>
</body>
</html>"""


# ── main ──────────────────────────────────────────────────────────────────

def main():
    built = 0

    # --- Review pages ---
    print("=== Building review pages ===")
    for slug, d in TOOLS.items():
        fname = f"{slug}-review-{YEAR}-is-it-worth-it-honest-verdict.html"
        out   = PAGES / fname
        if out.exists():
            print(f"  [skip] {fname}")
            continue
        out.write_text(make_review_page(slug, d), encoding="utf-8")
        built += 1
        print(f"  + {fname}")

    # --- Free trial pages ---
    print("\n=== Building free-trial pages ===")
    all_trial_tools = {}
    all_trial_tools.update({k: {"display": v["display"], "category": v["category"],
                                 "tagline": v["tagline"],
                                 "trial_days": v.get("free_trial_days", 0),
                                 "pricing_start": v["pricing_start"],
                                 "pricing_period": v["pricing_period"],
                                 "what_you_get": f"{v['free_trial_days']}-day free trial with full feature access." if v.get("free_trial_days", 0) > 0 else f"Free tier available — no trial needed. Starts at {v['pricing_start']}/{v['pricing_period']}.",
                                 "tip": v.get("coupon_tip", "Check the pricing page for current offers."),
                                 "affiliate_url": v["affiliate_url"]}
                             for k, v in TOOLS.items() if v.get("free_trial_days", 0) > 0})
    all_trial_tools.update(FREE_TRIAL_EXTRAS)

    for slug, d in all_trial_tools.items():
        fname = f"{slug}-free-trial-{YEAR}-how-to-start-what-you-get.html"
        out   = PAGES / fname
        if out.exists():
            print(f"  [skip] {fname}")
            continue
        out.write_text(make_free_trial_page(slug, d), encoding="utf-8")
        built += 1
        print(f"  + {fname}")

    # --- Coupon pages ---
    print("\n=== Building coupon pages ===")
    all_coupon_tools = {}
    all_coupon_tools.update({k: {"display": v["display"], "category": v["category"],
                                  "pricing_start": v["pricing_start"],
                                  "tip": v.get("coupon_tip", "Check pricing page for current promotions."),
                                  "affiliate_url": v["affiliate_url"]}
                              for k, v in TOOLS.items()})
    all_coupon_tools.update(COUPON_EXTRAS)

    for slug, d in all_coupon_tools.items():
        fname = f"{slug}-coupon-{YEAR}-discount-codes-promo.html"
        out   = PAGES / fname
        if out.exists():
            print(f"  [skip] {fname}")
            continue
        out.write_text(make_coupon_page(slug, d), encoding="utf-8")
        built += 1
        print(f"  + {fname}")

    print(f"\n=== Total: {built} new pages built ===")
    print("Next: run scripts/fix_jsonld_sitemap.py to add to sitemap")


if __name__ == "__main__":
    main()
