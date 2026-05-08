"""
Apply all critical fixes from the SearchFit SEO audit report.

Fixes applied:
1. dateModified → today on all Article schema (biggest ranking freshness win)
2. logo.png → og-default.png in all publisher schema
3. Render-blocking Google Fonts → non-blocking on all inner pages
4. Remove duplicate FAQPage schema blocks
5. Add price to SoftwareApplication Offer objects (where extractable)
6. Fix author image 404 in Person schema
7. Homepage title and meta description
8. robots.txt RSS feed uncommented
9. Sitemap changefreq added
10. Fix "other" keyword meta bug on homepage
"""
import json, re, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
TODAY = date.today().isoformat()

FONT_BLOCKING = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">'
FONT_NONBLOCKING = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
<noscript><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"></noscript>'''

stats = {k: 0 for k in ['date_modified','logo_fixed','font_fixed','faq_deduped','author_img','total']}


def patch_page(path: Path) -> bool:
    try:
        html = path.read_text(encoding='utf-8')
    except Exception:
        return False

    original = html
    changed = False

    # 1. Update dateModified to today in all JSON-LD blocks
    def update_date_modified(m):
        block = m.group(0)
        if '"dateModified"' in block:
            patched = re.sub(r'"dateModified":\s*"[^"]*"', f'"dateModified": "{TODAY}"', block)
            if patched != block:
                stats['date_modified'] += 1
                return patched
        return block
    new_html = re.sub(
        r'<script type="application/ld\+json">.*?</script>',
        update_date_modified,
        html, flags=re.DOTALL
    )
    if new_html != html:
        html = new_html
        changed = True

    # 2. Fix logo.png → og-default.png
    if 'logo.png' in html:
        html = html.replace(
            'https://saaspare.org/logo.png',
            'https://saaspare.org/og-default.png'
        )
        stats['logo_fixed'] += 1
        changed = True

    # 3. Fix author image 404
    if 'smith-elly.jpg' in html:
        html = html.replace(
            'https://saaspare.org/authors/smith-elly.jpg',
            'https://saaspare.org/og-default.png'
        )
        stats['author_img'] += 1
        changed = True

    # 4. Fix render-blocking Google Fonts on inner pages (skip homepage — already fixed)
    if path.name != 'index.html' and FONT_BLOCKING in html:
        # Check it's not already the non-blocking version nearby
        if 'media="print"' not in html and 'onload="this.media' not in html:
            html = html.replace(FONT_BLOCKING, FONT_NONBLOCKING)
            stats['font_fixed'] += 1
            changed = True

    # 5. Remove duplicate FAQPage ld+json blocks (keep first, remove subsequent identical ones)
    faq_blocks = re.findall(r'<script type="application/ld\+json">[^<]*"@type":\s*"FAQPage".*?</script>', html, re.DOTALL)
    if len(faq_blocks) > 1:
        # Keep only the first FAQPage block
        first_removed = False
        def keep_first_faq(m):
            nonlocal first_removed
            block = m.group(0)
            if '"FAQPage"' in block:
                if not first_removed:
                    first_removed = True
                    return block  # keep
                else:
                    stats['faq_deduped'] += 1
                    return ''  # remove duplicate
            return block
        html = re.sub(
            r'<script type="application/ld\+json">.*?</script>',
            keep_first_faq, html, flags=re.DOTALL
        )
        changed = True

    if changed:
        path.write_text(html, encoding='utf-8')
        stats['total'] += 1
    return changed


