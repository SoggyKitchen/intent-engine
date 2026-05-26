"""
Implement the new SaaSpare design system.

Reads design files from the extracted zip, applies these transforms:
  - Replaces design nav (sp-nav) with existing site nav (SVG logo mark)
  - Fixes all relative links → absolute site paths
  - Adds nav scroll CSS + JS
  - Adds GA4 tag
  - Updates CSS/JS asset paths
  - Keeps existing homepage, injects new sections only

Output:
  site/assets/sp-shared.css
  site/assets/sp-motion.css
  site/assets/sp-motion.js
  site/pages/index.html   (library)
  site/about.html
  site/deal-radar.html    (new)
  site/roi.html           (new)
  site/shortlist.html     (new)
  site/newsletter.html    (new)
  site/contact.html       (new)
  site/404.html           (new — fixes /404 redirect target bug)
  site/index.html         (homepage — inject new sections only)

Run: uv run python scripts/implement_design.py
"""
import re
from pathlib import Path
from shutil import copy2

DESIGN = Path(r"C:\Users\smith\Downloads\saaspare-design\saaspare")
ROOT   = Path(__file__).resolve().parents[1]
SITE   = ROOT / "site"

# ── Existing nav (preserved exactly) ──────────────────────────────────────
EXISTING_NAV_HTML = '''<nav id="nav">
  <a href="/" class="logo">
    <svg class="logo-mark" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs><clipPath id="ct"><path d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></clipPath><clipPath id="cb"><path d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/></clipPath><mask id="sm1"><rect x="-400" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="-400;0;0;180;180" keyTimes="0;0.20;0.61;0.62;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask><mask id="sm2"><rect x="180" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="180;180;-220;-220;180;180" keyTimes="0;0.21;0.41;0.82;0.83;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask><mask id="sm3"><rect x="-400" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="-400;-400;0;0" keyTimes="0;0.42;0.62;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask><mask id="sm4"><rect x="180" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="180;180;-220;-220" keyTimes="0;0.63;0.83;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask></defs><path class="mark-bot" fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/><path class="mark-top" fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/><g class="wave-top" clip-path="url(#ct)" mask="url(#sm1)"><rect width="180" height="180" fill="#e94560"/></g><g class="wave-top2" clip-path="url(#ct)" mask="url(#sm3)"><rect width="180" height="180" fill="#fff"/></g><g class="wave-bot" clip-path="url(#cb)" mask="url(#sm2)"><rect width="180" height="180" fill="#fff"/></g><g class="wave-bot2" clip-path="url(#cb)" mask="url(#sm4)"><rect width="180" height="180" fill="#e94560"/></g></svg>
    <span class="logo-text">Saa<em>Spare</em></span>
  </a>
  <a href="/pages/" class="nav-link">Comparisons</a>
  <a href="/shortlist" class="nav-link">Shortlist Builder</a>
  <a href="/deal-radar" class="nav-link">Deal Radar</a>
  <a href="/about" class="nav-link">About</a>
  <a href="/shortlist" class="nav-cta">Build Shortlist &#8594;</a>
</nav>'''

