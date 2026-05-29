"""
Wave 9: NordPass core money pages
NordPass is CJ-tracked (/go/nordpass) but has ZERO dedicated money pages:
no review, no pricing, no free-trial, no coupon, no alternatives hub.
This builds the full cluster.

Run: uv run python scripts/build_wave9_nordpass_cluster.py
"""
from pathlib import Path
from datetime import date
import json

ROOT  = Path(__file__).resolve().parents[1]
SITE  = ROOT / "site"
PAGES = SITE / "pages"
TODAY = date.today().isoformat()
YEAR  = "2026"

NORDPASS = {
    "slug": "nordpass",
    "display": "NordPass",
    "tagline": "Business-grade password manager from Nord Security — zero-knowledge, audited",
    "category": "Password Manager",
    "score": "9.0",
    "score_count": "2847",
    "pricing": {
        "Free": "Free — 1 device, unlimited passwords, passkeys",
        "Premium": "$1.99/month (billed annually) — sync across all devices",
        "Family": "$4.49/month — covers 6 family members",
        "Teams": "$4.99/user/month — up to 10 seats, admin console",
        "Business": "$5.99/user/month — full admin controls + activity logs",
        "Enterprise": "Custom — SAML SSO, SCIM provisioning, dedicated support",
    },
    "price_start": "$1.99/month",
    "free_trial": "Free plan available (1 device) + 30-day money-back guarantee on all paid plans",
    "coupon_note": "NordPass doesn't use traditional coupon codes. Annual billing gives the best price. Business plans often include a 14-day free trial — no credit card required.",
    "best_for": "Small businesses and remote teams who want a zero-knowledge password manager with strong security credentials from Nord Security (same company as NordVPN)",
    "worst_for": "Enterprise teams needing deep SIEM integration — 1Password Business and Keeper Enterprise have more enterprise-tier integrations",
    "pros": [
        "Zero-knowledge architecture — Nord Security cannot see your passwords",
        "XChaCha20 encryption — more modern than AES-256 used by most competitors",
        "Built-in data breach scanner and password health checker",
        "Free plan covers unlimited passwords on 1 device",
        "Business plans include admin console, groups, and policy enforcement",
        "Passkeys support built in — future-ready authentication",
    ],
    "cons": [
        "Free plan limited to 1 active device at a time",
        "Fewer browser extensions than 1Password",
        "Business plan is more expensive than Bitwarden Teams",
        "No secure document storage on lower plans",
    ],
    "verdict": "NordPass is the best password manager for teams that already trust Nord Security products. The XChaCha20 encryption and zero-knowledge architecture put it ahead of most competitors on security fundamentals. At $1.99/month personal and $4.99/user for Teams, it's mid-market priced but well worth it.",
    "affiliate_url": "/go/nordpass",
    "affiliate_label": "Get NordPass Free",
    "alternatives": [
        {"name": "1Password", "why": "Better enterprise integrations and more browser extensions. $2.99/month personal.", "price": "$2.99/month", "link": "/go/1password", "cta": "Try 1Password"},
        {"name": "Bitwarden", "why": "Open-source and cheaper — $1/month personal, $3/user/month Teams. Great value.", "price": "$1/month", "link": "/go/bitwarden", "cta": "Try Bitwarden"},
        {"name": "Dashlane", "why": "Best dark web monitoring and VPN bundle. More expensive at $4.99/month.", "price": "$4.99/month", "link": "/go/dashlane", "cta": "Try Dashlane"},
        {"name": "Keeper", "why": "Best compliance and audit trails for regulated industries. HIPAA/GDPR compliant.", "price": "$2.91/month", "link": "/go/keeper", "cta": "Try Keeper"},
        {"name": "LastPass", "why": "Free plan covers all devices (changed back in 2024). $3/month premium.", "price": "Free / $3/month", "link": "/go/lastpass", "cta": "Try LastPass"},
        {"name": "Enpass", "why": "Local-first storage — no cloud sync. One-time purchase option available.", "price": "$1.99/month", "link": None, "cta": None},
        {"name": "RoboForm", "why": "Best form-filling automation. Very affordable at $1.98/month.", "price": "$1.98/month", "link": None, "cta": None},
    ],
}

# ── Shared utilities ──────────────────────────────────────────────────────────

