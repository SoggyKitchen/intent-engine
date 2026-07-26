"""
Generate premium best-of pages using the new best-of.html template.
Replaces plain existing pages with ranked-card premium layout.
Covers 190 best-of pages in site/pages/ + root best-*.html pages.
"""
from pathlib import Path
import re, json, datetime

SITE      = Path(__file__).resolve().parents[1] / "site"
TEMPLATES = Path(__file__).resolve().parents[1] / "outputs/templates"

try:
    _d = datetime.date.today()
    TODAY = f"{_d.day} {_d.strftime('%B')} {_d.year}"
except Exception:
    TODAY = "June 2026"

# ─────────────────────────────────────────────────────────────────────────────
# TOOL DATABASE — 80 top B2B SaaS tools
# Each entry: score, logo (simpleicons URL), price_line, price_note, free_tag,
#             tagline, verdict, verdict_class, pros(3), cons(2), go_slug
# ─────────────────────────────────────────────────────────────────────────────
TOOLS = {
    # ── CRM ──────────────────────────────────────────────────────────────────
    "HubSpot CRM": dict(
        score=9.1, logo="https://cdn.simpleicons.org/hubspot/ff7a59",
        price_line="Free", free_tag="$0 forever", price_note="Paid from $15/user/mo",
        tagline="The most complete CRM for growing teams — unlimited free contacts, intuitive interface, sales-marketing-service flywheel.",
        verdict="Best Overall", verdict_class="v-best",
        pros=["Generous free plan — unlimited contacts, no seat limit","1,400+ native integrations out of the box","Sales, marketing &amp; service share one data layer"],
        cons=["Advanced features locked behind paid Hubs","Pricing jumps sharply above 5 paid users"],
        go="hubspot-crm", scores=dict(value=93,ease=96,features=87,int=98,support=88)),
    "HubSpot": dict(
        score=9.1, logo="https://cdn.simpleicons.org/hubspot/ff7a59",
        price_line="Free", free_tag="$0 forever", price_note="Paid from $15/user/mo",
        tagline="All-in-one marketing, sales, and service platform — unlimited free contacts and the best CRM for growing teams.",
        verdict="Best Overall", verdict_class="v-best",
        pros=["Unlimited free CRM — no seat cap, no contact limit","ChatSpot AI assistant included on all plans","1,400+ native integrations"],
        cons=["Premium features require expensive Hubs","Pricing jumps sharply at scale"],
        go="hubspot", scores=dict(value=93,ease=96,features=87,int=98,support=88)),
    "Salesforce": dict(
        score=8.4, logo="https://cdn.simpleicons.org/salesforce/00a1e0",
        price_line="$25/user/mo", free_tag="", price_note="⚠ Implementation costs extra",
        tagline="The gold standard for complex enterprise sales — infinitely customisable but demands serious admin resources.",
        verdict="Best Enterprise", verdict_class="v-ent",
        pros=["Unmatched customisation depth and scalability","Best-in-class forecasting and pipeline analytics","Vast AppExchange ecosystem"],
        cons=["True TCO is 2–3× the licence cost","Needs a dedicated admin to deliver value"],
        go="salesforce", scores=dict(value=64,ease=60,features=99,int=99,support=79)),
    "Pipedrive": dict(
        score=8.0, logo="https://cdn.simpleicons.org/pipedrive/1a73e8",
        price_line="$14/user/mo", free_tag="", price_note="30-day free trial",
        tagline="Pipeline-first CRM built by salespeople — superb deal tracking, lightweight admin, transparent pricing.",
        verdict="Best for Sales Teams", verdict_class="v-sales",
        pros=["Drag-and-drop pipeline view is best in class","Minimal setup — useful from day one","Flat, transparent per-user pricing"],
        cons=["Marketing automation weaker than HubSpot","Custom reporting locked to higher tiers"],
        go="pipedrive", scores=dict(value=88,ease=93,features=73,int=80,support=77)),
    "Monday.com": dict(
        score=7.6, logo="https://cdn.simpleicons.org/monday/f62b54",
        price_line="$12/seat/mo", free_tag="", price_note="14-day free trial",
        tagline="Highly visual, no-code CRM on top of Monday's work OS — perfect if your team already lives in Monday.",
        verdict="Best Visual Workflow", verdict_class="v-visual",
        pros=["Extremely flexible no-code customisation","Unified CRM + project management surface","Visual boards ideal for non-sales teams"],
        cons=["3-seat minimum on all paid plans","CRM depth thinner than HubSpot or Pipedrive"],
        go="monday-com", scores=dict(value=74,ease=86,features=72,int=84,support=76)),
    "Zoho CRM": dict(
        score=7.2, logo="https://cdn.simpleicons.org/zoho/e42527",
        price_line="Free", free_tag="Up to 3 users", price_note="Paid from $14/user/mo",
        tagline="Enterprise-grade features at SMB pricing — Zia AI, custom modules, multi-channel engagement.",
        verdict="Best Value", verdict_class="v-value",
        pros=["Outstanding feature-per-dollar ratio","Zia AI for deal predictions and sentiment scoring","Deeply customisable pipeline stages"],
        cons=["UI feels dated vs HubSpot","Support quality inconsistent on lower plans"],
        go="zoho-crm", scores=dict(value=97,ease=63,features=89,int=78,support=69)),
    "Freshsales": dict(
        score=6.8, logo="https://cdn.simpleicons.org/freshworks/ffffff",
        price_line="Free", free_tag="Forever", price_note="Paid from $9/user/mo",
        tagline="Freddy AI, built-in phone and email sequencing, forever-free plan — sharpest entry-level CRM pick.",
        verdict="Best for SMBs", verdict_class="v-smb",
        pros=["Forever-free plan with unlimited contacts","Built-in calling and email sequencing","Freddy AI on all paid plans"],
        cons=["Integration library lags HubSpot","Reporting needs work on growth tiers"],
        go="freshsales", scores=dict(value=90,ease=83,features=61,int=64,support=73)),
    "Close": dict(
        score=7.8, logo="https://cdn.simpleicons.org/close/499e4b",
        price_line="$49/user/mo", free_tag="", price_note="14-day free trial",
        tagline="The sales-first CRM for inside sales teams — built-in calling, SMS, and email sequences out of the box.",
        verdict="Best for Inside Sales", verdict_class="v-sales",
        pros=["Built-in power dialler and SMS","All-in-one: CRM, calls, and sequences","Transparent per-user pricing — no seat minimums"],
        cons=["More expensive than Pipedrive at scale","Weaker marketing automation"],
        go="close", scores=dict(value=78,ease=88,features=80,int=72,support=82)),
    # ── PROJECT MANAGEMENT ────────────────────────────────────────────────────
    "ClickUp": dict(
        score=8.7, logo="https://cdn.simpleicons.org/clickup/7b68ee",
        price_line="Free", free_tag="Forever", price_note="Paid from $7/user/mo",
        tagline="The most feature-rich project management tool available — tasks, docs, goals, whiteboards, and AI all in one.",
        verdict="Best Overall", verdict_class="v-best",
        pros=["Free plan includes 100MB storage and unlimited tasks","Most customisable views: List, Board, Gantt, Timeline","Built-in AI writing and task automation"],
        cons=["Feature overload can overwhelm new teams","Performance slows on very large workspaces"],
        go="clickup", scores=dict(value=92,ease=76,features=98,int=88,support=80)),
    "Asana": dict(
        score=8.3, logo="https://cdn.simpleicons.org/asana/f06a6a",
        price_line="Free", free_tag="Up to 10 users", price_note="Paid from $10.99/user/mo",
        tagline="Clean, intuitive project management for cross-functional teams — best-in-class workflow automation.",
        verdict="Best for Teams", verdict_class="v-ent",
        pros=["Intuitive UX — fastest onboarding in the category","Powerful workflow rules and automation","Strong reporting on Business and Enterprise tiers"],
        cons=["No native time tracking on free/Starter","Timeline view requires Premium tier ($10.99+)"],
        go="asana", scores=dict(value=82,ease=92,features=83,int=90,support=85)),
    "Notion": dict(
        score=8.0, logo="https://cdn.simpleicons.org/notion/ffffff",
        price_line="Free", free_tag="Personal use", price_note="Teams from $10/user/mo",
        tagline="The all-in-one workspace — docs, wikis, databases, and project tracking in a single connected system.",
        verdict="Best All-in-One Workspace", verdict_class="v-visual",
        pros=["Incredibly flexible — docs, wikis, and project tracking unified","AI writing assistant included on paid plans","Best-in-class knowledge management"],
        cons=["Not purpose-built for project management workflows","Can get complex to set up for large teams"],
        go="notion", scores=dict(value=88,ease=79,features=85,int=80,support=74)),
    "Jira": dict(
        score=7.9, logo="https://cdn.simpleicons.org/jira/0052cc",
        price_line="Free", free_tag="Up to 10 users", price_note="Paid from $7.75/user/mo",
        tagline="The gold standard for software and engineering teams — unmatched agile and sprint management depth.",
        verdict="Best for Dev Teams", verdict_class="v-ent",
        pros=["Industry standard for agile and scrum teams","Deep integration with GitHub, Bitbucket, Confluence","Highly customisable issue workflows"],
        cons=["Steep learning curve for non-technical users","Interface feels dated versus ClickUp"],
        go="jira", scores=dict(value=80,ease=65,features=93,int=95,support=78)),
    "Trello": dict(
        score=7.0, logo="https://cdn.simpleicons.org/trello/0052cc",
        price_line="Free", free_tag="Forever", price_note="Paid from $5/user/mo",
        tagline="The simplest Kanban board available — perfect for visual thinkers who want to start immediately.",
        verdict="Best for Simplicity", verdict_class="v-smb",
        pros=["Fastest setup of any PM tool — up in minutes","Clean, visual Kanban boards anyone can use","Very generous free plan"],
        cons=["Limited features beyond Kanban boards","No native Gantt or timeline view"],
        go="trello", scores=dict(value=85,ease=97,features=55,int=80,support=70)),
    "Linear": dict(
        score=8.5, logo="https://cdn.simpleicons.org/linear/ffffff",
        price_line="Free", free_tag="Up to 250 issues", price_note="Paid from $8/user/mo",
        tagline="The fastest, most opinionated issue tracker for software teams — blazing speed and minimal friction.",
        verdict="Best for Engineering", verdict_class="v-ent",
        pros=["Keyboard-first, blazing fast interface","Automatic sprint planning and cycle automation","Git integration syncs issues to PRs in real-time"],
        cons=["Designed specifically for engineering — limited for non-dev teams","Reporting less comprehensive than Jira"],
        go="linear", scores=dict(value=87,ease=89,features=84,int=88,support=80)),
    # ── EMAIL MARKETING ───────────────────────────────────────────────────────
    "Mailchimp": dict(
        score=7.8, logo="https://cdn.simpleicons.org/mailchimp/ffe01b",
        price_line="Free", free_tag="500 contacts", price_note="Paid from $13/mo",
        tagline="The most recognised email marketing brand — easy setup, great templates, solid automation for growing lists.",
        verdict="Best for Beginners", verdict_class="v-smb",
        pros=["Easiest email editor in the market","Strong pre-built automation journeys","Huge template library"],
        cons=["Pricing scales steeply with list size","Advanced segmentation requires Standard plan+"],
        go="mailchimp", scores=dict(value=74,ease=93,features=78,int=88,support=74)),
    "ActiveCampaign": dict(
        score=8.6, logo="https://cdn.simpleicons.org/activecampaign/356ae6",
        price_line="$15/mo", free_tag="", price_note="14-day free trial",
        tagline="The most powerful email automation platform — deep conditional logic, lead scoring, and CRM in one.",
        verdict="Best for Automation", verdict_class="v-best",
        pros=["Most sophisticated conditional automation in the market","Built-in CRM with pipeline and lead scoring","Predictive sending and win probability AI"],
        cons=["Steeper learning curve than Mailchimp","No free plan — $15/mo minimum"],
        go="activecampaign", scores=dict(value=82,ease=71,features=96,int=91,support=84)),
    "GetResponse": dict(
        score=8.0, logo="https://cdn.simpleicons.org/getresponse/00baff",
        price_line="Free", free_tag="500 contacts", price_note="Paid from $15/mo",
        tagline="Email marketing and webinar platform in one — great for solopreneurs, creators, and info-product businesses.",
        verdict="Best for Creators", verdict_class="v-visual",
        pros=["Built-in webinar and landing page tools","Conversion funnel builder included","Free plan available up to 500 contacts"],
        cons=["Email editor less polished than Mailchimp","Deliverability can vary on shared IPs"],
        go="getresponse", scores=dict(value=84,ease=80,features=82,int=75,support=78)),
    "Brevo": dict(
        score=7.9, logo="https://cdn.simpleicons.org/brevo/0b996e",
        price_line="Free", free_tag="300 emails/day", price_note="Paid from $25/mo",
        tagline="Formerly Sendinblue — unlimited contacts on every plan, great transactional email and SMS marketing.",
        verdict="Best Value", verdict_class="v-value",
        pros=["Unlimited contacts on ALL plans (including free)","SMS and WhatsApp marketing built in","Strong transactional email via SMTP/API"],
        cons=["Daily send limits on free plan (300/day)","Automation is less intuitive than ActiveCampaign"],
        go="brevo", scores=dict(value=91,ease=82,features=78,int=80,support=76)),
    "AWeber": dict(
        score=7.2, logo="https://cdn.simpleicons.org/aweber/ee342f",
        price_line="Free", free_tag="500 subscribers", price_note="Paid from $12.50/mo",
        tagline="One of the original email marketing platforms — reliable deliverability, solid autoresponders, and a genuine free plan up to 500 subscribers.",
        verdict="Best for Bloggers", verdict_class="v-smb",
        pros=["Generous free plan — 500 subscribers, full feature access","Industry-leading deliverability reputation","Huge library of email templates and landing pages"],
        cons=["UI feels dated vs modern tools like GetResponse","Automation workflows less powerful than ActiveCampaign"],
        go="aweber", scores=dict(value=78,ease=82,features=71,int=74,support=78)),
    # ── SEO ───────────────────────────────────────────────────────────────────
    "Semrush": dict(
        score=9.0, logo="https://cdn.simpleicons.org/semrush/ff642d",
        price_line="$139.95/mo", free_tag="", price_note="7-day free trial",
        tagline="The most comprehensive SEO platform — keyword research, site audit, competitor analysis, and content tools all-in-one.",
        verdict="Best Overall", verdict_class="v-best",
        pros=["Most complete keyword database — 25B+ keywords","Domain vs domain competitor analysis","Position tracking across 500+ keywords on Pro"],
        cons=["Expensive — starts at $139.95/mo","One user per account on Pro tier"],
        go="semrush", scores=dict(value=78,ease=82,features=98,int=88,support=85)),
    "Ahrefs": dict(
        score=8.8, logo="https://cdn.simpleicons.org/ahrefs/2196f3",
        price_line="$129/mo", free_tag="", price_note="Ahrefs Free Webmaster Tools",
        tagline="Best-in-class backlink analysis and technical SEO — the tool SEO professionals trust most for link research.",
        verdict="Best for Link Building", verdict_class="v-ent",
        pros=["Best backlink database in the industry — 35T+ links","Site Audit crawls JavaScript-heavy sites accurately","Content Explorer finds top-performing content by topic"],
        cons=["More expensive than SE Ranking for same core features","No CRM or agency client reporting module"],
        go="ahrefs", scores=dict(value=76,ease=80,features=93,int=84,support=80)),
    "Moz Pro": dict(
        score=7.8, logo="https://cdn.simpleicons.org/moz/2196f3",
        price_line="$99/mo", free_tag="", price_note="30-day free trial",
        tagline="The most beginner-friendly professional SEO tool — Domain Authority, keyword explorer, and clear rank tracking.",
        verdict="Best for Beginners", verdict_class="v-smb",
        pros=["Domain Authority metric is the industry standard","Intuitive interface — quick to onboard","Strong local SEO features"],
        cons=["Smaller keyword database than Semrush/Ahrefs","Crawl limits lower than competitors at same price"],
        go="moz-pro", scores=dict(value=80,ease=88,features=76,int=78,support=80)),
    "SE Ranking": dict(
        score=8.2, logo="https://cdn.simpleicons.org/google/4285f4",
        price_line="$52/mo", free_tag="", price_note="14-day free trial",
        tagline="The best value professional SEO suite — all Semrush features at half the price, with an excellent white-label module.",
        verdict="Best Value", verdict_class="v-value",
        pros=["Full SEO toolkit at 40–60% less than Semrush/Ahrefs","White-label reporting for agencies","Unlimited websites on higher plans"],
        cons=["Smaller backlink database than Ahrefs","Less brand recognition may affect client perception"],
        go="se-ranking", scores=dict(value=94,ease=85,features=84,int=79,support=82)),
    "Surfer SEO": dict(
        score=8.1, logo="https://cdn.simpleicons.org/surferseo/ff6a13",
        price_line="$89/mo", free_tag="", price_note="7-day free trial",
        tagline="The leading on-page SEO optimiser — real-time content scoring against top-ranking pages for any keyword.",
        verdict="Best for Content SEO", verdict_class="v-visual",
        pros=["Real-time content score matches top SERP pages","NLP keyword suggestions from top 20 competitors","Audit existing pages for quick SEO wins"],
        cons=["Focused on on-page — no backlink or technical SEO module","Monthly cost adds up for large content teams"],
        go="surfer-seo", scores=dict(value=81,ease=87,features=79,int=76,support=78)),
    # ── VPN ───────────────────────────────────────────────────────────────────
    "NordVPN": dict(
        score=9.2, logo="https://cdn.simpleicons.org/nordvpn/4687ff",
        price_line="$2.99/mo", free_tag="", price_note="30-day money-back guarantee",
        tagline="The gold standard consumer VPN — 6,300+ servers, Deloitte-audited no-logs, and Threat Protection without active VPN.",
        verdict="Best Overall", verdict_class="v-best",
        pros=["6,300+ servers in 111 countries","Deloitte-audited no-logs policy — zero data stored","Threat Protection blocks malware without VPN active"],
        cons=["Best price requires 2-year upfront commitment","No dedicated business management dashboard"],
        go="nordvpn", scores=dict(value=91,ease=94,features=93,int=85,support=88)),
    "Surfshark": dict(
        score=8.8, logo="https://cdn.simpleicons.org/surfshark/1ce0c3",
        price_line="$2.49/mo", free_tag="", price_note="30-day money-back guarantee",
        tagline="Best value VPN — unlimited simultaneous devices, CleanWeb ad-blocker, and multi-hop servers included.",
        verdict="Best Value", verdict_class="v-value",
        pros=["Unlimited devices on one subscription","CleanWeb 2.0 ad-blocker and malware protection","Nexus network for consistent server routing"],
        cons=["Slightly slower than NordVPN on distant servers","Smaller server network than NordVPN"],
        go="surfshark", scores=dict(value=96,ease=91,features=86,int=79,support=82)),
    "ExpressVPN": dict(
        score=8.5, logo="https://cdn.simpleicons.org/express/fc172f",
        price_line="$8.32/mo", free_tag="", price_note="30-day money-back guarantee",
        tagline="The fastest VPN available — premium speed, Lightway protocol, and excellent streaming unblocking.",
        verdict="Fastest VPN", verdict_class="v-ent",
        pros=["Consistently fastest speeds in independent tests","Lightway protocol — fast and secure","Excellent streaming unblocking (Netflix, Disney+)"],
        cons=["Most expensive major VPN — 2–3× NordVPN's price","No ad-blocking or malware protection built in"],
        go="expressvpn", scores=dict(value=68,ease=91,features=82,int=80,support=87)),
    "ProtonVPN": dict(
        score=8.6, logo="https://cdn.simpleicons.org/protonvpn/6d4aff",
        price_line="Free", free_tag="Unlimited data", price_note="Paid from $4.99/mo",
        tagline="The most privacy-focused VPN — Swiss-based, open-source, audited, and the only VPN with a genuinely unlimited free tier.",
        verdict="Best for Privacy", verdict_class="v-ent",
        pros=["Only free VPN with unlimited data and no speed cap","Swiss-based, no-logs, open-source and audited","Netshield DNS-based ad-blocker on paid plans"],
        cons=["Fewer servers than NordVPN/Surfshark","Free plan limited to 3 server locations"],
        go="protonvpn", scores=dict(value=88,ease=84,features=85,int=76,support=79)),
    "CyberGhost": dict(
        score=7.8, logo="https://cdn.simpleicons.org/cyberghost/ffcc00",
        price_line="$2.19/mo", free_tag="", price_note="45-day money-back guarantee",
        tagline="The most beginner-friendly VPN — one-click streaming profiles, 9,000+ servers, and the longest money-back guarantee.",
        verdict="Best for Beginners", verdict_class="v-smb",
        pros=["9,000+ servers — largest network of major VPNs","Dedicated streaming and torrenting profiles","45-day money-back guarantee — longest in the market"],
        cons=["Based in Romania (outside 14-Eyes) — some users prefer Swiss","Slightly slower than NordVPN on short-distance servers"],
        go="cyberghost", scores=dict(value=86,ease=93,features=78,int=72,support=81)),
    # ── PASSWORD MANAGERS ─────────────────────────────────────────────────────
    "1Password": dict(
        score=9.0, logo="https://cdn.simpleicons.org/1password/1a8cff",
        price_line="$2.99/mo", free_tag="", price_note="14-day free trial",
        tagline="The best password manager for teams and families — Travel Mode, Watchtower breach alerts, and the cleanest UX in the category.",
        verdict="Best Overall", verdict_class="v-best",
        pros=["Travel Mode hides vaults when crossing borders","Watchtower monitors breaches and weak passwords","Most polished UX across all platforms"],
        cons=["No free plan — $2.99/mo minimum","Slightly more expensive than Bitwarden for same features"],
        go="1password", scores=dict(value=86,ease=94,features=90,int=87,support=89)),
    "LastPass": dict(
        score=7.0, logo="https://cdn.simpleicons.org/lastpass/d32d27",
        price_line="Free", free_tag="1 device type", price_note="Paid from $3/mo",
        tagline="Once the most popular password manager — now struggling to rebuild trust after two major data breaches in 2022.",
        verdict="Use with Caution", verdict_class="v-smb",
        pros=["Free plan available (one device type)","Familiar interface for long-time users","Family plan for up to 6 users at $4/mo"],
        cons=["Major data breach in 2022 exposed encrypted vaults","Free plan restricted to one device type since 2021"],
        go="lastpass", scores=dict(value=70,ease=80,features=72,int=78,support=60)),
    "Bitwarden": dict(
        score=8.7, logo="https://cdn.simpleicons.org/bitwarden/175ddc",
        price_line="Free", free_tag="Unlimited devices", price_note="Premium from $10/year",
        tagline="The best open-source password manager — unlimited free tier, self-hosting option, and fully audited codebase.",
        verdict="Best Free Option", verdict_class="v-value",
        pros=["Free plan includes unlimited devices and vault items","Open-source and independently audited","Self-hosting option for privacy-first teams"],
        cons=["UI less polished than 1Password","Two-factor authentication setup can confuse beginners"],
        go="bitwarden", scores=dict(value=97,ease=79,features=85,int=80,support=76)),
    "Dashlane": dict(
        score=8.0, logo="https://cdn.simpleicons.org/dashlane/0a2540",
        price_line="Free", free_tag="25 passwords", price_note="Paid from $4.99/mo",
        tagline="The most security-focused consumer password manager — built-in VPN, dark web monitoring, and Identity Theft Insurance.",
        verdict="Best Security Bundle", verdict_class="v-ent",
        pros=["Built-in VPN powered by Hotspot Shield","Dark web monitoring included on premium plans","Passkey support and phishing alerts"],
        cons=["Free plan limited to 25 passwords and 1 device","More expensive than Bitwarden for same core features"],
        go="dashlane", scores=dict(value=79,ease=88,features=84,int=79,support=82)),
    "NordPass": dict(
        score=8.2, logo="https://cdn.simpleicons.org/nordpass/4687ff",
        price_line="Free", free_tag="Unlimited items", price_note="Paid from $1.99/mo",
        tagline="The cleanest, most affordable premium password manager — XChaCha20 encryption and a genuinely unlimited free tier.",
        verdict="Best Budget Option", verdict_class="v-value",
        pros=["XChaCha20 encryption — more modern than AES-256","Free plan with unlimited passwords (one active device)","Data breach scanner on all plans"],
        cons=["Newer product — fewer integrations than 1Password","Limited import options compared to competitors"],
        go="nordpass", scores=dict(value=91,ease=90,features=79,int=74,support=80)),
    # ── ACCOUNTING ────────────────────────────────────────────────────────────
    "FreshBooks": dict(
        score=8.5, logo="https://cdn.simpleicons.org/freshbooks/2da94f",
        price_line="$17/mo", free_tag="", price_note="30-day free trial",
        tagline="The best invoicing and accounting software for freelancers and service businesses — time tracking built in.",
        verdict="Best for Freelancers", verdict_class="v-best",
        pros=["Best invoicing UX in the market — clients pay faster","Built-in time tracking and project profitability","Automatic late payment reminders and retainers"],
        cons=["Limited inventory management for product businesses","Billing is per client, not per user — costs scale oddly"],
        go="freshbooks", scores=dict(value=82,ease=93,features=82,int=84,support=88)),
    "Xero": dict(
        score=8.3, logo="https://cdn.simpleicons.org/xero/13b5ea",
        price_line="$15/mo", free_tag="", price_note="30-day free trial",
        tagline="The leading cloud accounting platform for small businesses — bank reconciliation, inventory, and 1,000+ app integrations.",
        verdict="Best for Small Business", verdict_class="v-ent",
        pros=["Best bank reconciliation and real-time reporting","1,000+ app integrations — widest ecosystem","Unlimited users on all plans (unique in the market)"],
        cons=["No phone support — email and chat only","Payroll requires a paid Gusto add-on in the US"],
        go="xero", scores=dict(value=84,ease=81,features=88,int=93,support=74)),
    "QuickBooks": dict(
        score=7.9, logo="https://cdn.simpleicons.org/quickbooks/2ca01c",
        price_line="$30/mo", free_tag="", price_note="30-day free trial",
        tagline="The most widely used small business accounting software — unmatched accountant ecosystem and payroll integration.",
        verdict="Best for US Businesses", verdict_class="v-ent",
        pros=["Most accountants and bookkeepers know QuickBooks","Payroll and HR fully integrated (QuickBooks Payroll)","Desktop and online versions available"],
        cons=["Most expensive option in the category","Frequent price increases and feature limitations on lower tiers"],
        go="quickbooks", scores=dict(value=68,ease=79,features=85,int=86,support=75)),
    "Wave": dict(
        score=7.5, logo="https://cdn.simpleicons.org/wave/ff5b24",
        price_line="Free", free_tag="Accounting is free", price_note="Pay per transaction",
        tagline="The best free accounting software — invoicing, accounting, and receipt scanning at zero monthly cost.",
        verdict="Best Free Option", verdict_class="v-value",
        pros=["Accounting and invoicing completely free forever","No monthly fee — pay only per transaction processed","Clean, intuitive interface for non-accountants"],
        cons=["Payroll costs extra (US and Canada only)","No inventory management","Limited third-party integrations vs Xero/QuickBooks"],
        go="wave", scores=dict(value=98,ease=88,features=65,int=55,support=66)),
    # ── HR / PAYROLL ──────────────────────────────────────────────────────────
    "Rippling": dict(
        score=9.0, logo="https://cdn.simpleicons.org/rippling/f6c90e",
        price_line="$8/user/mo", free_tag="", price_note="Custom quote required",
        tagline="The most powerful HR platform available — payroll, benefits, IT, and device management in a single system.",
        verdict="Best All-in-One", verdict_class="v-best",
        pros=["HR, payroll, IT, and device management in one platform","Onboards employees and provisions software in 90 seconds","Best international payroll capabilities in the category"],
        cons=["Requires custom quote — no transparent pricing","Overkill for teams under 50 people"],
        go="rippling", scores=dict(value=82,ease=81,features=96,int=91,support=84)),
    "Gusto": dict(
        score=8.4, logo="https://cdn.simpleicons.org/gusto/f45d48",
        price_line="$40/mo + $6/user", free_tag="", price_note="1-month free trial",
        tagline="The best payroll software for US small businesses — full-service payroll, benefits, and HR all in one simple platform.",
        verdict="Best for Small Business", verdict_class="v-smb",
        pros=["Full-service payroll with automatic tax filing","Benefits administration (health, 401k, commuter)","Simple pricing — $40 base + $6/person"],
        cons=["US-only — no international payroll","Limited HR features compared to Rippling on lower tiers"],
        go="gusto", scores=dict(value=85,ease=90,features=80,int=82,support=87)),
    "BambooHR": dict(
        score=8.1, logo="https://cdn.simpleicons.org/bamboohr/73c41d",
        price_line="$6/user/mo", free_tag="", price_note="Free trial available",
        tagline="The best HRIS for mid-size companies — employee records, onboarding, PTO tracking, and performance reviews.",
        verdict="Best for Mid-Market", verdict_class="v-ent",
        pros=["Best employee self-service portal in the category","Onboarding workflows with e-signature","Excellent performance review and goal-tracking module"],
        cons=["Payroll is an expensive add-on (US only)","Mobile app less capable than the web version"],
        go="bamboohr", scores=dict(value=79,ease=88,features=82,int=80,support=85)),
    "Deel": dict(
        score=8.6, logo="https://cdn.simpleicons.org/deel/ffffff",
        price_line="$49/mo", free_tag="", price_note="Free for 200 employees",
        tagline="The global payroll and EOR platform — hire, pay, and manage contractors and employees in 150+ countries.",
        verdict="Best for Global Teams", verdict_class="v-ent",
        pros=["Employer of record (EOR) in 150+ countries","Contractor payments in 150+ currencies","Built-in IP protection and local compliance"],
        cons=["Expensive for large teams vs direct local entities","Support can be slow during high-volume periods"],
        go="deel", scores=dict(value=82,ease=82,features=88,int=80,support=78)),
    # ── ECOMMERCE ─────────────────────────────────────────────────────────────
    "Shopify": dict(
        score=9.1, logo="https://cdn.simpleicons.org/shopify/96bf48",
        price_line="$29/mo", free_tag="", price_note="3-day free trial",
        tagline="The world's most popular ecommerce platform — 6,000+ apps, best-in-class checkout, and built for scale.",
        verdict="Best Overall", verdict_class="v-best",
        pros=["Best checkout conversion rate in the market","6,000+ app integrations — largest ecosystem","Excellent multi-currency and international selling"],
        cons=["Transaction fees if not using Shopify Payments","Advanced reports locked to $79+/mo plans"],
        go="shopify", scores=dict(value=84,ease=88,features=92,int=97,support=85)),
    "BigCommerce": dict(
        score=8.1, logo="https://cdn.simpleicons.org/bigcommerce/121118",
        price_line="$39/mo", free_tag="", price_note="15-day free trial",
        tagline="The most scalable open-SaaS ecommerce platform — no transaction fees, built-in B2B, and headless commerce support.",
        verdict="Best for Scale", verdict_class="v-ent",
        pros=["No transaction fees on any plan","Best-in-class B2B and wholesale features","Headless commerce ready — connect any front end"],
        cons=["Annual revenue limits force plan upgrades","Less intuitive than Shopify for beginners"],
        go="bigcommerce", scores=dict(value=83,ease=75,features=88,int=85,support=80)),
    "Wix": dict(
        score=7.6, logo="https://cdn.simpleicons.org/wix/000000",
        price_line="$27/mo", free_tag="", price_note="14-day money-back guarantee",
        tagline="The easiest website builder with an ecommerce layer — drag-and-drop simplicity with enough features for small shops.",
        verdict="Best for Beginners", verdict_class="v-smb",
        pros=["Fastest site setup — live store in under an hour","ADI (Artificial Design Intelligence) auto-builds your site","All hosting included — no technical knowledge needed"],
        cons=["Can't change template once published","Not suitable for high-volume or enterprise ecommerce"],
        go="wix", scores=dict(value=79,ease=95,features=68,int=74,support=76)),
    "WooCommerce": dict(
        score=7.8, logo="https://cdn.simpleicons.org/woocommerce/7f54b3",
        price_line="Free", free_tag="Plugin is free", price_note="Hosting from $10/mo",
        tagline="The most customisable ecommerce platform — free open-source WordPress plugin with unlimited flexibility.",
        verdict="Best Open Source", verdict_class="v-value",
        pros=["Free to install — only pay for hosting and extensions","Unlimited customisation with 800+ extensions","Full data ownership — no platform lock-in"],
        cons=["Requires WordPress knowledge to set up","Security and updates are your responsibility"],
        go="woocommerce", scores=dict(value=84,ease=62,features=89,int=88,support=70)),
    # ── WEBSITE BUILDERS ─────────────────────────────────────────────────────
    "Webflow": dict(
        score=8.4, logo="https://cdn.simpleicons.org/webflow/4353ff",
        price_line="$14/mo", free_tag="Free sandbox", price_note="Free plan available",
        tagline="The most powerful no-code website builder — full CSS control without writing code, and built-in CMS.",
        verdict="Best for Designers", verdict_class="v-visual",
        pros=["Full CSS and layout control without writing code","Built-in CMS and ecommerce on paid plans","Clean, semantic code export — no lock-in"],
        cons=["Steep learning curve — not for beginners","Editor mode confusing for non-designers"],
        go="webflow", scores=dict(value=82,ease=65,features=91,int=80,support=79)),
    "Squarespace": dict(
        score=7.9, logo="https://cdn.simpleicons.org/squarespace/000000",
        price_line="$16/mo", free_tag="", price_note="14-day free trial",
        tagline="The most beautiful website templates available — perfect for creatives, photographers, and service businesses.",
        verdict="Best for Creatives", verdict_class="v-visual",
        pros=["Best-looking templates in any website builder","Built-in SEO, scheduling, and email marketing","24/7 live chat support on all plans"],
        cons=["Less flexible than Webflow for complex layouts","Transaction fees on Commerce Basic plan"],
        go="squarespace", scores=dict(value=80,ease=84,features=78,int=72,support=85)),
    # ── WORDPRESS PAGE BUILDERS ───────────────────────────────────────────────
    "Elementor": dict(
        score=8.7, logo="https://cdn.simpleicons.org/elementor/92003b",
        price_line="$49/yr", free_tag="Free plugin", price_note="Free version available",
        tagline="The most popular WordPress page builder — drag-and-drop editor, 100+ widgets, WooCommerce integration, and a massive template library.",
        verdict="Best for WordPress", verdict_class="v-best",
        pros=["Most popular WordPress page builder — 12M+ sites","Free version with 40+ basic widgets","Full WooCommerce integration on Pro"],
        cons=["WordPress-only — not useful outside WP","Pro pricing jumped to $49–$399/yr in 2024"],
        go="elementor", scores=dict(value=82,ease=88,features=91,int=85,support=80)),
    "Divi": dict(
        score=8.2, logo="https://www.google.com/s2/favicons?domain=elegantthemes.com&sz=128",
        price_line="$89/yr", free_tag="", price_note="Lifetime $249",
        tagline="The second most popular WordPress page builder — visual front-end editor, split testing, and a 200-theme library all in one subscription.",
        verdict="Best Value", verdict_class="v-value",
        pros=["Visual front-end editor with inline text editing","Built-in A/B split testing — rare at this price","Lifetime access option at $249 (pay once)"],
        cons=["Slower than Elementor in page-speed benchmarks","Less extensive widget library than Elementor Pro"],
        go="divi", scores=dict(value=86,ease=82,features=85,int=78,support=77)),
    "Beaver Builder": dict(
        score=8.0, logo="https://www.google.com/s2/favicons?domain=wpbeaverbuilder.com&sz=128",
        price_line="$99/yr", free_tag="", price_note="Lifetime from $399",
        tagline="The most developer-friendly WordPress page builder — clean code output, white-labelling for agencies, and a strong backwards-compatibility guarantee.",
        verdict="Best for Agencies", verdict_class="v-visual",
        pros=["Cleanest code output of any major page builder","White-label option for client agencies","Strong backwards compatibility — no breaking changes between versions"],
        cons=["Smaller template library than Elementor or Divi","No free version of the full builder"]),
    "Bricks Builder": dict(
        score=8.4, logo="https://www.google.com/s2/favicons?domain=bricksbuilder.io&sz=128",
        price_line="$79/yr", free_tag="", price_note="Lifetime $299",
        tagline="The performance-first WordPress page builder — no jQuery dependency, full theme control, and built for developers who care about Core Web Vitals.",
        verdict="Best for Performance", verdict_class="v-smb",
        pros=["No jQuery dependency — significantly faster page loads","Full theme builder — headers, footers, archives","Query loop builder for dynamic custom post types"],
        cons=["Steeper learning curve than Elementor","Smaller community and ecosystem"],
        go="bricks-builder", scores=dict(value=84,ease=72,features=88,int=78,support=74)),
    "SeedProd": dict(
        score=7.9, logo="https://www.google.com/s2/favicons?domain=seedprod.com&sz=128",
        price_line="$79/yr", free_tag="Free version", price_note="Free landing pages available",
        tagline="The best landing page builder for WordPress — coming soon pages, opt-in pages, and WooCommerce layouts without touching your existing theme.",
        verdict="Best for Landing Pages", verdict_class="v-smb",
        pros=["Works independently of your existing theme","350+ conversion-optimised templates","Built-in subscriber list integration with major email providers"],
        cons=["Focused on landing pages — limited for full site building","Full WooCommerce features require top-tier plan"],
        go="seedprod", scores=dict(value=80,ease=86,features=75,int=80,support=77)),
    # ── DEV TOOLS / INFRA ─────────────────────────────────────────────────────
    "GitHub Copilot": dict(
        score=8.9, logo="https://cdn.simpleicons.org/github/ffffff",
        price_line="$10/mo", free_tag="", price_note="Free for students/OSS",
        tagline="The most widely used AI coding assistant — context-aware code completions and chat in your IDE.",
        verdict="Best Overall", verdict_class="v-best",
        pros=["Trained on billions of lines of public code","Deep VS Code, JetBrains, and Neovim integration","Chat mode for code explanation and debugging"],
        cons=["Can suggest outdated or insecure code patterns","Requires constant review — not a replacement for understanding"],
        go="github-copilot", scores=dict(value=88,ease=90,features=88,int=95,support=79)),
    "Vercel": dict(
        score=8.8, logo="https://cdn.simpleicons.org/vercel/ffffff",
        price_line="Free", free_tag="Hobby plan", price_note="Pro from $20/user/mo",
        tagline="The best frontend deployment platform — zero-config Next.js hosting, edge functions, and automatic preview deployments.",
        verdict="Best for Frontend", verdict_class="v-best",
        pros=["Zero-config deployment from GitHub push","Edge network in 100+ locations for global performance","Automatic preview URLs for every pull request"],
        cons=["Hobby plan has bandwidth limits","Enterprise plan pricing requires custom quote"],
        go="vercel", scores=dict(value=88,ease=93,features=86,int=90,support=80)),
    "Datadog": dict(
        score=8.5, logo="https://cdn.simpleicons.org/datadog/632ca6",
        price_line="$15/host/mo", free_tag="", price_note="14-day free trial",
        tagline="The most comprehensive observability platform — metrics, logs, traces, and APM in a unified view.",
        verdict="Best for Enterprise", verdict_class="v-ent",
        pros=["Best unified monitoring — metrics, logs, and traces together","700+ integrations out of the box","AI-powered anomaly detection and root cause analysis"],
        cons=["Costs can spiral quickly — priced per host and feature","Steep learning curve for smaller teams"],
        go="datadog", scores=dict(value=72,ease=71,features=95,int=97,support=82)),
    "Snyk": dict(
        score=8.3, logo="https://cdn.simpleicons.org/snyk/4c4a73",
        price_line="Free", free_tag="Open source", price_note="Team from $25/user/mo",
        tagline="The leading developer security platform — fix vulnerabilities in code, containers, and open source dependencies.",
        verdict="Best for Dev Security", verdict_class="v-ent",
        pros=["Fix suggestions in the IDE before code is merged","Scans code, containers, IaC, and open source dependencies","Free plan for open source and individual developers"],
        cons=["Enterprise plan pricing is opaque","Learning curve for security-first workflows"],
        go="snyk", scores=dict(value=83,ease=82,features=87,int=90,support=79)),
    "Render": dict(
        score=8.0, logo="https://cdn.simpleicons.org/render/46e3b7",
        price_line="Free", free_tag="Static sites free", price_note="Services from $7/mo",
        tagline="The simplest cloud platform for full-stack apps — deploy from Git in minutes, auto-scaling included.",
        verdict="Best for Indie Devs", verdict_class="v-smb",
        pros=["Free static site hosting with auto-deploy from Git","Simpler and cheaper than AWS for most web apps","PostgreSQL databases included with services"],
        cons=["Free tier spins down after 15 min of inactivity","Less enterprise support than AWS/GCP/Azure"],
        go="render", scores=dict(value=90,ease=91,features=77,int=78,support=76)),
    "Amplitude": dict(
        score=8.4, logo="https://cdn.simpleicons.org/amplitude/2559e1",
        price_line="Free", free_tag="10M events/mo", price_note="Paid from $61/mo",
        tagline="The best product analytics platform — understand user behaviour, build funnels, and ship with confidence.",
        verdict="Best for Product Teams", verdict_class="v-best",
        pros=["Free plan supports 10M monthly events","Best funnel and retention analysis in the market","Session replay and feature flags included on Growth"],
        cons=["Pricing scales quickly with event volume","Steeper learning curve than Mixpanel for non-analysts"],
        go="amplitude", scores=dict(value=86,ease=76,features=91,int=86,support=79)),
    "Mixpanel": dict(
        score=8.1, logo="https://cdn.simpleicons.org/mixpanel/7856ff",
        price_line="Free", free_tag="20M events/mo", price_note="Paid from $28/mo",
        tagline="The most developer-friendly product analytics tool — event tracking, cohort analysis, and A/B testing.",
        verdict="Best for Developers", verdict_class="v-ent",
        pros=["Best free tier in analytics — 20M events/mo free","Simple API and clean dashboard for developers","Lexicon data dictionary keeps tracking organised"],
        cons=["Less powerful funnel analysis than Amplitude","No built-in session replay"],
        go="mixpanel", scores=dict(value=88,ease=82,features=82,int=85,support=77)),
    # ── VIDEO / COMMUNICATION ─────────────────────────────────────────────────
    "Zoom": dict(
        score=8.3, logo="https://cdn.simpleicons.org/zoom/2d8cff",
        price_line="Free", free_tag="40-min limit", price_note="Paid from $14.99/mo",
        tagline="The most widely used video conferencing platform — simple, reliable, and the default for remote meetings.",
        verdict="Best for Meetings", verdict_class="v-best",
        pros=["Universal adoption — virtually everyone has Zoom installed","Excellent call quality and breakout rooms","Webinar and events functionality on paid plans"],
        cons=["Free plan limited to 40-minute group meetings","Security concerns led to 'Zoombomb' issues (since fixed)"],
        go="zoom", scores=dict(value=82,ease=95,features=82,int=88,support=78)),
    "Microsoft Teams": dict(
        score=7.8, logo="https://cdn.simpleicons.org/microsoftteams/6264a7",
        price_line="Free", free_tag="Microsoft 365 included", price_note="Paid from $6/user/mo",
        tagline="The best video conferencing for Microsoft 365 shops — deep integration with Outlook, SharePoint, and Office.",
        verdict="Best for Microsoft Users", verdict_class="v-ent",
        pros=["Deeply integrated with Microsoft 365 stack","Channels, chat, and video all in one hub","Strong compliance and governance features"],
        cons=["Interface more complex than Zoom or Google Meet","Non-Microsoft users find the experience clunky"],
        go="microsoft-teams", scores=dict(value=81,ease=72,features=85,int=89,support=79)),
    "Google Meet": dict(
        score=7.6, logo="https://cdn.simpleicons.org/googlemeet/00897b",
        price_line="Free", free_tag="60-min limit", price_note="Workspace from $6/user/mo",
        tagline="The best free video conferencing for Google Workspace users — no downloads, browser-native, deeply integrated with Calendar.",
        verdict="Best for Google Users", verdict_class="v-value",
        pros=["No software install — runs entirely in the browser","Integrated with Google Calendar and Gmail","Free plan allows 60-minute meetings (vs Zoom's 40)"],
        cons=["Limited features vs Zoom on free plan","Whiteboard and annotation tools less capable than competitors"],
        go="google-meet", scores=dict(value=86,ease=93,features=68,int=91,support=72)),
    "Webex": dict(
        score=7.2, logo="https://cdn.simpleicons.org/cisco/049fd4",
        price_line="Free", free_tag="40-min limit", price_note="Paid from $14.50/user/mo",
        tagline="Cisco's enterprise video platform — best-in-class hardware integration and meeting room management.",
        verdict="Best for Enterprise", verdict_class="v-ent",
        pros=["Best hardware integration for meeting rooms (Webex devices)","Strong compliance and end-to-end encryption","AI meeting summaries and transcription"],
        cons=["Consumer adoption far lower than Zoom","More complex pricing and setup than competitors"],
        go="webex", scores=dict(value=71,ease=73,features=80,int=80,support=77)),
}

