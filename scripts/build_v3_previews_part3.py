"""Final batch of v3 previews — about, privacy, affiliate-disclosure, contact, 404, newsletter."""
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
# 07. ABOUT  — clones Image 3 row 1 + Image 7 panel 6
# ─────────────────────────────────────────────────────────────────────
def page_about() -> str:
    head = head_html(
        "About SaaSpare — Independent SaaS research",
        "SaaSpare is an independent research platform that helps businesses compare SaaS tools, understand pricing, and buy with confidence.",
        f"{BASE}/pages/v3-preview-about",
    )
    return f"""{head}
{nav_html(active='about')}

<section class="v3-hero left" style="padding-bottom:1.5rem">
  <div class="v3-container" style="display:grid;grid-template-columns:1.4fr 1fr;gap:3rem;align-items:center">
    <div>
      <span class="v3-eyebrow">About SaaSpare</span>
      <h1>We help teams find the<br><em>best SaaS decisions.</em></h1>
      <p class="v3-lede" style="margin:1rem 0 1.6rem;max-width:560px">SaaSpare is an independent research platform that helps businesses compare SaaS tools, understand pricing, and buy with confidence. No sales pitches. No hype. Just clarity.</p>
      <div class="v3-grid-4">
        <div class="v3-stat"><div class="num">1,150+</div><div class="lbl">Buyer pages researched</div></div>
        <div class="v3-stat"><div class="num">800+</div><div class="lbl">SaaS tools compared</div></div>
        <div class="v3-stat"><div class="num">34</div><div class="lbl">In-depth pricing guides</div></div>
        <div class="v3-stat"><div class="num">10,000+</div><div class="lbl">Teams making smarter decisions</div></div>
      </div>
      <div class="v3-row tight" style="margin-top:1.4rem">
        <span class="v3-trust-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>Last updated: May 10, 2026</span>
        <span class="v3-trust-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>Independent &amp; unbiased</span>
        <span class="v3-trust-pill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>No paid placements</span>
      </div>
    </div>
    <div class="v3-card v3-card-padded" style="position:relative;text-align:center;padding:2.4rem 1.6rem">
      <svg viewBox="0 0 200 200" style="width:100%;max-width:280px;height:auto;margin:0 auto" aria-hidden="true">
        <circle cx="100" cy="100" r="80" fill="none" stroke="rgba(233,69,96,.18)" stroke-width="1"/>
        <circle cx="100" cy="100" r="55" fill="none" stroke="rgba(233,69,96,.32)" stroke-width="1"/>
        <circle cx="100" cy="100" r="30" fill="rgba(233,69,96,.12)" stroke="var(--v3-red)" stroke-width="1.5"/>
        <text x="100" y="106" text-anchor="middle" font-family="Plus Jakarta Sans" font-weight="850" font-size="22" fill="#fff">S</text>
        <circle cx="40" cy="60" r="14" fill="rgba(233,69,96,.18)"/><text x="40" y="65" text-anchor="middle" font-size="11" fill="#fff">📦</text>
        <circle cx="160" cy="50" r="14" fill="rgba(233,69,96,.18)"/><text x="160" y="55" text-anchor="middle" font-size="11" fill="#fff">📊</text>
        <circle cx="170" cy="130" r="14" fill="rgba(233,69,96,.18)"/><text x="170" y="135" text-anchor="middle" font-size="11" fill="#fff">💡</text>
        <circle cx="50" cy="150" r="14" fill="rgba(233,69,96,.18)"/><text x="50" y="155" text-anchor="middle" font-size="11" fill="#fff">⚡</text>
      </svg>
      <h3 style="font-size:1rem;margin:1.2rem 0 .35rem">Clarity in a crowded market.</h3>
      <p style="font-size:.85rem;color:var(--v3-text-4);margin:0;line-height:1.6">SaaS is noisy. Features overlap. Pricing is confusing. We cut through the noise so you can focus on what matters — impact.</p>
    </div>
  </div>
</section>

<section class="v3-section">
  <div class="v3-container">
    <h2 style="margin-bottom:1.4rem">How we help</h2>
    <div class="v3-grid-4">
      <div class="v3-card">
        <div class="v3-row tight" style="margin-bottom:.65rem"><span style="display:grid;place-items:center;width:28px;height:28px;border-radius:8px;background:var(--v3-red-soft);color:var(--v3-red-light);font-weight:850;font-size:.8rem">1</span><h4 style="margin:0;font-size:.95rem">Research</h4></div>
        <p style="font-size:.85rem;color:var(--v3-text-4);margin:0;line-height:1.55">We analyse pricing pages, docs, reviews, and real buyer feedback.</p>
      </div>
      <div class="v3-card">
        <div class="v3-row tight" style="margin-bottom:.65rem"><span style="display:grid;place-items:center;width:28px;height:28px;border-radius:8px;background:var(--v3-red-soft);color:var(--v3-red-light);font-weight:850;font-size:.8rem">2</span><h4 style="margin:0;font-size:.95rem">Compare</h4></div>
        <p style="font-size:.85rem;color:var(--v3-text-4);margin:0;line-height:1.55">We normalise features, pricing, and terms side-by-side.</p>
      </div>
      <div class="v3-card">
        <div class="v3-row tight" style="margin-bottom:.65rem"><span style="display:grid;place-items:center;width:28px;height:28px;border-radius:8px;background:var(--v3-red-soft);color:var(--v3-red-light);font-weight:850;font-size:.8rem">3</span><h4 style="margin:0;font-size:.95rem">Explain</h4></div>
        <p style="font-size:.85rem;color:var(--v3-text-4);margin:0;line-height:1.55">We write clear, actionable guides without vendor jargon.</p>
      </div>
      <div class="v3-card">
        <div class="v3-row tight" style="margin-bottom:.65rem"><span style="display:grid;place-items:center;width:28px;height:28px;border-radius:8px;background:var(--v3-red-soft);color:var(--v3-red-light);font-weight:850;font-size:.8rem">4</span><h4 style="margin:0;font-size:.95rem">Empower</h4></div>
        <p style="font-size:.85rem;color:var(--v3-text-4);margin:0;line-height:1.55">You make a confident call your team will thank you for.</p>
      </div>
    </div>
  </div>
</section>

<section class="v3-section">
  <div class="v3-container">
    <div class="v3-card v3-card-emph v3-card-padded" style="text-align:center">
      <h2 style="margin:0 0 .55rem">Our mission</h2>
      <p style="font-size:1.05rem;color:var(--v3-text-2);max-width:680px;margin:0 auto;line-height:1.7">SaaSpare was built to solve a simple problem: buying SaaS is hard. Pricing is confusing, features lock you in, and vendor claims fall to the floor. We do the research so you don't have to.</p>
      <div class="v3-row center tight" style="margin-top:1.2rem;gap:1.5rem;flex-wrap:wrap">
        <span style="font-size:.9rem;color:var(--v3-text-3)">✓ Real pricing, no fluff</span>
        <span style="font-size:.9rem;color:var(--v3-text-3)">✓ Honest comparisons</span>
        <span style="font-size:.9rem;color:var(--v3-text-3)">✓ Hidden fees uncovered</span>
        <span style="font-size:.9rem;color:var(--v3-text-3)">✓ Better decisions, faster</span>
      </div>
    </div>
  </div>
</section>

{FOOTER}
{fab()}
</body></html>
"""