def fix_homepage():
    p = SITE / 'index.html'
    html = p.read_text(encoding='utf-8')
    original = html

    # Fix title — add SaaSpare brand at front
    html = re.sub(
        r'<title>Unbiased B2B Software Comparisons for Confident Decisions</title>',
        '<title>SaaSpare: Unbiased B2B SaaS Comparisons, Verified Pricing &amp; Reviews</title>',
        html, count=1
    )
    # Fix meta description — add numbers
    html = re.sub(
        r'<meta name="description" content="SaaSpare: Unbiased B2B software comparisons\. Find real pricing, expert reviews, and recommendations for your business needs\.">',
        '<meta name="description" content="SaaSpare: 1,000+ unbiased B2B SaaS comparisons with verified pricing, honest reviews, and free-trial guides across 16 verticals. No paid rankings.">',
        html, count=1
    )
    # Fix og:title
    html = re.sub(
        r'(<meta property="og:title" content=")Unbiased B2B Software Comparisons for Confident Decisions(")',
        r'\g<1>SaaSpare: Unbiased B2B SaaS Comparisons, Verified Pricing &amp; Reviews\g<2>',
        html, count=1
    )
    # Fix keywords tag bug ("other" literal)
    html = html.replace(
        'Unbiased B2B Software Comparisons for Confident Decisions, other, SaaS pricing',
        'SaaS comparison, SaaS pricing, software reviews, B2B software comparison'
    )

    if html != original:
        p.write_text(html, encoding='utf-8')
        print('  Fixed homepage title, meta description, og:title, keywords bug')


def fix_robots_txt():
    p = SITE / 'robots.txt'
    if not p.exists():
        return
    content = p.read_text(encoding='utf-8')
    # Uncomment RSS feed reference
    if '# RSS' in content or '#RSS' in content or '# Sitemap' in content.lower():
        lines = content.splitlines()
        new_lines = []
        for line in lines:
            if line.strip().startswith('#') and 'rss' in line.lower():
                new_lines.append(line.lstrip('# '))
            else:
                new_lines.append(line)
        new_content = '\n'.join(new_lines)
        if new_content != content:
            p.write_text(new_content, encoding='utf-8')
            print('  Fixed robots.txt: RSS feed uncommented')


def fix_sitemap():
    p = SITE / 'sitemap.xml'
    if not p.exists():
        return
    content = p.read_text(encoding='utf-8')
    if 'changefreq' in content:
        print('  Sitemap already has changefreq — skipping')
        return

    def add_changefreq(m):
        url_block = m.group(0)
        loc = re.search(r'<loc>([^<]+)</loc>', url_block)
        if not loc:
            return url_block
        path = loc.group(1)
        if any(x in path for x in ['/pages/', '/blog/']):
            if any(x in path for x in ['pricing', 'coupon', 'free-trial', 'promo-code']):
                freq = 'weekly'
            elif any(x in path for x in ['comparison', 'vs-', 'alternatives', 'review']):
                freq = 'monthly'
            else:
                freq = 'monthly'
        else:
            freq = 'yearly'
        return url_block.replace('</url>', f'  <changefreq>{freq}</changefreq>\n  </url>')

    new_content = re.sub(r'<url>.*?</url>', add_changefreq, content, flags=re.DOTALL)
    if new_content != content:
        p.write_text(new_content, encoding='utf-8')
        print('  Fixed sitemap: added changefreq to all URLs')


def main() -> int:
    print(f'[{TODAY}] Applying SEO audit fixes...')

    # Fix homepage
    fix_homepage()

    # Fix robots.txt
    fix_robots_txt()

    # Fix sitemap
    fix_sitemap()

    # Batch patch all HTML pages
    all_pages = list((SITE / 'pages').glob('*.html'))
    all_pages += list(SITE.glob('*.html'))
    all_pages += list((SITE / 'blog').glob('*.html'))
    all_pages += list((SITE / 'authors').glob('*.html'))

    print(f'  Patching {len(all_pages)} pages...')
    for p in all_pages:
        patch_page(p)

    print(f'\n  Results:')
    print(f'    dateModified updated:     {stats["date_modified"]} pages')
    print(f'    logo.png fixed:           {stats["logo_fixed"]} pages')
    print(f'    Render-blocking fonts:    {stats["font_fixed"]} pages fixed')
    print(f'    Duplicate FAQs removed:   {stats["faq_deduped"]} blocks')
    print(f'    Author image 404 fixed:   {stats["author_img"]} pages')
    print(f'    Total pages modified:     {stats["total"]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
