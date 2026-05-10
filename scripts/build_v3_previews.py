"""Builds 12 v3-design preview pages at site/pages/v3-preview-*.html.

These pages are noindex'd and exist purely so the user can review the
v3 design system on Cloudflare before mass rollout.

Run:    uv run python scripts/build_v3_previews.py
Output: site/pages/v3-preview-{homepage,comparison,roi,deal-radar,shortlist,
        library,about,privacy,affiliate-disclosure,contact,404,newsletter}.html

After approval -> redesign_v3.py sweeps existing pages + the page generators
in outputs/seo_page.py and outputs/programmatic.py are updated to emit v3.
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
# 01. HOMEPAGE  — clones Image 10
# ─────────────────────────────────────────────────────────────────────
def page_homepage() -> str:
    head = head_html(
        "SaaSpare — Confident SaaS buying decisions, backed by real costs",
        "Independent SaaS comparisons with real pricing, hidden fees and feature breakdowns. Compare 808+ tools.",
        f"{BASE}/pages/v3-preview-homepage",
    )
    return f"""{head}
{nav_html(active='')}

<section class="v3-hero left">
  <div class="v3-container" style="display:grid;grid-template-columns:1fr 1fr;gap:3rem;align-items:center;padding-top:3rem;padding-bottom:1rem">
    <div>
      <div class="v3-trust-avatars" style="margin-bottom:1.5rem">
        <span class="v3-avatars">
          <span style="background:#9b6dff"></span><span style="background:#34d399"></span><span style="background:#ffc864"></span><span style="background:#74a9ff"></span><span style="background:#e94560"></span>
        </span>
        <span>Trusted by <b>12,500+</b> buyers and growing</span>
      </div>
      <h1>Confident SaaS<br>buying decisions.<br><em>Backed by real costs.</em></h1>
      <p class="v3-lede" style="margin:1rem 0 1.5rem">SaaSpare compares real-world pricing, hidden fees and features so teams can choose the right SaaS with clarity and confidence.</p>
      <div class="v3-search">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" style="color:rgba(255,255,255,.32)"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <input type="search" placeholder="Search tools, categories or use cases…">
        <button>Compare &#8594;</button>
      </div>
      <div class="v3-trust-row">
        <span class="v3-trust-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Independent &amp; unbiased</span>
        <span class="v3-trust-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Real pricing, not guesses</span>
        <span class="v3-trust-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Updated weekly</span>
        <span class="v3-trust-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Free to use</span>
      </div>
    </div>
    <div class="v3-card v3-card-padded" style="position:relative">
      <div style="text-align:center;margin-bottom:1rem"><span class="v3-eyebrow" style="margin:0">Best for your team</span></div>
      <table class="v3-table" style="margin:0;border:0">
        <thead>
          <tr><th></th><th>1Password</th><th>Bitwarden</th><th>Dashlane</th></tr>
        </thead>
        <tbody>
          <tr><td><b>Starting price</b></td><td><span class="v3-tag red">Best price</span><br>$2.99/user/mo</td><td>$4.00/user/mo</td><td>$4.99/user/mo</td></tr>
          <tr><td><b>Hidden fees</b></td><td>Low</td><td>Low</td><td><span style="color:var(--v3-warn)">Medium</span></td></tr>
          <tr><td><b>Ease of setup</b></td><td>Easy</td><td>Easy</td><td>Medium</td></tr>
          <tr><td><b>Security</b></td><td>★★★★★</td><td>★★★★½</td><td>★★★★½</td></tr>
          <tr><td><b>Best for</b></td><td>Teams &amp; SMBs</td><td>Budget-first teams</td><td>Business users</td></tr>
        </tbody>
      </table>
      <a href="/pages/1password-vs-bitwarden-which-is-better-in-2026" class="v3-btn v3-btn-primary v3-btn-lg" style="width:100%;justify-content:center;margin-top:1.2rem">Compare all 3 &#8594;</a>
    </div>
  </div>
</section>

<section class="v3-section">
  <div class="v3-container">
    <div class="v3-section-head">
      <h2>Top categories</h2>
      <a href="/pages/" class="v3-link-cta">Browse all categories &#8594;</a>
    </div>
    <div class="v3-grid-4" style="grid-template-columns:repeat(7,minmax(0,1fr))">
      <a class="v3-card" href="/pages/best-password-managers-software-for-business-in-2026-ranked">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></div>
        <h4 style="font-size:.92rem;margin:.7rem 0 .15rem">Password Mgmt</h4>
        <p style="font-size:.74rem;color:var(--v3-text-5);margin:0">16 comparisons</p>
      </a>
      <a class="v3-card" href="/pages/best-crm-software-for-b2b-saas-in-2026-ranked">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></div>
        <h4 style="font-size:.92rem;margin:.7rem 0 .15rem">CRM</h4>
        <p style="font-size:.74rem;color:var(--v3-text-5);margin:0">22 comparisons</p>
      </a>
      <a class="v3-card" href="/pages/">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></div>
        <h4 style="font-size:.92rem;margin:.7rem 0 .15rem">Help Desk</h4>
        <p style="font-size:.74rem;color:var(--v3-text-5);margin:0">16 comparisons</p>
      </a>
      <a class="v3-card" href="/pages/best-project-management-software-for-startups-in-2026-ranked">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg></div>
        <h4 style="font-size:.92rem;margin:.7rem 0 .15rem">Project Mgmt</h4>
        <p style="font-size:.74rem;color:var(--v3-text-5);margin:0">20 comparisons</p>
      </a>
      <a class="v3-card" href="/pages/best-marketing-automation-software-for-small-business-in-2026-ranked">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg></div>
        <h4 style="font-size:.92rem;margin:.7rem 0 .15rem">Email Marketing</h4>
        <p style="font-size:.74rem;color:var(--v3-text-5);margin:0">14 comparisons</p>
      </a>
      <a class="v3-card" href="/pages/best-finance-ops-software-for-b2b-saas-in-2026-ranked">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div>
        <h4 style="font-size:.92rem;margin:.7rem 0 .15rem">Accounting</h4>
        <p style="font-size:.74rem;color:var(--v3-text-5);margin:0">13 comparisons</p>
      </a>
      <a class="v3-card" href="/pages/">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></div>
        <h4 style="font-size:.92rem;margin:.7rem 0 .15rem">View all</h4>
        <p style="font-size:.74rem;color:var(--v3-text-5);margin:0">72+ categories</p>
      </a>
    </div>
  </div>