# ─────────────────────────────────────────────────────────────────────
# 08. PRIVACY  — clones Image 3 row 2
# ─────────────────────────────────────────────────────────────────────
def page_privacy() -> str:
    head = head_html(
        "Privacy Policy",
        "SaaSpare's privacy policy explains what information we collect, how we use it, and the choices you have.",
        f"{BASE}/pages/v3-preview-privacy",
    )
    return f"""{head}
{nav_html(active='')}

<div class="v3-container" style="padding-top:5.5rem"><div class="v3-crumbs"><a href="/">Home</a><span>/</span><span>Privacy Policy</span></div></div>

<div class="v3-layout-filters" style="grid-template-columns:240px minmax(0,1fr)">
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

  <main>
    <div style="text-align:center;margin-bottom:1.5rem"><span class="v3-eyebrow">Privacy Policy</span></div>
    <h1 style="text-align:center">Privacy <em>Policy</em></h1>
    <p class="v3-help" style="text-align:center;margin:.4rem 0 1.5rem">Last updated: May 10, 2026</p>
    <p class="v3-lede" style="text-align:center;max-width:600px;margin:0 auto 2.5rem">At SaaSpare, your privacy matters. This policy explains what information we collect, how we use it, and the choices you have.</p>

    <h2 id="intro">1. Introduction</h2>
    <p>SaaSpare ("we", "our", or "us") operates the website saaspare.org (the "Site"). This Privacy Policy describes how we collect, use, disclose, and safeguard your information when you visit our Site.</p>
    <div class="v3-grid-3" style="margin:1.4rem 0 2rem">
      <div class="v3-card">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></div>
        <p style="font-size:.85rem;margin:.65rem 0 0;color:var(--v3-text-3);line-height:1.55"><b style="color:#fff">We don't sell your personal information.</b></p>
      </div>
      <div class="v3-card">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg></div>
        <p style="font-size:.85rem;margin:.65rem 0 0;color:var(--v3-text-3);line-height:1.55"><b style="color:#fff">We use data to improve content and user experience.</b></p>
      </div>
      <div class="v3-card">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></div>
        <p style="font-size:.85rem;margin:.65rem 0 0;color:var(--v3-text-3);line-height:1.55"><b style="color:#fff">You're in control of your privacy choices.</b></p>
      </div>
    </div>

    <h2 id="info-collect">2. Information We Collect</h2>
    <p>We collect information you provide directly, information automatically collected, and information from third parties.</p>
    <h3>a) Information you provide</h3>
    <p>When you sign up for our newsletter, contact us, or submit a comparison request, we collect your name, email address, and any details you choose to share.</p>
    <h3>b) Information collected automatically</h3>
    <p>We collect device, browser, IP address, referrer, and pages visited via cookies and similar technologies — used to improve site performance and personalise content.</p>

    <h2 id="how-we-use">3. How We Use Information</h2>
    <ul>
      <li>To provide and improve our services</li>
      <li>To communicate with you</li>
      <li>To analyse site usage</li>
      <li>To prevent fraud and abuse</li>
    </ul>

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


# ─────────────────────────────────────────────────────────────────────
# 09. AFFILIATE DISCLOSURE  — clones Image 2 + Image 3 row 3
# ─────────────────────────────────────────────────────────────────────
def page_affiliate() -> str:
    head = head_html(
        "Affiliate Disclosure & Editorial Standards",
        "How SaaSpare earns money and stays unbiased. Full FTC disclosure and our editorial standards.",
        f"{BASE}/pages/v3-preview-affiliate-disclosure",
    )
    return f"""{head}
{nav_html(active='')}

