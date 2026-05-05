#!/usr/bin/env python3
"""
fix_amazon_links.py — Fix Amazon Associates issues across the site.

Problems fixed:
  1. aws.amazon.com links have ?tag=soggykitchen1-22 embedded — AWS is NOT
     covered by Amazon Associates (it is a separate business). These earn
     zero commissions and look like spam. Remove tag + fix embedded newlines.

  2. Also strips the broken \n inside href/JSON-LD URLs on those pages.

  3. Adds a small "available on Amazon" pill to the bottom CTA on the 9
     microsoft-teams-vs-* comparison pages — MS365 Personal is sold on
     Amazon and the 24-hour Associates cookie means clicks here can convert
     on anything the visitor then buys on Amazon within 24 h.

Run:  uv run python scripts/fix_amazon_links.py
Dry:  uv run python scripts/fix_amazon_links.py --check
"""
from __future__ import annotations
import argparse, pathlib, re, sys

SITE = pathlib.Path(__file__).resolve().parent.parent / 'site'
PAGES = SITE / 'pages'

TAG = 'soggykitchen1-22'
AMZN_TAG = f'tag={TAG}'

# Canonical clean AWS URL (no tag — Associates doesn't cover AWS services)
CLEAN_AWS = 'https://aws.amazon.com'

# Amazon search URL for Microsoft 365 — always resolves correctly
MS365_AMZN = f'https://www.amazon.com/s?k=Microsoft+365+Personal&i=software&{AMZN_TAG}'

# Tiny pill injected before </body> on MS Teams pages
# Uses rel="sponsored" + Associates disclosure as required by FTC + Amazon TOS
MS365_PILL_CSS = (
    '<style>'
    '.ss-amzn-pill{display:inline-flex;align-items:center;gap:.5rem;'
    'background:rgba(255,153,0,.08);border:1px solid rgba(255,153,0,.28);'
    'border-radius:100px;padding:.45rem 1rem .45rem .75rem;'
    'font-size:.78rem;color:rgba(255,220,120,.85);text-decoration:none;'
    'transition:background .18s;margin-top:1.25rem}'
    '.ss-amzn-pill:hover{background:rgba(255,153,0,.16)}'
    '.ss-amzn-pill svg{flex-shrink:0}'
    '.ss-amzn-wrap{text-align:center}'
    '</style>'
)

AMAZON_ICON = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<path d="M21.5 17.5c-3.5 2-8 3-12.5 1.5" stroke="#FF9900" stroke-width="2" '
    'stroke-linecap="round"/>'
    '<path d="M18.5 19.5l3-2-1-3" stroke="#FF9900" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"/>'
    '<path d="M4 12.5C4 8.36 7.36 5 11.5 5S19 8.36 19 12.5" stroke="currentColor" '
    'stroke-width="1.5" stroke-linecap="round"/>'
    '</svg>'
)

MS365_PILL_HTML = (
    '\n<div class="ss-amzn-wrap">'
    f'<a class="ss-amzn-pill" href="{MS365_AMZN}" '
    'rel="sponsored noopener" target="_blank" '
    'data-track="amazon-associates" data-slot="amzn_ms365">'
    f'{AMAZON_ICON}'
    'Microsoft 365 Personal — buy on Amazon'
    '</a>'
    '<p style="font-size:.68rem;color:rgba(255,255,255,.22);margin-top:.35rem">'
    'As an Amazon Associate SaaSpare earns from qualifying purchases.'
    '</p>'
    '</div>'
)

# ── helpers ──────────────────────────────────────────────────────────────────

def clean_aws_links(html: str) -> tuple[str, list[str]]:
    """Remove the non-earning Associates tag from all aws.amazon.com hrefs
    and JSON-LD url strings, and strip embedded newlines from those URLs."""
    changes: list[str] = []

    # Pattern covers the full broken URL fragment in both href attrs and JSON-LD
    # The URL may have a literal \n followed by &utm_... or just end after the tag
    broken_url_re = re.compile(
        r'https://aws\.amazon\.com\?tag=soggykitchen1-22(?:\\n|\n)?(?:&[^">\s]*)?',
        re.IGNORECASE
    )

    def replace_aws(m: re.Match) -> str:
        return CLEAN_AWS

    new_html, n = broken_url_re.subn(replace_aws, html)
    if n:
        changes.append(f'aws-tag-removed({n})')

    # Also catch any remaining aws.amazon.com with just the tag and no utm
    plain_tag_re = re.compile(
        r'https://aws\.amazon\.com\?tag=soggykitchen1-22',
        re.IGNORECASE
    )
    new_html, n2 = plain_tag_re.subn(CLEAN_AWS, new_html)
    if n2:
        changes.append(f'aws-tag-plain-removed({n2})')

    return new_html, changes


def add_ms365_pill(html: str, fname: str) -> tuple[str, list[str]]:
    """Inject the Amazon MS365 pill before </body> on relevant pages.
    Only adds it once (idempotent)."""
    changes: list[str] = []

    if 'ss-amzn-pill' in html:
        return html, changes  # already present

    # Only inject on Microsoft Teams comparison/alternatives pages
    is_teams_page = (
        'microsoft-teams-vs-' in fname
        or 'vs-microsoft-teams' in fname
        or '7-best-microsoft-teams-alternatives' in fname
    )
    if not is_teams_page:
        return html, changes

    # Find the last cta-section before </body> to inject after it
    body_close = html.rfind('</body>')
    if body_close == -1:
        return html, changes

    # Inject CSS in <head> (before </style> closest to </head>)
    head_close = html.find('</head>')
    if head_close != -1 and 'ss-amzn-pill' not in html:
        html = html[:head_close] + MS365_PILL_CSS + '\n' + html[head_close:]
        body_close = html.rfind('</body>')  # recalculate after head insert

    # Inject pill HTML just before </body>
    html = html[:body_close] + MS365_PILL_HTML + '\n' + html[body_close:]
    changes.append('ms365-amazon-pill-added')

    return html, changes


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='Dry-run only')
    args = ap.parse_args()

    sys.stdout = __import__('io').TextIOWrapper(
        sys.stdout.buffer, encoding='utf-8', errors='replace'
    )

    html_files = sorted(PAGES.glob('*.html'))
    total_updated = 0

    for fp in html_files:
        raw = fp.read_bytes()
        enc = 'utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8'
        html = raw.decode(enc, errors='replace')
        all_changes: list[str] = []

        html, c1 = clean_aws_links(html)
        all_changes += c1

        html, c2 = add_ms365_pill(html, fp.name)
        all_changes += c2

        if not all_changes:
            continue

        total_updated += 1
        tag = '[CHECK]' if args.check else '[FIXED]'
        print(f'{tag} {fp.name}: {", ".join(all_changes)}')

        if not args.check:
            fp.write_bytes(html.encode(enc))

    print(f'\n{"[DRY RUN] " if args.check else ""}Done: {total_updated} pages updated')


if __name__ == '__main__':
    main()
