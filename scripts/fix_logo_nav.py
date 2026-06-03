"""
fix_logo_nav.py — Ensure every real page has the correct SaaSpare nav with animated SVG logo.

Fixes:
1. Pages with nav but OLD logo (no mark-top SVG) → replace nav HTML with canonical
2. Pages missing nav entirely (except skip list) → inject full nav
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

# Pages that intentionally have no nav or a custom nav — skip them
SKIP_PAGES = {
    "shortlist.html",          # has its own custom nav
    "fo-verify.html",          # verification page, keep minimal
    "fo-verify-c0ceba67-f661-491b-9895-78e0a0a9eb9f.html",
    "ph-preview-1.html",       # internal preview pages
    "ph-preview-2.html",
    "ph-preview-3.html",
}

# ── Canonical nav CSS ─────────────────────────────────────────────────────────
NAV_CSS = """<style id="sp-nav-css">
/* ── SaaSpare Universal Nav ───────────────────────────────────────────────── */
:root{--sp-red:#e94560;--sp-red2:#c73652;--sp-border:rgba(255,255,255,.07)}
nav#sp-nav{position:fixed;top:0;left:0;right:0;z-index:9999;padding:.9rem 2rem;
  display:flex;align-items:center;gap:4px;transition:all .4s ease;
  background:transparent;border-bottom:none}
nav#sp-nav.scrolled{background:rgba(7,7,13,.88);border-bottom:1px solid var(--sp-border);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px)}
.sp-nav-logo{display:flex;align-items:center;gap:9px;margin-right:auto;text-decoration:none}
.sp-nav-mark{height:26px;width:auto;flex-shrink:0;overflow:visible;
  animation:spMarkGlow 4s ease-in-out infinite}
.sp-nav-mark .mark-top,.sp-nav-mark .mark-bot{transform-box:fill-box;transform-origin:center;
  transition:transform .5s cubic-bezier(.34,1.56,.64,1)}
.sp-nav-logo:hover .mark-top{transform:translateX(26px)}
.sp-nav-logo:hover .mark-bot{transform:translateX(-26px)}
@keyframes spMarkGlow{
  0%,100%{filter:drop-shadow(0 0 0px rgba(233,69,96,0))}
  50%{filter:drop-shadow(0 3px 18px rgba(233,69,96,.6))}}
