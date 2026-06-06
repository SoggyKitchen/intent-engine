#!/usr/bin/env python3
"""
seo_consolidate.py — Phase 1+2 SEO consolidation pass.

Fixes (idempotent):
  1. Strip fake aggregateRating + review from JSON-LD where ratingCount<=1
     (Google penalises and Phase 2 rules forbid fake aggregate ratings).
  2. Update canonicals on duplicate pages so they point to the chosen
     canonical URL (consolidates link equity).
  3. Add `noindex,nofollow` to ph-preview-* preview pages.
  4. Fix the 2 stub meta descriptions ("SaaSpare" 8-char strings).
  5. Remove broken internal links from 3 hub pages by deleting the
     <li>/<a> rows whose href has no matching .html file.
  6. Add 301 redirects in site/_redirects for duplicate URL variants.

Run:  uv run python scripts/seo_consolidate.py
Dry:  uv run python scripts/seo_consolidate.py --check
"""
from __future__ import annotations
import argparse, io, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
PAGES = SITE / 'pages'

# Pages that should be canonical winners (the duplicate twins redirect/canonical to these)
COUPON_PAIRS: list[tuple[str, str]] = []  # (loser, winner) — promo-code → coupon-code
ALT_PAIRS: list[tuple[str, str]] = []     # 7-best-X → best-X

def discover_dupes() -> None:
    """Scan PAGES for the duplicate naming patterns and populate the pair lists."""
    for fp in sorted(PAGES.glob('*-promo-code-2026-discounts-deals-that-actually-work.html')):
        base = fp.name.replace('-promo-code-2026-discounts-deals-that-actually-work.html', '')
        winner = PAGES / f'{base}-coupon-code-promo-codes-2026-verified-discounts.html'
        if winner.exists():
            COUPON_PAIRS.append((fp.name, winner.name))

    # NOTE: Alternatives-page consolidation is intentionally DISABLED.
    # The `7-best-X-alternatives` pages are self-canonical revenue pages with real
    # GSC impressions (Ramp, Notion, etc.). Consolidating them to `best-X` twins
    # (a) noindexed pages that actually rank — a direct revenue loss, and
    # (b) re-pointed canonicals at slugs with no backing file when the `best-X`
    #     winner didn't exist, which broke the nightly integrity + content-QA
    #     gates every run (sitemap referenced / demanded non-existent pages).
    # Leave each alternatives page self-canonical and indexed. The minor cost of
    # not deduping the ~25 genuine twins is far smaller than noindexing rankers.
    #
    # for fp in sorted(PAGES.glob('7-best-*-alternatives-in-2026-free-paid.html')):
    #     winner = PAGES / fp.name[2:]  # strip "7-"
    #     if winner.exists():
    #         ALT_PAIRS.append((fp.name, winner.name))


# ── helpers ──────────────────────────────────────────────────────────────────

def read_html(fp: pathlib.Path) -> tuple[str, str]:
    raw = fp.read_bytes()
    enc = 'utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8'
    return raw.decode(enc, errors='replace'), enc


def write_html(fp: pathlib.Path, html: str, enc: str) -> None:
    fp.write_bytes(html.encode(enc))


# Match aggregateRating + review blocks where ratingCount/reviewCount <= 1.
# Conservative: only strips when ratingCount: 1 to avoid touching real ratings.
RE_FAKE_AGG = re.compile(
    r',\s*"aggregateRating"\s*:\s*\{[^{}]*?"ratingCount"\s*:\s*1[^{}]*?\}',
    re.DOTALL
)
RE_FAKE_REVIEW = re.compile(
    r',\s*"review"\s*:\s*\{[^{}]*?"reviewBody"[^{}]*?\}\s*\}',
    re.DOTALL
)
# Tighter review pattern (only inside Product blocks where we already removed aggregateRating)
RE_REVIEW_BLOCK = re.compile(
    r',\s*"review"\s*:\s*\{(?:[^{}]|\{[^{}]*\})*?"reviewBody"(?:[^{}]|\{[^{}]*\})*?\}',
    re.DOTALL
)


