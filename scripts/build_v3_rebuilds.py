"""Rebuilds priority v3 preview pages to match user-specified mockups exactly.

Library  → Image 6 (clean hub with category chips + 4 product cards + buyer-intent rail)
Privacy  → Image 13 (TOC left, hero centred, Key Points callout)
Shortlist → Image 2 ("Your Shortlist. Your Decision." + at-a-glance sidebar)
Affiliate → Image 14 (2-col: how we make money + ranking weights | editorial + review principles + transparency)
404      → Image 12 (with telescope SVG and red glow)
Newsletter → Image 15 (latest-issue magazine sidebar with mockup)
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from v3_partials import nav_html, head_html, FOOTER  # noqa: E402

OUT_DIR = ROOT / "site" / "pages"
BASE = "https://saaspare.org"


def fab() -> str:
    return '<a class="v3-fab" href="#decision-trail">Decision Trail <b>5</b></a>'


# ───────────────────────── LIBRARY (Image 6) ──────────────────────
def page_library():
    head = head_html(
        "Find the right SaaS answer faster",
        "Search 1,156 buyer pages — pricing guides, comparisons, alternatives and reviews.",
        f"{BASE}/pages/v3-preview-library",
    )
    return f"""{head}
{nav_html(active='comparisons')}

<section class="v3-hero" style="position:relative;overflow:hidden;padding-bottom:1.5rem">
  <div class="v3-matrix-bg" style="opacity:.4"></div>
  <div class="v3-hero-inner" style="position:relative;z-index:2">
    <h1 style="margin:1.5rem 0 1.2rem">Find the right <em>SaaS answer</em> faster.</h1>
    <p class="v3-sub">Search pricing pages, comparison verdicts, trial paths and alternatives without opening ten vendor tabs.</p>
    <div class="v3-search" style="margin-top:1.5rem">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" style="color:rgba(255,255,255,.32)"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
      <input type="search" placeholder="Search tools, use cases, categories…">
      <button>Search</button>
    </div>
    <div class="v3-row center" style="gap:2.5rem;margin-top:1.5rem">
      <div style="text-align:center"><b style="color:#fff;font-size:1rem;display:block">806</b><span style="font-size:.74rem;color:var(--v3-text-5)">Comparisons</span></div>
      <div style="text-align:center"><b style="color:#fff;font-size:1rem;display:block">64</b><span style="font-size:.74rem;color:var(--v3-text-5)">Pricing Guides</span></div>
      <div style="text-align:center"><b style="color:#fff;font-size:1rem;display:block">34</b><span style="font-size:.74rem;color:var(--v3-text-5)">Reviews</span></div>
      <div style="text-align:center"><b style="color:#fff;font-size:1rem;display:block">1,156</b><span style="font-size:.74rem;color:var(--v3-text-5)">Buyer Pages Indexed</span></div>
    </div>
  </div>
</section>

<div class="v3-container">
  <div class="v3-section-head" style="margin-bottom:1rem"><h2 style="font-size:1rem">Filter by what matters</h2><span class="v3-muted" style="font-size:.78rem">Buyer-intent first, then sort by what's most useful right now.</span></div>
  <div class="v3-tabs-bar" style="margin-bottom:1.5rem">
    <a href="#" class="active">All</a>
    <a href="#">CRM</a><a href="#">Marketing</a><a href="#">Sales</a><a href="#">Finance</a>
    <a href="#">Project Mgmt</a><a href="#">HR</a><a href="#">IT &amp; Security</a>
    <a href="#">Analytics</a><a href="#">Developer</a><a href="#">Other</a>
    <span style="margin-left:auto;color:var(--v3-text-4);font-size:.82rem;align-self:center">Sort by <b style="color:#fff">Recommended</b> ▾</span>
  </div>
</div>