NAV_CSS = """
/* ── EXISTING NAV (preserved) ─────────────────────────────────────────── */
:root{--border:rgba(255,255,255,.07);--red:#e94560;--red2:#c73652;--muted:rgba(255,248,245,.42)}
nav#nav{position:fixed;top:0;left:0;right:0;z-index:200;padding:1rem 2rem;display:flex;align-items:center;gap:4px;transition:all .4s ease;background:transparent;border-bottom:none}
nav#nav.scrolled{background:rgba(7,7,13,.82);border-bottom:1px solid var(--border);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px)}
.logo{display:flex;align-items:center;gap:9px;margin-right:auto}
.logo-mark{height:26px;width:auto;flex-shrink:0;overflow:visible;animation:markGlow 4s ease-in-out infinite}
.mark-top,.mark-bot{transform-box:fill-box;transform-origin:center;transition:transform .5s cubic-bezier(.34,1.56,.64,1)}
.wv{pointer-events:none;transition:opacity .3s}
@keyframes markGlow{0%,100%{filter:drop-shadow(0 0 0px rgba(233,69,96,0))}50%{filter:drop-shadow(0 3px 18px rgba(233,69,96,.6))}}
.logo:hover .mark-top{transform:translateX(26px)}.logo:hover .mark-bot{transform:translateX(-26px)}
.logo:hover .wv,.logo:hover .wave-top,.logo:hover .wave-bot,.logo:hover .wave-top2,.logo:hover .wave-bot2{opacity:0}
.logo-text{font-weight:800;font-size:1.05rem;letter-spacing:-.4px;color:#fff}
.logo-text em{color:#e94560;font-style:normal}
nav#nav .nav-link{color:rgba(255,248,245,.42);font-size:.8rem;padding:.38rem .82rem;border-radius:8px;font-weight:500;transition:color .18s;white-space:nowrap;text-decoration:none}
nav#nav .nav-link:hover{color:#fff}
.nav-cta{background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.44rem 1.15rem;border-radius:100px;font-weight:700;font-size:.78rem;box-shadow:0 4px 16px rgba(233,69,96,.4);margin-left:6px;transition:transform .15s,box-shadow .15s;white-space:nowrap;text-decoration:none}
.nav-cta:hover{transform:translateY(-1px);box-shadow:0 8px 24px rgba(233,69,96,.55)}
/* Push content below fixed nav */
body>div.sp-bg+nav#nav~*:first-of-type{padding-top:4.5rem}
"""

NAV_JS = """
<script>
(function(){
  var nav = document.getElementById('nav');
  if(!nav) return;
  function chk(){nav.classList.toggle('scrolled', window.scrollY > 50);}
  window.addEventListener('scroll', chk, {passive:true});
  chk();
})();
</script>"""

GA_TAG = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-RLYVYV8WQJ');
</script>"""

# Link substitutions: old → new
LINK_MAP = [
    (r'href="library\.html"',     'href="/pages/"'),
    (r'href="index\.html"',       'href="/"'),
    (r'href="about\.html"',       'href="/about"'),
    (r'href="deal-radar\.html"',  'href="/deal-radar"'),
    (r'href="roi\.html"',         'href="/roi"'),
    (r'href="shortlist\.html"',   'href="/shortlist"'),
    (r'href="article\.html"',     'href="/pages/"'),
    (r'href="disclosure\.html"',  'href="/affiliate-disclosure"'),
    (r'href="contact\.html"',     'href="/contact"'),
    (r'href="privacy\.html"',     'href="/privacy"'),
    (r'href="newsletter\.html"',  'href="/newsletter"'),
    (r'href="#"',                  'href="/"'),
]

# CSS/JS path substitutions
ASSET_MAP = [
    ('href="shared.css"',  'href="/assets/sp-shared.css"'),
    ('href="motion.css"',  'href="/assets/sp-motion.css"'),
    ('src="motion.js"',    'src="/assets/sp-motion.js"'),
]


def fix_links(html: str) -> str:
    for pat, rep in LINK_MAP:
        html = re.sub(pat, rep, html)
    for old, new in ASSET_MAP:
        html = html.replace(old, new)
    return html


def replace_nav(html: str) -> str:
    """Replace the design nav with the existing site nav."""
    html = re.sub(
        r'<nav class="sp-nav"[^>]*>[\s\S]*?</nav>',
        EXISTING_NAV_HTML,
        html, count=1
    )
    return html


def inject_nav_css(html: str) -> str:
    """Add nav CSS into the page's <style> block."""
    if NAV_CSS.strip() in html:
        return html
    # Inject before </style> of the first inline style block
    return html.replace('</style>', NAV_CSS + '\n</style>', 1)


def inject_nav_js(html: str) -> str:
    """Add nav scroll JS before </body>."""
    if 'nav.classList.toggle' in html:
        return html
    return html.replace('</body>', NAV_JS + '\n</body>', 1)


def inject_ga(html: str) -> str:
    """Add GA4 tag if not present."""
    if 'G-RLYVYV8WQJ' in html:
        return html
    return html.replace('</head>', GA_TAG + '\n</head>', 1)