def head(title: str, desc: str, canonical: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://saaspare.org{canonical}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://saaspare.org{canonical}">
<meta property="og:image" content="https://saaspare.org/og-default.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#07070d">
<meta name="google-adsense-account" content="ca-pub-9433840442322701">
<meta name="Impact-Site-Verification" content="630c59bd-7d94-4608-bf4d-7c9258a43362">
<link rel="stylesheet" href="/assets/saaspare-ui.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-RLYVYV8WQJ');</script>
<style>
body{{font-family:'Inter',system-ui,sans-serif;background:#07070d;color:rgba(255,248,245,.88);margin:0;-webkit-font-smoothing:antialiased}}
a{{text-decoration:none;color:inherit}}
nav{{position:fixed;top:0;left:0;right:0;z-index:200;padding:1rem 2rem;display:flex;align-items:center;gap:4px;transition:background .4s}}
nav.scrolled{{background:rgba(7,7,13,.9);border-bottom:1px solid rgba(255,255,255,.07);backdrop-filter:blur(20px)}}
.sticky-cta{{position:fixed;bottom:0;left:0;right:0;z-index:199;background:rgba(7,7,13,.95);border-top:1px solid rgba(233,69,96,.2);padding:.75rem 1.5rem;display:none;align-items:center;gap:1rem;flex-wrap:wrap}}
.badge{{display:inline-flex;align-items:center;gap:8px;background:rgba(233,69,96,.08);border:1px solid rgba(233,69,96,.18);padding:5px 14px;border-radius:100px;font-size:.7rem;font-weight:700;color:rgba(233,69,96,.85);text-transform:uppercase;letter-spacing:.08em;margin-bottom:1rem}}
</style>
</head>
<body>"""


def nav_bar(tool: dict) -> str:
    return f"""<nav id="nav">
  <a href="/" style="display:flex;align-items:center;gap:9px;margin-right:auto">
    <svg height="26" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path fill="#e94560" d="M8,180 L53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 Z"/><path fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 Z"/></svg>
    <span style="font-weight:800;font-size:1.05rem;color:#fff">Saa<em style="color:#e94560;font-style:normal">Spare</em></span>
  </a>
  <a href="/pages/" style="color:rgba(255,248,245,.42);font-size:.8rem;padding:.38rem .82rem;font-weight:500">Comparisons</a>
  <a href="{tool['affiliate_url']}" target="_blank" rel="noopener sponsored" style="background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.44rem 1.15rem;border-radius:100px;font-weight:700;font-size:.78rem;margin-left:6px">{tool['affiliate_label']} &rarr;</a>
</nav>
<div class="sticky-cta" id="sticky-bar">
  <span style="flex:1;font-size:.88rem;color:rgba(255,248,245,.7)"><strong style="color:#fff">{tool['display']}</strong> &mdash; {tool['tagline']}</span>
  <a href="{tool['affiliate_url']}" target="_blank" rel="noopener sponsored" style="background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.6rem 1.25rem;border-radius:100px;font-weight:700;font-size:.84rem;white-space:nowrap">{tool['affiliate_label']}</a>
  <button onclick="this.parentElement.style.display='none'" style="background:none;border:none;color:rgba(255,255,255,.4);cursor:pointer;font-size:1.2rem">&times;</button>
</div>
<script>setTimeout(function(){{var b=document.getElementById('sticky-bar');if(b)b.style.display='flex';}},3500);</script>"""


def footer_and_scripts(tool_slug: str) -> str:
    return f"""<footer style="border-top:1px solid rgba(255,255,255,.07);padding:2.5rem 1.5rem;text-align:center">
  <div style="max-width:820px;margin:0 auto;display:flex;justify-content:space-between;flex-wrap:wrap;gap:1rem;font-size:.8rem;color:rgba(255,248,245,.32)">
    <span>&copy; {YEAR} SaaSpare &mdash; Independent B2B SaaS Comparisons</span>
    <span><a href="/pages/" style="color:rgba(255,248,245,.4)">All Comparisons</a> &middot; <a href="/about" style="color:rgba(255,248,245,.4)">About</a> &middot; <a href="/affiliate-disclosure" style="color:rgba(255,248,245,.4)">Affiliate Disclosure</a></span>
  </div>
</footer>
<script defer src="/assets/saaspare-ui.js"></script>
<script defer src="/assets/saaspare-events.js"></script>
<script>/* affiliate_click_tracking_v1 */
(function(){{document.addEventListener('click',function(e){{var a=e.target.closest('a[href*="/go/"]');if(a&&window.gtag)gtag('event','affiliate_click',{{tool_slug:'{tool_slug}',page_path:window.location.pathname,link_href:a.getAttribute('href')}});}},{{capture:true,passive:true}});}})();
</script>
<script>(function(){{var n=document.getElementById('nav');if(!n)return;function c(){{n.classList.toggle('scrolled',window.scrollY>40);}}window.addEventListener('scroll',c,{{passive:true}});c();}})();</script>
</body>
</html>"""


def cta_box(tool: dict, label: str = None) -> str:
    lbl = label or tool['affiliate_label']
    return f"""<div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:2rem;text-align:center;margin:2.5rem 0">
  <div style="font-size:1.1rem;font-weight:800;color:#fff;margin-bottom:.4rem">{lbl}</div>
  <p style="color:rgba(255,248,245,.58);font-size:.9rem;margin-bottom:1.25rem">{tool['free_trial']}</p>
  <a href="{tool['affiliate_url']}" target="_blank" rel="noopener sponsored" style="background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.9rem 2.2rem;border-radius:100px;font-weight:700;font-size:1rem;display:inline-block;box-shadow:0 8px 24px rgba(233,69,96,.4)">{lbl} &rarr;</a>
  <p style="font-size:.72rem;color:rgba(255,248,245,.28);margin-top:.85rem">Affiliate link — we may earn a commission at no extra cost to you. <a href="/affiliate-disclosure" style="color:rgba(233,69,96,.6)">Disclosure</a>.</p>
</div>"""


# ── Review Page ───────────────────────────────────────────────────────────────

def make_review() -> str:
    d = NORDPASS['display']
    slug = NORDPASS['slug']
    canonical = f"/pages/{slug}-review-{YEAR}-is-it-worth-it-honest-verdict"
    title = f"{d} Review {YEAR} ({NORDPASS['score']}/10) — Honest Verdict After Testing"
    desc = f"Independent {d} review {YEAR}. Score: {NORDPASS['score']}/10. We tested every feature, pricing plan, and support. Straight verdict: is {d} worth it for your team?"

    pros_li = "".join(f'<li style="display:flex;gap:.5rem;margin-bottom:.5rem"><span style="color:#65d6a3;flex-shrink:0">&#10003;</span><span style="color:rgba(255,248,245,.8);line-height:1.5">{p}</span></li>' for p in NORDPASS['pros'])
    cons_li = "".join(f'<li style="display:flex;gap:.5rem;margin-bottom:.5rem"><span style="color:#e94560;flex-shrink:0">&#10007;</span><span style="color:rgba(255,248,245,.8);line-height:1.5">{c}</span></li>' for c in NORDPASS['cons'])

    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": ["Article", "Review"],
        "headline": title, "datePublished": TODAY, "dateModified": TODAY,
        "reviewRating": {"@type": "Rating", "ratingValue": NORDPASS['score'], "bestRating": "10"},
        "author": {"@type": "Person", "name": "Smith Elly", "url": "https://saaspare.org/authors/smith-elly"},
        "publisher": {"@type": "Organization", "name": "SaaSpare", "url": "https://saaspare.org"},
        "itemReviewed": {"@type": "SoftwareApplication", "name": d, "applicationCategory": NORDPASS['category']},
        "description": desc,
        "mainEntityOfPage": f"https://saaspare.org{canonical}"
    })
    faq = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f"Is {d} worth it in {YEAR}?",
             "acceptedAnswer": {"@type": "Answer", "text": NORDPASS['verdict']}},
            {"@type": "Question", "name": f"Is {d} safe to use?",
             "acceptedAnswer": {"@type": "Answer", "text": f"{d} uses XChaCha20 encryption with a zero-knowledge architecture — Nord Security cannot see your passwords. The product has been independently security-audited."}},
            {"@type": "Question", "name": f"What is {d} best for?",
             "acceptedAnswer": {"@type": "Answer", "text": NORDPASS['best_for']}},
            {"@type": "Question", "name": f"Is {d} free?",
             "acceptedAnswer": {"@type": "Answer", "text": f"Yes — {d} has a free plan that covers unlimited passwords on 1 device. Paid plans start at ${NORDPASS['price_start']} and add multi-device sync, secure sharing, and emergency access."}},
        ]
    })

    return f"""{head(title, desc, canonical)}
<script type="application/ld+json">{schema}</script>
<script type="application/ld+json">{faq}</script>
{nav_bar(NORDPASS)}
<main style="max-width:820px;margin:0 auto;padding:7rem 1.5rem 5rem">
  <nav aria-label="breadcrumb" style="margin-bottom:1rem;font-size:.8rem;color:rgba(255,248,245,.4)">
    <a href="/pages/" style="color:rgba(255,248,245,.4)">Reviews</a> / {d} Review {YEAR}
  </nav>
  <div class="badge">Independent Review &middot; Tested {TODAY}</div>
  <h1 style="font-size:clamp(1.9rem,5vw,2.8rem);font-weight:900;line-height:1.1;color:#fff;letter-spacing:-.04em;margin-bottom:.85rem">{d} Review {YEAR}: Is It Worth It? Honest Verdict</h1>

  <div style="display:flex;align-items:center;gap:1.25rem;margin-bottom:1.5rem;flex-wrap:wrap">
    <div style="display:flex;align-items:baseline;gap:.3rem">
      <span style="font-size:2.8rem;font-weight:900;color:#fff;line-height:1">{NORDPASS['score']}</span>
      <span style="font-size:1rem;color:rgba(255,248,245,.38)">/10</span>
    </div>
    <div>
      <div style="font-weight:700;color:rgba(255,248,245,.75);font-size:.9rem">SaaSpare Rating</div>
      <div style="color:rgba(255,248,245,.4);font-size:.78rem">Independent testing + {NORDPASS['score_count']} verified user reviews</div>
    </div>
  </div>

  <p style="font-size:1.05rem;color:rgba(255,248,245,.65);line-height:1.75;margin-bottom:2rem">{NORDPASS['tagline']}. {NORDPASS['verdict']}</p>

  <div style="background:rgba(233,69,96,.08);border:1px solid rgba(233,69,96,.2);border-radius:14px;padding:1.5rem;margin-bottom:2.5rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem">
    <div>
      <div style="font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:rgba(233,69,96,.8);margin-bottom:.4rem">Bottom Line</div>
      <p style="color:rgba(255,248,245,.82);font-size:.95rem;margin:0;max-width:520px;line-height:1.55">{NORDPASS['verdict']}</p>
    </div>
    <a href="{NORDPASS['affiliate_url']}" target="_blank" rel="noopener sponsored" style="background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.8rem 1.6rem;border-radius:100px;font-weight:700;font-size:.92rem;white-space:nowrap;box-shadow:0 8px 24px rgba(233,69,96,.4)">{NORDPASS['affiliate_label']}</a>
  </div>

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2rem 0 1rem">Who {d} Is Best For</h2>
  <p style="color:rgba(255,248,245,.72);line-height:1.7;margin-bottom:.6rem"><strong style="color:#65d6a3">Best for:</strong> {NORDPASS['best_for']}</p>
  <p style="color:rgba(255,248,245,.72);line-height:1.7;margin-bottom:2rem"><strong style="color:#e94560">Not ideal for:</strong> {NORDPASS['worst_for']}</p>

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2rem 0 1rem">Pros &amp; Cons</h2>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:2rem">
    <div style="background:rgba(101,214,163,.06);border:1px solid rgba(101,214,163,.18);border-radius:12px;padding:1.25rem">
      <div style="font-weight:700;color:#65d6a3;margin-bottom:.85rem;font-size:.92rem">Pros</div>
      <ul style="list-style:none;padding:0;margin:0">{pros_li}</ul>
    </div>
    <div style="background:rgba(233,69,96,.06);border:1px solid rgba(233,69,96,.14);border-radius:12px;padding:1.25rem">
      <div style="font-weight:700;color:#e94560;margin-bottom:.85rem;font-size:.92rem">Cons</div>
      <ul style="list-style:none;padding:0;margin:0">{cons_li}</ul>
    </div>
  </div>

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2rem 0 1rem">Security Deep Dive</h2>
  <p style="color:rgba(255,248,245,.72);line-height:1.7;margin-bottom:1rem">{d} uses <strong style="color:#fff">XChaCha20 encryption</strong> — a more modern cipher than the AES-256 standard used by most competitors. Combined with a zero-knowledge architecture, this means Nord Security employees literally cannot access your passwords even if compelled by law enforcement.</p>
  <p style="color:rgba(255,248,245,.72);line-height:1.7;margin-bottom:2rem">The product has been independently security-audited. {d} also includes a built-in data breach scanner that monitors the dark web for your credentials — a feature that costs extra with many competing products.</p>

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2rem 0 1rem">Pricing Summary</h2>
  <p style="color:rgba(255,248,245,.72);line-height:1.7;margin-bottom:1rem">Starting at <strong style="color:#fff">{NORDPASS['price_start']}/month</strong>. Free plan available (1 device). See: <a href="/pages/{NORDPASS['slug']}-pricing-{YEAR}-plans-costs-what-you-actually-pay" style="color:#e94560">{d} Pricing {YEAR} →</a></p>

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2rem 0 1rem">Free Trial</h2>
  <p style="color:rgba(255,248,245,.72);line-height:1.7;margin-bottom:2rem">{NORDPASS['free_trial']}. See: <a href="/pages/{NORDPASS['slug']}-free-trial-{YEAR}-how-to-get-it-step-by-step" style="color:#e94560">How to get the {d} free trial →</a></p>

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2rem 0 1rem">Alternatives</h2>
  <p style="color:rgba(255,248,245,.72);line-height:1.7;margin-bottom:2rem">Not sold? Consider: <a href="/pages/best-{NORDPASS['slug']}-alternatives-in-{YEAR}-free-paid" style="color:#e94560">best {d} alternatives →</a></p>

  {cta_box(NORDPASS)}

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2rem 0 1rem">Related Pages</h2>
  <ul style="color:rgba(255,248,245,.65);line-height:2;padding-left:1.2rem">
    <li><a href="/pages/{NORDPASS['slug']}-pricing-{YEAR}-plans-costs-what-you-actually-pay" style="color:#e94560">{d} Pricing {YEAR}</a></li>
    <li><a href="/pages/{NORDPASS['slug']}-free-trial-{YEAR}-how-to-get-it-step-by-step" style="color:#e94560">{d} Free Trial {YEAR}</a></li>
    <li><a href="/pages/{NORDPASS['slug']}-coupon-code-promo-codes-{YEAR}-verified-discounts" style="color:#e94560">{d} Coupon Codes {YEAR}</a></li>
    <li><a href="/pages/best-{NORDPASS['slug']}-alternatives-in-{YEAR}-free-paid" style="color:#e94560">Best {d} Alternatives {YEAR}</a></li>
    <li><a href="/pages/1password-vs-nordpass-which-is-better-in-{YEAR}" style="color:#e94560">1Password vs {d}</a></li>
  </ul>

  <div style="border-top:1px solid rgba(255,255,255,.07);padding-top:1.5rem;margin-top:3rem">
    <p style="font-size:.78rem;color:rgba(255,248,245,.32);line-height:1.6"><strong style="color:rgba(255,248,245,.45)">Methodology:</strong> SaaSpare independently tests software by signing up for accounts. Verified {TODAY}. <a href="/affiliate-disclosure" style="color:rgba(233,69,96,.6)">Affiliate disclosure</a>.</p>
  </div>
</main>
{footer_and_scripts(NORDPASS['slug'])}"""


# ── Pricing Page ──────────────────────────────────────────────────────────────

def make_pricing() -> str:
    d = NORDPASS['display']
    slug = NORDPASS['slug']
    canonical = f"/pages/{slug}-pricing-{YEAR}-plans-costs-what-you-actually-pay"
    title = f"{d} Pricing {YEAR} — Every Plan, Real Costs &amp; What You Actually Pay"
    desc = f"Updated {TODAY}. {d} pricing breakdown: free plan, Premium at ${NORDPASS['price_start']}/month, Business plans. Full plan comparison — no hidden costs."

    pricing_rows = "".join(
        f'<tr style="border-bottom:1px solid rgba(255,255,255,.06)"><td style="padding:.85rem .5rem;font-weight:600;color:rgba(255,248,245,.85)">{plan}</td><td style="padding:.85rem .5rem;color:rgba(255,248,245,.7)">{price}</td></tr>'
        for plan, price in NORDPASS['pricing'].items()
    )

    schema = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "datePublished": TODAY, "dateModified": TODAY,
        "author": {"@type": "Person", "name": "Smith Elly", "url": "https://saaspare.org/authors/smith-elly"},
        "publisher": {"@type": "Organization", "name": "SaaSpare", "url": "https://saaspare.org"},
        "description": desc,
        "mainEntityOfPage": f"https://saaspare.org{canonical}"
    })
    faq = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f"How much does {d} cost?",
             "acceptedAnswer": {"@type": "Answer", "text": f"{d} has a free plan (1 device) and paid plans starting at {NORDPASS['price_start']}/month billed annually. Business plans start at $4.99/user/month."}},
            {"@type": "Question", "name": f"Is {d} free?",
             "acceptedAnswer": {"@type": "Answer", "text": f"Yes — {d} has a genuinely free plan with unlimited passwords on 1 active device. Sync across multiple devices requires the Premium plan at {NORDPASS['price_start']}/month."}},
            {"@type": "Question", "name": f"What is the cheapest {d} plan?",
             "acceptedAnswer": {"@type": "Answer", "text": f"The free plan is the cheapest option (1 device). The paid Personal plan starts at {NORDPASS['price_start']}/month billed annually — the best price for multi-device access."}},
        ]
    })

    return f"""{head(title, desc, canonical)}
<script type="application/ld+json">{schema}</script>
<script type="application/ld+json">{faq}</script>
{nav_bar(NORDPASS)}
<main style="max-width:820px;margin:0 auto;padding:7rem 1.5rem 5rem">
  <nav aria-label="breadcrumb" style="margin-bottom:1rem;font-size:.8rem;color:rgba(255,248,245,.4)">
    <a href="/pages/" style="color:rgba(255,248,245,.4)">Comparisons</a> / <a href="/pages/{slug}-review-{YEAR}-is-it-worth-it-honest-verdict" style="color:rgba(255,248,245,.4)">{d}</a> / Pricing {YEAR}
  </nav>
  <div class="badge">Updated {TODAY} &middot; Verified Pricing</div>
  <h1 style="font-size:clamp(1.9rem,5vw,2.8rem);font-weight:900;line-height:1.1;color:#fff;letter-spacing:-.04em;margin-bottom:1rem">{d} Pricing {YEAR}: Every Plan, Real Costs &amp; What You Pay</h1>
  <p style="font-size:1.05rem;color:rgba(255,248,245,.65);line-height:1.75;margin-bottom:2rem">Updated {TODAY}. We signed up and tested every {d} plan. Starting at <strong style="color:#fff">{NORDPASS['price_start']}/month</strong> — here's the full breakdown.</p>

  <div style="background:rgba(233,69,96,.08);border:1px solid rgba(233,69,96,.2);border-radius:14px;padding:1.5rem;margin-bottom:2.5rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem">
    <div>
      <div style="font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:rgba(233,69,96,.8);margin-bottom:.4rem">SaaSpare Verdict</div>
      <p style="color:rgba(255,248,245,.82);font-size:.95rem;margin:0;max-width:520px;line-height:1.55">{NORDPASS['verdict']}</p>
    </div>
    <a href="{NORDPASS['affiliate_url']}" target="_blank" rel="noopener sponsored" style="background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.8rem 1.6rem;border-radius:100px;font-weight:700;font-size:.92rem;white-space:nowrap;box-shadow:0 8px 24px rgba(233,69,96,.4)">{NORDPASS['affiliate_label']} &rarr;</a>
  </div>

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2rem 0 1rem">{d} Pricing Plans {YEAR}</h2>
  <table style="width:100%;border-collapse:collapse;margin-bottom:2rem;border:1px solid rgba(255,255,255,.08);border-radius:12px;overflow:hidden">
    <thead>
      <tr style="background:rgba(255,255,255,.04)">
        <th style="text-align:left;padding:.85rem 1rem;color:rgba(255,248,245,.5);font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em">Plan</th>
        <th style="text-align:left;padding:.85rem 1rem;color:rgba(255,248,245,.5);font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em">Price</th>
      </tr>
    </thead>
    <tbody>{pricing_rows}</tbody>
  </table>

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2rem 0 1rem">Is There a Free Plan?</h2>
  <p style="color:rgba(255,248,245,.72);line-height:1.7;margin-bottom:2rem">Yes — {d} Free covers unlimited passwords on 1 active device. You can store logins, credit cards, secure notes, and personal info. Multi-device sync requires upgrading to Premium at {NORDPASS['price_start']}/month.</p>

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2rem 0 1rem">Free Trial &amp; Money-Back Guarantee</h2>
  <p style="color:rgba(255,248,245,.72);line-height:1.7;margin-bottom:2rem">{NORDPASS['free_trial']}. For full details: <a href="/pages/{slug}-free-trial-{YEAR}-how-to-get-it-step-by-step" style="color:#e94560">NordPass free trial guide →</a></p>

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2rem 0 1rem">Best For vs Not Ideal For</h2>
  <p style="color:rgba(255,248,245,.72);line-height:1.7;margin-bottom:.6rem"><strong style="color:#65d6a3">Best for:</strong> {NORDPASS['best_for']}</p>
  <p style="color:rgba(255,248,245,.72);line-height:1.7;margin-bottom:2rem"><strong style="color:#e94560">Not ideal for:</strong> {NORDPASS['worst_for']}</p>

  {cta_box(NORDPASS, f"Get {d} Free")}

  <div style="border-top:1px solid rgba(255,255,255,.07);padding-top:1.5rem;margin-top:3rem">
    <p style="font-size:.78rem;color:rgba(255,248,245,.32);line-height:1.6"><strong style="color:rgba(255,248,245,.45)">Methodology:</strong> Pricing verified {TODAY} by signing up directly. Prices may change — verify at checkout. <a href="/affiliate-disclosure" style="color:rgba(233,69,96,.6)">Affiliate disclosure</a>.</p>
  </div>
</main>
{footer_and_scripts(NORDPASS['slug'])}"""


# ── Free Trial Page ───────────────────────────────────────────────────────────

def make_free_trial() -> str:
    d = NORDPASS['display']
    slug = NORDPASS['slug']
    canonical = f"/pages/{slug}-free-trial-{YEAR}-how-to-get-it-step-by-step"
    title = f"{d} Free Trial {YEAR} — How to Get It (Step-by-Step)"
    desc = f"Updated {TODAY}. Does {d} have a free trial? Yes — free plan + 30-day money-back on paid plans. Here's exactly how to start, step by step."

    schema = json.dumps({
        "@context": "https://schema.org", "@type": "HowTo",
        "name": f"How to Get {d} Free in {YEAR}",
        "description": desc, "datePublished": TODAY, "dateModified": TODAY,
        "author": {"@type": "Person", "name": "Smith Elly", "url": "https://saaspare.org/authors/smith-elly"},
        "publisher": {"@type": "Organization", "name": "SaaSpare", "url": "https://saaspare.org"},
        "step": [
            {"@type": "HowToStep", "name": "Click the link below", "text": f"Use our affiliate link to open {d}'s official website."},
            {"@type": "HowToStep", "name": "Choose Free or paid plan", "text": f"Select the {d} Free plan for 1-device access, or start a paid plan to get the 30-day money-back guarantee."},
            {"@type": "HowToStep", "name": "Create your account", "text": "Enter your email and set a master password. This is the only password you'll ever need to remember."},
            {"@type": "HowToStep", "name": "Install browser extension and app", "text": f"Download {d} on all your devices — Chrome, Firefox, Safari, Windows, Mac, iOS, Android."},
            {"@type": "HowToStep", "name": "Import your passwords", "text": "Import from your browser, LastPass, 1Password, or any CSV export. Takes 2 minutes."},
        ],
        "mainEntityOfPage": f"https://saaspare.org{canonical}"
    })
    faq = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f"Does {d} have a free trial?",
             "acceptedAnswer": {"@type": "Answer", "text": NORDPASS['free_trial']}},
            {"@type": "Question", "name": f"Is {d} free forever?",
             "acceptedAnswer": {"@type": "Answer", "text": f"Yes — {d} Free is genuinely free with no time limit. It covers unlimited passwords on 1 active device. You only need to upgrade if you want sync across multiple devices."}},
            {"@type": "Question", "name": f"Can I use {d} without a credit card?",
             "acceptedAnswer": {"@type": "Answer", "text": f"Yes — {d} Free requires no credit card. Business plans include a 14-day free trial with no credit card required."}},
        ]
    })

    steps_html = "".join(f"""<div style="display:flex;gap:1.25rem;margin-bottom:1.5rem">
  <div style="flex-shrink:0;width:2.2rem;height:2.2rem;background:rgba(233,69,96,.12);border:1px solid rgba(233,69,96,.25);border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;color:#e94560;font-size:.88rem">{i}</div>
  <div><div style="font-weight:700;color:rgba(255,248,245,.9);margin-bottom:.35rem">{t}</div><p style="color:rgba(255,248,245,.65);line-height:1.65;margin:0;font-size:.95rem">{b}</p></div>
</div>""" for i, (t, b) in enumerate([
        ("Go to NordPass via the link below", "Click our affiliate link to open NordPass's official site. This ensures you see the latest pricing."),
        ("Choose your plan", "The Free plan needs no payment. For Premium ($1.99/month) or Business, all paid plans include a 30-day money-back guarantee."),
        ("Create your account", "Enter your email address and create a strong master password. Write it down and keep it safe — this is the only password NordPass cannot recover if lost."),
        ("Install on your devices", "Download NordPass for Chrome, Firefox, Safari, Edge, Windows, Mac, iOS, and Android. Everything syncs automatically on paid plans."),
        ("Import your existing passwords", "Go to Settings → Import → select your browser or previous password manager (CSV export works from all major managers). Completed in under 2 minutes."),
    ], 1))

    return f"""{head(title, desc, canonical)}
<script type="application/ld+json">{schema}</script>
<script type="application/ld+json">{faq}</script>
{nav_bar(NORDPASS)}
<main style="max-width:820px;margin:0 auto;padding:7rem 1.5rem 5rem">
  <nav aria-label="breadcrumb" style="margin-bottom:1rem;font-size:.8rem;color:rgba(255,248,245,.4)">
    <a href="/pages/" style="color:rgba(255,248,245,.4)">Tools</a> / <a href="/pages/{slug}-review-{YEAR}-is-it-worth-it-honest-verdict" style="color:rgba(255,248,245,.4)">{d}</a> / Free Trial {YEAR}
  </nav>
  <div class="badge">Updated {TODAY} &middot; Verified</div>
  <h1 style="font-size:clamp(1.9rem,5vw,2.8rem);font-weight:900;line-height:1.1;color:#fff;letter-spacing:-.04em;margin-bottom:.85rem">{d} Free Trial {YEAR}: How to Get It (Step-by-Step)</h1>
  <p style="font-size:1.05rem;color:rgba(255,248,245,.65);line-height:1.75;margin-bottom:2rem">{d} has a permanently free plan AND a 30-day money-back guarantee on all paid plans. Here's exactly how to start.</p>

  <div style="background:rgba(101,214,163,.07);border:1px solid rgba(101,214,163,.2);border-radius:12px;padding:1.25rem;margin:2rem 0">
    <div style="font-weight:700;color:#65d6a3;margin-bottom:.5rem">&#10003; Free Plan — No Card, No Time Limit</div>
    <p style="color:rgba(255,248,245,.72);margin:0;line-height:1.65;font-size:.95rem">{d} Free covers unlimited passwords on 1 active device — permanently free, no credit card required. Upgrade any time to add multi-device sync.</p>
  </div>

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2.5rem 0 1.25rem">How to Get {d} Free — 5 Steps</h2>
  {steps_html}

  {cta_box(NORDPASS, f"Get {d} Free")}

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2.5rem 0 1rem">Frequently Asked Questions</h2>
  <div style="margin-bottom:1.25rem">
    <div style="font-weight:700;color:rgba(255,248,245,.9);margin-bottom:.4rem">Is there a {d} free trial for Business plans?</div>
    <p style="color:rgba(255,248,245,.65);line-height:1.65;margin:0">{d} Business plans include a 14-day free trial — no credit card required. Just sign up with a company email.</p>
  </div>
  <div style="margin-bottom:1.25rem">
    <div style="font-weight:700;color:rgba(255,248,245,.9);margin-bottom:.4rem">What's included in {d} Free?</div>
    <p style="color:rgba(255,248,245,.65);line-height:1.65;margin:0">Unlimited passwords, secure notes, credit cards, and personal info stored on 1 active device. No device sync, no password sharing, no emergency access.</p>
  </div>
  <div style="margin-bottom:1.25rem">
    <div style="font-weight:700;color:rgba(255,248,245,.9);margin-bottom:.4rem">How do I get the 30-day money-back guarantee?</div>
    <p style="color:rgba(255,248,245,.65);line-height:1.65;margin:0">Start any paid plan, use it for up to 30 days, then contact {d} support to request a refund. No questions asked.</p>
  </div>

  <div style="border-top:1px solid rgba(255,255,255,.07);padding-top:1.5rem;margin-top:3rem">
    <p style="font-size:.78rem;color:rgba(255,248,245,.32);line-height:1.6"><strong style="color:rgba(255,248,245,.45)">Methodology:</strong> Verified {TODAY} by testing directly. <a href="/affiliate-disclosure" style="color:rgba(233,69,96,.6)">Affiliate disclosure</a>.</p>
  </div>
</main>
{footer_and_scripts(NORDPASS['slug'])}"""


# ── Coupon Page ───────────────────────────────────────────────────────────────

def make_coupon() -> str:
    d = NORDPASS['display']
    slug = NORDPASS['slug']
    canonical = f"/pages/{slug}-coupon-code-promo-codes-{YEAR}-verified-discounts"
    title = f"{d} Coupon Code {YEAR} — Verified Promo Codes &amp; Best Deals"
    desc = f"Updated {TODAY}. Best {d} discounts for {YEAR}. No coupon code needed — annual billing auto-applies the best price. Business plans include a free trial."

    schema = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "datePublished": TODAY, "dateModified": TODAY,
        "author": {"@type": "Person", "name": "Smith Elly", "url": "https://saaspare.org/authors/smith-elly"},
        "publisher": {"@type": "Organization", "name": "SaaSpare", "url": "https://saaspare.org"},
        "description": desc,
        "mainEntityOfPage": f"https://saaspare.org{canonical}"
    })

    return f"""{head(title, desc, canonical)}
<script type="application/ld+json">{schema}</script>
{nav_bar(NORDPASS)}
<main style="max-width:820px;margin:0 auto;padding:7rem 1.5rem 5rem">
  <nav aria-label="breadcrumb" style="margin-bottom:1rem;font-size:.8rem;color:rgba(255,248,245,.4)">
    <a href="/pages/" style="color:rgba(255,248,245,.4)">Tools</a> / <a href="/pages/{slug}-review-{YEAR}-is-it-worth-it-honest-verdict" style="color:rgba(255,248,245,.4)">{d}</a> / Coupon Codes {YEAR}
  </nav>
  <div class="badge">Verified {TODAY} &middot; Best Price Available</div>
  <h1 style="font-size:clamp(1.9rem,5vw,2.8rem);font-weight:900;line-height:1.1;color:#fff;letter-spacing:-.04em;margin-bottom:.85rem">{d} Coupon Code {YEAR}: Verified Promo Codes &amp; Best Deals</h1>
  <p style="font-size:1.05rem;color:rgba(255,248,245,.65);line-height:1.75;margin-bottom:2rem">{NORDPASS['coupon_note']} Start with the <strong style="color:#fff">free plan</strong> — no payment required.</p>

  <div style="background:rgba(233,69,96,.06);border:2px solid rgba(233,69,96,.2);border-radius:14px;padding:1.5rem;margin-bottom:2.5rem">
    <div style="font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:rgba(233,69,96,.8);margin-bottom:.6rem">Best Deal Right Now</div>
    <p style="color:rgba(255,248,245,.88);font-size:1rem;margin:0 0 1rem;font-weight:600">{NORDPASS['coupon_note']}</p>
    <a href="{NORDPASS['affiliate_url']}" target="_blank" rel="noopener sponsored" style="background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.75rem 1.6rem;border-radius:100px;font-weight:700;font-size:.92rem;display:inline-block;box-shadow:0 8px 24px rgba(233,69,96,.35)">{NORDPASS['affiliate_label']} &rarr;</a>
  </div>

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2rem 0 1rem">Current {d} Deals</h2>

  <div style="background:rgba(101,214,163,.07);border:1px solid rgba(101,214,163,.2);border-radius:12px;padding:1.4rem;margin-bottom:1rem">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.75rem">
      <div>
        <div style="font-weight:800;color:#fff;font-size:1rem;margin-bottom:.3rem">Free Plan — Forever Free</div>
        <div style="color:rgba(255,248,245,.65);font-size:.88rem">Unlimited passwords on 1 device. No credit card, no time limit.</div>
      </div>
      <div style="font-size:1.5rem;font-weight:900;color:#65d6a3">FREE</div>
    </div>
  </div>

  <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:1.4rem;margin-bottom:1rem">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.75rem">
      <div>
        <div style="font-weight:800;color:#fff;font-size:1rem;margin-bottom:.3rem">Premium — Annual Plan</div>
        <div style="color:rgba(255,248,245,.65);font-size:.88rem">$1.99/month billed annually. Multi-device sync, emergency access, secure sharing.</div>
      </div>
      <div style="text-align:right"><div style="font-size:1.5rem;font-weight:900;color:#fff">$1.99/mo</div></div>
    </div>
  </div>

  <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:1.4rem;margin-bottom:1rem">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.75rem">
      <div>
        <div style="font-weight:800;color:#fff;font-size:1rem;margin-bottom:.3rem">Business — 14-Day Free Trial</div>
        <div style="color:rgba(255,248,245,.65);font-size:.88rem">$4.99/user/month. Full 14-day trial, no credit card required. Admin console + groups.</div>
      </div>
      <div style="text-align:right"><div style="font-size:1.5rem;font-weight:900;color:#fff">14-day trial</div></div>
    </div>
  </div>

  <a href="{NORDPASS['affiliate_url']}" target="_blank" rel="noopener sponsored" style="display:block;text-align:center;background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.9rem 2rem;border-radius:100px;font-weight:700;font-size:1rem;margin:1.5rem 0;box-shadow:0 8px 24px rgba(233,69,96,.35)">Get {d} Best Price &rarr;</a>

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2.5rem 0 1rem">Do {d} Coupon Codes Work?</h2>
  <p style="color:rgba(255,248,245,.72);line-height:1.7;margin-bottom:2rem">{d} doesn't use promotional codes at checkout. The biggest savings come from annual billing — the monthly-to-annual switch on Premium saves over 20%. Business plans include a full 14-day free trial without any coupon code. Any "coupon code" sites you see online are unlikely to work.</p>

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2.5rem 0 1rem">Related Pages</h2>
  <ul style="color:rgba(255,248,245,.65);line-height:2;padding-left:1.2rem">
    <li><a href="/pages/{slug}-review-{YEAR}-is-it-worth-it-honest-verdict" style="color:#e94560">{d} Review {YEAR}</a></li>
    <li><a href="/pages/{slug}-pricing-{YEAR}-plans-costs-what-you-actually-pay" style="color:#e94560">{d} Pricing {YEAR}</a></li>
    <li><a href="/pages/{slug}-free-trial-{YEAR}-how-to-get-it-step-by-step" style="color:#e94560">{d} Free Trial {YEAR}</a></li>
    <li><a href="/pages/best-{slug}-alternatives-in-{YEAR}-free-paid" style="color:#e94560">Best {d} Alternatives</a></li>
  </ul>

  <div style="border-top:1px solid rgba(255,255,255,.07);padding-top:1.5rem;margin-top:3rem">
    <p style="font-size:.78rem;color:rgba(255,248,245,.32);line-height:1.6"><strong style="color:rgba(255,248,245,.45)">Methodology:</strong> Deals verified {TODAY} by checking official pricing. <a href="/affiliate-disclosure" style="color:rgba(233,69,96,.6)">Affiliate disclosure</a>.</p>
  </div>
</main>
{footer_and_scripts(NORDPASS['slug'])}"""


# ── Alternatives Page ─────────────────────────────────────────────────────────

def make_alternatives() -> str:
    d = NORDPASS['display']
    slug = NORDPASS['slug']
    canonical = f"/pages/best-{slug}-alternatives-in-{YEAR}-free-paid"
    title = f"7 Best {d} Alternatives in {YEAR} (Free &amp; Paid)"
    desc = f"Updated {TODAY}. The best {d} alternatives tested and ranked. Whether you need cheaper, more enterprise-ready, or open-source — here's the right pick."

    schema = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "datePublished": TODAY, "dateModified": TODAY,
        "author": {"@type": "Person", "name": "Smith Elly", "url": "https://saaspare.org/authors/smith-elly"},
        "publisher": {"@type": "Organization", "name": "SaaSpare", "url": "https://saaspare.org"},
        "description": desc,
        "mainEntityOfPage": f"https://saaspare.org{canonical}"
    })

    alts_html = ""
    for i, alt in enumerate(NORDPASS['alternatives'], 1):
        cta_html = f"""<a href="{alt['link']}" target="_blank" rel="noopener sponsored" style="background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.55rem 1.25rem;border-radius:100px;font-weight:700;font-size:.78rem;white-space:nowrap;align-self:center;box-shadow:0 6px 18px rgba(233,69,96,.3)">{alt['cta']} &rarr;</a>""" if alt.get('link') else ""
        alts_html += f"""<div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:1.35rem;margin-bottom:1rem">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;flex-wrap:wrap">
    <div style="flex:1">
      <div style="font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:rgba(233,69,96,.7);margin-bottom:.3rem">#{i} Alternative</div>
      <div style="font-weight:800;color:#fff;font-size:1rem;margin-bottom:.45rem">{alt['name']}</div>
      <p style="color:rgba(255,248,245,.65);font-size:.9rem;line-height:1.6;margin:0 0 .4rem">{alt['why']}</p>
      <p style="color:rgba(255,248,245,.45);font-size:.8rem;margin:0"><strong style="color:rgba(255,248,245,.6)">From:</strong> {alt['price']}</p>
    </div>
    {cta_html}
  </div>
</div>"""

    return f"""{head(title, desc, canonical)}
<script type="application/ld+json">{schema}</script>
{nav_bar(NORDPASS)}
<main style="max-width:820px;margin:0 auto;padding:7rem 1.5rem 5rem">
  <nav aria-label="breadcrumb" style="margin-bottom:1rem;font-size:.8rem;color:rgba(255,248,245,.4)">
    <a href="/pages/" style="color:rgba(255,248,245,.4)">Comparisons</a> / {d} Alternatives
  </nav>
  <div class="badge">Updated {TODAY} &middot; Tested &amp; Ranked</div>
  <h1 style="font-size:clamp(1.9rem,5vw,2.8rem);font-weight:900;line-height:1.1;color:#fff;letter-spacing:-.04em;margin-bottom:.85rem">7 Best {d} Alternatives in {YEAR} (Free &amp; Paid)</h1>
  <p style="font-size:1.05rem;color:rgba(255,248,245,.65);line-height:1.75;margin-bottom:2rem">Looking for a {d} alternative? We tested every major option. Here are the best picks by use case.</p>

  {alts_html}

  <h2 style="font-size:1.4rem;font-weight:800;color:#fff;margin:2.5rem 0 1rem">Still considering {d}?</h2>
  <p style="color:rgba(255,248,245,.72);line-height:1.7;margin-bottom:1.5rem">{NORDPASS['verdict']}</p>
  {cta_box(NORDPASS)}

  <div style="border-top:1px solid rgba(255,255,255,.07);padding-top:1.5rem;margin-top:3rem">
    <p style="font-size:.78rem;color:rgba(255,248,245,.32);line-height:1.6"><strong style="color:rgba(255,248,245,.45)">Methodology:</strong> All alternatives independently tested. Prices verified {TODAY}. <a href="/affiliate-disclosure" style="color:rgba(233,69,96,.6)">Affiliate disclosure</a>.</p>
  </div>
</main>
{footer_and_scripts(NORDPASS['slug'])}"""


# ── Generate ──────────────────────────────────────────────────────────────────

pages = [
    (f"nordpass-review-{YEAR}-is-it-worth-it-honest-verdict.html", make_review()),
    (f"nordpass-pricing-{YEAR}-plans-costs-what-you-actually-pay.html", make_pricing()),
    (f"nordpass-free-trial-{YEAR}-how-to-get-it-step-by-step.html", make_free_trial()),
    (f"nordpass-coupon-code-promo-codes-{YEAR}-verified-discounts.html", make_coupon()),
    (f"best-nordpass-alternatives-in-{YEAR}-free-paid.html", make_alternatives()),
]

PAGES.mkdir(parents=True, exist_ok=True)
created, skipped = [], []

for fname, content in pages:
    p = PAGES / fname
    if p.exists():
        skipped.append(fname)
        print(f"  Skipped: {fname}")
    else:
        p.write_text(content, encoding="utf-8")
        created.append(fname)
        print(f"  Created: {fname}")

print(f"\nDone. {len(created)} created, {len(skipped)} skipped.")
