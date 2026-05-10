"""v3.2 page rebuilds — part 2 (Shortlist + Comparison + About + Contact + Newsletter)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from v3_partials import nav_html, head_html, FOOTER  # noqa: E402

OUT_DIR = ROOT / "site" / "pages"
BASE = "https://saaspare.org"


def fab(label: str = "Decision Trail", count: int = 5) -> str:
    return f'<a class="v3-fab" href="#decision-trail">{label} <b>{count}</b></a>'


# ───────────── SHORTLIST BUILDER (Image 8) ─────────────
def page_shortlist():
    head = head_html(
        "Build your perfect SaaS shortlist",
        "Tell us what you need and we'll rank the best tools for your team based on fit, pricing, and real-world performance.",
        f"{BASE}/pages/v3-preview-shortlist",
    )
    return f"""{head}
{nav_html(active='shortlist')}

<div class="v3-container" style="padding-top:5.5rem"><div class="v3-crumbs"><a href="/">Home</a><span>/</span><span>Shortlist Builder</span></div></div>

<section class="v3-hero" style="padding-top:1rem">
  <div class="v3-hero-inner">
    <div class="v3-section-eyebrow"><span class="v3-eyebrow">Smart shortlist builder</span></div>
    <h1 style="margin:1rem 0 1rem">Build your <em>perfect</em> shortlist.</h1>
    <p class="v3-sub">Tell us what you need and we&rsquo;ll rank the best tools for your team based on fit, pricing, and real-world performance.</p>
    <div class="v3-row center" style="gap:2.5rem;margin-top:1.4rem;flex-wrap:wrap">
      <div class="v3-row tight" style="gap:.5rem"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="var(--v3-red-light)" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg><span style="font-size:.82rem;color:var(--v3-text-2)"><b style="color:#fff">Unbiased rankings</b><br><small style="color:var(--v3-text-5)">We don&rsquo;t play favorites</small></span></div>
      <div class="v3-row tight" style="gap:.5rem"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="var(--v3-red-light)" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg><span style="font-size:.82rem;color:var(--v3-text-2)"><b style="color:#fff">Real pricing, real outcomes</b><br><small style="color:var(--v3-text-5)">Data from verified buyer pages</small></span></div>
    </div>
  </div>
</section>

<div class="v3-layout-rail" style="grid-template-columns:340px minmax(0,1fr);gap:1.5rem">
  <aside>
    {_sl_requirements()}
    <div class="v3-card v3-card-padded" style="margin-top:1rem">
      <h4 style="margin:0 0 .55rem;font-size:.85rem;display:flex;align-items:center;gap:.4rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="var(--v3-red-light)" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>How we score &amp; rank</h4>
      <ul style="margin:0;padding-left:1.05rem;font-size:.78rem;color:var(--v3-text-3);line-height:1.55">
        <li>Fit Score combines your priorities, features, and team context.</li>
        <li>Pricing Score reflects total cost at your team size.</li>
        <li>Momentum Score includes reviews, search demand &amp; recency.</li>
        <li>Scores are updated daily from verified buyer pages.</li>
      </ul>
      <a href="#" class="v3-link-cta" style="font-size:.78rem;margin-top:.7rem;display:inline-flex">Learn more about our methodology &#8594;</a>
    </div>
  </aside>

  <main>
    <div class="v3-card v3-card-padded">
      <div class="v3-row between" style="margin-bottom:1rem;flex-wrap:wrap;gap:.6rem">
        <div class="v3-row tight" style="gap:.5rem"><span style="background:var(--v3-red-soft);color:var(--v3-red-light);width:24px;height:24px;border-radius:50%;display:grid;place-items:center;font-family:var(--v3-ff-display);font-size:.78rem;font-weight:850;border:1px solid rgba(233,69,96,.32)">2</span><h3 style="margin:0;font-size:1.05rem">Your ranked shortlist</h3></div>
        <span style="font-size:.74rem;color:var(--v3-text-4)"><b style="color:#fff">9 results</b> &middot; Updated just now</span>
      </div>

      <div class="v3-row tight" style="font-size:.66rem;color:var(--v3-text-5);text-transform:uppercase;letter-spacing:.5px;font-weight:700;padding:.4rem 0 .6rem;border-bottom:1px solid var(--v3-border)">
        <span style="flex:0 0 56px"></span>
        <span style="flex:1;padding-left:.85rem">Tool</span>
        <span style="flex:0 0 70px;text-align:center">Fit Score</span>
        <span style="flex:0 0 110px">Pricing (est.)</span>
        <span style="flex:0 0 130px">Best for</span>
        <span style="flex:0 0 130px;text-align:right">Action</span>
      </div>

      <div style="display:flex;flex-direction:column">
        {_sl_row(1, "HubSpot CRM", "Best Fit", "#ff7a59", "HS",
                 "Powerful, user-friendly CRM with marketing, sales, and service in one unified platform.",
                 ["Free plan", "Email tracking", "Pipelines"], 94, "excellent",
                 "$0–$90", "/user/mo", "Free plan available", "Growing teams that want an all-in-one CRM.")}
        {_sl_row(2, "Pipedrive", "", "#1a1a1a", "P",
                 "Sales-first CRM built to help teams close more deals, faster.",
                 ["14-day trial", "Visual pipeline", "Automation"], 89, "great",
                 "$14–$99", "/user/mo", "14-day free trial", "Small to mid-size teams focused on closing.")}
        {_sl_row(3, "Notion CRM", "New", "#ffffff", "N",
                 "Flexible, modern CRM for teams that love Notion&rsquo;s connected workspace.",
                 ["Free plan", "Custom views", "No code"], 82, "great",
                 "$0–$18", "/user/mo", "Free plan available", "Teams that want flexibility and ease of use.")}
        {_sl_row(4, "Salesforce Sales Cloud", "", "#00a1e0", "SF",
                 "Enterprise-grade CRM with unmatched customization and scalability.",
                 ["Free trial", "AI insights", "AppExchange"], 78, "good",
                 "$25–$500+", "/user/mo", "30-day free trial", "Enterprise teams with complex needs.")}
        {_sl_row(5, "folk CRM", "", "#ff8a3d", "f",
                 "Simple, beautiful CRM for relationship-driven teams.",
                 ["14-day trial", "Contact hub", "Integrations"], 74, "good",
                 "$20–$40", "/user/mo", "14-day trial", "Small teams that value relationships &amp; simplicity.")}
      </div>

      <div class="v3-row center" style="margin-top:1rem"><a href="#" class="v3-link-cta">View 4 more results &#8594;</a></div>
    </div>

    <div class="v3-card v3-card-padded" style="margin-top:1rem">
      <div class="v3-row between" style="flex-wrap:wrap;gap:.7rem">
        <div class="v3-row tight" style="gap:.5rem"><span style="background:var(--v3-red-soft);color:var(--v3-red-light);width:24px;height:24px;border-radius:50%;display:grid;place-items:center;font-family:var(--v3-ff-display);font-size:.78rem;font-weight:850;border:1px solid rgba(233,69,96,.32)">3</span>
          <div><h4 style="margin:0;font-size:.95rem">Save &amp; share your shortlist</h4>
          <small style="color:var(--v3-text-4);font-size:.78rem">Create an account to save, share, and revisit your shortlist anytime.</small></div></div>
        <div class="v3-row tight" style="gap:.5rem">
          <a href="#" class="v3-btn v3-btn-secondary v3-btn-sm">&darr; Download PDF</a>
          <a href="#" class="v3-btn v3-btn-primary v3-btn-sm">&#9733; Save shortlist</a>
        </div>
      </div>
    </div>
  </main>