</section>

<section class="v3-section">
  <div class="v3-container">
    <div class="v3-section-head">
      <h2>Featured comparisons</h2>
      <a href="/pages/" class="v3-link-cta">View all comparisons &#8594;</a>
    </div>
    <div class="v3-grid-4">
      <a class="v3-card" href="/pages/1password-vs-bitwarden-which-is-better-in-2026">
        <div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.85rem"><div class="v3-tool-logo" style="width:36px;height:36px;background:#0070ad;font-size:.85rem">1P</div><span style="color:var(--v3-text-4);font-size:.78rem;font-weight:700">vs</span><div class="v3-tool-logo" style="width:36px;height:36px;background:#175ddc;font-size:.85rem">BW</div></div>
        <h4 style="margin:0 0 .35rem">1Password vs Bitwarden</h4>
        <p style="font-size:.78rem;color:var(--v3-text-4);margin:0 0 .8rem;line-height:1.5">Security, features, and real-world pricing compared in detail.</p>
        <span class="v3-link-cta" style="font-size:.78rem">View comparison &#8594;</span>
      </a>
      <a class="v3-card" href="/pages/hubspot-vs-pipedrive-which-is-better-in-2026">
        <div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.85rem"><div class="v3-tool-logo" style="width:36px;height:36px;background:#ff7a59;font-size:.85rem">H</div><span style="color:var(--v3-text-4);font-size:.78rem;font-weight:700">vs</span><div class="v3-tool-logo" style="width:36px;height:36px;background:#1a1a1a;font-size:.85rem">P</div></div>
        <h4 style="margin:0 0 .35rem">HubSpot vs Pipedrive</h4>
        <p style="font-size:.78rem;color:var(--v3-text-4);margin:0 0 .8rem;line-height:1.5">Which CRM delivers the best value for growing teams?</p>
        <span class="v3-link-cta" style="font-size:.78rem">View comparison &#8594;</span>
      </a>
      <a class="v3-card" href="/pages/notion-vs-clickup-which-is-better-in-2026">
        <div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.85rem"><div class="v3-tool-logo" style="width:36px;height:36px;background:#fff;color:#000;font-size:.85rem">N</div><span style="color:var(--v3-text-4);font-size:.78rem;font-weight:700">vs</span><div class="v3-tool-logo" style="width:36px;height:36px;background:#7b68ee;font-size:.85rem">C</div></div>
        <h4 style="margin:0 0 .35rem">Notion vs ClickUp</h4>
        <p style="font-size:.78rem;color:var(--v3-text-4);margin:0 0 .8rem;line-height:1.5">Project docs, tasks, and teamwork — side by side.</p>
        <span class="v3-link-cta" style="font-size:.78rem">View comparison &#8594;</span>
      </a>
      <a class="v3-card" href="/pages/">
        <div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.85rem"><div class="v3-tool-logo" style="width:36px;height:36px;background:#4a154b;font-size:.85rem">S</div><span style="color:var(--v3-text-4);font-size:.78rem;font-weight:700">vs</span><div class="v3-tool-logo" style="width:36px;height:36px;background:#5b5fc7;font-size:.85rem">T</div></div>
        <h4 style="margin:0 0 .35rem">Slack vs Microsoft Teams</h4>
        <p style="font-size:.78rem;color:var(--v3-text-4);margin:0 0 .8rem;line-height:1.5">Messaging, collaboration, and total cost of ownership.</p>
        <span class="v3-link-cta" style="font-size:.78rem">View comparison &#8594;</span>
      </a>
    </div>
  </div>
</section>

<section class="v3-section">
  <div class="v3-container">
    <h2>Buyer tools</h2>
    <p class="v3-muted" style="margin:0 0 1.4rem">Everything you need to research, compare, and decide.</p>
    <div class="v3-grid-4">
      <a class="v3-card" href="/shortlist">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg></div>
        <h4 style="margin:.85rem 0 .25rem">Shortlist Builder</h4>
        <p style="font-size:.82rem;color:var(--v3-text-4);margin:0;line-height:1.5">Rank tools by fit, team size, budget and must-have features.</p>
      </a>
      <a class="v3-card" href="/deal-radar">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg></div>
        <h4 style="margin:.85rem 0 .25rem">Deal Radar</h4>
        <p style="font-size:.82rem;color:var(--v3-text-4);margin:0;line-height:1.5">Track pricing changes, promotions and the best time to buy.</p>
      </a>
      <a class="v3-card" href="/pages/saas-roi-calculator">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="8" y1="10" x2="10" y2="10"/><line x1="13" y1="10" x2="14" y2="10"/></svg></div>
        <h4 style="margin:.85rem 0 .25rem">ROI Calculator</h4>
        <p style="font-size:.82rem;color:var(--v3-text-4);margin:0;line-height:1.5">See the real return before you commit.</p>
      </a>
      <a class="v3-card" href="#">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12h6"/><path d="M12 9v6"/><circle cx="12" cy="12" r="10"/></svg></div>
        <h4 style="margin:.85rem 0 .25rem">Decision Trail</h4>
        <p style="font-size:.82rem;color:var(--v3-text-4);margin:0;line-height:1.5">Collaborate, take notes and build a clear decision record.</p>
      </a>
    </div>
  </div>
