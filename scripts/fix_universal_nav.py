"""
fix_universal_nav.py — Apply the perfect shortlist nav to ALL pages.

The shortlist.html nav is the canonical design:
- Animated SVG logo mark (red/white, glows on hover)
- Fixed position, transparent → frosted glass on scroll
- Links: Comparisons | Shortlist Builder | Deal Radar | About
- CTA: Build Shortlist →

This script:
1. Injects universal nav CSS into every page <head>
2. Replaces ALL existing nav elements with the canonical nav HTML
3. Ensures body padding so content isn't hidden behind fixed nav
4. Handles index.html, pages/, authors/, blog/, and key pages
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

# ── Universal nav CSS (self-contained, works on any page) ────────────────────
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
nav#sp-nav .sp-nav-link:hover{color:#fff}
nav#sp-nav .sp-nav-link.active{color:#fff;font-weight:600;position:relative}
nav#sp-nav .sp-nav-link.active::after{content:"";position:absolute;left:14px;right:14px;bottom:-2px;height:2px;border-radius:2px;background:linear-gradient(90deg, transparent, var(--sp-red), transparent);box-shadow:0 0 10px var(--sp-red)}
.sp-nav-cta{background:linear-gradient(135deg,#e94560,#c73652);color:#fff;
  padding:.44rem 1.15rem;border-radius:100px;font-weight:700;font-size:.78rem;
  box-shadow:0 4px 16px rgba(233,69,96,.4);margin-left:6px;
  transition:transform .15s,box-shadow .15s;white-space:nowrap;text-decoration:none}
.sp-nav-cta:hover{transform:translateY(-1px);box-shadow:0 8px 24px rgba(233,69,96,.55)}
.sp-nav-spacer{height:72px} /* overridden to 0 on homepage */
/* Remove old nav styles that cause bracket/black-bar glitches */
.sp-bg{display:none!important}
nav.sp-topnav{display:none!important}
</style>
<script>
(function(){
  window.addEventListener('scroll',function(){
    var nav=document.getElementById('sp-nav');
    if(nav){nav.classList.toggle('scrolled',window.scrollY>20);}
  },{passive:true});

  function highlightNav(){
    var path=window.location.pathname;
    var override=document.body.getAttribute('data-nav');
    var links=document.querySelectorAll('nav#sp-nav .sp-nav-link');
    var best=null,bestLen=0;
    links.forEach(function(a){
      var href=a.getAttribute('href');
      if(!href||href==='/') return;
      if(override){if(href===override){best=a;}return;}
      if(path===href||path.indexOf(href.replace(/\/$/,'')+'/')===0){
        if(href.length>bestLen){best=a;bestLen=href.length;}
      }
    });
    if(best){best.classList.add('active');}
  }
  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',highlightNav);}else{highlightNav();}
})();
</script>"""

# ── Universal nav HTML ────────────────────────────────────────────────────────
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
  <a href="/roi" class="sp-nav-link">ROI Calculator</a>
  <a href="/shortlist" class="sp-nav-link">Shortlist Builder</a>
  <a href="/deal-radar" class="sp-nav-link">Deal Radar</a>
  <a href="/about" class="sp-nav-link">About</a>
  <a href="/shortlist" class="sp-nav-cta">Build Shortlist &#8594;</a>
