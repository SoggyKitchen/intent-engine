#!/usr/bin/env python3
"""SaaSpare v2 design system rollout.

Applies the v2 design system to a list of HTML files (or all of site/) by:

  1. Adding `class="v2"` to <body>
  2. Linking /assets/saaspare-v2.css after /assets/saaspare-ui.css
  3. Replacing the <nav> block with the canonical homepage nav
  4. Removing AI-slop pills (<div class="page-eyebrow">, .badge with .badge-dot, .ss-fresh)
  5. Removing duplicate <p class="aff-disclosure-pill"> (footer disclosure stays)
  6. Removing redundant <div class="trust-bar"> with green OK markers

Usage:
  python scripts/redesign_v2.py --check                   # report only, no writes
  python scripts/redesign_v2.py --files site/foo.html ... # apply to listed files
  python scripts/redesign_v2.py --all                     # apply to all site/*.html and site/pages/*.html
  python scripts/redesign_v2.py --pilot                   # apply to the 5 pilot pages

The script is idempotent — re-running on already-v2 pages is a no-op.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

CANONICAL_NAV = """<!-- NAV (canonical, v2) -->
<nav id="nav">
  <a href="/" class="logo">
    <svg class="logo-mark" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs><clipPath id="ct"><path d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></clipPath><clipPath id="cb"><path d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/></clipPath><mask id="sm1"><rect x="-400" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="-400;0;0;180;180" keyTimes="0;0.20;0.61;0.62;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask><mask id="sm2"><rect x="180" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="180;180;-220;-220;180;180" keyTimes="0;0.21;0.41;0.82;0.83;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask><mask id="sm3"><rect x="-400" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="-400;-400;0;0" keyTimes="0;0.42;0.62;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask><mask id="sm4"><rect x="180" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="180;180;-220;-220" keyTimes="0;0.63;0.83;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask></defs><path class="mark-bot" fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/><path class="mark-top" fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/><g class="wave-top" clip-path="url(#ct)" mask="url(#sm1)"><rect width="180" height="180" fill="#e94560"/></g><g class="wave-top2" clip-path="url(#ct)" mask="url(#sm3)"><rect width="180" height="180" fill="#fff"/></g><g class="wave-bot" clip-path="url(#cb)" mask="url(#sm2)"><rect width="180" height="180" fill="#fff"/></g><g class="wave-bot2" clip-path="url(#cb)" mask="url(#sm4)"><rect width="180" height="180" fill="#e94560"/></g></svg>
    <span class="logo-text">Saa<em>Spare</em></span>
  </a>
  <a href="/pages/" class="nav-link">Comparisons</a>
  <a href="/shortlist" class="nav-link">Shortlist Builder</a>
  <a href="/deal-radar" class="nav-link">Deal Radar</a>
  <a href="/about" class="nav-link">About</a>
  <a href="/shortlist" class="nav-cta">Build Shortlist &#8594;</a>