</section>

<section class="v3-section">
  <div class="v3-container">
    <div class="v3-card v3-card-emph v3-card-padded" style="display:grid;grid-template-columns:1fr 2fr;gap:2rem;align-items:center">
      <div>
        <span class="v3-eyebrow" style="margin-bottom:.7rem">How we stay trusted</span>
        <h2 style="margin:0 0 .65rem">Real research. Real costs.<br>Zero vendor influence.</h2>
        <p class="v3-muted" style="margin:0 0 .85rem">We research, test and validate pricing from public sources, buyer inputs and our own hands-on evaluations.</p>
        <a href="/methodology" class="v3-link-cta">Our methodology &#8594;</a>
      </div>
      <div class="v3-grid-4">
        <div class="v3-stat"><div class="num red">808+</div><div class="lbl">In-depth comparisons</div></div>
        <div class="v3-stat"><div class="num">64</div><div class="lbl">Pricing guides</div></div>
        <div class="v3-stat"><div class="num">34</div><div class="lbl">Buyer reviews</div></div>
        <div class="v3-stat"><div class="num">May 10, 2026</div><div class="lbl">Last updated</div></div>
      </div>
    </div>
  </div>
</section>

<section class="v3-section">
  <div class="v3-container">
    <div class="v3-card v3-card-padded" style="display:grid;grid-template-columns:1fr 1.5fr;gap:2rem;align-items:center">
      <div style="text-align:center">
        <svg viewBox="0 0 100 100" style="width:80px;height:80px;color:var(--v3-red)" fill="none" stroke="currentColor" stroke-width="3"><rect x="10" y="20" width="80" height="60" rx="6"/><path d="m10 26 40 30 40-30"/></svg>
      </div>
      <div>
        <h3 style="margin:0 0 .3rem;font-size:1.4rem">Stay ahead of SaaS pricing.</h3>
        <p class="v3-muted" style="margin:0 0 1rem">Get new comparisons, pricing updates and buying tips delivered to your inbox.</p>
        <form style="display:flex;gap:.5rem;flex-wrap:wrap">
          <input type="email" placeholder="Enter your email" class="v3-input" style="flex:1;min-width:220px">
          <button type="submit" class="v3-btn v3-btn-primary">Subscribe &#8594;</button>
        </form>
        <p class="v3-help" style="margin-top:.5rem">No spam. Unsubscribe anytime.</p>
      </div>
    </div>
  </div>
</section>

{FOOTER}
{fab()}
</body></html>
"""


# ─────────────────────────────────────────────────────────────────────
# 02. COMPARISON / PRICING — clones Image 11
# ─────────────────────────────────────────────────────────────────────
def page_comparison() -> str:
    head = head_html(
        "1Password Pricing 2026: Plans, Costs &amp; What You Actually Pay",
        "Real-world 1Password pricing in May 2026 with hidden fees, plan breakdown, and buyer-friendly alternatives.",
        f"{BASE}/pages/v3-preview-comparison",
    )
    return f"""{head}
{nav_html(active='comparisons')}

<div class="v3-container" style="padding-top:5.5rem">
  <div class="v3-crumbs">
    <a href="/">Home</a><span>/</span>
    <a href="/pages/">Comparisons</a><span>/</span>
    <a href="/pages/best-password-managers-software-for-business-in-2026-ranked">Password Management</a><span>/</span>
    <span>1Password Pricing 2026</span>
  </div>
</div>