</div>

<div class="v3-container">
  <div class="v3-card v3-card-emph v3-card-padded" style="margin:0 0 4rem;display:grid;grid-template-columns:64px 1fr auto;gap:1rem;align-items:center">
    <div class="v3-card-icon" style="width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg, rgba(233,69,96,.32), rgba(233,69,96,.08));border-color:rgba(233,69,96,.4)"><svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 20l3-12 5 4 4-7 5 5 3-3 1 13z M2 20h20"/></svg></div>
    <div><h3 style="margin:0 0 .15rem;font-size:1.1rem">Ready to decide with confidence?</h3>
    <p style="margin:0;color:var(--v3-text-3);font-size:.85rem">Compare your top picks side-by-side on pricing, features, and real reviews.</p></div>
    <a href="#" class="v3-btn v3-btn-primary">Compare my shortlist &#8594;</a>
  </div>
  <p class="v3-help" style="text-align:center;margin:0 0 3rem">SaaSpare is an independent comparison site. We may earn a commission when you buy through links on our site &mdash; at no extra cost to you. We only recommend tools we believe provide real value.</p>
</div>

{FOOTER}
{fab()}
</body></html>
"""


def _sl_requirements():
    return """<div class="v3-card v3-card-padded">
    <div class="v3-row between" style="margin-bottom:1rem">
      <div class="v3-row tight" style="gap:.5rem"><span style="background:var(--v3-red-soft);color:var(--v3-red-light);width:24px;height:24px;border-radius:50%;display:grid;place-items:center;font-family:var(--v3-ff-display);font-size:.78rem;font-weight:850;border:1px solid rgba(233,69,96,.32)">1</span><h3 style="margin:0;font-size:1.05rem">Your requirements</h3></div>
      <a href="#" style="font-size:.74rem;color:var(--v3-red-light);font-weight:700">&#x21bb; Reset</a>
    </div>

    <label class="v3-label">Category</label>
    <select class="v3-select" style="margin-bottom:.85rem"><option>CRM &amp; Sales</option><option>Marketing</option><option>Project Management</option></select>

    <label class="v3-label">Team size</label>
    <div class="v3-pill-group" style="margin-bottom:.85rem">
      <label class="active">Solo</label><label>2&ndash;50</label><label>50&ndash;500</label><label>500+</label>
    </div>

    <label class="v3-label">Monthly budget (per user)</label>
    <select class="v3-select" style="margin-bottom:.85rem"><option>Under $50</option><option>$50&ndash;$100</option><option>$100+</option></select>

    <label class="v3-label">Buying stage</label>
    <select class="v3-select" style="margin-bottom:.85rem"><option>Researching options</option><option>Comparing finalists</option><option>Ready to buy</option></select>

    <label class="v3-label">Required capabilities (select all that matter)</label>
    <div class="v3-chip-group" style="margin-bottom:.85rem">
      <span class="v3-chip active">Contact management</span>
      <span class="v3-chip active">Email tracking</span>
      <span class="v3-chip active">Pipeline management</span>
      <span class="v3-chip">Reporting &amp; dashboards</span>
      <span class="v3-chip">Sales automation</span>
      <span class="v3-chip">AI / Assisted selling</span>
      <span class="v3-chip">Integrations</span>
    </div>

    <label class="v3-label">What matters most? (drag to prioritize)</label>
    <div style="margin-bottom:.85rem">
      <div class="v3-prio"><span class="lbl">Ease of use</span><span class="val">90</span><input type="range" class="v3-range" value="90" min="0" max="100"></div>
      <div class="v3-prio"><span class="lbl">Value for money</span><span class="val">70</span><input type="range" class="v3-range" value="70" min="0" max="100"></div>
      <div class="v3-prio"><span class="lbl">Features</span><span class="val">60</span><input type="range" class="v3-range" value="60" min="0" max="100"></div>
      <div class="v3-prio"><span class="lbl">Scalability</span><span class="val">40</span><input type="range" class="v3-range" value="40" min="0" max="100"></div>
      <div class="v3-prio"><span class="lbl">Security</span><span class="val">30</span><input type="range" class="v3-range" value="30" min="0" max="100"></div>
    </div>

    <label class="v3-label">Other preferences</label>
    <div style="display:flex;flex-direction:column;gap:.45rem;margin-bottom:1rem">
      <label class="v3-toggle" style="justify-content:space-between;width:100%"><span style="font-size:.82rem;color:var(--v3-text-2);font-weight:600">Show only tools with a free trial</span><input type="checkbox" checked><span class="track"></span></label>
      <label class="v3-toggle" style="justify-content:space-between;width:100%"><span style="font-size:.82rem;color:var(--v3-text-2);font-weight:600">Hide tools with setup fees</span><input type="checkbox"><span class="track"></span></label>
      <label class="v3-toggle" style="justify-content:space-between;width:100%"><span style="font-size:.82rem;color:var(--v3-text-2);font-weight:600">Only show SOC 2 certified tools</span><input type="checkbox"><span class="track"></span></label>
    </div>

    <button class="v3-btn v3-btn-primary" style="width:100%">&#x21bb; Update shortlist</button>
  </div>"""


def _sl_row(rank, name, badge, bg, logo, desc, tags, score, fit_class, price, period, sub_help, best_for):
    badge_html = f'<span class="v3-deal-badge best-value">{badge}</span>' if badge == "Best Fit" else (f'<span class="v3-deal-badge new-tag">{badge}</span>' if badge == "New" else "")
    fit_label = {"excellent": "Excellent fit", "great": "Great fit", "good": "Good fit", "poor": "Poor fit"}[fit_class]
    tags_html = "".join(f'<span class="v3-tag">{t}</span>' for t in tags)
    return f"""<div class="v3-row" style="padding:1.05rem 0;border-bottom:1px solid var(--v3-border);align-items:center;gap:1rem">
      <span style="flex:0 0 30px;color:var(--v3-text-5);font-family:var(--v3-ff-display);font-size:1.4rem;font-weight:850;text-align:center">{rank}</span>
      <div class="v3-tool-logo" style="background:{bg};color:{'#000' if bg == '#ffffff' else '#fff'};flex:0 0 56px;width:56px;height:56px">{logo}</div>
      <div style="flex:1;min-width:0">
        <div class="v3-row tight" style="gap:.4rem;align-items:center;flex-wrap:wrap"><h4 style="margin:0;font-size:.95rem;color:#fff">{name}</h4>{badge_html}</div>
        <p style="font-size:.78rem;color:var(--v3-text-4);margin:.15rem 0 .35rem;line-height:1.45">{desc}</p>
        <div class="v3-tool-tags">{tags_html}</div>
      </div>
      <div style="flex:0 0 80px;text-align:center;display:flex;flex-direction:column;align-items:center">
        <div class="v3-fit-circle {fit_class}">{score}</div>
        <div class="v3-fit-label {fit_class}" style="font-size:.6rem;margin-top:.3rem">{fit_label}</div>
      </div>
      <div style="flex:0 0 110px"><b style="color:#fff;font-family:var(--v3-ff-display);font-size:1rem;display:block">{price}</b><small style="color:var(--v3-text-5);font-size:.7rem">{period}</small><small style="color:var(--v3-good);font-size:.7rem;display:block;margin-top:2px">{sub_help}</small></div>
      <div style="flex:0 0 130px"><small style="color:var(--v3-text-3);font-size:.74rem;line-height:1.4;display:block">{best_for}</small></div>
      <div style="flex:0 0 130px;text-align:right;display:flex;flex-direction:column;gap:.35rem;align-items:flex-end">
        <a href="#" class="v3-btn v3-btn-primary v3-btn-sm">Compare</a>
        <a href="#" style="font-size:.72rem;color:var(--v3-red-light);font-weight:700">View details &#8594;</a>
      </div>
    </div>"""


# ───────────── ABOUT (Image 2 row 1) ─────────────
def page_about():
    head = head_html(
        "About SaaSpare — independent SaaS research",
        "We help teams find the best SaaS decisions. Independent research, no sales pitches, no hype. Just clarity.",
        f"{BASE}/pages/v3-preview-about",
    )
    return f"""{head}
{nav_html(active='about')}