def strip_fake_ratings(html: str) -> tuple[str, list[str]]:
    """Remove aggregateRating with ratingCount=1 and the paired review block."""
    changes: list[str] = []
    new_html, n_agg = RE_FAKE_AGG.subn('', html)
    if n_agg:
        changes.append(f'agg-rating-stripped({n_agg})')
    # Only remove reviews if we removed an aggregateRating from the same JSON-LD
    if n_agg:
        new_html, n_rev = RE_REVIEW_BLOCK.subn('', new_html)
        if n_rev:
            changes.append(f'review-stripped({n_rev})')
    return new_html, changes


def update_canonical(html: str, canonical_path: str) -> tuple[str, bool]:
    """Replace the canonical link's href with the given path."""
    new_canonical = f'<link rel="canonical" href="https://saaspare.org{canonical_path}">'
    pattern = re.compile(r'<link\s+rel="canonical"\s+href="[^"]*"\s*/?>', re.IGNORECASE)
    if pattern.search(html):
        new_html, n = pattern.subn(new_canonical, html, count=1)
        return new_html, n > 0
    return html, False


def fix_stub_description(html: str, real_desc: str) -> tuple[str, bool]:
    """Replace `description content="SaaSpare"` with a proper description."""
    pattern = re.compile(
        r'<meta\s+name="description"\s+content="SaaSpare"\s*/?>', re.IGNORECASE
    )
    if not pattern.search(html):
        return html, False
    new_meta = f'<meta name="description" content="{real_desc}">'
    new_html, n = pattern.subn(new_meta, html, count=1)
    # Also fix og:description and twitter:description if they're "SaaSpare"
    for og_pat in [
        r'<meta\s+property="og:description"\s+content="SaaSpare"\s*/?>',
        r'<meta\s+name="twitter:description"\s+content="SaaSpare"\s*/?>',
    ]:
        new_html = re.sub(og_pat, '', new_html, flags=re.IGNORECASE)
    return new_html, n > 0


def add_noindex(html: str) -> tuple[str, bool]:
    """Replace existing robots meta with noindex,nofollow (or insert if missing)."""
    if 'noindex' in html.lower():
        return html, False
    pattern = re.compile(r'<meta\s+name="robots"\s+content="[^"]*"\s*/?>', re.IGNORECASE)
    new_meta = '<meta name="robots" content="noindex, nofollow">'
    if pattern.search(html):
        new_html, n = pattern.subn(new_meta, html, count=1)
        return new_html, n > 0
    # Insert after <head>
    head = html.find('<head>')
    if head == -1:
        return html, False
    insert_at = html.find('>', head) + 1
    new_html = html[:insert_at] + '\n' + new_meta + html[insert_at:]
    return new_html, True