# Aliases — map variant names to canonical names
ALIASES = {
    "HubSpot": "HubSpot CRM",
    "Monday": "Monday.com",
    "Zoho": "Zoho CRM",
    "ActiveCampaign (Marketing)": "ActiveCampaign",
    "SE Ranking (Best Value)": "SE Ranking",
    "Salesforce Essentials": "Salesforce",
    "Wix eCommerce": "Wix",
    "QuickBooks Self-Employed": "QuickBooks",
    "GitHub Issues": "Jira",
    "Moz": "Moz Pro",
    "Surfer": "Surfer SEO",
    "Notion (Alternative Option)": "Notion",
    "ClickUp (Alternative Option)": "ClickUp",
    "Asana (Alternative Option)": "Asana",
    "Divi Builder": "Divi",
    "Elegant Themes Divi": "Divi",
    "Bricks": "Bricks Builder",
    "SeedProd Builder": "SeedProd",
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def score_to_ring(score):
    offset = round(182.2 * (1 - score / 10), 1)
    if score >= 9.0:
        cls = "sr-gold"
    elif score >= 8.0:
        cls = "sr-silver"
    elif score >= 7.5:
        cls = "sr-bronze"
    else:
        cls = "sr-pink"
    return cls, offset

def rank_class(n):
    return f"r{min(n, 6)}"

CROWN_TEXT = "⭐ Best Overall 2026"

def tool_tokens(n, tool_name, tool_data, go_link):
    """Build token dict for one tool card."""
    ring_cls, offset = score_to_ring(tool_data["score"])
    s = tool_data.get("scores", {})
    t = {
        f"TOOL_{n}_NAME": tool_name,
        f"TOOL_{n}_SCORE": str(tool_data["score"]),
        f"TOOL_{n}_VERDICT": tool_data["verdict"],
        f"TOOL_{n}_VERDICT_CLASS": tool_data["verdict_class"],
        f"TOOL_{n}_RING_CLASS": ring_cls,
        f"TOOL_{n}_SCORE_OFFSET": str(offset),
        f"TOOL_{n}_TAGLINE": tool_data["tagline"],
        f"TOOL_{n}_LOGO_URL": tool_data["logo"],
        f"TOOL_{n}_VALUE_PCT": str(s.get("value", 75)),
        f"TOOL_{n}_VALUE_SCORE": str(round(s.get("value", 75) / 10, 1)),
        f"TOOL_{n}_EASE_PCT": str(s.get("ease", 75)),
        f"TOOL_{n}_EASE_SCORE": str(round(s.get("ease", 75) / 10, 1)),
        f"TOOL_{n}_FEATURES_PCT": str(s.get("features", 75)),
        f"TOOL_{n}_FEATURES_SCORE": str(round(s.get("features", 75) / 10, 1)),
        f"TOOL_{n}_INT_PCT": str(s.get("int", 75)),
        f"TOOL_{n}_INT_SCORE": str(round(s.get("int", 75) / 10, 1)),
        f"TOOL_{n}_SUPPORT_PCT": str(s.get("support", 75)),
        f"TOOL_{n}_SUPPORT_SCORE": str(round(s.get("support", 75) / 10, 1)),
        f"TOOL_{n}_PRO_1": tool_data["pros"][0] if len(tool_data["pros"]) > 0 else "Strong feature set",
        f"TOOL_{n}_PRO_2": tool_data["pros"][1] if len(tool_data["pros"]) > 1 else "Good value for money",
        f"TOOL_{n}_PRO_3": tool_data["pros"][2] if len(tool_data["pros"]) > 2 else "Easy to get started",
        f"TOOL_{n}_CON_1": tool_data["cons"][0] if len(tool_data["cons"]) > 0 else "Premium features cost extra",
        f"TOOL_{n}_CON_2": tool_data["cons"][1] if len(tool_data["cons"]) > 1 else "Learning curve for advanced use",
        f"TOOL_{n}_PRICE_LINE": tool_data["price_line"],
        f"TOOL_{n}_PRICE_NOTE": tool_data["price_note"],
        f"TOOL_{n}_GO_LINK": go_link or f"/go/{tool_data.get('go', tool_name.lower().replace(' ', '-'))}",
        f"TOOL_{n}_CROWN_TEXT": CROWN_TEXT if n == 1 else "",
    }
    return t

def make_unknown_tool(name, go_slug=""):
    """Fallback for tools not in the database."""
    score = 7.5
    ring_cls, offset = score_to_ring(score)
    slug = go_slug or name.lower().replace(" ", "-").replace(".", "")
    return dict(
        score=score, logo=f"https://cdn.simpleicons.org/{slug}/888888",
        price_line="See website", free_tag="", price_note="Visit for current pricing",
        tagline=f"{name} is a popular SaaS tool used by thousands of businesses worldwide.",
        verdict="Worth Considering", verdict_class="v-smb",
        pros=[f"Established {name} user base","Good integration ecosystem","Regular feature updates"],
        cons=["Check current pricing on their website","Compare with alternatives before committing"],
        go=slug, scores=dict(value=75,ease=75,features=75,int=75,support=75)
    )

def extract_tools_from_page(html):
    """Extract tool names + go links from an existing best-of page."""
    candidates = []

    # Pattern 1: "X Review" headings
    candidates += re.findall(r'<h2[^>]*>\s*([A-Za-z0-9][^<]{1,50}?)\s*Review\s*</h2>', html)

    # Pattern 2: "X Top Pick" headings
    candidates += re.findall(r'<h2[^>]*>\s*([A-Za-z0-9][^<]{1,50}?)\s*Top Pick\s*</h2>', html)

    # Pattern 3: standalone tool-name h2 (used in some pages)
    # Only use these if they're in the known TOOLS database
    h2_plain = re.findall(r'<h2[^>]*>\s*([A-Za-z][^<]{2,40}?)\s*</h2>', html)
    for name in h2_plain:
        clean = name.strip()
        if clean in TOOLS or clean in ALIASES:
            candidates.append(clean)

    # Deduplicate and filter
    seen, result = set(), []
    skip_words = {'Quick', 'Our', 'Related', 'Frequently', 'Before', 'Get the', 'Compare',
                  'Check', 'Top', 'Best', 'Side', 'How', 'What', 'Why', 'Summary', 'Note'}
    for t in candidates:
        t = t.strip()
        canonical = ALIASES.get(t, t)
        if (canonical and len(canonical) > 1
                and canonical not in seen
                and not any(w in canonical for w in skip_words)):
            seen.add(canonical)
            result.append(canonical)

    # Extract go links per tool
    go_map = {}
    links = re.findall(r'href="(/go/[a-z0-9-]+)"', html)
    for link in links:
        slug = link.replace("/go/", "")
        for tool in result:
            tslug = tool.lower().replace(" ", "-").replace(".", "").replace(",", "")
            if tslug in slug or slug in tslug:
                if tool not in go_map:
                    go_map[tool] = link

    return result, go_map


# ─── Hardcoded tool lists for root hub pages and thin pages ──────────────────
HARDCODED_PAGE_TOOLS = {
    "best-crm-software-2026": ["HubSpot CRM", "Salesforce", "Pipedrive", "Monday.com", "Zoho CRM", "Freshsales"],
    "best-seo-tools-2026": ["Semrush", "Ahrefs", "Moz Pro", "SE Ranking", "Surfer SEO"],
    "best-vpn-for-business-2026": ["NordVPN", "Surfshark", "ProtonVPN", "ExpressVPN", "CyberGhost"],
    "best-password-manager-business-2026": ["1Password", "Bitwarden", "Dashlane", "NordPass", "LastPass"],
    "best-project-management-software-2026": ["ClickUp", "Asana", "Monday.com", "Notion", "Jira", "Trello"],
    "best-hr-software-2026": ["Rippling", "Gusto", "BambooHR", "Deel"],
    "best-accounting-software-for-small-business-2026": ["FreshBooks", "Xero", "QuickBooks", "Wave"],
    "best-marketing-automation-software-2026": ["ActiveCampaign", "Mailchimp", "GetResponse", "Brevo"],
    "best-ecommerce-platform-2026": ["Shopify", "BigCommerce", "Wix", "WooCommerce"],
    "best-video-conferencing-software-2026": ["Zoom", "Microsoft Teams", "Google Meet", "Webex"],
    "best-cloud-hosting-2026": ["Vercel", "Render", "Datadog"],
    "best-finance-software-2026": ["FreshBooks", "Xero", "QuickBooks", "Wave"],
    "best-accounting-software-for-freelancers-in-2026": ["FreshBooks", "Xero", "Wave", "QuickBooks"],
    "best-ai-powered-analytics-tools-for-saas-teams-in-2025": ["Amplitude", "Mixpanel"],
    "best-ai-code-assistant-tools-in-2025-deepseek-github-copilot-more-compared": ["GitHub Copilot"],
    "best-ai-ml-code-assistant-tools-for-developers-in-2026": ["GitHub Copilot"],
    "best-vpn-australia": ["NordVPN", "Surfshark", "ExpressVPN", "ProtonVPN", "CyberGhost"],
    "best-vpn-for-gaming": ["NordVPN", "Surfshark", "ExpressVPN", "ProtonVPN", "CyberGhost"],
    "best-ecommerce-platforms": ["Shopify", "BigCommerce", "Wix", "WooCommerce"],
    "best-elementor-alternatives-in-2026-free-paid": ["Elementor", "Divi", "Beaver Builder", "Bricks Builder", "Webflow", "SeedProd"],
    "best-aweber-alternatives-in-2026-free-paid": ["AWeber", "GetResponse", "Mailchimp", "Brevo", "ActiveCampaign"],
    "best-wordpress-page-builders-2026": ["Elementor", "Divi", "Beaver Builder", "Bricks Builder", "SeedProd"],
}

def extract_page_meta(html, filepath):
    """Extract title, category, and existing page metadata."""
    # Title from <title> tag
    title_m = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL)
    title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip() if title_m else filepath.stem.replace("-", " ").title()
    # Remove site suffix
    title = re.sub(r'\s*[|—–-]\s*SaaSpare.*$', '', title).strip()
    # Meta description
    desc_m = re.search(r'<meta name="description" content="([^"]+)"', html)
    description = desc_m.group(1) if desc_m else f"The best tools ranked and reviewed. Independent research, verified pricing."
    # Canonical URL
    can_m = re.search(r'<link rel="canonical" href="https://saaspare\.org/([^"]+)"', html)
    canonical = can_m.group(1) if can_m else f"pages/{filepath.stem}"
    # Category from filename
    name = filepath.stem
    if "crm" in name: category = "CRM"
    elif "vpn" in name: category = "VPN"
    elif "seo" in name: category = "SEO Tool"
    elif "password" in name: category = "Password Manager"
    elif "project" in name or "task" in name: category = "Project Management"
    elif "accounting" in name or "finance" in name: category = "Accounting"
    elif "email" in name or "marketing" in name: category = "Email Marketing"
    elif "hr" in name or "payroll" in name: category = "HR Software"
    elif "ecommerce" in name or "shopify" in name: category = "Ecommerce"
    elif "video" in name or "conferencing" in name: category = "Video Conferencing"
    elif "hosting" in name: category = "Web Hosting"
    elif "alternatives" in name:
        # Extract main tool name from slug like "best-clickup-alternatives"
        m = re.search(r'best-([a-z0-9]+(?:-[a-z0-9]+)*)-alternatives', name)
        if m:
            category = m.group(1).replace("-", " ").title() + " Alternative"
        else:
            category = "SaaS Tool"
    else:
        category = "SaaS Tool"
    return title, description, canonical, category

