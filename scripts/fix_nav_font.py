#!/usr/bin/env python3
"""Fix font (Inter->Plus Jakarta Sans), nav logo on /pages/, add Categories everywhere."""
import os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LOGO_SVG = (
    '<svg class="logo-mark" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<defs><clipPath id="ct"><path d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 '
    '47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 '
    'C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/>'
    '</clipPath><clipPath id="cb"><path d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 '
    'C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 '
    '134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 '
    'L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 '
    'C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/></clipPath>'
    '<mask id="sm1"><rect x="-400" y="-50" width="400" height="300" fill="white">'
    '<animate attributeName="x" values="-400;0;0;180;180" keyTimes="0;0.20;0.61;0.62;1" '
    'dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask>'
    '<mask id="sm2"><rect x="180" y="-50" width="400" height="300" fill="white">'
    '<animate attributeName="x" values="180;180;-220;-220;180;180" keyTimes="0;0.21;0.41;0.82;0.83;1" '
    'dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask>'
    '<mask id="sm3"><rect x="-400" y="-50" width="400" height="300" fill="white">'
    '<animate attributeName="x" values="-400;-400;0;0" keyTimes="0;0.42;0.62;1" '
    'dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask>'
    '<mask id="sm4"><rect x="180" y="-50" width="400" height="300" fill="white">'
    '<animate attributeName="x" values="180;180;-220;-220" keyTimes="0;0.63;0.83;1" '
    'dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask></defs>'
    '<path class="mark-bot" fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 '
    'C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 '
    '134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 '
    'L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 '
    'C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/>'
    '<path class="mark-top" fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 '
    'C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 '
    'L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/>'
    '<g class="wave-top" clip-path="url(#ct)" mask="url(#sm1)"><rect width="180" height="180" fill="#e94560"/></g>'
    '<g class="wave-top2" clip-path="url(#ct)" mask="url(#sm3)"><rect width="180" height="180" fill="#fff"/></g>'
    '<g class="wave-bot" clip-path="url(#cb)" mask="url(#sm2)"><rect width="180" height="180" fill="#fff"/></g>'
    '<g class="wave-bot2" clip-path="url(#cb)" mask="url(#sm4)"><rect width="180" height="180" fill="#e94560"/></g>'
    '</svg>'
)

def fix_inter_font(c):
    c = c.replace("family=Inter:wght@400;500;600;700;800;900", "family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900")
    c = c.replace("family=Inter:ital,opsz,wght@1,14..32,400..700&display=swap", "family=Plus+Jakarta+Sans:ital,wght@0,400;0,700;1,400&display=swap")
    c = c.replace("family=Inter:ital", "family=Plus+Jakarta+Sans:ital")
    c = c.replace("font-family:'Inter',", "font-family:'Plus Jakarta Sans',")
    return c

def add_categories(c):
    if "/categories" in c:
        return c
    # Insert after Comparisons link
    return re.sub(
        r'(<a href="/pages/" class="nav-link[^"]*">Comparisons</a>)',
        r'\1\n  <a href="/categories" class="nav-link">Categories</a>',
        c
    )

def fix_shortlist_link(c):
    return c.replace('href="/shortlist.html" class="nav-cta"', 'href="/shortlist" class="nav-cta"')


# ── 1. Homepage ──────────────────────────────────────────────────────────────
path = ROOT / "site" / "index.html"
c = path.read_text(encoding="utf-8")

# Fix font
c = fix_inter_font(c)

# Fix nav — replace the mismatched nav links from SEO sprint
# The SEO sprint replaced standard links with: Pricing Index, Free Trials, Glossary, Spend Audit
# Restore proper nav
old_nav_links = re.search(
    r'(<a href="/pages/saas-pricing-index" class="nav-link">.*?<a href="/shortlist" class="nav-cta">Build Shortlist &#8594;</a>)',
    c, re.DOTALL
)
if old_nav_links:
    proper_links = (
        '  <a href="/pages/" class="nav-link">Comparisons</a>\n'
        '  <a href="/categories" class="nav-link">Categories</a>\n'
        '  <a href="/shortlist" class="nav-link">Shortlist Builder</a>\n'
        '  <a href="/deal-radar" class="nav-link">Deal Radar</a>\n'
        '  <a href="/about" class="nav-link">About</a>\n'
        '  <a href="/shortlist" class="nav-cta">Build Shortlist &#8594;</a>'
    )
    c = c.replace(old_nav_links.group(0), proper_links)
