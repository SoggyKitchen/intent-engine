"""v3.2 page rebuilds — pixel-cloned to user-supplied mockup images.

Image -> Page mapping:
  Image 6  -> v3-preview-roi-calculator (Calculate the real ROI / Strong Buy / cash-flow chart)
  Image 7  -> v3-preview-deal-radar     (LIVE 128 active offers / Price Drop Alerts rail)
  Image 8  -> v3-preview-shortlist      (full requirements form + ranked list with Fit Scores)
  Image 9  -> v3-preview-comparison     (1Password Pricing 2026 article)
  Image 2 row 1 -> v3-preview-about     (4 stat cards + How we help + icon cluster)
  Image 1 row 1 -> v3-preview-contact   (4 contact cards + form + What to expect rail)
  Image 1 row 2 -> v3-preview-newsletter (Why subscribe + testimonials + magazine sidebar)
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from v3_partials import nav_html, head_html, FOOTER  # noqa: E402

OUT_DIR = ROOT / "site" / "pages"
BASE = "https://saaspare.org"


def fab(label: str = "Decision Trail", count: int = 5) -> str:
    return f'<a class="v3-fab" href="#decision-trail">{label} <b>{count}</b></a>'


# ───────────── 1. ROI CALCULATOR (Image 6) ─────────────
def page_roi_calculator():
    head = head_html(
        "Calculate the real ROI of any SaaS tool",
        "Model total costs, quantify savings and see the true return before you commit to any vendor.",
        f"{BASE}/pages/v3-preview-roi-calculator",
    )
    feature_cards = "".join([
        _roi_feat("M9 11h6l-3-7-3 7zM9 11l-2 7h10l-2-7", "All-in cost modeling",
                  "Include subscription, fees, implementation & switching."),
        _roi_feat("M12 6v6l4 2 M12 22a10 10 0 1 1 0-20 10 10 0 0 1 0 20z", "Time & efficiency value",
                  "Convert hours saved into real dollar impact."),
        _roi_feat("M3 12h4l3 8 4-16 3 8h4", "Instant ROI view",
                  "See payback period and annual savings instantly."),
        _roi_feat("M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10zm-2-12 2 2 4-4", "Benchmark & trust",
                  "Compare against market data and real buyer benchmarks."),
    ])

    return f"""{head}
{nav_html(active='roi')}

<section class="v3-hero">
  <div class="v3-hero-inner">
    <div class="v3-section-eyebrow"><span class="v3-eyebrow">ROI Calculator</span></div>
    <h1 style="margin:1rem 0 1rem">Calculate the real <em>ROI.</em><br>Justify every <em>SaaS decision.</em></h1>
    <p class="v3-sub">Model total costs, quantify savings and see the true return before you commit to any vendor.</p>
  </div>
</section>

<div class="v3-container">
  <div class="v3-grid-4" style="gap:.85rem;margin-bottom:1.6rem">{feature_cards}</div>

  <div class="v3-grid-2" style="gap:1.5rem;align-items:flex-start;grid-template-columns:1fr 1.1fr">
    {_roi_inputs()}
    {_roi_results()}
  </div>

  <details class="v3-accordion" style="margin-top:1.4rem">
    <summary><span><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="var(--v3-red-light)" stroke-width="2" style="vertical-align:-3px;margin-right:6px"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>Assumptions &amp; details</span><small style="color:var(--v3-text-4);font-weight:500">See key assumptions, formulas and how results are calculated.</small></summary>
    <div class="v3-accordion-body">
      <p>ROI is calculated as <code>(annual benefit − annual cost) ÷ annual cost</code>. Benefit includes time-savings (hours × loaded cost) plus non-time efficiency gains. Costs include subscription, fees, implementation and switching, amortised over year 1.</p>
      <p>Conservative scenario assumes 70% of benefits land in year 1; aggressive assumes 100%; balanced assumes 85%. Switch with the dropdown above the results panel.</p>
    </div>
  </details>

  <div class="v3-card v3-card-padded" style="margin-top:1.6rem">
    <p class="v3-muted" style="text-align:center;font-size:.78rem;text-transform:uppercase;letter-spacing:.5px;font-weight:700;margin:0 0 1.1rem">Trusted by buyers who do their homework</p>
    <div class="v3-grid-4" style="gap:1rem">
      {_roi_trust("M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z", "Independent &amp; unbiased", "We don&rsquo;t sell software.")}
      {_roi_trust("M3 12h4l3 8 4-16 3 8h4", "Real buyer benchmarks", "Based on 1,000+ pricing pages and buyer insights.")}
      {_roi_trust("M12 8a4 4 0 0 1 4 4M22 12a10 10 0 1 1-10-10 M16 8 22 2 m-2 0h2v2", "Updated monthly", "Our data is refreshed to stay current.")}
      {_roi_trust("M12 11a3 3 0 0 0-3 3v4h6v-4a3 3 0 0 0-3-3z M5 9V7a7 7 0 0 1 14 0v2", "Privacy first", "Your inputs are private and never shared.")}
    </div>
  </div>

  <div class="v3-card v3-card-emph v3-card-padded" style="margin:1.6rem 0 4rem;text-align:center">
    <h3 style="margin:0 0 .35rem;font-size:1.25rem">Make confident decisions, faster.</h3>
    <p class="v3-muted" style="font-size:.92rem;margin:0 0 1.1rem">Compare alternatives side by side or build a ranked shortlist for your team.</p>
    <div class="v3-row center" style="gap:.6rem;flex-wrap:wrap;justify-content:center">
      <a href="/pages/" class="v3-btn v3-btn-primary">Compare alternatives &#8594;</a>
      <a href="/shortlist" class="v3-btn v3-btn-secondary">Build shortlist &#8594;</a>
    </div>
  </div>