.sp-nav-wordmark{font-weight:800;font-size:1.05rem;letter-spacing:-.4px;color:#fff}
.sp-nav-wordmark em{color:#e94560;font-style:normal}
nav#sp-nav .sp-nav-link{color:rgba(255,248,245,.42);font-size:.8rem;padding:.38rem .82rem;
  border-radius:8px;font-weight:500;transition:color .18s;white-space:nowrap;text-decoration:none}
nav#sp-nav .sp-nav-link:hover,.sp-nav-link.active{color:#fff}
.sp-nav-cta{background:linear-gradient(135deg,#e94560,#c73652);color:#fff;
  padding:.44rem 1.15rem;border-radius:100px;font-weight:700;font-size:.78rem;
  box-shadow:0 4px 16px rgba(233,69,96,.4);margin-left:6px;
  transition:transform .15s,box-shadow .15s;white-space:nowrap;text-decoration:none}
.sp-nav-cta:hover{transform:translateY(-1px);box-shadow:0 8px 24px rgba(233,69,96,.55)}
.sp-nav-spacer{height:72px}
.sp-bg{display:none!important}
nav.sp-topnav{display:none!important}
</style>
<script>
(function(){
  window.addEventListener('scroll',function(){
    var nav=document.getElementById('sp-nav');
    if(nav){nav.classList.toggle('scrolled',window.scrollY>40);}
  },{passive:true});
})();
</script>"""

# ── Canonical nav HTML ────────────────────────────────────────────────────────
NAV_HTML = """<nav id="sp-nav">
  <a href="/" class="sp-nav-logo" aria-label="SaaSpare home">
    <svg class="sp-nav-mark" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <defs>
        <clipPath id="sp-ct"><path d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></clipPath>
        <clipPath id="sp-cb"><path d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/></clipPath>
      </defs>
      <path class="mark-bot" fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/>
      <path class="mark-top" fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/>
    </svg>
    <span class="sp-nav-wordmark">Saa<em>Spare</em></span>
  </a>
  <a href="/pages/" class="sp-nav-link">Comparisons</a>
  <a href="/shortlist" class="sp-nav-link">Shortlist Builder</a>
  <a href="/deal-radar" class="sp-nav-link">Deal Radar</a>
  <a href="/about" class="sp-nav-link">About</a>
  <a href="/shortlist" class="sp-nav-cta">Build Shortlist &#8594;</a>
</nav>
<div class="sp-nav-spacer"></div>"""

# Pattern to match any existing sp-nav (to replace old ones)
OLD_NAV_PATTERN = re.compile(
    r'<nav\s+id=["\']sp-nav["\'][^>]*>.*?</nav>\s*(?:<div\s+class=["\']sp-nav-spacer["\'][^>]*></div>)?',
    re.DOTALL
)
OLD_CSS_PATTERN = re.compile(
    r'<style\s+id=["\']sp-nav-css["\']>.*?</style>\s*<script>.*?\(function\(\)\{.*?window\.addEventListener.*?\}\)\(\);.*?</script>',
    re.DOTALL
)

def has_svg_logo(html: str) -> bool:
    return "mark-top" in html and "sp-nav-mark" in html

def has_nav(html: str) -> bool:
    return 'id="sp-nav"' in html

def fix_page(path: Path) -> str:
    """Fix logo/nav on a single page. Returns status string."""
    if path.name in SKIP_PAGES:
        return "skip"

    try:
        html = path.read_text(encoding="utf-8", errors="replace")
        original = html

        if has_nav(html) and has_svg_logo(html):
            return "ok"  # Already correct

        if has_nav(html) and not has_svg_logo(html):
            # Nav exists but old logo — replace nav HTML and CSS block
            # Replace the nav CSS block
            if OLD_CSS_PATTERN.search(html):
                html = OLD_CSS_PATTERN.sub(NAV_CSS, html, count=1)
            elif 'id="sp-nav-css"' in html:
                html = re.sub(
                    r'<style\s+id=["\']sp-nav-css["\']>.*?</style>',
                    f'<style id="sp-nav-css">{NAV_CSS.split("</style>")[0].split("<style id")[1].split(">", 1)[1]}</style>',
                    html, flags=re.DOTALL, count=1
                )
            else:
                html = html.replace("</head>", NAV_CSS + "\n</head>", 1)

            # Replace the nav HTML
            if OLD_NAV_PATTERN.search(html):
                html = OLD_NAV_PATTERN.sub(NAV_HTML, html, count=1)

            if html != original:
                path.write_text(html, encoding="utf-8")
                return "fixed-logo"
            return "ok"

        if not has_nav(html):
            # Missing nav entirely — inject CSS into head and nav into body
            if 'id="sp-nav-css"' not in html:
                html = html.replace("</head>", NAV_CSS + "\n</head>", 1)
            # Inject nav after <body...>
            html = re.sub(r'(<body[^>]*>)', r'\1\n' + NAV_HTML, html, count=1)

            if html != original:
                path.write_text(html, encoding="utf-8")
                return "injected"
            return "ok"

    except Exception as e:
        print(f"  ERROR {path.name}: {e}")
        return "error"

    return "ok"

def main():
    targets = (
        list(SITE.glob("*.html")) +
        list((SITE / "pages").glob("*.html")) +
        list((SITE / "blog").glob("*.html")) +
        list((SITE / "authors").glob("*.html"))
    )

    fixed_logo = injected = skipped = errors = ok = 0
    print(f"Fixing logos/nav across {len(targets)} pages...")

    for path in targets:
        status = fix_page(path)
        if status == "fixed-logo":
            fixed_logo += 1
            if fixed_logo <= 20:
                print(f"  [LOGO] {path.parent.name}/{path.name}")
        elif status == "injected":
            injected += 1
            if injected <= 20:
                print(f"  [NAV]  {path.parent.name}/{path.name}")
        elif status == "skip":
            skipped += 1
        elif status == "error":
            errors += 1
        else:
            ok += 1

    print()
    print(f"Done: {fixed_logo} logo-upgraded | {injected} nav-injected | {ok} already correct | {skipped} skipped | {errors} errors")

if __name__ == "__main__":
    main()