<div class="v3-layout-main" style="grid-template-columns:minmax(0,1fr) 280px;gap:1.5rem">
  <main>
    <div class="v3-grid-4" style="grid-template-columns:repeat(4,minmax(0,1fr));gap:1rem">
      {_lib_product_card("1Password","Security & Password Management","Secure password manager for teams, personal, and enterprise.","#0070ad","1P","$2.99","user / month","4.9","(522)","red")}
      {_lib_product_card("Bitwarden","Security & Password Management","Open-source password manager for teams &amp; enterprises.","#175ddc","BW","$4.00","user / month","4.6","(298)","")}
      {_lib_product_card("LastPass","Security & Password Management","Password manager with secure sharing and storage.","#d32d27","LP","$3.00","user / month","4.3","(341)","")}
      {_lib_product_card("Dashlane","Security & Password Management","Password manager built-in VPN and dark-web monitoring.","#0e7490","D","$4.99","user / month","4.6","(478)","")}
    </div>
  </main>

  <aside>
    <div class="v3-rail-card">
      <h3 style="display:flex;align-items:center;gap:.5rem"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="var(--v3-red)" stroke-width="2"><polyline points="22 11.08 12 17 2 11.08"/><polygon points="12 2 22 8.5 12 15 2 8.5 12 2"/></svg>Buyer intent quick filters</h3>
      <div style="display:flex;flex-direction:column;gap:.7rem;margin-top:.5rem">
        <a href="#" class="v3-row tight" style="gap:.55rem;align-items:flex-start;text-decoration:none;font-size:.82rem;color:var(--v3-text-2);line-height:1.45"><span style="color:var(--v3-red);font-size:1.1rem;line-height:1">●</span><span>Compare top tools<br><small style="color:var(--v3-text-5)">Side-by-side comparisons</small></span></a>
        <a href="#" class="v3-row tight" style="gap:.55rem;align-items:flex-start;text-decoration:none;font-size:.82rem;color:var(--v3-text-2);line-height:1.45"><span style="color:var(--v3-red);font-size:1.1rem;line-height:1">●</span><span>Find best value<br><small style="color:var(--v3-text-5)">Best ROI &amp; lowest cost</small></span></a>
        <a href="#" class="v3-row tight" style="gap:.55rem;align-items:flex-start;text-decoration:none;font-size:.82rem;color:var(--v3-text-2);line-height:1.45"><span style="color:var(--v3-red);font-size:1.1rem;line-height:1">●</span><span>Free trial available<br><small style="color:var(--v3-text-5)">Try before you buy</small></span></a>
        <a href="#" class="v3-row tight" style="gap:.55rem;align-items:flex-start;text-decoration:none;font-size:.82rem;color:var(--v3-text-2);line-height:1.45"><span style="color:var(--v3-red);font-size:1.1rem;line-height:1">●</span><span>Best for small teams<br><small style="color:var(--v3-text-5)">Best fit for SMB</small></span></a>
        <a href="#" class="v3-row tight" style="gap:.55rem;align-items:flex-start;text-decoration:none;font-size:.82rem;color:var(--v3-text-2);line-height:1.45"><span style="color:var(--v3-red);font-size:1.1rem;line-height:1">●</span><span>Enterprise ready<br><small style="color:var(--v3-text-5)">Scale &amp; security</small></span></a>
      </div>
      <button class="v3-btn v3-btn-secondary v3-btn-sm" style="width:100%;margin-top:1rem">Clear all filters</button>
    </div>
  </aside>
</div>

{FOOTER}
{fab()}
</body></html>
"""


def _lib_product_card(name, badge, desc, bg, logo, price, period, rating, count, badge_color):
    badge_html = '<span style="position:absolute;top:.7rem;right:.7rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="var(--v3-text-5)" stroke-width="2"><polygon points="19 21 12 17 5 21 5 5 19 5 19 21"/></svg></span>'
    return f"""<a class="v3-card" href="#" style="position:relative;display:block;text-decoration:none">
        {badge_html}
        <div class="v3-tool-logo" style="background:{bg};color:{'#000' if bg == '#fff' else '#fff'};margin-bottom:.85rem">{logo}</div>
        <h3 style="font-size:.95rem;margin:0 0 .25rem;color:#fff">{name}</h3>
        <p style="font-size:.7rem;color:var(--v3-text-5);margin:0 0 .55rem;letter-spacing:.4px;text-transform:uppercase">{badge}</p>
        <p style="font-size:.78rem;color:var(--v3-text-4);margin:0 0 1rem;line-height:1.5;min-height:50px">{desc}</p>
        <div style="font-family:var(--v3-ff-display);font-size:1.4rem;font-weight:850;color:#fff;line-height:1">{price}</div>
        <div style="font-size:.7rem;color:var(--v3-text-5);margin-bottom:.55rem">{period}</div>
        <div style="font-size:.78rem;color:var(--v3-text-3);margin-bottom:.85rem">★★★★★ <b style="color:#fff">{rating}</b> {count}</div>
        <span style="display:flex;align-items:center;justify-content:space-between;padding-top:.7rem;border-top:1px solid var(--v3-border);font-size:.78rem;color:var(--v3-red-light);font-weight:700">Pricing Guide <span>&#8594;</span></span>
      </a>"""


# ───────────────────── PRIVACY (Image 13) ─────────────────────────
def page_privacy():
    head = head_html(
        "Privacy Policy",
        "How SaaSpare collects, uses, and safeguards your information.",
        f"{BASE}/pages/v3-preview-privacy",
    )
    return f"""{head}
{nav_html(active='')}

