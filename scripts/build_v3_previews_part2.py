"""Continuation of build_v3_previews.py — pages 04..12.

Builds: deal-radar, shortlist, library, about, privacy, affiliate-disclosure,
contact, 404, newsletter.
"""
from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from v3_partials import nav_html, head_html, FOOTER  # noqa: E402

OUT_DIR = ROOT / "site" / "pages"
BASE = "https://saaspare.org"


def fab() -> str:
    return '<a class="v3-fab" href="#decision-trail">Decision Trail <b>5</b></a>'


# ─────────────────────────────────────────────────────────────────────
# 04. DEAL RADAR  — clones Image 8
# ─────────────────────────────────────────────────────────────────────
def page_deal_radar() -> str:
    head = head_html(
        "Deal Radar — Real SaaS offers, verified in real-time",
        "Track price drops, promo codes, hidden fees and stackable offers across 128 SaaS tools.",
        f"{BASE}/pages/v3-preview-deal-radar",
    )
    return f"""{head}
{nav_html(active='deals')}

<section class="v3-hero left" style="padding-bottom:1.5rem">
  <div class="v3-container" style="display:grid;grid-template-columns:1fr 280px;gap:2rem;align-items:flex-end">
    <div>
      <span class="v3-eyebrow">Live market intelligence</span>
      <h1>Deal Radar: Real SaaS<br>offers, <em>verified</em> in real-time.</h1>
      <p class="v3-lede" style="margin:1rem 0 0;max-width:620px">We track price drops, promo codes, hidden fees and stackable offers — so you never overpay for the tools your team depends on.</p>
    </div>
    <div class="v3-card-emph v3-card-padded" style="text-align:left;padding:1.2rem 1.4rem">
      <span class="v3-badge live" style="background:transparent;color:var(--v3-good);padding:0;font-size:.7rem">LIVE</span>
      <div style="font-family:var(--v3-ff-display);font-size:2.6rem;font-weight:850;color:var(--v3-red-light);line-height:1;margin:.35rem 0 .25rem">128</div>
      <div style="font-size:.85rem;color:var(--v3-text-2);margin-bottom:.2rem">Active offers right now</div>
      <div style="font-size:.74rem;color:var(--v3-text-5)">Updated 3m ago</div>
    </div>
  </div>
</section>

<div class="v3-container">
  <div class="v3-card v3-card-padded" style="padding:1rem 1.2rem;margin-bottom:1rem">
    <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:.7rem;align-items:end">
      <div><label class="v3-label">Category</label><select class="v3-select"><option>All Categories</option></select></div>
      <div><label class="v3-label">Vendor</label><select class="v3-select"><option>All Vendors</option></select></div>
      <div><label class="v3-label">Free trial</label><select class="v3-select"><option>Any</option></select></div>
      <div><label class="v3-label">Promo / Code</label><select class="v3-select"><option>Any</option></select></div>
      <div><label class="v3-label">Annual Discount</label><select class="v3-select"><option>Any</option></select></div>
      <div><label class="v3-label">Hidden-fee alert</label><select class="v3-select"><option>Any</option></select></div>
      <div><label class="v3-label">Urgency</label><select class="v3-select"><option>Any</option></select></div>
    </div>
    <div class="v3-row tight" style="margin-top:.85rem">
      <button class="v3-btn v3-btn-primary v3-btn-sm">All Offers <span class="v3-tag" style="background:rgba(255,255,255,.18);color:#fff;border:0;margin-left:6px">128</span></button>
      <button class="v3-btn v3-btn-secondary v3-btn-sm">📉 Price Drops <span class="v3-tag" style="margin-left:6px">32</span></button>
      <button class="v3-btn v3-btn-secondary v3-btn-sm">🆕 New Offers <span class="v3-tag green" style="margin-left:6px">NEW</span></button>
      <button class="v3-btn v3-btn-secondary v3-btn-sm">⏳ Ending Soon <span class="v3-tag red" style="margin-left:6px">14</span></button>
      <button class="v3-btn v3-btn-secondary v3-btn-sm">🎯 Exclusive <span class="v3-tag" style="margin-left:6px">9</span></button>
      <button class="v3-btn v3-btn-secondary v3-btn-sm">🔗 Stackable <span class="v3-tag" style="margin-left:6px">11</span></button>
    </div>
  </div>
</div>

<div class="v3-layout-main">
  <main>
    <div class="v3-row between" style="margin-bottom:1rem">
      <span class="v3-muted" style="font-size:.85rem"><b style="color:#fff">128 offers</b> found</span>
      <div><span class="v3-muted" style="font-size:.85rem;margin-right:.5rem">Sort by</span><select class="v3-select" style="display:inline-block;width:auto"><option>Best value</option></select></div>
    </div>

    {_deal_card("1Password","Password manager for teams and businesses.",
        ["Security","SSO","Team Management"], "PRICE DROP","#0070ad","1P",
        "BEST VALUE","-$4.00","20% off","Pro Plan","$7.99","$3.99","/user/month","May 20, 2026")}
    {_deal_card("HubSpot CRM","Free CRM for teams who want to grow better.",
        ["CRM","Sales","Marketing"], None,"#ff7a59","H",
        None,None,"FREE PLAN","Free forever","$0",None,"No credit card required","May 19, 2026")}
    {_deal_card("Notion","Docs, wikis, and projects — all in one workspace.",
        ["Productivity","Collaboration","Knowledge"], None,"#fff","N",
        None,None,"20% off","Plus Plan (Annual)","$12.00","$9.60","/user/month","May 18, 2026")}
    {_deal_card("Pipedrive","Sales CRM built to help you sell more.",
        ["Sales","CRM","Pipeline"], None,"#1a1a1a","P",
        None,None,"25% off","Advanced Plan (Annual)","$24.90","$18.68","/user/month","May 20, 2026")}
    {_deal_card("Bitwarden","Open-source password manager for teams.",
        ["Security","SSO","Open Source"], None,"#175ddc","B",
        None,None,"15% off","Teams Plan (Annual)","$5.00","$4.25","/user/month","May 17, 2026")}
    {_deal_card("Trello","Visual project management that works.",
        ["Project Mgmt","Kanban","Collaboration"], "PRICE DROP","#0079bf","T",
        None,"-$1.20","20% off","Standard Plan (Annual)","$5.00","$4.00","/user/month","May 19, 2026")}

    <div style="text-align:center;margin:2rem 0"><button class="v3-btn v3-btn-secondary">Load more offers &#8595;</button></div>
  </main>

  <aside>
    <div class="v3-rail-card">
      <h3 style="display:flex;align-items:center;gap:.5rem"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="var(--v3-red)" stroke-width="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>Price Drop Alerts <a href="#" style="margin-left:auto;font-size:.74rem;color:var(--v3-red-light);font-weight:700">View all</a></h3>
      <div class="v3-rail-row"><div class="v3-tool-logo" style="background:#4a154b">S</div><div style="flex:1"><b>Slack</b><small>Pro Plan</small></div><div style="text-align:right"><div style="color:var(--v3-good);font-weight:800;font-size:.85rem">-$2.00</div><small>2h ago</small></div></div>
      <div class="v3-rail-row"><div class="v3-tool-logo" style="background:#0d6efd">C</div><div style="flex:1"><b>Calendly</b><small>Teams Plan</small></div><div style="text-align:right"><div style="color:var(--v3-good);font-weight:800;font-size:.85rem">-$1.50</div><small>5h ago</small></div></div>
      <div class="v3-rail-row"><div class="v3-tool-logo" style="background:#7b68ee">C</div><div style="flex:1"><b>ClickUp</b><small>Business Plan</small></div><div style="text-align:right"><div style="color:var(--v3-good);font-weight:800;font-size:.85rem">-$3.00</div><small>1d ago</small></div></div>
    </div>

    <div class="v3-rail-card">
      <h3 style="display:flex;align-items:center;gap:.5rem"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="var(--v3-good)" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>Recently Verified <a href="#" style="margin-left:auto;font-size:.74rem;color:var(--v3-red-light);font-weight:700">View all</a></h3>
      <div class="v3-rail-row"><div class="v3-tool-logo" style="background:#0d65b8">A</div><div style="flex:1"><b>Airtable</b><small>Verified May 20, 2026</small></div></div>
      <div class="v3-rail-row"><div class="v3-tool-logo" style="background:#5e6ad2">L</div><div style="flex:1"><b>Linear</b><small>Verified May 20, 2026</small></div></div>
      <div class="v3-rail-row"><div class="v3-tool-logo" style="background:#0acf83">F</div><div style="flex:1"><b>Figma</b><small>Verified May 19, 2026</small></div></div>
    </div>

    <div class="v3-rail-card">
      <h3 style="display:flex;align-items:center;gap:.5rem"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="var(--v3-warn)" stroke-width="2"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>Buyer Warnings <a href="#" style="margin-left:auto;font-size:.74rem;color:var(--v3-red-light);font-weight:700">View all</a></h3>
      <div class="v3-rail-row" style="border:0;padding:.4rem 0"><span style="flex:1;font-size:.82rem">● Hidden fees detected</span><b style="color:var(--v3-warn)">3 tools</b></div>
      <div class="v3-rail-row" style="padding:.4rem 0"><span style="flex:1;font-size:.82rem">● Auto-renewal enabled</span><b style="color:var(--v3-warn)">5 tools</b></div>
      <div class="v3-rail-row" style="padding:.4rem 0"><span style="flex:1;font-size:.82rem">● Price increased recently</span><b style="color:var(--v3-warn)">2 tools</b></div>
    </div>

    <div class="v3-rail-card v3-card-emph">
      <h3 style="display:flex;align-items:center;gap:.5rem;color:var(--v3-red-light)"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>Never miss a deal</h3>
      <p style="font-size:.8rem;color:var(--v3-text-3);margin:0 0 .85rem">Get price drop alerts and new offers delivered to your inbox.</p>
      <div class="v3-row tight" style="gap:.4rem"><input type="email" placeholder="you@company.com" class="v3-input" style="flex:1"><button class="v3-btn v3-btn-primary v3-btn-sm">Subscribe</button></div>
      <p class="v3-help" style="margin-top:.5rem">No spam. Unsubscribe anytime.</p>
    </div>
  </aside>
</div>

{FOOTER}
{fab()}
</body></html>
"""