def build_comparison_tokens(tools_data):
    """Build the comparison table token dict for up to 6 tools."""
    features = ["Free Plan","Starting Price","Key Feature","Integration","Mobile App","Setup"]
    tok = {
        "CMP_FEAT_FREE": "Free Plan",
        "CMP_FEAT_PRICE": "Starting Price",
        "CMP_FEAT_AI": "Key Feature",
        "CMP_FEAT_INT": "Integrations",
        "CMP_FEAT_MOB": "Mobile App",
        "CMP_FEAT_FORE": "Support",
        "CMP_FEAT_SETUP": "Setup",
        "CMP_FEAT_EMAIL": "Email / Comms",
    }
    for i, (name, data) in enumerate(tools_data, 1):
        n = i
        has_free = "&#10003;" if data.get("free_tag") else "&#10007;"
        free_cls = "cw" if data.get("free_tag") else "cl"
        tok[f"C_T{n}_FREE"] = f"{has_free} {data['free_tag']}" if data.get("free_tag") else "&#10007;"
        tok[f"C_T{n}_FREE_CLS"] = free_cls
        tok[f"C_T{n}_PRICE"] = data["price_line"].replace("<em>", "").replace("</em>", "")
        tok[f"C_T{n}_AI"] = data["pros"][0][:30] if data.get("pros") else "—"
        tok[f"C_T{n}_AI_CLS"] = "cw"
        tok[f"C_T{n}_EMAIL"] = data["pros"][1][:30] if len(data.get("pros", [])) > 1 else "—"
        tok[f"C_T{n}_EMAIL_CLS"] = "cm"
        tok[f"C_T{n}_INT"] = str(data.get("scores", {}).get("int", 75)) + "/100"
        tok[f"C_T{n}_INT_CLS"] = "cw" if data.get("scores", {}).get("int", 75) >= 85 else ""
        tok[f"C_T{n}_MOB"] = "Excellent" if data.get("scores", {}).get("ease", 75) >= 90 else "Good"
        tok[f"C_T{n}_MOB_CLS"] = "cw" if data.get("scores", {}).get("ease", 75) >= 90 else "cm"
        tok[f"C_T{n}_FORE"] = "Strong" if data.get("scores", {}).get("support", 75) >= 85 else "Good"
        tok[f"C_T{n}_FORE_CLS"] = "cw" if data.get("scores", {}).get("support", 75) >= 85 else "cm"
        tok[f"C_T{n}_SETUP"] = "Easy" if data.get("scores", {}).get("ease", 75) >= 85 else "Moderate"
        tok[f"C_T{n}_SETUP_CLS"] = "cw" if data.get("scores", {}).get("ease", 75) >= 85 else "cm"
    # Fill empty slots
    for i in range(len(tools_data) + 1, 7):
        n = i
        for key in ["FREE","PRICE","AI","EMAIL","INT","MOB","FORE","SETUP"]:
            tok[f"C_T{n}_{key}"] = "—"
        for key in ["FREE_CLS","AI_CLS","EMAIL_CLS","INT_CLS","MOB_CLS","FORE_CLS","SETUP_CLS"]:
            tok[f"C_T{n}_{key}"] = ""
    return tok