<div class="v3-container" style="padding-top:5.5rem"><div class="v3-crumbs"><a href="/">Home</a><span>/</span><span>Privacy Policy</span></div></div>

<div style="max-width:var(--v3-page-max);margin:0 auto;padding:1rem var(--v3-page-pad);display:grid;grid-template-columns:240px minmax(0,1fr);gap:3rem;align-items:flex-start">
  <aside>
    <div class="v3-toc">
      <h4>On this page</h4>
      <ol>
        <li><a href="#intro" class="active">Introduction</a></li>
        <li><a href="#info-collect">Information We Collect</a></li>
        <li><a href="#how-we-use">How We Use Information</a></li>
        <li><a href="#cookies">Cookies &amp; Tracking</a></li>
        <li><a href="#info-share">Information Sharing</a></li>
        <li><a href="#data-security">Data Security</a></li>
        <li><a href="#choices">Your Choices</a></li>
        <li><a href="#retention">Data Retention</a></li>
        <li><a href="#kids">Children's Privacy</a></li>
        <li><a href="#int-transfer">International Transfers</a></li>
        <li><a href="#changes">Changes to This Policy</a></li>
        <li><a href="#contact">Contact Us</a></li>
      </ol>
    </div>
  </aside>

  <main style="max-width:760px">
    <div style="text-align:center;margin-bottom:1.2rem"><span class="v3-eyebrow">Privacy Policy</span></div>
    <h1 style="text-align:center">Privacy <em>Policy</em></h1>
    <p class="v3-help" style="text-align:center;margin:.4rem 0 1rem">Last updated: May 10, 2026</p>
    <p class="v3-lede" style="text-align:center;max-width:580px;margin:0 auto 2.5rem">At SaaSpare, your privacy matters. This policy explains what information we collect, how we use it, and the choices you have.</p>

    <h2 id="intro">1. Introduction</h2>
    <p>SaaSpare ("we", "our", or "us") operates the website saaspare.org (the "Site"). This Privacy Policy describes how we collect, use, disclose, and safeguard your information when you visit our Site.</p>

    <div class="v3-card v3-card-emph" style="padding:1.2rem 1.4rem;margin:1.4rem 0 2rem">
      <h4 style="font-size:.78rem;color:var(--v3-red-light);margin:0 0 .85rem;text-transform:uppercase;letter-spacing:.5px;font-weight:850">Key points</h4>
      <div class="v3-grid-3" style="gap:.7rem">
        <div style="background:rgba(255,255,255,.025);border:1px solid var(--v3-border);border-radius:12px;padding:.85rem 1rem">
          <div class="v3-card-icon" style="margin-bottom:.55rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg></div>
          <p style="font-size:.82rem;color:var(--v3-text-2);margin:0;line-height:1.5"><b>We don't sell your personal information.</b></p>
        </div>
        <div style="background:rgba(255,255,255,.025);border:1px solid var(--v3-border);border-radius:12px;padding:.85rem 1rem">
          <div class="v3-card-icon" style="margin-bottom:.55rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg></div>
          <p style="font-size:.82rem;color:var(--v3-text-2);margin:0;line-height:1.5"><b>We use data to improve content and user experience.</b></p>
        </div>
        <div style="background:rgba(255,255,255,.025);border:1px solid var(--v3-border);border-radius:12px;padding:.85rem 1rem">
          <div class="v3-card-icon" style="margin-bottom:.55rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></div>
          <p style="font-size:.82rem;color:var(--v3-text-2);margin:0;line-height:1.5"><b>You're in control of your privacy choices.</b></p>
        </div>
      </div>
    </div>

    <h2 id="info-collect">2. Information We Collect</h2>
    <p>We collect information you provide directly, information automatically collected, and information from third parties.</p>
    <h3 style="color:var(--v3-red-light);margin-top:1.2rem">a) Information you provide</h3>
    <p>When you sign up for our newsletter, contact us, or submit a comparison request, we collect your name, email address, and any details you choose to share.</p>
    <h3 style="color:var(--v3-red-light);margin-top:1.2rem">b) Information collected automatically</h3>
    <p>We collect device, browser, IP address, referrer, and pages visited via cookies and similar technologies — used to improve site performance and personalise content.</p>

    <h2 id="how-we-use">3. How We Use Information</h2>
    <ul><li>To provide and improve our services</li><li>To communicate with you</li><li>To analyse site usage</li><li>To prevent fraud and abuse</li></ul>

    <h2 id="cookies">4. Cookies &amp; Tracking</h2>
    <p>We use cookies and similar technologies to remember your preferences, measure traffic, and improve content. You can control cookies in your browser settings.</p>

    <h2 id="info-share">5. Information Sharing</h2>
    <p>We don't sell your personal data. We may share information with service providers (analytics, email, hosting) under strict confidentiality. Affiliate partners receive only anonymised click data.</p>

    <h2 id="data-security">6. Data Security</h2>
    <p>We use industry-standard technical and organisational measures to protect your information. No method of transmission over the internet is 100% secure, but we work hard to safeguard your data.</p>

    <h2 id="choices">7. Your Choices</h2>
    <p>You can opt out of marketing emails at any time by clicking unsubscribe. You can request a copy of your data, correction, or deletion by emailing <a href="mailto:privacy@saaspare.org">privacy@saaspare.org</a>.</p>

    <h2 id="contact">12. Contact Us</h2>
    <p>Questions? Email <a href="mailto:privacy@saaspare.org">privacy@saaspare.org</a>. We aim to respond within 5 business days.</p>
  </main>