</nav>
"""

V2_CSS_LINK = '<link rel="stylesheet" href="/assets/saaspare-v2.css">'

NAV_RE = re.compile(r"<nav\b[^>]*>.*?</nav\s*>", re.IGNORECASE | re.DOTALL)
BODY_OPEN_RE = re.compile(r"<body\b([^>]*)>", re.IGNORECASE)

# Inline pill / badge removers
PAGE_EYEBROW_RE = re.compile(
    r'<div class="page-eyebrow"[^>]*>.*?</div\s*>', re.IGNORECASE | re.DOTALL)
HERO_EYEBROW_RE = re.compile(
    r'<div class="hero-eyebrow"[^>]*>.*?</div\s*>', re.IGNORECASE | re.DOTALL)
BADGE_DOT_RE = re.compile(
    r'<div class="badge"[^>]*>\s*<span class="badge-dot"></span>[^<]*</div\s*>',
    re.IGNORECASE | re.DOTALL)
SS_FRESH_RE = re.compile(
    r'<div class="ss-fresh"[^>]*>.*?</div\s*>', re.IGNORECASE | re.DOTALL)
AFF_DISC_PILL_RE = re.compile(
    r'<p class="aff-disclosure-pill"[^>]*>.*?</p\s*>', re.IGNORECASE | re.DOTALL)
TRUST_BAR_RE = re.compile(
    r'<div class="trust-bar"[^>]*>.*?</div\s*>', re.IGNORECASE | re.DOTALL)


def apply_v2(html: str) -> tuple[str, dict]:
    """Returns (new_html, stats)."""
    stats: dict[str, int] = {}

    # 1. body class="v2"
    def add_body_class(m: re.Match) -> str:
        attrs = m.group(1)
        if 'class="v2"' in attrs or "class='v2'" in attrs:
            return m.group(0)
        cls_match = re.search(r'class="([^"]*)"', attrs)
        if cls_match:
            new_cls = (cls_match.group(1) + " v2").strip()
            attrs = attrs.replace(cls_match.group(0), f'class="{new_cls}"')
        else:
            attrs = (attrs.rstrip() + ' class="v2"').lstrip()
            if not attrs.startswith(" "):
                attrs = " " + attrs
        return f"<body{attrs}>"

    new_html, n = BODY_OPEN_RE.subn(add_body_class, html, count=1)
    if n:
        stats["body_class"] = n
    html = new_html

    # 2. Inject v2 CSS link if not present (after saaspare-ui.css link if there, else before </head>)
    if "saaspare-v2.css" not in html:
        if "saaspare-ui.css" in html:
            html = html.replace(
                '<link rel="stylesheet" href="/assets/saaspare-ui.css">',
                '<link rel="stylesheet" href="/assets/saaspare-ui.css">\n' + V2_CSS_LINK,
                1,
            )
        else:
            html = html.replace("</head>", V2_CSS_LINK + "\n</head>", 1)
        stats["v2_css_link"] = 1

    # 3. Replace nav with canonical
    matches = list(NAV_RE.finditer(html))
    if matches:
        # Replace ONLY the first <nav> (top of body) — leaves any in-page <nav>
        first = matches[0]
        html = html[: first.start()] + CANONICAL_NAV.rstrip() + html[first.end() :]
        stats["nav_replaced"] = 1

    # 4. Strip pills / badges / dupe disclosure / OK trust-bar
    for label, regex in (
        ("page_eyebrow", PAGE_EYEBROW_RE),
        ("hero_eyebrow", HERO_EYEBROW_RE),
        ("badge_dot", BADGE_DOT_RE),
        ("ss_fresh", SS_FRESH_RE),
        ("aff_disc_pill", AFF_DISC_PILL_RE),
        ("trust_bar", TRUST_BAR_RE),
    ):
        new_html, n = regex.subn("", html)
        if n:
            stats[label] = n
            html = new_html

    return html, stats


PILOT_PAGES = [
    "site/index.html",
    "site/affiliate-disclosure.html",
    "site/deal-radar.html",
    "site/pages/saas-roi-calculator.html",
    "site/pages/partnerstack-vs-firstpromoter-which-is-better-in-2026.html",
    "site/pages/1password-pricing-2026-plans-costs-what-you-actually-pay.html",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, do not write")
    ap.add_argument("--files", nargs="*", default=[], help="explicit file list")
    ap.add_argument("--all", action="store_true", help="all site HTML")
    ap.add_argument("--pilot", action="store_true", help="pilot 6 pages")
    args = ap.parse_args()

    if args.pilot:
        files = [ROOT / f for f in PILOT_PAGES]
    elif args.all:
        files = sorted(SITE.rglob("*.html"))
    elif args.files:
        files = [Path(f) if Path(f).is_absolute() else ROOT / f for f in args.files]
    else:
        ap.error("provide --pilot | --all | --files <paths>")

    total_changes = 0
    files_touched = 0
    summary: dict[str, int] = {}

    for fp in files:
        if not fp.exists():
            print(f"  ! missing: {fp}")
            continue
        try:
            html = fp.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"  ! binary or non-utf8: {fp}")
            continue

        new_html, stats = apply_v2(html)

        if not stats:
            continue

        files_touched += 1
        for k, v in stats.items():
            summary[k] = summary.get(k, 0) + v
            total_changes += v

        rel = fp.relative_to(ROOT)
        print(f"  {'[would]' if args.check else '[done] '} {rel}: {stats}")

        if not args.check and html != new_html:
            fp.write_text(new_html, encoding="utf-8")

    print("\n=== SUMMARY ===")
    print(f"  files {'would be' if args.check else ''} touched: {files_touched}")
    print(f"  total changes: {total_changes}")
    for k, v in sorted(summary.items()):
        print(f"    {k}: {v}")


if __name__ == "__main__":
    main()