</nav>
<div class="sp-nav-spacer"></div>"""

# ── Patterns to find and replace existing navs ────────────────────────────────
# These patterns match any existing nav we've used across waves
OLD_NAV_PATTERNS = [
    # sp-topnav style (waves 19-26)
    re.compile(
        r'<nav\s+class=["\']sp-topnav["\'][^>]*>.*?</nav>',
        re.DOTALL
    ),
    # Old nav#nav from shortlist-style pages
    re.compile(
        r'<nav\s+id=["\']nav["\'][^>]*>.*?</nav>',
        re.DOTALL
    ),
    # sp-nav already (idempotent - skip if already correct)
    re.compile(
        r'<nav\s+id=["\']sp-nav["\'][^>]*>.*?</nav>\s*<div\s+class=["\']sp-nav-spacer["\']></div>',
        re.DOTALL
    ),
]

# Marker so we don't double-inject CSS
CSS_MARKER = 'id="sp-nav-css"'
NAV_MARKER = 'id="sp-nav"'

def fix_page(path: Path) -> bool:
    """Inject universal nav CSS and replace nav element. Returns True if changed."""
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
        original = html

        # Remove any redundant template-baked <nav class="sp-nav"> duplicates
        # (these stack below the universal nav#sp-nav and cause double-nav bug)
        dup_pat = re.compile(r'\s*<nav\s+class=["\']sp-nav["\'][^>]*>.*?</nav>', re.DOTALL)
        if NAV_MARKER in html and dup_pat.search(html):
            html = dup_pat.sub('', html)

        # Upgrade outdated nav CSS/JS block (missing active-link underglow) in place
        old_css_pat = re.compile(
            r'<style id="sp-nav-css">.*?</script>',
            re.DOTALL
        )
        if CSS_MARKER in html and 'sp-nav-link.active::after' not in html:
            if old_css_pat.search(html):
                html = old_css_pat.sub(NAV_CSS, html, count=1)

        # Upgrade navs missing the ROI Calculator link (June 2026 redesign)
        if NAV_MARKER in html and '"/roi" class="sp-nav-link"' not in html:
            html = html.replace(
                '<a href="/pages/" class="sp-nav-link">Comparisons</a>',
                '<a href="/pages/" class="sp-nav-link">Comparisons</a>\n'
                '  <a href="/roi" class="sp-nav-link">ROI Calculator</a>', 1)

        # Skip if already has new nav, current CSS, and no duplicate (idempotent)
        if NAV_MARKER in html and CSS_MARKER in html and 'sp-nav-link.active::after' in html:
            if html != original:
                path.write_text(html, encoding="utf-8")
                return True
            return False

        # 1. Inject CSS before </head> if not already present
        if CSS_MARKER not in html:
            html = html.replace("</head>", NAV_CSS + "\n</head>", 1)

        # 2. Replace existing nav (try each pattern)
        nav_replaced = False
        for pat in OLD_NAV_PATTERNS:
            if pat.search(html):
                # Replace only the first nav found
                html = pat.sub(NAV_HTML, html, count=1)
                nav_replaced = True
                break

        # 3. If no nav found, inject after <body...>
        if not nav_replaced and NAV_MARKER not in html:
            if re.search(r'<body[^>]*>', html):
                html = re.sub(r'(<body[^>]*>)', r'\1\n' + NAV_HTML, html, count=1)
            elif '</head>' in html:
                # <body> tag itself is missing (seen on 5 pages, Aug 2026) -
                # add it rather than silently doing nothing.
                html = html.replace(
                    '</head>',
                    '</head>\n<body style="background:#050407;color:rgba(255,248,245,.88)">\n' + NAV_HTML,
                    1)
            elif CSS_MARKER in html:
                # Neither </head> nor <body> present - insert right after the
                # nav CSS/JS block, which is the last head-level content.
                css_block = re.search(r'<style id="sp-nav-css">.*?</script>', html, re.DOTALL)
                if css_block:
                    insert_at = css_block.end()
                    html = (html[:insert_at]
                            + '\n</head>\n<body style="background:#050407;color:rgba(255,248,245,.88)">\n'
                            + NAV_HTML + '\n' + html[insert_at:])

        # 4. Remove stray <div class="sp-bg"> elements (cause bracket glitch)
        html = re.sub(r'<div\s+class=["\']sp-bg["\'][^>]*>\s*</div>', '', html)
        html = re.sub(r'<div\s+class=["\']sp-bg["\'][^>]*/>', '', html)

        if html != original:
            path.write_text(html, encoding="utf-8")
            return True
        return False

    except Exception as e:
        print(f"  ERROR {path.name}: {e}")
        return False


def main():
    targets = []

    # All HTML in pages/, blog/, authors/
    for subdir in ["pages", "blog", "authors"]:
        targets.extend((SITE / subdir).glob("*.html"))

    # Key root pages
    for name in ["index.html", "about.html", "contact.html", "deal-radar.html",
                 "newsletter.html", "404.html", "media-kit.html",
                 "privacy.html", "terms.html", "methodology.html"]:
        p = SITE / name
        if p.exists():
            targets.append(p)

    # Skip shortlist.html — it already has the perfect nav
    targets = [t for t in targets if t.name != "shortlist.html"]

    total = len(targets)
    updated = 0
    errors = 0

    print(f"Universal nav fix — scanning {total} pages...")
    print()

    for path in targets:
        changed = fix_page(path)
        if changed:
            updated += 1
            if updated <= 20:
                print(f"  [OK] {path.parent.name}/{path.name}")
            elif updated == 21:
                print(f"  ... (showing first 20, continuing silently)")

    print()
    print(f"Done: {updated}/{total} pages updated, {errors} errors")
    print()
    print("What was fixed:")
    print("  - Universal animated SVG logo nav injected on all pages")
    print("  - Transparent→frosted glass scroll behaviour")
    print("  - sp-bg div removed (was causing bracket/black-bar glitch)")
    print("  - Old sp-topnav hidden via CSS")
    print("  - 72px spacer added to prevent content hiding behind fixed nav")
    print()
    print("Shortlist.html: unchanged (already has the perfect nav)")


if __name__ == "__main__":
    main()