<div class="v3-layout-main" style="margin-top:.5rem">
  <main>
    <h1>1Password Pricing 2026: Plans, Costs &amp;<br>What You Actually Pay</h1>
    <p class="v3-lede" style="margin:.85rem 0 1.5rem;max-width:760px">We break down 1Password's real-world pricing in May 2026, compare it with Bitwarden, and surface the hidden costs buyers often miss.</p>

    <div class="v3-row tight" style="margin-bottom:1.5rem">
      <span class="v3-trust-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg><b style="color:#fff">Last verified</b>&nbsp;May 20, 2026</span>
      <span class="v3-trust-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg><b style="color:#fff">Unbiased research</b>&nbsp;Independent &amp; objective</span>
      <span class="v3-trust-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg><b style="color:#fff">Affiliate disclosure</b>&nbsp;We may earn a commission</span>
      <span class="v3-trust-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v16l7-3z"/></svg><b style="color:#fff">Free to read</b>&nbsp;No signup required</span>
    </div>

    <div class="v3-callout v3-callout-quick">
      <div class="v3-callout-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></div>
      <div class="v3-callout-body">
        <h4>Quick answer</h4>
        <p>1Password in May 2026 starts at <strong>$2.99/user/month</strong> (Starter) and <strong>$7.99/user/month</strong> (Pro). It's the best pick for teams that want premium security and ease of use — if budget isn't the top priority.</p>
      </div>
    </div>

    <div class="v3-callout v3-callout-tldr">
      <div class="v3-callout-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg></div>
      <div class="v3-callout-body">
        <h4>TL;DR — The real cost takeaway</h4>
        <p style="font-size:1.1rem;color:#fff;font-weight:800">Expect to pay $2.99–$7.99 per user/month for 1Password.</p>
        <p>Add taxes and potential seat overages. Free trial: 14 days. No credit card required.</p>
      </div>
    </div>

    <h2 id="pricing-glance" style="margin-top:2.5rem">1Password pricing at a glance</h2>
    <div class="v3-plan-grid">
      <div class="v3-plan">
        <span class="v3-plan-flag">Best for individuals</span>
        <h3>Starter</h3>
        <div class="v3-plan-price">$2.99</div>
        <div class="v3-plan-period">user/month</div>
        <p class="v3-plan-desc">Personal &amp; basic sharing</p>
      </div>
      <div class="v3-plan popular">
        <span class="v3-plan-flag">Most popular</span>
        <h3>Pro</h3>
        <div class="v3-plan-price">$7.99</div>
        <div class="v3-plan-period">user/month</div>
        <p class="v3-plan-desc">Full features for individuals &amp; small teams</p>
      </div>
      <div class="v3-plan">
        <h3>Enterprise</h3>
        <div class="v3-plan-price">Custom</div>
        <div class="v3-plan-period">Contact sales</div>
        <p class="v3-plan-desc">Advanced controls &amp; SSO for organisations</p>
      </div>
      <div class="v3-plan">
        <h3>Free Trial</h3>
        <div class="v3-plan-price">14 days</div>
        <div class="v3-plan-period">No credit card</div>
        <p class="v3-plan-desc">Try any plan free</p>
      </div>
    </div>
    <div style="text-align:center;margin:1.6rem 0 0">
      <a href="/go/1password" rel="nofollow sponsored" class="v3-btn v3-btn-primary v3-btn-lg">Start 14-day free trial &#8594;</a>
      <p class="v3-help" style="margin:.6rem 0 0">No credit card required. Cancel anytime.</p>
    </div>

    <h2 id="vs-bitwarden" style="margin-top:2.5rem">1Password vs Bitwarden — Pricing comparison</h2>
    <div class="v3-table-wrap">
      <table class="v3-table">
        <thead><tr><th>Feature</th><th>1Password <span class="v3-badge red">Best pick</span></th><th>Bitwarden</th></tr></thead>
        <tbody>
          <tr><td>Starter Plan</td><td class="col-best">$2.99/user/month</td><td>$4.00/user/month</td></tr>
          <tr><td>Pro Plan</td><td class="col-best">$7.99/user/month</td><td>$6.00/user/month</td></tr>
          <tr><td>Enterprise Plan</td><td>Custom</td><td>Custom</td></tr>
          <tr><td>Free Plan</td><td>14 days trial</td><td>7 days trial</td></tr>
          <tr><td>Family / Team sharing</td><td>Yes (Starter &amp; Pro)</td><td>Yes (Premium)</td></tr>
          <tr><td>SSO &amp; Advanced Security</td><td>Yes (Pro &amp; Enterprise)</td><td>Yes (Premium &amp; Enterprise)</td></tr>
          <tr><td>Data Storage Region</td><td>Global (US/EU)</td><td>US</td></tr>
          <tr><td>Support</td><td>Email support (Starter+)<br>Priority (Pro+)</td><td>Community (Free)<br>Email (Premium+)</td></tr>
        </tbody>
      </table>
    </div>
    <p class="v3-help">Pricing verified May 20, 2026. Taxes may apply. Source: <a href="https://1password.com/pricing">1Password.com</a>, <a href="https://bitwarden.com/pricing">Bitwarden.com</a>.</p>

    <h2 id="hidden-fees" style="margin-top:2.5rem">Hidden fees &amp; what buyers actually pay</h2>
    <div class="v3-grid-4">
      <div class="v3-card">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg></div>
        <h4 style="margin:.65rem 0 .35rem;font-size:.92rem">Seat-based pricing</h4>
        <p style="font-size:.82rem;color:var(--v3-text-4);margin:0;line-height:1.5">You pay per active user each month. Remove users to avoid unused seat charges.</p>
      </div>
      <div class="v3-card">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg></div>
        <h4 style="margin:.65rem 0 .35rem;font-size:.92rem">Enterprise add-ons</h4>
        <p style="font-size:.82rem;color:var(--v3-text-4);margin:0;line-height:1.5">Advanced SSO, SCIM, and custom integrations may require add-ons.</p>
      </div>
      <div class="v3-card">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div>
        <h4 style="margin:.65rem 0 .35rem;font-size:.92rem">Taxes &amp; regional pricing</h4>
        <p style="font-size:.82rem;color:var(--v3-text-4);margin:0;line-height:1.5">Prices exclude VAT/GST in some regions. Final cost varies by location.</p>
      </div>
      <div class="v3-card">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
        <h4 style="margin:.65rem 0 .35rem;font-size:.92rem">Free trial limits</h4>
        <p style="font-size:.82rem;color:var(--v3-text-4);margin:0;line-height:1.5">14-day trial includes full features. No credit card required.</p>
      </div>
    </div>

    <div class="v3-verdict-box" style="margin-top:2rem">
      <div class="crown"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 4l3 12h14l3-12-6 7-4-7-4 7-6-7zm3 16h14"/></svg></div>
      <div>
        <h4>Our top pick</h4>
        <p class="verdict-line">1Password delivers the best balance of security, usability and features for most teams and businesses.</p>
        <p class="verdict-sub">14 days free. Cancel anytime.</p>
      </div>
      <a href="/go/1password" rel="nofollow sponsored" class="v3-btn v3-btn-primary v3-btn-lg">Start your free trial &#8594;</a>
    </div>

    <h2 style="margin-top:2.5rem">1Password review — Is it worth it?</h2>
    <div class="v3-grid-3">
      <div>
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
        <h4 style="margin:.7rem 0 .35rem">Security you can trust</h4>
        <p style="font-size:.85rem;color:var(--v3-text-4);margin:0;line-height:1.55">Industry-leading encryption, zero-knowledge architecture, and regular audits keep your data safe.</p>
      </div>
      <div>
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></div>
        <h4 style="margin:.7rem 0 .35rem">Built for productivity</h4>
        <p style="font-size:.85rem;color:var(--v3-text-4);margin:0;line-height:1.55">Clean UI, powerful sharing, and deep integrations across browsers and devices.</p>
      </div>
      <div>
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg></div>
        <h4 style="margin:.7rem 0 .35rem">Great for teams</h4>
        <p style="font-size:.85rem;color:var(--v3-text-4);margin:0;line-height:1.55">Granular permissions, SSO, and activity logs make it easy to manage access at scale.</p>
      </div>
    </div>
    <p style="margin:1rem 0 0"><a href="/pages/1password-review-2026-is-it-worth-it-honest-verdict" class="v3-link-cta">Read our full 1Password review &#8594;</a></p>

    <div class="v3-grid-2" style="margin-top:2.5rem">
      <div>
        <h2 style="margin:0 0 1rem;font-size:1.2rem">Related comparisons</h2>
        <div style="display:flex;flex-direction:column;gap:.55rem">
          <a class="v3-tool-card" href="/pages/1password-vs-bitwarden-which-is-better-in-2026">
            <div class="v3-tool-logo" style="background:#0070ad">1P</div>
            <div class="v3-tool-body"><h3 style="font-size:.86rem">1Password vs Bitwarden</h3><p>Which password manager is better in 2026?</p></div>
            <div class="v3-tool-actions"></div>
          </a>
          <a class="v3-tool-card" href="/pages/1password-vs-dashlane-which-is-better-in-2026">
            <div class="v3-tool-logo" style="background:#0070ad">1P</div>
            <div class="v3-tool-body"><h3 style="font-size:.86rem">1Password vs Dashlane</h3><p>Features, pricing and real-world fit comparison</p></div>
            <div class="v3-tool-actions"></div>
          </a>
          <a class="v3-tool-card" href="/pages/1password-vs-keeper-which-is-better-in-2026">
            <div class="v3-tool-logo" style="background:#0070ad">1P</div>
            <div class="v3-tool-body"><h3 style="font-size:.86rem">1Password vs Keeper</h3><p>Security, pricing and team features compared</p></div>
            <div class="v3-tool-actions"></div>
          </a>
        </div>
      </div>
      <div>
        <h2 style="margin:0 0 1rem;font-size:1.2rem">FAQs</h2>
        <details class="v3-card v3-card-flat" style="margin-bottom:.6rem"><summary style="cursor:pointer;font-weight:700;font-size:.9rem;color:#fff">Is there a 1Password free plan?</summary><p style="margin:.6rem 0 0;font-size:.86rem;color:var(--v3-text-3)">No, but a 14-day free trial is available with no credit card required.</p></details>
        <details class="v3-card v3-card-flat" style="margin-bottom:.6rem"><summary style="cursor:pointer;font-weight:700;font-size:.9rem;color:#fff">Can I try 1Password before I buy?</summary><p style="margin:.6rem 0 0;font-size:.86rem;color:var(--v3-text-3)">Yes — 14-day full-feature trial. Cancel anytime.</p></details>
        <details class="v3-card v3-card-flat" style="margin-bottom:.6rem"><summary style="cursor:pointer;font-weight:700;font-size:.9rem;color:#fff">What payment methods are accepted?</summary><p style="margin:.6rem 0 0;font-size:.86rem;color:var(--v3-text-3)">Major credit cards, PayPal, and invoicing on Enterprise plans.</p></details>
        <p style="margin-top:.85rem"><a href="#" class="v3-link-cta">View all FAQs &#8594;</a></p>
      </div>
    </div>

    <p class="v3-help" style="text-align:center;margin-top:3rem">SaaSpare is an independent comparison site. We may earn a commission when you buy through links on our site at no extra cost to you. We only recommend tools we believe provide real value.</p>
  </main>

  <aside>
    <div class="v3-rail-card">
      <h3 style="display:flex;align-items:center;gap:.45rem;color:var(--v3-red-light)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M3 3v18h18"/><polyline points="7 14 11 10 15 12 21 6"/></svg>True Cost Detector</h3>
      <p style="font-size:.78rem;color:var(--v3-text-3);margin:0 0 .85rem;font-weight:700">Hidden fees to know:</p>
      <ul style="list-style:none;padding:0;margin:0">
        <li style="font-size:.82rem;color:var(--v3-text-2);padding:.3rem 0;display:flex;gap:.5rem;align-items:center"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="14" height="14"><polyline points="20 6 9 17 4 12"/></svg>Extra seats billed monthly</li>
        <li style="font-size:.82rem;color:var(--v3-text-2);padding:.3rem 0;display:flex;gap:.5rem;align-items:center"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="14" height="14"><polyline points="20 6 9 17 4 12"/></svg>Enterprise add-ons (e.g. SCIM, advanced SSO)</li>
        <li style="font-size:.82rem;color:var(--v3-text-2);padding:.3rem 0;display:flex;gap:.5rem;align-items:center"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="14" height="14"><polyline points="20 6 9 17 4 12"/></svg>Taxes vary by region</li>
        <li style="font-size:.82rem;color:var(--v3-text-2);padding:.3rem 0;display:flex;gap:.5rem;align-items:center"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="14" height="14"><polyline points="20 6 9 17 4 12"/></svg>No setup fees</li>
      </ul>
      <div style="margin-top:.85rem;padding-top:.75rem;border-top:1px solid var(--v3-border);font-size:.78rem;color:var(--v3-text-3)">
        <span style="color:var(--v3-good)">●</span> <b style="color:#fff">Overall: Low risk</b><br><span style="color:var(--v3-text-5)">Transparent pricing</span>
      </div>
    </div>

    <div class="v3-rail-card">
      <h3>Best alternatives</h3>
      <a href="/pages/" class="v3-rail-row" style="text-decoration:none">
        <div class="v3-tool-logo" style="background:#175ddc">B</div>
        <div style="flex:1"><b>Bitwarden</b><small>Best budget option</small></div>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" style="color:var(--v3-text-5)"><polyline points="9 18 15 12 9 6"/></svg>
      </a>
      <a href="/pages/" class="v3-rail-row" style="text-decoration:none">
        <div class="v3-tool-logo" style="background:#0e7490">D</div>
        <div style="flex:1"><b>Dashlane</b><small>Best for ease of use</small></div>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" style="color:var(--v3-text-5)"><polyline points="9 18 15 12 9 6"/></svg>
      </a>
      <a href="/pages/" class="v3-rail-row" style="text-decoration:none">
        <div class="v3-tool-logo" style="background:#fbbf24;color:#000">K</div>
        <div style="flex:1"><b>Keeper</b><small>Best for security</small></div>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" style="color:var(--v3-text-5)"><polyline points="9 18 15 12 9 6"/></svg>
      </a>
      <p style="margin:.85rem 0 0"><a href="#" class="v3-link-cta" style="font-size:.8rem">See all alternatives &#8594;</a></p>
    </div>

    <div class="v3-rail-card">
      <h3>On this page</h3>
      <ol style="list-style:none;counter-reset:toc;padding:0;margin:0">
        <li style="counter-increment:toc;padding-left:1.4rem;margin:.3rem 0;position:relative;font-size:.82rem"><a href="#quick-answer" style="color:var(--v3-text-3)"><span style="position:absolute;left:0;color:var(--v3-text-5);font-weight:700">1</span>Quick answer</a></li>
        <li style="counter-increment:toc;padding-left:1.4rem;margin:.3rem 0;position:relative;font-size:.82rem"><a href="#pricing-glance" style="color:var(--v3-text-3)"><span style="position:absolute;left:0;color:var(--v3-text-5);font-weight:700">2</span>Pricing at a glance</a></li>
        <li style="counter-increment:toc;padding-left:1.4rem;margin:.3rem 0;position:relative;font-size:.82rem"><a href="#vs-bitwarden" style="color:var(--v3-text-3)"><span style="position:absolute;left:0;color:var(--v3-text-5);font-weight:700">3</span>1Password vs Bitwarden</a></li>
        <li style="counter-increment:toc;padding-left:1.4rem;margin:.3rem 0;position:relative;font-size:.82rem"><a href="#hidden-fees" style="color:var(--v3-red-light)"><span style="position:absolute;left:0;color:var(--v3-text-5);font-weight:700">4</span>Hidden fees</a></li>
        <li style="counter-increment:toc;padding-left:1.4rem;margin:.3rem 0;position:relative;font-size:.82rem"><a href="#" style="color:var(--v3-text-3)"><span style="position:absolute;left:0;color:var(--v3-text-5);font-weight:700">5</span>Our top pick</a></li>
        <li style="counter-increment:toc;padding-left:1.4rem;margin:.3rem 0;position:relative;font-size:.82rem"><a href="#" style="color:var(--v3-text-3)"><span style="position:absolute;left:0;color:var(--v3-text-5);font-weight:700">6</span>1Password review</a></li>
        <li style="counter-increment:toc;padding-left:1.4rem;margin:.3rem 0;position:relative;font-size:.82rem"><a href="#" style="color:var(--v3-text-3)"><span style="position:absolute;left:0;color:var(--v3-text-5);font-weight:700">7</span>Related comparisons</a></li>
        <li style="counter-increment:toc;padding-left:1.4rem;margin:.3rem 0;position:relative;font-size:.82rem"><a href="#" style="color:var(--v3-text-3)"><span style="position:absolute;left:0;color:var(--v3-text-5);font-weight:700">8</span>FAQs</a></li>
      </ol>
    </div>
  </aside>