def _deal_card(name, desc, tags, flag, logo_bg, logo_text,
               value_badge, drop, percent, plan, was_price, now_price, period, verified):
    flag_html = f'<span class="v3-tag red" style="position:absolute;top:0;left:0;border-radius:0 0 12px 0;padding:5px 14px;font-size:.65rem">{flag}</span>' if flag else ""
    val_badge = f'<span class="v3-badge" style="margin-left:.5rem">{value_badge}</span>' if value_badge else ""
    drop_html = f'<div style="color:var(--v3-good);font-weight:800;font-size:.95rem">{drop}</div>' if drop else ""
    was_html = f'<div style="color:var(--v3-text-5);text-decoration:line-through;font-size:.78rem">{was_price}</div>' if was_price and now_price else ""
    period_html = f'<div style="color:var(--v3-text-5);font-size:.74rem">{period}</div>' if period else ""
    return f"""    <div class="v3-tool-card" style="position:relative;margin-bottom:.75rem;padding-top:1.3rem">
      {flag_html}
      <div class="v3-tool-logo" style="background:{logo_bg};color:{'#000' if logo_bg == '#fff' else '#fff'}">{logo_text}</div>
      <div class="v3-tool-body">
        <h3>{name}{val_badge}</h3>
        <p>{desc}</p>
        <div class="v3-tool-tags">{''.join(f'<span class="v3-tag">{t}</span>' for t in tags)}</div>
        <div style="font-size:.74rem;color:var(--v3-good);margin-top:.55rem">✓ Verified {verified} · Official Pricing</div>
      </div>
      <div class="v3-tool-actions" style="text-align:right;align-items:flex-end">
        {drop_html}
        <div style="color:var(--v3-red-light);font-weight:800;font-size:.85rem">{percent}</div>
        <div style="color:var(--v3-text-5);font-size:.78rem;margin-bottom:.2rem">{plan}</div>
        {was_html}
        <div style="font-family:var(--v3-ff-display);font-size:1.4rem;font-weight:850;color:#fff;line-height:1">{now_price}</div>
        {period_html}
        <a href="/go/{name.lower().replace(' ','-')}" rel="nofollow sponsored" class="v3-btn v3-btn-primary v3-btn-sm" style="margin-top:.5rem">View Offer &#8594;</a>
      </div>
    </div>"""


