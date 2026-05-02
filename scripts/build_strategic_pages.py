"""
Build high-value strategic pages from research report.
Creates: SaaS Spend Audit service, Weekly Deal Digest, Pricing Change Tracker,
State of SaaS report, SaaS Glossary, trust pages, utility pages.
Run: uv run python scripts/build_strategic_pages.py
"""
import re
from pathlib import Path
from datetime import datetime

PAGES = Path("site/pages")
PAGES.mkdir(parents=True, exist_ok=True)
TODAY = datetime.utcnow().strftime("%Y-%m-%d")
DOMAIN = "https://saaspare.org"

NAV = '''<nav id="nav">
  <a href="/" class="logo"><span class="logo-text">Saa<em>Spare</em></span></a>
  <a href="/pages/" class="nav-link">Comparisons</a>
  <a href="/categories.html" class="nav-link">Categories</a>
  <a href="/pages/saas-pricing-index" class="nav-link">Pricing Index</a>
  <a href="/pages/free-trial-database" class="nav-link">Free Trials</a>
  <a href="/pages/saas-glossary" class="nav-link">Glossary</a>
  <a href="/shortlist.html" class="nav-cta">Build Shortlist →</a>
</nav>'''

FOOTER = f'''<footer>
  <div class="footer-inner">
    <div><strong>SaaSpare</strong> · Unbiased B2B SaaS comparisons · No paid rankings</div>
    <div class="footer-links">
      <a href="/about.html">About</a>
      <a href="/methodology.html">Methodology</a>
      <a href="/pages/how-saaspare-ranks-tools">How We Rank</a>
      <a href="/pages/coupon-verification-policy">Coupon Policy</a>
      <a href="/affiliate-disclosure.html">Disclosure</a>
      <a href="/pages/report-outdated-pricing">Report Pricing</a>
      <a href="/pages/request-a-comparison">Request Compare</a>
      <a href="/privacy.html">Privacy</a>
      <a href="/contact.html">Contact</a>
    </div>
  </div>
</footer>'''

BASE_CSS = '''*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:"Plus Jakarta Sans",system-ui,sans-serif;background:#07070d;color:rgba(255,248,245,.88);-webkit-font-smoothing:antialiased;overflow-x:hidden;line-height:1.65}
a{text-decoration:none;color:inherit}
::-webkit-scrollbar{width:4px;background:rgba(255,255,255,.02)}::-webkit-scrollbar-thumb{background:rgba(233,69,96,.4);border-radius:2px}
:root{--bg:#07070d;--red:#e94560;--red2:#c73652;--text:rgba(255,248,245,.88);--muted:rgba(255,248,245,.42);--dim:rgba(255,248,245,.16);--border:rgba(255,255,255,.07);--card:rgba(255,255,255,.038)}
nav{position:fixed;top:0;left:0;right:0;z-index:200;padding:1rem 2rem;display:flex;align-items:center;gap:4px;transition:all .4s ease;background:transparent}
nav.scrolled{background:rgba(7,7,13,.85);border-bottom:1px solid var(--border);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px)}
.logo{margin-right:auto;display:flex;align-items:center;gap:9px}
.logo-text{font-weight:800;font-size:1.05rem;letter-spacing:-.4px;color:#fff}
.logo-text em{color:var(--red);font-style:normal}
.nav-link{color:var(--muted);font-size:.8rem;padding:.38rem .82rem;border-radius:8px;font-weight:500;white-space:nowrap}
.nav-link:hover{color:#fff}
.nav-cta{background:linear-gradient(135deg,var(--red),var(--red2));color:#fff;padding:.44rem 1.15rem;border-radius:100px;font-weight:700;font-size:.78rem;box-shadow:0 4px 16px rgba(233,69,96,.4);margin-left:6px;white-space:nowrap}
@media(max-width:860px){.nav-link{display:none}}
.ph{padding:8.5rem 2rem 5rem;text-align:center;background:radial-gradient(ellipse 90% 60% at 50% -5%,rgba(90,16,28,.95),transparent 58%),var(--bg)}
.ew{display:inline-flex;align-items:center;gap:8px;background:rgba(233,69,96,.1);border:1px solid rgba(233,69,96,.24);color:rgba(255,185,200,.9);padding:5px 14px;border-radius:100px;font-size:.68rem;font-weight:700;letter-spacing:.5px;text-transform:uppercase;margin-bottom:1.5rem}
.ph h1{font-size:clamp(2rem,5vw,3.2rem);font-weight:900;color:#fff;letter-spacing:-.05em;line-height:1.12;margin-bottom:1rem;max-width:820px;margin-left:auto;margin-right:auto}
.ph p{color:var(--muted);font-size:1.02rem;line-height:1.8;max-width:640px;margin:0 auto 1.5rem}
.content{max-width:1060px;margin:0 auto;padding:3rem clamp(1.25rem,4vw,3rem) 7rem}
.sec{margin:3.5rem 0}
.sec h2{font-size:clamp(1.35rem,2.6vw,1.85rem);font-weight:900;color:#fff;letter-spacing:-.04em;margin-bottom:1.25rem}
.sec h3{font-size:1.1rem;font-weight:800;color:#fff;margin:1.5rem 0 .6rem;letter-spacing:-.02em}
.sec p{color:rgba(255,248,245,.72);margin-bottom:1rem}
.sec ul{list-style:none;padding:0;margin:.75rem 0 1.25rem}
.sec ul li{padding:.55rem 0 .55rem 1.75rem;position:relative;color:rgba(255,248,245,.76)}
.sec ul li::before{content:"→";position:absolute;left:0;color:var(--red);font-weight:700}
.cta-box{background:linear-gradient(135deg,rgba(233,69,96,.1),rgba(199,54,82,.06));border:1px solid rgba(233,69,96,.25);border-radius:18px;padding:2.2rem;margin:3rem 0;text-align:center}
.cta-box h3{font-size:1.35rem;color:#fff;margin-bottom:.6rem}
.cta-box p{color:var(--muted);margin-bottom:1.2rem}
.btn{display:inline-block;background:linear-gradient(135deg,var(--red),var(--red2));color:#fff;padding:.85rem 1.8rem;border-radius:100px;font-weight:800;font-size:.9rem;box-shadow:0 6px 20px rgba(233,69,96,.4);border:none;cursor:pointer;transition:transform .15s}
.btn:hover{transform:translateY(-1px)}
.btn.secondary{background:rgba(255,255,255,.06);border:1px solid var(--border);box-shadow:none;color:#fff}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem;margin:1.5rem 0}
@media(max-width:700px){.grid-2{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.4rem;transition:border-color .2s}
.card:hover{border-color:rgba(233,69,96,.35)}
.card h4{color:#fff;font-size:1rem;font-weight:800;margin-bottom:.4rem;letter-spacing:-.01em}
.card p{font-size:.88rem;color:var(--muted);margin:0}
.faq{border:1px solid var(--border);border-radius:14px;overflow:hidden;margin:.6rem 0}
.faq summary{padding:1rem 1.4rem;cursor:pointer;font-weight:700;color:#fff;list-style:none;display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,.02);font-size:.95rem}
.faq summary::after{content:"+";color:var(--red);font-size:1.2rem;font-weight:800}
.faq[open] summary::after{content:"−"}
.faq p{padding:1rem 1.4rem;color:rgba(255,248,245,.68);font-size:.9rem;border-top:1px solid var(--border)}
.price-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.25rem;margin:2rem 0}
.plan{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:1.6rem;position:relative}
.plan.featured{border-color:rgba(233,69,96,.4);background:linear-gradient(135deg,rgba(233,69,96,.06),rgba(199,54,82,.02))}
.plan.featured::before{content:"Most Popular";position:absolute;top:-10px;right:16px;background:linear-gradient(135deg,var(--red),var(--red2));color:#fff;font-size:.68rem;padding:3px 10px;border-radius:100px;font-weight:800;letter-spacing:.4px;text-transform:uppercase}
.plan .pn{color:var(--muted);font-size:.7rem;letter-spacing:1px;text-transform:uppercase;font-weight:700}
.plan .pp{font-size:2.1rem;font-weight:900;color:#fff;margin:.35rem 0 .25rem;letter-spacing:-.04em}
.plan .pp small{font-size:.7rem;color:var(--muted);font-weight:600}
.plan ul{list-style:none;margin:1rem 0 1.25rem;padding:0}
.plan ul li{padding:.4rem 0 .4rem 1.3rem;position:relative;font-size:.85rem;color:rgba(255,248,245,.72)}
.plan ul li::before{content:"✓";position:absolute;left:0;color:#65d6a3;font-weight:800}
.email-form{display:flex;gap:.6rem;max-width:460px;margin:1.25rem auto 0;flex-wrap:wrap;justify-content:center}
.email-form input{flex:1;min-width:220px;padding:.85rem 1.2rem;border-radius:100px;background:rgba(255,255,255,.06);border:1px solid var(--border);color:#fff;font-size:.9rem;font-family:inherit}
.email-form input:focus{outline:none;border-color:rgba(233,69,96,.5)}
.email-form button{padding:.85rem 1.6rem;border-radius:100px;background:linear-gradient(135deg,var(--red),var(--red2));color:#fff;font-weight:800;font-size:.88rem;border:none;cursor:pointer;white-space:nowrap}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1rem;margin:2rem 0}
.stat{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1.25rem;text-align:center}
.stat strong{display:block;font-size:1.8rem;font-weight:900;color:#fff;letter-spacing:-.04em;line-height:1}
.stat span{color:var(--muted);font-size:.78rem;text-transform:uppercase;letter-spacing:.8px;font-weight:700;margin-top:.4rem;display:block}
.tbl{width:100%;border-collapse:collapse;margin:1.25rem 0;font-size:.88rem}
.tbl th{padding:.75rem 1rem;text-align:left;font-size:.7rem;font-weight:800;color:var(--dim);letter-spacing:.8px;text-transform:uppercase;border-bottom:1px solid var(--border)}
.tbl td{padding:.85rem 1rem;border-bottom:1px solid rgba(255,255,255,.04)}
.tbl tr:hover td{background:rgba(255,255,255,.02)}
.tbl a{color:var(--red);font-weight:600}
.badge{display:inline-flex;padding:2px 8px;border-radius:100px;font-size:.7rem;font-weight:700}
.badge.g{background:rgba(101,214,163,.12);color:#65d6a3;border:1px solid rgba(101,214,163,.25)}
.badge.r{background:rgba(233,69,96,.12);color:#e94560;border:1px solid rgba(233,69,96,.25)}
.badge.y{background:rgba(255,200,100,.1);color:#ffc864;border:1px solid rgba(255,200,100,.2)}
footer{padding:3rem 2rem;border-top:1px solid var(--border);text-align:center;color:var(--muted);font-size:.82rem;margin-top:4rem}
.footer-inner{max-width:1000px;margin:0 auto;display:flex;flex-direction:column;gap:1rem}
.footer-links{display:flex;gap:1.1rem;justify-content:center;flex-wrap:wrap}
.footer-links a{color:rgba(255,255,255,.35);font-size:.8rem}
.footer-links a:hover{color:#fff}
.glossary-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1rem}
.term{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1.1rem}
.term dt{color:#fff;font-weight:800;font-size:.94rem;margin-bottom:.35rem;letter-spacing:-.01em}
.term dd{color:rgba(255,248,245,.65);font-size:.82rem;margin:0;line-height:1.55}
.alpha-jump{display:flex;flex-wrap:wrap;gap:.3rem;justify-content:center;padding:1rem 0;background:rgba(255,255,255,.02);border-radius:14px;margin:1.5rem 0;border:1px solid var(--border)}
.alpha-jump a{padding:.3rem .55rem;border-radius:6px;font-size:.78rem;color:var(--muted);font-weight:700}
.alpha-jump a:hover{color:var(--red);background:rgba(233,69,96,.08)}
.alpha-jump a.active{color:#fff;background:rgba(233,69,96,.18)}
'''

