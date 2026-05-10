"""Rebuilds /pages/v3-preview-homepage to match Image 10 — red matrix dot bg + typewriter."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from v3_partials import nav_html, head_html, FOOTER  # noqa: E402

OUT = ROOT / "site" / "pages" / "v3-preview-homepage.html"
BASE = "https://saaspare.org"


def fab() -> str:
    return '<a class="v3-fab" href="#decision-trail">Decision Trail <b>5</b></a>'


def build() -> str:
    head = head_html(
        "SaaSpare — The honest guide to SaaS for teams that care about ROI",
        "We dig through pricing pages, call out hidden fees, and give you a straight verdict on every SaaS tool.",
        f"{BASE}/pages/v3-preview-homepage",
    )
    return f"""{head}
{nav_html(active='')}

<section class="v3-hero" style="position:relative;overflow:hidden;padding-top:6rem;padding-bottom:3rem;text-align:center">
  <div class="v3-matrix-glow"></div>
  <div class="v3-matrix-bg"></div>
  <div class="v3-hero-inner" style="position:relative;z-index:2;max-width:880px">
    <span class="v3-eyebrow">1,156 buyer pages indexed</span>
    <h1 style="margin:1rem 0 1.2rem">The honest guide to<br><em class="v3-typewriter" data-words='["CRM Software","Marketing Tools","Email Marketing","Project Management","Password Managers","Help Desk Tools","Analytics Tools"]' style="min-width:6ch;display:inline-block">CRM Software</em><br>for teams that care about ROI</h1>
    <p class="v3-sub" style="max-width:620px;margin:0 auto 1.6rem">We dig through pricing pages, call out hidden fees, and give you a straight verdict — so your team picks the right tool without the regret.</p>

    <div class="v3-search">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" style="color:rgba(255,255,255,.32)"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
      <input type="search" placeholder="Search any tool, category, or use case…">
      <button>Search</button>
    </div>
    <div class="v3-popular">
      <span>Popular:</span>
      <a href="#">HubSpot</a><a href="#">Notion</a><a href="#">Shopify</a><a href="#">Salesforce</a><a href="#">Ahrefs vs SEMrush</a>
    </div>

    <div class="v3-grid-4" style="margin-top:1.8rem;max-width:860px;margin-left:auto;margin-right:auto">
      <div class="v3-card" style="text-align:left">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
        <h4 style="margin:.7rem 0 .25rem;font-size:.92rem">Unbiased &amp; Independent</h4>
        <p style="font-size:.78rem;color:var(--v3-text-4);margin:0;line-height:1.5">No affiliate fees. Ever.</p>
      </div>
      <div class="v3-card" style="text-align:left">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/></svg></div>
        <h4 style="margin:.7rem 0 .25rem;font-size:.92rem">Human Research</h4>
        <p style="font-size:.78rem;color:var(--v3-text-4);margin:0;line-height:1.5">Real humans. Real verdicts.</p>
      </div>
      <div class="v3-card" style="text-align:left">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div>
        <h4 style="margin:.7rem 0 .25rem;font-size:.92rem">Price Transparency</h4>
        <p style="font-size:.78rem;color:var(--v3-text-4);margin:0;line-height:1.5">Hidden fees? We find them.</p>
      </div>
      <div class="v3-card" style="text-align:left">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg></div>
        <h4 style="margin:.7rem 0 .25rem;font-size:.92rem">ROI Focused</h4>
        <p style="font-size:.78rem;color:var(--v3-text-4);margin:0;line-height:1.5">Tools that pay for themselves.</p>
      </div>
    </div>

    <div style="margin-top:1.8rem">
      <div class="v3-trust-avatars">
        <span class="v3-avatars">
          <span style="background:linear-gradient(135deg,#9b6dff,#7048d3)"></span>
          <span style="background:linear-gradient(135deg,#34d399,#10b981)"></span>
          <span style="background:linear-gradient(135deg,#ffc864,#f59e0b)"></span>
          <span style="background:linear-gradient(135deg,#74a9ff,#3b82f6)"></span>
          <span style="background:linear-gradient(135deg,#e94560,#c73652)"></span>
        </span>
        <span>Trusted by <b>8,000+</b> operators, founders &amp; teams</span>
        <span style="margin-left:6px;padding-left:14px;border-left:1px solid var(--v3-border)" class="v3-stars">★★★★★</span>
        <span><b>4.6/5</b> from 250+ reviews</span>
      </div>
    </div>
  </div>
</section>

<section class="v3-section">
  <div class="v3-container">
    <div class="v3-section-head"><h2>Top categories</h2><a href="/pages/" class="v3-link-cta">Browse all categories &#8594;</a></div>
    <div class="v3-grid-4" style="grid-template-columns:repeat(7,minmax(0,1fr))">
      <a class="v3-card" href="/pages/best-password-managers-software-for-business-in-2026-ranked"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></div><h4 style="font-size:.9rem;margin:.6rem 0 .15rem">Password Mgmt</h4><p style="font-size:.72rem;color:var(--v3-text-5);margin:0">16</p></a>
      <a class="v3-card" href="/pages/best-crm-software-for-b2b-saas-in-2026-ranked"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg></div><h4 style="font-size:.9rem;margin:.6rem 0 .15rem">CRM</h4><p style="font-size:.72rem;color:var(--v3-text-5);margin:0">22</p></a>
      <a class="v3-card" href="/pages/"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></div><h4 style="font-size:.9rem;margin:.6rem 0 .15rem">Help Desk</h4><p style="font-size:.72rem;color:var(--v3-text-5);margin:0">16</p></a>
      <a class="v3-card" href="/pages/best-project-management-software-for-startups-in-2026-ranked"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg></div><h4 style="font-size:.9rem;margin:.6rem 0 .15rem">Project Mgmt</h4><p style="font-size:.72rem;color:var(--v3-text-5);margin:0">20</p></a>
      <a class="v3-card" href="/pages/best-marketing-automation-software-for-small-business-in-2026-ranked"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg></div><h4 style="font-size:.9rem;margin:.6rem 0 .15rem">Email Marketing</h4><p style="font-size:.72rem;color:var(--v3-text-5);margin:0">14</p></a>
      <a class="v3-card" href="/pages/best-finance-ops-software-for-b2b-saas-in-2026-ranked"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div><h4 style="font-size:.9rem;margin:.6rem 0 .15rem">Accounting</h4><p style="font-size:.72rem;color:var(--v3-text-5);margin:0">13</p></a>
      <a class="v3-card" href="/pages/"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></div><h4 style="font-size:.9rem;margin:.6rem 0 .15rem">View all</h4><p style="font-size:.72rem;color:var(--v3-text-5);margin:0">72+</p></a>
    </div>
  </div>