# ─────────────────────────────────────────────────────────────────────
# 05. SHORTLIST BUILDER  — clones Image 6
# ─────────────────────────────────────────────────────────────────────
def page_shortlist() -> str:
    head = head_html(
        "Build your perfect SaaS shortlist",
        "Tell us what you need and we'll rank the best tools for your team based on fit, pricing, and real-world performance.",
        f"{BASE}/pages/v3-preview-shortlist",
    )
    return f"""{head}
{nav_html(active='shortlist')}

<div class="v3-container" style="padding-top:5.5rem"><div class="v3-crumbs"><a href="/">Home</a><span>/</span><span>Shortlist Builder</span></div></div>

<section class="v3-hero" style="padding-top:1rem;padding-bottom:1.5rem">
  <div class="v3-hero-inner">
    <span class="v3-eyebrow">Smart shortlist builder</span>
    <h1>Build your <em>perfect</em> shortlist.</h1>
    <p class="v3-sub">Tell us what you need and we'll rank the best tools for your team based on fit, pricing, and real-world performance.</p>
    <div class="v3-trust-row" style="margin-top:1.2rem">
      <span class="v3-trust-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg><b style="color:#fff">Unbiased rankings</b>&nbsp;We don't play favorites.</span>
      <span class="v3-trust-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg><b style="color:#fff">Real pricing, real outcomes</b>&nbsp;Data from verified buyer pages.</span>
    </div>
  </div>
</section>

<div class="v3-layout-main" style="grid-template-columns:340px minmax(0,1fr)">
  <aside>
    <div class="v3-card v3-card-padded">
      <div class="v3-row between" style="margin-bottom:.85rem">
        <h3 style="margin:0;font-size:1rem;display:flex;align-items:center;gap:.5rem"><span style="display:grid;place-items:center;width:24px;height:24px;border-radius:50%;background:var(--v3-red);color:#fff;font-size:.78rem;font-weight:800">1</span>Your requirements</h3>
        <button class="v3-btn-ghost v3-btn-sm" style="background:transparent;border:0;color:var(--v3-text-4);font:inherit;font-weight:600;font-size:.78rem;cursor:pointer">⟲ Reset</button>
      </div>

      <label class="v3-label">Category</label>
      <select class="v3-select"><option>CRM &amp; Sales</option></select>

      <label class="v3-label" style="margin-top:.85rem">Team size</label>
      <div class="v3-segmented"><label class="active">Solo</label><label>2-50</label><label>50-500</label><label>500+</label></div>

      <label class="v3-label" style="margin-top:.85rem">Monthly budget (per user)</label>
      <select class="v3-select"><option>Under $50</option></select>

      <label class="v3-label" style="margin-top:.85rem">Buying stage</label>
      <select class="v3-select"><option>Researching options</option></select>

      <label class="v3-label" style="margin-top:.85rem">Required capabilities (select all that matter)</label>
      <div class="v3-row tight">
        <span class="v3-tag red">Contact management</span>
        <span class="v3-tag red">Email tracking</span>
        <span class="v3-tag red">Pipeline management</span>
        <span class="v3-tag">Reporting &amp; dashboards</span>
        <span class="v3-tag">Sales automation</span>
        <span class="v3-tag">AI / Assisted selling</span>
        <span class="v3-tag">Integrations</span>
      </div>

      <label class="v3-label" style="margin-top:1rem">What matters most? (drag to prioritize)</label>
      <div class="v3-slider-row"><span>Ease of use</span><input type="range" min="0" max="100" value="90" style="width:100%"><b>90</b></div>
      <div class="v3-slider-row"><span>Value for money</span><input type="range" min="0" max="100" value="70" style="width:100%"><b>70</b></div>
      <div class="v3-slider-row"><span>Features</span><input type="range" min="0" max="100" value="60" style="width:100%"><b>60</b></div>
      <div class="v3-slider-row"><span>Scalability</span><input type="range" min="0" max="100" value="40" style="width:100%"><b>40</b></div>
      <div class="v3-slider-row"><span>Security</span><input type="range" min="0" max="100" value="30" style="width:100%"><b>30</b></div>

      <h4 style="font-size:.74rem;color:var(--v3-text-4);margin:1rem 0 .55rem;text-transform:uppercase;letter-spacing:.4px;font-weight:800">Other preferences</h4>
      <label class="v3-toggle" style="display:flex;justify-content:space-between;width:100%;padding:.4rem 0;font-size:.85rem;color:var(--v3-text-2)">Show only tools with a free trial<input type="checkbox" checked><span class="track"></span></label>
      <label class="v3-toggle" style="display:flex;justify-content:space-between;width:100%;padding:.4rem 0;font-size:.85rem;color:var(--v3-text-2)">Hide tools with setup fees<input type="checkbox"><span class="track"></span></label>
      <label class="v3-toggle" style="display:flex;justify-content:space-between;width:100%;padding:.4rem 0;font-size:.85rem;color:var(--v3-text-2)">Only show SOC 2 certified tools<input type="checkbox"><span class="track"></span></label>

      <button class="v3-btn v3-btn-primary v3-btn-lg" style="width:100%;margin-top:1.2rem">↻ Update shortlist</button>
    </div>

    <div class="v3-card v3-card-padded" style="margin-top:1rem">
      <h4 style="margin:0 0 .85rem;font-size:.92rem">How we score &amp; rank</h4>
      <div style="display:flex;flex-direction:column;gap:.5rem;font-size:.82rem;color:var(--v3-text-3)">
        <span>✓ <b style="color:#fff">Fit Score</b> combines your priorities, features, and team context.</span>
        <span>✓ <b style="color:#fff">Pricing Score</b> reflects total cost at your team size.</span>
        <span>✓ <b style="color:#fff">Momentum Score</b> includes reviews, search demand &amp; recency.</span>
        <span>✓ Scores are updated daily from verified buyer pages.</span>
      </div>
      <p style="margin:.85rem 0 0"><a href="/methodology" class="v3-link-cta">Learn more about our methodology &#8594;</a></p>
    </div>
  </aside>

  <main>
    <div class="v3-card v3-card-padded">
      <div class="v3-row between" style="margin-bottom:1.2rem">
        <h3 style="margin:0;display:flex;align-items:center;gap:.5rem"><span style="display:grid;place-items:center;width:24px;height:24px;border-radius:50%;background:var(--v3-red);color:#fff;font-size:.78rem;font-weight:800">2</span>Your ranked shortlist</h3>
        <span class="v3-muted" style="font-size:.78rem">9 results · Updated just now</span>
      </div>
      <div class="v3-row" style="font-size:.7rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.4px;padding:0 1rem .55rem;font-weight:800;border-bottom:1px solid var(--v3-border);margin-bottom:.5rem">
        <div style="width:38px"></div><div style="flex:1">Tool</div><div style="width:90px;text-align:center">Fit Score</div><div style="width:120px">Pricing (est.)</div><div style="width:160px">Best for</div><div style="width:120px">Action</div>
      </div>
      {_short_row(1,"H","#ff7a59","HubSpot CRM","Powerful, user-friendly CRM with marketing, sales, and service in one unified platform.",["Free plan","Email tracking","Pipelines"],94,"Excellent fit","$0–$90","/user/mo<br>Free plan available","Growing teams that want an all-in-one CRM.","Best Fit")}
      {_short_row(2,"P","#1a1a1a","Pipedrive","Sales-first CRM built to help teams close more deals, faster.",["14-day trial","Visual pipeline","Automation"],89,"Great fit","$14–$99","/user/mo<br>14-day free trial","Small to mid-size teams focused on closing.")}
      {_short_row(3,"N","#fff","Notion CRM","Flexible, modern CRM for teams that love Notion's connected workspace.",["Free plan","Custom views","No code"],82,"Very good","$0–$18","/user/mo<br>Free plan available","Teams that want flexibility and ease of use.","New",text_color="#000")}
      {_short_row(4,"S","#00a1e0","Salesforce Sales Cloud","Enterprise-grade CRM with unmatched customization and scalability.",["Free trial","AI insights","AppExchange"],78,"Good fit","$25–$500+","/user/mo<br>30-day free trial","Enterprise teams with complex needs.")}
      {_short_row(5,"f.","#f76b15","folk CRM","Simple, beautiful CRM for relationship-first teams.",["14-day trial","Contact hub","Integrations"],74,"Good fit","$20–$40","/user/mo<br>14-day free trial","Small teams that value relationships &amp; simplicity.")}
      <div style="text-align:center;margin-top:1rem"><a href="#" class="v3-link-cta">View 4 more results &#8595;</a></div>
    </div>

    <div class="v3-card v3-card-padded" style="margin-top:1.2rem">
      <div class="v3-row between" style="flex-wrap:wrap;gap:.85rem">
        <div><h3 style="margin:0;font-size:1rem;display:flex;align-items:center;gap:.5rem"><span style="display:grid;place-items:center;width:24px;height:24px;border-radius:50%;background:var(--v3-red);color:#fff;font-size:.78rem;font-weight:800">3</span>Save &amp; share your shortlist</h3><p class="v3-muted" style="font-size:.85rem;margin:.4rem 0 0">Create an account to save, share and revisit your shortlist anytime.</p></div>
        <div class="v3-row tight"><button class="v3-btn v3-btn-secondary"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>Download PDF</button><button class="v3-btn v3-btn-primary"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v16l7-3z"/></svg>Save shortlist</button></div>
      </div>
    </div>
  </main>
</div>

<div class="v3-container">
  <div class="v3-card v3-card-emph v3-card-padded" style="margin-top:1.5rem;display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap">
    <div style="width:60px;height:60px;border-radius:50%;background:rgba(233,69,96,.18);border:1px solid rgba(233,69,96,.32);display:grid;place-items:center;color:#fff"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22"><path d="M2 4l3 12h14l3-12-6 7-4-7-4 7-6-7zm3 16h14"/></svg></div>
    <div style="flex:1;min-width:280px"><h3 style="margin:0 0 .25rem">Ready to decide with confidence?</h3><p class="v3-muted" style="margin:0">Compare your top picks side-by-side on pricing, features, and real reviews.</p></div>
    <a href="/pages/" class="v3-btn v3-btn-primary v3-btn-lg">Compare my shortlist &#8594;</a>
  </div>
</div>

{FOOTER}
{fab()}
</body></html>
"""