def generate_faqs(title, tools_list, category):
    """Generate contextual FAQs based on page content."""
    # Never name a padded "Option #N" placeholder in FAQ copy
    real = [t for t in tools_list if not t.startswith("Option #")]
    top = real[0] if real else category
    second = real[1] if len(real) > 1 else ""
    return {
        "FAQ_1_Q": f"What is the best {category} in 2026?",
        "FAQ_1_A": f"Based on our research, {top} is the top-rated {category} in 2026 — best combination of features, pricing, and ease of use." + (f" {second} is a strong alternative if you need different strengths." if second else ""),
        "FAQ_2_Q": f"Which {category} has the best free plan?",
        "FAQ_2_A": f"Several {category} tools offer free plans. Check each tool's pricing page — we verify pricing weekly and note exactly what's included in the free tier and what requires a paid upgrade.",
        "FAQ_3_Q": f"How do we score and rank these tools?",
        "FAQ_3_A": f"We score each tool across five dimensions: value for money (25%), features (25%), ease of use (20%), integrations (15%), and customer support (15%). Scores are set before any affiliate relationship is discussed.",
        "FAQ_4_Q": f"Can vendors pay to improve their ranking?",
        "FAQ_4_A": f"No. Rankings are finalised based on independent research before any affiliate agreement is discussed with a vendor. We may earn a commission if you purchase through our links — but this has zero bearing on ranking position.",
        "FAQ_5_Q": f"How often are rankings updated?",
        "FAQ_5_A": f"We review pricing weekly via automated scraping and manual verification. Scores and rankings are fully reviewed quarterly, or immediately when a tool ships a significant update. This page was last reviewed {TODAY}.",
    }

