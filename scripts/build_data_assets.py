#!/usr/bin/env python3
"""Build SaaS Pricing Index and Free Trial Database data asset pages."""
import os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES_DIR = ROOT / "site" / "pages"
sys.path.insert(0, str(ROOT))

GA4 = '<script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>\n<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","G-RLYVYV8WQJ");</script>'
ADS = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9433840442322701" crossorigin="anonymous"></script>'
CJ = '<script src="https://www.anrdoezrs.net/am/101733230/include/allCj/impressions/page/am.js"></script>'

NAV = """<nav id="nav">
  <a href="/" class="logo">
    <svg class="logo-mark" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/><path fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></svg>
    <span class="logo-text">Saa<em>Spare</em></span>
  </a>
  <a href="/pages/" class="nav-link">Comparisons</a>
  <a href="/categories" class="nav-link">Categories</a>
  <a href="/shortlist" class="nav-link">Shortlist Builder</a>
  <a href="/deal-radar" class="nav-link">Deal Radar</a>
  <a href="/about" class="nav-link">About</a>
  <a href="/shortlist" class="nav-cta">Build Shortlist &#8594;</a>
</nav>"""

FOOTER = """<footer>
  <div class="fi"><div class="fb"><div class="fl"><svg style="height:22px;width:auto" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg"><path fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/><path fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></svg><span style="font-weight:800;font-size:.92rem;color:#fff">Saa<em style="color:#e94560;font-style:normal">Spare</em></span></div><p>Unbiased B2B SaaS comparisons for founders, CTOs and operators.</p></div>
  <div class="fc"><h4>Compare</h4><a href="/pages/">All Comparisons</a><a href="/categories">Categories</a><a href="/pages/?q=crm">CRM Tools</a><a href="/pages/?q=seo">SEO Software</a></div>
  <div class="fc"><h4>Data</h4><a href="/pages/saas-pricing-index">Pricing Index</a><a href="/pages/free-trial-database">Free Trial DB</a><a href="/pages/?type=pricing">Pricing Guides</a><a href="/pages/?type=alternatives">Alternatives</a></div>
  <div class="fc"><h4>Company</h4><a href="/about">About</a><a href="/methodology">Methodology</a><a href="/contact">Contact</a><a href="/affiliate-disclosure">Disclosure</a></div></div>
  <div class="fb2"><span>&copy; 2026 SaaSpare &middot; <a href="/affiliate-disclosure">Affiliate Disclosure</a></span><span>This site contains affiliate links. We may earn a commission at no extra cost to you.</span></div>
</footer>"""

