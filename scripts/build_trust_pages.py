"""Build missing trust stack pages required for PartnerStack / affiliate network approvals.
Pages: cookie-policy, dmca, accessibility, advertise (partner page).
"""
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"

NAV = '''<nav id="sp-nav" style="position:fixed;top:0;left:0;right:0;z-index:200;padding:.9rem 2rem;display:flex;align-items:center;gap:6px;background:transparent;border-bottom:none;transition:all .3s ease;">
    <a href="/" style="display:flex;align-items:center;gap:9px;margin-right:auto;text-decoration:none;">
      <svg style="height:26px;width:auto;flex-shrink:0;overflow:visible" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs><clipPath id="ct"><path d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></clipPath><clipPath id="cb"><path d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/></clipPath></defs><path fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/><path fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></svg>
      <span style="font-weight:800;font-size:1.05rem;letter-spacing:-.4px;color:#fff">Saa<em style="color:#e94560;font-style:normal">Spare</em></span>
    </a>
    <a href="/pages/" style="color:rgba(255,248,245,.42);font-size:.8rem;padding:.38rem .82rem;border-radius:8px;font-weight:500;text-decoration:none;white-space:nowrap;">Comparisons</a>
    <a href="/deal-radar" style="color:rgba(255,248,245,.42);font-size:.8rem;padding:.38rem .82rem;border-radius:8px;font-weight:500;text-decoration:none;white-space:nowrap;">Deal Radar</a>
    <a href="/about" style="color:rgba(255,248,245,.42);font-size:.8rem;padding:.38rem .82rem;border-radius:8px;font-weight:500;text-decoration:none;white-space:nowrap;">About</a>
    <a href="/shortlist" style="background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.44rem 1.15rem;border-radius:100px;font-weight:700;font-size:.78rem;box-shadow:0 4px 16px rgba(233,69,96,.4);margin-left:6px;text-decoration:none;white-space:nowrap;">Shortlist Builder &#8594;</a>
  </nav>
  <script>
    (function(){var n=document.getElementById('sp-nav');if(!n)return;window.addEventListener('scroll',function(){if(window.scrollY>40){n.style.background='rgba(7,7,13,.85)';n.style.borderBottom='1px solid rgba(255,255,255,.07)';n.style.backdropFilter='blur(20px)';}else{n.style.background='transparent';n.style.borderBottom='none';n.style.backdropFilter='none';}},{passive:true});})();
  </script>'''

FOOTER = '''<footer style="background:rgba(255,255,255,.02);border-top:1px solid rgba(255,255,255,.07);padding:3rem 2rem;margin-top:6rem;text-align:center;font-size:.8rem;color:rgba(255,248,245,.35);">
  <div style="max-width:900px;margin:0 auto;">
    <div style="display:flex;flex-wrap:wrap;gap:1rem;justify-content:center;margin-bottom:1.5rem;">
      <a href="/about" style="color:rgba(255,248,245,.5);text-decoration:none;transition:color .15s" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='rgba(255,248,245,.5)'">About</a>
      <a href="/contact" style="color:rgba(255,248,245,.5);text-decoration:none;transition:color .15s" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='rgba(255,248,245,.5)'">Contact</a>
      <a href="/privacy" style="color:rgba(255,248,245,.5);text-decoration:none;transition:color .15s" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='rgba(255,248,245,.5)'">Privacy Policy</a>
      <a href="/terms" style="color:rgba(255,248,245,.5);text-decoration:none;transition:color .15s" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='rgba(255,248,245,.5)'">Terms</a>
      <a href="/cookie-policy" style="color:rgba(255,248,245,.5);text-decoration:none;transition:color .15s" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='rgba(255,248,245,.5)'">Cookie Policy</a>
      <a href="/affiliate-disclosure" style="color:rgba(255,248,245,.5);text-decoration:none;transition:color .15s" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='rgba(255,248,245,.5)'">Affiliate Disclosure</a>
      <a href="/editorial-policy" style="color:rgba(255,248,245,.5);text-decoration:none;transition:color .15s" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='rgba(255,248,245,.5)'">Editorial Policy</a>
      <a href="/methodology" style="color:rgba(255,248,245,.5);text-decoration:none;transition:color .15s" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='rgba(255,248,245,.5)'">Methodology</a>
      <a href="/dmca" style="color:rgba(255,248,245,.5);text-decoration:none;transition:color .15s" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='rgba(255,248,245,.5)'">DMCA</a>
      <a href="/accessibility" style="color:rgba(255,248,245,.5);text-decoration:none;transition:color .15s" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='rgba(255,248,245,.5)'">Accessibility</a>
      <a href="/advertise" style="color:rgba(255,248,245,.5);text-decoration:none;transition:color .15s" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='rgba(255,248,245,.5)'">Advertise</a>
    </div>
    <p style="margin-bottom:.5rem">SaaSpare is operated by Kaylan von Papen (ABN 20 602 197 525) &mdash; Queensland, Australia.</p>
    <p>&copy; 2026 SaaSpare. Independent research. No paid rankings. Made for buyers.</p>
  </div>
</footer>'''