</div>

{FOOTER}
{fab()}
</body></html>
"""


# ───────────────────── SHORTLIST (Image 2) ────────────────────────
def page_shortlist():
    head = head_html(
        "Your Shortlist. Your Decision.",
        "Compare tools side-by-side, see total costs, and choose the one that fits your team.",
        f"{BASE}/pages/v3-preview-shortlist",
    )
    return f"""{head}
{nav_html(active='shortlist')}

<section class="v3-hero" style="padding-bottom:1.5rem;text-align:center">
  <div class="v3-hero-inner">
    <h1 style="margin:1.5rem 0 1rem">Your <em>Shortlist.</em><br>Your Decision.</h1>
    <p class="v3-sub">Compare tools side-by-side, see total costs, and choose the one that fits your team.</p>
  </div>
</section>

<div class="v3-container">
  <div class="v3-row between" style="margin-bottom:1.2rem;flex-wrap:wrap;gap:1rem">
    <div class="v3-row tight" style="align-items:center">
      <span class="v3-muted" style="font-size:.8rem">Shortlist name</span>
      <select class="v3-select" style="display:inline-block;width:auto;font-weight:700;color:#fff">
        <option>G2 CRM Review</option>
        <option>Help Desk Round</option>
      </select>
      <button class="v3-btn-ghost" style="border:0;background:transparent;color:var(--v3-red-light);font-size:.78rem;cursor:pointer;padding:.5rem"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" style="display:inline;vertical-align:middle"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg> Edit</button>
    </div>
    <div class="v3-row tight">
      <button class="v3-btn v3-btn-secondary v3-btn-sm">Share Shortlist</button>
      <button class="v3-btn v3-btn-secondary v3-btn-sm">↓ Export PDF</button>
      <button class="v3-btn-ghost v3-btn-sm" style="border:0;background:transparent;color:var(--v3-text-4);cursor:pointer;font-size:.78rem">Clear All</button>
    </div>
  </div>
</div>