def _short_row(rank, logo, bg, name, desc, tags, score, score_label,
               price, price_period, best_for, badge=None, text_color="#fff"):
    badge_html = f'<span class="v3-badge red">{badge}</span>' if badge else ""
    score_color = "var(--v3-good)" if score >= 90 else ("var(--v3-good)" if score >= 80 else "#74a9ff")
    return f"""      <div class="v3-row" style="padding:1rem;border-radius:14px;align-items:center;margin-bottom:.55rem;background:rgba(255,255,255,.025);border:1px solid var(--v3-border);gap:1rem">
        <div style="display:flex;align-items:center;gap:.7rem;flex:1.4">
          <div style="display:grid;place-items:center;width:28px;height:28px;border-radius:50%;border:1px solid var(--v3-border);color:var(--v3-text-3);font-weight:800;font-size:.85rem">{rank}</div>
          <div class="v3-tool-logo" style="background:{bg};color:{text_color};font-size:1rem">{logo}</div>
          <div style="min-width:0">
            <h3 style="margin:0 0 .2rem;font-size:.95rem;display:flex;align-items:center;gap:.4rem">{name} {badge_html}</h3>
            <p style="font-size:.76rem;color:var(--v3-text-4);margin:0 0 .35rem;line-height:1.4">{desc}</p>
            <div class="v3-tool-tags">{''.join(f'<span class="v3-tag" style="font-size:.62rem">{t}</span>' for t in tags)}</div>
          </div>
        </div>
        <div style="width:100px;text-align:center">
          <div style="display:grid;place-items:center;width:60px;height:60px;border-radius:50%;border:3px solid {score_color};color:#fff;font-family:var(--v3-ff-display);font-size:1.05rem;font-weight:850;margin:0 auto .35rem">{score}</div>
          <div style="font-size:.7rem;color:{score_color};font-weight:700">{score_label}</div>
        </div>
        <div style="width:130px"><div style="font-family:var(--v3-ff-display);font-size:1.05rem;font-weight:850;color:#fff;line-height:1.1">{price}</div><div style="font-size:.7rem;color:var(--v3-text-5)">{price_period}</div></div>
        <div style="width:160px;font-size:.78rem;color:var(--v3-text-3);line-height:1.45">{best_for}</div>
        <div style="width:120px;display:flex;flex-direction:column;gap:.35rem"><a href="#" class="v3-btn v3-btn-primary v3-btn-sm">Compare</a><a href="#" class="v3-link-cta" style="font-size:.78rem;justify-content:flex-start">View details &#8594;</a></div>
      </div>"""