HEAD_COMMON = '''  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-RLYVYV8WQJ');</script>
  <link rel="stylesheet" href="/assets/saaspare-v2.css">
  <link rel="stylesheet" href="/assets/saaspare-ui.css">
  <link rel="stylesheet" href="/assets/motion.css">
  <style>
    .trust-content{max-width:820px;margin:0 auto;padding:7rem 1.5rem 3rem;}
    .trust-hero{text-align:center;margin-bottom:3.5rem;}
    .trust-hero h1{font-size:clamp(1.8rem,4vw,2.8rem);font-weight:900;letter-spacing:-.04em;margin-bottom:1rem;line-height:1.1;}
    .trust-hero p{font-size:1rem;color:rgba(255,248,245,.55);max-width:540px;margin:0 auto;line-height:1.7;}
    .trust-meta{display:inline-flex;align-items:center;gap:.5rem;font-size:.75rem;color:rgba(255,248,245,.35);background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:100px;padding:.35rem .9rem;margin-bottom:1.5rem;}
    .trust-body h2{font-size:1.15rem;font-weight:800;letter-spacing:-.025em;margin:2.5rem 0 .75rem;padding-top:.5rem;border-top:1px solid rgba(255,255,255,.06);}
    .trust-body h2:first-child{border-top:none;margin-top:0;}
    .trust-body h3{font-size:.95rem;font-weight:700;margin:1.5rem 0 .5rem;color:rgba(255,248,245,.8);}
    .trust-body p{font-size:.9rem;color:rgba(255,248,245,.65);line-height:1.75;margin-bottom:1rem;}
    .trust-body ul,.trust-body ol{padding-left:1.4rem;margin-bottom:1rem;}
    .trust-body li{font-size:.9rem;color:rgba(255,248,245,.65);line-height:1.75;margin-bottom:.35rem;}
    .trust-body a{color:#e94560;text-decoration:underline;}
    .trust-body strong{color:rgba(255,248,245,.9);font-weight:700;}
    .trust-contact-box{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);border-radius:18px;padding:1.75rem 2rem;margin-top:2.5rem;}
    .trust-contact-box h3{margin-top:0!important;font-size:1rem;color:rgba(255,248,245,.9);}
    .trust-contact-box p{margin-bottom:.4rem;}
    .trust-contact-box a{color:#e94560;}
    .accent-bar{display:inline-block;width:36px;height:3px;background:linear-gradient(90deg,#e94560,#c73652);border-radius:3px;margin-bottom:1.25rem;}
  </style>'''

BODY_OPEN = '''<body style="background:#050407;color:rgba(255,248,245,.88);font-family:'Inter',system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased;min-height:100vh;overflow-x:hidden;">'''


