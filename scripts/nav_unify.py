#!/usr/bin/env python3
"""
nav_unify.py — Normalise every buyer page in site/pages/ to use the
current animated logo + consistent nav links.

There are three legacy logo variants this script fixes:
  1. logo-bars  (3 coloured <span> bars)  — oldest, ~652 pages
  2. 36x44 SVG  (two rectangles, markDrift anim) — mid, ~121 pages
  3. 180x180 SVG (animated) but with old CSS  — may exist

The canonical nav HTML and CSS are extracted from the "good" pages that
already use the 180x180 logo.

Run:  uv run python scripts/nav_unify.py
Dry:  uv run python scripts/nav_unify.py --check
"""
from __future__ import annotations
import argparse, pathlib, re, sys

# ── canonical fragments ─────────────────────────────────────────────────────

LOGO_SVG = (
    '<svg class="logo-mark" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<defs>'
    '<clipPath id="ct"><path d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></clipPath>'
    '<clipPath id="cb"><path d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/></clipPath>'
    '<mask id="sm1"><path d="M162,2 C100,2 58,44 55,60 C50,78 85,90 55,118" stroke="white" stroke-width="90" stroke-linecap="butt" fill="none" stroke-dasharray="1000 1000" stroke-dashoffset="1000"><animate attributeName="stroke-dashoffset" values="1000;0;0;1000;1000" keyTimes="0;0.20;0.721;0.722;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></path></mask>'
    '<mask id="sm2"><path d="M200,56 C165,62 130,90 128,118 C125,142 68,164 5,186" stroke="white" stroke-width="90" stroke-linecap="butt" fill="none" stroke-dasharray="1000 1000" stroke-dashoffset="1000"><animate attributeName="stroke-dashoffset" values="1000;1000;0;0;1000;1000" keyTimes="0;0.24;0.44;0.961;0.962;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></path></mask>'
    '<mask id="sm3"><path d="M162,2 C100,2 58,44 55,60 C50,78 85,90 55,118" stroke="white" stroke-width="90" stroke-linecap="butt" fill="none" stroke-dasharray="1000 1000" stroke-dashoffset="1000"><animate attributeName="stroke-dashoffset" values="1000;1000;0;0" keyTimes="0;0.52;0.72;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></path></mask>'
    '<mask id="sm4"><path d="M200,56 C165,62 130,90 128,118 C125,142 68,164 5,186" stroke="white" stroke-width="90" stroke-linecap="butt" fill="none" stroke-dasharray="1000 1000" stroke-dashoffset="1000"><animate attributeName="stroke-dashoffset" values="1000;1000;0;0" keyTimes="0;0.76;0.96;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></path></mask>'
    '</defs>'
    '<path class="mark-bot" fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/>'
    '<path class="mark-top" fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/>'
    '<g class="wave-top" clip-path="url(#ct)" mask="url(#sm1)"><rect width="180" height="180" fill="#e94560"/></g>'
    '<g class="wave-top2" clip-path="url(#ct)" mask="url(#sm3)"><rect width="180" height="180" fill="#fff"/></g>'
    '<g class="wave-bot" clip-path="url(#cb)" mask="url(#sm2)"><rect width="180" height="180" fill="#fff"/></g>'
    '<g class="wave-bot2" clip-path="url(#cb)" mask="url(#sm4)"><rect width="180" height="180" fill="#e94560"/></g>'
    '</svg>'
)

# Canonical nav HTML (buyer pages — all absolute URLs, /pages/ context)
NAV_HTML = (
    '<nav id="nav">\n'
    '  <a href="https://saaspare.org" class="logo">\n'
    '    ' + LOGO_SVG + '\n'
    '    <span class="logo-text">Saa<em>Spare</em></span>\n'
    '  </a>\n'
    '  <a href="https://saaspare.org/pages/" class="nav-link keep">Comparisons</a>\n'
    '  <a href="https://saaspare.org/pages/saas-roi-calculator" class="nav-link">ROI Calc</a>\n'
    '  <a href="https://saaspare.org/pages/" class="nav-cta">Browse Tools -></a>\n'
    '</nav>'
)