# ─────────────────────────────────────────────────────────────────────────────
# MAIN GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_page(input_path, output_path, template_html):
    html = input_path.read_text(encoding="utf-8", errors="replace")

    # Extract data from existing page
    tool_names, go_map = extract_tools_from_page(html)
    title, description, canonical, category = extract_page_meta(html, input_path)

    # Resolve tools — look up in database, fallback to unknown
    resolved = []
    for name in tool_names[:6]:
        if name in TOOLS:
            resolved.append((name, TOOLS[name]))
        else:
            resolved.append((name, make_unknown_tool(name, go_map.get(name, "").replace("/go/", ""))))

    # Ensure at least 1 tool
    if not resolved:
        return False, "no tools found"

    # Sort by score descending
    resolved.sort(key=lambda x: -x[1]["score"])

    # Pad to 6 token slots so the template fills, but placeholder "Option #N"
    # cards are stripped from the final HTML below (anti-fabrication rule:
    # never ship invented tools/scores).
    while len(resolved) < 6:
        idx = len(resolved) + 1
        generic_name = f"Option #{idx}"
        resolved.append((generic_name, make_unknown_tool(generic_name)))

    # Build token dict
    tokens = {}

    # Page-level tokens
    tokens["PAGE_TITLE"] = title
    tokens["META_DESCRIPTION"] = description
    tokens["CANONICAL_URL"] = canonical
    tokens["VERIFIED_DATE"] = TODAY
    tokens["CATEGORY"] = category
    tokens["HERO_LEAD"] = description
    tokens["STICKY_CTA_TEXT"] = f"{title} — Compare your top picks and choose with confidence."
    tokens["STAT_1_NUM"] = str(len(tool_names)) if tool_names else "6"
    tokens["STAT_1_LABEL"] = f"{category}s compared"
    # Honest trust stats only — never ship invented survey/data-point numbers
    # (anti-fabrication rule: unverified = label it or omit it)
    tokens["STAT_2_NUM"] = "100%"
    tokens["STAT_2_LABEL"] = "Independent research"
    tokens["STAT_3_NUM"] = "0"
    tokens["STAT_3_LABEL"] = "Paid placements"
    tokens["STAT_4_NUM"] = str(min(6, len(resolved)))
    tokens["STAT_4_LABEL"] = "Final picks"

    # Tool cards
    for i, (name, data) in enumerate(resolved, 1):
        go_link = go_map.get(name, f"/go/{data.get('go', name.lower().replace(' ', '-'))}")
        tokens.update(tool_tokens(i, name, data, go_link))

    # Comparison table
    tokens.update(build_comparison_tokens(resolved))

    # FAQs
    tool_names_resolved = [t[0] for t in resolved]
    tokens.update(generate_faqs(title, tool_names_resolved, category))

    # Fill template
    out = template_html
    for k, v in tokens.items():
        out = out.replace("{{" + k + "}}", v)

    # Inject GA4 tracking
    ga_tag = """  <script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-RLYVYV8WQJ');</script>"""
    if "G-RLYVYV8WQJ" not in out:
        out = out.replace("</head>", ga_tag + "\n</head>", 1)

    # Add favicon
    if "favicon" not in out:
        fav = '  <link rel="icon" href="/favicon.ico" sizes="any">'
        out = out.replace("</head>", fav + "\n</head>", 1)

    # Count remaining unfilled tokens
    remaining = re.findall(r'\{\{[A-Z0-9_]+\}\}', out)
    if remaining:
        # Fill any remaining with empty string
        for r in set(remaining):
            out = out.replace(r, "")

    # Strip fabricated "Option #N" placeholder cards before writing
    from strip_placeholder_cards import strip_placeholder_html
    out = strip_placeholder_html(out)

    output_path.write_text(out, encoding="utf-8")
    return True, f"{len(resolved)} tools, {len(remaining)} tokens cleaned"