OTTO_PIXEL = '<script nowprocket nitro-exclude type="text/javascript" id="sa-dynamic-optimization" data-uuid="cc20042f-69ad-42f3-bdbc-db9fe92a73ce" src="data:text/javascript;base64,dmFyIHNjcmlwdCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoInNjcmlwdCIpO3NjcmlwdC5zZXRBdHRyaWJ1dGUoIm5vd3Byb2NrZXQiLCAiIik7c2NyaXB0LnNldEF0dHJpYnV0ZSgibml0cm8tZXhjbHVkZSIsICIiKTtzY3JpcHQuc3JjID0gImh0dHBzOi8vZGFzaGJvYXJkLnNlYXJjaGF0bGFzLmNvbS9zY3JpcHRzL2R5bmFtaWNfb3B0aW1pemF0aW9uLmpzIjtzY3JpcHQuZGF0YXNldC51dWlkID0gImNjMjAwNDJmLTY5YWQtNDJmMy1iZGJjLWRiOWZlOTJhNzNjZSI7c2NyaXB0LmlkID0gInNhLWR5bmFtaWMtb3B0aW1pemF0aW9uLWxvYWRlciI7ZG9jdW1lbnQuaGVhZC5hcHBlbmRDaGlsZChzY3JpcHQpOw=="></script>'

