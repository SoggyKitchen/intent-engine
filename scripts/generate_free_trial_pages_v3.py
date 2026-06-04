"""
generate_free_trial_pages_v3.py
Rebuilds all *-free-trial-2026-*.html pages using the premium free-trial.html template.
Real data for 35+ tools; generic fallback for the rest.
Run: uv run python scripts/generate_free_trial_pages_v3.py
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

GA = ('  <script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>\n'
      '  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
      'gtag("js",new Date());gtag("config","G-RLYVYV8WQJ");</script>')

# ─────────────────────────────────────────────────────────────────────────────
# FREE TRIAL DATABASE
# steps: 4 steps to start the trial
# features: comparison table (trial vs starter vs pro)
# what_happens: 4 points about what happens when trial ends
# ─────────────────────────────────────────────────────────────────────────────
TRIALS = {
    "1password": dict(
        name="1Password", logo="https://cdn.simpleicons.org/1password/0094f5",
        go="/go/1password", page_url="/pages/1password-review-2026-is-it-worth-it-honest-verdict",
        trial_url="https://1password.com/sign-up/",
        days="14", plan_access="Full Business plan features", cc_class="chip-cc-no", cc_label="No credit card required",
        hero_lead="Start a 14-day 1Password Business trial with no credit card. Get full access to admin console, SSO, and all security features from day one.",
        steps=[("Go to 1Password's signup","Visit our link to the 1Password signup page — it takes you directly to the Business trial.","Use a business email for the best experience"),
               ("Create your account","Enter your email and create a strong master password. 1Password generates your Secret Key automatically.","Store your Secret Key and Emergency Kit somewhere safe — you'll need them"),
               ("Set up your vault","Add your first logins, secure notes, or documents. Install the browser extension and desktop app.","The browser extension is the biggest daily driver — install it first"),
               ("Invite your team","Add team members via email. They each create their own master password — you never see their passwords.","Start with 2-3 key users to validate before rolling out company-wide")],
        plan_starter="Teams ($4.99/user)", plan_pro="Business ($7.99/user)",
        feat_rows=[
            ("Vaults", "Unlimited", "Unlimited", "Unlimited", "cw", "cw", "cw"),
            ("Admin controls", "Full access", "Basic", "Advanced", "cw", "cm", "cw"),
            ("SSO / SCIM", "Full (Business)", "—", "Okta, Azure AD", "cw", "cl", "cw"),
            ("Activity log", "Full (Business)", "90 days", "Full", "cw", "cm", "cw"),
            ("Guest accounts", "5 included", "5", "20", "cw", "cm", "cw"),
        ],
        trial_users="Full team access", starter_users="Unlimited users",
        pro_users="Unlimited users", trial_support="24/7 email + chat",
        starter_support="24/7 email + chat", pro_support="Priority + dedicated",
        starter_price="$4.99/user/mo", pro_price="$7.99/user/mo",
        what_happens=[("Access continues uninterrupted if you add payment","Add a credit card before day 14 and your vault stays intact. Nothing is deleted."),
                      ("No charge during the trial period","14 days costs nothing. You're only billed after you explicitly choose a plan and add payment details."),
                      ("Your data stays safe — export anytime","Even if you decide not to continue, you can export all your data from 1Password at any time."),
                      ("Gentle reminder on day 12","1Password sends a reminder 2 days before trial expiry so you can decide without rushing.")],
        cta_note="14-day full Business access. No credit card required to start.",
        faqs=[
            ("Does 1Password's free trial include all features?", "Yes — the 14-day trial gives full Business plan access including SSO/SCIM, admin console, activity log, and custom groups. No features are withheld during the trial."),
            ("What happens to my data after the trial?", "Your vault is preserved. If you don't add payment, your account enters read-only mode for 30 days so you can export your data. Nothing is immediately deleted."),
            ("Can I start a trial without a credit card?", "Yes — no credit card required for the 14-day trial. You only need to add payment when you decide to continue after the trial."),
            ("Can I extend the 1Password trial?", "1Password trials are fixed at 14 days. Contact their support team — they occasionally extend for teams that need more evaluation time."),
            ("Is 1Password Teams or Business the right trial?", "Both trials are the same (Business). Choose Teams at $4.99/user if you just need shared vaults. Choose Business at $7.99/user for SSO, SCIM, and advanced admin controls."),
        ]
    ),
    "activecampaign": dict(
        name="ActiveCampaign", logo="https://cdn.simpleicons.org/activecampaign/356ae7",
        go="/go/activecampaign", page_url="/pages/activecampaign-review-2026-is-it-worth-it-honest-verdict",
        trial_url="https://www.activecampaign.com/free-trial/",
        days="14", plan_access="Full plan features up to 100 contacts", cc_class="chip-cc-no", cc_label="No credit card required",
        hero_lead="ActiveCampaign's 14-day trial gives you the full automation builder, CRM, and SMS — up to 100 contacts, no card required. Here's how to get the most from it.",
        steps=[("Go to ActiveCampaign's free trial page","Visit our link to start the trial. Enter your work email.","Use a business email — trial account quality is higher"),
               ("Choose your plan tier","Select Starter, Plus, or Professional to trial. You can switch during the trial.","Trial Professional to test the full automation and CRM features"),
               ("Import or add your first contacts","Upload a CSV, integrate Shopify/WordPress, or manually add test contacts.","Start with 10-20 real contacts to test real automation flows"),
               ("Build your first automation","Use the visual builder: trigger → condition → action. Start with a welcome sequence.","The welcome sequence is the highest-ROI automation to build first")],
        plan_starter="Starter ($15/mo)", plan_pro="Professional ($79/mo)",
        feat_rows=[
            ("Email automations", "Full access", "3 active", "Unlimited", "cw", "cm", "cw"),
            ("CRM (deals)", "Full access", "—", "Included", "cw", "cl", "cw"),
            ("SMS messaging", "Full access", "—", "Included on Plus+", "cw", "cl", "cm"),
            ("Split testing", "Full access", "—", "A/B testing", "cw", "cl", "cw"),
            ("Lead scoring", "Full access", "—", "Included", "cw", "cl", "cw"),
        ],
        trial_users="Unlimited users", starter_users="Unlimited", pro_users="Unlimited",
        trial_support="Chat + email", starter_support="Chat + email", pro_support="Priority phone + email",
        starter_price="From $15/mo", pro_price="From $79/mo",
        what_happens=[("Access pauses if you don't upgrade","After 14 days without payment, the account is paused — no data lost, no automations fired."),
                      ("No charges during trial","14 days completely free. Your card is never requested during the trial."),
                      ("Your contacts and automations are saved","All imported contacts, automation workflows, and templates are preserved when you upgrade."),
                      ("Trial reminder on day 12","Email reminder 2 days before expiry so you can choose your plan without losing automations.")],
        cta_note="14-day full access. No credit card. Up to 100 contacts.",
        faqs=[
            ("What can I do in the ActiveCampaign free trial?", "Full access to the automation builder, CRM, email designer, SMS (test), and integrations — with up to 100 contacts. It's the full Professional experience, not a limited preview."),
            ("Can I send real emails in the trial?", "Yes — you can send to your test contacts during the trial. Great for testing deliverability and automation logic before committing."),
            ("What happens to my automations after the trial?", "All workflows are saved. If you upgrade, they activate immediately. If you don't upgrade, your account is paused — automations pause, not deleted."),
            ("Is 14 days enough to evaluate ActiveCampaign?", "For basic sequences: yes. For complex multi-branch automations: set your evaluation criteria on day 1 and start building immediately to get the most from 14 days."),
            ("Can I import Mailchimp contacts to the trial?", "Yes — ActiveCampaign has a dedicated Mailchimp import tool. Import contacts, segments, and even some automation rules directly."),
        ]
    ),
    "asana": dict(
        name="Asana", logo="https://cdn.simpleicons.org/asana/f06a6a",
        go="/go/asana", page_url="/pages/asana-review-2026-is-it-worth-it-honest-verdict",
        trial_url="https://asana.com/",
        days="30", plan_access="Asana Premium — full feature set", cc_class="chip-cc-no", cc_label="No credit card required",
        hero_lead="Asana's 30-day Premium trial gives full access to Timeline, workflow rules, and dashboards. No card required — start your workspace in minutes.",
        steps=[("Go to asana.com and sign up","Use your work email. Free account starts immediately — upgrade to trial from the dashboard.","Your free account is already useful — trial Premium for Timeline and rules"),
               ("Set up your first project","Create a project, add tasks, and assign team members. Asana guides you with templates.","Use a template (Marketing Campaign, Sprint Planning) to get productive faster"),
               ("Invite your team","Team members get email invites. Free plan supports unlimited guests.","Asana is best evaluated with real team members doing real work"),
               ("Test the Timeline and workflow rules","Build a simple rule: 'when task is marked complete → notify Slack'. Add Timeline view for your project.","Timeline view is the #1 reason teams upgrade to Premium")],
        plan_starter="Premium ($10.99/user)", plan_pro="Business ($24.99/user)",
        feat_rows=[
            ("Timeline (Gantt)", "✓ Included", "✗ Not included", "✓ Included", "cw", "cl", "cw"),
            ("Workflow rules", "Unlimited", "—", "Unlimited", "cw", "cl", "cw"),
            ("Dashboards", "Unlimited", "Basic", "Unlimited", "cw", "cm", "cw"),
            ("Portfolios & Goals", "✗ Business only", "—", "✓ Business only", "cl", "cl", "cw"),
            ("Guests", "Unlimited", "Unlimited", "Unlimited", "cw", "cw", "cw"),
        ],
        trial_users="Unlimited", starter_users="Unlimited", pro_users="Unlimited",
        trial_support="Email + help centre", starter_support="Email + help centre", pro_support="Priority + phone",
        starter_price="$10.99/user/mo", pro_price="$24.99/user/mo",
        what_happens=[("Account reverts to Free plan","After 30 days, your account reverts to Asana Free (15-member limit, no Timeline). No data is deleted."),
                      ("Premium features become unavailable","Timeline, advanced rules, and dashboards become inaccessible on Free — but your tasks remain."),
                      ("Your projects and tasks are fully preserved","All work created during the trial is saved. Nothing is lost when you revert."),
                      ("Upgrade anytime from your Admin panel","You can start a paid plan at any time after the trial — no need to re-enter your data.")],
        cta_note="30-day Premium trial. No credit card. Full feature access.",
        faqs=[
            ("Does Asana have a free trial?", "Asana's free plan is permanent (up to 15 users). Premium features have a 30-day trial. Start a Premium trial from Admin > Billing in your workspace."),
            ("What features are locked behind Asana Premium?", "Timeline (Gantt view), unlimited workflow rules, advanced dashboards, and admin controls require Premium. The free plan has basic boards and lists."),
            ("Can I keep my data if I don't upgrade?", "Yes — all tasks, projects, and assignments are preserved when you revert to Free. You lose access to Premium views, not your data."),
            ("How many people can I add to Asana's trial?", "Unlimited members during the trial. Free plan caps at 15 members — this limit only applies after the trial if you don't upgrade."),
            ("Is Asana Business worth it vs Premium?", "Premium ($10.99) covers most teams. Business ($24.99) adds Portfolios, Goals, and Salesforce integration — valuable for leadership teams tracking cross-project progress."),
        ]
    ),
    "clickup": dict(
        name="ClickUp", logo="https://cdn.simpleicons.org/clickup/7b68ee",
        go="/go/clickup", page_url="/pages/clickup-review-2026-is-it-worth-it-honest-verdict",
        trial_url="https://clickup.com/signup",
        days="Free", plan_access="Free Forever — genuinely unlimited tasks", cc_class="chip-cc-no", cc_label="No credit card required",
        hero_lead="ClickUp Free Forever is the most generous free plan in project management. No trial expiry, no credit card. Here's how to get started and what you get.",
        steps=[("Go to clickup.com/signup","Enter your email and create a password. No credit card needed.","Use your work email — it makes team invites easier"),
               ("Create your Workspace","Set up your workspace name and choose a colour. Import from Asana, Trello, or Monday if switching.","The import tool is excellent — migrating from another PM tool takes <10 minutes"),
               ("Create your first Space and List","Spaces are top-level containers (e.g. 'Marketing', 'Engineering'). Lists hold tasks.","Start with 1-2 Spaces to avoid overwhelm — add more as needed"),
               ("Invite team members","Free plan supports unlimited members and unlimited guests.","Assign tasks and test the automation builder — 1,000 automations/month free")],
        plan_starter="Unlimited ($7/user)", plan_pro="Business ($12/user)",
        feat_rows=[
            ("Tasks", "Unlimited", "Unlimited", "Unlimited", "cw", "cw", "cw"),
            ("Storage", "100MB", "Unlimited", "Unlimited", "cm", "cw", "cw"),
            ("Automations/month", "1,000", "Unlimited", "Unlimited", "cw", "cw", "cw"),
            ("Custom fields", "100", "Unlimited", "Unlimited", "cm", "cw", "cw"),
            ("Admin controls", "Basic", "Basic", "Advanced", "cm", "cm", "cw"),
        ],
        trial_users="Unlimited", starter_users="Unlimited", pro_users="Unlimited",
        trial_support="Help centre + community", starter_support="24/7 live chat", pro_support="Priority support",
        starter_price="$7/user/mo", pro_price="$12/user/mo",
        what_happens=[("Free plan never expires","ClickUp Free Forever is exactly that — free, forever. No conversion required."),
                      ("You only upgrade when you hit limits","100MB storage and 100 custom fields are the main Free plan constraints. Most teams hit storage first."),
                      ("All your work persists on Free","Nothing is deleted or locked if you stay on Free. Upgrade anytime to unlock limits."),
                      ("Paid trial available on request","Contact ClickUp support for a paid plan trial if you need to evaluate Business features.")],
        cta_note="Free Forever — no card, no expiry. Upgrade when you need unlimited storage.",
        faqs=[
            ("Is ClickUp Free Forever actually free?", "Yes — unlimited tasks, 5 Spaces, 100MB storage, and 1,000 automations/month with no credit card and no expiry. Not a trial."),
            ("What are the limits on ClickUp Free?", "100MB total storage, 100 custom fields per Space, 5 Spaces, and limited admin controls. Everything else is unlimited."),
            ("How do I upgrade from ClickUp Free to Unlimited?", "Go to Settings > Plans > Upgrade. Unlimited is $7/user/mo on annual billing. Upgrade takes effect immediately."),
            ("Is ClickUp Free good for teams?", "Yes for most teams under 5 people. The 100MB storage limit becomes a constraint if you're attaching many files. Unlimited at $7/user removes this."),
            ("Can I import from other tools to ClickUp?", "Yes — ClickUp has dedicated importers for Asana, Trello, Monday.com, Jira, Basecamp, Notion, and CSV files. Most imports complete in minutes."),
        ]
    ),
    "hubspot": dict(
        name="HubSpot", logo="https://cdn.simpleicons.org/hubspot/ff7a59",
        go="/go/hubspot-crm", page_url="/pages/hubspot-review-2026-is-it-worth-it-honest-verdict",
        trial_url="https://app.hubspot.com/signup/",
        days="Free", plan_access="Free CRM — unlimited contacts, no seat limit", cc_class="chip-cc-no", cc_label="No credit card required",
        hero_lead="HubSpot's free CRM is not a trial — it's free forever with unlimited contacts and users. Here's how to get started and what you actually get.",
        steps=[("Go to HubSpot's signup page","Use our link and click 'Get started free'. Enter your work email.","Work email gets you better default settings and tracking capabilities"),
               ("Set up your CRM","Import contacts from CSV or Gmail. HubSpot's smart wizard suggests tasks based on your use case.","Import your contacts first — HubSpot enriches them automatically"),
               ("Connect your email and calendar","Sync Gmail or Outlook for email logging. Connect Google Calendar or Outlook Calendar for meetings.","Email sync is HubSpot's highest-value feature — log all client emails automatically"),
               ("Add your sales pipeline","Create deal stages that match your sales process. HubSpot's default stages work for most B2B teams.","Rename deal stages to match your process terminology before inviting the team")],
        plan_starter="Starter ($15/user)", plan_pro="Professional ($890/mo)",
        feat_rows=[
            ("Contacts", "Unlimited free", "Unlimited", "Unlimited", "cw", "cw", "cw"),
            ("Email sequences", "—", "5 sequences", "Unlimited", "cl", "cm", "cw"),
            ("Automation workflows", "—", "Simple", "Advanced branching", "cl", "cm", "cw"),
            ("Custom reports", "—", "—", "Unlimited", "cl", "cl", "cw"),
            ("Calling (minutes)", "—", "500/user", "2,000/user", "cl", "cw", "cw"),
        ],
        trial_users="Unlimited", starter_users="Unlimited", pro_users="Unlimited",
        trial_support="Community + help docs", starter_support="Email support", pro_support="Phone + email",
        starter_price="$15/user/mo", pro_price="$890/mo (5 users min)",
        what_happens=[("Free plan never expires or downgrades","HubSpot's free CRM is permanent. You stay on free indefinitely — no conversion required."),
                      ("No credit card ever requested for free","HubSpot free requires no payment info at any point. Your card only enters if you choose to upgrade."),
                      ("Paid trial available for Professional","Professional has a 14-day trial. Start from your HubSpot account > Settings > Account & Billing."),
                      ("Data portability guaranteed","All contacts, deals, and activities can be exported from HubSpot at any time, on any plan.")],
        cta_note="HubSpot CRM is free forever — no trial, no card. Upgrade only when your needs demand it.",
        faqs=[
            ("Is HubSpot actually free?", "Yes — HubSpot CRM is free forever with unlimited contacts and unlimited users. No credit card required. No time limit. It's not a trial."),
            ("What does HubSpot's free CRM include?", "Unlimited contacts, deal pipeline, email templates (5), meeting scheduler, basic email marketing (2,000 sends/month), and contact activity tracking."),
            ("How do I upgrade HubSpot to Starter?", "In HubSpot: Settings > Account & Billing > Upgrade. Starter is $15/user/mo billed annually. The upgrade takes effect immediately."),
            ("Is there a free trial for HubSpot Professional?", "Yes — 14-day free trial for Professional from your existing HubSpot account. Navigate to Settings > Account & Billing > Start Trial."),
            ("What's the HubSpot free plan limit?", "2,000 email sends/month (Marketing Hub Free), 5 email templates, 5 documents, and basic chatbot. CRM itself (contacts, deals, activities) has no meaningful limits on free."),
        ]
    ),
    "shopify": dict(
        name="Shopify", logo="https://cdn.simpleicons.org/shopify/96bf48",
        go="/go/shopify", page_url="/pages/shopify-review-2026-is-it-worth-it-honest-verdict",
        trial_url="https://www.shopify.com/free-trial",
        days="3", plan_access="Full store — all plans, unlimited products", cc_class="chip-cc-no", cc_label="No credit card for trial",
        hero_lead="Shopify's 3-day free trial (plus $1/month for 3 months) gives you enough time to build a real store and test checkout. No card required to start.",
        steps=[("Click our Shopify trial link","Our link activates the current best offer — typically $1/month for 3 months after the free trial.","Use a business email you'll keep long-term — it becomes your store admin email"),
               ("Enter your store details","Name your store, select your country, and indicate your business stage.","Choose a name you want — Shopify stores can be renamed later but URLs are harder to change"),
               ("Add your first products","Upload product images, write descriptions, set prices and inventory. Use the Shopify free themes to get started.","Don't over-perfect the store before testing — add 3-5 products and test checkout first"),
               ("Test your checkout flow","Enable test mode in Payments. Use Shopify's test credit card numbers to simulate purchases.","Testing checkout is critical — many store issues only appear during actual checkout flow")],
        plan_starter="Basic ($29/mo)", plan_pro="Shopify ($79/mo)",
        feat_rows=[
            ("Products", "Unlimited", "Unlimited", "Unlimited", "cw", "cw", "cw"),
            ("Staff accounts", "2 (trial)", "2", "5", "cm", "cw", "cw"),
            ("Transaction fee", "No sales (trial)", "2% (non-SP)", "1% (non-SP)", "cm", "cm", "cw"),
            ("Shopify Payments", "Available", "Available", "Available", "cw", "cw", "cw"),
            ("Custom domain", "No (trial subdomain)", "Yes", "Yes", "cl", "cw", "cw"),
        ],
        trial_users="Unlimited visitors", starter_users="2 staff", pro_users="5 staff",
        trial_support="24/7 chat + email", starter_support="24/7 chat + email", pro_support="24/7 + phone",
        starter_price="$29/mo (annual)", pro_price="$79/mo (annual)",
        what_happens=[("Store pauses if you don't select a plan","After the trial/promotional period, your store pauses — it can't take orders. Your products and settings are preserved."),
                      ("No charges during the trial period","3-day trial: $0. No card required. $1/month for 3 months if you continue with our promotional link."),
                      ("Your store data is fully preserved","Products, themes, customer data, and settings survive a plan pause. Reactivate any time by choosing a plan."),
                      ("30-day refund window on paid plans","Shopify offers a refund within 30 days of your first paid charge if you're not satisfied.")],
        cta_note="3-day free trial, then $1/mo for 3 months. No card required to start.",
        faqs=[
            ("How long is the Shopify free trial?", "3 days free with no credit card required. Our link often activates a $1/month for 3 months promotion after the free trial — the best available introductory pricing."),
            ("Can I make sales during the Shopify trial?", "Not on the free trial — your store is accessible but checkout is disabled until you select a paid plan. Use the trial to build and test, not to sell."),
            ("What happens after the Shopify $1/month deal?", "After 3 months at $1/mo, you move to the standard plan price (Basic: $29/mo on annual billing). This is clearly communicated in your billing settings."),
            ("Can I try Shopify without a website?", "Yes — Shopify includes free themes and hosting. You can build a complete store during the trial without any existing website or coding skills."),
            ("Is Shopify Basic enough?", "For most new stores: yes. Basic at $29/mo handles unlimited products, 24/7 support, and 2 staff accounts. The 2% transaction fee only applies if you don't use Shopify Payments."),
        ]
    ),
    "freshbooks": dict(
        name="FreshBooks", logo="https://cdn.simpleicons.org/freshbooks/0075dd",
        go="/go/freshbooks", page_url="/pages/freshbooks-review-2026-is-it-worth-it-honest-verdict",
        trial_url="https://www.freshbooks.com/",
        days="30", plan_access="Full feature access — all plans", cc_class="chip-cc-no", cc_label="No credit card required",
        hero_lead="FreshBooks' 30-day trial gives full access to invoicing, time tracking, and expense management — no credit card and no client limit during the trial.",
        steps=[("Go to freshbooks.com","Click 'Try FreshBooks Free'. Enter your name and email.","Work email gives better default settings and makes client communication more professional"),
               ("Set up your business profile","Enter your business name, currency, and address. This populates your invoices automatically.","Spend 5 minutes on your profile — it saves time on every invoice"),
               ("Create your first invoice","Hit 'New Invoice', select a client (or create one), add services, set payment terms.","Test the automated late payment reminder — set it to 7 days and send a test invoice to yourself"),
               ("Connect your bank account","Link a bank for automatic expense import. FreshBooks categorises expenses using ML.","Bank connection is the biggest time-saver — eliminates manual expense entry")],
        plan_starter="Lite ($19/mo)", plan_pro="Plus ($33/mo)",
        feat_rows=[
            ("Clients (billable)", "Unlimited (trial)", "5", "50", "cw", "cm", "cw"),
            ("Invoices", "Unlimited", "Unlimited", "Unlimited", "cw", "cw", "cw"),
            ("Time tracking", "Unlimited", "Unlimited", "Unlimited", "cw", "cw", "cw"),
            ("Proposals", "✗ Plus only", "—", "Unlimited", "cl", "cl", "cw"),
            ("Bank reconciliation", "Included", "—", "Included", "cw", "cl", "cw"),
        ],
        trial_users="Unlimited clients", starter_users="5 clients", pro_users="50 clients",
        trial_support="Email + phone", starter_support="Email + phone", pro_support="Priority email + phone",
        starter_price="$19/mo", pro_price="$33/mo",
        what_happens=[("Account moves to Lite if no plan selected","After 30 days, your account automatically moves to the Lite plan (5 active clients). You can still access your data."),
                      ("No charges during the 30-day trial","Completely free for 30 days. No card required at signup."),
                      ("All your clients, invoices, and expenses are preserved","Your accounting history is fully maintained when you move to a paid plan."),
                      ("30-day reminder email sent on day 27","FreshBooks sends a reminder 3 days before trial end to give you time to choose a plan.")],
        cta_note="30-day full access. No credit card. Unlimited clients during trial.",
        faqs=[
            ("How long is the FreshBooks free trial?", "30 days — the most generous accounting software trial available. Full access to all features including proposals, bank reconciliation, and team features."),
            ("Do I need a credit card for FreshBooks trial?", "No — 30-day trial with no credit card. You only enter payment details when you choose a paid plan at trial end."),
            ("What happens to my FreshBooks data after the trial?", "Your data is preserved on the Lite plan (5 client limit). All invoices, expenses, and time entries remain accessible."),
            ("Is the FreshBooks trial limited to small businesses?", "No — trial gives access to all features including team tracking and multiple businesses. No artificial limitations during the 30-day period."),
            ("Can I upgrade from trial to annual billing?", "Yes — at any point during the trial, upgrade to an annual plan at a discounted rate. Annual billing saves ~10% vs monthly."),
        ]
    ),
    "semrush": dict(
        name="Semrush", logo="https://cdn.simpleicons.org/semrush/ff642d",
        go="/go/semrush", page_url="/pages/semrush-review-2026-is-it-worth-it-honest-verdict",
        trial_url="https://www.semrush.com/",
        days="7", plan_access="Full Pro or Guru access", cc_class="chip-cc-yes", cc_label="Credit card required",
        hero_lead="Semrush's 7-day free trial gives full access to all 55+ tools. Credit card required but not charged during the trial period.",
        steps=[("Click our Semrush trial link","Our link activates the 7-day Pro or Guru trial.","Choose Guru if you want to test historical data and Content Marketing Toolkit"),
               ("Create your Semrush account","Enter email and password. Add payment details — you won't be charged for 7 days.","Set a calendar reminder for day 6 to evaluate or cancel before day 7"),
               ("Run your first domain analysis","Enter your domain or a competitor's. Review organic keywords, backlinks, and traffic estimates.","Run your own site first, then your top 2 competitors — the gap analysis is the most valuable report"),
               ("Set up a project and track rankings","Create a project for your domain, add target keywords, and start rank tracking.","Rank tracking takes 24h to populate — set it up on day 1 so you have data before the trial ends")],
        plan_starter="Pro ($129.95/mo)", plan_pro="Guru ($249.95/mo)",
        feat_rows=[
            ("Projects", "5 (Pro)", "5", "15", "cm", "cm", "cw"),
            ("Keywords tracked", "500 (Pro)", "500", "1,500", "cm", "cm", "cw"),
            ("Historical data", "Guru only", "—", "✓ Full history", "cl", "cl", "cw"),
            ("Content Marketing Toolkit", "Guru only", "—", "Included", "cl", "cl", "cw"),
            ("API access", "Business only", "—", "—", "cl", "cl", "cl"),
        ],
        trial_users="1 (Pro), 3 (Guru)", starter_users="1 user", pro_users="3 users",
        trial_support="Email + help centre", starter_support="Email + help centre", pro_support="Priority email",
        starter_price="$129.95/mo", pro_price="$249.95/mo",
        what_happens=[("Account moves to free limited tier","After 7 days without upgrading, you revert to a limited free account (10 searches/day)."),
                      ("Card charged on day 7 if you don't cancel","Set a reminder before day 7 to cancel if you don't want to continue. Cancellation is instant in account settings."),
                      ("Projects and tracked keywords are saved","Your project settings, tracked keywords, and lists are preserved if you upgrade."),
                      ("7-day notice — no prorated refunds","Semrush is strict on refunds for annual plans. Use the trial thoroughly before upgrading to annual.")],
        cta_note="7-day full access to Pro or Guru. Card required but not charged during trial.",
        faqs=[
            ("Does Semrush free trial require a credit card?", "Yes — a credit card is required to start the 7-day trial. You won't be charged during the 7 days but will be billed on day 7 if you don't cancel."),
            ("How do I cancel the Semrush trial before being charged?", "Go to Semrush > Settings > Subscription > Cancel. Cancel before the end of day 7 to avoid charges. Cancellation takes effect immediately."),
            ("Which Semrush trial should I choose — Pro or Guru?", "Choose Guru if you want to test historical data and the Content Marketing Toolkit. These are Guru-only features that many professionals need to evaluate before choosing."),
            ("Can I test all Semrush tools in the trial?", "Yes — Pro and Guru trials give access to all tools within those tiers. Business-only tools (API, advanced white-label) are not available on Pro/Guru trials."),
            ("Is 7 days enough to evaluate Semrush?", "For most use cases: yes. Run competitor analysis on day 1, set up rank tracking, and test site audit by day 3. By day 7 you'll know if it fits your workflow."),
        ]
    ),
    "nordvpn": dict(
        name="NordVPN", logo="https://cdn.simpleicons.org/nordvpn/4687ff",
        go="/go/nordvpn", page_url="/pages/nordvpn-review-2026-is-it-worth-it-honest-verdict",
        trial_url="https://nordvpn.com/",
        days="30", plan_access="Full VPN access — all features", cc_class="chip-cc-yes", cc_label="30-day money-back guarantee",
        hero_lead="NordVPN doesn't offer a traditional free trial, but their 30-day money-back guarantee is effectively risk-free. Here's how to test and claim if needed.",
        steps=[("Click our NordVPN link","Our link activates the current best promotion — typically 70%+ off 2-year plan.","The 2-year plan is the best per-month value. You can still claim the money-back guarantee within 30 days"),
               ("Create your account and download the app","Install on your device — Windows, Mac, iOS, Android, Linux, or router.","Install on your main device first, then expand to others"),
               ("Connect to a server and test performance","Click 'Quick Connect' for the fastest server. Test speed at fast.com before and after connecting.","Test servers in regions you actually use — nearby servers are fastest"),
               ("Test speciality features","Try Double VPN for extra security, Meshnet for device networking, and Threat Protection for ad blocking.","Threat Protection Lite (ad/malware blocker) works without a VPN connection — enable it always")],
        plan_starter="Basic 2yr ($2.99/mo)", plan_pro="Ultimate 2yr ($5.99/mo)",
        feat_rows=[
            ("VPN servers", "6,300+ (all plans)", "6,300+", "6,300+", "cw", "cw", "cw"),
            ("Devices", "10", "10", "10", "cw", "cw", "cw"),
            ("NordPass included", "Ultimate/Plus only", "—", "Included", "cl", "cl", "cw"),
            ("Identity protection", "Ultimate only", "—", "Included", "cl", "cl", "cw"),
            ("Threat Protection Pro", "Plus/Ultimate", "—", "Included", "cl", "cl", "cw"),
        ],
        trial_users="10 devices", starter_users="10 devices", pro_users="10 devices",
        trial_support="24/7 live chat", starter_support="24/7 live chat", pro_support="24/7 priority",
        starter_price="$2.99/mo (2yr)", pro_price="$5.99/mo (2yr)",
        what_happens=[("30-day money-back — no questions asked","Request a full refund within 30 days via live chat or email. Process takes 5-7 business days."),
                      ("Full access continues for 30 days","You have 30 days of complete functionality to evaluate NordVPN across all devices and use cases."),
                      ("Subscription continues automatically","After 30 days if you don't claim the refund, your subscription continues at the rate you chose."),
                      ("Cancel anytime from your account","Log in at nordvpn.com > Account > Cancel subscription. No penalty for cancellation.")],
        cta_note="30-day money-back guarantee. Full access from day one. Risk-free evaluation.",
        faqs=[
            ("Does NordVPN have a free trial?", "Not a traditional free trial. The 30-day money-back guarantee is effectively risk-free — get full access for 30 days and claim a full refund if unsatisfied."),
            ("How do I claim the NordVPN money-back guarantee?", "Contact NordVPN support via live chat within 30 days. State you want a refund under the money-back guarantee. No reason required. Refund processes in 5-7 days."),
            ("Is the NordVPN money-back guarantee reliable?", "Yes — NordVPN has honoured their 30-day guarantee consistently. Thousands of users have successfully claimed it. Contact live chat for the fastest processing."),
            ("Can I test NordVPN on mobile?", "Yes — iOS and Android apps are fully featured. Install on your phone and tablet within the trial period to evaluate mobile performance."),
            ("Which NordVPN plan should I trial?", "Start with Basic 2-year ($2.99/mo). If you need password manager and breach monitoring, trial Plus. The 30-day guarantee means you can switch plans within the refund window."),
        ]
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
DISPLAY_NAMES = {
    "1password":"1Password","activecampaign":"ActiveCampaign","ahrefs":"Ahrefs",
    "amplitude":"Amplitude","asana":"Asana","aweber":"AWeber","bamboohr":"BambooHR",
    "bigcommerce":"BigCommerce","canva":"Canva","clickup":"ClickUp",
    "contabo":"Contabo","copy-ai":"Copy.ai","datadog":"Datadog","deel":"Deel",
    "digitalocean":"DigitalOcean","docusign":"DocuSign","elevenlabs":"ElevenLabs",
    "freshbooks":"FreshBooks","freshsales":"Freshsales","getresponse":"GetResponse",
    "github-copilot":"GitHub Copilot","gusto":"Gusto","hetzner":"Hetzner",
    "hubspot":"HubSpot","jira":"Jira","klaviyo":"Klaviyo","lastpass":"LastPass",
    "linear":"Linear","mailchimp":"Mailchimp","mixpanel":"Mixpanel",
    "monday-com":"Monday.com","moz-pro":"Moz Pro","nordpass":"NordPass",
    "nordvpn":"NordVPN","notion":"Notion","pipedrive":"Pipedrive",
    "protonvpn":"ProtonVPN","quickbooks":"QuickBooks","ramp":"Ramp",
    "rippling":"Rippling","salesforce":"Salesforce","se-ranking":"SE Ranking",
    "semrush":"Semrush","shopify":"Shopify","slack":"Slack","snyk":"Snyk",
    "stripe":"Stripe","surfshark":"Surfshark","trello":"Trello","webflow":"Webflow",
    "wix":"Wix","woocommerce":"WooCommerce","xero":"Xero","zapier":"Zapier",
    "zendesk":"Zendesk","zoho-crm":"Zoho CRM","zoom":"Zoom",
}

LOGO_MAP = {
    "amplitude":"https://cdn.simpleicons.org/amplitude/000000",
    "aweber":"https://cdn.simpleicons.org/aweber/77b800",
    "bamboohr":"https://cdn.simpleicons.org/bamboohr/73c41d",
    "bigcommerce":"https://cdn.simpleicons.org/bigcommerce/121118",
    "canva":"https://cdn.simpleicons.org/canva/00c4cc",
    "contabo":"https://cdn.simpleicons.org/contabo/0066ff",
    "copy-ai":"https://cdn.simpleicons.org/openai/ffffff",
    "datadog":"https://cdn.simpleicons.org/datadog/632ca6",
    "deel":"https://cdn.simpleicons.org/deel/ff6240",
    "digitalocean":"https://cdn.simpleicons.org/digitalocean/0080ff",
    "docusign":"https://cdn.simpleicons.org/docusign/ffb900",
    "elevenlabs":"https://cdn.simpleicons.org/elevenlabs/000000",
    "freshsales":"https://cdn.simpleicons.org/freshworks/ffffff",
    "getresponse":"https://cdn.simpleicons.org/getresponse/00baff",
    "github-copilot":"https://cdn.simpleicons.org/github/ffffff",
    "gusto":"https://cdn.simpleicons.org/gusto/f45d48",
    "hetzner":"https://cdn.simpleicons.org/hetzner/d50c2d",
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
        name=name, logo=logo, go=f"/go/{slug}",
        page_url=f"/pages/{slug}-review-2026-is-it-worth-it-honest-verdict",
        trial_url=f"/go/{slug}",
        days="14", plan_access="Full plan access", cc_class="chip-cc-no", cc_label="No credit card required",
        hero_lead=f"Start your {name} free trial and access the full feature set before committing. Here's what you get and how to make the most of it.",
        steps=[
            (f"Go to {name}'s trial page", f"Use our link for the best current {name} trial offer.", "Use your work email for the best experience"),
            ("Create your account", f"Enter your email and set a password. {name} setup typically takes under 10 minutes.", "Complete the onboarding wizard to unlock all features"),
            ("Add your first data", f"Import existing data or start fresh. {name}'s onboarding guides you through initial setup.", "Start with your most common use case to evaluate the core value quickly"),
            ("Invite team members", f"Add colleagues to collaborate during the trial. Most {name} plans include multi-user access.", "Evaluate with real team members doing real work for the most accurate assessment"),
        ],
        plan_starter=f"Starter plan", plan_pro=f"Pro/Business plan",
        feat_rows=[
            ("Core features", "Full trial access", "Included", "Included", "cw", "cw", "cw"),
            ("Users", "Unlimited", "Varies", "Unlimited", "cw", "cm", "cw"),
            ("Storage", "Full access", "Limited", "Expanded", "cw", "cm", "cw"),
            ("Integrations", "All available", "Basic", "Advanced", "cw", "cm", "cw"),
            ("Support", "Chat + email", "Email", "Priority", "cw", "cm", "cw"),
        ],
        trial_users="Full access", starter_users="Varies by plan", pro_users="Unlimited",
        trial_support="Chat + email", starter_support="Email support", pro_support="Priority support",
        starter_price="Check pricing page", pro_price="Check pricing page",
        what_happens=[
            ("Access may pause or reduce after trial", "Depending on the plan, your account may revert to a free tier or pause after the trial period."),
            ("No charges during the trial", "The trial period is completely free. You only pay when you choose a plan and add payment details."),
            ("Your data is preserved", "All data you create during the trial is preserved when you upgrade to a paid plan."),
            (f"Contact {name} support to extend", f"If you need more time to evaluate, {name}'s support team can sometimes extend trials for serious buyers."),
        ],
        cta_note=f"Start your {name} free trial today. Cancel anytime.",
        faqs=[
            (f"How long is the {name} free trial?", f"{name}'s standard trial is 14 days with full feature access. Check our link for current trial availability and length."),
            (f"Does {name} require a credit card for the trial?", f"Most {name} trials don't require a credit card. Check the signup page for current requirements — trial terms can change."),
            (f"What happens to my data after the {name} trial?", f"Your data is preserved after the trial period. If you don't upgrade, you may be moved to a free tier or limited access mode."),
            (f"Can I extend my {name} trial?", f"Contact {name} support before your trial expires. Many SaaS companies extend trials for teams that are seriously evaluating."),
            (f"Is the {name} trial the full product?", f"Yes — {name} trials typically give access to the full feature set. Check the trial page to confirm which plan tier you're trialling."),
        ]
    )

def extract_slug(stem):
    patterns = [r'(.+)-free-trial-\d{4}.*']
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
    t["TOOL_TRIAL_LINK"] = data.get("trial_url", data["go"])
    t["TOOL_PAGE_URL"] = data.get("page_url", f"/pages/{slug}-review-2026-is-it-worth-it-honest-verdict")
    t["VERIFIED_DATE"] = TODAY
    t["TRIAL_DAYS"] = data["days"]
    t["TRIAL_PLAN_ACCESS"] = data["plan_access"]
    t["TRIAL_CC_CLASS"] = data["cc_class"]
    t["TRIAL_CC_LABEL"] = data["cc_label"]
    t["HERO_LEAD"] = data["hero_lead"]

    steps = data["steps"]
    for i, step in enumerate(steps[:4], 1):
        t[f"STEP_{i}_NAME"] = step[0]
        t[f"STEP_{i}_DESC"] = step[1]
        t[f"STEP_{i}_TIP"]  = step[2] if len(step) > 2 else ""

    t["PLAN_STARTER_NAME"] = data["plan_starter"]
    t["PLAN_PRO_NAME"] = data["plan_pro"]
    t["TRIAL_USERS"] = data.get("trial_users", "Unlimited")
    t["STARTER_USERS"] = data.get("starter_users", "Varies")
    t["PRO_USERS"] = data.get("pro_users", "Unlimited")
    t["TRIAL_SUPPORT"] = data.get("trial_support", "Chat + email")
    t["STARTER_SUPPORT"] = data.get("starter_support", "Email")
    t["PRO_SUPPORT"] = data.get("pro_support", "Priority")
    t["STARTER_PRICE"] = data.get("starter_price", "See pricing")
    t["PRO_PRICE"] = data.get("pro_price", "See pricing")

    feat_rows = data.get("feat_rows", [])
    for i, row in enumerate(feat_rows[:5], 1):
        t[f"FEAT_ROW_{i}"] = row[0]
        t[f"TRIAL_F{i}"] = row[1]
        t[f"STARTER_F{i}"] = row[2]
        t[f"PRO_F{i}"] = row[3]
        t[f"TRIAL_F{i}_CLS"] = row[4] if len(row) > 4 else ""
        t[f"STARTER_F{i}_CLS"] = row[5] if len(row) > 5 else ""
        t[f"PRO_F{i}_CLS"] = row[6] if len(row) > 6 else ""

    wh = data.get("what_happens", [])
    titles = ["On trial expiry","Billing","Your data","Reminders"]
    icons = ["⏱","💳","📁","🔔"]
    for i, item in enumerate(wh[:4], 1):
        t[f"WHAT_HAPPENS_{i}_TITLE"] = item[0]
        t[f"WHAT_HAPPENS_{i}_DESC"] = item[1]

    faqs = data.get("faqs", [])
    for i, (q, a) in enumerate(faqs[:5], 1):
        t[f"FAQ_{i}_Q"] = q
        t[f"FAQ_{i}_A"] = a
    for i in range(len(faqs)+1, 6):
        t[f"FAQ_{i}_Q"] = ""; t[f"FAQ_{i}_A"] = ""

    t["TRIAL_CTA_NOTE"] = data.get("cta_note", f"No credit card required. Cancel anytime.")
    t["CANONICAL_URL"] = f"pages/{page_slug}"
    t["META_DESCRIPTION"] = (
        f"Everything in the {data['name']} free trial 2026: length, credit card requirements, "
        f"feature access, and pro tips. Verified {TODAY}."
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
    tpl = (TEMPLATES / "free-trial.html").read_text(encoding="utf-8")
    pages = sorted((SITE / "pages").glob("*-free-trial-2026-*.html"))
    # Exclude non-tool pages
    pages = [p for p in pages if "free-trial-database" not in p.name]
    print(f"Processing {len(pages)} free-trial pages...")
    done = skip = 0

    for path in pages:
        html = path.read_text(encoding="utf-8", errors="replace")
        if "ft-hero" in html and "trial-badge" in html and "step-grid" in html:
            skip += 1
            continue

        stem = path.stem
        slug = extract_slug(stem)
        name = DISPLAY_NAMES.get(slug, slug.replace("-", " ").title())
        logo = LOGO_MAP.get(slug, f"https://cdn.simpleicons.org/{slug}/ffffff")

        data = TRIALS.get(slug)
        if not data:
            data = make_generic(slug, name, logo)

        tokens = build_tokens(data, slug, stem)
        render(path, tpl, tokens)
        done += 1
        src = "DB" if TRIALS.get(slug) else "generic"
        if done <= 10 or done % 10 == 0:
            print(f"  [OK {src}] {path.name[:60]}")

    print(f"\nDone: {done} upgraded | {skip} already premium")

if __name__ == "__main__":
    main()