<section class="v3-hero">
  <div class="v3-hero-inner" style="max-width:780px">
    <span class="v3-eyebrow">Our commitment</span>
    <h1>Independent. Transparent. Trusted.<br><em>Here's how SaaSpare works.</em></h1>
    <p class="v3-sub">SaaSpare may earn a commission when you click certain links and complete a qualifying action. This page explains exactly how that works — and why our verdicts are never for sale.</p>
  </div>
</section>

<div class="v3-container">
  <div class="v3-grid-2" style="gap:1.5rem">
    <div class="v3-card v3-card-padded">
      <h2 style="font-size:1.2rem">How SaaSpare Makes Money</h2>
      <p style="margin:0 0 1.2rem;color:var(--v3-text-3);font-size:.92rem">We earn commissions when you purchase through links on our site. These partnerships help us keep our content free.</p>
      <div class="v3-grid-3">
        <div class="v3-card-flat" style="padding:1rem"><div class="v3-card-icon" style="margin-bottom:.55rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div><b style="font-size:.85rem">You pay the same price</b><p style="font-size:.78rem;color:var(--v3-text-4);margin:.3rem 0 0">Our links never change your cost.</p></div>
        <div class="v3-card-flat" style="padding:1rem"><div class="v3-card-icon" style="margin-bottom:.55rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg></div><b style="font-size:.85rem">We may earn a commission</b><p style="font-size:.78rem;color:var(--v3-text-4);margin:.3rem 0 0">From qualifying purchases at no extra cost to you.</p></div>
        <div class="v3-card-flat" style="padding:1rem"><div class="v3-card-icon" style="margin-bottom:.55rem"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div><b style="font-size:.85rem">It helps us stay independent</b><p style="font-size:.78rem;color:var(--v3-text-4);margin:.3rem 0 0">So we can keep researching and publishing.</p></div>
      </div>
    </div>

    <div class="v3-card v3-card-padded">
      <h2 style="font-size:1.2rem">Our Editorial Standards</h2>
      <ul style="list-style:none;padding:0;margin:1rem 0 0">
        <li style="display:flex;gap:.6rem;padding:.55rem 0;font-size:.9rem;color:var(--v3-text-2)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="18" height="18" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>We do independent research and testing when possible.</li>
        <li style="display:flex;gap:.6rem;padding:.55rem 0;font-size:.9rem;color:var(--v3-text-2)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="18" height="18" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>We verify pricing and details directly from official sources.</li>
        <li style="display:flex;gap:.6rem;padding:.55rem 0;font-size:.9rem;color:var(--v3-text-2)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="18" height="18" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>We don't accept payment for positive coverage.</li>
        <li style="display:flex;gap:.6rem;padding:.55rem 0;font-size:.9rem;color:var(--v3-text-2)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="18" height="18" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>We update content regularly to stay accurate.</li>
      </ul>
    </div>

    <div class="v3-card v3-card-padded">
      <h2 style="font-size:1.2rem">How Our Rankings Work</h2>
      <p style="font-size:.92rem;color:var(--v3-text-3);margin:0 0 1rem">Our rankings are based on a 100-point framework across five pillars.</p>
      <div class="v3-grid-4" style="grid-template-columns:repeat(5,1fr);gap:.6rem">
        <div class="v3-card-flat" style="padding:.8rem .6rem;text-align:center"><div style="font-size:.65rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.5px;margin-bottom:.3rem">Pricing</div><b style="font-size:1.1rem">25 pts</b></div>
        <div class="v3-card-flat" style="padding:.8rem .6rem;text-align:center"><div style="font-size:.65rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.5px;margin-bottom:.3rem">Features</div><b style="font-size:1.1rem">25 pts</b></div>
        <div class="v3-card-flat" style="padding:.8rem .6rem;text-align:center"><div style="font-size:.65rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.5px;margin-bottom:.3rem">Ease of Use</div><b style="font-size:1.1rem">20 pts</b></div>
        <div class="v3-card-flat" style="padding:.8rem .6rem;text-align:center"><div style="font-size:.65rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.5px;margin-bottom:.3rem">Integrations</div><b style="font-size:1.1rem">15 pts</b></div>
        <div class="v3-card-flat" style="padding:.8rem .6rem;text-align:center"><div style="font-size:.65rem;color:var(--v3-text-4);text-transform:uppercase;letter-spacing:.5px;margin-bottom:.3rem">Support</div><b style="font-size:1.1rem">15 pts</b></div>
      </div>
      <p style="margin:1rem 0 0;font-size:.82rem;color:var(--v3-good);text-align:center">✓ No vendor can pay to rank higher. Ever.</p>
    </div>

    <div class="v3-card v3-card-padded">
      <h2 style="font-size:1.2rem">Our Review Principles</h2>
      <ul style="list-style:none;padding:0;margin:1rem 0 0">
        <li style="display:flex;gap:.6rem;padding:.55rem 0;font-size:.9rem;color:var(--v3-text-2)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="18" height="18" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>Be objective, not promotional.</li>
        <li style="display:flex;gap:.6rem;padding:.55rem 0;font-size:.9rem;color:var(--v3-text-2)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="18" height="18" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>Highlight pros, cons, and trade-offs.</li>
        <li style="display:flex;gap:.6rem;padding:.55rem 0;font-size:.9rem;color:var(--v3-text-2)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="18" height="18" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>Write for buyers, not vendors.</li>
        <li style="display:flex;gap:.6rem;padding:.55rem 0;font-size:.9rem;color:var(--v3-text-2)"><svg viewBox="0 0 24 24" fill="none" stroke="var(--v3-good)" stroke-width="2.5" width="18" height="18" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>Share real-world context and use cases.</li>
      </ul>
    </div>
  </div>

  <div class="v3-card v3-card-emph v3-card-padded" style="margin-top:1.5rem;text-align:center">
    <h2 style="margin:0 0 .55rem;font-size:1.2rem">Full Transparency</h2>
    <p style="font-size:.92rem;color:var(--v3-text-3);margin:0 0 1rem;max-width:580px;margin-left:auto;margin-right:auto">If a page contains affiliate links, we'll always disclose it clearly. Questions? Email us at <a href="mailto:hello@saaspare.org" class="v3-link-cta" style="display:inline">hello@saaspare.org</a>.</p>
    <p style="font-size:.85rem;color:var(--v3-good);margin:0">● <b>SaaSpare is 100% independent.</b> No acquisitions. No investor influence. Just a mission to help teams buy better.</p>
  </div>

  <div class="v3-card v3-card-padded" style="margin-top:1.5rem">
    <h3 style="font-size:1rem;margin:0 0 .85rem;color:var(--v3-red-light);text-transform:uppercase;letter-spacing:.5px">Required FTC disclosure</h3>
    <p style="font-size:.92rem;color:var(--v3-text-2);margin:0 0 1rem;line-height:1.7">SaaSpare participates in affiliate programmes run by software vendors and affiliate networks including Commission Junction (CJ Affiliate), PartnerStack, Impact.com, and direct vendor programmes. When you click a link marked with an affiliate tag (typically routing through <code>/go/[vendor]</code>) and complete a qualifying action — such as starting a free trial, signing up for a paid plan, or making a purchase — SaaSpare may receive a commission from the vendor.</p>
    <p style="font-size:.92rem;color:var(--v3-text-2);margin:0 0 1rem;line-height:1.7"><b>This commission comes from the vendor's marketing budget, not from you.</b> Affiliate links do not add any cost to your purchase or trial sign-up. The price you pay is identical to going directly to the vendor website.</p>
    <p style="font-size:.92rem;color:var(--v3-text-2);margin:0;line-height:1.7">This disclosure is made in compliance with FTC guidelines on endorsements and testimonials (16 CFR Part 255), and equivalent guidelines in other jurisdictions where SaaSpare operates.</p>
  </div>