<div class="v3-layout-main" style="grid-template-columns:minmax(0,1fr) 320px">
  <main>
    <div class="v3-row" style="font-size:.78rem;color:var(--v3-text-3);margin-bottom:1rem"><b style="color:#fff">4 tools selected</b></div>
    <div class="v3-grid-4">
      {_short_card_v2(1,"H","#ff7a59","HubSpot","CRM","$20","seat / month","4.5","(2,103)","14 day free trial")}
      {_short_card_v2(2,"P","#1a1a1a","Pipedrive","CRM","$14","seat / month","4.3","(5,842)","14 day free trial","Best Fit")}
      {_short_card_v2(3,"Z","#0066ff","Zoho CRM","CRM","$0","seat / month","4.2","(1,331)","15 day free trial")}
      {_short_card_v2(4,"C","#10b981","Close","CRM","$29","seat / month","4.6","(1,106)","14 day free trial")}
    </div>

    <button class="v3-btn v3-btn-secondary" style="width:100%;margin-top:1rem;border:1px dashed var(--v3-border-hi);background:transparent">+ Add Another Tool</button>

    <div class="v3-card v3-card-padded v3-card-emph" style="margin-top:1.4rem;display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap">
      <div style="width:54px;height:54px;border-radius:50%;background:rgba(233,69,96,.18);border:1px solid rgba(233,69,96,.3);display:grid;place-items:center;flex-shrink:0"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" style="color:#fff"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg></div>
      <div style="flex:1;min-width:240px"><h3 style="margin:0 0 .25rem;font-size:1rem">Need help deciding?</h3><p style="margin:0;font-size:.85rem;color:var(--v3-text-3)">Our experts can help you pick the right tool for your team.</p></div>
      <a href="/contact" class="v3-btn v3-btn-primary">Talk to an Expert</a>
    </div>
  </main>

  <aside>
    <div class="v3-rail-card v3-card-padded">
      <h3 style="margin:0 0 1rem">At a glance</h3>
      <div style="font-size:.78rem;color:var(--v3-text-4);margin-bottom:.3rem">Total <span style="color:var(--v3-text-5)">(per month)</span></div>
      <div style="font-family:var(--v3-ff-display);font-size:2.4rem;font-weight:850;color:var(--v3-red-light);line-height:1;letter-spacing:-.04em">$77<span style="font-size:1rem;color:var(--v3-text-4);font-weight:600"> / month</span></div>
      <div style="font-size:.74rem;color:var(--v3-text-5);margin-bottom:1rem">for 4 seats</div>

      <div class="v3-divider" style="margin:1rem 0"></div>

      <div style="margin-bottom:.85rem">
        <div style="font-size:.78rem;color:var(--v3-text-4);margin-bottom:.25rem">Est. annual savings</div>
        <div style="font-family:var(--v3-ff-display);font-size:1.3rem;font-weight:850;color:var(--v3-good)">$1,428</div>
        <div style="font-size:.7rem;color:var(--v3-text-5)">vs highest-priced option</div>
      </div>
      <div>
        <div style="font-size:.78rem;color:var(--v3-text-4);margin-bottom:.25rem">Best fit</div>
        <div style="font-family:var(--v3-ff-display);font-size:1.1rem;font-weight:850;color:#fff">Pipedrive</div>
        <div style="font-size:.7rem;color:var(--v3-text-5)">Best balance of price &amp; features</div>
      </div>

      <div class="v3-divider" style="margin:1rem 0"></div>
      <div style="margin-bottom:1rem">
        <h4 style="font-size:.74rem;color:var(--v3-text-3);margin:0 0 .55rem;text-transform:uppercase;letter-spacing:.5px;font-weight:850">Next steps</h4>
        <div style="font-size:.78rem;color:var(--v3-text-2);padding:.3rem 0;display:flex;gap:.5rem"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="14" height="14" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>Compare features side-by-side</div>
        <div style="font-size:.78rem;color:var(--v3-text-2);padding:.3rem 0;display:flex;gap:.5rem"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="14" height="14" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>Run ROI calculation</div>
        <div style="font-size:.78rem;color:var(--v3-text-2);padding:.3rem 0;display:flex;gap:.5rem"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="14" height="14" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>Invite your team to vote</div>
      </div>
      <a href="#" class="v3-btn v3-btn-primary v3-btn-lg" style="width:100%;justify-content:center">Compare Side-by-Side &#8594;</a>
    </div>
  </aside>
</div>

{FOOTER}
{fab()}
</body></html>
"""


def _short_card_v2(rank, logo, bg, name, category, price, period, rating, count, trial, badge=None):
    badge_html = f'<span class="v3-badge red" style="margin-left:.4rem;font-size:.6rem">{badge}</span>' if badge else ""
    text_color = "#000" if bg == "#fff" else "#fff"
    return f"""<div class="v3-card" style="position:relative;text-align:center">
        <div style="position:absolute;top:.6rem;left:.6rem;width:22px;height:22px;border-radius:50%;background:rgba(255,255,255,.06);border:1px solid var(--v3-border);display:grid;place-items:center;color:var(--v3-text-3);font-size:.7rem;font-weight:800">{rank}</div>
        <div class="v3-tool-logo" style="background:{bg};color:{text_color};margin:0 auto .6rem;width:48px;height:48px;font-size:1rem">{logo}</div>
        <h3 style="margin:0;font-size:1rem;display:flex;align-items:center;justify-content:center;gap:.3rem">{name}{badge_html}</h3>
        <p style="font-size:.7rem;color:var(--v3-text-5);margin:.2rem 0 .85rem;text-transform:uppercase;letter-spacing:.4px">{category}</p>
        <div style="font-family:var(--v3-ff-display);font-size:1.5rem;font-weight:850;color:#fff;line-height:1">{price}</div>
        <div style="font-size:.7rem;color:var(--v3-text-5);margin-bottom:.55rem">{period}</div>
        <div style="font-size:.78rem;color:var(--v3-text-3);margin-bottom:.85rem">★★★★★ <b style="color:#fff">{rating}</b> {count}</div>
        <div style="font-size:.74rem;color:var(--v3-good);margin-bottom:.85rem">{trial}</div>
        <button class="v3-btn v3-btn-secondary v3-btn-sm" style="width:100%">View Details</button>
      </div>"""


# ───────────────────── AFFILIATE DISCLOSURE (Image 14) ─────────────
def page_affiliate():
    head = head_html(
        "How SaaSpare earns money and stays unbiased",
        "Independent. Transparent. Trusted. Here's how SaaSpare works.",
        f"{BASE}/pages/v3-preview-affiliate-disclosure",
    )
    return f"""{head}
{nav_html(active='')}

