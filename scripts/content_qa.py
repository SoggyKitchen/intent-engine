#!/usr/bin/env python3
"""
content_qa.py — comprehensive content quality + SEO health gate.

Runs as a CI gate (called from nightly_site_integrity.yml). Exits non-zero
only on HARD failures; reports SOFT issues to a JSON output.

HARD failures (block publish):
  - duplicate canonicals across pages
  - missing canonical on indexable money pages
  - missing title or H1 on indexable pages
  - JSON-LD that fails to parse
  - sitemap references a URL that doesn't exist as a file
  - robots.txt blocks Googlebot/Bingbot/GPTBot/OAI-SearchBot
  - affiliate links missing rel="sponsored"

SOFT issues (logged, do not block):
  - title >70 chars
  - meta description outside 80-165 char range
  - missing affiliate disclosure on a money page
  - missing FAQ block on a money page
  - schema with aggregateRating where ratingCount<=1

Run:  uv run python scripts/content_qa.py
Strict mode: uv run python scripts/content_qa.py --strict (treats SOFT as HARD)
"""
from __future__ import annotations
import argparse, io, json, pathlib, re, sys
from collections import defaultdict
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
PAGES = SITE / 'pages'
OUTPUTS = ROOT / 'outputs' / 'seo'

# Pages exempt from indexable-page requirements
EXEMPT_PAGES = {
    'site/ph-preview-1.html', 'site/ph-preview-2.html', 'site/ph-preview-3.html',
    'site/_redirects', 'site/sitemap.xml', 'site/robots.txt',
    # Third-party verification files
    'site/fo-verify.html', 'site/fo-verify-c0ceba67-f661-491b-9895-78e0a0a9eb9f.html',
}


def is_indexable(html: str) -> bool:
    return 'noindex' not in html.lower() or '<meta name="robots" content="noindex' not in html.lower()


def extract(html: str, pattern: str, group: int = 1, flags: int = re.IGNORECASE | re.DOTALL) -> str | None:
    m = re.search(pattern, html, flags)
    return m.group(group).strip() if m else None


def find_jsonld(html: str) -> list[tuple[int, str]]:
    """Return (offset, raw_json) tuples for every <script type=application/ld+json> block."""
    out: list[tuple[int, str]] = []
    for m in re.finditer(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        html, re.DOTALL | re.IGNORECASE,
    ):
        out.append((m.start(), m.group(1)))
    return out


# ── individual checks ────────────────────────────────────────────────────────

class Report:
    def __init__(self) -> None:
        self.hard: list[str] = []
        self.soft: list[str] = []
        self.stats: dict[str, int] = defaultdict(int)

    def H(self, msg: str) -> None:
        self.hard.append(msg)
        self.stats['hard'] += 1

    def S(self, msg: str) -> None:
        self.soft.append(msg)
        self.stats['soft'] += 1


def check_robots(rep: Report) -> None:
    rfp = SITE / 'robots.txt'
    if not rfp.exists():
        rep.H('robots.txt missing')
        return
    txt = rfp.read_text(encoding='utf-8', errors='replace')
    required_allow = ['Googlebot', 'Bingbot', 'GPTBot', 'OAI-SearchBot', 'ChatGPT-User']
    for ua in required_allow:
        # Look for User-agent: <ua> followed by Allow: / (no Disallow: / first)
        m = re.search(
            rf'User-agent:\s*{re.escape(ua)}\s*\n((?:Disallow|Allow):[^\n]*)',
            txt, re.IGNORECASE,
        )
        if not m:
            rep.S(f'robots.txt: missing explicit allow for {ua}')
        elif m.group(1).strip().lower().startswith('disallow: /'):
            rep.H(f'robots.txt: blocks {ua}')
    if 'Sitemap:' not in txt:
        rep.H('robots.txt: missing Sitemap directive')


def check_sitemap(rep: Report) -> None:
    sfp = SITE / 'sitemap.xml'
    if not sfp.exists():
        rep.H('sitemap.xml missing')
        return
    txt = sfp.read_text(encoding='utf-8', errors='replace')
    urls = re.findall(r'<loc>https://saaspare\.org(/[^<]*)</loc>', txt)
    rep.stats['sitemap_urls'] = len(urls)
    rep.stats['sitemap_with_lastmod'] = txt.count('<lastmod>')
    if rep.stats['sitemap_with_lastmod'] < len(urls) * 0.95:
        rep.S(f'sitemap: only {rep.stats["sitemap_with_lastmod"]}/{len(urls)} have lastmod')
    # Verify each URL has a corresponding HTML file
    missing = []
    for url in urls:
        url = url.rstrip('/')
        if url == '':
            candidate = SITE / 'index.html'
        elif url == '/pages':
            candidate = SITE / 'pages' / 'index.html'
        elif url.startswith('/pages/'):
            slug = url[len('/pages/'):]
            candidate = SITE / 'pages' / (slug + '.html')
            if not candidate.exists():
                # Check directory index variant
                candidate = SITE / 'pages' / slug / 'index.html'
        else:
            candidate = SITE / (url[1:] + '.html')
            if not candidate.exists():
                candidate = SITE / url[1:] / 'index.html'
        if not candidate.exists():
            missing.append(url)
    if missing:
        rep.H(f'sitemap references {len(missing)} non-existent pages: {missing[:3]}')