</div>

{FOOTER}
{fab()}
</body></html>
"""


# ─────────────────────────────────────────────────────────────────────
# 10. CONTACT  — clones Image 1 row 1 + Image 7 panel 9
# ─────────────────────────────────────────────────────────────────────
def page_contact() -> str:
    head = head_html(
        "Contact SaaSpare — Partnerships, support &amp; corrections",
        "Contact SaaSpare for partnership ideas, pricing corrections, or general questions. Our team responds within one business day.",
        f"{BASE}/pages/v3-preview-contact",
    )
    return f"""{head}
{nav_html(active='')}

<section class="v3-hero left" style="padding-bottom:1rem">
  <div class="v3-container">
    <span class="v3-eyebrow">We'd love to hear from you</span>
    <h1>Let's build smarter<br>SaaS decisions—<em>together.</em></h1>
    <p class="v3-lede" style="margin:1rem 0 0;max-width:600px">Have a question, partnership idea, or feedback? Our team typically responds within one business day.</p>
  </div>
</section>

<div class="v3-container">
  <div class="v3-grid-3" style="grid-template-columns:1.1fr 1.4fr 1fr;gap:1.4rem">
    <div>
      <a href="mailto:hello@saaspare.org" class="v3-card" style="display:block;margin-bottom:.7rem"><div class="v3-row" style="gap:.85rem;align-items:center"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg></div><div style="flex:1"><b style="font-size:.95rem">Email Us</b><p style="font-size:.78rem;color:var(--v3-red-light);margin:.15rem 0 .15rem">hello@saaspare.org</p><p style="font-size:.74rem;color:var(--v3-text-5);margin:0">For general inquiries and support</p></div><span style="color:var(--v3-text-5)">›</span></div></a>
      <a href="mailto:partners@saaspare.org" class="v3-card" style="display:block;margin-bottom:.7rem"><div class="v3-row" style="gap:.85rem;align-items:center"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/></svg></div><div style="flex:1"><b style="font-size:.95rem">Partnerships</b><p style="font-size:.78rem;color:var(--v3-red-light);margin:.15rem 0 .15rem">partners@saaspare.org</p><p style="font-size:.74rem;color:var(--v3-text-5);margin:0">For media, affiliates, and integrations</p></div><span style="color:var(--v3-text-5)">›</span></div></a>
      <a href="mailto:press@saaspare.org" class="v3-card" style="display:block;margin-bottom:.7rem"><div class="v3-row" style="gap:.85rem;align-items:center"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg></div><div style="flex:1"><b style="font-size:.95rem">Press &amp; Media</b><p style="font-size:.78rem;color:var(--v3-red-light);margin:.15rem 0 .15rem">press@saaspare.org</p><p style="font-size:.74rem;color:var(--v3-text-5);margin:0">For press inquiries and media</p></div><span style="color:var(--v3-text-5)">›</span></div></a>
      <a href="#" class="v3-card" style="display:block;margin-bottom:.7rem"><div class="v3-row" style="gap:.85rem;align-items:center"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg></div><div style="flex:1"><b style="font-size:.95rem">Business Inquiries</b><p style="font-size:.78rem;color:var(--v3-red-light);margin:.15rem 0 .15rem">(415) 555-0118</p><p style="font-size:.74rem;color:var(--v3-text-5);margin:0">Mon–Fri, 9am–6pm PT</p></div><span style="color:var(--v3-text-5)">›</span></div></a>
      <a href="#" class="v3-card v3-card-emph" style="display:block;margin-top:.85rem"><div class="v3-row" style="gap:.85rem;align-items:center"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg></div><div style="flex:1"><b style="font-size:.95rem">Partner with SaaSpare</b><p style="font-size:.78rem;color:var(--v3-text-3);margin:.15rem 0 0">Join leading tools and platforms collaborating to help teams make confident SaaS buying decisions.</p></div><span class="v3-link-cta" style="font-size:.78rem">Explore →</span></div></a>
    </div>

    <div class="v3-card v3-card-padded">
      <h2 style="font-size:1.2rem;margin:0 0 .35rem">Send us a message</h2>
      <p class="v3-muted" style="margin:0 0 1.4rem;font-size:.86rem">Fill out the form and we'll get back to you soon.</p>
      <form>
        <label class="v3-label">Full name</label>
        <input class="v3-input" type="text" placeholder="Jane Doe">
        <label class="v3-label" style="margin-top:.85rem">Work email</label>
        <input class="v3-input" type="email" placeholder="jane@acme.com">
        <label class="v3-label" style="margin-top:.85rem">Company (optional)</label>
        <input class="v3-input" type="text" placeholder="Acme Inc.">
        <label class="v3-label" style="margin-top:.85rem">How can we help?</label>
        <textarea class="v3-textarea" rows="5" placeholder="Tell us more about your question or request…"></textarea>
        <button type="submit" class="v3-btn v3-btn-primary v3-btn-lg" style="width:100%;margin-top:1.2rem">Send Message →</button>
        <p class="v3-help" style="margin-top:.6rem;text-align:center">✓ We respect your privacy. See our <a href="/privacy" style="color:var(--v3-red-light)">Privacy Policy</a>.</p>
      </form>
    </div>

    <div>
      <div class="v3-card v3-card-padded" style="margin-bottom:.85rem">
        <h3 style="font-size:.95rem;margin:0 0 1rem">What to expect</h3>
        <div class="v3-row" style="gap:.7rem;align-items:flex-start;margin-bottom:.85rem"><span style="display:grid;place-items:center;width:26px;height:26px;border-radius:50%;background:var(--v3-red-soft);color:var(--v3-red-light);font-weight:850;font-size:.75rem;flex-shrink:0">1</span><div><b style="font-size:.85rem">Quick reply</b><p style="font-size:.76rem;color:var(--v3-text-4);margin:.2rem 0 0;line-height:1.5">We aim to respond within one business day.</p></div></div>
        <div class="v3-row" style="gap:.7rem;align-items:flex-start;margin-bottom:.85rem"><span style="display:grid;place-items:center;width:26px;height:26px;border-radius:50%;background:var(--v3-red-soft);color:var(--v3-red-light);font-weight:850;font-size:.75rem;flex-shrink:0">2</span><div><b style="font-size:.85rem">Helpful answers</b><p style="font-size:.76rem;color:var(--v3-text-4);margin:.2rem 0 0;line-height:1.5">Our experts provide clear, actionable info.</p></div></div>
        <div class="v3-row" style="gap:.7rem;align-items:flex-start"><span style="display:grid;place-items:center;width:26px;height:26px;border-radius:50%;background:var(--v3-red-soft);color:var(--v3-red-light);font-weight:850;font-size:.75rem;flex-shrink:0">3</span><div><b style="font-size:.85rem">No spam, ever</b><p style="font-size:.76rem;color:var(--v3-text-4);margin:.2rem 0 0;line-height:1.5">We only email you when it matters.</p></div></div>
      </div>
      <div class="v3-card v3-card-padded">
        <h3 style="font-size:.95rem;margin:0 0 .85rem">Trusted by teams at</h3>
        <div style="display:flex;flex-direction:column;gap:.6rem;font-size:.82rem;color:var(--v3-text-2);font-weight:700">
          <div>Notion</div><div>HubSpot</div><div>Dropbox</div><div>monday.com</div><div>Zoom</div>
        </div>
      </div>
    </div>
  </div>