<section class="v3-hero left" style="padding-top:6rem;padding-bottom:1.5rem">
  <div class="v3-hero-inner" style="display:grid;grid-template-columns:1.1fr 1fr;gap:3rem;align-items:center">
    <div>
      <span class="v3-eyebrow">About SaaSpare</span>
      <h1 style="margin:1rem 0 .85rem">We help teams find the<br><em>best SaaS</em> decisions.</h1>
      <p class="v3-sub" style="text-align:left;margin:0 0 1.4rem;max-width:520px">SaaSpare is an independent research platform that helps businesses compare SaaS tools, understand pricing, and buy with confidence. No sales pitches. No hype. Just clarity.</p>

      <div class="v3-grid-4" style="grid-template-columns:repeat(4,minmax(0,1fr));gap:.7rem;margin-top:1.4rem">
        {_about_stat("1,150+", "Buyer pages researched", "M9 11h6l-3-7-3 7zM9 11l-2 7h10l-2-7")}
        {_about_stat("800+", "SaaS tools compared", "M3 3h18v18H3z M3 9h18 M9 21V9")}
        {_about_stat("34", "In-depth pricing guides", "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M16 13H8 M16 17H8 M10 9H8")}
        {_about_stat("10,000+", "Teams making smarter decisions", "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M22 21v-2a4 4 0 0 0-3-3.87 M16 3.13a4 4 0 0 1 0 7.75")}
      </div>

      <div class="v3-row tight" style="margin-top:1.1rem;gap:1rem;flex-wrap:wrap;font-size:.8rem;color:var(--v3-text-3)">
        <span class="v3-row tight" style="gap:.4rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="var(--v3-good)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Last updated: May 10, 2026</span>
        <span class="v3-row tight" style="gap:.4rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="var(--v3-good)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Independent &amp; unbiased</span>
        <span class="v3-row tight" style="gap:.4rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="var(--v3-good)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>No paid placements</span>
      </div>
    </div>

    <div>
      <div class="v3-icon-cluster">
        <div class="core"><span>S</span></div>
        <div class="orbit"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg></div>
        <div class="orbit"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
        <div class="orbit"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg></div>
        <div class="orbit"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg></div>
        <div class="orbit"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div>
        <div class="orbit"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
      </div>
      <div class="v3-card" style="margin-top:1.2rem;padding:1rem 1.25rem;text-align:center">
        <h4 style="margin:0 0 .25rem;font-size:.92rem">Clarity in a crowded market.</h4>
        <p style="font-size:.78rem;color:var(--v3-text-4);margin:0;line-height:1.5">SaaS is noisy. Features overlap. Pricing is confusing. We cut through the noise so you can focus on what matters &mdash; impact.</p>
      </div>
    </div>
  </div>
</section>

<div class="v3-container">
  <div class="v3-card v3-card-padded" style="margin:0 0 4rem">
    <h2 style="font-size:1.1rem;margin:0 0 1rem">How we help</h2>
    <div class="v3-grid-4" style="gap:.85rem">
      {_about_help("1. Research", "We analyse pricing pages, docs, reviews, and real buyer feedback.", "M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z")}
      {_about_help("2. Compare", "We normalise features, pricing, and terms side-by-side.", "M3 3h7v7H3z M14 3h7v7h-7z M14 14h7v7h-7z M3 14h7v7H3z")}
      {_about_help("3. Explain", "We write clear, actionable guides without vendor jargon.", "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M16 13H8 M16 17H8")}
      {_about_help("4. Empower", "You make a confident call your team will thank you for.", "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M22 21v-2a4 4 0 0 0-3-3.87 M16 3.13a4 4 0 0 1 0 7.75")}
    </div>
  </div>