<section class="v3-hero" style="padding-bottom:1rem">
  <div class="v3-hero-inner" style="max-width:760px">
    <span class="v3-eyebrow">Our commitment</span>
    <h1 style="margin:1rem 0 1rem">Independent. Transparent. Trusted.<br><em>Here's how SaaSpare works.</em></h1>
    <p class="v3-sub">We're reader-first. Our mission is to help you make better SaaS buying decisions with honest research and clear, unbiased information.</p>
  </div>
</section>

<div class="v3-container">
  <div class="v3-grid-2" style="gap:1.5rem;align-items:flex-start">
    <div style="display:flex;flex-direction:column;gap:1.5rem">
      <div class="v3-card v3-card-padded">
        <h2 style="font-size:1.05rem;margin:0 0 .55rem">How SaaSpare Makes Money</h2>
        <p style="font-size:.85rem;color:var(--v3-text-3);margin:0 0 1rem">We earn commissions when you purchase through links on our site. These partnerships help us keep our content free.</p>
        <div class="v3-grid-3">
          <div style="background:rgba(255,255,255,.025);border:1px solid var(--v3-border);border-radius:12px;padding:.85rem"><div class="v3-card-icon" style="width:30px;height:30px;margin-bottom:.5rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div><b style="font-size:.78rem;display:block">You pay the same price</b><p style="font-size:.7rem;color:var(--v3-text-4);margin:.25rem 0 0;line-height:1.4">Our links never change your cost.</p></div>
          <div style="background:rgba(255,255,255,.025);border:1px solid var(--v3-border);border-radius:12px;padding:.85rem"><div class="v3-card-icon" style="width:30px;height:30px;margin-bottom:.5rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><polyline points="20 6 9 17 4 12"/></svg></div><b style="font-size:.78rem;display:block">We may earn a commission</b><p style="font-size:.7rem;color:var(--v3-text-4);margin:.25rem 0 0;line-height:1.4">From qualifying purchases at no extra cost to you.</p></div>
          <div style="background:rgba(255,255,255,.025);border:1px solid var(--v3-border);border-radius:12px;padding:.85rem"><div class="v3-card-icon" style="width:30px;height:30px;margin-bottom:.5rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div><b style="font-size:.78rem;display:block">It helps us stay independent</b><p style="font-size:.7rem;color:var(--v3-text-4);margin:.25rem 0 0;line-height:1.4">So we can keep researching and publishing.</p></div>
        </div>
      </div>

      <div class="v3-card v3-card-padded">
        <h2 style="font-size:1.05rem;margin:0 0 .55rem">How Our Rankings Work</h2>
        <p style="font-size:.85rem;color:var(--v3-text-3);margin:0 0 1rem">Our rankings are based on a 100-point framework across five pillars.</p>
        <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:.5rem;margin-bottom:.85rem">
          <div style="background:rgba(255,255,255,.025);border:1px solid var(--v3-border);border-radius:10px;padding:.7rem .5rem;text-align:center"><div style="font-size:.6rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.4px;margin-bottom:.2rem">Pricing</div><b style="font-family:var(--v3-ff-display);font-size:1rem">25 pts</b></div>
          <div style="background:rgba(255,255,255,.025);border:1px solid var(--v3-border);border-radius:10px;padding:.7rem .5rem;text-align:center"><div style="font-size:.6rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.4px;margin-bottom:.2rem">Features</div><b style="font-family:var(--v3-ff-display);font-size:1rem">25 pts</b></div>
          <div style="background:rgba(255,255,255,.025);border:1px solid var(--v3-border);border-radius:10px;padding:.7rem .5rem;text-align:center"><div style="font-size:.6rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.4px;margin-bottom:.2rem">Ease of Use</div><b style="font-family:var(--v3-ff-display);font-size:1rem">20 pts</b></div>
          <div style="background:rgba(255,255,255,.025);border:1px solid var(--v3-border);border-radius:10px;padding:.7rem .5rem;text-align:center"><div style="font-size:.6rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.4px;margin-bottom:.2rem">Integrations</div><b style="font-family:var(--v3-ff-display);font-size:1rem">15 pts</b></div>
          <div style="background:rgba(255,255,255,.025);border:1px solid var(--v3-border);border-radius:10px;padding:.7rem .5rem;text-align:center"><div style="font-size:.6rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.4px;margin-bottom:.2rem">Support</div><b style="font-family:var(--v3-ff-display);font-size:1rem">15 pts</b></div>
        </div>
        <p style="font-size:.78rem;color:var(--v3-good);text-align:center;margin:0">✓ No vendor can pay to rank higher. Ever.</p>
      </div>
    </div>

    <div style="display:flex;flex-direction:column;gap:1.5rem">
      <div class="v3-card v3-card-padded">
        <h2 style="font-size:1.05rem;margin:0 0 .85rem">Our Editorial Standards</h2>
        <ul style="list-style:none;padding:0;margin:0">
          <li style="display:flex;gap:.6rem;padding:.45rem 0;font-size:.85rem;color:var(--v3-text-2)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="16" height="16" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>We do independent research and testing when possible.</li>
          <li style="display:flex;gap:.6rem;padding:.45rem 0;font-size:.85rem;color:var(--v3-text-2)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="16" height="16" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>We verify pricing and details directly from official sources.</li>
          <li style="display:flex;gap:.6rem;padding:.45rem 0;font-size:.85rem;color:var(--v3-text-2)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="16" height="16" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>We don't accept payment for positive coverage.</li>
          <li style="display:flex;gap:.6rem;padding:.45rem 0;font-size:.85rem;color:var(--v3-text-2)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="16" height="16" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>We update content regularly to stay accurate.</li>
        </ul>
      </div>

      <div class="v3-card v3-card-padded">
        <h2 style="font-size:1.05rem;margin:0 0 .85rem">Our Review Principles</h2>
        <ul style="list-style:none;padding:0;margin:0">
          <li style="display:flex;gap:.6rem;padding:.45rem 0;font-size:.85rem;color:var(--v3-text-2)"><span style="color:var(--v3-red);font-size:1.1rem;line-height:1;flex-shrink:0">●</span>Be objective, not promotional.</li>
          <li style="display:flex;gap:.6rem;padding:.45rem 0;font-size:.85rem;color:var(--v3-text-2)"><span style="color:var(--v3-red);font-size:1.1rem;line-height:1;flex-shrink:0">●</span>Highlight pros, cons, and trade-offs.</li>
          <li style="display:flex;gap:.6rem;padding:.45rem 0;font-size:.85rem;color:var(--v3-text-2)"><span style="color:var(--v3-red);font-size:1.1rem;line-height:1;flex-shrink:0">●</span>Write for buyers, not vendors.</li>
          <li style="display:flex;gap:.6rem;padding:.45rem 0;font-size:.85rem;color:var(--v3-text-2)"><span style="color:var(--v3-red);font-size:1.1rem;line-height:1;flex-shrink:0">●</span>Share real-world context and use cases.</li>
        </ul>
      </div>

      <div class="v3-card v3-card-padded v3-card-emph">
        <div class="v3-card-icon" style="margin-bottom:.55rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h18v18H3z"/><path d="M9 12h6"/><path d="M12 9v6"/></svg></div>
        <h3 style="font-size:.95rem;margin:0 0 .5rem">Full Transparency</h3>
        <p style="font-size:.85rem;color:var(--v3-text-3);margin:0">If a page contains affiliate links, we'll always disclose it clearly. Questions? Email us at <a href="mailto:hello@saaspare.org" class="v3-link-cta" style="display:inline">hello@saaspare.org</a>.</p>
      </div>
    </div>
  </div>

  <div class="v3-card v3-card-padded" style="margin-top:1.5rem;text-align:center;background:linear-gradient(145deg,rgba(233,69,96,.08),rgba(255,255,255,.02));border-color:rgba(233,69,96,.22)">
    <p style="margin:0;font-size:.95rem;color:var(--v3-text-2)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-red)" stroke-width="2" width="18" height="18" style="display:inline;vertical-align:middle;margin-right:8px"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg><b style="color:#fff">SaaSpare is 100% independent.</b> &nbsp;No acquisitions. No investor influence. Just a mission to help teams buy better.</p>
  </div>