# ─────────────────────────────────────────────────────────────────────────────
# 1. COOKIE POLICY
# ─────────────────────────────────────────────────────────────────────────────
cookie_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
{HEAD_COMMON}
  <title>Cookie Policy | SaaSpare</title>
  <meta name="description" content="SaaSpare's Cookie Policy explains what cookies we use, why we use them, and how you can control them.">
  <link rel="canonical" href="https://saaspare.org/cookie-policy">
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"Cookie Policy","url":"https://saaspare.org/cookie-policy","description":"SaaSpare cookie policy — how we use cookies and how to opt out.","publisher":{{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"}}}}</script>
</head>
{BODY_OPEN}
{NAV}
<main class="trust-content">
  <div class="trust-hero">
    <div class="accent-bar"></div>
    <div class="trust-meta">Last updated: June 2026</div>
    <h1>Cookie Policy</h1>
    <p>We use a small number of cookies to make SaaSpare work properly and to understand how our content performs. This page explains exactly what we use and how to opt out.</p>
  </div>
  <div class="trust-body">
    <h2>What are cookies?</h2>
    <p>Cookies are small text files stored on your device when you visit a website. They help websites remember your preferences and understand how visitors use the site. SaaSpare uses only the cookies necessary to run the site and measure its performance — we do not use advertising cookies or sell data to third parties.</p>

    <h2>Cookies we use</h2>
    <h3>1. Essential cookies</h3>
    <p>These cookies are required for the site to function. They cannot be disabled.</p>
    <ul>
      <li><strong>Session management</strong> — keeps you logged in if you use the Shortlist Builder tool.</li>
      <li><strong>Cloudflare security cookies</strong> (<code>__cf_bm</code>, <code>cf_clearance</code>) — bot protection and DDoS mitigation provided by Cloudflare Pages, our hosting provider. Set on first visit, expire after 30 minutes to 1 year.</li>
    </ul>

    <h3>2. Analytics cookies (Google Analytics 4)</h3>
    <p>We use Google Analytics 4 (GA4) to understand which pages are popular and how visitors navigate the site. This helps us improve our content and fix problems. GA4 sets the following cookies:</p>
    <ul>
      <li><strong>_ga</strong> — Distinguishes unique users. Expires after 2 years.</li>
      <li><strong>_ga_RLYVYV8WQJ</strong> — Stores session state. Expires after 2 years.</li>
      <li><strong>_gid</strong> — Distinguishes users, expires after 24 hours.</li>
    </ul>
    <p>Analytics data is anonymised and IP addresses are not stored in full. We do not use GA4 for advertising or remarketing. You can opt out via <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="nofollow noopener">Google Analytics Opt-Out</a> or by enabling "Do Not Track" in your browser.</p>

    <h3>3. Affiliate tracking cookies</h3>
    <p>When you click an affiliate link (e.g. <code>/go/nordvpn</code>) you are redirected to the vendor's website. The vendor may set their own cookies to track whether you make a purchase. These cookies are set by the vendor, not by SaaSpare. Vendors include Commission Junction (CJ), Impact.com, Awin, and others. Please refer to each vendor's own privacy and cookie policy for details.</p>
    <p>SaaSpare's own pages do not set affiliate tracking cookies on our domain. We earn a commission if you purchase after clicking — this is disclosed on every page that contains affiliate links.</p>

    <h2>How to control cookies</h2>
    <p>You can control cookies through your browser settings. Most browsers allow you to:</p>
    <ul>
      <li>View which cookies are set</li>
      <li>Block cookies from specific sites</li>
      <li>Delete cookies</li>
      <li>Enable Do Not Track requests</li>
    </ul>
    <p>Blocking essential cookies may affect how the site works. Blocking analytics cookies will not affect your experience. Instructions for major browsers:</p>
    <ul>
      <li><a href="https://support.google.com/chrome/answer/95647" target="_blank" rel="nofollow noopener">Google Chrome</a></li>
      <li><a href="https://support.mozilla.org/en-US/kb/cookies-information-websites-store-on-your-computer" target="_blank" rel="nofollow noopener">Mozilla Firefox</a></li>
      <li><a href="https://support.apple.com/en-au/guide/safari/sfri11471/mac" target="_blank" rel="nofollow noopener">Safari</a></li>
      <li><a href="https://support.microsoft.com/en-us/microsoft-edge/delete-cookies-in-microsoft-edge-63947406-40ac-c3b8-57b9-2a946a29ae09" target="_blank" rel="nofollow noopener">Microsoft Edge</a></li>
    </ul>

    <h2>Changes to this policy</h2>
    <p>We may update this Cookie Policy from time to time. When we do, we update the "Last updated" date at the top of this page. Continued use of the site after a change constitutes acceptance of the updated policy.</p>

    <div class="trust-contact-box">
      <h3>Questions about cookies?</h3>
      <p>Contact us at <a href="mailto:privacy@saaspare.org">privacy@saaspare.org</a> or via our <a href="/contact">contact page</a>.</p>
      <p style="font-size:.8rem;color:rgba(255,248,245,.35);margin-bottom:0">SaaSpare is operated by Kaylan von Papen (ABN 20 602 197 525), Queensland, Australia.</p>
    </div>
  </div>
</main>
{FOOTER}
</body>
</html>'''


# ─────────────────────────────────────────────────────────────────────────────
# 2. DMCA POLICY
# ─────────────────────────────────────────────────────────────────────────────
dmca_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
{HEAD_COMMON}
  <title>DMCA / Copyright Policy | SaaSpare</title>
  <meta name="description" content="SaaSpare's DMCA and copyright policy — how to submit a copyright takedown notice and how we handle disputes.">
  <link rel="canonical" href="https://saaspare.org/dmca">
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"DMCA Policy","url":"https://saaspare.org/dmca","description":"SaaSpare DMCA and copyright takedown procedure.","publisher":{{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"}}}}</script>
</head>
{BODY_OPEN}
{NAV}
<main class="trust-content">
  <div class="trust-hero">
    <div class="accent-bar"></div>
    <div class="trust-meta">Last updated: June 2026</div>
    <h1>DMCA &amp; Copyright Policy</h1>
    <p>SaaSpare respects intellectual property rights. This page explains how to submit a copyright takedown notice and how we respond.</p>
  </div>
  <div class="trust-body">
    <h2>Our content policy</h2>
    <p>All original content published on SaaSpare — including articles, comparison data, pricing research, and methodology — is written by or under the direction of our editorial team. We do not reproduce copyrighted vendor documentation, marketing copy, or third-party articles without permission.</p>
    <p>We do use publicly available information (pricing pages, feature lists, press releases) for research and editorial purposes. We cite sources and do not reproduce them verbatim.</p>

    <h2>Submitting a DMCA takedown notice</h2>
    <p>If you believe content published on SaaSpare infringes your copyright, you may submit a written notice to our designated agent. To be valid under the Digital Millennium Copyright Act (DMCA, 17 U.S.C. &sect; 512), your notice must include:</p>
    <ol>
      <li>Your name, address, telephone number, and email address.</li>
      <li>A description of the copyrighted work you claim has been infringed.</li>
      <li>The URL(s) on SaaSpare where the allegedly infringing content appears.</li>
      <li>A statement that you have a good-faith belief that the use is not authorised by the copyright owner, its agent, or the law.</li>
      <li>A statement, made under penalty of perjury, that the information in your notice is accurate and that you are the copyright owner or authorised to act on the owner's behalf.</li>
      <li>Your physical or electronic signature.</li>
    </ol>
    <p>Send DMCA notices to: <a href="mailto:dmca@saaspare.org">dmca@saaspare.org</a></p>
    <p>We will review every valid notice and, where required, remove or disable access to the infringing content within a reasonable time.</p>

    <h2>Counter-notices</h2>
    <p>If content you own or are authorised to use has been removed in response to a DMCA notice, you may submit a counter-notice. A valid counter-notice must include:</p>
    <ol>
      <li>Your name, address, telephone number, and email address.</li>
      <li>Identification of the removed content and the location where it appeared before removal.</li>
      <li>A statement, under penalty of perjury, that the content was removed or disabled by mistake or misidentification.</li>
      <li>A statement that you consent to the jurisdiction of the Federal District Court in your area, or any judicial district in which SaaSpare may be found, and that you will accept service of process from the original complainant.</li>
      <li>Your physical or electronic signature.</li>
    </ol>

    <h2>Repeat infringers</h2>
    <p>SaaSpare will terminate the publishing rights of any contributor who is found to be a repeat infringer of copyright.</p>

    <h2>Trademarks</h2>
    <p>Product names, logos, and trademarks mentioned on SaaSpare (HubSpot, ClickUp, Notion, etc.) are the property of their respective owners. Use of these names is for identification and editorial reference only and does not imply endorsement or affiliation.</p>

    <div class="trust-contact-box">
      <h3>DMCA agent contact</h3>
      <p><strong>Kaylan von Papen</strong> &mdash; Designated DMCA Agent</p>
      <p>Email: <a href="mailto:dmca@saaspare.org">dmca@saaspare.org</a></p>
      <p style="font-size:.8rem;color:rgba(255,248,245,.35);margin-bottom:0">SaaSpare is operated by Kaylan von Papen (ABN 20 602 197 525), Queensland, Australia. DMCA provisions apply where the DMCA has jurisdictional reach. Australian copyright law (Copyright Act 1968) applies in all other cases.</p>
    </div>
  </div>
</main>
{FOOTER}
</body>
</html>'''


# ─────────────────────────────────────────────────────────────────────────────
# 3. ACCESSIBILITY STATEMENT
# ─────────────────────────────────────────────────────────────────────────────
access_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
{HEAD_COMMON}
  <title>Accessibility Statement | SaaSpare</title>
  <meta name="description" content="SaaSpare's commitment to web accessibility — our standards, known limitations, and how to request accessible content.">
  <link rel="canonical" href="https://saaspare.org/accessibility">
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"Accessibility Statement","url":"https://saaspare.org/accessibility","description":"SaaSpare accessibility statement and commitment to WCAG 2.1 AA standards.","publisher":{{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"}}}}</script>
</head>
{BODY_OPEN}
{NAV}
<main class="trust-content">
  <div class="trust-hero">
    <div class="accent-bar"></div>
    <div class="trust-meta">Last updated: June 2026</div>
    <h1>Accessibility Statement</h1>
    <p>SaaSpare is committed to making our website accessible to all users, including people with disabilities. We aim to conform to WCAG 2.1 Level AA.</p>
  </div>
  <div class="trust-body">
    <h2>Our commitment</h2>
    <p>We believe everyone should be able to access accurate, independent SaaS pricing and comparison data. We work to ensure SaaSpare is usable by people using screen readers, keyboard navigation, voice control, and other assistive technologies.</p>

    <h2>Standards we target</h2>
    <p>SaaSpare targets <strong>Web Content Accessibility Guidelines (WCAG) 2.1 Level AA</strong>. Our pages are built with:</p>
    <ul>
      <li>Semantic HTML5 — correct use of headings, lists, tables, and landmark regions</li>
      <li>ARIA labels on interactive elements where native semantics are insufficient</li>
      <li>Colour contrast ratios meeting or exceeding WCAG AA (4.5:1 for normal text, 3:1 for large text)</li>
      <li>Keyboard-navigable navigation, links, and interactive components</li>
      <li>Alt text on all informative images</li>
      <li>Responsive layouts that work from 320px screen width upward</li>
      <li>Respect for <code>prefers-reduced-motion</code> — animations are paused for users who prefer reduced motion</li>
      <li>Readable font sizes (minimum 14px body text) and sufficient line height</li>
    </ul>

    <h2>Known limitations</h2>
    <p>While we strive for full accessibility, some areas of the site may not yet fully conform:</p>
    <ul>
      <li><strong>Comparison tables</strong> on very long pages may be difficult to navigate on some screen readers. We are working to add improved ARIA table descriptions.</li>
      <li><strong>Third-party scripts</strong> (e.g. Google Analytics) may not be fully accessible — we minimise third-party code to reduce this risk.</li>
      <li><strong>PDF documents</strong> — any downloadable PDFs on the site may not be fully tagged for screen reader use. Contact us for an accessible alternative.</li>
    </ul>

    <h2>Requesting accessible content</h2>
    <p>If you encounter a barrier on SaaSpare, or need content in a different format, please contact us:</p>
    <ul>
      <li>Email: <a href="mailto:accessibility@saaspare.org">accessibility@saaspare.org</a></li>
      <li>Contact form: <a href="/contact">saaspare.org/contact</a></li>
    </ul>
    <p>We will respond within 5 business days and aim to resolve accessibility issues within 30 days where technically feasible.</p>

    <h2>Feedback</h2>
    <p>We welcome feedback on the accessibility of SaaSpare. If you find something that does not meet the accessibility standard, or if you have a suggestion for improvement, please <a href="/contact">contact us</a>. Your feedback helps us improve for everyone.</p>

    <h2>Technical specification</h2>
    <p>SaaSpare is a static HTML site deployed via Cloudflare Pages. We use:</p>
    <ul>
      <li>HTML5, CSS3, and vanilla JavaScript (no heavy frameworks)</li>
      <li>System font stack with Inter as primary typeface</li>
      <li>Dark background (#050407) with high-contrast text</li>
      <li>Tested in Chrome, Firefox, Safari, and Edge on desktop and mobile</li>
    </ul>

    <div class="trust-contact-box">
      <h3>Accessibility contact</h3>
      <p>Email: <a href="mailto:accessibility@saaspare.org">accessibility@saaspare.org</a></p>
      <p>This statement was prepared in June 2026 and reviewed by our founder Kaylan von Papen.</p>
      <p style="font-size:.8rem;color:rgba(255,248,245,.35);margin-bottom:0">SaaSpare is operated by Kaylan von Papen (ABN 20 602 197 525), Queensland, Australia.</p>
    </div>
  </div>
</main>
{FOOTER}
</body>
</html>'''


# ─────────────────────────────────────────────────────────────────────────────
# 4. ADVERTISE / PARTNER PAGE
# ─────────────────────────────────────────────────────────────────────────────
advertise_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
{HEAD_COMMON}
  <title>Advertise on SaaSpare | Partner With Us</title>
  <meta name="description" content="Partner with SaaSpare to reach 1,400+ pages of B2B SaaS buyer intent traffic. Independent research, no paid rankings — honest affiliate partnerships only.">
  <link rel="canonical" href="https://saaspare.org/advertise">
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"Advertise on SaaSpare","url":"https://saaspare.org/advertise","description":"Affiliate and partnership opportunities with SaaSpare — independent B2B SaaS comparison publisher.","publisher":{{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"}}}}</script>
</head>
{BODY_OPEN}
{NAV}
<main class="trust-content">
  <div class="trust-hero">
    <div class="accent-bar"></div>
    <div class="trust-meta">Affiliate &amp; Partnership Enquiries</div>
    <h1>Partner With SaaSpare</h1>
    <p>SaaSpare is an independent B2B SaaS comparison publisher with 1,400+ buyer-intent pages. We work with software companies through honest affiliate partnerships — no paid placements, no ranking manipulation.</p>
  </div>
  <div class="trust-body">
    <h2>Who we are</h2>
    <p>SaaSpare (saaspare.org) is an independent research and comparison site covering B2B SaaS tools across 20+ categories including CRM, project management, VPN, accounting, email marketing, password management, and more.</p>
    <p>We are operated by <strong>Kaylan von Papen</strong> (ABN 20 602 197 525), based in Queensland, Australia. The site publishes verified pricing data, honest comparisons, and buyer guides for 80+ tools. We do not sell sponsored rankings or pay-to-play placements.</p>

    <h2>Our audience</h2>
    <ul>
      <li><strong>1,400+ buyer-intent pages</strong> covering software pricing, alternatives, reviews, and comparisons</li>
      <li><strong>Primary audience:</strong> B2B decision-makers, IT managers, founders, and finance teams evaluating software purchases</li>
      <li><strong>Traffic:</strong> Growing organic search audience primarily from English-speaking markets (Australia, US, UK, Canada, Singapore)</li>
      <li><strong>Content freshness:</strong> Pricing data verified weekly via automated scraping and manual review</li>
    </ul>

    <h2>How we work with partners</h2>
    <h3>Affiliate partnerships</h3>
    <p>We participate in affiliate programs through established networks including Commission Junction (CJ), Impact.com, Awin, and PartnerStack. When a reader clicks an affiliate link and makes a purchase, we earn a commission. This does not affect our editorial scores or rankings.</p>
    <p>Our editorial scores and rankings are determined entirely by our research methodology (see <a href="/methodology">Methodology</a>). Affiliate status has zero influence on a tool's ranking position — we rank tools based on value, features, pricing, and real buyer feedback.</p>

    <h3>Direct affiliate inquiries</h3>
    <p>If your software company is not currently listed on an affiliate network we work with, contact us to discuss a direct partnership. We assess direct partnerships against the same criteria as network programs.</p>

    <h3>What we do not offer</h3>
    <ul>
      <li>Paid "featured" or "sponsored" placements in our rankings</li>
      <li>Pay-to-rank upgrades — ranking position is editorial-only</li>
      <li>Guaranteed positive reviews</li>
      <li>Banner advertising</li>
      <li>Email list rental</li>
    </ul>

    <h2>Our editorial standards</h2>
    <p>All affiliate relationships are disclosed on every page that contains affiliate links (see our <a href="/affiliate-disclosure">Affiliate Disclosure</a>). Our <a href="/editorial-policy">Editorial Policy</a> and <a href="/methodology">Methodology</a> explain how we score and rank tools.</p>
    <p>Scores are set before any affiliate conversation takes place with a vendor. This is non-negotiable and documented for every review.</p>

    <h2>Affiliate networks we use</h2>
    <ul>
      <li><strong>Commission Junction (CJ)</strong> — Publisher ID 101733230</li>
      <li><strong>Impact.com</strong> — Publisher ID 7269601</li>
      <li><strong>Awin</strong> — Publisher ID 2917137</li>
      <li><strong>PartnerStack</strong> — publisher application active</li>
    </ul>
    <p>If your program is available on any of these networks, please invite us directly through the network platform.</p>

    <div class="trust-contact-box">
      <h3>Partnership enquiries</h3>
      <p>Email: <a href="mailto:partnerships@saaspare.org">partnerships@saaspare.org</a></p>
      <p>Include your company name, affiliate network (if applicable), commission structure, and a brief description of your program. We respond within 3 business days.</p>
      <p style="font-size:.8rem;color:rgba(255,248,245,.35);margin-bottom:0">SaaSpare is operated by Kaylan von Papen (ABN 20 602 197 525), Queensland, Australia. Business hours: Mon-Fri, AEST.</p>
    </div>
  </div>
</main>
{FOOTER}
</body>
</html>'''


# ─────────────────────────────────────────────────────────────────────────────
# Write all files
# ─────────────────────────────────────────────────────────────────────────────
pages = {
    "cookie-policy.html": cookie_html,
    "dmca.html": dmca_html,
    "accessibility.html": access_html,
    "advertise.html": advertise_html,
}

for filename, html in pages.items():
    path = SITE / filename
    path.write_text(html, encoding="utf-8")
    print(f"[OK] Wrote {path}")

print(f"\nBuilt {len(pages)} trust stack pages.")
print("Update footer on ALL existing pages to include links to these new pages.")