</div>

{FOOTER}
{fab()}
</body></html>
"""


def _about_stat(num, lbl, svg_d):
    return f"""<div class="v3-card" style="padding:1rem 1.1rem;text-align:left">
      <div class="v3-card-icon" style="margin-bottom:.55rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="{svg_d}"/></svg></div>
      <div style="font-family:var(--v3-ff-display);font-size:1.4rem;font-weight:850;color:#fff;letter-spacing:-.025em;line-height:1">{num}</div>
      <small style="color:var(--v3-text-4);font-size:.7rem;margin-top:.2rem;display:block;line-height:1.4">{lbl}</small>
    </div>"""


def _about_help(title, desc, svg_d):
    return f"""<div class="v3-card" style="padding:1.2rem 1.3rem">
      <div class="v3-card-icon" style="margin-bottom:.6rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="{svg_d}"/></svg></div>
      <h4 style="margin:.5rem 0 .3rem;font-size:.92rem">{title}</h4>
      <p style="font-size:.78rem;color:var(--v3-text-4);margin:0;line-height:1.5">{desc}</p>
    </div>"""


# ───────────── CONTACT (Image 1 row 1) ─────────────
def page_contact():
    head = head_html(
        "Contact SaaSpare",
        "Build trust and open the door to meaningful relationships. Have a question, partnership idea, or feedback?",
        f"{BASE}/pages/v3-preview-contact",
    )
    return f"""{head}
{nav_html(active='')}

<div class="v3-layout-rail" style="grid-template-columns:1.05fr 1fr 240px;gap:1.4rem;align-items:flex-start;padding-top:6rem">
  <div>
    <span class="v3-eyebrow" style="margin-bottom:1rem;display:inline-flex">We&rsquo;d love to hear from you</span>
    <h1 style="margin:1rem 0 1rem;font-size:clamp(1.8rem,3.6vw,2.6rem)">Let&rsquo;s build smarter<br>SaaS decisions&mdash;<br><em>together.</em></h1>
    <p class="v3-sub" style="text-align:left;margin:0 0 1.5rem">Have a question, partnership idea, or feedback? Our team typically responds within one business day.</p>

    <div class="v3-contact-list">
      <a href="mailto:hello@saaspare.com">
        <div class="v3-contact-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg></div>
        <div><b>Email Us</b><span class="v3-contact-meta">hello@saaspare.com</span><small class="v3-contact-help">For general inquiries and support</small></div>
        <span class="v3-contact-arrow">&#8250;</span>
      </a>
      <a href="mailto:partnerships@saaspare.com">
        <div class="v3-contact-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M22 21v-2a4 4 0 0 0-3-3.87 M16 3.13a4 4 0 0 1 0 7.75"/></svg></div>
        <div><b>Partnerships</b><span class="v3-contact-meta">partnerships@saaspare.com</span><small class="v3-contact-help">For media, affiliates, and integrations</small></div>
        <span class="v3-contact-arrow">&#8250;</span>
      </a>
      <a href="mailto:press@saaspare.com">
        <div class="v3-contact-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h18v18H3z M3 9h18 M9 21V9"/></svg></div>
        <div><b>Press &amp; Media</b><span class="v3-contact-meta">press@saaspare.com</span><small class="v3-contact-help">For press inquiries and media</small></div>
        <span class="v3-contact-arrow">&#8250;</span>
      </a>
      <a href="tel:+14155550199">
        <div class="v3-contact-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg></div>
        <div><b>Business Inquiries</b><span class="v3-contact-meta">(415) 555-0199</span><small class="v3-contact-help">Mon&ndash;Fri, 9am&ndash;6pm PT</small></div>
        <span class="v3-contact-arrow">&#8250;</span>
      </a>
    </div>

    <div class="v3-card v3-card-padded" style="margin-top:1.2rem;display:grid;grid-template-columns:48px 1fr auto;gap:1rem;align-items:center">
      <div class="v3-card-icon" style="width:48px;height:48px;border-radius:12px;background:var(--v3-red-soft);border:1px solid rgba(233,69,96,.32)"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--v3-red-light)" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></div>
      <div><b style="color:#fff;font-size:.92rem;display:block">Partner with SaaSpare</b><small style="color:var(--v3-text-4);font-size:.78rem;display:block;line-height:1.45;margin-top:.15rem">Join leading tools and platforms collaborating to help teams make confident SaaS buying decisions.</small></div>
      <a href="#" class="v3-btn v3-btn-secondary v3-btn-sm">Explore Partnerships &#8594;</a>
    </div>
  </div>

  <div class="v3-card v3-card-padded">
    <h3 style="margin:0 0 .15rem;font-size:1.05rem">Send us a message</h3>
    <p class="v3-muted" style="font-size:.78rem;margin:0 0 1.1rem">Fill out the form and we&rsquo;ll get back to you soon.</p>
    <form onsubmit="return false">
      <div class="v3-grid-2" style="gap:.6rem">
        <div class="v3-form-row"><label>Full name</label><input class="v3-input" type="text" placeholder="Jane Doe"></div>
        <div class="v3-form-row"><label>Work email</label><input class="v3-input" type="email" placeholder="jane@acme.com"></div>
      </div>
      <div class="v3-form-row"><label>Company (optional)</label><input class="v3-input" type="text" placeholder="Acme Inc."></div>
      <div class="v3-form-row"><label>How can we help?</label><textarea class="v3-textarea" rows="5" placeholder="Tell us more about your question or request&hellip;"></textarea></div>
      <button type="submit" class="v3-btn v3-btn-primary" style="width:100%;margin-top:.6rem">Send Message &#8594;</button>
      <p class="v3-help" style="text-align:center;margin-top:.6rem">We respect your privacy. See our <a href="/privacy" style="color:var(--v3-red-light)">Privacy Policy</a>.</p>
    </form>
  </div>

  <aside>
    <div class="v3-rail-card">
      <h3 style="margin:0 0 .9rem">What to expect</h3>
      <ul class="v3-expect-list" style="margin:0;padding:0">
        <li><span class="num">1</span><div><b>Quick reply</b><small>We aim to respond within 1 business day.</small></div></li>
        <li><span class="num">2</span><div><b>Helpful answers</b><small>Our experts provide clear, actionable info.</small></div></li>
        <li><span class="num">3</span><div><b>No spam, ever</b><small>We only email you when it matters.</small></div></li>
      </ul>
    </div>
    <div class="v3-rail-card" style="margin-top:.85rem">
      <h3 style="margin:0 0 .85rem">Trusted by teams at</h3>
      <div style="display:flex;flex-direction:column;gap:.55rem;font-size:.78rem;font-weight:700;color:var(--v3-text-3)">
        <span class="v3-row tight" style="gap:.4rem"><span style="background:#1a1a1a;color:#fff;width:22px;height:22px;border-radius:5px;display:grid;place-items:center;font-size:.62rem;font-weight:850">N</span>Notion</span>
        <span class="v3-row tight" style="gap:.4rem"><span style="background:#ff7a59;color:#fff;width:22px;height:22px;border-radius:5px;display:grid;place-items:center;font-size:.62rem;font-weight:850">H</span>HubSpot</span>
        <span class="v3-row tight" style="gap:.4rem"><span style="background:#0061fe;color:#fff;width:22px;height:22px;border-radius:5px;display:grid;place-items:center;font-size:.62rem;font-weight:850">D</span>Dropbox</span>
        <span class="v3-row tight" style="gap:.4rem"><span style="background:#ffc864;color:#000;width:22px;height:22px;border-radius:5px;display:grid;place-items:center;font-size:.62rem;font-weight:850">M</span>monday<span style="font-weight:400;color:var(--v3-text-4)">.com</span></span>
        <span class="v3-row tight" style="gap:.4rem"><span style="background:#2d8cff;color:#fff;width:22px;height:22px;border-radius:5px;display:grid;place-items:center;font-size:.62rem;font-weight:850">Z</span>zoom</span>
      </div>
    </div>
  </aside>