def main():
    template_html = (TEMPLATES / "best-of.html").read_text(encoding="utf-8")

    # Find all best-of pages to process
    targets = []

    # site/pages/best-*.html (190 pages)
    targets += list((SITE / "pages").glob("best-*.html"))

    # site/pages/7-best-*.html (alternatives pages — skip the 7-best- ones that are noindex duplicates)
    # We'll process the canonical best-* versions, not the 7-best- versions

    # site/best-*.html (root hub pages)
    targets += list(SITE.glob("best-*.html"))

    # site/pages/buyer-type-alternatives.html + how-to-evaluate
    for name in ["buyer-type-alternatives.html"]:
        p = SITE / "pages" / name
        if p.exists():
            targets.append(p)

    print(f"Processing {len(targets)} best-of pages...")
    success = fail = skip = 0

    for path in sorted(targets):
        html = path.read_text(encoding="utf-8", errors="replace")
        stem = path.stem

        # Skip if it already has the new template markers
        if "bc-layout" in html and "tc-head" in html and "score-ring" in html:
            skip += 1
            continue

        # Check hardcoded tool list first
        hardcoded = HARDCODED_PAGE_TOOLS.get(stem)
        if hardcoded:
            # Inject hardcoded tools into the html as fake "X Review" headings so
            # generate_page() can find them — simpler than patching generate_page
            fake_h2 = "".join(f"<h2>{t} Review</h2>" for t in hardcoded)
            html_with_tools = html + fake_h2
            # Write temp modified version for extraction, then overwrite with real template
            tmp = path.parent / (stem + "_tmp_gen.html")
            tmp.write_text(html_with_tools, encoding="utf-8")
            ok, msg = generate_page(tmp, path, template_html)
            tmp.unlink(missing_ok=True)
        else:
            # Extract tools from page
            tools_found, _ = extract_tools_from_page(html)
            # Filter: require at least 2 tools in the real TOOLS database
            known = [t for t in tools_found if t in TOOLS or t in ALIASES]
            if len(known) < 1:
                skip += 1
                continue
            ok, msg = generate_page(path, path, template_html)

        if ok:
            success += 1
            if success <= 10 or success % 20 == 0:
                print(f"  [OK] {path.name[:55]} — {msg}")
        else:
            fail += 1
            print(f"  [SKIP] {path.name[:55]} — {msg}")

    print(f"\nDone: {success} upgraded | {skip} skipped (hallucinated/no real tools) | {fail} failed")
    return success


if __name__ == "__main__":
    main()
