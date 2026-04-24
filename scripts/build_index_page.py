"""
Rebuilds site/pages/index.html as a polished dark-theme directory page.
Scans all site/pages/*.html, auto-categorises, prettifies titles, and renders
a card-grid layout matching the homepage design.
Run: .venv/Scripts/python scripts/build_index_page.py
"""
import re
from pathlib import Path

PAGES = Path("site/pages")
DOMAIN = "https://saaspare.org"

SKIP = {"index", "thanks", "verification", "saas-roi-calculator"}

def pretty_title(slug: str) -> str:
    """Convert slug to a clean human-readable title."""
    s = slug
    s = re.sub(r'-2026.*', '', s)
    s = re.sub(r'-2025.*', '', s)
    s = s.replace('-vs-', ' vs ')
    s = s.replace('-io', '.io')
    s = s.replace('-ai', ' AI')
    s = s.replace('-com', '.com')
    words = s.split('-')
    titled = []
    for w in words:
        if w.lower() in ('vs', 'for', 'the', 'in', 'of', 'and', 'to', 'a', 'an', 'is', 'it'):
            titled.append(w.lower())
        else:
            titled.append(w.capitalize())
    title = ' '.join(titled)
    # Fix known brand names
    brands = {
        'Semrush': 'Semrush', 'Ahrefs': 'Ahrefs', 'Hubspot': 'HubSpot',
        'Clickup': 'ClickUp', 'Freshbooks': 'FreshBooks', 'Bigcommerce': 'BigCommerce',
        'Digitalocean': 'DigitalOcean', 'Pandadoc': 'PandaDoc', 'Nordlayer': 'NordLayer',
        'Bamboohr': 'BambooHR', 'Docusign': 'DocuSign', 'Activecampaign': 'ActiveCampaign',
        'Moz': 'Moz', 'Spyfu': 'SpyFu', 'Surfer': 'Surfer SEO', 'Rankmath': 'RankMath',
        'Se': 'SE', 'Saas': 'SaaS', 'Devops': 'DevOps', '1password': '1Password',
        'Jasper': 'Jasper AI', 'Copy': 'Copy.AI', 'Pipedrive': 'Pipedrive',
        'Clearscope': 'Clearscope', 'Mangools': 'Mangools', 'Frase': 'Frase.io',
        'Crm': 'CRM', 'Seo': 'SEO', 'Pm': 'PM',
    }
    for wrong, right in brands.items():
        title = re.sub(r'\b' + wrong + r'\b', right, title, flags=re.IGNORECASE)
    return title.strip()


def categorise(slug: str) -> str:
    if re.search(r'-vs-', slug):
        return 'Comparisons'
    if 'alternatives' in slug:
        return 'Alternatives'
    if 'pricing' in slug:
        return 'Pricing Guides'
    if 'review' in slug:
        return 'Reviews'
    if 'free-trial' in slug:
        return 'Free Trials'
    if 'promo-code' in slug or 'coupon' in slug or 'discount' in slug:
        return 'Promo Codes & Deals'
    if slug.startswith('best-'):
        return 'Best-Of Lists'
    return 'Other'

CAT_ORDER = ['Comparisons', 'Alternatives', 'Pricing Guides', 'Reviews',
             'Free Trials', 'Promo Codes & Deals', 'Best-Of Lists', 'Other']

CAT_ICONS = {
    'Comparisons': '⚡',
    'Alternatives': '🔄',
    'Pricing Guides': '💰',
    'Reviews': '⭐',
    'Free Trials': '🎁',
    'Promo Codes & Deals': '🏷️',
    'Best-Of Lists': '🏆',
    'Other': '📄',
}

CAT_DESC = {
    'Comparisons': 'Side-by-side breakdowns of competing tools',
    'Alternatives': 'Best alternatives to popular SaaS tools',
    'Pricing Guides': 'Exact plans, costs & what you actually pay',
    'Reviews': 'Honest verdicts with pros, cons & scores',
    'Free Trials': 'How to get free access, step by step',
    'Promo Codes & Deals': 'Working discount codes & limited offers',
    'Best-Of Lists': 'Top picks across categories & use cases',
    'Other': 'Additional guides & resources',
}


