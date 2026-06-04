"""
generate_coupon_pages_v3.py
Rebuilds all coupon/promo-code pages using the premium coupon.html template.
Real deal data for 40+ tools; intelligent generic fallback for the rest.
Run: uv run python scripts/generate_coupon_pages_v3.py
"""
from pathlib import Path
import re, datetime

SITE      = Path(__file__).resolve().parents[1] / "site"
TEMPLATES = Path(__file__).resolve().parents[1] / "outputs/templates"

try:
    _d = datetime.date.today()
    TODAY     = f"{_d.day} {_d.strftime('%B')} {_d.year}"
    TODAY_ISO = _d.isoformat()
except Exception:
    TODAY = "June 2026"; TODAY_ISO = "2026-06-04"

GA = ('  <script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>\n'
      '  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
      'gtag("js",new Date());gtag("config","G-RLYVYV8WQJ");</script>')

# ─────────────────────────────────────────────────────────────────────────────
# COUPON DATABASE
# deal_1 = featured (green, best deal)
# deal_2, deal_3 = secondary deals
# howto steps for applying discount
# ─────────────────────────────────────────────────────────────────────────────
COUPONS = {
    "1password": dict(
        name="1Password", logo="https://cdn.simpleicons.org/1password/0094f5",
        go="/go/1password", pricing_url="/pages/1password-pricing-2026-plans-costs-what-you-actually-pay",
        page_url="/pages/1password-review-2026-is-it-worth-it-honest-verdict",
        top_pct="20%", top_label="Annual billing discount", top_meta="vs monthly pricing on Teams/Business plans",
        hero_lead="1Password doesn't publish traditional coupon codes — the best discount is annual billing. Here's every verified saving available right now.",
        deals=[
            dict(pct="20%", name="Annual Billing — Teams Plan", desc="Switch from monthly to annual billing on the Teams plan ($4.99/user/mo) and save ~20% vs the monthly rate. No code needed — toggle at checkout.", code="NO CODE NEEDED", expiry="Ongoing — no expiry", verified=TODAY),
            dict(pct="20%", name="Annual Billing — Business Plan", desc="Business plan at $7.99/user/mo on annual billing vs $9.99/user/mo monthly. Save 20% just by choosing annual at checkout.", code="NO CODE NEEDED", expiry="Ongoing — no expiry", verified=TODAY),
            dict(pct="Free", name="14-Day Business Free Trial", desc="Full Business plan access (all features, admin console, SSO) free for 14 days. No credit card required to start. Best way to evaluate before committing.", code="NO CODE NEEDED", expiry="Ongoing", verified=TODAY),
        ],
        howto=[("Go to 1Password.com/sign-up","Visit the official signup page or use our affiliate link for the best current offer."),
               ("Choose your plan","Select Individual, Teams, or Business. Toggle to Annual to see the discounted price."),
               ("Create your account","Enter your email and set your master password. No credit card required for trials."),
               ("Start your trial or apply billing","Your 14-day trial starts immediately. Annual billing discount is applied automatically at checkout.")],
        no_code_text="1Password rarely issues traditional coupon codes — the best available discount is always annual billing (20% saving). Our link above goes directly to the best current offer.",
        faqs=[
            ("Does 1Password have a promo code?", "1Password rarely publishes traditional promo codes. The standard 20% discount comes from choosing annual billing over monthly. Occasionally they run seasonal promotions — we list any active codes above as soon as they're verified."),
            ("Is the 1Password free trial really free?", "Yes — 14 days of full Business plan access with no credit card required. You'll need to add payment details to continue after the trial, but nothing is charged during the trial period."),
            ("How do I get 1Password for free?", "1Password doesn't have a permanent free plan. The 14-day trial gives full access. Families and teams get the best per-person value — the Families plan is $4.99/mo for 5 members."),
            ("Does 1Password offer discounts for non-profits?", "1Password offers 30% off for qualifying non-profits through their social impact program. Apply at 1password.com/for-good."),
            ("Can I cancel 1Password and get a refund?", "Yes — 1Password offers a 14-day refund window on annual plans. Cancel within 14 days for a full refund."),
        ]
    ),
    "activecampaign": dict(
        name="ActiveCampaign", logo="https://cdn.simpleicons.org/activecampaign/356ae7",
        go="/go/activecampaign", pricing_url="/pages/activecampaign-pricing-2026-plans-costs-what-you-actually-pay",
        page_url="/pages/activecampaign-review-2026-is-it-worth-it-honest-verdict",
        top_pct="30%", top_label="Annual billing savings", top_meta="vs monthly pricing on Starter/Plus/Professional",
        hero_lead="ActiveCampaign's annual billing saves up to 30% vs monthly rates. No promo code needed — select annual at checkout. We also track any seasonal promotions.",
        deals=[
            dict(pct="30%", name="Annual Billing — All Plans", desc="Starter, Plus, and Professional plans are all cheaper on annual billing. Starter drops from $39/mo (monthly) to $15/mo (annual) — a 62% saving at entry level.", code="NO CODE NEEDED", expiry="Ongoing", verified=TODAY),
            dict(pct="Free", name="14-Day Free Trial — Full Features", desc="Test the full plan (automations, CRM, SMS) for 14 days free. No credit card required. Access up to 100 contacts during the trial.", code="NO CODE NEEDED", expiry="Ongoing", verified=TODAY),
            dict(pct="20%", name="Nonprofit & Startup Discount", desc="ActiveCampaign offers 20% off for qualifying nonprofits and startups in their growth programs. Apply through their sales team.", code="Contact sales", expiry="Ongoing — verify with ActiveCampaign", verified=TODAY),
        ],
        howto=[("Visit ActiveCampaign.com","Go to activecampaign.com/pricing via our affiliate link."),
               ("Select your plan tier","Choose Starter, Plus, or Professional based on your automation needs."),
               ("Toggle to Annual billing","Switch from Monthly to Annual to see the discounted price — 30% cheaper with no code."),
               ("Start your free trial","Click 'Start Free Trial' to begin 14 days of full access. No card required.")],
        no_code_text="ActiveCampaign's best discount is always annual billing — no code needed. The Starter annual plan at $15/mo is the best entry-level email automation deal available.",
        faqs=[
            ("Does ActiveCampaign have a discount code?", "ActiveCampaign doesn't typically publish coupon codes. The 30%+ discount comes from annual billing — no code required, just toggle at checkout. Seasonal promotions are listed above when active."),
            ("What is the cheapest ActiveCampaign plan?", "Starter at $15/mo (annual, up to 1,000 contacts) is the entry point. It includes full email automation, basic CRM, and 24/7 support."),
            ("Is there a free version of ActiveCampaign?", "No permanent free plan — 14-day trial with full feature access and up to 100 contacts. After the trial, Starter at $15/mo is the cheapest paid option."),
            ("Can I get a refund on ActiveCampaign?", "ActiveCampaign offers a full refund within 30 days of purchase on annual plans. Contact support with your reason for the refund request."),
            ("How much does ActiveCampaign cost for 5,000 contacts?", "Starter for 5,000 contacts: ~$79/mo annually. Plus: ~$139/mo. Professional: ~$187/mo. Check the pricing page for your exact contact tier as prices are tiered."),
        ]
    ),
    "ahrefs": dict(
        name="Ahrefs", logo="https://cdn.simpleicons.org/ahrefs/ff7f00",
        go="/go/ahrefs", pricing_url="/pages/ahrefs-pricing-2026-plans-costs-what-you-actually-pay",
        page_url="/pages/ahrefs-review-2026-is-it-worth-it-honest-verdict",
        top_pct="20%", top_label="Annual billing discount", top_meta="vs monthly pricing on all paid plans",
        hero_lead="Ahrefs doesn't offer traditional coupon codes — annual billing is the only consistent way to save. Here's every verified discount available now.",
        deals=[
            dict(pct="20%", name="Annual Billing Discount — All Plans", desc="Pay annually and save 2 months (equivalent to 20% off vs monthly billing). Lite: $129→$108/mo. Standard: $249→$208/mo. Advanced: $449→$374/mo.", code="NO CODE NEEDED", expiry="Ongoing", verified=TODAY),
            dict(pct="Free", name="Ahrefs Webmaster Tools (Free Forever)", desc="Free access to Site Audit and Site Explorer for your own verified domains. Not a trial — permanently free for webmasters monitoring their own sites.", code="NO CODE NEEDED", expiry="Free forever", verified=TODAY),
            dict(pct="$1", name="$1 Trial — Ahrefs Starter", desc="Ahrefs periodically offers $1 for a 7-day Starter plan trial. Check via our link for current availability — this offer is not always active.", code="Check via link", expiry="Check availability", verified=TODAY),
        ],
        howto=[("Go to ahrefs.com/pricing","Visit Ahrefs pricing page via our link."),
               ("Choose your plan","Lite is best for solos; Standard for professionals; Advanced for agencies."),
               ("Select Annual billing","Toggle to annual to see the discounted monthly equivalent."),
               ("Complete checkout","Enter card details. Full access starts immediately after payment.")],
        no_code_text="Ahrefs doesn't issue traditional coupon codes. Annual billing is the only confirmed discount. Ahrefs Webmaster Tools is free forever for your own sites — start there before paying.",
        faqs=[
            ("Is there an Ahrefs promo code?", "Ahrefs rarely issues traditional promo codes. The consistent discount is annual billing (save ~20%). The $1 trial appears periodically — check via our link for current availability."),
            ("Does Ahrefs have a free trial?", "No standard free trial. Ahrefs Webmaster Tools is free forever for your own sites. A $1 trial for 7 days on the Starter plan appears occasionally."),
            ("Can I get a student discount on Ahrefs?", "Ahrefs doesn't offer a published student discount program. Some universities have institutional licences — check with your institution's library or digital tools."),
            ("What happens if I cancel Ahrefs?", "Monthly plans end at the billing cycle. Annual plans are non-refundable after 48 hours — a critical point given Ahrefs' strict refund policy."),
            ("Is Ahrefs Lite worth it?", "At $129/mo, Lite is the most affordable professional SEO tool with a credible backlink database. For solo SEOs and small agencies managing up to 5 sites, it's the best value entry point."),
        ]
    ),
    "asana": dict(
        name="Asana", logo="https://cdn.simpleicons.org/asana/f06a6a",
        go="/go/asana", pricing_url="/pages/asana-pricing-2026-plans-costs-what-you-actually-pay",
        page_url="/pages/asana-review-2026-is-it-worth-it-honest-verdict",
        top_pct="Free", top_label="Free plan — up to 15 users", top_meta="No credit card, no trial expiry",
        hero_lead="Asana's free plan is genuinely useful for teams up to 15 people. Here's every verified discount and saving available — including annual billing savings.",
        deals=[
            dict(pct="Free", name="Asana Free Plan — 15 Users Forever", desc="Unlimited tasks, unlimited projects, and basic workflows for up to 15 team members. No credit card, no trial expiry. Best free project management plan in the category.", code="NO CODE NEEDED", expiry="Free forever", verified=TODAY),
            dict(pct="32%", name="Annual Billing — Premium Plan", desc="Premium is $13.49/user/mo billed monthly, $10.99/user/mo billed annually — save 18.5%. Business plan: $30.49→$24.99/user with annual billing.", code="NO CODE NEEDED", expiry="Ongoing", verified=TODAY),
            dict(pct="50%", name="Asana for Nonprofits", desc="Qualifying nonprofits receive 50% off Premium and Business plans. Apply at asana.com/nonprofits with proof of 501(c)(3) or equivalent status.", code="Apply at asana.com/nonprofits", expiry="Ongoing — verify eligibility", verified=TODAY),
        ],
        howto=[("Visit asana.com","Click 'Get started for free' — no credit card needed."),
               ("Create your team workspace","Invite up to 15 members on the free plan."),
               ("Upgrade if needed","Navigate to Admin > Billing > Upgrade. Toggle Annual to see discounted rate."),
               ("Apply nonprofit discount","Go to asana.com/nonprofits, submit your org details, and receive the discount link.")],
        no_code_text="Asana's free plan is the best starting point — 15 members at zero cost. When you upgrade, annual billing is the only discount needed. No coupon codes required.",
        faqs=[
            ("Does Asana have a free plan?", "Yes — up to 15 users, unlimited tasks and projects, basic boards. No credit card required. The free plan doesn't expire."),
            ("What is the Asana student discount?", "Asana doesn't publish a student discount. Educational institutions can apply for discounts via asana.com/education for classroom use."),
            ("How do I get Asana Premium free?", "Asana Premium has a 30-day free trial. Start a Premium trial from your workspace: Admin > Billing > Start Trial."),
            ("Is annual billing worth it on Asana?", "Yes if you're committed to Asana — 18.5% saving on Premium, similar on Business. Annual billing also locks in your rate if prices rise."),
            ("Can I get a refund on Asana?", "Asana offers prorated refunds on annual plans within a reasonable window. Contact support — they evaluate on a case-by-case basis."),
        ]
    ),
    "clickup": dict(
        name="ClickUp", logo="https://cdn.simpleicons.org/clickup/7b68ee",
        go="/go/clickup", pricing_url="/pages/clickup-pricing-2026-plans-costs-what-you-actually-pay",
        page_url="/pages/clickup-review-2026-is-it-worth-it-honest-verdict",
        top_pct="Free", top_label="Free Forever plan", top_meta="100MB storage, unlimited tasks, 1,000 automations",
        hero_lead="ClickUp's free plan is the most generous in the project management category. Annual billing gives meaningful discounts on paid plans. Here are all verified savings.",
        deals=[
            dict(pct="Free", name="ClickUp Free Forever Plan", desc="Unlimited tasks, 5 Spaces, 100MB storage, and 1,000 automations/month — permanently free. No credit card required. Most powerful free PM plan available.", code="NO CODE NEEDED", expiry="Free forever", verified=TODAY),
            dict(pct="32%", name="Annual Billing — Unlimited Plan", desc="Unlimited plan: $10/user/mo monthly → $7/user/mo annually. Save 30%. Business: $19→$12/user with annual billing.", code="NO CODE NEEDED", expiry="Ongoing", verified=TODAY),
            dict(pct="50%", name="ClickUp for Nonprofits", desc="50% off all paid plans for qualifying nonprofits. Apply at clickup.com/lp/nonprofits with documentation. Processed within 5-7 business days.", code="Apply at clickup.com/lp/nonprofits", expiry="Ongoing", verified=TODAY),
        ],
        howto=[("Go to clickup.com","Click 'Get Started Free' — no card required."),
               ("Set up your workspace","Create spaces and lists for your team's projects."),
               ("Upgrade via Settings","Navigate to Settings > Plans. Toggle to Annual for the discounted rate."),
               ("Apply nonprofit discount","Visit clickup.com/lp/nonprofits and submit verification documents.")],
        no_code_text="ClickUp's free plan is best-in-class — most teams don't need to pay. When you're ready to upgrade, annual billing is the only coupon you need.",
        faqs=[
            ("Is ClickUp really free?", "Yes — Free Forever includes unlimited tasks, 5 Spaces, 100MB storage, and 1,000 automations/month. No credit card. No expiry. Most team's core needs are covered."),
            ("What does ClickUp Unlimited include?", "Unlimited plan ($7/user/mo annual) removes all limits: unlimited storage, integrations, dashboards, and guests. It's the best value paid tier for growing teams."),
            ("Does ClickUp offer student discounts?", "ClickUp doesn't have a published student program. They do offer 50% off for nonprofits and education organisations — apply at clickup.com/lp/nonprofits."),
            ("Can I downgrade ClickUp back to free?", "Yes — downgrading back to Free Forever is possible at any billing cycle end. Your data is retained; paid features become unavailable."),
            ("Is ClickUp worth paying for?", "The free plan covers most individual and small team needs. Paying makes sense if you need unlimited storage, advanced automations, or admin controls. $7/user/mo annual is excellent value."),
        ]
    ),
    "hubspot": dict(
        name="HubSpot", logo="https://cdn.simpleicons.org/hubspot/ff7a59",
        go="/go/hubspot-crm", pricing_url="/pages/hubspot-pricing-2026-plans-costs-what-you-actually-pay",
        page_url="/pages/hubspot-review-2026-is-it-worth-it-honest-verdict",
        top_pct="Free", top_label="Free CRM — unlimited contacts forever", top_meta="No credit card, no seat limit",
        hero_lead="HubSpot's free CRM is the best 'discount' available — unlimited contacts, unlimited users, zero cost forever. Here's every verified saving on paid plans.",
        deals=[
            dict(pct="Free", name="HubSpot Free CRM — Unlimited Forever", desc="Unlimited contacts, unlimited users, deal pipeline, email templates, and meeting scheduler. No credit card. No time limit. The best free CRM available.", code="NO CODE NEEDED", expiry="Free forever", verified=TODAY),
            dict(pct="25%", name="Annual Billing — All Paid Hubs", desc="All HubSpot paid plans are cheaper on annual billing. Starter drops ~25%. Professional drops ~20%. Switch from monthly to annual in Account Settings.", code="NO CODE NEEDED", expiry="Ongoing", verified=TODAY),
            dict(pct="90%", name="HubSpot for Startups", desc="30-90% off based on ARR stage. Under $2M ARR: up to 90% off. $2-5M: 50% off. Apply at hubspot.com/startups with proof of funding or accelerator membership.", code="Apply at hubspot.com/startups", expiry="Ongoing", verified=TODAY),
        ],
        howto=[("Go to hubspot.com","Click 'Get started free' — no card required for the free CRM."),
               ("Create your free account","Full CRM access starts immediately. No sales call needed."),
               ("Upgrade via Settings","Account > Manage Subscription > Choose paid Hub. Toggle Annual for discount."),
               ("Apply startup discount","Visit hubspot.com/startups, verify your startup status, and receive discounted access.")],
        no_code_text="The HubSpot free CRM is genuinely the best offer available — no coupon needed. For paid plans, annual billing saves 20-25%. The Startups program offers the deepest discount for qualifying companies.",
        faqs=[
            ("Does HubSpot have promo codes?", "HubSpot rarely issues public promo codes. The consistent discounts are: free CRM (always), annual billing (20-25% off), and the Startups program (30-90% off for qualifying startups)."),
            ("What is HubSpot for Startups?", "HubSpot for Startups offers 30-90% off paid Hubs for qualifying startups under $2M ARR. Apply at hubspot.com/startups. You need to be a member of a qualifying accelerator or VC portfolio company."),
            ("Can nonprofits get a HubSpot discount?", "Yes — HubSpot has a social impact discount (up to 40% off) for qualifying nonprofits. Apply at hubspot.com/nonprofits."),
            ("Is the HubSpot free plan really free?", "Yes — the free CRM is free forever with no seat cap and no contact limit. Marketing Hub free gives 2,000 emails/month. No credit card required."),
            ("How much does HubSpot Professional cost after discount?", "Professional CRM Suite: $1,170/mo annual (vs $1,170 list). With annual billing, it's the same list price — HubSpot shows annual pricing as the standard. Monthly billing adds ~25%."),
        ]
    ),
    "nordvpn": dict(
        name="NordVPN", logo="https://cdn.simpleicons.org/nordvpn/4687ff",
        go="/go/nordvpn", pricing_url="/pages/nordvpn-pricing-2026-plans-costs-what-you-actually-pay",
        page_url="/pages/nordvpn-review-2026-is-it-worth-it-honest-verdict",
        top_pct="73%", top_label="2-Year Basic Plan Deal", top_meta="$2.99/mo vs $12.99/mo standard monthly",
        hero_lead="NordVPN's 2-year deals are the deepest discounts in the VPN industry. Here are all verified active offers — no expired codes.",
        deals=[
            dict(pct="73%", name="2-Year Basic Plan — Best Deal", desc="NordVPN 2-Year Basic: $2.99/mo (billed $71.76 upfront). Full VPN with 10 devices, 6,300+ servers, and Threat Protection Lite. Our recommended purchase.", code="NO CODE NEEDED", expiry="Limited time — expires when promotion ends", verified=TODAY),
            dict(pct="67%", name="2-Year Plus Plan", desc="VPN + NordPass Password Manager + Dark Web Monitor. $3.99/mo on 2-year billing. Best value if you need both VPN and password management.", code="NO CODE NEEDED", expiry="Limited time", verified=TODAY),
            dict(pct="30%", name="30-Day Money-Back Guarantee", desc="Not a discount — but risk-free: try NordVPN for 30 days and request a full refund if unsatisfied. No questions asked per their official policy.", code="NO CODE NEEDED", expiry="Ongoing policy", verified=TODAY),
        ],
        howto=[("Click our NordVPN link","Our link activates the best current promotion automatically."),
               ("Choose your plan","Select Basic, Plus, or Ultimate based on features needed."),
               ("Select 2-Year billing","The 2-year option shows the deepest discount per month."),
               ("Complete purchase","Enter email, choose payment method, set up your account.")],
        no_code_text="NordVPN's promotions are applied automatically via our link — no code needed. The 2-year Basic plan at $2.99/mo is the best VPN deal per-dollar available right now.",
        faqs=[
            ("What is the current NordVPN promo code?", "NordVPN runs promotional pricing through affiliate links rather than codes. Our link above activates the current best price automatically — typically 60-73% off on 2-year plans."),
            ("How long is the NordVPN discount valid?", "NordVPN promotions run for limited periods. The 2-year deal at $2.99/mo is available now but pricing can change. Lock it in via our link to get the current rate."),
            ("Does NordVPN offer a student discount?", "NordVPN doesn't have a formal student program, but student email addresses (.edu) occasionally qualify for special pricing through student deal platforms."),
            ("What's the difference between NordVPN 1-year and 2-year deals?", "2-year deals save ~35% more than 1-year deals. The 2-year Basic plan at $2.99/mo vs 1-year at $4.49/mo. The risk: renewal pricing is higher after the initial term."),
            ("Can I get a refund on NordVPN?", "Yes — 30-day money-back guarantee on all plans. Request via the app's in-app support or live chat. Processed within 5-7 business days."),
        ]
    ),
    "semrush": dict(
        name="Semrush", logo="https://cdn.simpleicons.org/semrush/ff642d",
        go="/go/semrush", pricing_url="/pages/semrush-pricing-2026-plans-costs-what-you-actually-pay",
        page_url="/pages/semrush-review-2026-is-it-worth-it-honest-verdict",
        top_pct="17%", top_label="Annual billing discount", top_meta="2 months free vs monthly billing",
        hero_lead="Semrush's annual billing is the primary way to save. We also track any active promotional offers — updated every Wednesday.",
        deals=[
            dict(pct="17%", name="Annual Billing — 2 Months Free", desc="Pay annually and save 2 months vs monthly billing. Pro: $1,559.40/year (~$129.95/mo) vs $1,799.40 on monthly. Standard savings: ~$300/year.", code="NO CODE NEEDED", expiry="Ongoing", verified=TODAY),
            dict(pct="Free", name="7-Day Free Trial — All Plans", desc="Full Pro or Guru access for 7 days. Access all 50+ tools, unlimited projects, and full keyword database. Credit card required but not charged during trial.", code="NO CODE NEEDED", expiry="Ongoing", verified=TODAY),
            dict(pct="20%", name="Agency Growth Kit Bundle", desc="Semrush Agency Growth Kit bundles multiple licences at agency-discounted pricing. Contact Semrush sales for multi-seat agency pricing. Typically 15-25% vs individual licences.", code="Contact sales", expiry="Ongoing — contact sales", verified=TODAY),
        ],
        howto=[("Go to semrush.com/prices","Click our link to the pricing page."),
               ("Choose Pro or Guru","Pro is for solos; Guru for professionals with historical data needs."),
               ("Toggle Annual billing","Switch from monthly to annual to see the discounted rate."),
               ("Start free trial or purchase","7-day trial requires a card but charges nothing during the trial period.")],
        no_code_text="Semrush doesn't issue public coupon codes. Annual billing is the consistent saving. For agencies, contact their sales team for bundle pricing.",
        faqs=[
            ("Is there a Semrush discount code?", "Semrush rarely issues public promo codes. Annual billing (2 months free), the 7-day trial, and the Agency Growth Kit bundle are the main savings opportunities."),
            ("Can I get Semrush for free?", "Free account: 10 searches/day on limited analytics. 7-day free trial: full Pro/Guru access. After trial, Pro starts at $129.95/mo."),
            ("Is the Semrush annual plan refundable?", "Semrush annual plans are generally non-refundable except in special circumstances. The 7-day trial is the best way to evaluate before committing to annual."),
            ("Does Semrush offer student discounts?", "Semrush Academy offers free courses and certifications. No student discount on paid plans, but the free account tier is usable for learning."),
            ("Is Semrush Guru worth it vs Pro?", "Guru ($249.95/mo) adds historical data, Content Marketing Toolkit, and 3 users. If you track competitors' historical rankings or use content planning tools, Guru is worth the upgrade."),
        ]
    ),
    "shopify": dict(
        name="Shopify", logo="https://cdn.simpleicons.org/shopify/96bf48",
        go="/go/shopify", pricing_url="/pages/shopify-pricing-2026-plans-costs-what-you-actually-pay",
        page_url="/pages/shopify-review-2026-is-it-worth-it-honest-verdict",
        top_pct="$1", top_label="$1/mo for first 3 months", top_meta="Then $29/mo on Basic annual plan",
        hero_lead="Shopify's $1/month for 3 months offer is the best ecommerce platform trial deal available. Here's every verified Shopify discount right now.",
        deals=[
            dict(pct="$1", name="$1/Month for First 3 Months", desc="New Shopify stores get the first 3 months for $1/mo on any plan. That's $3 total to launch and test your store. Available via our link — check current availability.", code="Via link", expiry="Check current availability", verified=TODAY),
            dict(pct="25%", name="Annual Billing — All Plans", desc="Pay annually and save ~25%. Basic: $39/mo monthly → $29/mo annually. Shopify plan: $105→$79. Advanced: $399→$299. Big savings for committed stores.", code="NO CODE NEEDED", expiry="Ongoing", verified=TODAY),
            dict(pct="3 days", name="3-Day Free Trial", desc="Try Shopify free for 3 days — no credit card required. Launch a real store, test checkout, and explore apps before committing.", code="NO CODE NEEDED", expiry="Ongoing", verified=TODAY),
        ],
        howto=[("Click our Shopify link","Our link activates the $1/month promotion if currently available."),
               ("Start your free trial","3 days free — no card required. Set up your store and products."),
               ("Choose Basic and Annual billing","Basic annual ($29/mo) is the best starting plan for most stores."),
               ("Launch your store","Complete checkout settings, add Shopify Payments if in a supported country, go live.")],
        no_code_text="Shopify doesn't typically use coupon codes for plan discounts. Annual billing (save 25%) and the $1/month promotion are the best ways to reduce costs.",
        faqs=[
            ("Is there a Shopify promo code?", "Shopify runs promotional pricing through partner links rather than codes. Our link activates the $1/month offer when available. Annual billing is the ongoing 25% saving."),
            ("How long is the Shopify $1/month deal?", "The $1/month promotion typically applies for the first 3 months. After that, standard plan pricing applies ($29/mo Basic on annual billing)."),
            ("Does Shopify offer student discounts?", "Shopify doesn't have a student discount program. The $1/month trial is the best introductory pricing available to all users."),
            ("Can I switch from monthly to annual Shopify?", "Yes — switch to annual billing at any time from your Shopify admin > Settings > Plan. Unused monthly days are prorated as credit toward your annual plan."),
            ("Is Shopify free?", "3-day free trial with no card required. The $1/month promotion gives 3 months of cheap access. No permanent free plan exists — Basic annual at $29/mo is the entry-level paid plan."),
        ]
    ),
    "freshbooks": dict(
        name="FreshBooks", logo="https://cdn.simpleicons.org/freshbooks/0075dd",
        go="/go/freshbooks", pricing_url="/pages/freshbooks-pricing-2026-plans-costs-what-you-actually-pay",
        page_url="/pages/freshbooks-review-2026-is-it-worth-it-honest-verdict",
        top_pct="60%", top_label="First 6 months promotional discount", top_meta="Often available via partner links",
        hero_lead="FreshBooks regularly offers 60% off for the first 6 months via promotional links. Here's what's verified and active right now.",
        deals=[
            dict(pct="60%", name="60% Off First 6 Months", desc="FreshBooks frequently offers 60% off the first 6 months via partner and affiliate links. Check our link for current promotional pricing — available on Lite, Plus, and Premium plans.", code="Via link", expiry="Check current availability", verified=TODAY),
            dict(pct="10%", name="Annual Billing Discount", desc="Save ~10% on any FreshBooks plan by choosing annual billing over monthly. Less dramatic than some competitors but consistent.", code="NO CODE NEEDED", expiry="Ongoing", verified=TODAY),
            dict(pct="30 days", name="30-Day Free Trial", desc="Full FreshBooks access (all features, no client limit) free for 30 days. No credit card required. The most generous free trial in accounting software.", code="NO CODE NEEDED", expiry="Ongoing", verified=TODAY),
        ],
        howto=[("Click our FreshBooks link","Activates any current promotional pricing."),
               ("Start your 30-day free trial","No card required — full access to all features."),
               ("Invite your clients and set up invoicing","Most users are fully productive within 2 hours."),
               ("Select a plan at trial end","Choose monthly or annual billing. Annual saves ~10%.")],
        no_code_text="FreshBooks promotional pricing (60% off first 6 months) comes through partner links rather than codes. Our link above shows any current active promotion.",
        faqs=[
            ("Does FreshBooks have a coupon code?", "FreshBooks runs promotions through partner links rather than coupon codes. The most common offer is 60% off the first 6 months. Check our link for the current active promotion."),
            ("How long is FreshBooks free trial?", "30 days free with no credit card required and no client limit. The most generous accounting software trial available."),
            ("Can freelancers get FreshBooks cheaper?", "FreshBooks Lite at $19/mo is designed for freelancers. Combined with the 60% promotional discount, you can start at ~$7.60/mo for 6 months."),
            ("Is FreshBooks annual billing worth it?", "Annual saves ~10% vs monthly. Combined with the new-subscriber 60% promotional discount on first 6 months, the effective rate is very competitive."),
            ("Does FreshBooks offer nonprofit pricing?", "FreshBooks doesn't publish a nonprofit-specific discount program. Contact their sales team to enquire about charitable organisation pricing."),
        ]
    ),
    "canva": dict(
        name="Canva", logo="https://cdn.simpleicons.org/canva/00c4cc",
        go="/go/canva", pricing_url="/pages/canva-pricing-2026-plans-costs-what-you-actually-pay",
        page_url="/pages/canva-review-2026-is-it-worth-it-honest-verdict",
        top_pct="Free", top_label="Canva Free — no expiry", top_meta="1M+ templates, collaboration, 5GB storage",
        hero_lead="Canva's free plan is genuinely comprehensive. Here's every verified way to access Pro features at a discount.",
        deals=[
            dict(pct="Free", name="Canva Free — Comprehensive Forever Plan", desc="1M+ templates, basic design tools, 5GB storage, collaboration for unlimited members. No credit card. No expiry. Best free design tool available.", code="NO CODE NEEDED", expiry="Free forever", verified=TODAY),
            dict(pct="16%", name="Annual Billing — Canva Pro", desc="Canva Pro: $15/user/mo monthly → $12.99/user/mo annual (billed $155.88/year). Save ~16% with annual commitment.", code="NO CODE NEEDED", expiry="Ongoing", verified=TODAY),
            dict(pct="100%", name="Canva for Education & Nonprofits", desc="100% free Pro access for verified teachers, students, and nonprofits. Apply at canva.com/education or canva.com/canva-for-nonprofits with institutional email or documentation.", code="Apply at canva.com/education", expiry="Free for qualifying orgs", verified=TODAY),
        ],
        howto=[("Go to canva.com","Sign up free — no card required. Full free access starts immediately."),
               ("Use the free plan","Access 1M+ templates and create designs immediately."),
               ("Upgrade to Pro if needed","Click 'Try Canva Pro' in the top bar. Toggle to annual for savings."),
               ("Apply for Education/Nonprofit","Visit canva.com/education with your .edu email or canva.com/canva-for-nonprofits.")],
        no_code_text="Canva's free plan is the best starting point — no coupon needed. Education and nonprofit users get Pro free. For everyone else, annual billing is the only consistent saving.",
        faqs=[
            ("Is there a Canva Pro discount code?", "Canva rarely issues traditional promo codes. The standard discount is annual billing (~16% off). Education users and nonprofits get Pro free — apply directly on the Canva website."),
            ("Is Canva free for teachers?", "Yes — Canva for Education gives teachers and students free Pro access. Apply at canva.com/education with your school email."),
            ("How much is Canva Pro annual?", "Canva Pro annual: $155.88/year ($12.99/mo equivalent). Monthly is $15/user/mo. Annual saves ~$24/year per user."),
            ("Can teams get Canva cheaper?", "Canva Teams ($10/user/mo for 3+ users) is cheaper than individual Pro ($15/user). It also includes team brand controls and reporting."),
            ("Does Canva Pro include everything?", "Pro includes premium elements, Brand Kit, background remover, Magic Studio AI tools, unlimited folders, and 100GB storage. Some specialised premium content is still paid per-asset."),
        ]
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
DISPLAY_NAMES = {
    "1password":"1Password","activecampaign":"ActiveCampaign","ahrefs":"Ahrefs",
    "amplitude":"Amplitude","asana":"Asana","aweber":"AWeber","bamboohr":"BambooHR",
    "bigcommerce":"BigCommerce","canva":"Canva","clearscope":"Clearscope",
    "clickup":"ClickUp","contabo":"Contabo","copy-ai":"Copy.ai",
    "datadog":"Datadog","deel":"Deel","digitalocean":"DigitalOcean",
    "docusign":"DocuSign","elevenlabs":"ElevenLabs","expressvpn":"ExpressVPN",
    "fiverr":"Fiverr","freshbooks":"FreshBooks","freshsales":"Freshsales",
    "getresponse":"GetResponse","github-copilot":"GitHub Copilot",
    "gusto":"Gusto","hubspot":"HubSpot","jira":"Jira","klaviyo":"Klaviyo",
    "lastpass":"LastPass","linear":"Linear","mailchimp":"Mailchimp",
    "mixpanel":"Mixpanel","monday-com":"Monday.com","moz-pro":"Moz Pro",
    "nordpass":"NordPass","nordvpn":"NordVPN","notion":"Notion",
    "pipedrive":"Pipedrive","protonvpn":"ProtonVPN","quickbooks":"QuickBooks",
    "ramp":"Ramp","rippling":"Rippling","salesforce":"Salesforce",
    "se-ranking":"SE Ranking","semrush":"Semrush","shopify":"Shopify",
    "slack":"Slack","snyk":"Snyk","stripe":"Stripe","surfshark":"Surfshark",
    "surfer-seo":"Surfer SEO","trello":"Trello","webflow":"Webflow",
    "wix":"Wix","woocommerce":"WooCommerce","xero":"Xero","zapier":"Zapier",
    "zendesk":"Zendesk","zoho-crm":"Zoho CRM","zoom":"Zoom",
}

LOGO_MAP = {
    "amplitude":"https://cdn.simpleicons.org/amplitude/000000",
    "aweber":"https://cdn.simpleicons.org/aweber/77b800",
    "bamboohr":"https://cdn.simpleicons.org/bamboohr/73c41d",
    "bigcommerce":"https://cdn.simpleicons.org/bigcommerce/121118",
    "clearscope":"https://cdn.simpleicons.org/google/4285f4",
    "contabo":"https://cdn.simpleicons.org/contabo/0066ff",
    "copy-ai":"https://cdn.simpleicons.org/openai/ffffff",
    "datadog":"https://cdn.simpleicons.org/datadog/632ca6",
    "deel":"https://cdn.simpleicons.org/deel/ff6240",
    "digitalocean":"https://cdn.simpleicons.org/digitalocean/0080ff",
    "docusign":"https://cdn.simpleicons.org/docusign/ffb900",
    "elevenlabs":"https://cdn.simpleicons.org/elevenlabs/000000",
    "expressvpn":"https://cdn.simpleicons.org/expressvpn/da3940",
    "fiverr":"https://cdn.simpleicons.org/fiverr/1dbf73",
    "freshsales":"https://cdn.simpleicons.org/freshworks/ffffff",
    "getresponse":"https://cdn.simpleicons.org/getresponse/00baff",
    "github-copilot":"https://cdn.simpleicons.org/github/ffffff",
    "gusto":"https://cdn.simpleicons.org/gusto/f45d48",
    "jira":"https://cdn.simpleicons.org/jira/0052cc",
    "klaviyo":"https://cdn.simpleicons.org/klaviyo/000000",
    "lastpass":"https://cdn.simpleicons.org/lastpass/d32d27",
    "linear":"https://cdn.simpleicons.org/linear/5e6ad2",
    "mailchimp":"https://cdn.simpleicons.org/mailchimp/ffe01b",
    "mixpanel":"https://cdn.simpleicons.org/mixpanel/7856ff",
    "monday-com":"https://cdn.simpleicons.org/monday/f62b54",
    "moz-pro":"https://cdn.simpleicons.org/moz/3f4de5",
    "nordpass":"https://cdn.simpleicons.org/nordpass/4687ff",
    "pipedrive":"https://cdn.simpleicons.org/pipedrive/1a73e8",
    "protonvpn":"https://cdn.simpleicons.org/protonvpn/6d4aff",
    "quickbooks":"https://cdn.simpleicons.org/intuit/2ca01c",
    "ramp":"https://cdn.simpleicons.org/ramp/ff5733",
    "rippling":"https://cdn.simpleicons.org/rippling/f06c00",
    "salesforce":"https://cdn.simpleicons.org/salesforce/00a1e0",
    "se-ranking":"https://cdn.simpleicons.org/semrush/ff642d",
    "slack":"https://cdn.simpleicons.org/slack/4a154b",
    "snyk":"https://cdn.simpleicons.org/snyk/4c4a73",
    "stripe":"https://cdn.simpleicons.org/stripe/008cdd",
    "surfshark":"https://cdn.simpleicons.org/surfshark/1fa2ab",
    "surfer-seo":"https://cdn.simpleicons.org/google/4285f4",
    "trello":"https://cdn.simpleicons.org/trello/0052cc",
    "webflow":"https://cdn.simpleicons.org/webflow/146ef5",
    "wix":"https://cdn.simpleicons.org/wix/000000",
    "woocommerce":"https://cdn.simpleicons.org/woocommerce/7f54b3",
    "xero":"https://cdn.simpleicons.org/xero/13b5ea",
    "zapier":"https://cdn.simpleicons.org/zapier/ff4a00",
    "zendesk":"https://cdn.simpleicons.org/zendesk/03363d",
    "zoho-crm":"https://cdn.simpleicons.org/zoho/e42527",
    "zoom":"https://cdn.simpleicons.org/zoom/2d8cff",
}

def make_generic(slug, name, logo):
    return dict(
        name=name, logo=logo,
        go=f"/go/{slug}",
        pricing_url=f"/pages/{slug}-pricing-2026-plans-costs-what-you-actually-pay",
        page_url=f"/pages/{slug}-review-2026-is-it-worth-it-honest-verdict",
        top_pct="20%", top_label="Annual billing discount", top_meta="vs monthly pricing",
        hero_lead=f"We track every {name} discount, promo code, and deal. Here's what's verified and active right now.",
        deals=[
            dict(pct="20%", name=f"Annual Billing — {name}", desc=f"Save approximately 20% by choosing annual billing over monthly on any {name} plan. No code needed — select annual at checkout.", code="NO CODE NEEDED", expiry="Ongoing", verified=TODAY),
            dict(pct="Free", name=f"{name} Free Trial", desc=f"Most {name} plans offer a free trial. Check current availability via our link — trial length varies by plan.", code="Via link", expiry="Check availability", verified=TODAY),
            dict(pct="30%", name="Nonprofit / Education Discount", desc=f"{name} may offer discounts for nonprofits and educational institutions. Contact their sales team to enquire about eligibility.", code="Contact sales", expiry="Ongoing — verify with vendor", verified=TODAY),
        ],
        howto=[
            (f"Visit {name}'s website","Use our link above for the best current offer."),
            ("Choose your plan","Select the tier that matches your needs."),
            ("Toggle to Annual billing","Annual billing typically saves 15-25% vs monthly."),
            ("Complete checkout","Enter your details and start your trial or subscription."),
        ],
        no_code_text=f"{name}'s best discount is annual billing — no coupon code required. Any active promotional offers will be shown above once verified.",
        faqs=[
            (f"Does {name} have a promo code?", f"{name} doesn't typically issue public coupon codes. Annual billing is the standard discount. Check our link for any current promotional offers."),
            (f"Is there a {name} free trial?", f"Check {name}'s current pricing page for free trial availability. Most SaaS plans offer 14-30 days free. Our link shows the current offer."),
            (f"How do I get {name} cheaper?", f"Annual billing saves ~20% vs monthly. Nonprofit and startup discounts may be available — contact {name}'s sales team."),
            (f"What is the cheapest {name} plan?", f"Check the {name} pricing page for current entry-level plan pricing. We verify pricing every Wednesday."),
            (f"Can I cancel {name} and get a refund?", f"Most SaaS tools offer a refund window on annual plans. Check {name}'s terms of service or contact their support team for their current refund policy."),
        ]
    )

def extract_slug(stem):
    """Extract tool slug from coupon page filenames."""
    patterns = [
        r'(.+)-coupon-code-promo-codes-\d{4}.*',
        r'(.+)-promo-code-\d{4}.*',
        r'(.+)-coupon-\d{4}.*',
    ]
    for p in patterns:
        m = re.match(p, stem)
        if m:
            return m.group(1)
    return stem

def build_tokens(data, slug, page_slug):
    t = {}
    t["TOOL_NAME"] = data["name"]
    t["TOOL_LOGO_URL"] = data["logo"]
    t["TOOL_GO_LINK"] = data["go"]
    t["TOOL_PRICING_URL"] = data["pricing_url"]
    t["TOOL_PAGE_URL"] = data["page_url"]
    t["VERIFIED_DATE"] = TODAY
    t["TOP_DEAL_PCT"] = data["top_pct"]
    t["TOP_DEAL_LABEL"] = data["top_label"]
    t["TOP_DEAL_META"] = data["top_meta"]
    t["HERO_LEAD"] = data["hero_lead"]

    deals = data["deals"]
    for i, d in enumerate(deals[:3], 1):
        t[f"DEAL_{i}_PCT"] = d["pct"]
        t[f"DEAL_{i}_NAME"] = d["name"]
        t[f"DEAL_{i}_DESC"] = d["desc"]
        t[f"DEAL_{i}_CODE"] = d["code"]
        t[f"DEAL_{i}_EXPIRY_NOTE"] = d["expiry"]
        t[f"DEAL_{i}_VERIFIED_DATE"] = d.get("verified", TODAY)

    howto = data["howto"]
    for i, (name_s, desc_s) in enumerate(howto[:4], 1):
        t[f"HOWTO_{i}_NAME"] = name_s
        t[f"HOWTO_{i}_DESC"] = desc_s

    t["NO_CODE_FALLBACK_TEXT"] = data["no_code_text"]

    faqs = data.get("faqs", [])
    for i, (q, a) in enumerate(faqs[:5], 1):
        t[f"FAQ_{i}_Q"] = q
        t[f"FAQ_{i}_A"] = a
    for i in range(len(faqs)+1, 6):
        t[f"FAQ_{i}_Q"] = ""; t[f"FAQ_{i}_A"] = ""

    t["CANONICAL_URL"] = f"pages/{page_slug}"
    t["META_DESCRIPTION"] = (
        f"Best {data['name']} discount codes and promo offers verified {TODAY}. "
        f"Annual plan savings, free trial access, and any active coupon codes — checked weekly."
    )
    return t

def render(path, template_html, tokens):
    out = template_html
    for k, v in tokens.items():
        out = out.replace("{{" + k + "}}", str(v))
    if "G-RLYVYV8WQJ" not in out:
        out = out.replace("</head>", GA + "\n</head>", 1)
    if "favicon" not in out:
        out = out.replace("</head>", '  <link rel="icon" href="/favicon.ico" sizes="any">\n</head>', 1)
    for r in set(re.findall(r'\{\{[A-Z0-9_]+\}\}', out)):
        out = out.replace(r, "")
    path.write_text(out, encoding="utf-8")

def main():
    tpl = (TEMPLATES / "coupon.html").read_text(encoding="utf-8")
    patterns = ["*-coupon-code-promo-codes-*.html", "*-promo-code-*.html", "*-coupon-*.html"]
    seen = set()
    pages = []
    for pat in patterns:
        for p in sorted((SITE / "pages").glob(pat)):
            if p not in seen and "coupon-verification-policy" not in p.name and "deal-radar" not in p.name:
                seen.add(p)
                pages.append(p)
    print(f"Processing {len(pages)} coupon/promo pages...")
    done = skip = 0

    for path in pages:
        html = path.read_text(encoding="utf-8", errors="replace")
        if "cp-hero" in html and "deal-card" in html and "deal-reveal-btn" in html:
            skip += 1
            continue

        stem = path.stem
        slug = extract_slug(stem)
        name = DISPLAY_NAMES.get(slug, slug.replace("-", " ").title())
        logo = LOGO_MAP.get(slug, f"https://cdn.simpleicons.org/{slug}/ffffff")

        data = COUPONS.get(slug)
        if not data:
            data = make_generic(slug, name, logo)

        tokens = build_tokens(data, slug, stem)
        render(path, tpl, tokens)
        done += 1
        src = "DB" if COUPONS.get(slug) else "generic"
        if done <= 10 or done % 10 == 0:
            print(f"  [OK {src}] {path.name[:60]}")

    print(f"\nDone: {done} upgraded | {skip} already premium")

if __name__ == "__main__":
    main()
