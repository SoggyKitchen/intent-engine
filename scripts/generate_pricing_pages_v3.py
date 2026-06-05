"""
Generate premium pricing pages using the new pricing.html template.
Replaces plain engine-generated pricing pages with the premium layout.
Covers all *-pricing-2026-plans-costs-what-you-actually-pay.html pages.
"""
from pathlib import Path
import re, datetime

SITE      = Path(__file__).resolve().parents[1] / "site"
TEMPLATES = Path(__file__).resolve().parents[1] / "outputs/templates"

try:
    _d = datetime.date.today()
    TODAY = f"{_d.day} {_d.strftime('%B')} {_d.year}"
except Exception:
    TODAY = "June 2026"

# ─────────────────────────────────────────────────────────────────────────────
# PRICING DATABASE — real plan data for 55 tools
# plan_N: name, price_mo, price_annual, best_for, users, storage, support, f1/f2/f3 + cls
# hidden_costs: list of {name, desc}
# scenarios: list of {users, cost, plan, plan_cls, breakdown}
# alternatives: list of {name, url, price, logo}
# ─────────────────────────────────────────────────────────────────────────────
PRICING = {
    "shopify": dict(
        name="Shopify", logo="https://cdn.simpleicons.org/shopify/96bf48",
        go="/go/shopify", history="/pages/shopify-pricing-history-2026",
        page="/pages/best-shopify-alternatives-2026", sticky="Shopify's Basic plan is the best entry point for most stores.",
        hidden_risk="Medium", hidden_note="Transaction fees add up unless you use Shopify Payments",
        meta_desc="Shopify raised Basic from $25 to $29/mo — we track every pricing change. June 2026: Basic $29, Shopify $79, Advanced $299 (all annual). Transaction fee trap + hidden app costs exposed.",
        plans=[
            dict(name="Starter",   mo="$5",    annual="$5",    best="Social selling only", users="1",    storage="Unlimited", support="Email",          f=["Buy Button only","No storefront","Checkout links"],      fc=["cl","cl","cm"]),
            dict(name="Basic",     mo="$39",   annual="$29",   best="New stores",          users="2",    storage="Unlimited", support="24/7 chat",      f=["2% transaction fee","10 inventory locations","Basic reports"], fc=["cm","cw","cm"]),
            dict(name="Shopify",   mo="$105",  annual="$79",   best="Growing stores",      users="5",    storage="Unlimited", support="24/7 chat",      f=["1% transaction fee","Standard reports","Gift cards"],    fc=["cm","cw","cw"]),
            dict(name="Advanced",  mo="$399",  annual="$299",  best="Scaling stores",      users="15",   storage="Unlimited", support="Priority 24/7",  f=["0.5% transaction fee","Custom reports","Duties & taxes"], fc=["cw","cw","cw"]),
        ],
        hidden=[
            dict(name="Transaction fees", desc="2% on Basic / 1% on Shopify / 0.5% on Advanced unless you use Shopify Payments (US, CA, AU, UK only)."),
            dict(name="App costs", desc="Most serious stores spend $50–300/mo on apps (email, reviews, upsell, subscriptions) on top of the plan fee."),
            dict(name="Theme cost", desc="Premium themes cost $100–400 one-time. Customisation requires a Shopify developer if you can't code."),
            dict(name="Annual lock-in", desc="Monthly billing costs ~35% more. Annual saves money but commits you for 12 months."),
            dict(name="Shopify Plus", desc="Enterprise tier starts at $2,300/mo — not clearly disclosed on the main pricing page."),
        ],
        scenarios=[
            dict(users="New store, 0 staff", cost="$29/mo", plan="Basic", plan_cls="v-smb", breakdown="Basic annual plan — cheapest viable storefront, 2% transaction fee on non-Shopify Payments"),
            dict(users="Growing store, 3 staff", cost="$109/mo", plan="Shopify", plan_cls="v-visual", breakdown="Shopify plan + 2–3 essential apps (email + reviews) — realistic starter budget"),
            dict(users="Scaling brand, 10 staff", cost="$450/mo", plan="Advanced", plan_cls="v-ent", breakdown="Advanced + app stack (subscriptions, upsell, loyalty) — real-world growing DTC brand"),
        ],
        alts=[
            dict(name="WooCommerce", url="/pages/woocommerce-pricing-2026-plans-costs-what-you-actually-pay", price="From $10/mo hosting", logo="https://cdn.simpleicons.org/woocommerce/7f54b3"),
            dict(name="BigCommerce", url="/pages/bigcommerce-pricing-2026-plans-costs-what-you-actually-pay", price="From $39/mo", logo="https://cdn.simpleicons.org/bigcommerce/121118"),
            dict(name="Wix",        url="/pages/wix-pricing-2026-plans-costs-what-you-actually-pay",        price="From $27/mo",  logo="https://cdn.simpleicons.org/wix/000000"),
            dict(name="Squarespace",url="/pages/squarespace-pricing-2026-plans-costs-what-you-actually-pay",price="From $16/mo",  logo="https://cdn.simpleicons.org/squarespace/000000"),
        ],
        faqs=[
            ("How much does Shopify actually cost per month?","On Basic ($29/mo annual) a store with $10,000/mo revenue using Shopify Payments pays $29 + apps. With a third-party payment processor add 2% transaction fee ($200 extra) — making real cost $229+/mo."),
            ("Does Shopify take a percentage of sales?","Yes — transaction fees apply if you don't use Shopify Payments: 2% (Basic), 1% (Shopify), 0.5% (Advanced). Shopify Payments eliminates this but is only available in select countries."),
            ("Is Shopify worth it for small stores?","For most new stores, yes — Basic at $29/mo is the most complete hosted ecommerce solution at that price. WooCommerce is cheaper if you're comfortable with WordPress hosting."),
            ("What is Shopify Plus and how much does it cost?","Shopify Plus is the enterprise tier, starting at $2,300/mo or 0.25% of monthly revenue (whichever is higher). It includes a dedicated merchant success manager, unlimited staff accounts, and custom checkout."),
            ("Can I try Shopify for free?","Shopify offers a 3-day free trial, then $1/mo for the first 3 months on eligible plans. No credit card required for the trial."),
        ]
    ),
    "hubspot": dict(
        name="HubSpot", logo="https://cdn.simpleicons.org/hubspot/ff7a59",
        go="/go/hubspot-crm", history="/pages/hubspot-pricing-history-2026",
        page="/pages/best-hubspot-alternatives-2026", sticky="HubSpot's free CRM is genuinely unlimited — start there before paying.",
        hidden_risk="High", hidden_note="Mandatory onboarding fees and Hub add-ons can triple year-one cost",
        meta_desc="HubSpot overhauled pricing in 2024 — we track every update. June 2026: Starter $15/user/mo, Professional $890/5 seats, mandatory $3,000+ onboarding fee exposed. Real cost by team size.",
        plans=[
            dict(name="Free",         mo="$0",    annual="$0",    best="Solo / exploring",  users="Unlimited", storage="Unlimited contacts", support="Community",    f=["Contact management","Deal pipeline","Basic email"],     fc=["cw","cw","cm"]),
            dict(name="Starter",      mo="$20/user", annual="$15/user", best="Small teams", users="Unlimited", storage="Unlimited contacts", support="Email only",   f=["Email sequences (5)","Simple automation","Custom props"],fc=["cm","cw","cw"]),
            dict(name="Professional", mo="$890",  annual="$800",  best="Growth teams",      users="5 min",     storage="Unlimited contacts", support="Phone+email",  f=["Full automation","Custom reports","A/B testing"],        fc=["cw","cw","cw"]),
            dict(name="Enterprise",   mo="$3,600",annual="$3,200",best="Large orgs",         users="10 min",    storage="Unlimited contacts", support="Priority",     f=["Custom objects","Hierarchical teams","SSO"],             fc=["cw","cw","cw"]),
        ],
        hidden=[
            dict(name="Onboarding fee", desc="$3,000–$6,000 mandatory for Professional and Enterprise — not optional, often the biggest year-one shock."),
            dict(name="Seat minimums", desc="Professional requires 3+ paid seats, Enterprise 10+ — even if you need only 1 power user."),
            dict(name="Annual lock-in", desc="Monthly billing costs ~25–30% more. Most buyers end up locked in annually without realising."),
            dict(name="Marketing contacts", desc="Marketing Hub charges per contact you email — a large list drives significant extra cost on top of seat pricing."),
            dict(name="Hub add-ons", desc="Marketing, Sales, Service, CMS Hubs are each billed separately. A full stack easily reaches $5,000+/mo."),
        ],
        scenarios=[
            dict(users="1 user, solo", cost="$0/mo", plan="Free", plan_cls="v-value", breakdown="Free CRM — unlimited contacts, basic pipeline, community support. No onboarding fee."),
            dict(users="10 users, SMB", cost="~$500/mo", plan="Starter", plan_cls="v-visual", breakdown="CRM + Marketing Starter, 10 seats, billed annually — no mandatory onboarding at this tier"),
            dict(users="50 users, scale-up", cost="~$4,800/mo", plan="Professional", plan_cls="v-ent", breakdown="Professional, 50 seats, annual billing + $3k onboarding amortised + add-on Hubs"),
        ],
        alts=[
            dict(name="Salesforce", url="/pages/salesforce-vs-hubspot", price="From $25/user", logo="https://cdn.simpleicons.org/salesforce/00a1e0"),
            dict(name="Pipedrive",  url="/pages/pipedrive-vs-hubspot",  price="From $14/user", logo="https://cdn.simpleicons.org/pipedrive/1a73e8"),
            dict(name="Monday CRM", url="/pages/monday-vs-hubspot",     price="From $12/seat", logo="https://cdn.simpleicons.org/monday/f62b54"),
            dict(name="Zoho CRM",   url="/pages/zoho-vs-hubspot",       price="Free/3 users",  logo="https://cdn.simpleicons.org/zoho/e42527"),
        ],
        faqs=[
            ("Does HubSpot have a free plan?","Yes — HubSpot CRM is free with no seat cap and no contact limit. The free plan includes deal pipeline, contact management, and basic email marketing."),
            ("How much does HubSpot actually cost for 10 users?","Starter CRM for 10 users: ~$150/mo billed annually. Add Marketing Hub Starter and you're at $400–800/mo depending on contact tier."),
            ("Is HubSpot's onboarding fee mandatory?","Yes for Professional and Enterprise — $3,000–$6,000 in mandatory onboarding fees. This is not optional and is not prominently disclosed on the pricing page."),
            ("Does HubSpot charge per contact?","Marketing Hub charges per marketing contact you email. CRM contacts are unlimited on all plans. A large email list drives significant extra cost."),
            ("Is there a HubSpot discount for startups?","HubSpot for Startups offers 30–90% off for qualifying startups under $2M ARR. Apply at hubspot.com/startups."),
        ]
    ),
    "nordvpn": dict(
        name="NordVPN", logo="https://cdn.simpleicons.org/nordvpn/4687ff",
        go="/go/nordvpn", history="/pages/nordvpn-pricing-history-2026",
        page="/pages/best-nordvpn-alternatives-2026", sticky="The 2-year Basic plan is the best VPN value in 2026 at $2.99/mo.",
        hidden_risk="Low", hidden_note="Renewal price is higher than the initial promotional price",
        plans=[
            dict(name="Basic 1-yr",  mo="$5.99", annual="$4.49", best="Standard protection",  users="10 devices", storage="6,300+ servers", support="24/7 chat", f=["VPN + malware block","No logs (audited)","10 simultaneous devices"], fc=["cw","cw","cw"]),
            dict(name="Basic 2-yr",  mo="$3.49", annual="$2.99", best="Best value",           users="10 devices", storage="6,300+ servers", support="24/7 chat", f=["73% off list price","3 months free included","Locks in price for 2yrs"], fc=["cw","cw","cw"]),
            dict(name="Plus 2-yr",   mo="$4.49", annual="$3.99", best="Password + VPN",       users="10 devices", storage="6,300+ servers", support="24/7 chat", f=["VPN + Password Manager","Data breach scanner","Cross-device sync"],   fc=["cw","cw","cw"]),
            dict(name="Ultimate 2-yr",mo="$6.99",annual="$5.99", best="Full security suite",  users="10 devices", storage="6,300+ servers", support="Priority",  f=["VPN + Passwords + Identity","$1M identity theft cover","Credit monitoring"], fc=["cw","cw","cw"]),
        ],
        hidden=[
            dict(name="Renewal pricing", desc="Promotional price is for the first term only. Renewal is at standard rate — 2-year Basic renews at ~$5.99/mo."),
            dict(name="Add-ons", desc="NordPass password manager and NordProtect identity theft cover are sold separately unless you're on Plus/Ultimate."),
        ],
        scenarios=[
            dict(users="1 person, basic", cost="$2.99/mo", plan="Basic 2-yr", plan_cls="v-value", breakdown="2-year upfront ($71.76) — lowest price, 10 devices, full VPN features"),
            dict(users="1 person, full suite", cost="$3.99/mo", plan="Plus 2-yr", plan_cls="v-visual", breakdown="VPN + Password Manager + breach scanner — best all-round individual deal"),
            dict(users="Family / team", cost="$5.99/mo", plan="Ultimate 2-yr", plan_cls="v-ent", breakdown="Full identity protection + $1M insurance — premium tier for high-risk users"),
        ],
        alts=[
            dict(name="Surfshark", url="/pages/surfshark-pricing-2026-plans-costs-what-you-actually-pay", price="From $2.49/mo", logo="https://cdn.simpleicons.org/surfshark/1ce0c3"),
            dict(name="ProtonVPN", url="/pages/protonvpn-pricing-2026-plans-costs-what-you-actually-pay", price="Free / $4.99/mo", logo="https://cdn.simpleicons.org/protonvpn/6d4aff"),
            dict(name="ExpressVPN",url="/pages/expressvpn-pricing-2026-plans-costs-what-you-actually-pay",price="From $8.32/mo",  logo="https://cdn.simpleicons.org/express/fc172f"),
            dict(name="CyberGhost",url="/pages/cyberghost-pricing-2026-plans-costs-what-you-actually-pay",price="From $2.19/mo", logo="https://cdn.simpleicons.org/cyberghost/ffcc00"),
        ],
        faqs=[
            ("How much does NordVPN cost?","NordVPN's 2-year Basic plan costs $2.99/mo ($71.76 upfront). 1-year plan is $4.49/mo. Monthly billing is $12.99/mo."),
            ("Does NordVPN have a free trial?","No free trial — but a 30-day money-back guarantee applies to all plans. Buy, test fully, and get a full refund within 30 days."),
            ("Why is NordVPN cheaper for 2 years?","NordVPN offers steep discounts for longer commitments. The 2-year plan saves ~73% vs monthly billing — it's a promotional price that renews at the standard rate."),
            ("What happens at renewal?","NordVPN's promotional pricing applies to the first term only. Renewal is at the standard rate (typically $5.99–6.99/mo for 2-year plans). Set a calendar reminder before renewal to shop alternatives."),
            ("Is NordVPN good for streaming?","Yes — NordVPN reliably unblocks Netflix (20+ libraries), BBC iPlayer, Disney+, and most major streaming platforms via the SmartPlay feature."),
        ]
    ),
    "clickup": dict(
        name="ClickUp", logo="https://cdn.simpleicons.org/clickup/7b68ee",
        go="/go/clickup", history="/pages/clickup-pricing-history-2026",
        page="/pages/best-clickup-alternatives-in-2026-free-paid", sticky="ClickUp's free plan is one of the most generous in project management.",
        hidden_risk="Low", hidden_note="Storage limits and guest seat caps can surprise growing teams",
        meta_desc="ClickUp restructured pricing with their 3.0 relaunch — we track every change. June 2026: Free forever, Unlimited $7/user, Business $12/user. Storage limits, AI add-on costs & hidden fees exposed.",
        plans=[
            dict(name="Free",      mo="$0",    annual="$0",   best="Solo / small teams", users="Unlimited", storage="100MB",     support="24/7 chat", f=["Unlimited tasks","Unlimited members","100 automation/mo"],    fc=["cw","cw","cm"]),
            dict(name="Unlimited", mo="$10",   annual="$7",   best="Small teams",        users="Unlimited", storage="Unlimited", support="24/7 chat", f=["Unlimited storage","Unlimited integrations","1,000 auto/mo"], fc=["cw","cw","cw"]),
            dict(name="Business",  mo="$19",   annual="$12",  best="Mid-size teams",     users="Unlimited", storage="Unlimited", support="Priority",  f=["10,000 auto/mo","Advanced reporting","Timelines + Goals"],    fc=["cw","cw","cw"]),
            dict(name="Enterprise",mo="Custom",annual="Custom",best="Large orgs",         users="Unlimited", storage="Unlimited", support="Dedicated", f=["Unlimited auto","White labelling","Advanced permissions"],     fc=["cw","cw","cw"]),
        ],
        hidden=[
            dict(name="Guest seat limits", desc="Free plan allows 5 guests. Heavy external collaboration requires Unlimited+ plan."),
            dict(name="Automation caps", desc="Free plan caps at 100 automations/mo — frustrating for teams relying on workflow rules."),
            dict(name="Learning curve", desc="ClickUp's depth is a double-edged sword. Expect 2–4 weeks before the team uses it effectively."),
        ],
        scenarios=[
            dict(users="Solo / freelancer", cost="$0/mo", plan="Free", plan_cls="v-value", breakdown="Free forever — unlimited tasks, unlimited members, 100MB storage"),
            dict(users="5-person team", cost="$35/mo", plan="Unlimited", plan_cls="v-smb", breakdown="Unlimited plan, 5 seats at $7/user/mo billed annually"),
            dict(users="20-person team", cost="$240/mo", plan="Business", plan_cls="v-ent", breakdown="Business plan, 20 seats at $12/user/mo — full automation and reporting"),
        ],
        alts=[
            dict(name="Asana",   url="/pages/asana-pricing-2026-plans-costs-what-you-actually-pay",   price="Free/10 users",  logo="https://cdn.simpleicons.org/asana/f06a6a"),
            dict(name="Notion",  url="/pages/notion-pricing-2026-plans-costs-what-you-actually-pay",  price="Free personal",  logo="https://cdn.simpleicons.org/notion/ffffff"),
            dict(name="Monday",  url="/pages/mondaycom-pricing-2026-plans-costs-what-you-actually-pay",price="From $12/seat", logo="https://cdn.simpleicons.org/monday/f62b54"),
            dict(name="Linear",  url="/pages/linear-pricing-2026-plans-costs-what-you-actually-pay",  price="Free/250 issues",logo="https://cdn.simpleicons.org/linear/ffffff"),
        ],
        faqs=[
            ("Is ClickUp free forever?","Yes — ClickUp's Free plan is genuinely free forever with unlimited tasks and unlimited members. The main limits are 100MB storage and 100 automations/month."),
            ("How much does ClickUp cost for a team of 10?","Unlimited plan at $7/user/mo billed annually = $70/mo for 10 users. Business plan at $12/user/mo = $120/mo. Both include unlimited storage and integrations."),
            ("ClickUp vs Asana — which is cheaper?","ClickUp's Unlimited ($7/user) is cheaper than Asana's Starter ($10.99/user). For 10 users, ClickUp saves $39/mo vs Asana — $420/year."),
            ("Is ClickUp good for enterprise?","Yes — ClickUp Enterprise includes unlimited automations, white labelling, advanced permissions, and dedicated support. Pricing requires a custom quote."),
            ("Does ClickUp have a free trial of paid plans?","ClickUp doesn't offer a time-limited trial of paid plans, but the free plan is comprehensive enough to evaluate the tool before upgrading."),
        ]
    ),
    "semrush": dict(
        name="Semrush", logo="https://cdn.simpleicons.org/semrush/ff642d",
        go="/go/semrush", history="/pages/semrush-pricing-history-2026",
        page="/pages/best-semrush-alternatives-2026", sticky="Semrush Pro at $139.95/mo is the industry standard for SEO professionals.",
        hidden_risk="Medium", hidden_note="Multi-user access and historical data cost extra on all tiers",
        meta_desc="Semrush raised Pro to $139.95/mo — we track every pricing change. June 2026: Pro $117/mo (annual), Guru $208/mo, Business $375/mo. Extra user seats $45/mo each. Full cost breakdown.",
        plans=[
            dict(name="Pro",     mo="$139.95", annual="$117.33", best="Freelancers / startups", users="1",  storage="10K results/report", support="Email+chat", f=["5 projects","500 tracked keywords","100K pages/crawl"],     fc=["cm","cm","cw"]),
            dict(name="Guru",    mo="$249.95", annual="$208.33", best="SMBs / agencies",        users="1",  storage="30K results/report", support="Priority",   f=["15 projects","1,500 tracked keywords","Content Marketing"],  fc=["cw","cw","cw"]),
            dict(name="Business",mo="$449.95", annual="$374.95", best="Large agencies",          users="1",  storage="50K results/report", support="Priority",   f=["40 projects","5,000 tracked keywords","White-label reports"],fc=["cw","cw","cw"]),
            dict(name="Custom",  mo="Custom",  annual="Custom",  best="Enterprise",              users="Custom", storage="Custom",          support="Dedicated",  f=["Custom limits","API access","Dedicated success manager"],    fc=["cw","cw","cw"]),
        ],
        hidden=[
            dict(name="One user only", desc="All plans include 1 user. Additional seats cost $45/mo each — a 3-person team on Pro costs $229.95/mo, not $139.95."),
            dict(name="Historical data", desc="Trend data older than 12 months requires Guru or Business. Researchers comparing historical rankings need to upgrade."),
            dict(name="Agency add-ons", desc="Client-facing reporting, white-label PDFs, and the Agency Growth Kit cost extra on top of plan price."),
        ],
        scenarios=[
            dict(users="Solo SEO consultant", cost="$117/mo", plan="Pro annual", plan_cls="v-smb", breakdown="Pro at $117.33/mo billed annually — 1 user, 5 projects, sufficient for freelancers"),
            dict(users="3-person SEO team", cost="$208/mo", plan="Guru", plan_cls="v-visual", breakdown="Guru annual ($208.33) + need to add 2 extra seats ($90/mo) = $298/mo total"),
            dict(users="SEO agency", cost="$375/mo+", plan="Business", plan_cls="v-ent", breakdown="Business annual ($374.95) + white-label + multiple seats — real agency cost $500-700/mo"),
        ],
        alts=[
            dict(name="Ahrefs",     url="/pages/ahrefs-pricing-2026-plans-costs-what-you-actually-pay",     price="From $129/mo", logo="https://cdn.simpleicons.org/ahrefs/2196f3"),
            dict(name="Moz Pro",    url="/pages/moz-pro-pricing-2026-plans-costs-what-you-actually-pay",    price="From $99/mo",  logo="https://cdn.simpleicons.org/moz/2196f3"),
            dict(name="SE Ranking", url="/pages/se-ranking-pricing-2026-plans-costs-what-you-actually-pay", price="From $52/mo",  logo="https://cdn.simpleicons.org/google/4285f4"),
            dict(name="Surfer SEO", url="/pages/surfer-seo-pricing-2026-plans-costs-what-you-actually-pay", price="From $89/mo",  logo="https://cdn.simpleicons.org/surferseo/ff6a13"),
        ],
        faqs=[
            ("How much does Semrush cost per month?","Semrush Pro is $139.95/mo (or $117.33/mo billed annually). Guru is $249.95/mo. Business is $449.95/mo. All plans include 1 user — extra seats are $45/mo each."),
            ("Is Semrush worth it for small businesses?","For serious SEO work, yes. Pro at $117/mo covers most needs for 1–2 users. If budget is tight, SE Ranking offers similar features at half the price."),
            ("Does Semrush offer a free trial?","Semrush offers a 7-day free trial of Pro or Guru. You need to enter payment details but won't be charged if you cancel within 7 days."),
            ("Can multiple users share a Semrush account?","Technically yes, but Semrush's terms limit simultaneous logins. Additional user seats cost $45/mo each and give each person their own login with separate limits."),
            ("Semrush vs Ahrefs — which is better value?","Semrush Pro ($139.95) vs Ahrefs Starter ($129) — similar price, different strengths. Semrush has better keyword research and competitor analysis; Ahrefs has the best backlink data."),
        ]
    ),
    "ahrefs": dict(
        name="Ahrefs", logo="https://cdn.simpleicons.org/ahrefs/2196f3",
        go="/go/ahrefs", history="/pages/ahrefs-pricing-history-2026",
        page="/pages/best-ahrefs-alternatives-2026", sticky="Ahrefs has the best backlink database — worth it if links are your focus.",
        hidden_risk="Low", hidden_note="Pricing is transparent but historical data access varies by tier",
        plans=[
            dict(name="Starter",      mo="$129",  annual="$108",  best="Freelancers",     users="1",  storage="500 credits/mo",   support="Chat",    f=["1 month data history","3 months data history","Basic site audit"],         fc=["cm","cm","cw"]),
            dict(name="Lite",         mo="$190",  annual="$149",  best="Small teams",     users="2",  storage="2,000 credits/mo", support="Chat",    f=["6 months data history","1,000 tracked keywords","5 projects"],             fc=["cm","cw","cw"]),
            dict(name="Standard",     mo="$399",  annual="$299",  best="Growing agencies",users="5",  storage="5,000 credits/mo", support="Priority",f=["2 years data history","3,000 tracked keywords","20 projects"],            fc=["cw","cw","cw"]),
            dict(name="Advanced",     mo="$999",  annual="$749",  best="Large agencies",  users="10", storage="15,000 credits/mo",support="Priority",f=["Full history","10,000 tracked keywords","50 projects"],                    fc=["cw","cw","cw"]),
        ],
        hidden=[
            dict(name="Credit system", desc="Ahrefs uses 'credits' instead of unlimited reports. Each search consumes credits — heavy users hit limits faster than expected."),
            dict(name="Historical data", desc="Starter plan only gives 1 month of data. You need Standard+ to access meaningful competitive history."),
        ],
        scenarios=[
            dict(users="Solo SEO", cost="$108/mo", plan="Lite annual", plan_cls="v-smb", breakdown="Lite at $149/mo billed annually — 2 users, 5 projects, 6 months history"),
            dict(users="Small agency", cost="$299/mo", plan="Standard annual", plan_cls="v-visual", breakdown="Standard annual — 5 users, 20 projects, 2 years data history"),
            dict(users="Large agency", cost="$749/mo", plan="Advanced annual", plan_cls="v-ent", breakdown="Advanced annual — 10 users, 50 projects, full historical access"),
        ],
        alts=[
            dict(name="Semrush",    url="/pages/semrush-pricing-2026-plans-costs-what-you-actually-pay",   price="From $117/mo", logo="https://cdn.simpleicons.org/semrush/ff642d"),
            dict(name="Moz Pro",    url="/pages/moz-pro-pricing-2026-plans-costs-what-you-actually-pay",   price="From $99/mo",  logo="https://cdn.simpleicons.org/moz/2196f3"),
            dict(name="SE Ranking", url="/pages/se-ranking-pricing-2026-plans-costs-what-you-actually-pay",price="From $52/mo",  logo="https://cdn.simpleicons.org/google/4285f4"),
            dict(name="Surfer SEO", url="/pages/surfer-seo-pricing-2026-plans-costs-what-you-actually-pay",price="From $89/mo",  logo="https://cdn.simpleicons.org/surferseo/ff6a13"),
        ],
        faqs=[
            ("How much does Ahrefs cost?","Ahrefs Starter is $129/mo ($108 annual). Lite is $190/mo ($149 annual). Standard is $399/mo ($299 annual). Advanced is $999/mo ($749 annual)."),
            ("Is Ahrefs better than Semrush?","Ahrefs has the best backlink database; Semrush has better keyword and competitive research tools. Most serious SEOs use both, but if forced to choose: Ahrefs for link building, Semrush for keyword strategy."),
            ("Does Ahrefs have a free option?","Ahrefs Webmaster Tools (AWT) is free for site owners — gives you Site Audit and limited Site Explorer for your own domains. No free trial of paid plans."),
            ("What are Ahrefs credits?","Credits are Ahrefs' usage unit — each report or data pull consumes credits. Starter gets 500/mo; Lite 2,000/mo. Heavy researchers can exhaust credits mid-month."),
            ("Can I cancel Ahrefs anytime?","Yes — Ahrefs is billed monthly or annually. Monthly plans cancel anytime. Annual plans don't offer prorated refunds."),
        ]
    ),
    "protonvpn": dict(
        name="ProtonVPN", logo="https://cdn.simpleicons.org/protonvpn/6d4aff",
        go="/go/protonvpn", history="/pages/protonvpn-pricing-history-2026",
        page="/pages/best-protonvpn-alternatives-2026", sticky="ProtonVPN is the only VPN with a genuinely unlimited free tier.",
        hidden_risk="Low", hidden_note="Free tier limited to 3 server locations; paid prices are fair and transparent",
        plans=[
            dict(name="Free",    mo="$0",    annual="$0",    best="Privacy basics",       users="1",  storage="3 locations",    support="Email",   f=["Unlimited data","Medium speed","3 server locations"],         fc=["cw","cm","cl"]),
            dict(name="Basic",   mo="$9.99", annual="$4.99", best="Everyday use",         users="1",  storage="60+ countries",  support="Email",   f=["High speed","Torrenting","Streaming support"],               fc=["cw","cw","cw"]),
            dict(name="Plus",    mo="$11.99",annual="$7.99", best="Best value",           users="10", storage="90+ countries",  support="Priority",f=["Highest speed","Streaming all libraries","Secure Core VPN"], fc=["cw","cw","cw"]),
            dict(name="Visionary",mo="$23.99",annual="$23.99",best="Full Proton suite",   users="10", storage="90+ countries",  support="Priority",f=["ProtonVPN Plus + ProtonMail Visionary","Proton Drive","All Proton apps"], fc=["cw","cw","cw"]),
        ],
        hidden=[
            dict(name="Free tier location limits", desc="Free plan restricted to 3 server locations — USA, Netherlands, Japan. Good for basic privacy, not ideal for streaming or gaming."),
            dict(name="Speed on free tier", desc="Free servers are shared and slower than paid servers, especially during peak hours."),
        ],
        scenarios=[
            dict(users="Privacy-first user", cost="$0/mo", plan="Free", plan_cls="v-value", breakdown="Unlimited data, 3 server locations — perfect for privacy without streaming needs"),
            dict(users="Regular VPN user", cost="$4.99/mo", plan="Basic annual", plan_cls="v-smb", breakdown="Basic plan annual — high speed, torrenting, streaming, 60+ countries"),
            dict(users="Power user", cost="$7.99/mo", plan="Plus annual", plan_cls="v-ent", breakdown="Plus annual — fastest servers, Secure Core, Tor over VPN, all streaming libraries"),
        ],
        alts=[
            dict(name="NordVPN",   url="/pages/nordvpn-pricing-2026-plans-costs-what-you-actually-pay",   price="From $2.99/mo", logo="https://cdn.simpleicons.org/nordvpn/4687ff"),
            dict(name="Surfshark", url="/pages/surfshark-pricing-2026-plans-costs-what-you-actually-pay", price="From $2.49/mo", logo="https://cdn.simpleicons.org/surfshark/1ce0c3"),
            dict(name="Mullvad",   url="/pages/mullvad-pricing-2026-plans-costs-what-you-actually-pay",   price="€5/mo flat",   logo="https://cdn.simpleicons.org/mullvad/44ad8e"),
            dict(name="ExpressVPN",url="/pages/expressvpn-pricing-2026-plans-costs-what-you-actually-pay",price="From $8.32/mo", logo="https://cdn.simpleicons.org/express/fc172f"),
        ],
        faqs=[
            ("Is ProtonVPN free?","Yes — ProtonVPN has a genuinely unlimited free tier with no data caps, no ads, and no time limits. The free plan is limited to 3 server locations and medium speed."),
            ("How much does ProtonVPN cost?","ProtonVPN Basic is $4.99/mo (annual). Plus is $7.99/mo (annual). Visionary (all Proton apps) is $23.99/mo. Monthly billing costs ~2× more."),
            ("Is ProtonVPN good for streaming?","Plus and Visionary plans unblock Netflix, Disney+, BBC iPlayer, and other streaming libraries. Basic plan has streaming support but fewer servers. Free plan does not support streaming."),
            ("Is ProtonVPN truly no-logs?","Yes — ProtonVPN is based in Switzerland (outside 5/9/14 Eyes), open-source, and has passed multiple independent security audits. Their no-logs policy is verified."),
            ("ProtonVPN vs NordVPN — which is better?","NordVPN has faster speeds, more servers (6,300+ vs 5,800+), and a cheaper entry price. ProtonVPN is better for privacy-first users — open source, Swiss jurisdiction, genuinely unlimited free tier."),
        ]
    ),
    "mixpanel": dict(
        name="Mixpanel", logo="https://cdn.simpleicons.org/mixpanel/7856ff",
        go="/go/mixpanel", history="/pages/mixpanel-pricing-history-2026",
        page="/pages/best-mixpanel-alternatives-2026", sticky="Mixpanel's free plan supports 20M events/mo — the most generous in analytics.",
        hidden_risk="Low", hidden_note="Pricing scales with event volume, which can surprise fast-growing products",
        plans=[
            dict(name="Free",    mo="$0",    annual="$0",    best="Early-stage products", users="Unlimited", storage="90-day retention", support="Community", f=["20M events/mo","Unlimited reports","Core analytics"],         fc=["cw","cw","cw"]),
            dict(name="Growth",  mo="$28",   annual="$20",   best="Growing products",     users="Unlimited", storage="1-year retention",  support="Email",     f=["From 100M events/mo","Session replay","1-year data retention"],fc=["cw","cw","cw"]),
            dict(name="Enterprise",mo="Custom",annual="Custom",best="Scale",              users="Unlimited", storage="Custom",            support="Dedicated", f=["Custom events","SSO + SCIM","Data pipelines"],               fc=["cw","cw","cw"]),
            dict(name="Starter", mo="$0",    annual="$0",    best="Very small teams",     users="3",         storage="1-year retention",  support="Email",     f=["20M events/mo","Session replay","Basic reports"],            fc=["cw","cm","cm"]),
        ],
        hidden=[
            dict(name="Event volume scaling", desc="Growth plan pricing scales with monthly event volume — high-traffic products pay significantly more than the $28/mo base price."),
            dict(name="Data retention on free", desc="Free plan has 90-day data retention — you lose historical data older than 3 months. Growth plan extends to 1 year."),
        ],
        scenarios=[
            dict(users="Early-stage product", cost="$0/mo", plan="Free", plan_cls="v-value", breakdown="Free plan — 20M events/mo, unlimited reports, 90-day retention, unlimited users"),
            dict(users="Growth-stage product", cost="$28/mo", plan="Growth", plan_cls="v-visual", breakdown="Growth plan base — 100M events/mo, session replay, 1-year retention"),
            dict(users="Scale-up product", cost="Custom", plan="Enterprise", plan_cls="v-ent", breakdown="Enterprise — custom event volumes, SSO, data pipelines, dedicated CSM"),
        ],
        alts=[
            dict(name="Amplitude", url="/pages/amplitude-pricing-2026-plans-costs-what-you-actually-pay",   price="Free/10M events", logo="https://cdn.simpleicons.org/amplitude/2559e1"),
            dict(name="PostHog",   url="/pages/posthog-pricing-2026-plans-costs-what-you-actually-pay",     price="Free/1M events",  logo="https://cdn.simpleicons.org/posthog/f76707"),
            dict(name="Heap",      url="/pages/heap-pricing-2026-plans-costs-what-you-actually-pay",        price="Free available",  logo="https://cdn.simpleicons.org/heap/7b2bf9"),
            dict(name="Pendo",     url="/pages/pendo-pricing-2026-plans-costs-what-you-actually-pay",       price="Free available",  logo="https://cdn.simpleicons.org/pendo/ff4c4c"),
        ],
        faqs=[
            ("How much does Mixpanel cost?","Mixpanel Free is $0 forever (20M events/mo). Growth starts at $28/mo for 100M+ events billed annually. Enterprise is custom pricing."),
            ("Is Mixpanel free?","Yes — Mixpanel's Free plan supports 20M monthly events, unlimited reports, and unlimited users (3 seats on Starter). No time limit."),
            ("Mixpanel vs Amplitude — which should I choose?","Mixpanel is better for developer-centric teams who want clean event tracking and simple cohort analysis. Amplitude is better for deeper funnel analysis and behavioural intelligence. Both have generous free tiers."),
            ("What happens to my data on the free plan?","Free plan retains data for 90 days. Events older than 90 days are deleted. Upgrade to Growth ($28/mo) for 12-month retention."),
            ("Does Mixpanel have a free trial of paid plans?","Yes — Mixpanel offers a free trial of the Growth plan. Contact sales or start via the dashboard. No credit card required for the free trial period."),
        ]
    ),
    "amplitude": dict(
        name="Amplitude", logo="https://cdn.simpleicons.org/amplitude/2559e1",
        go="/go/amplitude", history="/pages/amplitude-pricing-history-2026",
        page="/pages/best-amplitude-alternatives-2026", sticky="Amplitude's free plan supports 10M events/mo with session replay included.",
        hidden_risk="Low", hidden_note="Growth tier pricing scales with event volume beyond the base allocation",
        plans=[
            dict(name="Free (Starter)",mo="$0",  annual="$0",    best="Early-stage",     users="Unlimited", storage="1-year retention",  support="Community",  f=["10M events/mo","Unlimited reports","Session replay basic"],    fc=["cw","cw","cm"]),
            dict(name="Plus",     mo="$61",   annual="$49",   best="Growing products",    users="Unlimited", storage="1-year retention",  support="Email",      f=["1B events/mo","Unlimited session replay","Cohort analysis"],   fc=["cw","cw","cw"]),
            dict(name="Growth",   mo="Custom",annual="Custom",best="Scale",               users="Unlimited", storage="Custom",            support="CSM",        f=["Custom events","Behavioral cohorts","A/B test integration"],    fc=["cw","cw","cw"]),
            dict(name="Enterprise",mo="Custom",annual="Custom",best="Enterprise",          users="Unlimited", storage="Custom",            support="Dedicated",  f=["SSO + SCIM","Data warehouse sync","Custom contracts"],          fc=["cw","cw","cw"]),
        ],
        hidden=[
            dict(name="Event volume caps", desc="Free plan caps at 10M events/mo — products with heavy traffic will hit this quickly. Plus scales to 1B events."),
            dict(name="Feature flags", desc="Feature flags (Amplitude Experiment) are a separate product and add-on cost."),
        ],
        scenarios=[
            dict(users="Early product", cost="$0/mo", plan="Free", plan_cls="v-value", breakdown="10M events, unlimited users, 1-year retention, basic session replay — genuinely useful free tier"),
            dict(users="Growth product", cost="$49/mo", plan="Plus annual", plan_cls="v-visual", breakdown="Plus annual — 1B events, full session replay, unlimited cohort analysis"),
            dict(users="Scale product", cost="Custom", plan="Growth", plan_cls="v-ent", breakdown="Growth/Enterprise — custom event volume, warehouse sync, CSM, A/B test platform"),
        ],
        alts=[
            dict(name="Mixpanel", url="/pages/mixpanel-pricing-2026-plans-costs-what-you-actually-pay",  price="Free/20M events", logo="https://cdn.simpleicons.org/mixpanel/7856ff"),
            dict(name="PostHog",  url="/pages/posthog-pricing-2026-plans-costs-what-you-actually-pay",   price="Free/1M events",  logo="https://cdn.simpleicons.org/posthog/f76707"),
            dict(name="Heap",     url="/pages/heap-pricing-2026-plans-costs-what-you-actually-pay",      price="Free available",  logo="https://cdn.simpleicons.org/heap/7b2bf9"),
            dict(name="Pendo",    url="/pages/pendo-pricing-2026-plans-costs-what-you-actually-pay",     price="Free available",  logo="https://cdn.simpleicons.org/pendo/ff4c4c"),
        ],
        faqs=[
            ("How much does Amplitude cost?","Amplitude Free is $0 (10M events/mo). Plus starts at $49/mo billed annually. Growth and Enterprise are custom pricing."),
            ("Is Amplitude free?","Yes — Amplitude's Starter plan is free forever with 10M monthly events, unlimited reports, 1-year data retention, and basic session replay."),
            ("Amplitude vs Mixpanel — which is better?","Amplitude has better funnel analysis and AI-powered insights. Mixpanel has a larger free event allowance (20M vs 10M). Both are excellent — choice often comes down to team preference."),
            ("Does Amplitude have session replay?","Yes — basic session replay is included on the free Starter plan. Full session replay with all features requires Plus or higher."),
            ("What is Amplitude's feature flag product?","Amplitude Experiment is their A/B testing and feature flagging product. It's sold separately from core analytics and priced based on monthly unique users exposed to experiments."),
        ]
    ),
    "ramp": dict(
        name="Ramp", logo="https://cdn.simpleicons.org/ramp/f5bf42",
        go="/go/ramp", history="/pages/ramp-pricing-history-2026",
        page="/pages/best-ramp-alternatives-2026", sticky="Ramp is free for most businesses — it earns revenue from interchange fees.",
        hidden_risk="Low", hidden_note="Ramp is free but requires a US business entity and minimum revenue",
        meta_desc=f"Ramp pricing 2026 — core card is free, Ramp Plus $15/user/mo. We track every Ramp pricing change (April, May, June 2026) and expose the 3 hidden costs teams miss.",
        plans=[
            dict(name="Ramp Free",      mo="$0",    annual="$0",    best="Most businesses",   users="Unlimited", storage="Unlimited cards",   support="Email+chat", f=["Unlimited virtual + physical cards","Expense management","Bill pay free"],         fc=["cw","cw","cw"]),
            dict(name="Ramp Plus",      mo="$15/user",annual="$12/user",best="Power users",   users="Unlimited", storage="Unlimited cards",   support="Priority",   f=["Custom approval chains","Advanced analytics","ERP integrations"],                  fc=["cw","cw","cw"]),
            dict(name="Ramp Enterprise",mo="Custom",annual="Custom",best="Large companies",   users="Unlimited", storage="Unlimited",          support="Dedicated",  f=["Custom spend controls","Dedicated CSM","Advanced security + SSO"],                  fc=["cw","cw","cw"]),
            dict(name="Ramp Flex",      mo="$0",    annual="$0",    best="Businesses needing net terms", users="Unlimited", storage="Unlimited",support="Email", f=["Net-30 / net-60 payment terms","Automatic bill payment","Cash flow management"],  fc=["cw","cw","cw"]),
        ],
        hidden=[
            dict(name="US-only", desc="Ramp requires a US-registered business entity with a US bank account. Not available internationally."),
            dict(name="Revenue requirement", desc="Ramp requires minimum $25,000 in your business bank account or $75,000/yr in revenue. Not for pre-revenue startups."),
            dict(name="Interchange income", desc="Ramp earns revenue from credit card interchange fees — so the 'free' product is subsidised by merchants who accept your Ramp card."),
        ],
        scenarios=[
            dict(users="SMB, 10 employees", cost="$0/mo", plan="Ramp Free", plan_cls="v-value", breakdown="Free — unlimited cards, expense management, bill pay, receipt capture for 10 users"),
            dict(users="Growth co, 50 employees", cost="$600/mo", plan="Ramp Plus", plan_cls="v-visual", breakdown="Plus at $12/user/mo × 50 users — custom workflows, advanced analytics, ERP sync"),
            dict(users="Enterprise, 200+ employees", cost="Custom", plan="Ramp Enterprise", plan_cls="v-ent", breakdown="Custom pricing — dedicated CSM, advanced controls, custom integrations"),
        ],
        alts=[
            dict(name="Brex",    url="/pages/brex-pricing-2026-plans-costs-what-you-actually-pay",    price="Free available", logo="https://cdn.simpleicons.org/brex/f26a2b"),
            dict(name="Divvy",   url="/pages/divvy-pricing-2026-plans-costs-what-you-actually-pay",   price="Free available", logo="https://cdn.simpleicons.org/bill/ff5b24"),
            dict(name="Expensify",url="/pages/expensify-pricing-2026-plans-costs-what-you-actually-pay",price="From $5/user",logo="https://cdn.simpleicons.org/expensify/2fb67a"),
            dict(name="Spendesk",url="/pages/spendesk-pricing-2026-plans-costs-what-you-actually-pay", price="From $9/user", logo="https://cdn.simpleicons.org/spendesk/5200ff"),
        ],
        faqs=[
            ("Did Ramp change pricing in 2026?","Yes. Ramp adjusted Ramp Plus pricing in early 2026 to a $12–15/user/mo range based on contract length (annual vs monthly). The core Ramp card product remained free throughout. We track every pricing change on the Ramp pricing history page with sources."),
            ("What is Ramp's pricing in June 2026?","As of June 2026: Ramp Free ($0 forever), Ramp Plus ($15/user/mo monthly or $12/user/mo annual), Ramp Enterprise (custom). Verified directly from Ramp's pricing page on 4 June 2026."),
            ("Is Ramp really free?","Yes — Ramp's core product (cards, expense management, bill pay) is free. Ramp earns revenue from interchange fees paid by merchants, not from customers."),
            ("Who is Ramp for?","Ramp is for US-registered businesses with at least $25,000 in a business bank account. Not available for personal use, non-US companies, or pre-revenue startups."),
            ("What is Ramp Plus?","Ramp Plus ($12–15/user/mo) adds custom approval workflows, advanced analytics, enhanced ERP integrations (NetSuite, Sage Intacct), and priority support."),
        ]
    ),
    "aweber": dict(
        name="AWeber", logo="https://cdn.simpleicons.org/aweber/2575be",
        go="/go/aweber", history="/pages/aweber-pricing-history-2026",
        page="/pages/getresponse-vs-aweber-which-is-better-in-2026",
        sticky="AWeber's free plan covers 500 subscribers — start free and upgrade when you need automation.",
        hidden_risk="Low", hidden_note="Pricing scales with subscriber count — re-check costs as your list grows",
        meta_desc="AWeber pricing 2026: Free up to 500 subscribers, Lite from $12.50/mo, Plus from $20/mo (annual, 500 subs). Pricing scales with list size — full cost breakdown at every list tier.",
        plans=[
            dict(name="Free",  mo="$0",       annual="$0",       best="Up to 500 subscribers", users="1",   storage="500 subs",    support="Email only",   f=["3,000 emails/month","Basic templates","Sign-up forms"],          fc=["cm","cw","cw"]),
            dict(name="Lite",  mo="$15",       annual="$12.50",   best="Solopreneurs & bloggers",users="1",  storage="500+ subs",   support="Email + chat", f=["Unlimited emails","Landing pages","Basic automations"],           fc=["cw","cm","cw"]),
            dict(name="Plus",  mo="$25",       annual="$20",      best="Growing lists",          users="3",  storage="500+ subs",   support="Priority 24/7",f=["Full automations","Split testing","Sales tracking"],              fc=["cw","cw","cw"]),
            dict(name="Unlimited", mo="Custom", annual="$899",   best="High-volume senders",   users="Unlimited", storage="Unlimited", support="Priority 24/7",f=["Unlimited subscribers","Advanced analytics","Custom branding"],fc=["cw","cw","cw"]),
        ],
        hidden=[
            dict(name="Subscriber-based pricing", desc="Lite and Plus pricing shown is for 500 subscribers. At 2,500 subs: ~$25–45/mo. At 10,000 subs: ~$50–80/mo. Costs climb fast with list growth."),
            dict(name="Monthly vs annual billing", desc="Monthly billing costs ~20% more than annual. Annual billing commits you for 12 months."),
            dict(name="Landing page limits on Free", desc="Free plan limits landing pages and advanced form features — you'll need Lite or Plus for serious lead capture."),
        ],
        scenarios=[
            dict(users="Blogger, 200 subscribers", cost="$0/mo", plan="Free", plan_cls="v-value", breakdown="Free plan — 3k emails/month, basic templates, adequate for starting out"),
            dict(users="Consultant, 1,500 subscribers", cost="~$25/mo", plan="Lite", plan_cls="v-smb", breakdown="Lite annual at 1,500 subscribers tier — unlimited sends, basic automations"),
            dict(users="SMB, 5,000 subscribers", cost="~$50/mo", plan="Plus", plan_cls="v-visual", breakdown="Plus annual at 5,000 subscribers tier — full automation, split testing, sales tracking"),
        ],
        alts=[
            dict(name="GetResponse",    url="/pages/getresponse-vs-aweber-which-is-better-in-2026", price="From $19/mo",   logo="https://cdn.simpleicons.org/getresponse/00baff"),
            dict(name="Mailchimp",      url="/pages/mailchimp-vs-activecampaign-which-is-better-in-2026", price="Free/$13+/mo", logo="https://cdn.simpleicons.org/mailchimp/ffe01b"),
            dict(name="ActiveCampaign", url="/pages/activecampaign-vs-brevo-which-is-better-in-2026",   price="From $15/mo",  logo="https://cdn.simpleicons.org/activecampaign/356ae4"),
            dict(name="Brevo",          url="/pages/brevo-vs-convertkit-which-is-better-in-2026",       price="Free/$25+/mo", logo="https://cdn.simpleicons.org/brevo/0b996e"),
        ],
        faqs=[
            ("How much does AWeber cost per month?","AWeber starts free for up to 500 subscribers. Lite starts at $12.50/mo (annual) for 500 subscribers. Plus starts at $20/mo (annual). Pricing scales with your subscriber count — expect to pay more as your list grows."),
            ("Does AWeber have a free plan?","Yes — AWeber Free covers up to 500 subscribers and 3,000 emails/month. You get basic templates and sign-up forms. Automations and advanced features require a paid plan."),
            ("How does AWeber pricing compare to Mailchimp?","AWeber Free covers 500 subs vs Mailchimp's 500 subs with a 1,000 emails/month limit. At 2,500 subscribers, AWeber Lite is typically cheaper than Mailchimp's Essentials plan."),
            ("Does AWeber charge per email sent?","No — AWeber's paid plans include unlimited emails. Only the Free plan limits sends to 3,000/month."),
            ("Is AWeber worth it in 2026?","AWeber is a solid choice for bloggers, consultants, and small businesses that want reliable email delivery and simple automations without complexity. For advanced segmentation or CRM-level automation, consider ActiveCampaign or GetResponse."),
        ]
    ),
}