</section>

<section class="v3-section">
  <div class="v3-container">
    <div class="v3-section-head"><h2>Featured comparisons</h2><a href="/pages/" class="v3-link-cta">View all &#8594;</a></div>
    <div class="v3-grid-4">
      <a class="v3-card" href="/pages/1password-vs-bitwarden-which-is-better-in-2026"><div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.85rem"><div class="v3-tool-logo" style="width:36px;height:36px;background:#0070ad;font-size:.85rem">1P</div><span style="color:var(--v3-text-4);font-size:.78rem;font-weight:700">vs</span><div class="v3-tool-logo" style="width:36px;height:36px;background:#175ddc;font-size:.85rem">BW</div></div><h4 style="margin:0 0 .35rem">1Password vs Bitwarden</h4><p style="font-size:.78rem;color:var(--v3-text-4);margin:0 0 .8rem">Security, features, and pricing compared.</p><span class="v3-link-cta" style="font-size:.78rem">View &#8594;</span></a>
      <a class="v3-card" href="/pages/hubspot-vs-pipedrive-which-is-better-in-2026"><div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.85rem"><div class="v3-tool-logo" style="width:36px;height:36px;background:#ff7a59;font-size:.85rem">H</div><span style="color:var(--v3-text-4);font-size:.78rem;font-weight:700">vs</span><div class="v3-tool-logo" style="width:36px;height:36px;background:#1a1a1a;font-size:.85rem">P</div></div><h4 style="margin:0 0 .35rem">HubSpot vs Pipedrive</h4><p style="font-size:.78rem;color:var(--v3-text-4);margin:0 0 .8rem">Best CRM for growing teams?</p><span class="v3-link-cta" style="font-size:.78rem">View &#8594;</span></a>
      <a class="v3-card" href="/pages/notion-vs-clickup-which-is-better-in-2026"><div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.85rem"><div class="v3-tool-logo" style="width:36px;height:36px;background:#fff;color:#000;font-size:.85rem">N</div><span style="color:var(--v3-text-4);font-size:.78rem;font-weight:700">vs</span><div class="v3-tool-logo" style="width:36px;height:36px;background:#7b68ee;font-size:.85rem">C</div></div><h4 style="margin:0 0 .35rem">Notion vs ClickUp</h4><p style="font-size:.78rem;color:var(--v3-text-4);margin:0 0 .8rem">Project docs vs tasks.</p><span class="v3-link-cta" style="font-size:.78rem">View &#8594;</span></a>
      <a class="v3-card" href="/pages/"><div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.85rem"><div class="v3-tool-logo" style="width:36px;height:36px;background:#4a154b;font-size:.85rem">S</div><span style="color:var(--v3-text-4);font-size:.78rem;font-weight:700">vs</span><div class="v3-tool-logo" style="width:36px;height:36px;background:#5b5fc7;font-size:.85rem">T</div></div><h4 style="margin:0 0 .35rem">Slack vs Teams</h4><p style="font-size:.78rem;color:var(--v3-text-4);margin:0 0 .8rem">Messaging, real cost.</p><span class="v3-link-cta" style="font-size:.78rem">View &#8594;</span></a>
    </div>
  </div>
</section>

<section class="v3-section">
  <div class="v3-container">
    <h2>Buyer tools</h2>
    <p class="v3-muted" style="margin:0 0 1.4rem">Everything you need to research, compare, and decide.</p>
    <div class="v3-grid-4">
      <a class="v3-card" href="/shortlist"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/></svg></div><h4 style="margin:.85rem 0 .25rem">Shortlist Builder</h4><p style="font-size:.82rem;color:var(--v3-text-4);margin:0">Rank tools by fit, budget, must-haves.</p></a>
      <a class="v3-card" href="/deal-radar"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg></div><h4 style="margin:.85rem 0 .25rem">Deal Radar</h4><p style="font-size:.82rem;color:var(--v3-text-4);margin:0">Track pricing changes &amp; promos.</p></a>
      <a class="v3-card" href="/pages/saas-roi-calculator"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/></svg></div><h4 style="margin:.85rem 0 .25rem">ROI Calculator</h4><p style="font-size:.82rem;color:var(--v3-text-4);margin:0">See real return before you commit.</p></a>
      <a class="v3-card" href="#"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div><h4 style="margin:.85rem 0 .25rem">Decision Trail</h4><p style="font-size:.82rem;color:var(--v3-text-4);margin:0">Build a clear decision record.</p></a>
    </div>
  </div>
</section>

{FOOTER}
{fab()}
</body></html>
"""


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"  wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size:,} bytes)")