SHARED_CSS = """<style>
:root{--bg:#07070d;--red:#e94560;--red2:#c73652;--text:rgba(255,248,245,.88);--muted:rgba(255,248,245,.42);--dim:rgba(255,248,245,.16);--border:rgba(255,255,255,.07);--card:rgba(255,255,255,.038)}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:"Plus Jakarta Sans",system-ui,sans-serif;background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased;overflow-x:hidden}
a{text-decoration:none;color:inherit}
::-webkit-scrollbar{width:4px;background:rgba(255,255,255,.02)}
::-webkit-scrollbar-thumb{background:rgba(233,69,96,.4);border-radius:2px}
nav{position:fixed;top:0;left:0;right:0;z-index:200;padding:1rem 2rem;display:flex;align-items:center;gap:4px;transition:all .4s ease}
nav.scrolled{background:rgba(7,7,13,.82);border-bottom:1px solid var(--border);backdrop-filter:blur(20px)}
.logo{display:flex;align-items:center;gap:9px;margin-right:auto}
.logo-mark{height:26px;width:auto;flex-shrink:0;overflow:visible}
.logo-text{font-weight:800;font-size:1.05rem;letter-spacing:-.4px;color:#fff}
.logo-text em{color:var(--red);font-style:normal}
.nav-link{color:var(--muted);font-size:.8rem;padding:.38rem .82rem;border-radius:8px;font-weight:500;transition:color .18s;white-space:nowrap}
.nav-link:hover{color:#fff}
.nav-cta{background:linear-gradient(135deg,var(--red),var(--red2));color:#fff;padding:.44rem 1.15rem;border-radius:100px;font-weight:700;font-size:.78rem;margin-left:6px}
.ph{padding:8.5rem 2rem 5rem;text-align:center;background:radial-gradient(ellipse 90% 60% at 50% -5%,rgba(90,16,28,.95),transparent 58%),var(--bg)}
.ew{display:inline-flex;align-items:center;gap:8px;background:rgba(233,69,96,.1);border:1px solid rgba(233,69,96,.24);color:rgba(255,185,200,.9);padding:5px 14px;border-radius:100px;font-size:.68rem;font-weight:700;letter-spacing:.5px;text-transform:uppercase;margin-bottom:1.5rem}
.ph h1{font-size:clamp(2rem,5vw,3.2rem);font-weight:900;color:#fff;letter-spacing:-.05em;line-height:1.12;margin-bottom:1rem}
.ph p{color:var(--muted);font-size:.98rem;line-height:1.8;max-width:600px;margin:0 auto 1.5rem}
.ph-stats{display:flex;gap:2rem;justify-content:center;flex-wrap:wrap;margin-top:1.5rem}
.ph-stat{background:rgba(255,255,255,.05);border:1px solid var(--border);border-radius:12px;padding:.6rem 1.4rem;font-size:.8rem}
.ph-stat strong{color:#fff;font-weight:800;display:block;font-size:1.1rem}
.content{max-width:1200px;margin:0 auto;padding:3rem clamp(1.5rem,4vw,3rem) 7rem}
.sec-ew{font-size:.62rem;font-weight:700;color:var(--red);letter-spacing:1.2px;text-transform:uppercase;margin-bottom:.5rem;display:block}
.sec-title{font-size:clamp(1.3rem,2.5vw,1.7rem);font-weight:900;color:#fff;letter-spacing:-.04em;margin-bottom:1.5rem}
.data-table{width:100%;border-collapse:collapse;margin-top:1rem;font-size:.85rem}
.data-table th{padding:.75rem 1rem;text-align:left;font-size:.7rem;font-weight:700;color:var(--dim);letter-spacing:.8px;text-transform:uppercase;border-bottom:1px solid var(--border)}
.data-table td{padding:.85rem 1rem;border-bottom:1px solid rgba(255,255,255,.04);vertical-align:middle}
.data-table tr:hover td{background:rgba(255,255,255,.02)}
.data-table a{color:var(--red);font-weight:600}
.badge{display:inline-flex;padding:2px 8px;border-radius:100px;font-size:.7rem;font-weight:700}
.badge.green{background:rgba(101,214,163,.12);color:#65d6a3;border:1px solid rgba(101,214,163,.25)}
.badge.red{background:rgba(233,69,96,.12);color:#e94560;border:1px solid rgba(233,69,96,.25)}
.badge.gray{background:rgba(255,255,255,.06);color:var(--muted);border:1px solid var(--border)}
.badge.blue{background:rgba(96,165,250,.1);color:#60a5fa;border:1px solid rgba(96,165,250,.2)}
.filter-wrap{display:flex;gap:.75rem;flex-wrap:wrap;margin-bottom:1.5rem;align-items:center}
.filter-input{background:rgba(255,255,255,.06);border:1px solid var(--border);border-radius:100px;padding:.5rem 1.2rem;font-size:.85rem;color:#fff;outline:none;font-family:inherit;min-width:220px}
.filter-input::placeholder{color:var(--dim)}
.filter-input:focus{border-color:rgba(233,69,96,.4)}
.filter-btn{background:rgba(233,69,96,.1);border:1px solid rgba(233,69,96,.2);color:rgba(255,185,200,.9);border-radius:100px;padding:.4rem .9rem;font-size:.75rem;font-weight:600;cursor:pointer;font-family:inherit;transition:all .2s}
.filter-btn:hover,.filter-btn.active{background:rgba(233,69,96,.22);border-color:rgba(233,69,96,.4)}
.note{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1rem 1.3rem;font-size:.82rem;color:var(--muted);line-height:1.7;margin-top:2rem}
.note strong{color:rgba(255,255,255,.7)}
.note a{color:var(--red)}
footer{border-top:1px solid var(--border)}
.fi{max-width:1300px;margin:0 auto;padding:3.5rem clamp(1.5rem,4vw,3rem) 2.5rem;display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:3rem}
.fb p{font-size:.8rem;color:rgba(255,255,255,.24);line-height:1.75;max-width:220px;margin-top:.75rem}
.fl{display:flex;align-items:center;gap:8px;margin-bottom:.65rem}
.fc h4{font-size:.62rem;font-weight:700;color:rgba(255,255,255,.22);letter-spacing:.9px;text-transform:uppercase;margin-bottom:.9rem}
.fc a{display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;transition:color .18s}
.fc a:hover{color:#fff}
.fb2{max-width:1300px;margin:0 auto;padding:1.25rem clamp(1.5rem,4vw,3rem);border-top:1px solid rgba(255,255,255,.04);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.5rem;font-size:.72rem;color:rgba(255,255,255,.18)}
.fb2 a{color:rgba(255,255,255,.24)}
@media(max-width:768px){nav{padding:.8rem 1.2rem}.nav-link{display:none}.data-table{font-size:.78rem}}
@media(max-width:640px){.fi{grid-template-columns:1fr 1fr;gap:2rem}}
@media(max-width:480px){.fi{grid-template-columns:1fr}}
</style>"""

