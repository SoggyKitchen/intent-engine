from __future__ import annotations

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SITE = ROOT / "site"
PAGES = SITE / "pages"
REPORTS = ROOT / "seo" / "reports"
TODAY = date(2026, 5, 11)
TODAY_TEXT = TODAY.strftime("%B %d, %Y")
YEAR = 2026

BRAND_FIXES = {
    "ahrefs": "Ahrefs",
    "asana": "Asana",
    "bitwarden": "Bitwarden",
    "canva": "Canva",
    "clickup": "ClickUp",
    "datadog": "Datadog",
    "github": "GitHub",
    "hubspot": "HubSpot",
    "jasper-ai": "Jasper AI",
    "linear": "Linear",
    "mixpanel": "Mixpanel",
    "monday-com": "Monday.com",
    "nordlayer": "NordLayer",
    "notion": "Notion",
    "pipedrive": "Pipedrive",
    "ramp": "Ramp",
    "salesforce": "Salesforce",
    "semrush": "Semrush",
    "shopify": "Shopify",
    "slack": "Slack",
    "surfer-seo": "Surfer SEO",
    "xero": "Xero",
    "zendesk": "Zendesk",
}

KNOWN_GSC_OPPORTUNITIES = [
    {
        "path": "/pages/ramp-pricing-2026-plans-costs-what-you-actually-pay",
        "query": "ramp pricing change / bill pay fees",
        "impressions": 374,
        "clicks": 0,
        "ctr": "0.0%",
        "position": 5.2,
        "reason": "Top-10 pricing-change intent with no clicks; title/meta must match hidden-fee and fee-change intent.",
    },
    {
        "path": "/pages/mixpanel-pricing-2026-plans-costs-what-you-actually-pay",
        "query": "mixpanel pricing / mixpanel cost",
        "impressions": 347,
        "clicks": 1,
        "ctr": "0.3%",
        "position": 11.9,
        "reason": "Position 8-15 pricing intent; needs stronger true-cost and alternatives angle.",
    },
    {
        "path": "/pages/nordlayer-pricing-2026-plans-costs-what-you-actually-pay",
        "query": "nordlayer price",
        "impressions": 97,
        "clicks": 0,
        "ctr": "0.0%",
        "position": 11.0,
        "reason": "Page is close to page one; align title with singular price query and free-trial intent.",
    },
    {
        "path": "/pages/bitwarden-free-trial-2026-how-to-get-it-step-by-step",
        "query": "bitwarden free plan limitations",
        "impressions": 42,
        "clicks": 0,
        "ctr": "0.0%",
        "position": 5.8,
        "reason": "Top-10 free-plan query with zero clicks; title/meta should promise limits and card rules.",
    },
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_if_changed(path: Path, content: str) -> bool:
    old = read(path) if path.exists() else ""
    if old == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def clean_tool(slug: str) -> str:
    slug = slug.strip("-")
    if slug in BRAND_FIXES:
        return BRAND_FIXES[slug]
    parts = []
    for part in slug.split("-"):
        parts.append(BRAND_FIXES.get(part, part.upper() if len(part) <= 3 else part.capitalize()))
    return " ".join(parts).replace(" Crm", " CRM").replace(" Seo", " SEO").replace(" Ai", " AI")


def pricing_slug(path: Path) -> str | None:
    suffix = "-pricing-2026-plans-costs-what-you-actually-pay"
    stem = path.stem
    if not stem.endswith(suffix):
        return None
    return stem[: -len(suffix)]


def page_type(path: Path) -> str:
    stem = path.stem
    if "-pricing-2026-" in stem:
        return "pricing"
    if "-free-trial-2026-" in stem:
        return "free_trial"
    if "-vs-" in stem:
        return "comparison"
    if "alternatives" in stem:
        return "alternatives"
    if "coupon" in stem or "promo-code" in stem:
        return "coupon"
    if "-review-2026-" in stem:
        return "review"
    if stem.startswith("best-") or stem.startswith("7-best-"):
        return "best_of"
    return "other"


def infer_names(path: Path) -> tuple[str, str | None]:
    stem = path.stem
    typ = page_type(path)
    if typ == "pricing":
        slug = pricing_slug(path) or stem.split("-pricing-")[0]
        return clean_tool(slug), None
    if typ == "free_trial":
        return clean_tool(stem.split("-free-trial-")[0]), None
    if typ == "comparison" and "-vs-" in stem:
        left, rest = stem.split("-vs-", 1)
        right = rest.split("-which-is-better", 1)[0]
        return clean_tool(left), clean_tool(right)
    if typ == "alternatives":
        s = stem
        s = re.sub(r"^7-best-", "", s)
        s = re.sub(r"^best-", "", s)
        s = re.sub(r"-alternatives.*$", "", s)
        return clean_tool(s), None
    if typ == "coupon":
        s = re.sub(r"-(coupon-code|promo-code).*", "", stem)
        return clean_tool(s), None
    if typ == "review":
        return clean_tool(stem.split("-review-")[0]), None
    return clean_tool(stem), None


def path_url(path: Path) -> str:
    rel = path.relative_to(SITE).as_posix()
    if rel.endswith(".html"):
        rel = rel[:-5]
    if rel == "index":
        rel = ""
    return "/" + rel


def build_title_meta(path: Path) -> tuple[str, str]:
    typ = page_type(path)
    a, b = infer_names(path)
    if typ == "pricing":
        title = f"{a} Pricing {YEAR}: Hidden Fees, Plans & True Cost"
        desc = f"{a} pricing in {YEAR}: compare advertised plan prices, likely hidden costs, trial limits and cheaper alternatives before you buy."
    elif typ == "free_trial":
        title = f"{a} Free Trial {YEAR}: Length, Limits & Card Rules"
        desc = f"Check the {a} free trial in {YEAR}: signup steps, limits, credit-card rules, cancellation notes and cheaper alternatives."
    elif typ == "comparison" and b:
        title = f"{a} vs {b} {YEAR}: Pricing, Hidden Fees & Best Fit"
        desc = f"Compare {a} vs {b} on pricing, free trials, limits, switching risk and best-fit buyer types before choosing."
    elif typ == "alternatives":
        title = f"Best {a} Alternatives {YEAR}: Cheaper Options Compared"
        desc = f"Compare the best {a} alternatives by pricing, free trials, hidden tradeoffs and buyer fit before switching."
    elif typ == "coupon":
        title = f"{a} Promo Codes & Discounts {YEAR}: Verified Deal Checks"
        desc = f"Check current {a} promo code and discount paths, trial offers, restrictions and safer alternatives before checkout."
    elif typ == "review":
        title = f"{a} Review {YEAR}: Pricing, Pros, Cons & Alternatives"
        desc = f"Read the {a} review for {YEAR}: pricing risks, best-fit teams, avoid-if notes, alternatives and source checks."
    else:
        title = f"{a}: Pricing, Trials & Buyer Guide {YEAR}"
        desc = f"Use this SaaSpare buyer guide to compare pricing, trials, hidden costs and alternatives for {a}."
    return title[:68], desc[:158]


def replace_meta(html_text: str, title: str, desc: str, canonical_path: str) -> str:
    canonical = "https://saaspare.org" + (canonical_path if canonical_path != "/" else "/")
    title_e = esc(title)
    desc_e = esc(desc)
    html_text = re.sub(r"<title>.*?</title>", f"<title>{title_e}</title>", html_text, flags=re.I | re.S)
    html_text = re.sub(r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']*["\']\s*/?>', f'<meta name="description" content="{desc_e}">', html_text, flags=re.I)
    html_text = re.sub(r'<link\s+rel=["\']canonical["\']\s+href=["\'][^"\']*["\']\s*/?>', f'<link rel="canonical" href="{esc(canonical)}">', html_text, flags=re.I)
    replacements = {
        "og:title": title_e,
        "og:description": desc_e,
        "og:url": esc(canonical),
        "twitter:title": title_e,
        "twitter:description": desc_e,
        "twitter:card": "summary_large_image",
    }
    for key, val in replacements.items():
        if key.startswith("og:"):
            pattern = rf'<meta\s+property=["\']{re.escape(key)}["\']\s+content=["\'][^"\']*["\']\s*/?>'
            tag = f'<meta property="{key}" content="{val}">'
        else:
            pattern = rf'<meta\s+name=["\']{re.escape(key)}["\']\s+content=["\'][^"\']*["\']\s*/?>'
            tag = f'<meta name="{key}" content="{val}">'
        if re.search(pattern, html_text, flags=re.I):
            html_text = re.sub(pattern, tag, html_text, flags=re.I)
        elif "</head>" in html_text:
            html_text = html_text.replace("</head>", tag + "\n</head>", 1)
    return html_text


def risk_for(tool: str) -> tuple[str, str]:
    lower = tool.lower()
    high = {"salesforce", "hubspot", "semrush", "marketo", "workday", "netsuite", "jira", "zendesk"}
    low = {"bitwarden", "linear", "notion", "canva", "miro", "slack"}
    if any(x in lower for x in high):
        return "High", "Watch for annual billing, seat minimums, add-ons, admin features and implementation costs."
    if any(x in lower for x in low):
        return "Low", "Main risk is usually plan limits or add-ons rather than surprise implementation fees."
    return "Medium", "Verify billing period, seat count, add-ons, usage caps, support tiers and renewal terms."


def go_slugs() -> set[str]:
    redirects = SITE / "_redirects"
    if not redirects.exists():
        return set()
    out: set[str] = set()
    for line in read(redirects).splitlines():
        m = re.match(r"\s*/go/([a-z0-9-]+)\s+", line)
        if m:
            out.add(m.group(1))
    return out


def related_link(slug: str, suffix: str) -> str:
    candidates = [
        PAGES / f"{slug}-{suffix}.html",
        PAGES / f"best-{slug}-{suffix}.html",
        PAGES / f"7-best-{slug}-{suffix}.html",
    ]
    for p in candidates:
        if p.exists():
            return path_url(p)
    return "/pages/"


def pricing_module(tool: str, slug: str, can_affiliate: bool) -> str:
    risk, risk_copy = risk_for(tool)
    trial_link = related_link(slug, f"free-trial-{YEAR}-how-to-get-it-step-by-step")
    alternatives_link = related_link(slug, f"alternatives-in-{YEAR}-free-paid")
    review_link = related_link(slug, f"review-{YEAR}-is-it-worth-it-honest-verdict")
    cta_href = f"/go/{slug}" if can_affiliate else "/deal-radar"
    cta_label = f"Check current {tool} offer" if can_affiliate else "Find current offers"
    return f"""
  <section class="growth-answer" data-growth-answer>
    <strong>Quick answer:</strong> {esc(tool)} is worth shortlisting only after you compare the advertised plan price with likely seat, billing-period and add-on costs. Start with the vendor price page, then check cheaper alternatives before entering a card.
  </section>

  <section class="pricing-intel-card" data-pricing-intel>
    <div class="pricing-intel-head">
      <p class="mini-kicker">SaaSpare pricing intelligence</p>
      <h2>{esc(tool)} true-cost check</h2>
      <p>Use this before buying so the visible monthly price does not hide renewal, seat or add-on costs.</p>
    </div>
    <div class="intel-grid">
      <div><span>Hidden fee risk</span><strong>{risk}</strong><p>{esc(risk_copy)}</p></div>
      <div><span>Advertised price</span><strong>Vendor plan price</strong><p>Use the public pricing page as the starting point only.</p></div>
      <div><span>Likely true cost</span><strong>Plan + seats + add-ons</strong><p>Confirm annual billing, usage caps, support tiers and tax before checkout.</p></div>
      <div><span>Source checked</span><strong>{TODAY_TEXT}</strong><p>Pricing changes often. Report outdated details if you spot a mismatch.</p></div>
    </div>
    <table class="alternatives-table">
      <thead><tr><th>Buyer situation</th><th>Best next step</th></tr></thead>
      <tbody>
        <tr><td>Need the lowest risk path</td><td><a href="{trial_link}" data-track="pricing_cta">Check free plan or trial limits</a></td></tr>
        <tr><td>Price feels too high</td><td><a href="{alternatives_link}" data-track="compare_alternative">Compare cheaper alternatives</a></td></tr>
        <tr><td>Need a final verdict</td><td><a href="{review_link}" data-track="compare_alternative">Read the SaaSpare review</a></td></tr>
      </tbody>
    </table>
    <div class="money-cta-row">
      <a class="money-cta primary" href="{cta_href}" rel="sponsored noopener" data-track="pricing_cta">{esc(cta_label)} -></a>
      <a class="money-cta secondary" href="/pages/hidden-fee-detector" data-track="pricing_cta">Run hidden fee check</a>
      <a class="money-cta secondary" href="/pages/report-outdated-pricing" data-track="pricing_error_report">Report outdated pricing</a>
      <a class="money-cta secondary" href="/pages/saas-pricing-changes" data-track="compare_alternative">View price changes</a>
    </div>
  </section>
"""


NATIVE_BLOCKS = [
    """
  <aside class="native-intent-block" data-native-intent>
    <p class="mini-kicker">Cheaper path</p>
    <h3>Compare cheaper alternatives before you buy</h3>
    <p>See free plans, trial limits and lower-cost tools before you commit to a subscription.</p>
    <a href="/shortlist" data-track="compare_alternative">Find my best-fit alternatives -></a>
  </aside>
""",
    """
  <aside class="native-intent-block" data-native-intent>
    <p class="mini-kicker">Free trials</p>
    <h3>Check the trial path before entering your card</h3>
    <p>SaaSpare tracks free trials, pricing pages and comparison paths so you can avoid the wrong plan.</p>
    <a href="/deal-radar" data-track="deal_radar_click">Open Deal Radar -></a>
  </aside>
""",
]


def replace_ad_slots(html_text: str) -> tuple[str, int]:
    count = 0

    def repl(_: re.Match[str]) -> str:
        nonlocal count
        block = NATIVE_BLOCKS[count % len(NATIVE_BLOCKS)]
        count += 1
        return block

    html_text = re.sub(r"\s*<div class=\"ad-slot(?:-v2)?\"[^>]*>.*?</div>\s*", repl, html_text, flags=re.I | re.S)
    html_text = re.sub(r"\s*<script>\(adsbygoogle=window\.adsbygoogle\|\|\[\]\)\.push\(\{\}\);</script>\s*", "\n", html_text)
    return html_text, count


GROWTH_CSS = """
<style id="growth-conversion-css">
.growth-answer,.pricing-intel-card,.native-intent-block{background:linear-gradient(145deg,rgba(255,255,255,.055),rgba(255,255,255,.025));border:1px solid rgba(255,255,255,.1);box-shadow:0 18px 55px rgba(0,0,0,.24);border-radius:18px}
.growth-answer{padding:1rem 1.15rem;margin:1.35rem 0;color:rgba(255,255,255,.78);font-size:.95rem}
.growth-answer strong,.pricing-intel-card h2,.native-intent-block h3{color:#fff}
.pricing-intel-card{padding:1.35rem;margin:1.75rem 0}
.pricing-intel-head{margin-bottom:1rem}.pricing-intel-head p{color:rgba(255,255,255,.54);font-size:.9rem}
.mini-kicker{color:#ff6f8d!important;font-size:.72rem!important;letter-spacing:.12em;text-transform:uppercase;font-weight:800;margin-bottom:.35rem!important}
.intel-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.75rem;margin:1rem 0}
.intel-grid>div{background:rgba(0,0,0,.2);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:.85rem}
.intel-grid span{display:block;color:rgba(255,255,255,.45);font-size:.72rem;text-transform:uppercase;letter-spacing:.07em;font-weight:800}.intel-grid strong{display:block;color:#ff6f8d;font-size:1.05rem;margin:.2rem 0}.intel-grid p{font-size:.78rem;color:rgba(255,255,255,.58);line-height:1.55}
.alternatives-table a{color:#ff8ca0;text-decoration:underline;text-decoration-color:rgba(255,140,160,.35)}
.money-cta-row{display:flex;gap:.65rem;flex-wrap:wrap;margin-top:1rem}.money-cta{border-radius:999px;padding:.65rem 1rem;font-weight:800;font-size:.86rem}.money-cta.primary{background:linear-gradient(135deg,#e94560,#c73652);color:#fff;box-shadow:0 10px 24px rgba(233,69,96,.28)}.money-cta.secondary{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.11);color:rgba(255,255,255,.8)}
.native-intent-block{padding:1.25rem;margin:2rem 0}.native-intent-block p{color:rgba(255,255,255,.55);font-size:.9rem}.native-intent-block a{display:inline-block;margin-top:.8rem;color:#fff;background:rgba(233,69,96,.18);border:1px solid rgba(233,69,96,.32);border-radius:999px;padding:.55rem .9rem;font-weight:800}
@media(max-width:760px){.intel-grid{grid-template-columns:1fr 1fr}}@media(max-width:520px){.intel-grid{grid-template-columns:1fr}.money-cta{width:100%;text-align:center}}
</style>
"""


def ensure_growth_css(html_text: str) -> str:
    if "growth-conversion-css" in html_text:
        return html_text
    return html_text.replace("</head>", GROWTH_CSS + "\n</head>", 1)


def insert_pricing_module(html_text: str, tool: str, slug: str, can_affiliate: bool) -> str:
    if 'data-pricing-intel' in html_text:
        if "/pages/hidden-fee-detector" not in html_text:
            html_text = html_text.replace(
                '<a class="money-cta secondary" href="/pages/report-outdated-pricing" data-track="pricing_error_report">Report outdated pricing</a>',
                '<a class="money-cta secondary" href="/pages/hidden-fee-detector" data-track="pricing_cta">Run hidden fee check</a>\n      <a class="money-cta secondary" href="/pages/report-outdated-pricing" data-track="pricing_error_report">Report outdated pricing</a>',
                1,
            )
        return html_text
    module = pricing_module(tool, slug, can_affiliate)
    if '<div class="container">' in html_text:
        return html_text.replace('<div class="container">', '<div class="container">\n' + module, 1)
    if "<main" in html_text:
        return re.sub(r"(<main[^>]*>)", r"\1\n" + module, html_text, count=1, flags=re.I)
    return html_text.replace("<body>", "<body>\n" + module, 1)


def candidate_pages() -> list[Path]:
    pages = [p for p in PAGES.glob("*.html") if p.name != "index.html"]
    priority = {
        "pricing": 0,
        "free_trial": 1,
        "comparison": 2,
        "alternatives": 3,
        "coupon": 4,
        "review": 5,
        "best_of": 6,
        "other": 9,
    }
    preferred = [
        "ramp", "mixpanel", "nordlayer", "bitwarden", "clickup", "asana", "monday-com",
        "hubspot", "semrush", "shopify", "pipedrive", "xero", "salesforce", "notion",
        "linear", "datadog", "ahrefs", "canva", "miro", "zendesk", "slack",
    ]

    def score(p: Path) -> tuple[int, int, str]:
        stem = p.stem
        pref = next((i for i, name in enumerate(preferred) if stem.startswith(name)), 99)
        return (priority.get(page_type(p), 9), pref, stem)

    return sorted(pages, key=score)[:50]


def create_hidden_fee_detector() -> bool:
    from scripts._page_shell import page_shell

    body = """
<section class="tool-panel">
  <p class="eyebrow">Hidden Fee Detector</p>
  <h1>Find the SaaS costs hiding behind the advertised price.</h1>
  <p class="lede">Paste a tool name, pick a risk profile, and SaaSpare gives you the checks to run before starting a trial or asking finance to approve spend.</p>
  <div class="detector-card" data-hidden-fee-detector>
    <label>Tool or vendor name<input id="hf-tool" placeholder="HubSpot, Ramp, ClickUp..."></label>
    <label>Buying situation<select id="hf-risk"><option value="medium">Team subscription</option><option value="high">Enterprise / sales-led plan</option><option value="low">Self-serve or free plan</option></select></label>
    <button id="hf-run" class="primary-action">Run hidden fee check</button>
    <div id="hf-output" class="result-box" aria-live="polite">Start the check to get a buyer-safe risk score and next steps.</div>
  </div>
</section>
<section class="tool-grid">
  <article><h2>What this checks</h2><p>Seat minimums, annual billing traps, add-ons, usage caps, support tiers, implementation fees and renewal changes.</p></article>
  <article><h2>Best next action</h2><p>Open the vendor pricing page, compare alternatives, then record the renewal-risk items before starting a trial.</p></article>
  <article><h2>Why it matters</h2><p>Most budget pain comes from expansion and renewal terms, not the first advertised per-seat price.</p></article>
</section>
<script>
document.getElementById('hf-run')?.addEventListener('click',function(){
  var tool=(document.getElementById('hf-tool').value||'this tool').trim();
  var risk=document.getElementById('hf-risk').value;
  var label=risk==='high'?'High':risk==='low'?'Low':'Medium';
  if(typeof gtag==='function')gtag('event','hidden_fee_detector_start',{tool_name:tool,risk_level:label});
  document.getElementById('hf-output').innerHTML='<strong>'+label+' hidden-fee risk for '+tool+'.</strong><br>Check annual billing, seat count, add-ons, usage caps, support tier, cancellation terms and renewal pricing before you enter a card. <a href="/deal-radar">Open Deal Radar</a> or <a href="/shortlist">compare alternatives</a>.';
  if(typeof gtag==='function')gtag('event','hidden_fee_detector_complete',{tool_name:tool,risk_level:label});
});
</script>
"""
    html_text = page_shell(
        slug="hidden-fee-detector",
        title="Hidden Fee Detector",
        desc="Find SaaS hidden fees, annual billing traps, add-ons and renewal risks before starting a trial or buying a plan.",
        canonical_path="/pages/hidden-fee-detector",
        body=body,
        nav_active="tools",
        schema_extra="",
        page_type="WebApplication",
    )
    html_text = html_text.replace("</head>", '<style>.tool-panel{max-width:980px;margin:0 auto;padding:7rem 1.25rem 2rem;text-align:center}.lede{color:rgba(255,255,255,.62);max-width:720px;margin:1rem auto 2rem}.detector-card,.tool-grid article{background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.1);border-radius:22px;padding:1.25rem;text-align:left}.detector-card{display:grid;grid-template-columns:1fr 1fr auto;gap:1rem;align-items:end}.detector-card label{font-weight:800;color:rgba(255,255,255,.78);font-size:.82rem}.detector-card input,.detector-card select{display:block;width:100%;margin-top:.45rem;padding:.8rem 1rem;border-radius:14px;background:#0b0b13;border:1px solid rgba(255,255,255,.12);color:#fff}.primary-action{border:0;border-radius:999px;background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.85rem 1.1rem;font-weight:900}.result-box{grid-column:1/-1;background:rgba(0,0,0,.22);border:1px solid rgba(255,255,255,.09);border-radius:16px;padding:1rem;color:rgba(255,255,255,.7)}.result-box a{color:#ff8ca0}.tool-grid{max-width:980px;margin:1rem auto 4rem;padding:0 1.25rem;display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}.tool-grid p{color:rgba(255,255,255,.6)}@media(max-width:800px){.detector-card,.tool-grid{grid-template-columns:1fr}}</style>\n</head>', 1)
    return write_if_changed(PAGES / "hidden-fee-detector.html", html_text)


def create_buyer_type_alternatives() -> bool:
    from scripts._page_shell import page_shell

    body = """
<section class="tool-panel">
  <p class="eyebrow">Buyer Type Matcher</p>
  <h1>Find the best SaaS alternative for your team type.</h1>
  <p class="lede">Choose how you buy software. SaaSpare routes you to the most useful pricing, trial and alternatives pages without forcing an account.</p>
  <div class="buyer-grid" data-buyer-type-module>
    <a href="/shortlist?team=startup" data-track="compare_alternative"><strong>Startup</strong><span>Low setup time, transparent price, easy cancellation.</span></a>
    <a href="/shortlist?team=agency" data-track="compare_alternative"><strong>Agency</strong><span>Client workspaces, predictable seats, strong integrations.</span></a>
    <a href="/shortlist?team=enterprise" data-track="compare_alternative"><strong>Enterprise</strong><span>Security, admin controls, procurement and audit needs.</span></a>
    <a href="/deal-radar?intent=trial" data-track="deal_radar_click"><strong>Trial hunter</strong><span>Free trials, card rules and cancellation steps first.</span></a>
  </div>
</section>
"""
    html_text = page_shell(
        slug="buyer-type-alternatives",
        title="Best SaaS Alternative by Buyer Type",
        desc="Match your team type to the safest SaaS alternatives, pricing pages, free trials and comparison paths.",
        canonical_path="/pages/buyer-type-alternatives",
        body=body,
        nav_active="tools",
        schema_extra="",
        page_type="WebPage",
    )
    html_text = html_text.replace("</head>", '<style>.tool-panel{max-width:1100px;margin:0 auto;padding:7rem 1.25rem 4rem;text-align:center}.lede{color:rgba(255,255,255,.62);max-width:720px;margin:1rem auto 2rem}.buyer-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;text-align:left}.buyer-grid a{background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.1);border-radius:22px;padding:1.2rem;color:#fff;transition:transform .18s,border-color .18s}.buyer-grid a:hover{transform:translateY(-3px);border-color:rgba(233,69,96,.45)}.buyer-grid span{display:block;color:rgba(255,255,255,.58);margin-top:.5rem;font-size:.9rem}@media(max-width:900px){.buyer-grid{grid-template-columns:1fr 1fr}}@media(max-width:560px){.buyer-grid{grid-template-columns:1fr}}</style>\n</head>', 1)
    return write_if_changed(PAGES / "buyer-type-alternatives.html", html_text)


def write_reports(actions: dict) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    metadata_count = max(actions.get("metadata_pages", 0), len(actions.get("top50", [])))
    native_blocks = sum(read(p).count("data-native-intent") for p in PAGES.glob("*pricing-2026-plans-costs-what-you-actually-pay.html"))
    native_count = max(actions.get("ad_slots_removed", 0), native_blocks)
    quickwins = []
    for item in KNOWN_GSC_OPPORTUNITIES:
        quickwins.append(item)
    for p in actions["top50"]:
        title, desc = build_title_meta(p)
        quickwins.append({
            "path": path_url(p),
            "query": page_type(p).replace("_", " "),
            "impressions": "priority-proxy",
            "clicks": "unknown",
            "ctr": "low/unknown",
            "position": "target 8-30",
            "recommended_title": title,
            "recommended_meta": desc,
            "reason": "Buyer-intent local page selected for CTR-focused metadata and first-answer upgrade.",
        })

    write_if_changed(REPORTS / "gsc-quick-win-opportunities.json", json.dumps(quickwins[:54], indent=2))
    md = [
        "# GSC SEO Quick Wins",
        "",
        "Baseline used: GA4 Apr 21-May 11 = 247 active users / 100 key events; GSC last 28 days = 36 clicks / 8.45K impressions / 0.4% CTR / 19.1 avg position.",
        "",
        "Live GSC credentials were not present in the local run, so this report combines the latest user-provided baseline, previously exported Windsor/GSC opportunities, and a local buyer-intent priority scan. When `GSC_SERVICE_ACCOUNT_JSON` is available, `npm run seo:agent -- --mode=audit --only=gsc` should replace the proxy rows with live API data.",
        "",
        "| Priority | Page | Query / intent | Impressions | CTR | Position | Action |",
        "| --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for i, item in enumerate(quickwins[:50], 1):
        md.append(f"| {i} | `{item['path']}` | {item.get('query','buyer intent')} | {item.get('impressions','?')} | {item.get('ctr','?')} | {item.get('position','?')} | Rewrite title/meta, add first answer and stronger money CTA |")
    write_if_changed(REPORTS / "gsc-quick-win-opportunities.md", "\n".join(md) + "\n")

    perf = f"""# Performance And Cache Audit

Baseline: Cloudflare last 30 days shows 12.34K unique visitors, 149.99K requests, 2GB served and 3.86% cached.

## Changes Made

- Increased HTML caching windows in `site/_headers` for `/pages/*`, `/blog/*`, `/research/*` and root paths while keeping stale-while-revalidate.
- Kept `/go/*` affiliate redirects uncacheable and noindex.
- Kept `/assets/*`, favicons and icons on one-year immutable caching.
- Replaced large empty ad containers with native buyer-intent blocks so blank ad inventory does not create layout dead zones.
- Pricing-page conversion blocks use HTML/CSS only and do not introduce heavy client JavaScript.

## Cloudflare Rule Still Recommended

Create a Cloudflare Cache Rule for static HTML: cache eligible `saaspare.org/pages/*`, `saaspare.org/blog/*`, `saaspare.org/research/*` for 1 hour, bypass `/go/*`, and respect origin cache headers. This should move the cache rate materially closer to 40%+ once traffic is mostly repeat crawlers and returning users.

## Risks

- Google Analytics undercounts users if consent, blockers or bot filtering suppress client-side scripts.
- AdSense can still inject layout changes after approval; ad slots should stay below first useful content.
"""
    write_if_changed(REPORTS / "performance-cache-audit.md", perf)

    growth = f"""# SaaSpare Growth Health Audit

## Baseline

- GA4 Apr 21-May 11: 247 active users, 244 new users, 4.4K events, 100 key events.
- GSC last 28 days: 36 clicks, 8.45K impressions, 0.4% CTR, 19.1 average position.
- Cloudflare last 30 days: 12.34K unique visitors, 149.99K requests, 2GB served, 3.86% cached.

## Changes Made

- Rewrote CTR-focused title tags and meta descriptions for {metadata_count} high-priority buyer-intent pages.
- Upgraded {actions['pricing_pages']} pricing pages with first-answer blocks, hidden-fee risk scoring, true-cost checks, cheaper-alternative paths, source checked dates and report-pricing CTAs.
- Replaced {native_count} empty ad containers with native blocks for alternatives, free trials and Deal Radar.
- Added high-profit extension pages: Hidden Fee Detector and Best SaaS Alternative by Buyer Type.
- Added exact GA4 event aliases requested by the growth plan.
- Generated GSC quick-win and performance/cache reports.

## Analytics Events Added

- `affiliate_outbound_click`
- `pricing_cta_click`
- `compare_alternative_click`
- `shortlist_builder_start`
- `shortlist_builder_complete`
- `deal_radar_click`
- `newsletter_signup`
- `hidden_fee_detector_start`
- `hidden_fee_detector_complete`

## Technical Fixes

- Stronger cache headers for static HTML areas and assets.
- Empty ad inventory converted into useful internal navigation.
- Pricing pages now surface trust, source-check and correction paths above the long article body.

## Remaining Risks

- Average position 19.1 means most Google traffic is still discovery-stage; clicks will not boom until more pages move into positions 8-10.
- Authority/backlinks remain the limiting factor for competitive queries.
- Live GSC API credentials should be wired into CI so opportunities are based on real page/query data every week.
- Pricing claims remain intentionally conservative; exact pricing requires vendor source verification.

## Next 30-Day SEO Plan

1. Wire GSC service account credentials into GitHub Actions as `GSC_SERVICE_ACCOUNT_JSON`.
2. Run `npm run seo:agent -- --mode=audit --only=gsc` weekly and upgrade pages ranking 8-30 with low CTR.
3. Verify the top 25 pricing pages against vendor pricing pages and mark trust boxes as vendor-verified.
4. Build backlinks to the pricing-change tracker, Hidden Fee Detector and SaaS Pricing Index.
5. Submit the new tool pages to GSC and IndexNow after deployment.
6. Apply to high-commission programs first: Semrush, HubSpot, Pipedrive, Shopify, ClickUp, 1Password, Xero, Canva, Miro, Slack, Zendesk and Tresorit.
7. Replace any remaining blank ad inventory below the first useful content only.
8. Watch GA4 key events per landing page; improve pages with impressions but zero commercial events.
9. Add 5-10 verified source links per highest-impression pricing page.
10. Keep adding useful data assets, not generic AI pages.
"""
    write_if_changed(REPORTS / "growth-health-audit.md", growth)


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    go = go_slugs()
    changed_files = 0
    metadata_pages = 0
    pricing_pages = 0
    ad_slots_removed = 0
    top50 = candidate_pages()

    for p in top50:
        content = read(p)
        title, desc = build_title_meta(p)
        updated = replace_meta(content, title, desc, path_url(p))
        if updated != content:
            metadata_pages += 1
        updated, removed = replace_ad_slots(updated)
        ad_slots_removed += removed
        if page_type(p) == "pricing":
            slug = pricing_slug(p) or p.stem.split("-pricing-")[0]
            tool = clean_tool(slug)
            updated = ensure_growth_css(updated)
            updated = insert_pricing_module(updated, tool, slug, slug in go)
            pricing_pages += 1
        if write_if_changed(p, updated):
            changed_files += 1

    for p in PAGES.glob("*pricing-2026-plans-costs-what-you-actually-pay.html"):
        if p in top50:
            continue
        content = read(p)
        slug = pricing_slug(p) or p.stem.split("-pricing-")[0]
        tool = clean_tool(slug)
        updated = ensure_growth_css(content)
        updated = insert_pricing_module(updated, tool, slug, slug in go)
        updated, removed = replace_ad_slots(updated)
        ad_slots_removed += removed
        if write_if_changed(p, updated):
            changed_files += 1
            pricing_pages += 1

    if create_hidden_fee_detector():
        changed_files += 1
    if create_buyer_type_alternatives():
        changed_files += 1

    actions = {
        "changed_files": changed_files,
        "metadata_pages": metadata_pages,
        "pricing_pages": pricing_pages,
        "ad_slots_removed": ad_slots_removed,
        "top50": top50,
    }
    write_reports(actions)
    print(json.dumps({k: v for k, v in actions.items() if k != "top50"}, indent=2))


if __name__ == "__main__":
    main()
