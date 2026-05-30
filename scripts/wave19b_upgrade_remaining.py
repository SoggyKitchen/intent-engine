"""
Wave 19b: Upgrade remaining non-v2 pages (best-*, does-*, etc.)
Run: uv run python scripts/wave19b_upgrade_remaining.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
GA4_ID = "G-RLYVYV8WQJ"

SKIP = {
    "report-outdated-pricing.html", "coupon-verification-policy.html",
    "editorial-policy.html", "corrections.html", "affiliate-disclosure.html",
    "privacy.html", "contact.html", "thanks.html", "verification.html",
}

V2_HEAD = """\
  <link rel="stylesheet" href="/assets/saaspare-v2.css">
  <link rel="stylesheet" href="/assets/motion.css">"""

V2_NAV = """\
  <nav class="sp-nav" id="sp-nav">
    <a href="/" class="sp-logo">SaaSpare</a>
    <div class="sp-nav-links">
      <a href="/pages/">Compare</a>
      <a href="/blog/">Blog</a>
      <a href="/about">About</a>
    </div>
  </nav>"""

V2_FOOT = """\
  <footer class="sp-footer">
    <div style="max-width:1100px;margin:0 auto;padding:3rem 1.5rem 2rem;text-align:center;">
      <p style="color:var(--ink-4);font-size:.85rem;">&copy; 2026 SaaSpare.org</p>
      <div style="display:flex;gap:1.5rem;justify-content:center;flex-wrap:wrap;font-size:.82rem;">
        <a href="/" style="color:var(--ink-4);">Home</a>
        <a href="/blog/" style="color:var(--ink-4);">Blog</a>
        <a href="/affiliate-disclosure" style="color:var(--ink-4);">Disclosure</a>
        <a href="/editorial-policy" style="color:var(--ink-4);">Editorial Policy</a>
      </div>
    </div>
  </footer>
  <script src="/assets/motion.js"></script>"""

STICKY = """\
  <div id="sticky-cta" style="position:fixed;bottom:0;left:0;right:0;z-index:999;background:rgba(5,4,7,0.97);backdrop-filter:blur(12px);border-top:1px solid rgba(255,65,109,0.25);padding:14px 20px;display:flex;align-items:center;justify-content:center;gap:16px;transform:translateY(100%);transition:transform 0.4s ease;">
    <span style="color:#a0a0b8;font-size:.88rem;">Find the best tool for your needs</span>
    <a href="/go/semrush" target="_blank" rel="noopener sponsored"
       onclick="if(window.gtag){gtag('event','affiliate_click',{tool:'semrush',placement:'sticky_cta',page:window.location.pathname});}"
       style="display:inline-flex;align-items:center;padding:10px 22px;background:linear-gradient(135deg,#ff416d,#ff6b35);color:#fff;font-weight:700;font-size:.92rem;border-radius:9999px;text-decoration:none;">
      Compare Top Tools &rarr;
    </a>
    <button onclick="document.getElementById('sticky-cta').style.display='none'" style="background:none;border:none;color:#666;cursor:pointer;font-size:1.2rem;padding:4px 8px;">&times;</button>
  </div>
  <script>(function(){var b=document.getElementById('sticky-cta');if(!b)return;var s=false;window.addEventListener('scroll',function(){if(!s&&window.scrollY>300){b.style.transform='translateY(0)';s=true;}},{passive:true});})();</script>"""


def extract_meta(html):
    def g(pat, default=''):
        m = re.search(pat, html, re.IGNORECASE)
        return m.group(1) if m else default
    return {
        'title': g(r'<title>([^<]+)</title>', 'SaaSpare'),
        'desc': g(r'<meta\s+name="description"\s+content="([^"]+)"'),
        'canonical': g(r'<link\s+rel="canonical"\s+href="([^"]+)"'),
        'og_url': g(r'<meta\s+property="og:url"\s+content="([^"]+)"'),
        'noindex': bool(re.search(r'noindex', html, re.IGNORECASE)),
        'jsonld': re.findall(
            r'<script\s+type="application/ld\+json"[^>]*>.*?</script>',
            html, re.DOTALL | re.IGNORECASE
        ),
    }


def extract_body(html):
    m = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL | re.IGNORECASE)
    if not m:
        return html
    body = m.group(1)
    body = re.sub(r'<header[^>]*>.*?</header>', '', body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<nav[^>]*>.*?</nav>', '', body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<footer[^>]*>.*?</footer>', '', body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<!--\s*Sticky.*?</script>', '', body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<div[^>]*id="sticky-cta"[^>]*>.*?</script>', '', body, flags=re.DOTALL | re.IGNORECASE)
    return body.strip()


def rebuild(fp: Path):
    html = fp.read_text(encoding='utf-8', errors='replace')
    if 'saaspare-v2.css' in html:
        return False

    meta = extract_meta(html)
    inner = extract_body(html)
    noindex = '<meta name="robots" content="noindex,nofollow">' if meta['noindex'] else ''
    jld = '\n  '.join(meta['jsonld'])
    ga4 = (
        f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>\n'
        f'  <script>window.dataLayer=window.dataLayer||[];'
        f'function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());gtag("config","{GA4_ID}");</script>'
    )

    new_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  {noindex}
  <title>{meta['title']}</title>
  <meta name="description" content="{meta['desc']}">
  <link rel="canonical" href="{meta['canonical']}">
  <meta property="og:url" content="{meta['og_url']}">
  <meta property="og:image" content="https://saaspare.org/og/default.svg">
  <meta name="twitter:card" content="summary_large_image">
  {jld}
  {ga4}
{V2_HEAD}
</head>
<body class="sp-bg">

{V2_NAV}

  <div style="max-width:940px;margin:0 auto;padding:5rem 1.5rem 4rem;">
{inner}
  </div>

{V2_FOOT}

{STICKY}
</body>
</html>"""

    fp.write_text(new_html, encoding='utf-8')
    return True


def main():
    rebuilt = 0
    for fp in sorted(PAGES.glob('*.html')):
        if fp.name in SKIP or 'v3-preview' in fp.name:
            continue
        try:
            if rebuild(fp):
                rebuilt += 1
        except Exception as e:
            print(f"  ERROR {fp.name}: {e}")

    print(f"Upgraded {rebuilt} additional pages to v2 design")


if __name__ == '__main__':
    main()