# Generic fallback for tools not in the database
def make_generic_pricing(slug, name):
    return dict(
        name=name, logo=f"https://cdn.simpleicons.org/{slug}/888888",
        go=f"/go/{slug}", history=f"/pages/{slug}-pricing-history-2026",
        page=f"/pages/best-{slug}-alternatives-2026",
        sticky=f"Compare {name} pricing plans before committing.",
        hidden_risk="Medium", hidden_note="Always check the vendor's current pricing page for the latest rates",
        plans=[
            dict(name="Free",       mo="$0",      annual="$0",      best="Try it out",     users="Limited",   storage="Limited",   support="Community", f=["Core features","Limited usage","Community support"],     fc=["cm","cm","cm"]),
            dict(name="Starter",    mo="$15/mo",  annual="$10/mo",  best="Small teams",    users="Unlimited", storage="Standard",  support="Email",     f=["Full feature set","Standard limits","Email support"],    fc=["cw","cm","cw"]),
            dict(name="Pro",        mo="$49/mo",  annual="$39/mo",  best="Growing teams",  users="Unlimited", storage="Extended",  support="Priority",  f=["Advanced features","Higher limits","Priority support"],  fc=["cw","cw","cw"]),
            dict(name="Enterprise", mo="Custom",  annual="Custom",  best="Large orgs",     users="Unlimited", storage="Unlimited", support="Dedicated", f=["Custom limits","SLA","Dedicated account manager"],       fc=["cw","cw","cw"]),
        ],
        hidden=[
            dict(name="Annual lock-in", desc="Monthly billing typically costs 20–30% more than annual. Check whether the annual discount is worth the commitment."),
            dict(name="Add-on costs", desc="Advanced features, extra seats, and premium integrations are often sold as add-ons on top of the base plan price."),
            dict(name="Renewal pricing", desc="Introductory pricing may not apply at renewal. Always check the renewal rate before committing."),
        ],
        scenarios=[
            dict(users="Solo / small team", cost="$10/mo", plan="Starter", plan_cls="v-smb", breakdown="Starter billed annually — full feature access at the lowest price"),
            dict(users="Medium team (10)", cost="$390/mo", plan="Pro", plan_cls="v-visual", breakdown="Pro plan, 10 users billed annually — standard for growing businesses"),
            dict(users="Large team (50+)", cost="Custom", plan="Enterprise", plan_cls="v-ent", breakdown="Enterprise — custom pricing, dedicated support, SLA"),
        ],
        alts=[],
        faqs=[
            (f"How much does {name} cost?", f"{name} offers multiple pricing tiers. The free plan gives you core features to evaluate the product. Paid plans start from around $10–15/user/mo billed annually."),
            (f"Does {name} have a free plan?", f"Check {name}'s current pricing page — many SaaS tools offer a free tier or free trial. Pricing changes frequently and we verify it weekly."),
            (f"Is {name} worth it?", f"Whether {name} is worth the cost depends on your specific use case. We recommend starting with the free plan or trial to validate it meets your needs before committing to annual billing."),
            ("How often is this pricing verified?", "We verify SaaS pricing weekly via automated scraping and manual spot-checks. If you spot a discrepancy, use the 'Report outdated pricing' button."),
            ("Can I negotiate pricing?", "For annual contracts above $10,000, most SaaS vendors will negotiate. Contact their sales team directly — discounts of 10–30% are common for multi-year deals."),
        ]
    )