</div>

{FOOTER}
{fab()}
</body></html>
"""


# ─────────────────────────── 404 (Image 12) ──────────────────────
def page_404():
    head = head_html(
        "Page not found",
        "The page you're looking for doesn't exist or may have been moved.",
        f"{BASE}/pages/v3-preview-404",
    )
    return f"""{head}
{nav_html(active='')}

<section class="v3-hero" style="position:relative;overflow:hidden;padding-bottom:2rem">
  <div class="v3-matrix-bg" style="opacity:.5"></div>
  <div class="v3-container" style="position:relative;z-index:2;display:grid;grid-template-columns:1.1fr 1fr;gap:3rem;align-items:center;min-height:480px">
    <div>
      <span class="v3-eyebrow">Page not found</span>
      <div class="v3-404-num">404</div>
      <h1 style="font-size:clamp(1.6rem,3.2vw,2.4rem);margin:0 0 .85rem">Looks like this page<br>took a detour.</h1>
      <p class="v3-sub" style="margin:0 auto 0 0;text-align:left">The page you're looking for doesn't exist or may have been moved. Let's get you back on track.</p>
    </div>
    <div style="position:relative;text-align:center">
      <svg viewBox="0 0 320 320" style="width:100%;max-width:320px;margin:0 auto" aria-hidden="true">
        <defs><radialGradient id="g404" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#e94560" stop-opacity="0.4"/><stop offset="60%" stop-color="#e94560" stop-opacity="0.1"/><stop offset="100%" stop-color="#e94560" stop-opacity="0"/></radialGradient></defs>
        <circle cx="220" cy="170" r="85" fill="url(#g404)"/>
        <circle cx="220" cy="170" r="78" fill="none" stroke="#e94560" stroke-width="1.5" opacity="0.4"/>
        <circle cx="220" cy="170" r="45" fill="#1a0508" stroke="#e94560" stroke-width="1.5"/>
        <g transform="translate(60,140) rotate(-25 60 50)">
          <rect x="0" y="40" width="120" height="22" rx="4" fill="#1f1f2a" stroke="rgba(255,255,255,.18)" stroke-width="1"/>
          <rect x="-8" y="32" width="16" height="38" rx="3" fill="#0f0f18" stroke="rgba(255,255,255,.2)" stroke-width="1"/>
          <rect x="116" y="28" width="22" height="46" rx="3" fill="#0f0f18" stroke="#e94560" stroke-width="1.5"/>
          <circle cx="127" cy="51" r="6" fill="#e94560"/>
          <line x1="60" y1="62" x2="60" y2="115" stroke="rgba(255,255,255,.4)" stroke-width="2"/>
          <polygon points="40,140 80,140 60,115" fill="#1f1f2a" stroke="rgba(255,255,255,.18)" stroke-width="1"/>
        </g>
        <circle cx="50" cy="60" r="2" fill="#e94560" opacity="0.7"/>
        <circle cx="280" cy="80" r="1.5" fill="#fff" opacity="0.6"/>
        <circle cx="290" cy="240" r="2" fill="#e94560" opacity="0.5"/>
        <circle cx="80" cy="270" r="1.5" fill="#fff" opacity="0.5"/>
      </svg>
    </div>
  </div>