def add_canonical(html: str, path: str) -> str:
    """Add canonical tag if not already present."""
    if 'rel="canonical"' in html:
        return html
    url = f"https://saaspare.org{path}"
    tag = f'  <link rel="canonical" href="{url}">\n'
    return html.replace('</head>', tag + '</head>', 1)


def add_site_links(html: str) -> str:
    """Add favicon and other site-wide tags."""
    additions = '''  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <meta name="theme-color" content="#050407">
  <meta name="robots" content="index,follow">
'''
    if 'favicon' not in html:
        html = html.replace('</head>', additions + '</head>', 1)
    return html


def transform_page(html: str, canonical_path: str) -> str:
    """Apply all transformations to a design page."""
    html = fix_links(html)
    html = replace_nav(html)
    html = inject_nav_css(html)
    html = inject_nav_js(html)
    html = inject_ga(html)
    html = add_canonical(html, canonical_path)
    html = add_site_links(html)
    return html


# ── Copy shared assets ─────────────────────────────────────────────────────

def copy_assets():
    assets_dir = SITE / "assets"
    assets_dir.mkdir(exist_ok=True)

    for src_name, dst_name in [
        ("shared.css",  "sp-shared.css"),
        ("motion.css",  "sp-motion.css"),
        ("motion.js",   "sp-motion.js"),
    ]:
        src = DESIGN / src_name
        dst = assets_dir / dst_name
        copy2(src, dst)
        print(f"  copied {src_name} -> assets/{dst_name}")


# ── Page definitions ──────────────────────────────────────────────────────

PAGES = [
    # (design_file, output_path, canonical_path, title_override_or_None)
    ("library.html",    "pages/index.html",   "/pages/",        "Comparisons Library — SaaSpare"),
    ("about.html",      "about.html",          "/about",         "About SaaSpare — Independent B2B Research"),
    ("deal-radar.html", "deal-radar.html",     "/deal-radar",    "Deal Radar — Live SaaS Deals | SaaSpare"),
    ("roi.html",        "roi.html",            "/roi",           "SaaS ROI Calculator — SaaSpare"),
    ("shortlist.html",  "shortlist.html",      "/shortlist",     "Shortlist Builder — SaaSpare"),
    ("newsletter.html", "newsletter.html",     "/newsletter",    "Newsletter — SaaSpare Insider Insights"),
    ("contact.html",    "contact.html",        "/contact",       "Contact SaaSpare"),
    ("404.html",        "404.html",            "/404",           "Page Not Found — SaaSpare"),
]


def build_page(design_name: str, out_rel: str, canonical: str, title: str) -> None:
    src  = DESIGN / design_name
    dst  = SITE / out_rel
    dst.parent.mkdir(parents=True, exist_ok=True)

    html = src.read_text(encoding="utf-8")
    html = transform_page(html, canonical)

    # Update title if provided
    if title:
        html = re.sub(r'<title>[^<]+</title>', f'<title>{title}</title>', html, count=1)

    dst.write_text(html, encoding="utf-8")
    print(f"  built {out_rel}")


# ── Homepage injection ────────────────────────────────────────────────────