</div>

{FOOTER}
{fab()}
</body></html>
"""


def _roi_feat(svg_d, title, desc):
    return f"""<div class="v3-card" style="padding:1.1rem 1.25rem">
      <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="{svg_d}"/></svg></div>
      <h4 style="margin:.6rem 0 .2rem;font-size:.9rem">{title}</h4>
      <p style="font-size:.76rem;color:var(--v3-text-4);margin:0;line-height:1.5">{desc}</p>
    </div>"""


def _roi_trust(svg_d, title, desc):
    return f"""<div class="v3-row tight" style="align-items:flex-start;gap:.6rem">
      <div class="v3-card-icon" style="flex-shrink:0;margin-top:2px"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="{svg_d}"/></svg></div>
      <div><b style="color:#fff;font-size:.82rem;display:block">{title}</b><small style="color:var(--v3-text-4);font-size:.72rem;line-height:1.45;display:block">{desc}</small></div>
    </div>"""


def _roi_inputs():
    return """<div class="v3-card v3-card-padded">
    <h2 style="font-size:1.05rem;margin:0 0 .35rem">Your inputs</h2>
    <p class="v3-muted" style="font-size:.78rem;margin:0 0 1.1rem">Enter your numbers to see your potential return.</p>

    <div style="font-size:.68rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.5px;font-weight:700;margin:.85rem 0 .55rem">Costs</div>
    <div class="v3-form-row"><label>Annual subscription cost <span style="opacity:.6">&#9432;</span></label><div class="v3-input-grp"><input class="v3-input" value="$ 24,000"><select class="v3-select"><option>per year</option><option>per month</option></select></div></div>
    <div class="v3-form-row"><label>Number of users <span style="opacity:.6">&#9432;</span></label><div class="v3-input-grp"><input class="v3-input" value="25"><select class="v3-select"><option>users</option><option>seats</option></select></div></div>
    <div class="v3-form-row"><label>One-time implementation cost <span style="opacity:.6">&#9432;</span></label><input class="v3-input" value="$ 8,000"></div>
    <div class="v3-form-row"><label>Switching &amp; migration cost <span style="opacity:.6">&#9432;</span></label><input class="v3-input" value="$ 3,000"></div>

    <div style="font-size:.68rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.5px;font-weight:700;margin:1.2rem 0 .55rem">Benefits</div>
    <div class="v3-form-row"><label>Average fully loaded cost per user <span style="opacity:.6">&#9432;</span></label><div class="v3-input-grp"><input class="v3-input" value="$ 85"><select class="v3-select"><option>per hour</option><option>per year</option></select></div></div>
    <div class="v3-form-row"><label>Hours saved per user per week <span style="opacity:.6">&#9432;</span></label><div class="v3-input-grp"><input class="v3-input" value="2.5"><select class="v3-select"><option>hours</option></select></div></div>
    <div class="v3-form-row"><label>Efficiency improvement (non-time savings) <span style="opacity:.6">&#9432;</span></label><div class="v3-input-grp"><input class="v3-input" value="10"><select class="v3-select"><option>%</option></select></div></div>

    <div class="v3-callout v3-callout-pro" style="margin:1.2rem 0">
      <div class="v3-callout-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></div>
      <div class="v3-callout-body"><h4>Pro tip</h4><p style="font-size:.82rem">Include both time savings and non-time efficiency gains for a more accurate ROI.</p></div>
    </div>

    <div class="v3-row tight" style="margin-top:1rem;gap:.6rem">
      <button class="v3-btn v3-btn-primary" style="flex:1">Calculate ROI</button>
      <button class="v3-btn v3-btn-secondary" style="flex:0 0 auto">Reset</button>
    </div>
  </div>"""


def _roi_results():
    return """<div class="v3-card v3-card-padded">
    <div class="v3-row between" style="margin-bottom:1rem">
      <h2 style="font-size:1.05rem;margin:0">Your ROI results</h2>
      <select class="v3-select" style="width:auto;font-weight:700;color:#fff;font-size:.82rem"><option>Conservative</option><option>Balanced</option><option>Aggressive</option></select>
    </div>

    <div style="font-size:.68rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.5px;font-weight:700;margin:0 0 .55rem">Key outcomes</div>
    <div class="v3-grid-2" style="gap:.7rem">
      <div class="v3-stat-tile">
        <h5>Monthly ROI</h5>
        <div class="v3-stat-num green">312%</div>
        <p class="v3-stat-help">$6,240 net benefit / month</p>
        <span class="v3-stat-rating good">Excellent</span>
      </div>
      <div class="v3-stat-tile">
        <h5>Annual net savings</h5>
        <div class="v3-stat-num green">$74,880</div>
        <p class="v3-stat-help">Total after all costs</p>
        <span class="v3-stat-rating good">Excellent</span>
      </div>
      <div class="v3-stat-tile">
        <h5>Payback period</h5>
        <div class="v3-stat-num purple">1.7 months</div>
        <p class="v3-stat-help">Time to break even</p>
        <span class="v3-stat-rating good">Excellent</span>
      </div>
      <div class="v3-stat-tile">
        <h5>3-year ROI</h5>
        <div class="v3-stat-num blue">412%</div>
        <p class="v3-stat-help">Total return over 3 years</p>
        <span class="v3-stat-rating good">Excellent</span>
      </div>
    </div>

    <div class="v3-verdict" style="margin-top:1rem">
      <div class="v3-verdict-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 20l3-12 5 4 4-7 5 5 3-3 1 13z M2 20h20"/></svg></div>
      <div class="v3-verdict-body">
        <h4>Our verdict</h4>
        <div class="v3-verdict-name">Strong Buy</div>
        <p>This investment delivers exceptional value and pays for itself in under 2 months.</p>
      </div>
    </div>

    <div class="v3-chart">
      <div class="v3-chart-head">
        <span>Cash flow overview</span>
        <span class="v3-chart-legend">
          <span style="--c:#f97070">Total Costs</span>
          <span style="--c:#34d399">Total Benefits</span>
          <span style="--c:#c084fc">Net Benefit</span>
        </span>
      </div>
      <svg viewBox="0 0 480 200" style="width:100%;height:auto" aria-hidden="true">
        <defs>
          <linearGradient id="rcLine" x1="0" x2="1"><stop offset="0" stop-color="#c084fc"/><stop offset="1" stop-color="#a855f7"/></linearGradient>
        </defs>
        <line x1="40" y1="20"  x2="460" y2="20"  stroke="rgba(255,255,255,.05)"/>
        <line x1="40" y1="60"  x2="460" y2="60"  stroke="rgba(255,255,255,.05)"/>
        <line x1="40" y1="100" x2="460" y2="100" stroke="rgba(255,255,255,.18)"/>
        <line x1="40" y1="140" x2="460" y2="140" stroke="rgba(255,255,255,.05)"/>
        <line x1="40" y1="180" x2="460" y2="180" stroke="rgba(255,255,255,.05)"/>
        <text x="6"  y="24"  fill="rgba(255,255,255,.32)" font-size="9">$100k</text>
        <text x="6"  y="64"  fill="rgba(255,255,255,.32)" font-size="9">$50k</text>
        <text x="20" y="104" fill="rgba(255,255,255,.32)" font-size="9">$0</text>
        <text x="0"  y="144" fill="rgba(255,255,255,.32)" font-size="9">-$50k</text>
        <g>
          <rect x="60"  y="115" width="14" height="20"  fill="#f97070" rx="2"/><rect x="76"  y="92"  width="14" height="8"   fill="#34d399" rx="2"/>
          <rect x="140" y="100" width="14" height="35"  fill="#f97070" rx="2"/><rect x="156" y="68"  width="14" height="32"  fill="#34d399" rx="2"/>
          <rect x="220" y="85"  width="14" height="50"  fill="#f97070" rx="2"/><rect x="236" y="40"  width="14" height="60"  fill="#34d399" rx="2"/>
          <rect x="300" y="70"  width="14" height="65"  fill="#f97070" rx="2"/><rect x="316" y="22"  width="14" height="78"  fill="#34d399" rx="2"/>
          <rect x="380" y="55"  width="14" height="80"  fill="#f97070" rx="2"/><rect x="396" y="6"   width="14" height="94"  fill="#34d399" rx="2"/>
        </g>
        <polyline points="73,128 153,108 233,82 313,55 393,28" stroke="url(#rcLine)" stroke-width="2.5" fill="none"/>
        <circle cx="73"  cy="128" r="4" fill="#c084fc"/>
        <circle cx="153" cy="108" r="4" fill="#c084fc"/>
        <circle cx="233" cy="82"  r="4" fill="#c084fc"/>
        <circle cx="313" cy="55"  r="4" fill="#c084fc"/>
        <circle cx="393" cy="28"  r="4" fill="#c084fc"/>
        <text x="60"  y="195" fill="rgba(255,255,255,.42)" font-size="9">Month 1</text>
        <text x="140" y="195" fill="rgba(255,255,255,.42)" font-size="9">Month 6</text>
        <text x="218" y="195" fill="rgba(255,255,255,.42)" font-size="9">Month 12</text>
        <text x="300" y="195" fill="rgba(255,255,255,.42)" font-size="9">Year 2</text>
        <text x="380" y="195" fill="rgba(255,255,255,.42)" font-size="9">Year 3</text>
      </svg>
    </div>
  </div>"""


# ───────────── 2. DEAL RADAR (Image 7) ─────────────
def page_deal_radar():
    head = head_html(
        "Deal Radar — real SaaS offers, verified in real-time",
        "We track price drops, promo codes, hidden fees and stackable offers — so you never overpay.",
        f"{BASE}/pages/v3-preview-deal-radar",
    )
    return f"""{head}
{nav_html(active='deals')}