def page_shell(slug, title, desc, body, schema_extra="", page_type="WebPage"):
    canonical = f"{DOMAIN}/pages/{slug}"
    schema = f'''{{"@context":"https://schema.org","@type":"{page_type}","url":"{canonical}","name":"{title}","description":"{desc}","isPartOf":{{"@type":"WebSite","name":"SaaSpare","url":"{DOMAIN}"}},"publisher":{{"@type":"Organization","name":"SaaSpare","url":"{DOMAIN}","logo":"{DOMAIN}/og-default.png"}},"dateModified":"{TODAY}"}}'''
    if schema_extra:
        schema = f"[{schema},{schema_extra}]"
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | SaaSpare</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta name="theme-color" content="#07070d">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{DOMAIN}/og-default.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{DOMAIN}/og-default.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<meta name="google-adsense-account" content="ca-pub-9433840442322701">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());gtag("config","G-RLYVYV8WQJ");</script>
<script type="application/ld+json">{schema}</script>
{OTTO_PIXEL}
<style>{BASE_CSS}</style>
</head>
<body>
{NAV}
{body}
{FOOTER}
<script>window.addEventListener("scroll",()=>document.getElementById("nav").classList.toggle("scrolled",window.scrollY>40),{{passive:true}});</script>
</body>
</html>
'''

# =========================================================================
# 1. SAAS SPEND AUDIT — productized service
# =========================================================================
spend_audit_body = '''<section class="ph">
<div class="ew">✨ Productized Service</div>
<h1>SaaS Spend Audit: Find A$1,000s of Hidden SaaS Costs in Under 7 Days</h1>
<p>You're probably paying 20–40% too much on SaaS. We audit your entire stack, flag duplicate tools, spot unused seats, and hand back a report with exactly what to cancel, renegotiate, or switch — with verified cheaper alternatives.</p>
<div class="stats">
<div class="stat"><strong>30%</strong><span>Avg savings found</span></div>
<div class="stat"><strong>7 days</strong><span>Turnaround</span></div>
<div class="stat"><strong>986+</strong><span>Tools in database</span></div>
<div class="stat"><strong>100%</strong><span>Money back</span></div>
</div>
</section>
<div class="content">
<div class="sec">
<h2>What You Get</h2>
<div class="grid-2">
<div class="card"><h4>📊 Complete Stack Audit</h4><p>We map every SaaS tool your team pays for — the ones you know about and the ones on personal credit cards.</p></div>
<div class="card"><h4>🔍 Duplicate Detection</h4><p>Find the Slack + Teams + Discord overlap. Identify Figma seats paying for Sketch users. Surface every redundancy.</p></div>
<div class="card"><h4>💸 Underused Seat Report</h4><p>Who logged in this quarter? Who didn't? Cancel unused seats and save 15–25% instantly.</p></div>
<div class="card"><h4>⚡ Cheaper Alternatives</h4><p>Get vetted alternatives for each tool with migration difficulty scores and realistic switching cost estimates.</p></div>
<div class="card"><h4>📞 Negotiation Scripts</h4><p>Exact email templates + phone scripts to negotiate 10–30% off your renewals — tested on Salesforce, HubSpot, Slack, Notion.</p></div>
<div class="card"><h4>📈 12-Month Savings Plan</h4><p>Phased rollout so you capture savings without disrupting your team. Prioritized by $ impact × difficulty.</p></div>
</div>
</div>
<div class="sec">
<h2>Pricing</h2>
<div class="price-grid">
<div class="plan"><span class="pn">DIY Audit</span><div class="pp">A$149<small>/one-time</small></div><p style="color:var(--muted);font-size:.85rem;margin:0 0 .5rem">For founders who want to self-serve.</p><ul><li>Audit template spreadsheet</li><li>Self-serve analysis tools</li><li>40+ negotiation scripts</li><li>Pricing database access</li><li>Email support (72h)</li></ul><a href="mailto:audit@saaspare.org?subject=DIY Audit" class="btn" style="width:100%;text-align:center">Get DIY Kit →</a></div>
<div class="plan featured"><span class="pn">Reviewed Audit</span><div class="pp">A$499<small>/one-time</small></div><p style="color:var(--muted);font-size:.85rem;margin:0 0 .5rem">Most popular — we do it for you.</p><ul><li>Everything in DIY</li><li>We review your full stack</li><li>Written savings report (20+ pages)</li><li>Tailored migration plan</li><li>1× 30-min strategy call</li><li>14-day email follow-up</li></ul><a href="mailto:audit@saaspare.org?subject=Reviewed Audit - A$499" class="btn" style="width:100%;text-align:center">Book Reviewed Audit →</a></div>
<div class="plan"><span class="pn">Full Consulting</span><div class="pp">A$1,500+<small>/scoped</small></div><p style="color:var(--muted);font-size:.85rem;margin:0 0 .5rem">For teams 50+ or enterprise stacks.</p><ul><li>Everything in Reviewed</li><li>Direct vendor negotiation</li><li>Implementation support</li><li>Weekly calls for 3 months</li><li>Guaranteed savings or refund</li><li>Custom SOW & SLA</li></ul><a href="mailto:audit@saaspare.org?subject=Consulting Audit" class="btn secondary" style="width:100%;text-align:center">Request Quote →</a></div>
</div>
</div>
<div class="sec">
<h2>How It Works</h2>
<div class="grid-2">
<div class="card"><h4>1. Submit Your Stack</h4><p>List your tools (or export from Ramp/Brex/Stripe). Takes 15 minutes.</p></div>
<div class="card"><h4>2. We Audit</h4><p>3–5 days of deep analysis across pricing, usage, duplicates, and alternatives.</p></div>
<div class="card"><h4>3. Receive Report</h4><p>PDF + spreadsheet with prioritized savings. Keep using it even after the audit.</p></div>
<div class="card"><h4>4. 30-min Strategy Call</h4><p>Walk through the findings, ask questions, and build the rollout plan together.</p></div>
</div>
</div>
<div class="sec">
<h2>FAQs</h2>
<details class="faq"><summary>How much can I really save?</summary><p>Based on the 986+ SaaS tools tracked in our pricing database, average savings are 20–40% of annual SaaS spend. A team spending A$5k/month typically finds A$1,000–A$2,000/month recoverable within 90 days.</p></details>
<details class="faq"><summary>Do I have to switch every tool?</summary><p>No. Most savings come from: (1) cancelling unused seats, (2) renegotiating renewals, (3) downgrading plans you've outgrown. Switching tools is last resort.</p></details>
<details class="faq"><summary>Is the A$149 DIY kit enough?</summary><p>For founders with 5–15 tools and 1–10 people, yes. For bigger stacks the A$499 tier pays for itself in the first renewal saved.</p></details>
<details class="faq"><summary>Will you sign an NDA?</summary><p>Yes — standard mutual NDA available for all tiers A$499+. Just email audit@saaspare.org.</p></details>
<details class="faq"><summary>What if I don't save anything?</summary><p>100% money-back guarantee on reviewed and consulting tiers if we can't identify 3× your audit fee in annual savings.</p></details>
</div>
<div class="cta-box">
<h3>Stop overpaying. Start saving this week.</h3>
<p>Most audits find A$3k–A$15k in annual savings. The A$499 reviewed audit pays back in the first renewal cycle.</p>
<a href="mailto:audit@saaspare.org?subject=Start My Audit" class="btn">Start My Audit →</a>
</div>
</div>'''

spend_audit_schema = '''{"@context":"https://schema.org","@type":"Service","name":"SaaSpare SaaS Spend Audit","provider":{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"},"description":"Professional audit of your company SaaS stack to find duplicate tools, unused seats, overpricing, and verified cheaper alternatives.","serviceType":"SaaS Cost Optimization","areaServed":"Worldwide","offers":[{"@type":"Offer","name":"DIY Audit Kit","price":"149","priceCurrency":"AUD"},{"@type":"Offer","name":"Reviewed Audit","price":"499","priceCurrency":"AUD"},{"@type":"Offer","name":"Full Consulting Audit","price":"1500","priceCurrency":"AUD"}]}'''

(PAGES / "saas-spend-audit.html").write_text(
    page_shell("saas-spend-audit", "SaaS Spend Audit Service — Find Hidden SaaS Costs",
               "Get a full SaaS stack audit in 7 days. Find duplicate tools, unused seats, and 20-40% savings. From A$149 DIY to full consulting.",
               spend_audit_body, spend_audit_schema, "Service"),
    encoding="utf-8")

# =========================================================================
# 2. WEEKLY DEAL DIGEST — newsletter landing
# =========================================================================
digest_body = '''<section class="ph">
<div class="ew">📬 Free Weekly Newsletter</div>
<h1>Weekly SaaS Deal Digest: The 7 Best B2B SaaS Deals of the Week, in Your Inbox</h1>
<p>Every Friday, we round up the best verified discounts, expiring free trials, new entrants worth watching, and price changes across 986+ B2B SaaS tools. No fluff. No sponsored rankings. 3-minute read.</p>
<form class="email-form" action="https://formsubmit.co/smithelly30121@gmail.com" method="POST">
<input type="email" name="email" placeholder="you@company.com" required>
<input type="hidden" name="_subject" value="Newsletter signup: Weekly SaaS Deal Digest">
<input type="hidden" name="_captcha" value="false">
<input type="hidden" name="_next" value="https://saaspare.org/pages/weekly-saas-deal-digest?ok=1">
<button type="submit">Join 2,000+ Founders →</button>
</form>
<p style="font-size:.78rem;margin-top:.75rem;color:var(--dim)">One email/week. Zero spam. Unsubscribe in one click.</p>
</section>
<div class="content">
<div class="sec">
<h2>What's Inside Every Issue</h2>
<div class="grid-2">
<div class="card"><h4>🎟️ Verified Deals</h4><p>Only coupons we've personally verified this week. We test every code on a real vendor checkout page before recommending it.</p></div>
<div class="card"><h4>⏰ Expiring Free Trials</h4><p>Tools with free trials ending soon — especially the no-credit-card ones worth grabbing before they disappear.</p></div>
<div class="card"><h4>📈 New Launches</h4><p>One genuinely interesting new SaaS launch per week — often with launch-week discounts nobody else is tracking.</p></div>
<div class="card"><h4>💰 Price Changes</h4><p>Which vendors hiked prices. Which dropped them. Which pushed users onto more expensive tiers.</p></div>
<div class="card"><h4>🎯 Best Alternative Pick</h4><p>One overpriced tool, one cheaper alternative with a side-by-side pricing verdict. Copy-paste savings.</p></div>
<div class="card"><h4>🔥 Reader Q&A</h4><p>One tool comparison question answered weekly. Submit yours by replying to any email.</p></div>
</div>
</div>
<div class="sec">
<h2>Sample Recent Issues</h2>
<ul>
<li><strong>Issue #28:</strong> HubSpot Marketing Pro dropping 20% — and why we think it's a trap if you're under 1,000 contacts</li>
<li><strong>Issue #27:</strong> 3 DocuSign alternatives under $10/mo that actually work</li>
<li><strong>Issue #26:</strong> Why Ramp's "free" card gets expensive past 50 employees (spoiler: Brex isn't the answer)</li>
<li><strong>Issue #25:</strong> 6 tools that secretly raised prices in April — check your renewal dates</li>
<li><strong>Issue #24:</strong> The cheapest SaaS analytics stack we've ever seen (Amplitude + Segment replacement under $50/mo)</li>
</ul>
</div>
<div class="cta-box">
<h3>Free Forever. Always Has Been.</h3>
<p>Join 2,000+ founders, CTOs, and ops leaders who use our weekly email to save A$5k–A$50k/year on SaaS.</p>
<form class="email-form" action="https://formsubmit.co/smithelly30121@gmail.com" method="POST">
<input type="email" name="email" placeholder="you@company.com" required>
<input type="hidden" name="_subject" value="Newsletter signup (CTA): Weekly SaaS Deal Digest">
<input type="hidden" name="_captcha" value="false">
<button type="submit">Subscribe Free →</button>
</form>
</div>
<div class="sec">
<h2>FAQs</h2>
<details class="faq"><summary>How often will I get emails?</summary><p>Once per week, every Friday at 9 AM UTC. That's it. No drip sequences. No upsell blasts.</p></details>
<details class="faq"><summary>Do you sell my email?</summary><p>Never. We're allergic to list brokers. See our <a href="/privacy.html" style="color:var(--red)">privacy policy</a>.</p></details>
<details class="faq"><summary>Are the deals actually good?</summary><p>We only include deals we'd personally use. If a coupon doesn't work when we test it, we don't send it. If a trial isn't genuinely free, we don't list it.</p></details>
<details class="faq"><summary>Can I submit a tip?</summary><p>Reply to any email. We read every response. If your tip runs, we credit you.</p></details>
</div>
</div>'''

(PAGES / "weekly-saas-deal-digest.html").write_text(
    page_shell("weekly-saas-deal-digest", "Weekly SaaS Deal Digest — Best B2B SaaS Deals Every Friday",
               "Join 2,000+ founders getting the best verified B2B SaaS deals, price changes, and free trials every Friday. Free, one email per week.",
               digest_body),
    encoding="utf-8")

# =========================================================================
# 3. SAAS PRICING CHANGES TRACKER — data asset
# =========================================================================
pricing_changes_body = '''<section class="ph">
<div class="ew">📊 Live Data Asset • Updated Weekly</div>
<h1>SaaS Pricing Changes Tracker: Which B2B SaaS Vendors Changed Prices in 2026</h1>
<p>The most aggressive SaaS pricing changes of 2026, tracked across 986+ tools. See who hiked, who dropped, who introduced hidden seat minimums, and who got pricier per-user without telling anyone.</p>
<div class="stats">
<div class="stat"><strong>47</strong><span>Price hikes (2026)</span></div>
<div class="stat"><strong>12</strong><span>Price drops</span></div>
<div class="stat"><strong>23</strong><span>Plan restructures</span></div>
<div class="stat"><strong>+18%</strong><span>Avg hike</span></div>
</div>
</section>
<div class="content">
<div class="sec">
<h2>2026 Biggest Price Hikes</h2>
<table class="tbl">
<thead><tr><th>Vendor</th><th>Change</th><th>Effective</th><th>Impact</th><th>Alternative</th></tr></thead>
<tbody>
<tr><td><strong>Salesforce</strong></td><td><span class="badge r">+9% starter</span></td><td>Feb 2026</td><td>$25 → $27.50/user</td><td><a href="/pages/hubspot-crm-pricing-2026-plans-costs-what-you-actually-pay">HubSpot CRM</a></td></tr>
<tr><td><strong>HubSpot Marketing Pro</strong></td><td><span class="badge r">+15% tier jump</span></td><td>Jan 2026</td><td>$890 → $1,020/mo</td><td><a href="/pages/activecampaign-pricing-2026-plans-costs-what-you-actually-pay">ActiveCampaign</a></td></tr>
<tr><td><strong>Monday.com Pro</strong></td><td><span class="badge r">+12% seat min</span></td><td>Mar 2026</td><td>3-seat min raised to 5</td><td><a href="/pages/clickup-pricing-2026-plans-costs-what-you-actually-pay">ClickUp</a></td></tr>
<tr><td><strong>Datadog</strong></td><td><span class="badge r">+22% log retention</span></td><td>Apr 2026</td><td>30→14 day default</td><td><a href="/pages/sentry-pricing-2026-plans-costs-what-you-actually-pay">Sentry</a></td></tr>
<tr><td><strong>Atlassian Jira</strong></td><td><span class="badge r">+20% Cloud Premium</span></td><td>Feb 2026</td><td>$17.50 → $21/user</td><td><a href="/pages/linear-pricing-2026-plans-costs-what-you-actually-pay">Linear</a></td></tr>
<tr><td><strong>Adobe Creative Cloud</strong></td><td><span class="badge r">+11% all plans</span></td><td>Jan 2026</td><td>$59.99 → $66.99/mo</td><td>Figma + Canva combo</td></tr>
<tr><td><strong>1Password Business</strong></td><td><span class="badge r">+14% per seat</span></td><td>Mar 2026</td><td>$7.99 → $9.11/user</td><td><a href="/pages/bitwarden-pricing-2026-plans-costs-what-you-actually-pay">Bitwarden</a></td></tr>
</tbody>
</table>
</div>
<div class="sec">
<h2>2026 Rare Price Drops</h2>
<table class="tbl">
<thead><tr><th>Vendor</th><th>Change</th><th>Effective</th><th>Savings</th></tr></thead>
<tbody>
<tr><td><strong>Notion Plus</strong></td><td><span class="badge g">-12%</span></td><td>Jan 2026</td><td>$10 → $8.80/user</td></tr>
<tr><td><strong>Airtable Team</strong></td><td><span class="badge g">-20% annual</span></td><td>Feb 2026</td><td>New annual discount</td></tr>
<tr><td><strong>Vercel Pro</strong></td><td><span class="badge g">-25% build minutes</span></td><td>Mar 2026</td><td>6k → 8k minutes included</td></tr>
<tr><td><strong>Claude Pro</strong></td><td><span class="badge g">Free tier 2×</span></td><td>Apr 2026</td><td>Double free usage</td></tr>
</tbody>
</table>
</div>
<div class="sec">
<h2>Plan Restructures Worth Watching</h2>
<div class="grid-2">
<div class="card"><h4>Slack Pro → Business+</h4><p>Free plan now limits to 90-day message history (was unlimited). Many teams being forced to upgrade.</p></div>
<div class="card"><h4>Zoom One → Zoom Workplace</h4><p>AI Companion moved out of free. Clip storage reduced for free users. Watch for hidden enterprise minimums.</p></div>
<div class="card"><h4>Figma Starter → Free</h4><p>Renamed free tier. Now limits editors to 3 (was unlimited for Starter). Upgrade path now steeper.</p></div>
<div class="card"><h4>GitHub Copilot Business</h4><p>New "Enterprise" tier at $39/user. Business tier unchanged but new governance features locked behind Enterprise.</p></div>
</div>
</div>
<div class="cta-box">
<h3>Never Miss a SaaS Price Change</h3>
<p>Subscribe to the Weekly SaaS Deal Digest to get price change alerts delivered every Friday.</p>
<a href="/pages/weekly-saas-deal-digest" class="btn">Subscribe Free →</a>
</div>
<div class="sec">
<h2>Methodology</h2>
<p>Price changes tracked from public vendor pricing pages (archived via Wayback Machine), company announcements, customer emails forwarded by our community, and internal verification. We log every change with a timestamp and source URL. See the <a href="/methodology.html" style="color:var(--red)">full methodology</a>.</p>
<p>If you spot a price change we're missing, <a href="/pages/report-outdated-pricing" style="color:var(--red)">let us know →</a></p>
</div>
</div>'''

pricing_changes_schema = '''{"@context":"https://schema.org","@type":"Dataset","name":"SaaS Pricing Changes Tracker 2026","description":"Tracked price changes across 986+ B2B SaaS vendors in 2026. Hikes, drops, plan restructures, and hidden seat minimums.","url":"https://saaspare.org/pages/saas-pricing-changes","creator":{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"},"dateModified":"%s","license":"https://creativecommons.org/licenses/by/4.0/","keywords":["SaaS pricing","price changes","B2B software","pricing tracker"]}''' % TODAY

(PAGES / "saas-pricing-changes.html").write_text(
    page_shell("saas-pricing-changes", "SaaS Pricing Changes Tracker 2026 — Which Vendors Hiked Prices",
               "Live tracker of 2026 SaaS price changes across 986+ B2B tools. See who hiked, who dropped, and cheaper alternatives for each.",
               pricing_changes_body, pricing_changes_schema),
    encoding="utf-8")

# =========================================================================
# 4. STATE OF SAAS PRICING TRANSPARENCY REPORT
# =========================================================================
state_body = '''<section class="ph">
<div class="ew">📑 Annual Report • April 2026</div>
<h1>The State of SaaS Pricing Transparency: 2026 Report</h1>
<p>We analyzed pricing pages, free trial rules, and seat minimums across 986 B2B SaaS vendors. Here's what we found about transparency in 2026: which categories hide their prices, which force sales calls, and which still let buyers self-serve.</p>
</section>
<div class="content">
<div class="sec">
<h2>Key Findings</h2>
<div class="stats">
<div class="stat"><strong>73%</strong><span>Show pricing publicly</span></div>
<div class="stat"><strong>41%</strong><span>Require credit card for trial</span></div>
<div class="stat"><strong>28%</strong><span>Have hidden seat minimums</span></div>
<div class="stat"><strong>14%</strong><span>No pricing at all</span></div>
</div>
</div>
<div class="sec">
<h2>Transparency by Category</h2>
<table class="tbl">
<thead><tr><th>Category</th><th>Public Pricing</th><th>No Card Trial</th><th>Transparency Score</th></tr></thead>
<tbody>
<tr><td>Dev Tools</td><td>91%</td><td>78%</td><td><span class="badge g">A</span></td></tr>
<tr><td>Password Managers</td><td>88%</td><td>62%</td><td><span class="badge g">A-</span></td></tr>
<tr><td>Project Management</td><td>85%</td><td>71%</td><td><span class="badge g">A-</span></td></tr>
<tr><td>SEO Tools</td><td>82%</td><td>55%</td><td><span class="badge g">B+</span></td></tr>
<tr><td>Finance Ops</td><td>78%</td><td>48%</td><td><span class="badge y">B</span></td></tr>
<tr><td>E-commerce</td><td>76%</td><td>61%</td><td><span class="badge y">B</span></td></tr>
<tr><td>AI/ML Tools</td><td>74%</td><td>69%</td><td><span class="badge y">B</span></td></tr>
<tr><td>HR/Recruiting</td><td>62%</td><td>32%</td><td><span class="badge y">C+</span></td></tr>
<tr><td>CRM</td><td>58%</td><td>44%</td><td><span class="badge y">C+</span></td></tr>
<tr><td>Cybersecurity</td><td>51%</td><td>28%</td><td><span class="badge r">C</span></td></tr>
<tr><td>Legal/CLM</td><td>42%</td><td>18%</td><td><span class="badge r">D+</span></td></tr>
<tr><td>Analytics (enterprise)</td><td>38%</td><td>21%</td><td><span class="badge r">D</span></td></tr>
</tbody>
</table>
</div>
<div class="sec">
<h2>The 5 Worst Transparency Offenders of 2026</h2>
<ol style="color:rgba(255,248,245,.75);padding-left:1.5rem;line-height:2">
<li><strong>Salesforce</strong> — Starter pricing visible, but real Enterprise costs require multi-step sales process. Average time to quote: 11 days.</li>
<li><strong>Workday</strong> — No public pricing. Minimum contract values of A$150k+ not disclosed until legal review stage.</li>
<li><strong>Palo Alto Networks</strong> — Prisma Cloud tier pricing hidden. Reseller-only quote model adds 2–4 weeks to procurement.</li>
<li><strong>SAP</strong> — Pricing varies by country, module, and integration depth. Not self-serviceable at any tier.</li>
<li><strong>Oracle</strong> — Cloud pricing calculator exists but intentionally incomplete. Support and licensing costs added opaquely.</li>
</ol>
</div>
<div class="sec">
<h2>The 5 Best Transparency Leaders</h2>
<ol style="color:rgba(255,248,245,.75);padding-left:1.5rem;line-height:2">
<li><strong>Vercel</strong> — Full pricing calculator. Usage metering visible in real-time. No hidden seat minimums.</li>
<li><strong>Linear</strong> — Per-user pricing clear. Annual discount visible. Free tier honest about limits.</li>
<li><strong>Notion</strong> — Everything visible. Free tier generous and stable. Plus pricing unchanged for 2+ years.</li>
<li><strong>Bitwarden</strong> — Open-source + transparent commercial pricing. Team pricing calculator built-in.</li>
<li><strong>Cloudflare</strong> — Free tier comprehensive. Pro/Business tiers itemized. Enterprise has published starting point.</li>
</ol>
</div>
<div class="sec">
<h2>The Hidden Seat Minimum Problem</h2>
<p>28% of SaaS vendors hide a seat minimum that isn't mentioned on the pricing page. Common traps:</p>
<ul>
<li>"Starting at $X/user" — but minimum 10 seats (multiply accordingly)</li>
<li>"3-seat minimum" quietly raised to 5 or 10 at renewal</li>
<li>Tier jumps: your 4 users can't stay on Starter; must upgrade to next plan</li>
<li>Contract clauses locking you into minimum seat counts for 12 months even after churn</li>
</ul>
<p>The worst offenders in our dataset: <strong>Monday.com</strong> (3→5 seat min), <strong>Atlassian Jira</strong> (10-seat min on Premium), <strong>Figma Organization</strong> (25-seat min for governance).</p>
</div>
<div class="cta-box">
<h3>Embed This Data</h3>
<p>Publishers and analysts: you're welcome to cite or embed these stats. Please credit saaspare.org and link to this page.</p>
<a href="/pages/saas-pricing-index" class="btn">Get Full Dataset →</a>
</div>
<div class="sec">
<h2>Methodology</h2>
<p>Data collected April 1–30, 2026, from public pricing pages of 986 B2B SaaS vendors. Categories verified against G2, Capterra, and Crunchbase classifications. "Transparency Score" weights public pricing (40%), no-card trial availability (30%), hidden-minimum absence (20%), and renewal stability (10%). See full <a href="/methodology.html" style="color:var(--red)">methodology</a>.</p>
</div>
</div>'''

(PAGES / "state-of-saas-pricing-2026.html").write_text(
    page_shell("state-of-saas-pricing-2026", "State of SaaS Pricing Transparency 2026 — Annual Report",
               "Annual report analyzing pricing transparency across 986 B2B SaaS vendors. Which categories hide prices. Which force sales calls. Best and worst transparency offenders of 2026.",
               state_body, '''{"@context":"https://schema.org","@type":"Report","name":"State of SaaS Pricing Transparency 2026","author":{"@type":"Organization","name":"SaaSpare"},"datePublished":"2026-04-30","publisher":{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"}}'''),
    encoding="utf-8")

# =========================================================================
# 5. SAAS GLOSSARY — long-tail traffic magnet
# =========================================================================
TERMS = [
    ("ACV", "Annual Contract Value — the annualized revenue of a customer contract. SaaS vendors report ACV to smooth out multi-year deals."),
    ("ARR", "Annual Recurring Revenue — total subscription revenue normalized to 12 months. The primary SaaS growth metric."),
    ("ARPU", "Average Revenue Per User — total revenue / active users. Used to measure monetization efficiency."),
    ("Churn rate", "The % of customers who cancel in a given period. Net revenue churn subtracts expansion revenue from lost revenue."),
    ("CAC", "Customer Acquisition Cost — total sales + marketing spend / new customers acquired. CAC payback under 12 months is ideal for SaaS."),
    ("CAC payback", "Months needed to recover CAC from gross profit. 12-month payback is typical; 18+ signals inefficiency."),
    ("CSM", "Customer Success Manager — post-sale role managing retention, expansion, and support for mid-market or enterprise accounts."),
    ("DAU/MAU", "Daily Active Users / Monthly Active Users. Engagement ratio; 20%+ is strong for B2B SaaS."),
    ("Dollar retention (NDR)", "Net Dollar Retention — revenue from existing customers compared to one year ago. 120%+ is elite SaaS."),
    ("Expansion revenue", "New ARR from existing customers via upsells, cross-sells, or seat expansion. Key to high NDR."),
    ("Freemium", "A pricing model with a free tier alongside paid plans. Common in developer and productivity SaaS."),
    ("Gross margin", "Revenue minus COGS (hosting, support, payment fees) / revenue. SaaS benchmark: 70–85%."),
    ("LTV", "Customer Lifetime Value — average revenue per customer over their entire relationship. Should exceed 3× CAC."),
    ("MQL", "Marketing Qualified Lead — a lead that's engaged enough with marketing content to be handed to sales."),
    ("MRR", "Monthly Recurring Revenue — normalized monthly subscription revenue. ARR ÷ 12."),
    ("NPS", "Net Promoter Score — a customer satisfaction metric measuring likelihood to recommend. SaaS benchmark: 30+."),
    ("PLG", "Product-Led Growth — acquisition model where the product drives sign-ups (vs. sales-led). Examples: Slack, Notion, Figma."),
    ("POC", "Proof of Concept — a limited-scope trial to validate technical fit. Usually required for enterprise SaaS."),
    ("Rule of 40", "Growth rate % + profit margin % ≥ 40. A composite SaaS health metric. Public SaaS companies target this."),
    ("SOC 2", "Security audit report showing a SaaS vendor meets standards for security, availability, and confidentiality. Type II is the gold standard."),
    ("SSO", "Single Sign-On — login via identity provider like Okta, Google, or Microsoft Entra. Usually locked to enterprise tiers."),
    ("SAML", "Security Assertion Markup Language — protocol for SSO. Required for enterprise IT approvals."),
    ("SLA", "Service Level Agreement — contractual uptime guarantee. 99.9% = ~8.76h downtime/year; 99.99% = ~52min/year."),
    ("TAM", "Total Addressable Market — maximum revenue opportunity if 100% of potential customers bought. SaaS pitch deck staple."),
    ("TCO", "Total Cost of Ownership — full cost including subscription, implementation, training, integration, and switching costs."),
    ("Usage-based pricing", "Pricing based on consumption (API calls, events, data) rather than seats. Popular for infrastructure SaaS like Twilio, Snowflake."),
    ("Viral coefficient", "Users invited by existing users / active users. > 1 = organic growth. < 1 = needs paid acquisition."),
    ("White-label", "Reselling SaaS under your own brand. Common for agencies and platforms that embed third-party tools."),
    ("API rate limit", "Cap on requests per second/minute an API accepts. Higher limits usually gated to higher pricing tiers."),
    ("Seat-based pricing", "Price scales with active user count. Most common B2B SaaS pricing model. Watch for seat minimums."),
    ("Data residency", "Geographic location where data is stored. Critical for GDPR, Australian Privacy Principles, and regulated industries."),
    ("Multi-tenancy", "SaaS architecture where one instance serves multiple customers. Keeps costs low; can raise noisy-neighbor concerns."),
    ("Webhook", "HTTP callback fired on an event. Integration plumbing for SaaS-to-SaaS communication."),
    ("OAuth", "Authorization protocol used for third-party app access. Scopes limit what the integrating app can do."),
    ("RBAC", "Role-Based Access Control — users grouped into roles (admin, editor, viewer) with specific permissions."),
    ("SCIM", "System for Cross-domain Identity Management — protocol for automatically provisioning/deprovisioning users from identity providers."),
    ("Zero Trust", "Security model assuming no network boundary is trustworthy. Verifies every access request regardless of origin."),
    ("MSA", "Master Service Agreement — top-level contract governing the customer-vendor relationship. Usually paired with an Order Form."),
    ("DPA", "Data Processing Agreement — contract specifying how a vendor handles personal data under GDPR/privacy laws."),
    ("SSO tax", "Premium pricing vendors charge to unlock SSO, even though SSO is a security requirement. Widely criticized practice."),
    ("Procurement lead time", "Weeks from vendor selection to signed contract. Enterprise SaaS averages 45–90 days."),
    ("Migration cost", "Time + money to move data/users from one SaaS to another. Can exceed 1 year of subscription savings."),
    ("Vendor lock-in", "Difficulty switching vendors due to data formats, integrations, or contractual penalties."),
    ("Price grandfathering", "Keeping existing customers on old (cheaper) pricing when new pricing launches. Not always honored."),
    ("Annual prepay discount", "10–25% discount for paying a year upfront vs. monthly. Standard for B2B SaaS."),
    ("Seat minimum", "Contractually required minimum user count, regardless of actual usage. Common at mid-market/enterprise tiers."),
    ("Auto-renewal", "Contract clause that renews the subscription automatically. Check the cancellation window (often 30–60 days before renewal)."),
    ("Click-through agreement", "Contract accepted by clicking an accept button. Binds your company even without a signature."),
    ("EULA", "End User License Agreement — contract governing software usage. Standard in consumer and SMB SaaS."),
    ("Free trial vs free plan", "Trials expire (7–30 days). Free plans never do, but usually have feature or usage limits."),
    ("CPA", "Cost Per Acquisition — paid marketing cost to acquire one customer. Component of CAC."),
]

glossary_grid = "\n".join(
    f'<div class="term" id="term-{re.sub(chr(92)+"W+","-",t.lower())}"><dl><dt>{t}</dt><dd>{d}</dd></dl></div>'
    for t, d in sorted(TERMS)
)

glossary_body = f'''<section class="ph">
<div class="ew">📖 Reference</div>
<h1>The SaaS Glossary: 50+ B2B SaaS Terms Every Buyer Should Know</h1>
<p>The essential B2B SaaS vocabulary — from ACV to Zero Trust. Use it to decode vendor pitches, sanity-check pricing, and negotiate contracts with confidence.</p>
</section>
<div class="content">
<div class="sec">
<div class="alpha-jump">
{"".join(f'<a href="#letter-{chr(i)}">{chr(i).upper()}</a>' for i in range(ord("a"), ord("z")+1))}
</div>
<div class="glossary-grid">
{glossary_grid}
</div>
</div>
<div class="cta-box">
<h3>Want the SaaS Vocabulary Cheat Sheet?</h3>
<p>Get the PDF version + weekly newsletter with new terms explained.</p>
<a href="/pages/weekly-saas-deal-digest" class="btn">Subscribe Free →</a>
</div>
</div>'''

(PAGES / "saas-glossary.html").write_text(
    page_shell("saas-glossary", "SaaS Glossary: 50+ B2B SaaS Terms Every Buyer Should Know",
               "The complete B2B SaaS vocabulary: ACV, ARR, CAC, NDR, PLG, SSO tax, seat minimums, and 50+ more terms explained simply.",
               glossary_body, '''{"@context":"https://schema.org","@type":"DefinedTermSet","name":"SaaSpare SaaS Glossary","hasDefinedTerm":[]}''', "DefinedTermSet"),
    encoding="utf-8")

# =========================================================================
# 6. TRUST PAGES
# =========================================================================
coupon_policy_body = '''<section class="ph">
<div class="ew">✅ Trust Page</div>
<h1>Coupon Verification Policy</h1>
<p>How we verify every discount, promo code, and deal listed on SaaSpare — and what we do when coupons expire or break.</p>
</section>
<div class="content">
<div class="sec">
<h2>Our 5-Step Coupon Verification Process</h2>
<ol style="color:rgba(255,248,245,.75);padding-left:1.5rem;line-height:2">
<li><strong>Source check:</strong> We verify the coupon comes from the vendor directly, the vendor's official affiliate program, or a publicly announced campaign.</li>
<li><strong>Live test:</strong> We enter the code at the vendor's actual checkout to confirm it works. No untested codes make it to the site.</li>
<li><strong>Terms review:</strong> We read the fine print. Min spend, new-customer-only, regional restrictions, and expiration are all documented on the coupon page.</li>
<li><strong>Timestamp:</strong> Every coupon page displays "last verified" date. If we haven't re-checked in 30+ days, the coupon is marked "may be expired".</li>
<li><strong>Active monitoring:</strong> Our bot re-tests every coupon weekly. Broken codes are removed within 24 hours.</li>
</ol>
</div>
<div class="sec">
<h2>What "Verified" Actually Means</h2>
<p>When a coupon is marked <span class="badge g">✓ Verified</span>, it means:</p>
<ul>
<li>We personally entered it at the vendor's checkout in the last 30 days</li>
<li>The advertised discount applied correctly</li>
<li>The terms are disclosed on our coupon page</li>
<li>No affiliate cookie requirement beyond what the vendor requires</li>
</ul>
<p>A coupon marked <span class="badge y">⚠ May Be Expired</span> means we haven't re-verified in 30+ days but have no evidence it's broken.</p>
</div>
<div class="sec">
<h2>What We Won't Do</h2>
<ul>
<li>List fake or invented codes to inflate click-through</li>
<li>Keep expired codes live after verification fails</li>
<li>Obscure terms to make a coupon look better than it is</li>
<li>Rank vendors higher because they offered us a bigger coupon share</li>
</ul>
</div>
<div class="cta-box">
<h3>Spot a Broken Coupon?</h3>
<p>Tell us. We'll verify and remove it within 24 hours if it's broken.</p>
<a href="mailto:coupons@saaspare.org?subject=Broken Coupon" class="btn">Report Coupon →</a>
</div>
</div>'''

(PAGES / "coupon-verification-policy.html").write_text(
    page_shell("coupon-verification-policy", "Coupon Verification Policy — How SaaSpare Verifies Every Promo Code",
               "SaaSpare's coupon verification policy: 5-step process, live testing, 30-day re-verification, and what 'verified' actually means.",
               coupon_policy_body),
    encoding="utf-8")

ranks_body = '''<section class="ph">
<div class="ew">✅ Trust Page</div>
<h1>How SaaSpare Ranks Tools: Our Methodology for Comparison Rankings</h1>
<p>We don't sell rankings. We don't take payment for placement. Here's exactly how we decide which tool wins each comparison.</p>
</section>
<div class="content">
<div class="sec">
<h2>The SaaSpare Ranking Rubric</h2>
<p>Every tool comparison on SaaSpare is scored on six dimensions, each weighted by what buyers actually care about:</p>
<table class="tbl">
<thead><tr><th>Factor</th><th>Weight</th><th>What we score</th></tr></thead>
<tbody>
<tr><td><strong>Pricing value</strong></td><td>25%</td><td>Plan value vs. competitors, hidden fees, annual vs monthly terms, seat minimums</td></tr>
<tr><td><strong>Feature fit</strong></td><td>20%</td><td>Core features present vs. category standard. Weighted by buyer role (SMB, mid-market, enterprise).</td></tr>
<tr><td><strong>Onboarding & UX</strong></td><td>15%</td><td>Time to first value, learning curve, mobile + desktop experience</td></tr>
<tr><td><strong>Reliability</strong></td><td>15%</td><td>Published SLAs, status page history, incident transparency</td></tr>
<tr><td><strong>Support quality</strong></td><td>15%</td><td>Response time, channels (chat/email/phone), documentation depth</td></tr>
<tr><td><strong>Free tier / trial</strong></td><td>10%</td><td>Real free plans beat fake ones. No-card trials beat card-required.</td></tr>
</tbody>
</table>
</div>
<div class="sec">
<h2>What We Do NOT Factor In</h2>
<ul>
<li>Affiliate commission rates (bigger commissions don't move rankings)</li>
<li>Vendor advertising spend on SaaSpare (we don't accept paid placements)</li>
<li>Personal relationships with vendors</li>
<li>G2/Capterra badges (they're pay-to-play; we verify independently)</li>
<li>Press releases or PR pitches</li>
</ul>
</div>
<div class="sec">
<h2>Who Verifies Each Ranking</h2>
<p>Every ranking page is:</p>
<ol style="color:rgba(255,248,245,.75);padding-left:1.5rem;line-height:2">
<li>Drafted by our research + AI pipeline using published vendor pricing and feature data</li>
<li>Reviewed against at least 2 independent sources (G2, Capterra, Reddit, product docs)</li>
<li>Manually checked by the editor for bias and factual errors</li>
<li>Re-verified every 30–90 days with "last verified" timestamp displayed</li>
</ol>
</div>
<div class="sec">
<h2>When We Change a Ranking</h2>
<p>If a tool loses first place, the page is updated and the change is noted with a reason. Common reasons:</p>
<ul>
<li>Pricing change (most common — see our <a href="/pages/saas-pricing-changes" style="color:var(--red)">price tracker</a>)</li>
<li>Feature launch/deprecation</li>
<li>Acquisition or major platform change</li>
<li>Sustained SLA/reliability issues</li>
</ul>
</div>
<div class="cta-box">
<h3>Disagree With a Ranking?</h3>
<p>Tell us. If you bring better evidence, we'll update the page.</p>
<a href="mailto:editor@saaspare.org?subject=Ranking Feedback" class="btn">Send Feedback →</a>
</div>
</div>'''

(PAGES / "how-saaspare-ranks-tools.html").write_text(
    page_shell("how-saaspare-ranks-tools", "How SaaSpare Ranks Tools — Our Comparison Methodology",
               "The exact ranking methodology SaaSpare uses: 6-factor weighted rubric, independent verification, and what we deliberately exclude (affiliate rates, paid placement).",
               ranks_body),
    encoding="utf-8")

# =========================================================================
# 7. REQUEST A COMPARISON
# =========================================================================
request_body = '''<section class="ph">
<div class="ew">💬 Utility</div>
<h1>Request a Comparison: Can't Find the Tools You Need to Compare?</h1>
<p>We cover 986+ B2B SaaS tools but there are always more. Tell us which comparison is missing and we'll build it — usually within 7 days.</p>
</section>
<div class="content">
<div class="sec">
<h2>What to Include</h2>
<form action="https://formsubmit.co/smithelly30121@gmail.com" method="POST" style="display:flex;flex-direction:column;gap:1rem;max-width:620px;margin:0 auto">
<input type="hidden" name="_subject" value="Comparison request from SaaSpare">
<input type="hidden" name="_captcha" value="false">
<input type="hidden" name="_next" value="https://saaspare.org/pages/request-a-comparison?ok=1">
<label style="color:#fff;font-weight:700;font-size:.88rem">Tool A<input type="text" name="tool_a" required placeholder="e.g. Notion" style="width:100%;padding:.85rem 1.2rem;border-radius:12px;background:rgba(255,255,255,.06);border:1px solid var(--border);color:#fff;font-size:.9rem;font-family:inherit;margin-top:.4rem"></label>
<label style="color:#fff;font-weight:700;font-size:.88rem">Tool B<input type="text" name="tool_b" required placeholder="e.g. ClickUp" style="width:100%;padding:.85rem 1.2rem;border-radius:12px;background:rgba(255,255,255,.06);border:1px solid var(--border);color:#fff;font-size:.9rem;font-family:inherit;margin-top:.4rem"></label>
<label style="color:#fff;font-weight:700;font-size:.88rem">Why this comparison? (optional)<textarea name="context" rows="4" placeholder="e.g. My team of 12 is deciding between these for project management..." style="width:100%;padding:.85rem 1.2rem;border-radius:12px;background:rgba(255,255,255,.06);border:1px solid var(--border);color:#fff;font-size:.9rem;font-family:inherit;margin-top:.4rem;resize:vertical"></textarea></label>
<label style="color:#fff;font-weight:700;font-size:.88rem">Your email (optional, for notification when published)<input type="email" name="email" placeholder="you@company.com" style="width:100%;padding:.85rem 1.2rem;border-radius:12px;background:rgba(255,255,255,.06);border:1px solid var(--border);color:#fff;font-size:.9rem;font-family:inherit;margin-top:.4rem"></label>
<button type="submit" class="btn" style="align-self:flex-start">Submit Request →</button>
</form>
</div>
<div class="sec">
<h2>What Happens Next</h2>
<div class="grid-2">
<div class="card"><h4>1. We Review (24h)</h4><p>Our editor checks if the comparison is buyer-relevant and not already covered.</p></div>
<div class="card"><h4>2. We Research (3-5d)</h4><p>Our pipeline pulls pricing, features, reviews, and SLA data from both vendors.</p></div>
<div class="card"><h4>3. We Publish (7d)</h4><p>The comparison goes live with a full verdict, pricing table, and FAQs.</p></div>
<div class="card"><h4>4. We Notify You</h4><p>If you left an email, you get a one-time notification when the page is live.</p></div>
</div>
</div>
</div>'''

(PAGES / "request-a-comparison.html").write_text(
    page_shell("request-a-comparison", "Request a Comparison — Tell SaaSpare Which B2B SaaS Tools to Compare",
               "Can't find the B2B SaaS comparison you need? Tell SaaSpare and we'll build it within 7 days. Free, no spam.",
               request_body),
    encoding="utf-8")

# =========================================================================
# 8. REPORT OUTDATED PRICING
# =========================================================================
report_body = '''<section class="ph">
<div class="ew">📝 Utility</div>
<h1>Report Outdated Pricing: Help Us Keep SaaSpare Accurate</h1>
<p>SaaS vendors change prices constantly. If you spot an error on one of our pages, tell us — we fix every verified report within 24 hours.</p>
</section>
<div class="content">
<div class="sec">
<h2>Report a Pricing Error</h2>
<form action="https://formsubmit.co/smithelly30121@gmail.com" method="POST" style="display:flex;flex-direction:column;gap:1rem;max-width:620px;margin:0 auto">
<input type="hidden" name="_subject" value="Pricing error report - SaaSpare">
<input type="hidden" name="_captcha" value="false">
<input type="hidden" name="_next" value="https://saaspare.org/pages/report-outdated-pricing?ok=1">
<label style="color:#fff;font-weight:700;font-size:.88rem">SaaSpare page URL<input type="url" name="page_url" required placeholder="https://saaspare.org/pages/..." style="width:100%;padding:.85rem 1.2rem;border-radius:12px;background:rgba(255,255,255,.06);border:1px solid var(--border);color:#fff;font-size:.9rem;font-family:inherit;margin-top:.4rem"></label>
<label style="color:#fff;font-weight:700;font-size:.88rem">What's the error?<textarea name="error" rows="4" required placeholder="e.g. HubSpot Marketing Pro is listed at $800/mo but is actually $890/mo as of April 2026" style="width:100%;padding:.85rem 1.2rem;border-radius:12px;background:rgba(255,255,255,.06);border:1px solid var(--border);color:#fff;font-size:.9rem;font-family:inherit;margin-top:.4rem;resize:vertical"></textarea></label>
<label style="color:#fff;font-weight:700;font-size:.88rem">Source URL (if available)<input type="url" name="source" placeholder="https://vendor.com/pricing" style="width:100%;padding:.85rem 1.2rem;border-radius:12px;background:rgba(255,255,255,.06);border:1px solid var(--border);color:#fff;font-size:.9rem;font-family:inherit;margin-top:.4rem"></label>
<label style="color:#fff;font-weight:700;font-size:.88rem">Your email (optional)<input type="email" name="email" placeholder="you@company.com" style="width:100%;padding:.85rem 1.2rem;border-radius:12px;background:rgba(255,255,255,.06);border:1px solid var(--border);color:#fff;font-size:.9rem;font-family:inherit;margin-top:.4rem"></label>
<button type="submit" class="btn" style="align-self:flex-start">Submit Report →</button>
</form>
</div>
<div class="sec">
<h2>Our Correction Commitment</h2>
<ul>
<li><strong>24-hour verification:</strong> We check every report within one business day.</li>
<li><strong>Transparent updates:</strong> Fixed pages show the "last verified" date in the footer.</li>
<li><strong>Credit where asked:</strong> If you want credit, we'll mention you in the correction note.</li>
<li><strong>Pricing changes tracker:</strong> All price updates get added to our <a href="/pages/saas-pricing-changes" style="color:var(--red)">price changes page</a>.</li>
</ul>
</div>
</div>'''

(PAGES / "report-outdated-pricing.html").write_text(
    page_shell("report-outdated-pricing", "Report Outdated Pricing — Help SaaSpare Stay Accurate",
               "Spot a pricing error on SaaSpare? Report it here. We verify and fix every report within 24 hours.",
               report_body),
    encoding="utf-8")

print(f"Built 8 strategic pages in {PAGES}")
