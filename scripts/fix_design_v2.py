"""
Targeted fixes for design pages:

1. About page - orbit center: replace demo "S" box with real SVG logo mark
2. Homepage hero - upgrade old .grad-text typewriter to new sp-accent glint + cursor
3. All new design pages - replace /pages/ dead-end links with real working URLs

Run: uv run python scripts/fix_design_v2.py
"""
import re
from pathlib import Path

ROOT  = Path(__file__).resolve().parents[1]
SITE  = ROOT / "site"

# ── 1. About page: real logo in orbit center ──────────────────────────────
# Replace the pink "S" box with the actual SaaSpare SVG mark (compact version)
ORBIT_CORE_NEW = """<div class="orbit-core" style="background:none;box-shadow:none;width:80px;height:80px">
          <a href="/" style="display:flex;align-items:center;justify-content:center;width:100%;height:100%">
            <svg viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" style="width:80px;height:80px;filter:drop-shadow(0 0 24px rgba(233,69,96,.7))"><defs><clipPath id="abc_ct"><path d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></clipPath><clipPath id="abc_cb"><path d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/></clipPath></defs><path fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/><path fill="#ffffff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></svg>
          </a>
        </div>"""


def fix_about_orbit():
    about = SITE / "about.html"
    html  = about.read_text(encoding="utf-8", errors="replace")

    new_html = re.sub(
        r'<div class="orbit-core">[^<]*</div>',
        ORBIT_CORE_NEW,
        html, count=1
    )
    if new_html != html:
        about.write_text(new_html, encoding="utf-8")
        print("  about.html: orbit-core updated to real SVG logo")
    else:
        print("  about.html: orbit-core pattern not found (may already be fixed)")


# ── 2. Homepage: new glint typewriter in hero h1 ──────────────────────────
# Replace old .grad-text with new sp-accent + sp-tw-cursor
# Old: <span class="grad-text"><span id="typewriter">CRM Software</span></span>
# New: <span class="sp-accent sp-tw-outer"><span id="tw-word">CRM Software</span><span class="sp-tw-cursor"></span></span>

NEW_TW_SPAN = '<span class="sp-accent sp-tw-outer"><span id="tw-word">CRM Software</span><span class="sp-tw-cursor"></span></span>'

NEW_TW_CSS = """
/* ── NEW TYPEWRITER (design system) ───────────────────────────────── */
.sp-accent{
  background:linear-gradient(100deg,#ff416d 0%,#ff7a9a 35%,#ffd0dc 50%,#ff7a9a 65%,#ff416d 100%);
  background-size:300% 100%;
  -webkit-background-clip:text;background-clip:text;color:transparent;
  text-shadow:0 0 32px rgba(255,65,109,.30);
  animation:spGlint 3.6s linear infinite;
  padding-right:.05em;display:inline;
}
.sp-tw-cursor{display:inline-block;width:.05em;background:#ff416d;height:.85em;vertical-align:-.05em;margin-left:.05em;animation:spBlink 1s steps(2,end) infinite;box-shadow:0 0 14px #ff416d}
@keyframes spBlink{0%,50%{opacity:1}50.01%,100%{opacity:0}}
"""

NEW_TW_JS = """
/* ── NEW TYPEWRITER (design system) ── */
(function(){
  var WORDS = ["CRM Software","Project Management","Password Managers","Marketing Tools","SEO Software","Email Platforms","Help Desk Tools","Analytics Stacks","Finance Tools","Dev Tools"];
  var tw = document.getElementById('tw-word');
  if(!tw) return;
  var wIdx=0, cIdx=0, deleting=false;
  function spType(){
    var word = WORDS[wIdx];
    if(!deleting){
      cIdx++;
      tw.textContent = word.slice(0, cIdx);
      if(cIdx >= word.length){ deleting=true; setTimeout(spType, 1800); return; }
      setTimeout(spType, 70 + Math.random()*40);
    } else {
      cIdx--;
      tw.textContent = word.slice(0, cIdx);
      if(cIdx <= 0){ deleting=false; wIdx=(wIdx+1)%WORDS.length; setTimeout(spType, 350); return; }
      setTimeout(spType, 35);
    }
  }
  setTimeout(spType, 800);
})();
"""

OLD_TW_JS_PAT = re.compile(
    r"/\* TYPEWRITER \*/\s*const words=\[.*?setTimeout\(type,800\);",
    re.DOTALL
)
OLD_TW_CSS_PAT = re.compile(
    r'#typewriter::after\{[^}]+\}'
)


def fix_homepage_typewriter():
    idx  = SITE / "index.html"
    html = idx.read_text(encoding="utf-8", errors="replace")

    # Replace old CSS cursor with nothing (new cursor is .sp-tw-cursor)
    html = OLD_TW_CSS_PAT.sub('', html)

    # Add new CSS if not present
    if "sp-tw-cursor" not in html:
        html = html.replace("</style>", NEW_TW_CSS + "\n</style>", 1)

    # Replace old span in h1
    html = re.sub(
        r'<span class="grad-text"><span id="typewriter">[^<]*</span></span>',
        NEW_TW_SPAN,
        html, count=1
    )

    # Replace old JS typewriter with new one
    if OLD_TW_JS_PAT.search(html):
        html = OLD_TW_JS_PAT.sub(NEW_TW_JS.strip(), html)
    elif "tw-word" not in html:
        # Inject before closing </script> of the main script block
        html = html.replace("/* SITEMAP COUNT */", NEW_TW_JS + "\n/* SITEMAP COUNT */", 1)

    idx.write_text(html, encoding="utf-8")
    print("  index.html: typewriter upgraded to sp-accent glint + cursor")