</div>

{FOOTER}
{fab()}
</body></html>
"""


# ───────────── NEWSLETTER (Image 1 row 2) ─────────────
def page_newsletter():
    head = head_html(
        "Insider insights. Smarter SaaS decisions.",
        "Join 18,000+ SaaS buyers for in-class comparisons, pricing updates, buyer guides, and exclusive deals — delivered weekly.",
        f"{BASE}/pages/v3-preview-newsletter",
    )
    return f"""{head}
{nav_html(active='')}

<section class="v3-hero" style="padding-top:6rem;padding-bottom:1.5rem">
  <div class="v3-hero-inner">
    <div class="v3-section-eyebrow"><span class="v3-eyebrow">&#x2691; Join 18,000+ SaaS buyers</span></div>
    <h1 style="margin:1rem 0 1rem">Insider insights.<br>Smarter <em>SaaS</em> decisions.</h1>
    <p class="v3-sub">Join our newsletter for best-in-class comparisons, pricing updates, buyer guides, and exclusive deals &mdash; delivered weekly.</p>
  </div>
</section>

<div class="v3-layout-rail" style="grid-template-columns:280px minmax(0,1fr) 240px;gap:1.5rem;align-items:flex-start">
  <aside>
    <div class="v3-rail-card">
      <h3 style="margin:0 0 .9rem">Why subscribe?</h3>
      <ul class="v3-bullet-list">
        <li><span class="v3-bul-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="3 6 21 6 18 19 6 19 3 6"/><path d="m6 6 .9-3h10.2L18 6"/></svg></span><div><b>Unbiased comparisons</b><small>Side-by-side breakdowns you can trust.</small></div></li>
        <li><span class="v3-bul-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></span><div><b>Pricing updates</b><small>We track changes as you don&rsquo;t have to.</small></div></li>
        <li><span class="v3-bul-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></span><div><b>Expert buyer guides</b><small>Actionable advice for every team and budget.</small></div></li>
        <li><span class="v3-bul-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg></span><div><b>Exclusive deals</b><small>Subscriber-only discounts on top SaaS tools.</small></div></li>
      </ul>
    </div>
  </aside>

  <main>
    <form class="v3-search" style="max-width:540px;margin:0 auto" onsubmit="return false">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" style="color:rgba(255,255,255,.32)"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
      <input type="email" placeholder="Enter your work email">
      <button type="submit">Subscribe Free &#8594;</button>
    </form>

    <div class="v3-row center" style="gap:1.6rem;margin-top:1rem;flex-wrap:wrap;font-size:.78rem;color:var(--v3-text-4)">
      <span class="v3-row tight" style="gap:.4rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="var(--v3-good)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>No spam.</span>
      <span class="v3-row tight" style="gap:.4rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="var(--v3-good)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Unsubscribe anytime.</span>
      <span class="v3-row tight" style="gap:.4rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="var(--v3-good)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Written by real buyers.</span>
    </div>

    <p class="v3-muted" style="text-align:center;margin:2rem 0 1rem;font-size:.85rem">Loved by SaaS buyers</p>
    <div class="v3-grid-3" style="gap:.8rem">
      {_ns_test("&ldquo;SaaSpare saves me hours of research every month.&rdquo;", "Alex R.", "Head of Ops", "linear-gradient(135deg,#9b6dff,#7048d3)")}
      {_ns_test("&ldquo;The pricing alerts and guides are insanely helpful.&rdquo;", "Priya S.", "Growth Lead", "linear-gradient(135deg,#34d399,#10b981)")}
      {_ns_test("&ldquo;Finally, unbiased info without the fluff.&rdquo;", "Mark T.", "IT Manager", "linear-gradient(135deg,#74a9ff,#3b82f6)")}
    </div>

    <div class="v3-row center" style="gap:1.6rem;margin-top:2rem;flex-wrap:wrap;font-size:.78rem;color:var(--v3-text-4);font-weight:700">
      <span style="font-size:.7rem;text-transform:uppercase;letter-spacing:.5px;color:var(--v3-text-5)">Featured in</span>
      <span>TechCrunch</span><span>Capterra</span><span>Product Hunt</span><span>SaaS Weekly</span><span>FOUNDR</span>
    </div>
  </main>

  <aside>
    <div class="v3-rail-card" style="background:linear-gradient(165deg, rgba(233,69,96,.16), rgba(233,69,96,.04));border-color:rgba(233,69,96,.32)">
      <div class="v3-row between" style="margin-bottom:.85rem"><b style="color:#fff;font-size:.78rem">Latest issue</b><small style="color:var(--v3-text-5);font-size:.7rem">May 10, 2026</small></div>
      <h4 style="margin:0 0 .5rem;font-size:.95rem">Top 10 CRM Tools<br>Compared (2026)</h4>
      <ul style="list-style:none;padding:0;margin:.5rem 0 .85rem;font-size:.74rem;color:var(--v3-text-3);line-height:1.55">
        <li class="v3-row tight" style="gap:.4rem"><span style="color:var(--v3-good)">&#10003;</span> Real pricing and hidden fees</li>
        <li class="v3-row tight" style="gap:.4rem"><span style="color:var(--v3-good)">&#10003;</span> Best fit for small teams</li>
        <li class="v3-row tight" style="gap:.4rem"><span style="color:var(--v3-good)">&#10003;</span> Enterprise-ready options</li>
        <li class="v3-row tight" style="gap:.4rem"><span style="color:var(--v3-good)">&#10003;</span> ROI benchmarks</li>
      </ul>
      <a href="#" class="v3-btn v3-btn-primary v3-btn-sm" style="width:100%">Read Latest Issue &#8594;</a>
      <div class="v3-mag-stack" style="margin-top:1rem">
        <div class="v3-mag">
          <span class="v3-mag-tag">TOP 10</span>
          <h4>CRM Tools<br>Compared (2026)</h4>
          <p>Pricing &middot; Hidden fees &middot; Best fit</p>
          <div class="v3-mag-bars"><span></span><span></span><span></span><span></span><span></span></div>
        </div>
      </div>
    </div>
  </aside>