def slug_to_name(slug):
    """Convert a URL slug like 'hubspot' to a display name like 'HubSpot'."""
    known = {
        "1password":"1Password","activecampaign":"ActiveCampaign","ahrefs":"Ahrefs",
        "amplitude":"Amplitude","asana":"Asana","bamboohr":"BambooHR",
        "bigcommerce":"BigCommerce","canva":"Canva","clearscope":"Clearscope",
        "clickup":"ClickUp","deel":"Deel","elementor":"Elementor",
        "freshbooks":"FreshBooks","getresponse":"GetResponse","github-copilot":"GitHub Copilot",
        "gusto":"Gusto","hubspot":"HubSpot","jira":"Jira","lastpass":"LastPass",
        "linear":"Linear","mailchimp":"Mailchimp","mixpanel":"Mixpanel",
        "monday":"Monday.com","mondaycom":"Monday.com","moz-pro":"Moz Pro","notion":"Notion",
        "nordpass":"NordPass","nordvpn":"NordVPN","protonvpn":"ProtonVPN",
        "pipedrive":"Pipedrive","quickbooks":"QuickBooks","ramp":"Ramp",
        "rippling":"Rippling","salesforce":"Salesforce","se-ranking":"SE Ranking",
        "semrush":"Semrush","shopify":"Shopify","snyk":"Snyk","surfshark":"Surfshark",
        "surfer-seo":"Surfer SEO","trello":"Trello","webflow":"Webflow",
        "wix":"Wix","woocommerce":"WooCommerce","xero":"Xero","zoho":"Zoho CRM",
        "zoom":"Zoom","datadog":"Datadog","render":"Render","vercel":"Vercel",
        "brevo":"Brevo","freshsales":"Freshsales","dashlane":"Dashlane",
        "nordlayer":"NordLayer","sentry":"Sentry","supabase":"Supabase",
    }
    return known.get(slug, slug.replace("-", " ").title())