# ── 3. All new design pages: fix dead /pages/ links ──────────────────────
# Replace href="/pages/" dead-ends with the best matching real page

# Generic real pages to use for category links
REAL_PAGES_BY_CONTEXT = {
    # ROI calculator - comparison links
    "roi.html": [
        (r'href="/pages/"', 'href="/pages/"'),   # keep as-is (it's the index)
        (r'href="/go/\w+"', None),               # keep real go links
    ],
}

# For all new pages, replace href="/pages/" with the actual library
# and fix any remaining placeholder links

LINK_FIXES = {
    # Shortlist page - tool links should go to real comparisons
    "shortlist.html": [
        ('href="/pages/"', 'href="/pages/"'),  # library - fine
        ('href="/go/1password"', 'href="/go/1password"'),
        ('href="/go/bitwarden"', 'href="/go/bitwarden"'),
        ('href="/go/hubspot"', 'href="/go/hubspot"'),
        ('href="/go/clickup"', 'href="/go/clickup"'),
    ],
    # ROI - comparison link
    "roi.html": [
        # The "View Comparison →" link at bottom needs a real URL
        ('href="/pages/"', 'href="/pages/1password-vs-bitwarden-which-is-better-in-2026"'),
    ],
    # 404 - recovery links need to be real
    "404.html": [
        ('href="/pages/"', 'href="/pages/"'),  # already correct
    ],
}

# Dead link patterns across ALL new design pages
GLOBAL_DEAD_LINK_FIXES = [
    # Shortlist Builder link in sidebar
    (r'href="shortlist\.html"',   'href="/shortlist"'),
    (r'href="roi\.html"',         'href="/roi"'),
    (r'href="library\.html"',     'href="/pages/"'),
    (r'href="deal-radar\.html"',  'href="/deal-radar"'),
    (r'href="about\.html"',       'href="/about"'),
    (r'href="article\.html"',     'href="/pages/"'),
    (r'href="index\.html"',       'href="/"'),
    (r'href="newsletter\.html"',  'href="/newsletter"'),
    (r'href="contact\.html"',     'href="/contact"'),
    (r'href="privacy\.html"',     'href="/privacy"'),
    (r'href="disclosure\.html"',  'href="/affiliate-disclosure"'),
]

NEW_DESIGN_PAGES = [
    "pages/index.html",
    "about.html",
    "deal-radar.html",
    "roi.html",
    "shortlist.html",
    "newsletter.html",
    "contact.html",
    "404.html",
]


def fix_all_links():
    fixed = 0
    for rel in NEW_DESIGN_PAGES:
        p    = SITE / rel
        html = p.read_text(encoding="utf-8", errors="replace")
        new  = html

        for pat, rep in GLOBAL_DEAD_LINK_FIXES:
            new = re.sub(pat, rep, new)

        # ROI page: the single "View Comparison →" should link to a real comparison
        if rel == "roi.html":
            new = new.replace(
                '<a href="/pages/" class="sp-btn sp-btn-ghost">View Comparison &rarr;</a>',
                '<a href="/pages/1password-vs-bitwarden-which-is-better-in-2026" class="sp-btn sp-btn-ghost">View Comparison &rarr;</a>'
            )
            # Also add real tool options to the dropdown
            new = new.replace(
                "<option>1Password</option><option>Bitwarden</option><option>HubSpot</option>",
                "<option>1Password</option><option>Bitwarden</option><option>HubSpot</option><option>NordVPN</option><option>Semrush</option><option>ClickUp</option><option>Notion</option><option>Shopify</option>"
            )

        # Shortlist page: tool CTAs should link to real pages
        if rel == "shortlist.html":
            new = new.replace(
                '<a href="/pages/" class="sp-btn sp-btn-primary glint-button" style="width:100%">Open Shortlist Builder &rarr;</a>',
                '<a href="/shortlist" class="sp-btn sp-btn-primary glint-button" style="width:100%">Open Shortlist Builder &rarr;</a>'
            )

        # 404 page: navigation cards link to real pages
        if rel == "404.html":
            new = new.replace('href="/pages/"', 'href="/pages/"')  # library = fine

        if new != html:
            p.write_text(new, encoding="utf-8")
            fixed += 1
            print(f"  links fixed: {rel}")

    print(f"  {fixed} pages had dead links updated")


# ── main ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Fix 1: About orbit center — real SVG logo ===")
    fix_about_orbit()

    print("\n=== Fix 2: Homepage — new glint typewriter ===")
    fix_homepage_typewriter()

    print("\n=== Fix 3: All new pages — fix dead links ===")
    fix_all_links()

    print("\nDone.")