def remove_broken_links(html: str, valid_paths: set[str]) -> tuple[str, int]:
    """Strip <a href="/pages/foo">...</a> if /pages/foo.html doesn't exist."""
    # Match <a href="/pages/X">label</a> where X may not have .html
    pattern = re.compile(
        r'<a\s+([^>]*?)href="(/pages/[^"#?]+)"([^>]*)>(.*?)</a>',
        re.IGNORECASE | re.DOTALL
    )
    removed = 0

    def replace(m: re.Match) -> str:
        nonlocal removed
        href = m.group(2).rstrip('/')
        # Normalise to filename
        candidate = href + '.html' if not href.endswith('.html') else href
        slug = candidate[len('/pages/'):]
        if slug in valid_paths:
            return m.group(0)
        # Broken — replace with plain text (preserve label)
        removed += 1
        label = re.sub(r'<[^>]+>', '', m.group(4))
        return label

    new_html = pattern.sub(replace, html)
    return new_html, removed


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()

    discover_dupes()
    print(f'[discover] coupon pairs: {len(COUPON_PAIRS)}, alt pairs: {len(ALT_PAIRS)}')

    # Build set of valid page slugs for broken-link check
    valid_slugs = {fp.name for fp in PAGES.glob('*.html')}

    summary = {'pages_touched': 0, 'fixes': {}}

    def bump(key: str, n: int = 1) -> None:
        summary['fixes'][key] = summary['fixes'].get(key, 0) + n

    # ── 1. Strip fake aggregateRating across all pages ──────────────────────
    for fp in sorted(PAGES.glob('*.html')):
        html, enc = read_html(fp)
        new_html, changes = strip_fake_ratings(html)
        if changes:
            summary['pages_touched'] += 1
            for c in changes:
                bump(f'fake-rating:{c.split("(")[0]}', int(c.split('(')[1].rstrip(')')))
            if not args.check:
                write_html(fp, new_html, enc)

    # ── 2. Update canonicals on duplicate pages ─────────────────────────────
    for loser, winner in COUPON_PAIRS + ALT_PAIRS:
        loser_fp = PAGES / loser
        winner_path = '/pages/' + winner.replace('.html', '')
        html, enc = read_html(loser_fp)
        new_html, ok = update_canonical(html, winner_path)
        if ok:
            bump('canonical-consolidated')
            # Also add noindex to the duplicate (Google will prefer canonical anyway)
            new_html, ni = add_noindex(new_html)
            if ni:
                bump('duplicate-noindexed')
            if not args.check:
                write_html(loser_fp, new_html, enc)

    # ── 3. Add noindex to ph-preview-* pages ────────────────────────────────
    for fp in SITE.glob('ph-preview-*.html'):
        html, enc = read_html(fp)
        new_html, ok = add_noindex(html)
        if ok:
            bump('ph-preview-noindexed')
            if not args.check:
                write_html(fp, new_html, enc)

    # ── 4. Fix stub descriptions ────────────────────────────────────────────
    PRIVACY_DESC = (
        "SaaSpare's privacy policy: how we collect, use, and protect "
        "personal data when you visit saaspare.org or subscribe to our "
        "newsletter. GDPR / Australian Privacy Act compliant."
    )
    COUPON_POLICY_DESC = (
        "How SaaSpare verifies coupon codes: testing methodology, source "
        "checks, and how we handle expired or invalid affiliate discounts."
    )
    for fp, desc in [
        (SITE / 'privacy.html', PRIVACY_DESC),
        (PAGES / 'coupon-verification-policy.html', COUPON_POLICY_DESC),
    ]:
        if not fp.exists():
            continue
        html, enc = read_html(fp)
        new_html, ok = fix_stub_description(html, desc)
        if ok:
            bump('stub-desc-fixed')
            if not args.check:
                write_html(fp, new_html, enc)

    # ── 5. Remove broken internal links from hub pages ──────────────────────
    HUB_PAGES = [
        'free-trial-database.html',
        'saas-pricing-index.html',
        'saas-pricing-changes.html',
    ]
    for hub in HUB_PAGES:
        fp = PAGES / hub
        if not fp.exists():
            continue
        html, enc = read_html(fp)
        new_html, n = remove_broken_links(html, valid_slugs)
        if n:
            bump(f'broken-links-removed:{hub}', n)
            summary['pages_touched'] += 1
            if not args.check:
                write_html(fp, new_html, enc)

    # ── 6. Add 301 redirects to _redirects ──────────────────────────────────
    redirects_fp = SITE / '_redirects'
    new_redirects: list[str] = []
    if redirects_fp.exists():
        existing = redirects_fp.read_text(encoding='utf-8', errors='replace')
    else:
        existing = ''

    new_lines: list[str] = []
    marker = '# === seo_consolidate.py duplicates -> canonical 301s ==='
    if marker not in existing:
        new_lines.append('\n' + marker)
        for loser, winner in COUPON_PAIRS + ALT_PAIRS:
            loser_path = '/pages/' + loser.replace('.html', '')
            winner_path = '/pages/' + winner.replace('.html', '')
            line = f'{loser_path} {winner_path} 301'
            if line not in existing:
                new_lines.append(line)
                bump('301-redirect-added')

    if new_lines and not args.check:
        with redirects_fp.open('a', encoding='utf-8') as f:
            f.write('\n'.join(new_lines) + '\n')
    elif new_lines:
        bump('301-redirects-pending', len(new_lines) - 1)  # -1 for marker

    # ── summary ─────────────────────────────────────────────────────────────
    print(f'\n{"[DRY RUN] " if args.check else ""}seo_consolidate complete:')
    print(f'  pages touched: {summary["pages_touched"]}')
    for k in sorted(summary['fixes']):
        print(f'  {k}: {summary["fixes"][k]}')


if __name__ == '__main__':
    main()
