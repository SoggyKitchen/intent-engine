"""
Wave 19: Upgrade all non-VS pages to v2 design system chrome
- Applies saaspare-v2.css + motion.css + motion.js shell to review, pricing, coupon, hub, alternatives pages
- Preserves ALL existing content (no fake data introduced)
- Replaces old white-background inline styles with dark v2 design wrapper
- Adds v2 nav, v2 footer, sticky CTA where missing

Run: uv run python scripts/wave19_upgrade_non_vs_pages.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PAGES = SITE / "pages"

# Pages to skip entirely
SKIP_NAMES = {
    "coupon-verification-policy.html",
    "report-outdated-pricing.html",
    "editorial-policy.html",
    "corrections.html",
    "affiliate-disclosure.html",
}
SKIP_PATTERNS = ["v3-preview-"]

# Tool slug → affiliate route for sticky CTA
TOOL_GO = {
    "nordvpn": "/go/nordvpn", "surfshark": "/go/surfshark", "expressvpn": "/go/expressvpn",
    "sucuri": "/go/sucuri", "nordpass": "/go/nordpass", "semrush": "/go/semrush",
    "shopify": "/go/shopify", "elevenlabs": "/go/elevenlabs", "contabo": "/go/contabo",
    "hostpapa": "/go/hostpapa", "freshbooks": "/go/freshbooks-trial",
    "hubspot": "/go/hubspot-crm", "clickup": "/go/clickup-trial",
    "1password": "/go/1password-trial", "activecampaign": "/go/activecampaign-trial",
    "monday": "/go/monday", "xero": "/go/xero-trial", "dashlane": "/go/dashlane-trial",
    "kajabi": "/go/kajabi", "teachable": "/go/teachable", "quickbooks": "/go/quickbooks",
    "bitdefender": "/go/bitdefender", "malwarebytes": "/go/malwarebytes",
    "getresponse": "/go/getresponse-email", "ahrefs": "/go/ahrefs",
    "amplitude": "/go/amplitude", "asana": "/go/asana", "bigcommerce": "/go/bigcommerce",
    "canva": "/go/canva", "clearscope": "/go/clearscope", "copy-ai": "/go/copyai",
    "datadog": "/go/datadog", "digitalocean": "/go/digitalocean",
    "gusto": "/go/gusto", "hetzner": "/go/hetzner", "linear": "/go/linear",
    "miro": "/go/miro", "mixpanel": "/go/mixpanel", "moz": "/go/moz",
    "notion": "/go/notion", "pandadoc": "/go/pandadoc", "pipedrive": "/go/pipedrive",
    "ramp": "/go/ramp", "salesforce": "/go/salesforce", "slack": "/go/slack",
    "stripe": "/go/stripe", "supabase": "/go/supabase", "tresorit": "/go/tresorit",
    "vultr": "/go/vultr", "workable": "/go/workable", "zendesk": "/go/zendesk",
    "cyberghost": "/go/cyberghost", "protonvpn": "/go/protonvpn",
}

GA4_ID = "G-RLYVYV8WQJ"

V2_HEAD_ASSETS = """  <link rel="stylesheet" href="/assets/saaspare-v2.css">
  <link rel="stylesheet" href="/assets/motion.css">"""

V2_NAV = """  <nav class="sp-nav" id="sp-nav">
    <a href="/" class="sp-logo">SaaSpare</a>
    <div class="sp-nav-links">
      <a href="/pages/">Compare</a>
      <a href="/blog/">Blog</a>
      <a href="/about">About</a>
    </div>
  </nav>"""

V2_FOOTER = """  <footer class="sp-footer">
    <div style="max-width:1100px;margin:0 auto;padding:3rem 1.5rem 2rem;text-align:center;">
      <p style="color:var(--ink-4);font-size:.85rem;margin-bottom:.75rem;">
        &copy; 2026 SaaSpare.org &mdash; Independent B2B SaaS research
      </p>
      <div style="display:flex;gap:1.5rem;justify-content:center;flex-wrap:wrap;font-size:.82rem;">
        <a href="/" style="color:var(--ink-4);">Home</a>
        <a href="/blog/" style="color:var(--ink-4);">Blog</a>
        <a href="/about" style="color:var(--ink-4);">About</a>
        <a href="/affiliate-disclosure" style="color:var(--ink-4);">Affiliate Disclosure</a>
        <a href="/privacy" style="color:var(--ink-4);">Privacy</a>
        <a href="/editorial-policy" style="color:var(--ink-4);">Editorial Policy</a>
      </div>
    </div>
  </footer>
  <script src="/assets/motion.js"></script>"""

GA4_SNIPPET = f"""  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA4_ID}');
  </script>"""


def make_sticky_cta(go_url: str, tool_key: str, label: str) -> str:
    return f"""  <!-- Sticky Bottom CTA (v2) -->
  <div id="sticky-cta" style="position:fixed;bottom:0;left:0;right:0;z-index:999;background:rgba(5,4,7,0.97);backdrop-filter:blur(12px);border-top:1px solid rgba(255,65,109,0.25);padding:14px 20px;display:flex;align-items:center;justify-content:center;gap:16px;transform:translateY(100%);transition:transform 0.4s ease;">
    <span style="color:#a0a0b8;font-size:.88rem;">Ready to start?</span>
    <a href="{go_url}" target="_blank" rel="noopener sponsored"
       onclick="if(window.gtag){{gtag('event','affiliate_click',{{tool:'{tool_key}',placement:'sticky_cta',page:window.location.pathname}});}}"
       style="display:inline-flex;align-items:center;padding:10px 22px;background:linear-gradient(135deg,#ff416d,#ff6b35);color:#fff;font-weight:700;font-size:.92rem;border-radius:9999px;text-decoration:none;box-shadow:0 4px 20px rgba(255,65,109,0.35);">
      {label} →
    </a>
    <button onclick="document.getElementById('sticky-cta').style.display='none'" style="background:none;border:none;color:#666;cursor:pointer;font-size:1.2rem;padding:4px 8px;">&times;</button>
  </div>
  <script>
    (function(){{
      var bar=document.getElementById('sticky-cta');
      if(!bar) return;
      var shown=false;
      window.addEventListener('scroll',function(){{
        if(!shown&&window.scrollY>300){{bar.style.transform='translateY(0)';shown=true;}}
      }},{{passive:true}});
    }})();
  </script>"""


def extract_inner_body(html: str) -> str:
    """Extract content between <body> and </body>, stripping old nav/header/footer."""
    # Get body content
    body_match = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL | re.IGNORECASE)
    if not body_match:
        return html
    body = body_match.group(1)

    # Remove old header/nav elements (they'll be replaced by v2 nav)
    body = re.sub(r'<header[^>]*>.*?</header>', '', body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<nav[^>]*>.*?</nav>', '', body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<footer[^>]*>.*?</footer>', '', body, flags=re.DOTALL | re.IGNORECASE)

    # Remove old sticky CTA if present (will add fresh one)
    body = re.sub(r'<!-- Sticky.*?</script>', '', body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<div[^>]*id="sticky-cta"[^>]*>.*?</script>', '', body, flags=re.DOTALL | re.IGNORECASE)

    return body.strip()


def extract_head_meta(html: str) -> dict:
    """Extract key meta tags from existing page."""
    meta = {}
    title_m = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
    meta['title'] = title_m.group(1) if title_m else "SaaSpare"

    desc_m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html, re.IGNORECASE)
    meta['desc'] = desc_m.group(1) if desc_m else ""

    canon_m = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', html, re.IGNORECASE)
    meta['canonical'] = canon_m.group(1) if canon_m else ""

    og_title_m = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html, re.IGNORECASE)
    meta['og_title'] = og_title_m.group(1) if og_title_m else meta['title']

    og_desc_m = re.search(r'<meta\s+property="og:description"\s+content="([^"]+)"', html, re.IGNORECASE)
    meta['og_desc'] = og_desc_m.group(1) if og_desc_m else meta['desc']

    og_url_m = re.search(r'<meta\s+property="og:url"\s+content="([^"]+)"', html, re.IGNORECASE)
    meta['og_url'] = og_url_m.group(1) if og_url_m else ""

    # Extract all JSON-LD blocks
    meta['jsonld'] = re.findall(
        r'<script\s+type="application/ld\+json"[^>]*>.*?</script>',
        html, re.DOTALL | re.IGNORECASE
    )

    # Noindex
    meta['noindex'] = bool(re.search(r'noindex', html, re.IGNORECASE))

    return meta


def get_tool_key_and_cta(filename: str):
    """Determine the tool key and CTA config for a page."""
    name = filename.replace('.html', '')
    # Remove common suffixes
    for suffix in [
        '-review-2026', '-pricing-2026-plans-costs-what-you-actually-pay',
        '-pricing-history-2026', '-pricing-2026', '-pricing',
        '-coupon-code-promo-codes-2026-verified-discounts',
        '-coupon-2026-discount-codes-promo',
        '-promo-codes-2026-verified-deals',
        '-coupon-2026', '-free-trial-2026-how-to-get-it-step-by-step',
        '-free-trial-2026', '-alternatives-2026',
        '-promo-code-2026-discounts-deals-that-actually-work',
    ]:
        name = name.replace(suffix, '')

    # Remove leading "7-best-" or "X-best-"
    name = re.sub(r'^\d+-best-', '', name)
    name = re.sub(r'-alternatives$', '', name)

    for key, go_url in TOOL_GO.items():
        if name == key or name.startswith(key + '-') or name.endswith('-' + key):
            labels = {
                'review': 'Try It Free',
                'pricing': 'See Best Price',
                'coupon': 'Get This Deal',
            }
            label = 'Try It Free'
            if 'pricing' in filename:
                label = 'See Best Price'
            elif 'coupon' in filename or 'promo' in filename or 'discount' in filename:
                label = 'Get This Deal'
            return key, go_url, label

    # Generic fallback
    return name, '/go/semrush', 'Compare Top Tools'


def rebuild_page(fp: Path) -> bool:
    """Wrap existing page content in v2 design shell."""
    original = fp.read_text(encoding='utf-8', errors='replace')

    # Skip if already v2
    if 'saaspare-v2.css' in original:
        return False

    meta = extract_head_meta(original)
    inner = extract_inner_body(original)
    tool_key, go_url, cta_label = get_tool_key_and_cta(fp.name)

    noindex_tag = '\n  <meta name="robots" content="noindex,nofollow">' if meta['noindex'] else ''
    jsonld_blocks = '\n  '.join(meta['jsonld'])

    sticky_cta = make_sticky_cta(go_url, tool_key, cta_label)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">{noindex_tag}
  <title>{meta['title']}</title>
  <meta name="description" content="{meta['desc']}">
  <link rel="canonical" href="{meta['canonical']}">
  <meta property="og:title" content="{meta['og_title']}">
  <meta property="og:description" content="{meta['og_desc']}">
  <meta property="og:url" content="{meta['og_url']}">
  <meta property="og:image" content="https://saaspare.org/og/default.svg">
  <meta name="twitter:card" content="summary_large_image">
  {jsonld_blocks}
{GA4_SNIPPET}
{V2_HEAD_ASSETS}
</head>
<body class="sp-bg">

{V2_NAV}

  <div style="max-width:900px;margin:0 auto;padding:5rem 1.5rem 4rem;">
{inner}
  </div>

{V2_FOOTER}

{sticky_cta}
</body>
</html>"""

    fp.write_text(html, encoding='utf-8')
    return True