else:
    c = add_categories(c)

path.write_text(c, encoding="utf-8")
print("Fixed site/index.html: font + nav links restored")


# ── 2. /pages/index.html nav logo ───────────────────────────────────────────
path = ROOT / "site" / "pages" / "index.html"
c = path.read_text(encoding="utf-8")

# Replace text-only ss-logo with full SVG
if 'class="ss-logo">SaaSpare</a>' in c:
    c = c.replace(
        '<a href="/" class="ss-logo">SaaSpare</a>',
        f'<a href="/" class="logo">{LOGO_SVG}<span class="logo-text">Saa<em>Spare</em></span></a>'
    )
    # Add logo CSS before nav CSS
    if ".logo{" not in c:
        logo_css = (
            ".logo{display:flex;align-items:center;gap:9px;margin-right:auto}"
            ".logo-mark{height:26px;width:auto;flex-shrink:0;overflow:visible}"
            ".logo-text{font-weight:800;font-size:1.05rem;letter-spacing:-.4px;color:#fff}"
            ".logo-text em{color:#e94560;font-style:normal}"
        )
        c = c.replace("nav#nav{", logo_css + "\nnav#nav{", 1)
    print("  Replaced ss-logo with SVG logo")

# Fix arrow in CTA
c = c.replace("Build Shortlist ->", "Build Shortlist &#8594;")

# Add Categories
c = add_categories(c)

path.write_text(c, encoding="utf-8")
print("Fixed site/pages/index.html: SVG logo, Categories, arrow")


# ── 3. All static site pages ─────────────────────────────────────────────────
static = [
    "site/about.html", "site/methodology.html", "site/contact.html",
    "site/privacy.html", "site/deal-radar.html", "site/shortlist.html",
    "site/affiliate-disclosure.html",
]

for rel in static:
    p = ROOT / rel
    if not p.exists():
        continue
    c = p.read_text(encoding="utf-8")
    orig = c
    c = fix_inter_font(c)
    c = add_categories(c)
    c = fix_shortlist_link(c)
    if c != orig:
        p.write_text(c, encoding="utf-8")
        print(f"Fixed {rel}")


# ── 4. Strategic pages in site/pages/ ────────────────────────────────────────
strategic = [
    "saas-spend-audit.html", "coupon-verification-policy.html",
    "how-saaspare-ranks-tools.html", "report-outdated-pricing.html",
    "request-a-comparison.html", "saas-glossary.html",
    "saas-pricing-changes.html", "saas-stack-audit-checkout.html",
    "state-of-saas-pricing-2026.html", "weekly-saas-deal-digest.html",
]

for fn in strategic:
    p = ROOT / "site" / "pages" / fn
    if not p.exists():
        continue
    c = p.read_text(encoding="utf-8")
    orig = c
    c = fix_inter_font(c)
    c = add_categories(c)
    c = fix_shortlist_link(c)
    if c != orig:
        p.write_text(c, encoding="utf-8")
        print(f"Fixed site/pages/{fn}")


# ── 5. Update _page_shell.py font for future pages ───────────────────────────
shell = ROOT / "scripts" / "_page_shell.py"
c = shell.read_text(encoding="utf-8")
if "Inter" in c:
    c = c.replace(
        "family=Inter:wght@400;500;600;700;800;900&family=Inter:ital,opsz,wght@1,14..32,400..700&display=swap",
        "family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap"
    )
    c = c.replace("font-family:'Inter',", "font-family:'Plus Jakarta Sans',")
    shell.write_text(c, encoding="utf-8")
    print("Fixed scripts/_page_shell.py: font")

print("\nAll fixes applied.")