<section class="v3-hero left" style="padding-bottom:1.5rem">
  <div class="v3-hero-inner" style="display:grid;grid-template-columns:1.4fr 1fr;gap:2rem;align-items:flex-start">
    <div>
      <span class="v3-eyebrow">Live market intelligence</span>
      <h1 style="margin:1rem 0 .85rem">Deal Radar: Real SaaS<br>offers, <em>verified</em> in real-time.</h1>
      <p class="v3-sub" style="margin:0;text-align:left">We track price drops, promo codes, hidden fees and stackable offers &mdash; so you never overpay for the tools your team depends on.</p>
    </div>
    <div class="v3-card v3-card-padded" style="background:rgba(255,255,255,.045)">
      <span class="v3-live-indicator">Live</span>
      <div style="font-family:var(--v3-ff-display);font-size:3rem;font-weight:850;color:var(--v3-red-light);letter-spacing:-.04em;line-height:1.05;margin:.55rem 0 .15rem">128</div>
      <p style="font-size:.85rem;color:#fff;margin:0;font-weight:700">Active offers right now</p>
      <small style="color:var(--v3-text-5);font-size:.72rem">Updated 3m ago</small>
    </div>
  </div>
</section>

<div class="v3-container">
  <div class="v3-card v3-card-padded" style="padding:1.1rem 1.25rem;margin-bottom:1.2rem">
    <div style="display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:.7rem">
      {_dr_select("Category","All Categories")}
      {_dr_select("Vendor","All Vendors")}
      {_dr_select("Free trial","Any")}
      {_dr_select("Promo / Code","Any")}
      {_dr_select("Annual Discount","Any")}
      {_dr_select("Hidden-fee alert","Any")}
      {_dr_select("Urgency","Any")}
    </div>
    <div class="v3-row tight" style="margin-top:1rem;gap:.4rem;flex-wrap:wrap">
      <a class="v3-filter-pill active" href="#">All Offers <span class="v3-pill-count">128</span></a>
      <a class="v3-filter-pill" href="#"><span style="color:var(--v3-red-light)">&#11015;</span> Price Drops <span class="v3-pill-count">32</span></a>
      <a class="v3-filter-pill" href="#"><span style="color:var(--v3-info)">&#11088;</span> New Offers <span class="v3-deal-badge new-tag">NEW</span></a>
      <a class="v3-filter-pill" href="#"><span style="color:var(--v3-warn)">&#9203;</span> Ending Soon <span class="v3-pill-count warn">14</span></a>
      <a class="v3-filter-pill" href="#"><span style="color:#c084fc">&#10024;</span> Exclusive <span class="v3-pill-count">9</span></a>
      <a class="v3-filter-pill" href="#"><span style="color:var(--v3-good)">&#43;</span> Stackable <span class="v3-pill-count">11</span></a>
    </div>
  </div>