# ─────────────────────────────────────────────────────────────────────
# 06. LIBRARY / COMPARISONS HUB  — clones Image 9 + Image 12
# ─────────────────────────────────────────────────────────────────────
def page_library() -> str:
    head = head_html(
        "Browse 1,156 buyer pages — comparisons, pricing, alternatives",
        "Search pricing pages, comparison verdicts, trial paths and alternatives across every B2B SaaS tool.",
        f"{BASE}/pages/v3-preview-library",
    )
    return f"""{head}
{nav_html(active='comparisons')}

<section class="v3-hero" style="padding-bottom:1.2rem">
  <div class="v3-hero-inner" style="text-align:left;display:grid;grid-template-columns:1fr 320px;gap:2rem;align-items:flex-start">
    <div>
      <span class="v3-eyebrow">1,156 buyer pages indexed</span>
      <h1>Find the right<br><em>SaaS answer</em> faster.</h1>
      <p class="v3-lede" style="margin:.85rem 0 1.4rem;max-width:560px">Search pricing pages, comparison verdicts, trial paths and alternatives without opening ten vendor tabs.</p>
      <div class="v3-search" style="margin-left:0;margin-right:0;max-width:520px">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" style="color:rgba(255,255,255,.32)"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <input type="search" placeholder="Search any tool, brand, page type or feature…">
        <button>Search</button>
      </div>
      <div class="v3-popular" style="justify-content:flex-start">
        <span>Popular searches:</span>
        <a href="#">CRM pricing</a><a href="#">1Password pricing</a><a href="#">Notion free vs paid</a><a href="#">Best help desk</a>
      </div>
      <div class="v3-row" style="gap:1.2rem;margin-top:1.4rem">
        <div><b style="color:#fff;font-size:1.4rem;display:block">1,156</b><span style="font-size:.74rem;color:var(--v3-text-5)">Buyer pages indexed</span></div>
        <div><b style="color:#fff;font-size:1.4rem;display:block">808</b><span style="font-size:.74rem;color:var(--v3-text-5)">Comparisons</span></div>
        <div><b style="color:#fff;font-size:1.4rem;display:block">64</b><span style="font-size:.74rem;color:var(--v3-text-5)">Pricing guides</span></div>
        <div><b style="color:#fff;font-size:1.4rem;display:block">34</b><span style="font-size:.74rem;color:var(--v3-text-5)">Reviews</span></div>
        <div><b style="color:#fff;font-size:1.4rem;display:block">May 10, 2026</b><span style="font-size:.74rem;color:var(--v3-text-5)">Updated</span></div>
      </div>
    </div>
    <div class="v3-rail-card">
      <div class="v3-row between" style="margin-bottom:.6rem"><h3 style="margin:0">Your shortlist</h3><span class="v3-tag red">5</span></div>
      <div class="v3-rail-row"><div class="v3-tool-logo" style="background:#0070ad">1P</div><div style="flex:1"><b>1Password</b><small>Password Management</small></div></div>
      <div class="v3-rail-row"><div class="v3-tool-logo" style="background:#175ddc">B</div><div style="flex:1"><b>Bitwarden</b><small>Password Management</small></div></div>
      <div class="v3-rail-row"><div class="v3-tool-logo" style="background:#0e7490">D</div><div style="flex:1"><b>Dashlane</b><small>Password Management</small></div></div>
      <div class="v3-rail-row"><div class="v3-tool-logo" style="background:#fbbf24;color:#000">K</div><div style="flex:1"><b>Keeper</b><small>Password Management</small></div></div>
      <div class="v3-rail-row"><div class="v3-tool-logo" style="background:#4d4dff">N</div><div style="flex:1"><b>NordPass</b><small>Password Management</small></div></div>
      <a href="/shortlist" class="v3-btn v3-btn-primary v3-btn-sm" style="width:100%;margin-top:.85rem">View shortlist &#8594;</a>
    </div>
  </div>
</section>

<div class="v3-layout-3col">
  <aside class="v3-filters">
    <div class="v3-filter-group">
      <h4>Refine your search</h4>
      <div class="v3-row tight" style="gap:.4rem"><select class="v3-select"><option>Buyer intent: Any</option></select></div>
      <div style="height:.55rem"></div>
      <select class="v3-select"><option>Page type: Any</option></select>
      <div style="height:.55rem"></div>
      <select class="v3-select"><option>Pricing model: Any</option></select>
    </div>

    <div class="v3-filter-group">
      <h4>Filter by buyer intent</h4>
      <label class="v3-filter-row"><span>I'm researching</span><b>—</b></label>
      <label class="v3-filter-row" style="background:rgba(233,69,96,.08);border-radius:8px;padding:.4rem .6rem;margin:.2rem -.6rem"><span style="color:#fff;font-weight:700">I'm comparing</span><b style="color:var(--v3-red-light)">●</b></label>
      <label class="v3-filter-row"><span>I'm buying</span><b>—</b></label>
      <label class="v3-filter-row"><span>I'm renewing</span><b>—</b></label>
    </div>

    <div class="v3-filter-group">
      <h4>Recent research</h4>
      <div class="v3-rail-row"><div class="v3-tool-logo" style="background:#0070ad;width:28px;height:28px;border-radius:6px;font-size:.75rem">1P</div><div style="flex:1"><b style="font-size:.78rem">1Password Pricing 2026</b><small>Viewed just now</small></div></div>
      <div class="v3-rail-row"><div class="v3-tool-logo" style="background:#ff7a59;width:28px;height:28px;border-radius:6px;font-size:.75rem">H</div><div style="flex:1"><b style="font-size:.78rem">HubSpot vs Pipedrive</b><small>Viewed 2h ago</small></div></div>
      <div class="v3-rail-row"><div class="v3-tool-logo" style="background:#0d65b8;width:28px;height:28px;border-radius:6px;font-size:.75rem">A</div><div style="flex:1"><b style="font-size:.78rem">Ahrefs Discount 2026</b><small>Viewed yesterday</small></div></div>
      <p style="margin:.85rem 0 0"><a href="#" class="v3-link-cta" style="font-size:.78rem">View all history &#8594;</a></p>
    </div>

    <div class="v3-filter-group">
      <h4>How we do this</h4>
      <div style="font-size:.78rem;color:var(--v3-text-3);line-height:1.55">
        <p style="margin:.25rem 0">✓ We scan official pricing and product pages daily.</p>
        <p style="margin:.25rem 0">✓ We test free trials and validate deals ourselves.</p>
        <p style="margin:.25rem 0">✓ We stay independent — no vendor influence.</p>
      </div>
      <p style="margin:.85rem 0 0"><a href="/methodology" class="v3-link-cta" style="font-size:.78rem">See our methodology &#8594;</a></p>
    </div>
  </aside>

  <main>
    <div class="v3-tabs" style="margin-bottom:1.2rem">
      <a href="#" class="active">All content <span style="opacity:.65">1,156</span></a>
      <a href="#">Pricing Guides <span style="opacity:.65">64</span></a>
      <a href="#">Comparisons <span style="opacity:.65">808</span></a>
      <a href="#">Alternatives <span style="opacity:.65">71</span></a>
      <a href="#">Reviews <span style="opacity:.65">34</span></a>
      <a href="#">Free Trials <span style="opacity:.65">50</span></a>
      <a href="#">Deals <span style="opacity:.65">49</span></a>
    </div>
    <div class="v3-row between" style="margin-bottom:1rem"><span class="v3-muted" style="font-size:.85rem"><b style="color:#fff">1,156</b> results</span><div><span class="v3-muted" style="font-size:.85rem;margin-right:.5rem">Sort by</span><select class="v3-select" style="display:inline-block;width:auto"><option>Recommended</option></select></div></div>

    <div class="v3-grid-3">
      {_lib_card("PRICING GUIDE","1Password Pricing 2026: Plans, Costs & What You Actually Pay","Real-world pricing for individuals and teams. Hidden fees, taxes and add-ons explained.","Apr 20, 2026","Verified")}
      {_lib_card("COMPARISON","1Password vs Bitwarden 2026: Which Password Manager Wins?","Security, UX, pricing and features compared. See side-by-side verdicts and our top pick.","Apr 18, 2026","Updated")}
      {_lib_card("ALTERNATIVES","10 Best 1Password Alternatives for Teams in 2026","From Bitwarden to Dashlane — ranked alternatives for security, budget and ease of use.","May 2, 2026","Verified")}
      {_lib_card("REVIEW","Notion Review 2026: Features, Pros, Cons & Real Pricing","Hands-on review of Notion for teams. What we love, what's missing, and who it's for.","May 5, 2026","Unbiased")}
      {_lib_card("FREE TRIAL","HubSpot CRM Free Trial 2026: How It Works & What's Included","Trial length, limits, and setup steps. Get started without surprises.","May 6, 2026","Verified")}
      {_lib_card("DEAL","Ahrefs 2026 Discount: Save Up to 20% on Annual Plans","Active promo codes, coupon stacking tips, and best time to buy.","May 9, 2026","Deal verified")}
      {_lib_card("COMPARISON","HubSpot vs Pipedrive 2026: CRM Showdown for SMBs","Pricing, pipelines, automation and reporting compared with real use cases.","Apr 28, 2026","Updated")}
      {_lib_card("PRICING GUIDE","Salesforce Pricing 2026: Editions, Add-Ons & Total Cost","Breakdown of editions, key add-ons and total cost of ownership.","Apr 21, 2026","Verified")}
      {_lib_card("ALTERNATIVES","Best Notion Alternatives in 2026 (Free & Paid Options)","Top picks for docs, projects and knowledge base — ranked by use case.","May 1, 2026","Verified")}
    </div>
    <div style="text-align:center;margin:1.6rem 0"><button class="v3-btn v3-btn-secondary">Load more results ↻</button></div>
  </main>

  <aside>
    <div class="v3-rail-card v3-card-emph">
      <h3 style="display:flex;align-items:center;gap:.5rem;color:var(--v3-red-light)"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><polyline points="7 14 11 10 15 12 21 6"/></svg>True Cost Detector</h3>
      <p style="font-size:.8rem;color:var(--v3-text-3);margin:0 0 .85rem">See the real cost behind any SaaS — hidden fees, overages, and add-on breakdown.</p>
      <a href="#" class="v3-btn v3-btn-primary v3-btn-sm" style="width:100%">Reveal true costs &#8594;</a>
    </div>
    <div class="v3-rail-card">
      <h3 style="display:flex;align-items:center;gap:.5rem"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="var(--v3-red)" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/></svg>Shortlist Builder</h3>
      <p style="font-size:.8rem;color:var(--v3-text-3);margin:0 0 .85rem">Save, compare, and share your top picks with your team in one click.</p>
      <a href="/shortlist" class="v3-btn v3-btn-primary v3-btn-sm" style="width:100%">Start your shortlist &#8594;</a>
    </div>
  </aside>
</div>

<div class="v3-container" style="margin-top:2.5rem">
  <div class="v3-grid-4">
    <div style="display:flex;align-items:flex-start;gap:.7rem;font-size:.82rem;color:var(--v3-text-3)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2" width="18" height="18" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg><div><b style="color:#fff">Independent &amp; commission-free</b><br>We never accept payments to influence verdicts.</div></div>
    <div style="display:flex;align-items:flex-start;gap:.7rem;font-size:.82rem;color:var(--v3-text-3)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2" width="18" height="18" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg><div><b style="color:#fff">Hands-on verification</b><br>We test free trials, validate pricing, and confirm deals.</div></div>
    <div style="display:flex;align-items:flex-start;gap:.7rem;font-size:.82rem;color:var(--v3-text-3)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2" width="18" height="18" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg><div><b style="color:#fff">Always up to date</b><br>Pages are rescanned monthly to stay fresh.</div></div>
    <div></div>
  </div>
  <p class="v3-help" style="text-align:center;margin-top:1rem">SaaSpare is an independent comparison site. We may earn a commission when you buy through links on our site at no extra cost to you.</p>
</div>

{FOOTER}
{fab()}
</body></html>
"""