SCROLL_JS = """<script>window.addEventListener("scroll",function(){document.getElementById("nav").classList.toggle("scrolled",window.scrollY>40);},{passive:true});</script>"""

# --- DATA: Tool pricing and trials ---
TOOLS = [
    # (slug, name, category, free_plan, trial_days, card_required, starter_price, notes)
    ("hubspot", "HubSpot", "CRM", True, 14, False, "$0–$20/mo", "Free CRM tier; paid starts $20/seat/mo"),
    ("salesforce", "Salesforce", "CRM", False, 30, True, "$25/user/mo", "Essentials plan; free trial with card"),
    ("pipedrive", "Pipedrive", "CRM", False, 14, False, "$14/user/mo", "Essential plan; no card for trial"),
    ("notion", "Notion", "PM", True, 0, False, "$0–$10/mo", "Free forever for individuals"),
    ("monday-com", "Monday.com", "PM", True, 14, False, "$9/seat/mo", "Free 2-seat plan; 14-day paid trial"),
    ("asana", "Asana", "PM", True, 30, False, "$0–$10.99/mo", "Free plan up to 10 users"),
    ("clickup", "ClickUp", "PM", True, 0, False, "$0–$7/mo", "Generous free plan with unlimited tasks"),
    ("linear", "Linear", "Dev", True, 0, False, "$0–$8/user/mo", "Free for small teams"),
    ("datadog", "Datadog", "Dev", False, 14, True, "$15/host/mo", "Infrastructure monitoring starting price"),
    ("sentry", "Sentry", "Dev", True, 0, False, "$0–$26/mo", "Free developer plan available"),
    ("ahrefs", "Ahrefs", "SEO", False, 0, False, "$29/mo", "Starter plan; free limited tools"),
    ("semrush", "Semrush", "SEO", False, 7, True, "$139.95/mo", "Pro plan; 7-day money back"),
    ("moz", "Moz", "SEO", False, 30, True, "$49/mo", "Standard plan; 30-day free trial"),
    ("surfer-seo", "Surfer SEO", "SEO", False, 7, True, "$79/mo", "Essential plan"),
    ("rippling", "Rippling", "HR", False, 0, True, "Custom", "Custom pricing; demo required"),
    ("deel", "Deel", "HR", False, 0, False, "$49/mo", "EOR contractor plan"),
    ("bamboohr", "BambooHR", "HR", False, 7, False, "Custom", "SMB HR; 7-day trial"),
    ("gusto", "Gusto", "HR", False, 1, False, "$40+$6/mo", "Simple plan payroll; 1-month trial"),
    ("xero", "Xero", "Finance", False, 30, False, "$15/mo", "Starter plan; 30-day trial no card"),
    ("quickbooks", "QuickBooks", "Finance", False, 30, True, "$30/mo", "Simple Start; 30-day trial"),
    ("freshbooks", "FreshBooks", "Finance", False, 30, False, "$17/mo", "Lite plan; 30-day free trial"),
    ("ramp", "Ramp", "Finance", True, 0, False, "$0", "Free spend management platform"),
    ("brex", "Brex", "Finance", True, 0, False, "$0–$12/mo", "Free Essentials; premium plans available"),
    ("shopify", "Shopify", "Ecommerce", False, 3, False, "$29/mo", "Basic plan; 3-day free trial"),
    ("1password", "1Password", "Security", False, 14, True, "$2.99/mo", "Individual plan; 14-day trial"),
    ("bitwarden", "Bitwarden", "Security", True, 0, False, "$0–$3/mo", "Free personal plan available"),
    ("okta", "Okta", "Security", False, 30, False, "Custom", "Enterprise pricing; 30-day trial"),
    ("nordlayer", "NordLayer", "Security", False, 14, True, "$7/user/mo", "Basic plan; 14-day trial"),
    ("docusign", "DocuSign", "Legal", False, 30, True, "$15/mo", "Personal plan; 30-day trial"),
    ("pandadoc", "PandaDoc", "Legal", True, 14, False, "$0–$19/mo", "Free eSign plan available"),
    ("jasper-ai", "Jasper AI", "AI", False, 7, True, "$39/mo", "Creator plan; 7-day trial"),
    ("copy-ai", "Copy.ai", "AI", True, 0, False, "$0–$36/mo", "Free plan with 2k words/mo"),
    ("mailchimp", "Mailchimp", "Marketing", True, 0, False, "$0–$13/mo", "Free up to 500 contacts"),
    ("activecampaign", "ActiveCampaign", "Marketing", False, 14, False, "$15/mo", "Starter plan; 14-day trial"),
    ("klaviyo", "Klaviyo", "Marketing", True, 0, False, "$0–$20/mo", "Free up to 250 contacts"),
    ("mixpanel", "Mixpanel", "Analytics", True, 0, False, "$0–$28/mo", "Free up to 20M events/mo"),
    ("amplitude", "Amplitude", "Analytics", True, 0, False, "$0–$49/mo", "Free Starter plan"),
    ("hotjar", "Hotjar", "Analytics", True, 0, False, "$0–$32/mo", "Basic free plan available"),
    ("cloudflare", "Cloudflare", "Cloud", True, 0, False, "$0–$20/mo", "Free CDN/DNS; Pro $20/mo"),
    ("vercel", "Vercel", "Cloud", True, 0, False, "$0–$20/mo", "Hobby free; Pro $20/mo"),
    ("digitalocean", "DigitalOcean", "Cloud", False, 0, True, "$4/mo", "Basic droplet; $200 credit for new"),
    ("supabase", "Supabase", "Cloud", True, 0, False, "$0–$25/mo", "Free tier available"),
]