# Canonical logo/nav CSS block (single minified line per property group)
LOGO_CSS = (
    '.logo-mark{height:26px;width:auto;flex-shrink:0;overflow:visible;animation:markGlow 4s ease-in-out infinite}'
    '.mark-top,.mark-bot{transform-box:fill-box;transform-origin:center;transition:transform .5s cubic-bezier(.34,1.56,.64,1)}'
    '.wv{pointer-events:none;transition:opacity .3s}'
    '@keyframes markGlow{0%,100%{filter:drop-shadow(0 0 0px rgba(233,69,96,0))}50%{filter:drop-shadow(0 3px 18px rgba(233,69,96,.6))}}'
    '.logo:hover .logo-mark{animation:none}'
    '.logo:hover .mark-top{transform:translateX(26px);filter:drop-shadow(-2px 0 6px rgba(0,0,0,.9)) drop-shadow(0 0 14px rgba(233,69,96,.5))}'
    '.logo:hover .mark-bot{transform:translateX(-26px);filter:drop-shadow(2px 0 6px rgba(0,0,0,.9)) drop-shadow(0 0 14px rgba(233,69,96,.5))}'
    '.logo:hover .wv,.logo:hover .wave-top2,.logo:hover .wave-bot2{opacity:0}'
)

LOGO_BASE_CSS = (
    '.logo{display:flex;align-items:center;gap:9px;margin-right:auto}'
)

LOGO_TEXT_CSS = (
    '.logo-text{font-weight:800;font-size:1.05rem;letter-spacing:-.5px;color:#fff;font-family:\'Inter\',system-ui,sans-serif}'
    '.logo-text em{color:#e94560;font-style:normal}'
)

# ── regex patterns for old variants ─────────────────────────────────────────

# Variant 1: logo-bars CSS (matches the full block from .logo-bars{ to the end of .logo-text em rule)
RE_LOGO_BARS_CSS = re.compile(
    r'\.logo-bars\{[^}]*\}.*?\.logo-text em\{[^}]*\}',
    re.DOTALL
)
# Variant 1: logo-bars HTML
RE_LOGO_BARS_HTML = re.compile(
    r'<div class="logo-bars"><span></span><span></span><span></span></div>\s*'
    r'<div class="logo-text">Saa<em>Spare</em></div>',
    re.DOTALL
)

# Variant 2: markDrift CSS (matches from .logo-mark{height:22 to end of .logo:hover .logo-mark rule)
RE_MARKDRIFT_CSS = re.compile(
    r'\.logo-mark\{height:22px[^}]*\}.*?\.logo:hover \.logo-mark\{[^}]*\}',
    re.DOTALL
)
# Variant 2: 36x44 SVG
RE_SMALL_SVG = re.compile(
    r'<svg class="logo-mark" viewBox="0 0 36 44"[^>]*>.*?</svg>',
    re.DOTALL
)
# Variant 2: may have <span class="logo-text"> already — keep it
RE_LOGO_TEXT_DIV = re.compile(
    r'<div class="logo-text">Saa<em>Spare</em></div>'
)

# Old logo-text CSS (multi-line style, no font-family)
RE_OLD_LOGO_TEXT_CSS = re.compile(
    r'\.logo-text\{font-weight:800;font-size:1\.05rem;letter-spacing:-\.5px;color:#fff\}\s*'
    r'\.logo-text em\{color:#e94560;font-style:normal\}'
)

# Already-correct (180x180) but may still have markGlow CSS without transform-box
RE_OLD_MARKGLOW_CSS = re.compile(
    r'\.logo-mark\{height:26px;[^}]+animation:markGlow 4s[^}]+\}'
    r'(?!.*transform-box)',  # negative lookahead: only old version lacking transform-box
    re.DOTALL
)

# ── per-page processor ───────────────────────────────────────────────────────

def needs_update(html: str) -> bool:
    """Quick heuristic — does this page need a logo update?"""
    return (
        'logo-bars' in html
        or 'viewBox="0 0 36 44"' in html
        or 'markDrift' in html
    )