</div>

<div class="v3-layout-rail">
  <main>
    <div class="v3-card v3-card-flat" style="padding:.85rem 1.1rem;margin-bottom:.85rem">
      <div class="v3-row between"><b style="color:#fff;font-size:.85rem">128 offers found</b><span style="color:var(--v3-text-4);font-size:.78rem">Sort by <select class="v3-select" style="display:inline-block;width:auto;color:#fff;font-weight:700;font-size:.78rem;padding:.3rem .6rem"><option>Best value</option><option>Newest</option><option>Biggest discount</option></select></span></div>
    </div>
    <div style="display:flex;flex-direction:column;gap:.75rem">
      {_dr_offer("1Password","#0070ad","1P","Secure password management for teams and businesses.","Security","SSO","Team Management","-$4.00","20% off","Pro Plan","$7.99","$3.99","/user/month","May 20, 2026",["best-value","price-drop"])}
      {_dr_offer("HubSpot CRM","#ff7a59","HS","Free CRM for teams who want to grow better.","CRM","Sales","Marketing","FREE PLAN","Free forever","No credit card required","","","","May 19, 2026",["exclusive","free-plan"])}
      {_dr_offer("Notion","#ffffff","N","Docs, wikis, and projects &mdash; all in one workspace.","Productivity","Collaboration","Knowledge","20% off","","Plus Plan (Annual)","$12.00","$9.60","/user/month","May 18, 2026",[])}
      {_dr_offer("Pipedrive","#1a1a1a","P","Sales CRM built to help you sell more.","Sales","CRM","Pipeline","25% off","","Advanced Plan (Annual)","$24.90","$18.68","/user/month","May 20, 2026",[])}
      {_dr_offer("Bitwarden","#175ddc","BW","Open-source password manager for teams.","Security","SSO","Open Source","15% off","","Teams Plan (Annual)","$5.00","$4.25","/user/month","May 17, 2026",[])}
      {_dr_offer("Trello","#0079bf","T","Visual project management that works.","Project Mgmt","Kanban","Collaboration","-$1.20","20% off","Standard Plan (Annual)","$5.00","$4.00","/user/month","May 19, 2026",["price-drop"])}
    </div>
    <div class="v3-row center" style="margin:1.6rem 0 4rem"><a href="#" class="v3-btn v3-btn-secondary">Load more offers &#8594;</a></div>
  </main>

  <aside>
    <div class="v3-sticky-rail">
      <div class="v3-rail-card">
        <div class="v3-row between" style="margin-bottom:.5rem"><h3 style="margin:0;display:flex;align-items:center;gap:.4rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="var(--v3-red)" stroke-width="2.5"><path d="M12 5v14M19 12l-7 7-7-7"/></svg>Price Drop Alerts</h3><a href="#" style="font-size:.72rem;color:var(--v3-red-light);font-weight:700">View all</a></div>
        <div class="v3-rail-list">
          <a href="#"><div class="v3-tool-logo" style="background:#4a154b;color:#fff;width:30px;height:30px;border-radius:8px;font-size:.74rem">SL</div><span><b>Slack</b><small>Pro Plan</small></span><b style="margin-left:auto;color:var(--v3-red-light);font-size:.78rem">-$2.00<small style="display:block;color:var(--v3-text-5);font-weight:500;text-align:right">2h ago</small></b></a>
          <a href="#"><div class="v3-tool-logo" style="background:#0b6bcb;color:#fff;width:30px;height:30px;border-radius:8px;font-size:.74rem">CA</div><span><b>Calendly</b><small>Teams Plan</small></span><b style="margin-left:auto;color:var(--v3-red-light);font-size:.78rem">-$1.50<small style="display:block;color:var(--v3-text-5);font-weight:500;text-align:right">5h ago</small></b></a>
          <a href="#"><div class="v3-tool-logo" style="background:#7b68ee;color:#fff;width:30px;height:30px;border-radius:8px;font-size:.74rem">CU</div><span><b>ClickUp</b><small>Business Plan</small></span><b style="margin-left:auto;color:var(--v3-red-light);font-size:.78rem">-$3.00<small style="display:block;color:var(--v3-text-5);font-weight:500;text-align:right">1d ago</small></b></a>
        </div>
      </div>

      <div class="v3-rail-card" style="margin-top:.85rem">
        <div class="v3-row between" style="margin-bottom:.5rem"><h3 style="margin:0;display:flex;align-items:center;gap:.4rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="var(--v3-good)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Recently Verified</h3><a href="#" style="font-size:.72rem;color:var(--v3-red-light);font-weight:700">View all</a></div>
        <div class="v3-rail-list">
          <a href="#"><div class="v3-tool-logo" style="background:#36c5f0;color:#fff;width:30px;height:30px;border-radius:8px;font-size:.74rem">AB</div><span><b>Airtable</b><small>Verified May 20, 2026</small></span></a>
          <a href="#"><div class="v3-tool-logo" style="background:#5b3fff;color:#fff;width:30px;height:30px;border-radius:8px;font-size:.74rem">L</div><span><b>Linear</b><small>Verified May 20, 2026</small></span></a>
          <a href="#"><div class="v3-tool-logo" style="background:#000;color:#fff;width:30px;height:30px;border-radius:8px;font-size:.74rem">F</div><span><b>Figma</b><small>Verified May 19, 2026</small></span></a>
        </div>
      </div>

      <div class="v3-rail-card" style="margin-top:.85rem">
        <div class="v3-row between" style="margin-bottom:.5rem"><h3 style="margin:0;display:flex;align-items:center;gap:.4rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="var(--v3-warn)" stroke-width="2.5"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12" y2="17"/></svg>Buyer Warnings</h3><a href="#" style="font-size:.72rem;color:var(--v3-red-light);font-weight:700">View all</a></div>
        <div class="v3-rail-list">
          <a href="#"><span style="color:var(--v3-warn)">&#9888;</span><span><b>Hidden fees detected</b></span><b style="margin-left:auto;color:var(--v3-warn);font-size:.78rem">3 tools</b></a>
          <a href="#"><span style="color:var(--v3-warn)">&#9888;</span><span><b>Auto-renewal enabled</b></span><b style="margin-left:auto;color:var(--v3-warn);font-size:.78rem">5 tools</b></a>
          <a href="#"><span style="color:var(--v3-warn)">&#9888;</span><span><b>Price increased recently</b></span><b style="margin-left:auto;color:var(--v3-warn);font-size:.78rem">2 tools</b></a>
        </div>
      </div>

      <div class="v3-rail-card" style="margin-top:.85rem">
        <h3 style="margin:0 0 .35rem;display:flex;align-items:center;gap:.4rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="var(--v3-red-light)" stroke-width="2.5"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>Never miss a deal</h3>
        <p style="font-size:.78rem;color:var(--v3-text-4);margin:.2rem 0 .85rem;line-height:1.5">Get price drop alerts and new offers delivered to your inbox.</p>
        <div class="v3-row tight" style="gap:.45rem"><input type="email" class="v3-input" placeholder="you@company.com" style="flex:1;font-size:.78rem;padding:.55rem .7rem"><button class="v3-btn v3-btn-primary v3-btn-sm">Subscribe</button></div>
        <small style="display:block;font-size:.66rem;color:var(--v3-text-5);margin-top:.4rem">No spam. Unsubscribe anytime.</small>
      </div>
    </div>
  </aside>