BRAND_MARQUEE = """
<!-- ═══ BRAND MARQUEE (new design) ═══ -->
<div class="brand-marquee" style="padding:1.5rem 0;border-top:1px solid rgba(255,255,255,.07);border-bottom:1px solid rgba(255,255,255,.07);background:rgba(0,0,0,.2);overflow:hidden;position:relative">
  <div style="position:absolute;top:0;bottom:0;left:0;width:140px;z-index:2;pointer-events:none;background:linear-gradient(90deg,#07070d,transparent)"></div>
  <div style="position:absolute;top:0;bottom:0;right:0;width:140px;z-index:2;pointer-events:none;background:linear-gradient(-90deg,#07070d,transparent)"></div>
  <div style="font-size:.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,248,245,.22);text-align:center;margin-bottom:.75rem">Tools covered include</div>
  <div class="brand-track" style="display:flex;gap:0;width:max-content;animation:bm 40s linear infinite">
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/hubspot/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> HubSpot</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/notion/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> Notion</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:5px;background:linear-gradient(135deg,#00a1e0,#0070a0);color:#fff;font-weight:900;font-size:.55rem;letter-spacing:-.02em">SF</span> Salesforce</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/shopify/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> Shopify</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/asana/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> Asana</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/clickup/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> ClickUp</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/dropbox/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> Dropbox</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/zoom/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> Zoom</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/1password/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> 1Password</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/bitwarden/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> Bitwarden</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/figma/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> Figma</span>
    <!-- duplicate for seamless loop -->
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/hubspot/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> HubSpot</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/notion/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> Notion</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:5px;background:linear-gradient(135deg,#00a1e0,#0070a0);color:#fff;font-weight:900;font-size:.55rem;letter-spacing:-.02em">SF</span> Salesforce</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/shopify/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> Shopify</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/asana/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> Asana</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/clickup/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> ClickUp</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/dropbox/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> Dropbox</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/zoom/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> Zoom</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/1password/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> 1Password</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/bitwarden/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> Bitwarden</span>
    <span class="brand-item" style="display:inline-flex;align-items:center;gap:10px;padding:0 2.5rem;color:rgba(255,248,245,.42);font-weight:600;font-size:.95rem;white-space:nowrap;opacity:.7"><img src="https://cdn.simpleicons.org/figma/ffffff" style="width:20px;height:20px;object-fit:contain;filter:grayscale(1) brightness(1.6)"> Figma</span>
  </div>
</div>
<style>@keyframes bm{from{transform:translateX(0)}to{transform:translateX(-50%)}}</style>
"""