</div>

{FOOTER}
{fab()}
</body></html>
"""


# ─────────────────────────────────────────────────────────────────────
# 11. 404 — clones Image 1 row 3 + Image 7 panel 10
# ─────────────────────────────────────────────────────────────────────
def page_404() -> str:
    head = head_html(
        "Page not found",
        "The page you're looking for doesn't exist or may have been moved. Let's get you back on track.",
        f"{BASE}/pages/v3-preview-404",
    )
    return f"""{head}
{nav_html(active='')}

<section class="v3-hero">
  <div class="v3-hero-inner" style="max-width:720px">
    <span class="v3-eyebrow">Page not found</span>
    <div style="font-family:var(--v3-ff-display);font-size:clamp(6rem,15vw,9rem);font-weight:900;background:linear-gradient(135deg,#ff7890 0%,#e94560 50%,#c73652 100%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;line-height:1;margin:1rem 0;animation:v3Glint 7s linear infinite;background-size:220% 100%">404</div>
    <h1 style="font-size:clamp(1.5rem,3.4vw,2.2rem);margin:0 0 .85rem">Looks like this page took a detour.</h1>
    <p class="v3-sub">The page you're looking for doesn't exist or may have been moved. Let's get you back on track.</p>
    <div class="v3-grid-3" style="margin-top:2rem">
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
        <a href="/pages/" class="v3-btn v3-btn-secondary v3-btn-sm">Browse Library →</a>
      </div>
      <div class="v3-card">
        <div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg></div>
        <h4 style="margin:.7rem 0 .3rem">See Top Picks</h4>
        <p style="font-size:.82rem;color:var(--v3-text-4);margin:0 0 .85rem;line-height:1.5">Check out our expert-recommended tools.</p>
        <a href="/shortlist" class="v3-btn v3-btn-secondary v3-btn-sm">View Top Picks →</a>
      </div>
    </div>
    <p class="v3-help" style="margin-top:2rem">Still stuck? <a href="/contact" class="v3-link-cta" style="display:inline">Contact us</a> and we'll help.</p>
  </div>