def main():
    # Collect target pages: review, pricing, coupon, promo, discount, hub, alternatives, blog-style
    patterns = ['*review*.html', '*pricing*.html', '*coupon*.html', '*promo*.html',
                '*discount*.html', '*deal*.html', '*alternatives*.html', '*free-trial*.html',
                '*hub*.html']

    seen = set()
    targets = []
    for pat in patterns:
        for fp in PAGES.glob(pat):
            if fp.name not in seen:
                seen.add(fp.name)
                targets.append(fp)

    # Also include blog pages
    blog_dir = SITE / 'blog'
    if blog_dir.exists():
        for fp in blog_dir.glob('*.html'):
            if fp.name not in seen:
                seen.add(fp.name)
                targets.append(fp)

    rebuilt = 0
    skipped_skip = 0
    skipped_v2 = 0
    errors = 0

    total = len(targets)
    print(f"Processing {total} non-VS pages…")

    for i, fp in enumerate(sorted(targets), 1):
        # Skip list
        if fp.name in SKIP_NAMES:
            skipped_skip += 1
            continue
        if any(pat in fp.name for pat in SKIP_PATTERNS):
            skipped_skip += 1
            continue

        try:
            if rebuild_page(fp):
                rebuilt += 1
            else:
                skipped_v2 += 1
        except Exception as e:
            errors += 1
            print(f"  ERROR {fp.name}: {e}")

        if rebuilt % 50 == 0 and rebuilt > 0:
            print(f"  Rebuilt {rebuilt}/{total}…")

    print(f"\nDone.")
    print(f"  Upgraded to v2:   {rebuilt}")
    print(f"  Already v2:       {skipped_v2}")
    print(f"  Skipped (policy): {skipped_skip}")
    print(f"  Errors:           {errors}")


if __name__ == '__main__':
    main()