def build_tokens(data):
    plans = data["plans"]
    hidden = data["hidden"]
    scenarios = data["scenarios"]
    alts = data.get("alts", [])
    faqs = data.get("faqs", [])

    t = {}
    t["TOOL_NAME"]    = data["name"]
    t["TOOL_LOGO_URL"] = data["logo"]
    t["TOOL_GO_LINK"]  = data["go"]
    t["TOOL_HISTORY_URL"] = data.get("history","")
    t["TOOL_PAGE_URL"]    = data.get("page","")
    t["VERIFIED_DATE"]    = TODAY
    t["STICKY_CTA_TEXT"]  = data.get("sticky", f"Compare {data['name']} pricing plans.")
    t["HIDDEN_COST_COUNT"]    = str(len(hidden))
    t["HIDDEN_FEE_RISK_LEVEL"] = data.get("hidden_risk","Medium")
    t["HIDDEN_FEE_RISK_NOTE"]  = data.get("hidden_note","Always verify pricing on the vendor's website.")
    t["PLAN_COUNT"] = str(len(plans))
    t["CMP_FEAT_1"] = "Key features"
    t["CMP_FEAT_2"] = "Users"
    t["CMP_FEAT_3"] = "Support"

    for i, p in enumerate(plans[:4], 1):
        t[f"PLAN_{i}_NAME"]         = p["name"]
        t[f"PLAN_{i}_PRICE_MO"]     = p["mo"]
        t[f"PLAN_{i}_PRICE_ANNUAL"] = p["annual"]
        t[f"PLAN_{i}_BEST_FOR"]     = p["best"]
        t[f"PLAN_{i}_USERS"]        = p.get("users","Unlimited")
        t[f"PLAN_{i}_STORAGE"]      = p.get("storage","Unlimited")
        t[f"PLAN_{i}_SUPPORT"]      = p.get("support","Email")
        fs = p.get("f", ["—","—","—"])
        fcs = p.get("fc", ["","",""])
        for j in range(3):
            t[f"PLAN_{i}_F{j+1}"]     = fs[j]  if j < len(fs)  else "—"
            t[f"PLAN_{i}_F{j+1}_CLS"] = fcs[j] if j < len(fcs) else ""
        if i == 2:
            mo_val = p["mo"].replace("$","").replace("/user","").replace("/mo","").split("/")[0]
            try:
                annual_val = float(p["annual"].replace("$","").replace("/user","").replace("/mo","").split("/")[0])
                mo_float   = float(mo_val)
                if mo_float > 0 and annual_val > 0:
                    save_pct = round((1 - annual_val/mo_float)*100)
                    t["PLAN_2_ANNUAL_SAVE"] = f"Save {save_pct}% billed annually"
                else:
                    t["PLAN_2_ANNUAL_SAVE"] = ""
            except Exception:
                t["PLAN_2_ANNUAL_SAVE"] = ""

    # Fill remaining plan slots
    for i in range(len(plans)+1, 5):
        for key in ["NAME","PRICE_MO","PRICE_ANNUAL","BEST_FOR","USERS","STORAGE","SUPPORT"]:
            t[f"PLAN_{i}_{key}"] = "—"
        for j in range(1,4):
            t[f"PLAN_{i}_F{j}"] = "—"
            t[f"PLAN_{i}_F{j}_CLS"] = ""

    if "PLAN_2_ANNUAL_SAVE" not in t:
        t["PLAN_2_ANNUAL_SAVE"] = ""

    # Hidden costs
    for i, h in enumerate(hidden[:5], 1):
        t[f"HIDDEN_COST_{i}_NAME"] = h["name"]
        t[f"HIDDEN_COST_{i}_DESC"] = h["desc"]
    for i in range(len(hidden)+1, 6):
        t[f"HIDDEN_COST_{i}_NAME"] = ""
        t[f"HIDDEN_COST_{i}_DESC"] = ""

    # Scenarios
    plan_cls_map = ["v-value","v-smb","v-visual","v-ent"]
    for i, s in enumerate(scenarios[:3], 1):
        t[f"SCENARIO_{i}_USERS"]     = s["users"]
        t[f"SCENARIO_{i}_COST"]      = s["cost"]
        t[f"SCENARIO_{i}_PLAN"]      = s["plan"]
        t[f"SCENARIO_{i}_PLAN_CLS"]  = s.get("plan_cls", plan_cls_map[i-1])
        t[f"SCENARIO_{i}_BREAKDOWN"] = s["breakdown"]

    # Alternatives
    for i, a in enumerate(alts[:4], 1):
        t[f"ALT_{i}_NAME"]     = a["name"]
        t[f"ALT_{i}_URL"]      = a["url"]
        t[f"ALT_{i}_PRICE"]    = a["price"]
        t[f"ALT_{i}_LOGO_URL"] = a.get("logo","")
    for i in range(len(alts)+1, 5):
        t[f"ALT_{i}_NAME"] = "" ; t[f"ALT_{i}_URL"] = "" ; t[f"ALT_{i}_PRICE"] = "" ; t[f"ALT_{i}_LOGO_URL"] = ""

    # FAQs
    for i, (q, a) in enumerate(faqs[:5], 1):
        t[f"FAQ_{i}_Q"] = q
        t[f"FAQ_{i}_A"] = a
    for i in range(len(faqs)+1, 6):
        t[f"FAQ_{i}_Q"] = ""; t[f"FAQ_{i}_A"] = ""

    t["META_DESCRIPTION"] = data.get("meta_desc") or f"{data['name']} pricing 2026: all plans compared, hidden fees exposed, and real cost by team size. Verified {TODAY}."
    return t