</section>

{FOOTER}
{fab()}
</body></html>
"""


# ─────────────────────────────────────────────────────────────────────
# 12. NEWSLETTER — clones Image 1 row 2 + Image 7 panel 11
# ─────────────────────────────────────────────────────────────────────
def page_newsletter() -> str:
    head = head_html(
        "SaaSpare Newsletter — Insider SaaS insights weekly",
        "Join 16,000+ SaaS buyers. Get unbiased comparisons, pricing updates, and exclusive deals delivered weekly.",
        f"{BASE}/pages/v3-preview-newsletter",
    )
    return f"""{head}
{nav_html(active='')}

<section class="v3-hero">
  <div class="v3-hero-inner" style="max-width:780px">
    <div class="v3-trust-avatars" style="margin-bottom:1.2rem">
      <span class="v3-avatars">
        <span style="background:#9b6dff"></span><span style="background:#34d399"></span><span style="background:#ffc864"></span><span style="background:#74a9ff"></span><span style="background:#e94560"></span>
      </span>
      <span>Join <b>16,000+</b> SaaS buyers</span>
    </div>
    <h1>Insider insights.<br>Smarter <em>SaaS decisions.</em></h1>
    <p class="v3-sub">Join our newsletter for best-in-class comparisons, pricing updates, buyer guides, and exclusive deals — delivered weekly.</p>
    <div class="v3-search" style="margin-top:1.4rem">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" style="color:rgba(255,255,255,.32)"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
      <input type="email" placeholder="Enter your work email">
      <button>Subscribe Free →</button>
    </div>
    <div class="v3-row center tight" style="margin-top:1.2rem;gap:1.5rem;flex-wrap:wrap;color:var(--v3-text-4);font-size:.78rem">
      <span>✓ No spam.</span><span>✓ Unsubscribe anytime.</span><span>✓ Written by real buyers.</span>
    </div>
  </div>