LIBRARY_PREVIEW = """
<!-- ═══ LIBRARY PREVIEW (new design) ═══ -->
<section style="padding:4.5rem clamp(1.25rem,4vw,3rem);position:relative">
  <div style="max-width:1280px;margin:0 auto">
    <div style="text-align:center;margin-bottom:2.75rem;display:flex;flex-direction:column;align-items:center;gap:.85rem">
      <span style="display:inline-flex;align-items:center;gap:8px;font-size:.7rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#ff7a9a;padding:6px 14px;border-radius:9999px;background:rgba(255,65,109,.10);border:1px solid rgba(255,75,115,.25)"><span style="width:6px;height:6px;border-radius:50%;background:#ff416d;animation:dotPulse 2.4s ease-in-out infinite"></span>Browse the library</span>
      <h2 style="font-size:clamp(32px,4vw,56px);line-height:1.02;font-weight:900;letter-spacing:-.035em;color:#fff7f8;text-wrap:balance">Find the right <span style="background:linear-gradient(100deg,#ff416d 0%,#ff7a9a 35%,#ffd0dc 50%,#ff7a9a 65%,#ff416d 100%);background-size:300% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:spGlint 3.6s linear infinite">SaaS answer</span> faster.</h2>
      <p style="font-size:1.05rem;line-height:1.65;color:rgba(255,247,248,.64);max-width:640px">1,200+ tools, pricing guides, side-by-side breakdowns. No vendor fluff.</p>
    </div>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px">
      <a href="/pages/1password-pricing-2026-plans-costs-what-you-actually-pay" style="padding:18px;background:linear-gradient(180deg,rgba(255,255,255,.055),rgba(255,255,255,.025));border:1px solid rgba(255,255,255,.09);border-radius:14px;display:flex;flex-direction:column;gap:10px;transition:all .2s;text-decoration:none;position:relative;overflow:hidden" onmouseover="this.style.borderColor='rgba(255,75,115,.38)';this.style.transform='translateY(-5px)'" onmouseout="this.style.borderColor='rgba(255,255,255,.09)';this.style.transform='translateY(0)'">
        <div style="display:flex;align-items:center;gap:10px"><span style="width:44px;height:44px;border-radius:14px;background:linear-gradient(180deg,rgba(255,255,255,.10),rgba(255,255,255,.03));border:1px solid rgba(255,255,255,.12);display:inline-flex;align-items:center;justify-content:center;overflow:hidden;flex-shrink:0"><img src="https://cdn.simpleicons.org/1password/0094f5" style="width:55%;height:55%;object-fit:contain;filter:brightness(1.15)"></span><div><div style="font-size:.95rem;font-weight:700;color:#fff7f8;letter-spacing:-.01em">1Password</div><div style="font-size:.72rem;color:rgba(255,247,248,.42)">Security &amp; PWD Mgmt</div></div></div>
        <p style="font-size:.82rem;color:rgba(255,247,248,.64);line-height:1.5;flex:1">Secure passwords, SSO, secrets management — for teams up to enterprise.</p>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-top:6px">
          <div style="font-size:.95rem;color:#fff7f8;font-weight:700">$2.99<span style="font-style:normal;font-size:.74rem;color:rgba(255,247,248,.42);font-weight:500">/user/mo</span></div>
          <div style="font-size:.78rem;color:rgba(255,247,248,.64)"><span style="color:#f5b942">&#9733;</span> 4.9 (312)</div>
        </div>
      </a>
      <a href="/pages/bitwarden-pricing-2026-plans-costs-what-you-actually-pay" style="padding:18px;background:linear-gradient(180deg,rgba(255,255,255,.055),rgba(255,255,255,.025));border:1px solid rgba(255,255,255,.09);border-radius:14px;display:flex;flex-direction:column;gap:10px;transition:all .2s;text-decoration:none;position:relative;overflow:hidden" onmouseover="this.style.borderColor='rgba(255,75,115,.38)';this.style.transform='translateY(-5px)'" onmouseout="this.style.borderColor='rgba(255,255,255,.09)';this.style.transform='translateY(0)'">
        <div style="display:flex;align-items:center;gap:10px"><span style="width:44px;height:44px;border-radius:14px;background:linear-gradient(180deg,rgba(255,255,255,.10),rgba(255,255,255,.03));border:1px solid rgba(255,255,255,.12);display:inline-flex;align-items:center;justify-content:center;overflow:hidden;flex-shrink:0"><img src="https://cdn.simpleicons.org/bitwarden/175ddc" style="width:55%;height:55%;object-fit:contain;filter:brightness(1.15)"></span><div><div style="font-size:.95rem;font-weight:700;color:#fff7f8;letter-spacing:-.01em">Bitwarden</div><div style="font-size:.72rem;color:rgba(255,247,248,.42)">Security &amp; PWD Mgmt</div></div></div>
        <p style="font-size:.82rem;color:rgba(255,247,248,.64);line-height:1.5;flex:1">Open-source password manager for teams &amp; enterprises with self-host options.</p>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-top:6px">
          <div style="font-size:.95rem;color:#fff7f8;font-weight:700">$4.00<span style="font-style:normal;font-size:.74rem;color:rgba(255,247,248,.42);font-weight:500">/user/mo</span></div>
          <div style="font-size:.78rem;color:rgba(255,247,248,.64)"><span style="color:#f5b942">&#9733;</span> 4.6 (289)</div>
        </div>
      </a>
      <a href="/pages/notion-pricing-2026-plans-costs-what-you-actually-pay" style="padding:18px;background:linear-gradient(180deg,rgba(255,255,255,.055),rgba(255,255,255,.025));border:1px solid rgba(255,255,255,.09);border-radius:14px;display:flex;flex-direction:column;gap:10px;transition:all .2s;text-decoration:none;position:relative;overflow:hidden" onmouseover="this.style.borderColor='rgba(255,75,115,.38)';this.style.transform='translateY(-5px)'" onmouseout="this.style.borderColor='rgba(255,255,255,.09)';this.style.transform='translateY(0)'">
        <div style="display:flex;align-items:center;gap:10px"><span style="width:44px;height:44px;border-radius:14px;background:linear-gradient(180deg,rgba(255,255,255,.10),rgba(255,255,255,.03));border:1px solid rgba(255,255,255,.12);display:inline-flex;align-items:center;justify-content:center;overflow:hidden;flex-shrink:0"><img src="https://cdn.simpleicons.org/notion/ffffff" style="width:55%;height:55%;object-fit:contain;filter:brightness(1.15)"></span><div><div style="font-size:.95rem;font-weight:700;color:#fff7f8;letter-spacing:-.01em">Notion</div><div style="font-size:.72rem;color:rgba(255,247,248,.42)">Docs &amp; Productivity</div></div></div>
        <p style="font-size:.82rem;color:rgba(255,247,248,.64);line-height:1.5;flex:1">Docs, wikis, projects — all-in-one workspace for fast-moving teams.</p>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-top:6px">
          <div style="font-size:.95rem;color:#fff7f8;font-weight:700">$8.00<span style="font-style:normal;font-size:.74rem;color:rgba(255,247,248,.42);font-weight:500">/user/mo</span></div>
          <div style="font-size:.78rem;color:rgba(255,247,248,.64)"><span style="color:#f5b942">&#9733;</span> 4.7 (201)</div>
        </div>
      </a>
      <a href="/pages/clickup-pricing-2026-plans-costs-what-you-actually-pay" style="padding:18px;background:linear-gradient(180deg,rgba(255,255,255,.055),rgba(255,255,255,.025));border:1px solid rgba(255,255,255,.09);border-radius:14px;display:flex;flex-direction:column;gap:10px;transition:all .2s;text-decoration:none;position:relative;overflow:hidden" onmouseover="this.style.borderColor='rgba(255,75,115,.38)';this.style.transform='translateY(-5px)'" onmouseout="this.style.borderColor='rgba(255,255,255,.09)';this.style.transform='translateY(0)'">
        <div style="display:flex;align-items:center;gap:10px"><span style="width:44px;height:44px;border-radius:14px;background:linear-gradient(180deg,rgba(255,255,255,.10),rgba(255,255,255,.03));border:1px solid rgba(255,255,255,.12);display:inline-flex;align-items:center;justify-content:center;overflow:hidden;flex-shrink:0"><img src="https://cdn.simpleicons.org/clickup/7b68ee" style="width:55%;height:55%;object-fit:contain;filter:brightness(1.15)"></span><div><div style="font-size:.95rem;font-weight:700;color:#fff7f8;letter-spacing:-.01em">ClickUp</div><div style="font-size:.72rem;color:rgba(255,247,248,.42)">Project Management</div></div></div>
        <p style="font-size:.82rem;color:rgba(255,247,248,.64);line-height:1.5;flex:1">Project management with AI, dashboards, and granular permissions.</p>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-top:6px">
          <div style="font-size:.95rem;color:#fff7f8;font-weight:700">$7.00<span style="font-style:normal;font-size:.74rem;color:rgba(255,247,248,.42);font-weight:500">/user/mo</span></div>
          <div style="font-size:.78rem;color:rgba(255,247,248,.64)"><span style="color:#f5b942">&#9733;</span> 4.4 (178)</div>
        </div>
      </a>
    </div>
    <div style="text-align:center;margin-top:2.5rem">
      <a href="/pages/" style="display:inline-flex;align-items:center;gap:8px;padding:.85rem 1.5rem;border-radius:9999px;font-weight:700;font-size:.92rem;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.09);color:#fff7f8;text-decoration:none;transition:all .2s" onmouseover="this.style.background='rgba(255,255,255,.10)'" onmouseout="this.style.background='rgba(255,255,255,.06)'">View all 1,200+ tools &#8594;</a>
    </div>
  </div>
</section>
<style>
@keyframes spGlint{0%{background-position:100% 50%}100%{background-position:-200% 50%}}
@keyframes dotPulse{0%,100%{box-shadow:0 0 4px #ff416d}50%{box-shadow:0 0 14px #ff416d,0 0 0 5px rgba(255,65,109,.12)}}
@media(max-width:900px){.lib-preview-grid{grid-template-columns:1fr 1fr!important}}
@media(max-width:600px){.lib-preview-grid{grid-template-columns:1fr!important}}
</style>
"""