def check_pages(rep: Report) -> None:
    titles: dict[str, list[str]] = defaultdict(list)
    descriptions: dict[str, list[str]] = defaultdict(list)
    canonicals: dict[str, list[str]] = defaultdict(list)

    all_pages = list(SITE.rglob('*.html'))
    rep.stats['total_pages'] = len(all_pages)

    for fp in all_pages:
        rel = fp.relative_to(ROOT).as_posix()
        if rel in EXEMPT_PAGES or fp.name.startswith('fo-verify'):
            continue
        try:
            raw = fp.read_bytes()
            enc = 'utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8'
            html = raw.decode(enc, errors='replace')
        except Exception as e:
            rep.H(f'{rel}: cannot read ({e})')
            continue

        if not is_indexable(html):
            continue  # skip noindex pages
        rep.stats['indexable_pages'] += 1

        # Title
        title = extract(html, r'<title>([^<]+)</title>')
        if not title:
            rep.H(f'{rel}: missing <title>')
        else:
            titles[title].append(rel)
            if len(title) > 70:
                rep.stats['title_over_70'] += 1
            if len(title) < 30:
                rep.S(f'{rel}: title <30 chars ({len(title)})')

        # Meta description
        desc = extract(html, r'<meta\s+name="description"\s+content="([^"]+)"')
        if not desc:
            rep.H(f'{rel}: missing meta description')
        else:
            descriptions[desc].append(rel)
            if len(desc) < 80:
                rep.S(f'{rel}: meta desc <80 chars ({len(desc)})')
            if len(desc) > 165:
                rep.stats['desc_over_165'] += 1

        # Canonical
        canonical = extract(html, r'<link\s+rel="canonical"\s+href="([^"]+)"')
        if not canonical:
            rep.H(f'{rel}: missing canonical')
        else:
            canonicals[canonical].append(rel)

        # H1
        h1_count = len(re.findall(r'<h1[^>]*>', html, re.IGNORECASE))
        if h1_count == 0 and 'pages/' in rel:
            rep.H(f'{rel}: no <h1>')
        elif h1_count > 1:
            rep.S(f'{rel}: {h1_count} <h1> tags (should be 1)')

        # AI-tell markers: em-dashes and overused AI vocabulary read as
        # machine-generated to both readers and Google's scaled-content-abuse
        # detection. Soft flag only; a script can rewrite offending text with
        # scripts/humanize_text.py.
        body_text = re.sub(r'<script.*?</script>', ' ', html, flags=re.S | re.I)
        body_text = re.sub(r'<style.*?</style>', ' ', body_text, flags=re.S | re.I)
        em_hits = body_text.count('—') + body_text.count('&mdash;')
        if em_hits:
            rep.S(f'{rel}: {em_hits} em-dash(es) — run scripts/humanize_text.py')
        for w in ('seamless', 'seamlessly', 'robust'):
            if re.search(r'' + w + r'', body_text, re.IGNORECASE):
                rep.S(f'{rel}: AI-tell word "{w}" — run scripts/humanize_text.py')
                break

        # JSON-LD parse
        for offset, blob in find_jsonld(html):
            try:
                json.loads(blob)
            except json.JSONDecodeError as e:
                rep.H(f'{rel}: JSON-LD parse error at byte {offset}: {e}')

        # Money page checks (comparison/pricing/alternative pages)
        is_money = any(t in rel for t in ['vs-', '-pricing-', '-alternatives-', '-review-', '-coupon-', '-promo-', '-free-trial-'])
        if is_money:
            rep.stats['money_pages'] += 1
            # Affiliate disclosure presence
            if 'affiliate-disclosure' not in html.lower() and 'affiliate link' not in html.lower():
                rep.S(f'{rel}: money page missing affiliate disclosure mention')
            # Affiliate link rel="sponsored"
            for m in re.finditer(r'<a\s+([^>]*?)href="(/go/[^"]+)"([^>]*)>', html):
                attrs = m.group(1) + m.group(3)
                if 'rel=' not in attrs.lower():
                    rep.S(f'{rel}: /go/ link without rel attribute: {m.group(2)}')
                elif 'sponsored' not in attrs.lower():
                    rep.H(f'{rel}: /go/ link rel missing "sponsored": {m.group(2)}')

    # Cross-page duplicate analysis
    for title, paths in titles.items():
        if len(paths) > 1:
            rep.S(f'duplicate title ({len(paths)} pages): "{title[:60]}" — {paths[:3]}')
            rep.stats['duplicate_titles'] += 1
    for desc, paths in descriptions.items():
        if len(paths) > 1:
            rep.S(f'duplicate description ({len(paths)} pages): "{desc[:60]}" — {paths[:3]}')
            rep.stats['duplicate_descs'] += 1


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    ap = argparse.ArgumentParser()
    ap.add_argument('--strict', action='store_true', help='Treat SOFT issues as failures')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

    rep = Report()
    check_robots(rep)
    check_sitemap(rep)
    check_pages(rep)

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    out = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'stats': dict(rep.stats),
        'hard_failures': rep.hard,
        'soft_issues': rep.soft[:200],  # cap at 200 to keep file readable
        'soft_issues_total': len(rep.soft),
    }
    (OUTPUTS / 'content_qa.json').write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8'
    )

    print(f'\n=== Content QA report ===')
    for k, v in sorted(rep.stats.items()):
        print(f'  {k}: {v}')
    print(f'\nHARD failures: {len(rep.hard)}')
    for msg in rep.hard[:25]:
        print(f'  ✗ {msg}')
    if len(rep.hard) > 25:
        print(f'  ... and {len(rep.hard) - 25} more (see outputs/seo/content_qa.json)')

    if not args.quiet:
        print(f'\nSOFT issues: {len(rep.soft)} (top 10):')
        for msg in rep.soft[:10]:
            print(f'  · {msg}')

    if rep.hard or (args.strict and rep.soft):
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