def fix_page(html: str) -> tuple[str, list[str]]:
    """Return (updated_html, list_of_changes). If nothing changed list is empty."""
    changes: list[str] = []

    # ── 1. Fix logo-bars variant ────────────────────────────────────────────
    if 'logo-bars' in html:
        # Replace CSS block
        new_css = LOGO_CSS + '\n' + LOGO_BASE_CSS + '\n' + LOGO_TEXT_CSS
        m = RE_LOGO_BARS_CSS.search(html)
        if m:
            html = html[:m.start()] + new_css + html[m.end():]
            changes.append('css:logo-bars→markGlow')

        # Replace HTML logo area
        m2 = RE_LOGO_BARS_HTML.search(html)
        if m2:
            replacement = LOGO_SVG + '\n    <span class="logo-text">Saa<em>Spare</em></span>'
            html = html[:m2.start()] + replacement + html[m2.end():]
            changes.append('html:logo-bars→new-svg')

    # ── 2. Fix 36x44 SVG variant ────────────────────────────────────────────
    if 'viewBox="0 0 36 44"' in html or 'markDrift' in html:
        # Replace CSS
        m = RE_MARKDRIFT_CSS.search(html)
        if m:
            html = html[:m.start()] + LOGO_CSS + html[m.end():]
            changes.append('css:markDrift→markGlow')

        # Replace SVG
        m2 = RE_SMALL_SVG.search(html)
        if m2:
            html = html[:m2.start()] + LOGO_SVG + html[m2.end():]
            changes.append('html:36x44→180x180')

        # Replace any <div class="logo-text"> with <span>
        if RE_LOGO_TEXT_DIV.search(html):
            html = RE_LOGO_TEXT_DIV.sub(
                '<span class="logo-text">Saa<em>Spare</em></span>', html
            )
            changes.append('html:logo-text-div→span')

        # Update old logo-text CSS to include font-family
        if RE_OLD_LOGO_TEXT_CSS.search(html):
            html = RE_OLD_LOGO_TEXT_CSS.sub(LOGO_TEXT_CSS, html)
            changes.append('css:logo-text+font-family')

    # ── 3. Ensure nav HTML uses <span> not <div> for logo-text (global) ─────
    if '<div class="logo-text">' in html:
        html = html.replace(
            '<div class="logo-text">Saa<em>Spare</em></div>',
            '<span class="logo-text">Saa<em>Spare</em></span>'
        )
        changes.append('html:logo-text-div→span(global)')

    return html, changes


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description='Unify nav logo across all buyer pages')
    ap.add_argument('--check', action='store_true', help='Dry-run: report without writing')
    args = ap.parse_args()

    pages_dir = pathlib.Path(__file__).resolve().parent.parent / 'site' / 'pages'
    if not pages_dir.is_dir():
        sys.exit(f'[nav_unify] pages dir not found: {pages_dir}')

    html_files = sorted(pages_dir.glob('*.html'))
    total = len(html_files)
    updated = 0
    skipped = 0

    for fp in html_files:
        try:
            raw = fp.read_bytes()
            # Detect encoding (BOM or UTF-8)
            if raw.startswith(b'\xef\xbb\xbf'):
                enc = 'utf-8-sig'
            else:
                enc = 'utf-8'
            html = raw.decode(enc, errors='replace')
        except Exception as e:
            print(f'[WARN] could not read {fp.name}: {e}')
            continue

        if not needs_update(html):
            skipped += 1
            continue

        new_html, changes = fix_page(html)

        if not changes:
            skipped += 1
            continue

        updated += 1
        if args.check:
            print(f'[CHECK] {fp.name}: {", ".join(changes)}')
        else:
            fp.write_bytes(new_html.encode(enc))
            print(f'[FIXED] {fp.name}: {", ".join(changes)}')

    print(f'\n{"[DRY RUN] " if args.check else ""}Done: {updated} updated, {skipped} skipped ({total} total pages)')


if __name__ == '__main__':
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    main()