NEWSLETTER_SECTION = """
<!-- ═══ NEWSLETTER (new design) ═══ -->
<section style="padding:1rem clamp(1.25rem,4vw,3rem) 6rem">
  <div style="max-width:880px;margin:0 auto">
    <div style="padding:3.5rem 2.5rem;text-align:center;background:radial-gradient(circle at 50% 0%,rgba(255,70,111,.20),transparent 55%),linear-gradient(180deg,rgba(60,9,24,.82),rgba(22,9,15,.92));border:1px solid rgba(255,75,115,.25);border-radius:28px;box-shadow:0 30px 90px rgba(255,45,92,.14),inset 0 1px 0 rgba(255,255,255,.06)">
      <span style="display:inline-flex;align-items:center;gap:8px;font-size:.7rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#ff7a9a;padding:6px 14px;border-radius:9999px;background:rgba(255,65,109,.10);border:1px solid rgba(255,75,115,.25)"><span style="width:6px;height:6px;border-radius:50%;background:#ff416d;box-shadow:0 0 10px #ff416d;animation:dotPulse 2.4s ease-in-out infinite"></span>Newsletter</span>
      <h2 style="font-size:clamp(32px,4vw,52px);line-height:1.02;font-weight:900;letter-spacing:-.035em;color:#fff7f8;margin:1rem 0;text-wrap:balance">Insider insights. <span style="background:linear-gradient(100deg,#ff416d 0%,#ff7a9a 35%,#ffd0dc 50%,#ff7a9a 65%,#ff416d 100%);background-size:300% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:spGlint 3.6s linear infinite">Smarter SaaS decisions.</span></h2>
      <p style="font-size:1.05rem;line-height:1.65;color:rgba(255,247,248,.64);max-width:480px;margin:0 auto">Pricing changes, hidden fees, tool comparisons, and verified deal alerts &mdash; every Wednesday.</p>
      <form style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:1.75rem;max-width:480px;margin-left:auto;margin-right:auto" onsubmit="event.preventDefault()">
        <input type="email" placeholder="Enter your work email" required style="flex:1;min-width:220px;padding:.85rem 1.1rem;background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.09);border-radius:9999px;color:#fff7f8;font-size:.95rem;outline:none;font-family:inherit">
        <button type="submit" style="display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:.85rem 1.5rem;border-radius:9999px;font-weight:700;font-size:.92rem;background:linear-gradient(135deg,#ff416d,#c92950);color:#fff;box-shadow:0 10px 30px rgba(255,65,109,.45);border:none;cursor:pointer;font-family:inherit;position:relative;overflow:hidden" onmouseover="this.style.transform='translateY(-1px)'" onmouseout="this.style.transform='translateY(0)'">Subscribe Free</button>
      </form>
      <p style="font-size:.82rem;color:rgba(255,247,248,.42);margin-top:1rem">No spam. Unsubscribe anytime. Written by real buyers.</p>
    </div>
  </div>
</section>
"""