</section>

<div class="v3-container">
  <div class="v3-grid-3">
    <div class="v3-card">
      <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg></div>
      <h4 style="margin:.7rem 0 .3rem">Return Home</h4>
      <p style="font-size:.82rem;color:var(--v3-text-4);margin:0 0 .85rem;line-height:1.5">Go back to the homepage and start fresh.</p>
      <a href="/" class="v3-btn v3-btn-primary v3-btn-sm">Go Home →</a>
    </div>
    <div class="v3-card">
      <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg></div>
      <h4 style="margin:.7rem 0 .3rem">Browse Comparisons</h4>
      <p style="font-size:.82rem;color:var(--v3-text-4);margin:0 0 .85rem;line-height:1.5">Explore 1,000+ comparisons across top SaaS tools.</p>
      <a href="/pages/" class="v3-btn v3-btn-primary v3-btn-sm">Browse Library →</a>
    </div>
    <div class="v3-card">
      <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg></div>
      <h4 style="margin:.7rem 0 .3rem">See Top Picks</h4>
      <p style="font-size:.82rem;color:var(--v3-text-4);margin:0 0 .85rem;line-height:1.5">Check out our expert-recommended tools.</p>
      <a href="/shortlist" class="v3-btn v3-btn-primary v3-btn-sm">View Top Picks →</a>
    </div>
  </div>
  <p class="v3-help" style="text-align:center;margin-top:2rem">Still stuck? <a href="/contact" class="v3-link-cta" style="display:inline">Contact us</a> and we'll help.</p>
</div>

{FOOTER}
{fab()}
</body></html>
"""


PAGES = {
    "library": page_library,
    "privacy": page_privacy,
    "shortlist": page_shortlist,
    "affiliate-disclosure": page_affiliate,
    "404": page_404,
}

if __name__ == "__main__":
    written = 0
    for slug, builder in PAGES.items():
        path = OUT_DIR / f"v3-preview-{slug}.html"
        path.write_text(builder(), encoding="utf-8")
        size = path.stat().st_size
        print(f"  wrote {path.relative_to(ROOT)}  ({size:,} bytes)")
        written += 1
    print(f"\n{written} pages rebuilt.")