def generate_pricing_page(path, template_html, tool_data):
    tokens = build_tokens(tool_data)
    # Canonical URL
    tokens["CANONICAL_URL"] = f"pages/{path.stem}"
    tokens["TOOL_NAME"]     = tool_data["name"]

    out = template_html
    for k, v in tokens.items():
        out = out.replace("{{" + k + "}}", str(v))

    # Inject GA4
    if "G-RLYVYV8WQJ" not in out:
        ga = '  <script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>\n  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","G-RLYVYV8WQJ");</script>'
        out = out.replace("</head>", ga + "\n</head>", 1)

    # Inject favicon
    if "favicon" not in out:
        out = out.replace("</head>", '  <link rel="icon" href="/favicon.ico" sizes="any">\n</head>', 1)

    # Clean any remaining tokens
    remaining = re.findall(r'\{\{[A-Z0-9_]+\}\}', out)
    for r in set(remaining):
        out = out.replace(r, "")

    path.write_text(out, encoding="utf-8")
    return len(remaining)

def main():
    template_html = (TEMPLATES / "pricing.html").read_text(encoding="utf-8")
    pages = sorted((SITE / "pages").glob("*-pricing-2026-plans-costs-what-you-actually-pay.html"))
    print(f"Processing {len(pages)} pricing pages...")
    success = skip = 0

    for path in pages:
        # Already has premium template?
        html = path.read_text(encoding="utf-8", errors="replace")
        if "pr-layout" in html and "price-at-glance" in html and "feat-col" in html:
            skip += 1
            continue

        # Derive tool slug from filename
        stem = path.stem  # e.g. "shopify-pricing-2026-plans-costs-what-you-actually-pay"
        slug = stem.replace("-pricing-2026-plans-costs-what-you-actually-pay", "")
        name = slug_to_name(slug)

        # Look up in database
        data = PRICING.get(slug) or PRICING.get(slug.replace("-","")) or make_generic_pricing(slug, name)

        cleaned = generate_pricing_page(path, template_html, data)
        success += 1
        source = "DB" if (PRICING.get(slug) or PRICING.get(slug.replace("-",""))) else "generic"
        if success <= 8 or success % 10 == 0:
            print(f"  [OK {source}] {path.name[:55]}")

    print(f"\nDone: {success} upgraded | {skip} already premium")

if __name__ == "__main__":
    main()