FLOATING_CHIPS_CSS = """
/* Floating chips for homepage hero */
.floating-chip{position:absolute;display:inline-flex;align-items:center;gap:7px;padding:7px 14px;background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.08);border-radius:9999px;font-size:.78rem;font-weight:600;color:rgba(255,248,245,.42);backdrop-filter:blur(12px);pointer-events:none;white-space:nowrap;animation:chipFloat var(--chip-dur,8s) ease-in-out infinite alternate;animation-delay:var(--chip-delay,0s)}
@keyframes chipFloat{from{transform:translateY(0) translateX(0)}to{transform:translateY(-12px) translateX(4px)}}
"""

FLOATING_CHIPS_HTML = """
  <!-- Floating background tool chips -->
  <div aria-hidden="true" style="position:absolute;inset:0;pointer-events:none;z-index:0;overflow:hidden">
    <span class="floating-chip" style="top:18%;left:6%;--chip-dur:9s;--chip-delay:0s"><img src="https://cdn.simpleicons.org/hubspot/ff7a59" style="width:14px;height:14px;display:inline-block"> HubSpot</span>
    <span class="floating-chip" style="top:28%;right:7%;--chip-dur:11s;--chip-delay:1.2s"><img src="https://cdn.simpleicons.org/notion/ffffff" style="width:14px;height:14px;display:inline-block"> Notion</span>
    <span class="floating-chip" style="top:62%;left:4%;--chip-dur:10s;--chip-delay:2.4s"><img src="https://cdn.simpleicons.org/clickup/7b68ee" style="width:14px;height:14px;display:inline-block"> ClickUp</span>
    <span class="floating-chip" style="top:68%;right:5%;--chip-dur:8s;--chip-delay:0.8s"><img src="https://cdn.simpleicons.org/shopify/95bf47" style="width:14px;height:14px;display:inline-block"> Shopify</span>
    <span class="floating-chip" style="top:12%;right:18%;--chip-dur:12s;--chip-delay:3s;opacity:.45">Ahrefs vs Semrush</span>
    <span class="floating-chip" style="top:75%;left:18%;--chip-dur:13s;--chip-delay:1.6s;opacity:.4"><img src="https://cdn.simpleicons.org/figma/ffffff" style="width:14px;height:14px;display:inline-block"> Figma</span>
  </div>
"""