</section>

<div class="v3-container">
  <div class="v3-grid-2" style="grid-template-columns:1fr 1.6fr;gap:2rem;align-items:flex-start">
    <div>
      <h2 style="font-size:1.2rem;margin:0 0 1.2rem">Why subscribe?</h2>
      <div class="v3-card" style="margin-bottom:.7rem"><div class="v3-row" style="gap:.85rem"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg></div><div><b style="font-size:.92rem">Unbiased comparisons</b><p style="font-size:.78rem;color:var(--v3-text-4);margin:.25rem 0 0;line-height:1.5">Side-by-side breakdowns you can trust.</p></div></div></div>
      <div class="v3-card" style="margin-bottom:.7rem"><div class="v3-row" style="gap:.85rem"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div><div><b style="font-size:.92rem">Pricing updates</b><p style="font-size:.78rem;color:var(--v3-text-4);margin:.25rem 0 0;line-height:1.5">We track changes so you don't have to.</p></div></div></div>
      <div class="v3-card" style="margin-bottom:.7rem"><div class="v3-row" style="gap:.85rem"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg></div><div><b style="font-size:.92rem">Expert buyer guides</b><p style="font-size:.78rem;color:var(--v3-text-4);margin:.25rem 0 0;line-height:1.5">Actionable advice for every team and budget.</p></div></div></div>
      <div class="v3-card"><div class="v3-row" style="gap:.85rem"><div class="v3-card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg></div><div><b style="font-size:.92rem">Exclusive deals</b><p style="font-size:.78rem;color:var(--v3-text-4);margin:.25rem 0 0;line-height:1.5">Subscriber-only discounts on top SaaS tools.</p></div></div></div>
    </div>

    <div>
      <h2 style="font-size:1.2rem;margin:0 0 1.2rem">Loved by SaaS buyers</h2>
      <div class="v3-grid-3">
        <div class="v3-card"><p style="font-size:.85rem;color:var(--v3-text-2);margin:0 0 1rem;line-height:1.6">"SaaSpare saves me hours of research every month."</p><div class="v3-row tight"><div class="v3-tool-logo" style="width:36px;height:36px;background:#9b6dff;font-size:.8rem">A</div><div><b style="font-size:.82rem">Alex R.</b><br><small style="color:var(--v3-text-5);font-size:.7rem">Head of Ops</small></div></div></div>
        <div class="v3-card"><p style="font-size:.85rem;color:var(--v3-text-2);margin:0 0 1rem;line-height:1.6">"The pricing alerts and guides are insanely helpful."</p><div class="v3-row tight"><div class="v3-tool-logo" style="width:36px;height:36px;background:#34d399;font-size:.8rem">P</div><div><b style="font-size:.82rem">Priya S.</b><br><small style="color:var(--v3-text-5);font-size:.7rem">Growth Lead</small></div></div></div>
        <div class="v3-card"><p style="font-size:.85rem;color:var(--v3-text-2);margin:0 0 1rem;line-height:1.6">"Finally, unbiased info without the fluff."</p><div class="v3-row tight"><div class="v3-tool-logo" style="width:36px;height:36px;background:#ffc864;color:#000;font-size:.8rem">M</div><div><b style="font-size:.82rem">Mark T.</b><br><small style="color:var(--v3-text-5);font-size:.7rem">IT Manager</small></div></div></div>
      </div>

      <div class="v3-card v3-card-emph v3-card-padded" style="margin-top:1.4rem">
        <span class="v3-trust-pill" style="margin-bottom:.85rem">Latest issue · May 10, 2026</span>
        <h3 style="font-size:1.1rem;margin:0 0 .55rem">Top 10 CRM Tools Compared (2026)</h3>
        <div class="v3-row tight" style="margin:0 0 .85rem;font-size:.8rem;color:var(--v3-text-3)">
          <span>✓ Real pricing and hidden fees</span>
          <span>✓ Best for small teams</span>
          <span>✓ Enterprise-ready options</span>
        </div>
        <a href="#" class="v3-btn v3-btn-primary">Read Latest Issue →</a>
      </div>
    </div>
  </div>

  <div class="v3-card v3-card-padded" style="margin-top:2rem;text-align:center">
    <p class="v3-muted" style="font-size:.78rem;text-transform:uppercase;letter-spacing:.6px;margin:0 0 .85rem">Featured in</p>
    <div class="v3-row center" style="gap:2.5rem;flex-wrap:wrap;color:var(--v3-text-4);font-weight:800;font-size:1rem">
      <span>📰 TechCrunch</span><span>🎯 Capterra</span><span>🚀 Product Hunt</span><span>📨 SaaS Weekly</span><span>📊 FOUNDR</span>
    </div>
  </div>
</div>

{FOOTER}
{fab()}
</body></html>
"""


PAGES = {
    "about": page_about,
    "privacy": page_privacy,
    "affiliate-disclosure": page_affiliate,
    "contact": page_contact,
    "404": page_404,
    "newsletter": page_newsletter,
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