# Build pricing index page
def build_pricing_index():
    rows = ""
    for slug, name, cat, free_plan, trial, card, price, notes in TOOLS:
        pricing_page = f"/pages/{slug}-pricing-2026-plans-costs-what-you-actually-pay"
        pricing_pages = [f for f in os.listdir(PAGES_DIR) if f.startswith(slug + "-pricing")]
        pricing_link = f"/pages/{pricing_pages[0][:-5]}" if pricing_pages else pricing_page

        free_badge = '<span class="badge green">Free plan</span>' if free_plan else '<span class="badge gray">No free plan</span>'
        trial_badge = f'<span class="badge blue">{trial}-day trial</span>' if trial else '<span class="badge gray">No trial</span>'
        card_badge = '<span class="badge red">Card required</span>' if (trial and card) else ('<span class="badge green">No card needed</span>' if trial else "")

        rows += f"""<tr data-cat="{cat.lower()}" data-name="{name.lower()}" data-free="{'yes' if free_plan else 'no'}">
  <td><a href="{pricing_link}">{name}</a></td>
  <td><span class="badge gray">{cat}</span></td>
  <td>{price}</td>
  <td>{free_badge}</td>
  <td>{trial_badge}{" " + card_badge if card_badge else ""}</td>
  <td style="font-size:.78rem;color:var(--muted)">{notes}</td>
</tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SaaS Pricing Index 2026: Starter Plan Costs for 40+ B2B Tools | SaaSpare</title>
<meta name="description" content="Compare starter plan pricing for 40+ B2B SaaS tools in 2026. See which tools have free plans, free trials, and what you actually pay. Updated monthly.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://saaspare.org/pages/saas-pricing-index">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta property="og:title" content="SaaS Pricing Index 2026: Starter Plan Costs for 40+ B2B Tools">
<meta property="og:description" content="Compare starter plan pricing for 40+ B2B SaaS tools in 2026. Free plans, free trials, and what you actually pay.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://saaspare.org/pages/saas-pricing-index">
<meta property="og:image" content="https://saaspare.org/og-default.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<meta name="google-adsense-account" content="ca-pub-9433840442322701">
{ADS}
{GA4}
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Dataset","name":"SaaS Pricing Index 2026","description":"Starter plan pricing, free plan availability, and trial conditions for 40+ major B2B SaaS tools tracked by SaaSpare.","url":"https://saaspare.org/pages/saas-pricing-index","creator":{{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"}},"dateModified":"2026-05-02","license":"https://creativecommons.org/licenses/by/4.0/"}}</script>
{SHARED_CSS}
</head>
<body>
{NAV}

<div class="ph">
  <span class="ew">&#128202; Data Asset</span>
  <h1>SaaS Pricing Index 2026</h1>
  <p>Starter plan costs, free plan availability, and trial conditions for 40+ major B2B SaaS tools. Updated monthly. Free to share with attribution.</p>
  <div class="ph-stats">
    <div class="ph-stat"><strong>{len(TOOLS)}</strong>Tools tracked</div>
    <div class="ph-stat"><strong>{sum(1 for t in TOOLS if t[2])}</strong>With free plans</div>
    <div class="ph-stat"><strong>{sum(1 for t in TOOLS if t[3])}</strong>With free trials</div>
    <div class="ph-stat"><strong>May 2026</strong>Last updated</div>
  </div>
</div>

<main class="content">

  <div class="filter-wrap">
    <input class="filter-input" type="text" id="pi-search" placeholder="Search tools..." oninput="filterTable()">
    <button class="filter-btn" onclick="setFilter('all')">All</button>
    <button class="filter-btn" onclick="setFilter('crm')">CRM</button>
    <button class="filter-btn" onclick="setFilter('seo')">SEO</button>
    <button class="filter-btn" onclick="setFilter('pm')">PM</button>
    <button class="filter-btn" onclick="setFilter('hr')">HR</button>
    <button class="filter-btn" onclick="setFilter('finance')">Finance</button>
    <button class="filter-btn" onclick="setFilter('dev')">Dev</button>
    <button class="filter-btn" onclick="setFilter('security')">Security</button>
    <button class="filter-btn free-only" onclick="setFreeFilter()">Free plan only</button>
  </div>

  <table class="data-table" id="pricing-table">
    <thead><tr>
      <th>Tool</th><th>Category</th><th>Starter price</th><th>Free plan</th><th>Trial</th><th>Notes</th>
    </tr></thead>
    <tbody id="pt-body">{rows}</tbody>
  </table>

  <div class="note">
    <strong>Data notes:</strong> Prices shown are publicly listed starter plan costs in USD, accurate as of May 2026. Actual pricing may vary by region, negotiation, or plan changes. Always verify on the vendor website before purchasing. Some tools offer annual discounts of 10&ndash;25% not reflected in monthly prices shown.<br><br>
    <strong>Free to cite:</strong> This dataset is free to use with attribution. Link back to <a href="https://saaspare.org/pages/saas-pricing-index">saaspare.org/pages/saas-pricing-index</a>. For corrections or additions, <a href="/contact">contact us</a>.
  </div>

  <div style="margin-top:3rem;padding-top:2rem;border-top:1px solid var(--border)">
    <span class="sec-ew">Related resources</span>
    <h2 class="sec-title">Explore individual tool pricing</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:.65rem;margin-top:1rem">
      {"".join(f'<a href="/pages/{slug}-pricing-2026-plans-costs-what-you-actually-pay" style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:.7rem .9rem;font-size:.82rem;color:rgba(255,255,255,.7);transition:border-color .2s" onmouseover="this.style.borderColor=\'rgba(233,69,96,.3)\'" onmouseout="this.style.borderColor=\'rgba(255,255,255,.07)\'">{name} Pricing</a>' for slug, name, *_ in TOOLS[:20] if (PAGES_DIR / f"{slug}-pricing-2026-plans-costs-what-you-actually-pay.html").exists())}
    </div>
  </div>

</main>

{FOOTER}

{SCROLL_JS}
<script>
var curCat="all",freeOnly=false;
function filterTable(){{
  var q=document.getElementById("pi-search").value.toLowerCase();
  document.querySelectorAll("#pt-body tr").forEach(function(r){{
    var name=r.dataset.name||"";
    var cat=r.dataset.cat||"";
    var free=r.dataset.free||"";
    var catOk=curCat==="all"||cat===curCat;
    var freeOk=!freeOnly||free==="yes";
    var qOk=!q||name.includes(q);
    r.style.display=(catOk&&freeOk&&qOk)?"":"none";
  }});
}}
function setFilter(c){{
  curCat=c;freeOnly=false;
  document.querySelectorAll(".filter-btn").forEach(function(b){{b.classList.remove("active")}});
  event.target.classList.add("active");
  filterTable();
}}
function setFreeFilter(){{
  freeOnly=!freeOnly;event.target.classList.toggle("active",freeOnly);filterTable();
}}
</script>
{CJ}
</body>
</html>"""