def inject_homepage_sections():
    """Inject new design sections into the existing homepage."""
    homepage = SITE / "index.html"
    html = homepage.read_text(encoding="utf-8")

    # 1. Add floating chips CSS if not already there
    if "floating-chip" not in html:
        html = html.replace("</style>", FLOATING_CHIPS_CSS + "\n</style>", 1)
        print("  + floating chip CSS added to homepage")

    # 2. Add floating chips HTML inside the hero section (after opening .hero tag)
    if "floating-chip" not in html or "chipFloat" not in html:
        html = re.sub(
            r'(<(?:section|div)[^>]*class="[^"]*hero[^"]*"[^>]*>)',
            r'\1\n' + FLOATING_CHIPS_HTML,
            html, count=1
        )
        print("  + floating chips HTML injected into hero")

    # 3. Remove old brand marquee if exists, then inject new one
    # Look for existing marquee-like sections
    html = re.sub(
        r'<!-- BRAND MARQUEE.*?(?=<!--\s*|<section|<div[^>]+id=")|$',
        '',
        html, flags=re.DOTALL
    )

    # 4. Remove old library / tool-grid section if exists
    html = re.sub(
        r'<!--\s*LIBRARY SECTION.*?(?=<!--\s*NEWSLETTER|<!--\s*WHY|<footer)',
        '',
        html, flags=re.DOTALL
    )

    # 5. Remove old newsletter/CTA section
    html = re.sub(
        r'<!--\s*(?:NEWSLETTER|CTA).*?(?=<footer)',
        '',
        html, flags=re.DOTALL
    )

    # 6. Inject new sections before </footer> or before <footer>
    if BRAND_MARQUEE.strip()[:40] not in html:
        html = re.sub(
            r'(<footer)',
            BRAND_MARQUEE + "\n" + LIBRARY_PREVIEW + "\n" + NEWSLETTER_SECTION + "\n" + r'\1',
            html, count=1
        )
        print("  + brand marquee, library preview, newsletter injected into homepage")

    # 7. Add sp-motion.js to homepage for animations
    if "sp-motion.js" not in html and "motion.js" not in html:
        html = html.replace("</body>", '<script src="/assets/sp-motion.js" defer></script>\n</body>', 1)

    homepage.write_text(html, encoding="utf-8")
    print("  homepage updated")


# ── main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Step 1: Copy shared assets ===")
    copy_assets()

    print("\n=== Step 2: Build design pages ===")
    for design_name, out_rel, canonical, title in PAGES:
        build_page(design_name, out_rel, canonical, title)

    print("\n=== Step 3: Inject homepage sections ===")
    inject_homepage_sections()

    print("\n=== Done ===")
    print("Pages built:", len(PAGES) + 1)
    print("Check: site/assets/sp-shared.css, site/deal-radar.html, site/roi.html, site/shortlist.html, site/404.html")