def build():
    cats: dict[str, list[tuple[str, str]]] = {c: [] for c in CAT_ORDER}

    for f in sorted(PAGES.glob("*.html")):
        if f.stem in SKIP:
            continue
        cat = categorise(f.stem)
        title = pretty_title(f.stem)
        url = f"{DOMAIN}/pages/{f.name}"
        cats[cat].append((url, title))

    total = sum(len(v) for v in cats.values())

    sections_html = ""
    for cat in CAT_ORDER:
        items = cats[cat]
        if not items:
            continue
        icon = CAT_ICONS[cat]
        desc = CAT_DESC[cat]
        items_html = "\n".join(
            f'          <a href="{url}" class="page-link">{title}</a>'
            for url, title in items
        )
        sections_html += f"""
  <section class="cat-section">
    <div class="cat-header">
      <div class="cat-icon">{icon}</div>
      <div>
        <h2>{cat} <span class="count">({len(items)})</span></h2>
        <p class="cat-desc">{desc}</p>
      </div>
    </div>
    <div class="page-grid">
{items_html}
    </div>
  </section>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>All SaaS Comparisons & Guides | SaaSpare</title>
<meta name="description" content="Browse {total} B2B SaaS comparison pages, pricing guides, reviews and alternatives — all free.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{DOMAIN}/pages/">
<meta property="og:title" content="All SaaS Comparisons & Guides | SaaSpare">
<meta property="og:description" content="Browse {total} B2B SaaS comparison pages, pricing guides, reviews and alternatives — all free.">
<meta property="og:image" content="{DOMAIN}/og-default.png">
<meta property="og:type" content="website">
<meta property="og:url" content="{DOMAIN}/pages/">
<meta name="google-adsense-account" content="ca-pub-9433840442322701">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="preconnect" href="https://pagead2.googlesyndication.com" crossorigin>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9433840442322701" crossorigin="anonymous"></script>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Plus Jakarta Sans',system-ui,sans-serif;background:#080810;color:rgba(255,255,255,.85);line-height:1.6}}
  /* NAV */
  nav{{background:rgba(8,8,16,.92);backdrop-filter:blur(24px);border-bottom:1px solid rgba(255,255,255,.06);padding:.75rem 1.5rem;display:flex;align-items:center;gap:1.5rem;position:sticky;top:0;z-index:50}}
  .logo{{display:flex;align-items:center;gap:.6rem;text-decoration:none;margin-right:auto}}
  .logo-bars{{display:flex;flex-direction:column;gap:3px}}
  .logo-bars span{{display:block;height:2px;border-radius:2px;background:#e94560}}
  .logo-bars span:nth-child(1){{width:18px}}
  .logo-bars span:nth-child(2){{width:12px}}
  .logo-bars span:nth-child(3){{width:15px}}
  .logo-text{{font-weight:800;font-size:1.15rem;color:#fff;letter-spacing:-.02em}}
  .logo-text em{{font-style:normal;color:#e94560}}
  nav a{{color:rgba(255,255,255,.55);text-decoration:none;font-size:.875rem;font-weight:500;transition:color .2s}}
  nav a:hover{{color:#fff}}
  /* HERO */
  .hero{{background:radial-gradient(ellipse 120% 80% at 50% -10%,#1a0d12 0%,#0d0008 45%,#080810 80%);padding:3.5rem 1.5rem 2.5rem;text-align:center;border-bottom:1px solid rgba(255,255,255,.05)}}
  .hero h1{{font-size:clamp(1.8rem,5vw,3rem);font-weight:800;letter-spacing:-.03em;line-height:1.1;color:#fff;margin-bottom:.6rem}}
  .hero h1 em{{font-style:normal;color:#e94560}}
  .hero-sub{{color:rgba(255,255,255,.5);font-size:1.05rem;margin-bottom:1.5rem}}
  .stat-pills{{display:flex;gap:.75rem;justify-content:center;flex-wrap:wrap;margin-top:1rem}}
  .stat-pill{{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:50px;padding:.35rem .9rem;font-size:.82rem;color:rgba(255,255,255,.65);font-weight:500}}
  .stat-pill strong{{color:#fff}}
  /* SEARCH */
  .search-bar{{max-width:500px;margin:1.5rem auto 0;position:relative}}
  .search-bar input{{width:100%;padding:.75rem 1rem .75rem 2.75rem;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:12px;color:#fff;font-size:.95rem;font-family:inherit;outline:none;transition:border-color .2s}}
  .search-bar input::placeholder{{color:rgba(255,255,255,.3)}}
  .search-bar input:focus{{border-color:rgba(233,69,96,.4)}}
  .search-bar svg{{position:absolute;left:.85rem;top:50%;transform:translateY(-50%);color:rgba(255,255,255,.3)}}
  /* CONTAINER */
  .container{{max-width:980px;margin:0 auto;padding:2rem 1rem 4rem}}
  /* CATEGORY SECTIONS */
  .cat-section{{margin:2.5rem 0}}
  .cat-header{{display:flex;align-items:flex-start;gap:.9rem;margin-bottom:1rem}}
  .cat-icon{{font-size:1.4rem;width:2.4rem;height:2.4rem;background:rgba(233,69,96,.1);border:1px solid rgba(233,69,96,.2);border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:.1rem}}
  .cat-header h2{{font-size:1.1rem;color:#fff;font-weight:700;letter-spacing:-.01em}}
  .count{{color:rgba(255,255,255,.35);font-weight:400;font-size:.95rem}}
  .cat-desc{{color:rgba(255,255,255,.4);font-size:.82rem;margin-top:.1rem}}
  /* PAGE GRID */
  .page-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:.5rem}}
  .page-link{{display:block;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:10px;padding:.6rem .9rem;font-size:.85rem;color:rgba(255,255,255,.7);text-decoration:none;font-weight:500;transition:all .18s;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
  .page-link:hover{{background:rgba(233,69,96,.08);border-color:rgba(233,69,96,.25);color:#fff}}
  /* DIVIDER */
  .divider{{border:none;border-top:1px solid rgba(255,255,255,.06);margin:0}}
  /* FOOTER */
  footer{{text-align:center;color:rgba(255,255,255,.25);font-size:.82rem;padding:2rem 1rem;border-top:1px solid rgba(255,255,255,.07)}}
  footer a{{color:rgba(255,255,255,.35);text-decoration:none}}
  footer a:hover{{color:rgba(255,255,255,.7)}}
  /* HIDDEN search */
  .page-link.hidden{{display:none}}
  @media(max-width:600px){{.page-grid{{grid-template-columns:1fr 1fr}}.hero h1{{font-size:1.8rem}}nav .hide-mobile{{display:none}}}}
</style>
</head>
<body>
<nav>
  <a href="{DOMAIN}" class="logo">
    <div class="logo-bars"><span></span><span></span><span></span></div>
    <div class="logo-text">Saa<em>Spare</em></div>
  </a>
  <a href="{DOMAIN}/pages/" class="hide-mobile">All Comparisons</a>
  <a href="{DOMAIN}/about.html" class="hide-mobile">About</a>
</nav>

<div class="hero">
  <h1>All SaaS <em>Comparisons</em> & Guides</h1>
  <p class="hero-sub">{total} pages covering pricing, comparisons, reviews and alternatives</p>
  <div class="stat-pills">
    <span class="stat-pill"><strong>{len(cats['Comparisons'])}</strong> Comparisons</span>
    <span class="stat-pill"><strong>{len(cats['Pricing Guides'])}</strong> Pricing Guides</span>
    <span class="stat-pill"><strong>{len(cats['Reviews'])}</strong> Reviews</span>
    <span class="stat-pill"><strong>{len(cats['Alternatives'])}</strong> Alternatives</span>
    <span class="stat-pill"><strong>{len(cats['Free Trials'])}</strong> Free Trials</span>
  </div>
  <div class="search-bar">
    <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
    <input type="text" id="search" placeholder="Search tools, categories…" autocomplete="off">
  </div>
</div>

<div class="container">
{sections_html}
</div>

<footer>
  <p>Last updated: April 24, 2026 &nbsp;·&nbsp;
  <a href="{DOMAIN}/about.html">About</a> &nbsp;·&nbsp;
  <a href="{DOMAIN}/privacy.html">Privacy</a></p>
</footer>

<script>
var inp=document.getElementById('search');
var links=document.querySelectorAll('.page-link');
inp.addEventListener('input',function(){{
  var q=this.value.toLowerCase().trim();
  links.forEach(function(a){{
    a.classList.toggle('hidden', q && !a.textContent.toLowerCase().includes(q));
  }});
  document.querySelectorAll('.cat-section').forEach(function(s){{
    var vis=[...s.querySelectorAll('.page-link')].some(function(a){{return !a.classList.contains('hidden')}});
    s.style.display=(!q||vis)?'':'none';
  }});
}});
</script>
</body>
</html>"""
    out = PAGES / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"Built index.html — {total} pages across {sum(1 for c in cats.values() if c)} categories")


if __name__ == "__main__":
    build()