def _lib_card(chip, title, desc, date, status):
    chip_color = {"PRICING GUIDE":"red","COMPARISON":"red","ALTERNATIVES":"red","REVIEW":"green","FREE TRIAL":"green","DEAL":"red"}.get(chip, "red")
    return f"""      <a class="v3-card" href="#" style="display:block;text-decoration:none">
        <div class="v3-row between" style="margin-bottom:.85rem"><span class="v3-type-chip">📄 {chip}</span><span style="color:var(--v3-text-5)">☆</span></div>
        <h3 style="margin:0 0 .55rem;font-size:1rem;line-height:1.35;color:#fff">{title}</h3>
        <p style="font-size:.82rem;color:var(--v3-text-4);margin:0 0 .85rem;line-height:1.5">{desc}</p>
        <div class="v3-row between" style="font-size:.74rem;color:var(--v3-text-5);padding-top:.7rem;border-top:1px solid var(--v3-border)"><span>{date}</span><span style="color:var(--v3-good)">✓ {status}</span></div>
      </a>"""


# Continued in part2b... (kept short to fit in tool call limits)
PAGES = {
    "deal-radar": page_deal_radar,
    "shortlist": page_shortlist,
    "library": page_library,
}


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    for slug, builder in PAGES.items():
        path = OUT_DIR / f"v3-preview-{slug}.html"
        path.write_text(builder(), encoding="utf-8")
        size = path.stat().st_size
        print(f"  wrote {path.relative_to(ROOT)}  ({size:,} bytes)")
        written += 1
    print(f"\n{written} preview pages written.")