# Build free trial database page
def build_free_trial_db():
    trial_tools = [(s, n, c, fp, t, cr, p, nt) for s, n, c, fp, t, cr, p, nt in TOOLS if t > 0]

    rows = ""
    for slug, name, cat, free_plan, trial, card, price, notes in sorted(trial_tools, key=lambda x: -x[4]):
        trial_pages = [f for f in os.listdir(PAGES_DIR) if f.startswith(slug + "-free-trial")]
        trial_link = f"/pages/{trial_pages[0][:-5]}" if trial_pages else f"/pages/{slug}-free-trial-2026-how-to-get-it-step-by-step"

        card_badge = '<span class="badge red">Card required</span>' if card else '<span class="badge green">No card needed</span>'
        free_badge = '<span class="badge green">Yes</span>' if free_plan else '<span class="badge gray">No</span>'

        rows += f"""<tr data-cat="{cat.lower()}" data-name="{name.lower()}" data-card="{'yes' if card else 'no'}">
  <td><a href="{trial_link}">{name}</a></td>
  <td><span class="badge gray">{cat}</span></td>
  <td><strong>{trial} days</strong></td>
  <td>{card_badge}</td>
  <td>{free_badge}</td>
  <td style="font-size:.78rem;color:var(--muted)">{notes}</td>
</tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SaaS Free Trial Database 2026: Which Tools Offer Real Free Trials? | SaaSpare</title>
<meta name="description" content="The complete database of B2B SaaS free trials in 2026. See trial length, whether a credit card is required, and whether a free plan exists. Updated monthly.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://saaspare.org/pages/free-trial-database">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta property="og:title" content="SaaS Free Trial Database 2026: Which Tools Offer Real Free Trials?">
<meta property="og:description" content="Trial length, credit card requirements, and free plan availability for 30+ B2B SaaS tools. Updated monthly by SaaSpare.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://saaspare.org/pages/free-trial-database">
<meta property="og:image" content="https://saaspare.org/og-default.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<meta name="google-adsense-account" content="ca-pub-9433840442322701">
{ADS}
{GA4}
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Dataset","name":"SaaS Free Trial Database 2026","description":"Free trial length, credit card requirements, and free plan availability for major B2B SaaS tools tracked by SaaSpare.","url":"https://saaspare.org/pages/free-trial-database","creator":{{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"}},"dateModified":"2026-05-02"}}</script>
{SHARED_CSS}
</head>
<body>
{NAV}

<div class="ph">
  <span class="ew">&#128202; Data Asset</span>
  <h1>SaaS Free Trial Database 2026</h1>
  <p>Which B2B SaaS tools offer real free trials in 2026? Trial length, credit card requirements, and whether a free plan exists &mdash; all in one place. Updated monthly.</p>
  <div class="ph-stats">
    <div class="ph-stat"><strong>{len(trial_tools)}</strong>Tools with trials</div>
    <div class="ph-stat"><strong>{sum(1 for t in trial_tools if not t[5])}</strong>No card needed</div>
    <div class="ph-stat"><strong>{sum(1 for t in trial_tools if t[4] >= 30)}</strong>30-day trials</div>
    <div class="ph-stat"><strong>May 2026</strong>Last updated</div>
  </div>
</div>

<main class="content">

  <div class="filter-wrap">
    <input class="filter-input" type="text" id="ft-search" placeholder="Search tools..." oninput="filterFT()">
    <button class="filter-btn" onclick="setFTFilter('all')">All</button>
    <button class="filter-btn" onclick="setFTFilter('crm')">CRM</button>
    <button class="filter-btn" onclick="setFTFilter('seo')">SEO</button>
    <button class="filter-btn" onclick="setFTFilter('pm')">PM</button>
    <button class="filter-btn" onclick="setFTFilter('hr')">HR</button>
    <button class="filter-btn" onclick="setFTFilter('finance')">Finance</button>
    <button class="filter-btn nocard-only" onclick="setNoCard()">No card required</button>
  </div>

  <table class="data-table" id="ft-table">
    <thead><tr>
      <th>Tool</th><th>Category</th><th>Trial length</th><th>Credit card</th><th>Free plan</th><th>Notes</th>
    </tr></thead>
    <tbody id="ft-body">{rows}</tbody>
  </table>

  <div class="note">
    <strong>How to use this database:</strong> Click any tool name to see the full free trial guide including how to claim it, what happens when it ends, and the best alternatives if it doesn&rsquo;t fit.<br><br>
    <strong>Free to cite:</strong> This data is free to use with attribution. Link back to <a href="https://saaspare.org/pages/free-trial-database">saaspare.org/pages/free-trial-database</a>. For corrections, <a href="/contact">contact us</a>.
  </div>

  <div style="margin-top:3rem;padding-top:2rem;border-top:1px solid var(--border)">
    <span class="sec-ew">Get the trial guide</span>
    <h2 class="sec-title">Step-by-step trial guides</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:.65rem;margin-top:1rem">
      {"".join(f'<a href="/pages/{slug}-free-trial-2026-how-to-get-it-step-by-step" style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:.7rem .9rem;font-size:.82rem;color:rgba(255,255,255,.7);transition:border-color .2s" onmouseover="this.style.borderColor=\'rgba(233,69,96,.3)\'" onmouseout="this.style.borderColor=\'rgba(255,255,255,.07)\'">{name} Free Trial Guide</a>' for slug, name, *_ in trial_tools if (PAGES_DIR / f"{slug}-free-trial-2026-how-to-get-it-step-by-step.html").exists())}
    </div>
  </div>

</main>

{FOOTER}

{SCROLL_JS}
<script>
var ftCat="all",noCardOnly=false;
function filterFT(){{
  var q=document.getElementById("ft-search").value.toLowerCase();
  document.querySelectorAll("#ft-body tr").forEach(function(r){{
    var name=r.dataset.name||"";
    var cat=r.dataset.cat||"";
    var card=r.dataset.card||"";
    var catOk=ftCat==="all"||cat===ftCat;
    var cardOk=!noCardOnly||card==="no";
    var qOk=!q||name.includes(q);
    r.style.display=(catOk&&cardOk&&qOk)?"":"none";
  }});
}}
function setFTFilter(c){{
  ftCat=c;noCardOnly=false;
  document.querySelectorAll(".filter-btn").forEach(function(b){{b.classList.remove("active")}});
  event.target.classList.add("active");
  filterFT();
}}
function setNoCard(){{
  noCardOnly=!noCardOnly;event.target.classList.toggle("active",noCardOnly);filterFT();
}}
</script>
{CJ}
</body>
</html>"""


if __name__ == "__main__":
    pi_html = build_pricing_index()
    pi_path = PAGES_DIR / "saas-pricing-index.html"
    pi_path.write_text(pi_html, encoding="utf-8")
    print(f"Written: {pi_path} ({len(pi_html):,} chars)")

    ft_html = build_free_trial_db()
    ft_path = PAGES_DIR / "free-trial-database.html"
    ft_path.write_text(ft_html, encoding="utf-8")
    print(f"Written: {ft_path} ({len(ft_html):,} chars)")