</div>

{FOOTER}
{fab()}
</body></html>
"""


def _dr_select(lbl, default):
    return f"""<label style="display:flex;flex-direction:column;gap:.2rem;font-size:.7rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.4px;font-weight:700">{lbl}<select class="v3-select" style="font-size:.82rem;padding:.5rem .65rem;color:#fff"><option>{default}</option></select></label>"""


def _dr_offer(name, bg, logo, desc, t1, t2, t3, discount, alt_disc, plan, was, now, period, verified, badges):
    """Render a deal radar offer row (Image 7)."""
    badge_lookup = {
        "best-value": '<span class="v3-deal-badge best-value">Best Value</span>',
        "price-drop": '<span class="v3-deal-badge price-drop">Price Drop</span>',
        "exclusive":  '<span class="v3-deal-badge exclusive">Exclusive</span>',
        "free-plan":  '<span class="v3-deal-badge free-plan">Free Plan</span>',
    }
    badge_html = " ".join(badge_lookup[b] for b in badges)
    side_left = '<span class="v3-deal-badge price-drop">Price Drop</span>' if "price-drop" in badges else ('<span class="v3-deal-badge exclusive">Exclusive</span>' if "exclusive" in badges else "")
    has_drop = "has-drop" if "price-drop" in badges else ""

    if was and now:
        price_block = f"""<div style="text-align:right">
          {f'<div class="v3-deal-discount">{discount}</div>' if discount else ''}
          {f'<div style="color:var(--v3-text-4);font-size:.72rem;margin-top:2px">{alt_disc}</div>' if alt_disc else ''}
          <div style="color:var(--v3-text-3);font-size:.72rem;margin-top:4px">{plan}</div>
          <div><span class="v3-deal-strike">{was}</span> <span class="v3-deal-now">{now}</span></div>
          <div style="color:var(--v3-text-5);font-size:.7rem">{period}</div>
        </div>"""
    else:
        price_block = f"""<div style="text-align:right">
          <div class="v3-deal-discount" style="color:var(--v3-good);font-size:.85rem">{discount}</div>
          <div style="color:#fff;font-size:.92rem;font-weight:850;font-family:var(--v3-ff-display);margin-top:4px">{plan}</div>
          <div style="color:var(--v3-text-5);font-size:.7rem;margin-top:2px">{period}</div>
        </div>"""

    tags_html = "".join(f'<span class="v3-tag">{t}</span>' for t in [t1, t2, t3] if t)

    return f"""<div class="v3-deal-row {has_drop}">
      <div style="position:relative">
        {f'<div style="position:absolute;top:-10px;left:-12px">{side_left}</div>' if side_left else ''}
        <div class="v3-tool-logo" style="background:{bg};color:{'#000' if bg == '#ffffff' else '#fff'}">{logo}</div>
      </div>
      <div>
        <div class="v3-row tight" style="gap:.5rem;align-items:center;flex-wrap:wrap"><h3 style="margin:0;font-size:1rem;color:#fff">{name}</h3>{badge_html}</div>
        <p style="font-size:.78rem;color:var(--v3-text-4);margin:.2rem 0 .35rem;line-height:1.45">{desc}</p>
        <div class="v3-tool-tags">{tags_html}</div>
        <small style="display:block;color:var(--v3-text-5);font-size:.7rem;margin-top:.4rem">&#10003; Verified {verified}  &middot;  Official Pricing</small>
      </div>
      {price_block}
      <div><a href="#" class="v3-btn v3-btn-primary v3-btn-sm">View Offer &#8594;</a></div>
    </div>"""


# (page generators 3, 4, 5, 6, 7 follow in part 2 of this script — see build_v3_pages_v32_part2.py)
if __name__ == "__main__":
    pages = {
        "v3-preview-roi-calculator.html": page_roi_calculator(),
        "v3-preview-deal-radar.html":     page_deal_radar(),
    }
    for name, html in pages.items():
        target = OUT_DIR / name
        target.write_text(html, encoding="utf-8")
        print(f"  wrote {target.relative_to(ROOT)}  ({len(html):,} bytes)")