</div>

{FOOTER}
{fab()}
</body></html>
"""


# ─────────────────────────────────────────────────────────────────────
# 03. ROI CALCULATOR — clones Image 5 / Image 7
# ─────────────────────────────────────────────────────────────────────
def page_roi() -> str:
    head = head_html(
        "Calculate the real ROI of any SaaS tool",
        "Model total costs, quantify savings, and see the true return before you commit. Free SaaS ROI calculator.",
        f"{BASE}/pages/v3-preview-roi-calculator",
    )
    return f"""{head}
{nav_html(active='roi')}

<section class="v3-hero">
  <div class="v3-hero-inner">
    <span class="v3-eyebrow">ROI Calculator</span>
    <h1>Calculate the real <em>ROI.</em><br>Justify every <em>SaaS decision.</em></h1>
    <p class="v3-sub">Model total costs, quantify savings and see the true return before you commit to any vendor.</p>
  </div>
</section>

<div class="v3-container">
  <div class="v3-feature-grid">
    <div class="v3-feature">
      <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div>
      <h4>All-in cost modelling</h4>
      <p>Include subscription, fees, implementation and switching.</p>
    </div>
    <div class="v3-feature">
      <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
      <h4>Time &amp; efficiency value</h4>
      <p>Convert hours saved into real dollar impact.</p>
    </div>
    <div class="v3-feature">
      <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg></div>
      <h4>Instant ROI view</h4>
      <p>See payback period and annual savings instantly.</p>
    </div>
    <div class="v3-feature">
      <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
      <h4>Benchmark &amp; trust</h4>
      <p>Compare against market data and real buyer benchmarks.</p>
    </div>
  </div>

  <div class="v3-grid-2" style="margin-top:1.5rem">
    <div class="v3-card v3-card-padded">
      <h2 style="font-size:1.2rem">Your inputs</h2>
      <p class="v3-muted" style="margin:0 0 1.4rem;font-size:.86rem">Enter your numbers to see your potential return.</p>

      <h4 style="font-size:.7rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.6px;margin:1rem 0 .55rem">Costs</h4>
      <label class="v3-label">Annual subscription cost</label>
      <div class="v3-row tight" style="gap:.5rem"><input type="number" class="v3-input" value="24000" style="flex:1"><select class="v3-select" style="max-width:120px"><option>per year</option></select></div>

      <label class="v3-label" style="margin-top:.85rem">Number of users</label>
      <div class="v3-row tight" style="gap:.5rem"><input type="number" class="v3-input" value="25" style="flex:1"><select class="v3-select" style="max-width:120px"><option>users</option></select></div>

      <label class="v3-label" style="margin-top:.85rem">One-time implementation cost</label>
      <input type="number" class="v3-input" value="8000">

      <label class="v3-label" style="margin-top:.85rem">Switching &amp; migration cost</label>
      <input type="number" class="v3-input" value="3000">

      <h4 style="font-size:.7rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.6px;margin:1.4rem 0 .55rem">Benefits</h4>
      <label class="v3-label">Average fully-loaded cost per user</label>
      <div class="v3-row tight" style="gap:.5rem"><input type="number" class="v3-input" value="85" style="flex:1"><select class="v3-select" style="max-width:120px"><option>per hour</option></select></div>

      <label class="v3-label" style="margin-top:.85rem">Hours saved per user per week</label>
      <div class="v3-row tight" style="gap:.5rem"><input type="number" class="v3-input" value="2.5" step="0.1" style="flex:1"><select class="v3-select" style="max-width:120px"><option>hours</option></select></div>

      <label class="v3-label" style="margin-top:.85rem">Efficiency improvement (non-time savings)</label>
      <div class="v3-row tight" style="gap:.5rem"><input type="number" class="v3-input" value="10" style="flex:1"><select class="v3-select" style="max-width:120px"><option>%</option></select></div>

      <div class="v3-callout v3-callout-pro" style="margin:1.4rem 0 1.2rem">
        <div class="v3-callout-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></div>
        <div class="v3-callout-body"><h4>Pro tip</h4><p>Include both time savings and non-time efficiency gains for a more accurate ROI.</p></div>
      </div>

      <div class="v3-row" style="gap:.6rem"><button class="v3-btn v3-btn-primary v3-btn-lg" style="flex:1">Calculate ROI</button><button class="v3-btn v3-btn-secondary">Reset</button></div>
    </div>

    <div class="v3-card v3-card-padded">
      <div class="v3-row between" style="margin-bottom:1rem"><h2 style="font-size:1.2rem;margin:0">Your ROI results</h2><select class="v3-select" style="max-width:170px"><option>Conservative</option></select></div>
      <h4 style="font-size:.7rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.6px;margin:0 0 .85rem">Key outcomes</h4>

      <div class="v3-grid-2">
        <div class="v3-card-flat" style="padding:1.05rem 1.2rem">
          <div style="font-size:.78rem;color:var(--v3-text-4);margin-bottom:.45rem">Monthly ROI</div>
          <div style="font-family:var(--v3-ff-display);font-size:2rem;font-weight:850;color:var(--v3-good);line-height:1">312%</div>
          <div style="font-size:.78rem;color:var(--v3-text-4);margin-top:.35rem">$6,240 net benefit / month</div>
          <div style="margin-top:.55rem"><span class="v3-tag green">Excellent</span></div>
        </div>
        <div class="v3-card-flat" style="padding:1.05rem 1.2rem">
          <div style="font-size:.78rem;color:var(--v3-text-4);margin-bottom:.45rem">Annual net savings</div>
          <div style="font-family:var(--v3-ff-display);font-size:2rem;font-weight:850;color:var(--v3-good);line-height:1">$74,880</div>
          <div style="font-size:.78rem;color:var(--v3-text-4);margin-top:.35rem">Total after all costs</div>
          <div style="margin-top:.55rem"><span class="v3-tag green">Excellent</span></div>
        </div>
        <div class="v3-card-flat" style="padding:1.05rem 1.2rem">
          <div style="font-size:.78rem;color:var(--v3-text-4);margin-bottom:.45rem">Payback period</div>
          <div style="font-family:var(--v3-ff-display);font-size:2rem;font-weight:850;color:#74a9ff;line-height:1">1.7 months</div>
          <div style="font-size:.78rem;color:var(--v3-text-4);margin-top:.35rem">Time to break even</div>
          <div style="margin-top:.55rem"><span class="v3-tag blue">Excellent</span></div>
        </div>
        <div class="v3-card-flat" style="padding:1.05rem 1.2rem">
          <div style="font-size:.78rem;color:var(--v3-text-4);margin-bottom:.45rem">3-year ROI</div>
          <div style="font-family:var(--v3-ff-display);font-size:2rem;font-weight:850;color:#74a9ff;line-height:1">412%</div>
          <div style="font-size:.78rem;color:var(--v3-text-4);margin-top:.35rem">Total return over 3 years</div>
          <div style="margin-top:.55rem"><span class="v3-tag blue">Excellent</span></div>
        </div>
      </div>

      <div class="v3-verdict-box" style="margin:1.4rem 0">
        <div class="crown"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 4l3 12h14l3-12-6 7-4-7-4 7-6-7zm3 16h14"/></svg></div>
        <div>
          <h4>Our verdict</h4>
          <p class="verdict-line" style="color:var(--v3-good)">Strong Buy</p>
          <p class="verdict-sub">This investment delivers exceptional value and pays for itself in under 2 months.</p>
        </div>
      </div>

      <div class="v3-card-flat" style="padding:1.2rem">
        <div style="font-size:.74rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.5px;margin-bottom:.6rem;font-weight:800">Cash flow overview</div>
        <div style="display:flex;gap:1.2rem;font-size:.74rem;color:var(--v3-text-4);margin-bottom:.85rem"><span style="display:inline-flex;align-items:center;gap:5px">●&nbsp;Total Costs</span><span style="display:inline-flex;align-items:center;gap:5px;color:var(--v3-good)">●&nbsp;Total Benefits</span><span style="display:inline-flex;align-items:center;gap:5px;color:#74a9ff">●&nbsp;Net Benefit</span></div>
        <svg viewBox="0 0 600 200" style="width:100%;height:auto" aria-label="Cash flow chart">
          <polyline points="0,170 120,150 240,110 360,80 480,55 600,30" fill="none" stroke="#74a9ff" stroke-width="2.5"/>
          <g fill="#34d399" opacity=".7"><rect x="20" y="120" width="20" height="60"/><rect x="120" y="100" width="20" height="80"/><rect x="240" y="60" width="20" height="120"/><rect x="360" y="35" width="20" height="145"/><rect x="480" y="20" width="20" height="160"/></g>
          <g fill="#f97070" opacity=".7"><rect x="50" y="135" width="20" height="45"/><rect x="150" y="142" width="20" height="38"/><rect x="270" y="148" width="20" height="32"/><rect x="390" y="151" width="20" height="29"/><rect x="510" y="153" width="20" height="27"/></g>
          <g fill="#fff" font-size="11" font-family="Inter"><text x="20" y="195">Month 1</text><text x="120" y="195">Month 6</text><text x="240" y="195">Month 12</text><text x="360" y="195">Year 2</text><text x="480" y="195">Year 3</text></g>
          <g fill="rgba(255,255,255,.4)" font-size="10" font-family="Inter" text-anchor="end"><text x="595" y="35">$100k</text><text x="595" y="80">$50k</text><text x="595" y="125">$0</text><text x="595" y="170">-$50k</text></g>
        </svg>
      </div>
    </div>
  </div>

  <details class="v3-card v3-card-flat" style="margin-top:1.5rem"><summary style="cursor:pointer;display:flex;align-items:center;gap:.6rem;font-weight:700;color:#fff"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>Assumptions &amp; details</summary><p class="v3-muted" style="margin:.85rem 0 0;font-size:.86rem">Calculations assume annual billing. Time savings valued at fully-loaded cost. Adjust efficiency % to fit your team's reality.</p></details>

  <div class="v3-card v3-card-padded" style="margin-top:1.5rem;text-align:center">
    <p style="font-size:.78rem;color:var(--v3-text-4);margin:0 0 .85rem">Trusted by buyers who do their homework</p>
    <div class="v3-grid-4">
      <div><div class="v3-card-icon" style="margin:0 auto .55rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div><b style="font-size:.85rem">Independent &amp; unbiased</b><p style="font-size:.76rem;color:var(--v3-text-4);margin:.25rem 0 0">We don't sell software.</p></div>
      <div><div class="v3-card-icon" style="margin:0 auto .55rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15 8.5 22 9.5 17 14 18.5 21 12 17.5 5.5 21 7 14 2 9.5 9 8.5 12 2"/></svg></div><b style="font-size:.85rem">Real buyer benchmarks</b><p style="font-size:.76rem;color:var(--v3-text-4);margin:.25rem 0 0">Based on 1,000+ pricing pages and buyer insights.</p></div>
      <div><div class="v3-card-icon" style="margin:0 auto .55rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg></div><b style="font-size:.85rem">Updated monthly</b><p style="font-size:.76rem;color:var(--v3-text-4);margin:.25rem 0 0">Our data is refreshed to stay current.</p></div>
      <div><div class="v3-card-icon" style="margin:0 auto .55rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></div><b style="font-size:.85rem">Privacy first</b><p style="font-size:.76rem;color:var(--v3-text-4);margin:.25rem 0 0">Your inputs are private and never shared.</p></div>
    </div>
  </div>

  <div class="v3-card v3-card-padded v3-card-emph" style="margin-top:1.5rem;text-align:center">
    <h2 style="font-size:1.2rem;margin:0 0 .35rem">Make confident decisions, faster.</h2>
    <p class="v3-muted" style="margin:0 0 1rem;font-size:.86rem">Compare alternatives side-by-side or build a ranked shortlist for your team.</p>
    <div class="v3-row center" style="gap:.6rem"><a href="/pages/" class="v3-btn v3-btn-primary">Compare alternatives &#8594;</a><a href="/shortlist" class="v3-btn v3-btn-secondary">Build shortlist &#8594;</a></div>
  </div>
</div>

{FOOTER}
{fab()}
</body></html>
"""


# Map name → builder. Will be populated below.
PAGES = {
    "homepage": page_homepage,
    "comparison": page_comparison,
    "roi-calculator": page_roi,
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
    print(f"\n{written} preview pages written to {OUT_DIR.relative_to(ROOT)}/")