</div>

{FOOTER}
{fab()}
</body></html>
"""


def _ns_test(quote, name, role, avatar_bg):
    return f"""<div class="v3-testimonial">
      <p>{quote}</p>
      <div class="v3-testimonial-foot">
        <span class="v3-testimonial-avatar" style="background:{avatar_bg}"></span>
        <div><div class="v3-testimonial-name">{name}</div><div class="v3-testimonial-role">{role}</div></div>
      </div>
    </div>"""


# ───────────── COMPARISON / PRICING ARTICLE (Image 9) ─────────────
def page_comparison():
    head = head_html(
        "1Password Pricing 2026: Plans, Costs & What You Actually Pay",
        "We break down 1Password's real-world pricing in May 2026, compare it with Bitwarden, and surface the hidden costs buyers often miss.",
        f"{BASE}/pages/v3-preview-comparison",
    )
    return f"""{head}
{nav_html(active='comparisons')}

<div class="v3-container" style="padding-top:5.5rem"><div class="v3-crumbs"><a href="/">Home</a><span>/</span><a href="/pages/">Comparisons</a><span>/</span><a href="#">Password Management</a><span>/</span><span>1Password Pricing 2026</span></div></div>

<div class="v3-layout-rail" style="grid-template-columns:minmax(0,1fr) 280px;gap:2rem;margin-top:1rem">
  <main>
    <h1 style="margin:0 0 1rem">1Password Pricing 2026: Plans, Costs &amp; What You Actually Pay</h1>
    <p class="v3-lede">We break down 1Password&rsquo;s real-world pricing in May 2026, compare it with Bitwarden, and surface the hidden costs buyers often miss.</p>

    <div class="v3-disc-row">
      <div class="v3-disc-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg><div><h4>Last verified</h4><p>May 20, 2026</p></div></div>
      <div class="v3-disc-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg><div><h4>Unbiased research</h4><p>Independent &amp; objective</p></div></div>
      <div class="v3-disc-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg><div><h4>Affiliate disclosure</h4><p>We may earn a commission</p></div></div>
      <div class="v3-disc-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg><div><h4>Free to read</h4><p>No signup required</p></div></div>
    </div>

    <div class="v3-callout v3-callout-quick">
      <div class="v3-callout-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg></div>
      <div class="v3-callout-body"><h4>Quick answer</h4><p>1Password pricing in May 2026 starts at <strong>$2.99/user/month (Starter)</strong> and <strong>$7.99/user/month (Pro)</strong>. It&rsquo;s the best pick for teams that want premium security and ease of use &mdash; if budget isn&rsquo;t the top priority.</p></div>
    </div>

    <div class="v3-tldr-bank">
      <div class="v3-tldr-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 7c0-1.1-.9-2-2-2H7C5.9 5 5 5.9 5 7v8c0 1.1.9 2 2 2h2v3l3-3h5c1.1 0 2-.9 2-2z"/></svg></div>
      <div class="v3-tldr-body"><h4>TL;DR &mdash; The real cost takeaway</h4><p>Expect to pay $2.99&ndash;$7.99 per user/month for 1Password.</p><small>Add taxes and potential seat overages. Free trial: 14 days. No credit card required.</small></div>
    </div>

    <h2 id="pricing">1Password pricing at a glance</h2>
    <div class="v3-plan-grid" style="grid-template-columns:repeat(4,minmax(0,1fr));gap:.7rem">
      <div class="v3-plan"><span class="v3-plan-flag green">Best for individuals</span><h3>Starter</h3><div class="v3-plan-price">$2.99</div><div class="v3-plan-period">user/month</div><p class="v3-plan-desc">Personal &amp; basic sharing</p></div>
      <div class="v3-plan popular"><span class="v3-plan-flag">Most popular</span><h3>Pro</h3><div class="v3-plan-price">$7.99</div><div class="v3-plan-period">user/month</div><p class="v3-plan-desc">Full features for individuals &amp; small teams</p></div>
      <div class="v3-plan"><h3>Enterprise</h3><div class="v3-plan-price">Custom</div><div class="v3-plan-period">Contact sales</div><p class="v3-plan-desc">Advanced controls &amp; SSO for organizations</p></div>
      <div class="v3-plan"><h3>Free Trial</h3><div class="v3-plan-price">14 days</div><div class="v3-plan-period">No credit card</div><p class="v3-plan-desc">Try any plan free</p></div>
    </div>

    <div class="v3-row center" style="margin:1.2rem 0 1.5rem"><a href="#" class="v3-btn v3-btn-primary v3-btn-lg">Start 14-day free trial &#8594;</a></div>
    <p class="v3-help" style="text-align:center;margin:0 0 2rem">No credit card required. Cancel anytime.</p>

    <h2 id="vs-bitwarden">1Password vs Bitwarden &mdash; Pricing comparison</h2>
    <div class="v3-table-wrap">
      <table class="v3-table">
        <thead><tr><th>Feature</th><th>1Password <span class="v3-badge red" style="margin-left:.4rem">Best Pick</span></th><th>Bitwarden</th></tr></thead>
        <tbody>
          <tr><td>Starter Plan</td><td class="col-best">$2.99/user/month</td><td>$4.00/user/month</td></tr>
          <tr><td>Pro Plan</td><td class="col-best">$7.99/user/month</td><td>$6.00/user/month</td></tr>
          <tr><td>Enterprise Plan</td><td>Custom</td><td>Custom</td></tr>
          <tr><td>Free Plan</td><td>14 days trial</td><td class="col-best">7 days trial</td></tr>
          <tr><td>Family / Team sharing</td><td class="col-best">Yes (Starter &amp; Pro)</td><td>Yes (Premium)</td></tr>
          <tr><td>SSO &amp; Advanced Security</td><td>Yes (Pro &amp; Enterprise)</td><td class="col-best">Yes (Premium &amp; Enterprise)</td></tr>
          <tr><td>Data Storage Region</td><td>Global (US/EU)</td><td>US</td></tr>
          <tr><td>Support</td><td>Email support (Starter+)<br>Priority (Pro+)</td><td>Community (Free)<br>Email (Premium+)</td></tr>
        </tbody>
      </table>
    </div>
    <p class="v3-help" style="margin:.5rem 0 2rem">Pricing verified May 20, 2026. Taxes may apply. Source: <a href="#" style="color:var(--v3-red-light)">1Password.com</a>, <a href="#" style="color:var(--v3-red-light)">Bitwarden.com</a></p>

    <h2 id="hidden-fees">Hidden fees &amp; what buyers actually pay</h2>
    <div class="v3-grid-4" style="gap:.6rem;margin-bottom:2rem">
      <div class="v3-card" style="padding:.85rem 1rem"><div class="v3-row tight" style="gap:.4rem;color:var(--v3-red-light);font-size:.78rem;font-weight:800;margin-bottom:.3rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>Seat-based pricing</div><small style="font-size:.74rem;color:var(--v3-text-4);line-height:1.4;display:block">You pay per active seat each month. Remove users to avoid unused seat charges.</small></div>
      <div class="v3-card" style="padding:.85rem 1rem"><div class="v3-row tight" style="gap:.4rem;color:var(--v3-red-light);font-size:.78rem;font-weight:800;margin-bottom:.3rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>Enterprise add-ons</div><small style="font-size:.74rem;color:var(--v3-text-4);line-height:1.4;display:block">Advanced SSO, SCIM, and custom integrations may require add-ons.</small></div>
      <div class="v3-card" style="padding:.85rem 1rem"><div class="v3-row tight" style="gap:.4rem;color:var(--v3-red-light);font-size:.78rem;font-weight:800;margin-bottom:.3rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>Taxes &amp; regional pricing</div><small style="font-size:.74rem;color:var(--v3-text-4);line-height:1.4;display:block">Prices exclude VAT/GST in some regions. Final cost varies by location.</small></div>
      <div class="v3-card" style="padding:.85rem 1rem"><div class="v3-row tight" style="gap:.4rem;color:var(--v3-red-light);font-size:.78rem;font-weight:800;margin-bottom:.3rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>Free trial limits</div><small style="font-size:.74rem;color:var(--v3-text-4);line-height:1.4;display:block">14-day trial includes full features. No credit card required.</small></div>
    </div>

    <div class="v3-card v3-card-emph" style="padding:1.4rem 1.6rem;display:grid;grid-template-columns:64px 1fr auto;gap:1.1rem;align-items:center;margin:1.6rem 0">
      <div class="v3-card-icon" style="width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg, rgba(233,69,96,.32), rgba(233,69,96,.08));border-color:rgba(233,69,96,.4)"><svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 20l3-12 5 4 4-7 5 5 3-3 1 13z M2 20h20"/></svg></div>
      <div><h3 style="margin:0 0 .25rem;font-size:1.1rem">Our top pick</h3><p style="margin:0;font-size:.85rem;color:var(--v3-text-3)">1Password delivers the best balance of security, usability, and features for most teams and businesses.</p></div>
      <div style="text-align:center"><a href="#" class="v3-btn v3-btn-primary">Start your free trial &#8594;</a><br><small style="color:var(--v3-text-5);font-size:.7rem;margin-top:.4rem;display:inline-block">14 days free. Cancel anytime.</small></div>
    </div>

    <h2 id="review">1Password review &mdash; Is it worth it?</h2>
    <div class="v3-grid-3" style="gap:.7rem;margin-bottom:1.4rem">
      <div class="v3-card" style="padding:1rem 1.2rem"><h4 style="margin:0 0 .35rem;font-size:.92rem;color:var(--v3-red-light)">&#x1F510; Security you can trust</h4><p style="font-size:.78rem;color:var(--v3-text-4);margin:0;line-height:1.5">Industry-leading encryption, zero-knowledge architecture, and regular audits keep your data safe.</p></div>
      <div class="v3-card" style="padding:1rem 1.2rem"><h4 style="margin:0 0 .35rem;font-size:.92rem;color:var(--v3-red-light)">&#x26A1; Built for productivity</h4><p style="font-size:.78rem;color:var(--v3-text-4);margin:0;line-height:1.5">Clean UI, powerful sharing, and deep integrations across browsers and devices.</p></div>
      <div class="v3-card" style="padding:1rem 1.2rem"><h4 style="margin:0 0 .35rem;font-size:.92rem;color:var(--v3-red-light)">&#x1F4BC; Great for teams</h4><p style="font-size:.78rem;color:var(--v3-text-4);margin:0;line-height:1.5">Granular permissions, SSO, and activity logs make it easy to manage access at scale.</p></div>
    </div>
    <p style="margin:0 0 2rem"><a href="#" class="v3-link-cta">Read our full 1Password review &#8594;</a></p>

    <div class="v3-grid-2" style="gap:1rem;margin-bottom:2rem">
      <div>
        <h3 style="margin:0 0 .7rem;font-size:1rem">Related comparisons</h3>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem">
          <a class="v3-card" href="#" style="padding:.85rem"><b style="color:#fff;font-size:.78rem;display:block;margin-bottom:.25rem">1Password vs Bitwarden</b><small style="font-size:.7rem;color:var(--v3-text-4)">Which password manager is better in 2026?</small></a>
          <a class="v3-card" href="#" style="padding:.85rem"><b style="color:#fff;font-size:.78rem;display:block;margin-bottom:.25rem">1Password vs Dashlane</b><small style="font-size:.7rem;color:var(--v3-text-4)">Features, pricing, and real-cost comparison.</small></a>
          <a class="v3-card" href="#" style="padding:.85rem"><b style="color:#fff;font-size:.78rem;display:block;margin-bottom:.25rem">1Password vs Keeper</b><small style="font-size:.7rem;color:var(--v3-text-4)">Security, pricing, and team features compared.</small></a>
        </div>
      </div>
      <div>
        <h3 style="margin:0 0 .7rem;font-size:1rem">FAQs</h3>
        <details class="v3-accordion"><summary>Is there a 1Password free plan?</summary><div class="v3-accordion-body">No, but there&rsquo;s a 14-day free trial &mdash; no credit card required.</div></details>
        <details class="v3-accordion"><summary>Can I try 1Password before I buy?</summary><div class="v3-accordion-body">Yes, every plan includes a 14-day free trial.</div></details>
        <details class="v3-accordion"><summary>What payment methods are accepted?</summary><div class="v3-accordion-body">All major credit cards. Enterprise plans support invoicing.</div></details>
        <p style="margin:.6rem 0 0"><a href="#" class="v3-link-cta">View all FAQs &#8594;</a></p>
      </div>
    </div>

    <p class="v3-help" style="text-align:center;margin:0 0 3rem;border-top:1px solid var(--v3-border);padding-top:1rem">SaaSpare is an independent comparison site. We may earn a commission when you buy through links on our site at no extra cost to you. We only recommend tools we believe provide real value.</p>
  </main>

  <aside>
    <div class="v3-sticky-rail">
      <div class="v3-rail-card" style="background:linear-gradient(165deg, rgba(233,69,96,.14), rgba(233,69,96,.04));border-color:rgba(233,69,96,.32)">
        <h3 style="margin:0 0 .65rem;display:flex;align-items:center;gap:.4rem"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="var(--v3-red-light)" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>True Cost Detector</h3>
        <p style="font-size:.74rem;color:var(--v3-red-light);margin:0 0 .5rem;font-weight:700">Hidden fees to know</p>
        <ul style="list-style:none;padding:0;margin:0;font-size:.78rem;color:var(--v3-text-3);line-height:1.6">
          <li class="v3-row tight" style="gap:.4rem"><span style="color:var(--v3-good)">&#10003;</span>Extra seats billed monthly</li>
          <li class="v3-row tight" style="gap:.4rem"><span style="color:var(--v3-good)">&#10003;</span>Enterprise add-ons<br><small style="color:var(--v3-text-5);padding-left:1.1rem;display:block">(e.g., SCIM, advanced SSO)</small></li>
          <li class="v3-row tight" style="gap:.4rem"><span style="color:var(--v3-good)">&#10003;</span>Taxes vary by region</li>
          <li class="v3-row tight" style="gap:.4rem"><span style="color:var(--v3-good)">&#10003;</span>No setup fees</li>
        </ul>
        <div class="v3-row tight" style="gap:.4rem;margin-top:.7rem;font-size:.78rem"><span style="color:var(--v3-good)">&#x25CF;</span><b style="color:#fff">Overall: Low risk</b></div>
        <small style="display:block;color:var(--v3-text-4);font-size:.7rem;margin-top:.2rem">Transparent pricing</small>
      </div>

      <div class="v3-rail-card" style="margin-top:.85rem">
        <h3 style="margin:0 0 .65rem">Best alternatives</h3>
        <div class="v3-rail-list">
          <a href="#"><div class="v3-tool-logo" style="background:#175ddc;color:#fff;width:30px;height:30px;border-radius:8px;font-size:.74rem">BW</div><span><b>Bitwarden</b><small>Best budget option</small></span><span style="color:var(--v3-red-light);margin-left:auto">&#8250;</span></a>
          <a href="#"><div class="v3-tool-logo" style="background:#0e7490;color:#fff;width:30px;height:30px;border-radius:8px;font-size:.74rem">D</div><span><b>Dashlane</b><small>Best for ease of use</small></span><span style="color:var(--v3-red-light);margin-left:auto">&#8250;</span></a>
          <a href="#"><div class="v3-tool-logo" style="background:#febe10;color:#000;width:30px;height:30px;border-radius:8px;font-size:.74rem">K</div><span><b>Keeper</b><small>Best for security</small></span><span style="color:var(--v3-red-light);margin-left:auto">&#8250;</span></a>
        </div>
        <p style="margin:.6rem 0 0"><a href="#" class="v3-link-cta" style="font-size:.78rem">See all alternatives &#8594;</a></p>
      </div>

      <div class="v3-toc" style="margin-top:.85rem;position:relative;top:auto">
        <h4>On this page</h4>
        <ol>
          <li><a href="#" class="active">Quick answer</a></li>
          <li><a href="#pricing">Pricing at a glance</a></li>
          <li><a href="#vs-bitwarden">1Password vs Bitwarden</a></li>
          <li><a href="#hidden-fees">Hidden fees</a></li>
          <li><a href="#review">Our top pick</a></li>
          <li><a href="#review">1Password review</a></li>
          <li><a href="#related">Related comparisons</a></li>
          <li><a href="#faqs">FAQs</a></li>
        </ol>
      </div>
    </div>
  </aside>
</div>

{FOOTER}
{fab()}
</body></html>
"""


if __name__ == "__main__":
    pages = {
        "v3-preview-shortlist.html":   page_shortlist(),
        "v3-preview-comparison.html":  page_comparison(),
        "v3-preview-about.html":       page_about(),
        "v3-preview-contact.html":     page_contact(),
        "v3-preview-newsletter.html":  page_newsletter(),
    }
    for name, html in pages.items():
        target = OUT_DIR / name
        target.write_text(html, encoding="utf-8")
        print(f"  wrote {target.relative_to(ROOT)}  ({len(html):,} bytes)")
