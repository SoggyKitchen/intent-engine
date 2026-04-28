import os
import re
import subprocess
import time
from pathlib import Path

import httpx

from core.db import db
from core.logger import log
from core.secrets import DRY_RUN, get

SITE_DIR = Path("site")
PAGES_DIR = Path("site/pages")


def deploy_all() -> bool:
    _enhance_site_html(SITE_DIR)
    _rebuild_sitemap(SITE_DIR)
    _rebuild_homepage(SITE_DIR)
    _rebuild_pages_index(SITE_DIR)
    _enhance_site_html(SITE_DIR)
    _ping_indexnow(SITE_DIR)

    if DRY_RUN:
        log.info("[DRY RUN] Would deploy to Cloudflare Pages")
        return True

    hook = get("CF_PAGES_DEPLOY_HOOK")
    if hook:
        return _deploy_via_webhook(hook)

    repo = get("CF_PAGES_REPO")
    if repo:
        return _deploy_via_git(repo)

    log.warning("No CF_PAGES_DEPLOY_HOOK or CF_PAGES_REPO set — skipping deploy")
    return False


def _deploy_via_webhook(hook_url: str) -> bool:
    try:
        resp = httpx.post(hook_url, timeout=30)
        resp.raise_for_status()
        log.info("Cloudflare Pages deploy triggered via webhook")
        return True
    except Exception as e:
        log.error(f"CF Pages webhook deploy failed: {e}")
        return False


def _deploy_via_git(repo_url: str) -> bool:
    try:
        site_repo = Path("site_deploy")
        if not site_repo.exists():
            subprocess.run(["git", "clone", repo_url, str(site_repo)], check=True,
                           capture_output=True)

        pages_dest = site_repo / "pages"
        pages_dest.mkdir(exist_ok=True)

        for html_file in PAGES_DIR.glob("*.html"):
            dest = pages_dest / html_file.name
            dest.write_text(html_file.read_text(encoding="utf-8"), encoding="utf-8")

        redirects_src = SITE_DIR / "_redirects"
        if redirects_src.exists():
            (site_repo / "_redirects").write_text(
                redirects_src.read_text(encoding="utf-8"), encoding="utf-8"
            )

        _rebuild_sitemap(site_repo)
        _ping_indexnow(site_repo)

        env = {**os.environ, "GIT_AUTHOR_NAME": "IntentBot",
               "GIT_AUTHOR_EMAIL": "bot@intentengine.local",
               "GIT_COMMITTER_NAME": "IntentBot",
               "GIT_COMMITTER_EMAIL": "bot@intentengine.local"}

        subprocess.run(["git", "-C", str(site_repo), "add", "-A"], check=True, env=env)
        result = subprocess.run(
            ["git", "-C", str(site_repo), "commit", "-m",
             f"chore: publish pages {time.strftime('%Y-%m-%d %H:%M')} [skip ci]"],
            capture_output=True, env=env,
        )
        if result.returncode == 0:
            subprocess.run(["git", "-C", str(site_repo), "push"], check=True, env=env)
            log.info("Site deployed via git push")
        else:
            log.info("No new pages to deploy")
        return True
    except Exception as e:
        log.error(f"Git deploy failed: {e}")
        return False


_SITEMAP_EXCLUDE = {"index", "thanks", "verification"}
_PAGES_EXCLUDE = {"index", "thanks", "verification"}

_MOJIBAKE_REPLACEMENTS = {
    "â€”": " - ",
    "â€“": " - ",
    "â†’": " -> ",
    "Â·": " · ",
    "Ã—": "x",
}


def _inject_once(html: str, marker: str, snippet: str, before: str) -> str:
    if marker in html:
        return html
    return html.replace(before, snippet + before, 1)


def _enhance_site_html(site_dir: Path = SITE_DIR) -> int:
    """Attach shared SaaSpare UX assets to every public HTML page."""
    paths = list(site_dir.glob("*.html"))
    pages_dir = site_dir / "pages"
    if pages_dir.exists():
        paths.extend(pages_dir.glob("*.html"))

    changed = 0
    for path in paths:
        if path.stem in {"thanks", "verification"}:
            continue
        try:
            html = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        original = html
        html = _inject_once(
            html,
            "saaspare-ui.css",
            '<link rel="stylesheet" href="/assets/saaspare-ui.css">\n',
            "</head>",
        )
        html = _inject_once(
            html,
            "saaspare-ui.js",
            '<script defer src="/assets/saaspare-ui.js"></script>\n',
            "</body>",
        )
        if html != original:
            path.write_text(html, encoding="utf-8")
            changed += 1
    if changed:
        log.info(f"Enhanced shared SaaSpare UX assets on {changed} HTML pages")
    return changed


def _clean_display_text(text: str) -> str:
    cleaned = (text or "").strip()
    for bad, good in _MOJIBAKE_REPLACEMENTS.items():
        cleaned = cleaned.replace(bad, good)
    cleaned = cleaned.replace("| SaaSpare", "").strip()
    cleaned = cleaned.replace(".io.io", ".io")
    cleaned = re.sub(r"\b(SEO|CRM|SaaS|AI|PM) \1\b", r"\1", cleaned)
    cleaned = re.sub(r"\b([A-Z][a-z0-9.+]+) \1\b", r"\1", cleaned)
    cleaned = re.sub(r"\bWhich Is Better In\s*$", "Which Is Better", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned.strip(" -")


def _page_label(stem: str) -> str:
    label = stem.replace("-vs-", " vs ")
    label = label.replace("-io", ".io")
    label = label.replace("-ai", " ai")
    label = label.replace("-com", ".com")
    label = re.sub(r"-\d{4}.*$", "", label)
    label = " ".join(part for part in label.split("-") if part)
    label = " ".join(word.capitalize() for word in label.split())
    replacements = {
        "Hubspot": "HubSpot",
        "Clickup": "ClickUp",
        "Freshbooks": "FreshBooks",
        "Bigcommerce": "BigCommerce",
        "Digitalocean": "DigitalOcean",
        "Pandadoc": "PandaDoc",
        "Nordlayer": "NordLayer",
        "Bamboohr": "BambooHR",
        "Docusign": "DocuSign",
        "Activecampaign": "ActiveCampaign",
        "Rankmath": "RankMath",
        "Spyfu": "SpyFu",
        "Frase Io": "Frase.io",
        "Copy Ai": "Copy.ai",
        "Monday Com": "Monday.com",
        "Se Ranking": "SE Ranking",
        "Seo": "SEO",
        "Crm": "CRM",
        "Pm": "PM",
        "Saas": "SaaS",
    }
    for wrong, right in replacements.items():
        label = re.sub(rf"\b{wrong}\b", right, label)
    label = label.replace(" Vs ", " vs ")
    return _clean_display_text(label)


def _detect_page_type(stem: str) -> str:
    lower = stem.lower()
    if "-vs-" in lower:
        return "comparison"
    if "pricing" in lower or "-cost" in lower:
        return "pricing"
    if "alternatives" in lower or "alternative" in lower:
        return "alternatives"
    if "review" in lower:
        return "review"
    if "promo-code" in lower or "coupon" in lower or "discount" in lower:
        return "promo"
    if "free-trial" in lower or "free-plan" in lower or "free-tier" in lower or lower.startswith("does-"):
        return "free-trial"
    if lower.startswith("best-"):
        return "best-of"
    return "guide"


def _page_title_from_html(path: Path) -> str:
    try:
        html = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return _page_label(path.stem)
    match = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    if not match:
        return _page_label(path.stem)
    title = _clean_display_text(match.group(1))
    return title or _page_label(path.stem)


def _homepage_stats(site_dir: Path) -> tuple[int, int, int]:
    pages_dir = site_dir / "pages"
    pages = [p for p in pages_dir.glob("*.html") if p.stem not in _PAGES_EXCLUDE] if pages_dir.exists() else []
    page_count = len(pages)
    weekly_pages = sum(
        1 for p in pages
        if (time.time() - p.stat().st_mtime) <= 7 * 86400
    )
    categories = set()
    for page in pages:
        title = _page_title_from_html(page).lower()
        if " vs " in title:
            categories.add("comparisons")
        elif "pricing" in title:
            categories.add("pricing")
        elif "review" in title:
            categories.add("review")
        elif "alternative" in title:
            categories.add("alternatives")
        elif "free plan" in title or "free trial" in title:
            categories.add("free")
        elif "best " in title:
            categories.add("best")
        else:
            categories.add("other")
    return page_count, max(len(categories), 1), weekly_pages

def _rebuild_homepage(site_dir: Path):
    index_path = site_dir / "index.html"
    if not index_path.exists():
        return
    pages_dir = site_dir / "pages"
    pages = [p for p in sorted(pages_dir.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)
             if p.stem not in _PAGES_EXCLUDE] if pages_dir.exists() else []
    html = index_path.read_text(encoding="utf-8")
    page_count, category_count, weekly_pages = _homepage_stats(site_dir)
    replacements = [
        ("Tool comparisons", page_count),
        ("SaaS categories", category_count),
        ("New pages weekly", weekly_pages),
    ]
    for label, count in replacements:
        html = re.sub(
            rf'(<span class="stat-val" data-count=")\d+(">)(?:\d+)(</span><span class="stat-label">{re.escape(label)}</span>)',
            lambda m: f"{m.group(1)}{count}{m.group(2)}{count}{m.group(3)}",
            html,
        )
    newsletter_form_action = get(
        "NEWSLETTER_FORM_ACTION",
        "https://formsubmit.co/smithelly30121@gmail.com",
    )
    html = re.sub(
        r'action="https://formsubmit\.co/[^"]+"',
        f'action="{newsletter_form_action}"',
        html,
    )
    html = re.sub(
        r'(<div class="badge"><span class="badge-dot"></span>)(.*?)(</div>)',
        rf'\g<1>{page_count} comparisons live\g<3>',
        html,
        count=1,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"function doHeroSearch\(\)\{const q=document\.getElementById\('hero-search'\)\.value\.trim\(\);if\(q\)window\.location\.href='/pages/'\}",
        "function doHeroSearch(){const q=document.getElementById('hero-search').value.trim();window.location.href=q?'/pages/?q='+encodeURIComponent(q):'/pages/';}",
        html,
        count=1,
    )
    featured_pages = {
        "Marketing Automation": ("hubspot", "pricing"),
        "Dev Tools": ("datadog",),
        "Cybersecurity": ("1password",),
        "Cloud Infrastructure": ("digitalocean",),
        "Legal &amp; Contracts": ("pandadoc",),
        "AI Writing Tools": ("jasper",),
    }
    for label, keywords in featured_pages.items():
        target = "/pages/"
        for page in pages:
            stem = page.stem.lower()
            if all(keyword in stem for keyword in keywords):
                target = f"/pages/{page.stem}"
                break
        html = re.sub(
            rf'(<a class="cat-card" href=")/pages/("><span class="cat-emoji">.*?<div class="cat-name">{label}</div>)',
            rf'\g<1>{target}\2',
            html,
            count=1,
            flags=re.DOTALL,
        )
    index_path.write_text(html, encoding="utf-8")
    log.info(
        f"Homepage updated: {page_count} pages, {category_count} content groups, {weekly_pages} new this week"
    )

def _rebuild_sitemap(site_repo: Path):
    pages_dir = site_repo / "pages"
    pages = list(pages_dir.glob("*.html")) if pages_dir.exists() else []
    domain = get("SITE_DOMAIN", "https://saaspare.org")
    today = time.strftime("%Y-%m-%d")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f'  <url><loc>{domain}/</loc><lastmod>{today}</lastmod><priority>1.0</priority></url>',
    ]
    for p in sorted(site_repo.glob("*.html")):
        if p.stem not in _SITEMAP_EXCLUDE:
            lines.append(f'  <url><loc>{domain}/{p.stem}</loc><lastmod>{today}</lastmod><priority>0.7</priority></url>')
    for p in sorted(pages):
        if p.stem not in _SITEMAP_EXCLUDE:
            lines.append(f'  <url><loc>{domain}/pages/{p.stem}</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>')
    lines.append("</urlset>")
    (site_repo / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info(f"Sitemap rebuilt: {len(pages)} comparison pages + static pages")


def _rebuild_pages_index(site_dir: Path = SITE_DIR):
    pages_dir = site_dir if site_dir.name == "pages" else site_dir / "pages"
    if not pages_dir.exists():
        log.warning("_rebuild_pages_index: pages dir not found")
        return

    TYPE_ORDER = ["comparison", "pricing", "alternatives", "review", "promo", "free-trial", "best-of", "guide"]
    TYPE_LABELS = {
        "comparison": "Comparisons",
        "pricing": "Pricing Guides",
        "alternatives": "Alternatives",
        "review": "Reviews",
        "promo": "Coupon & Promo Codes",
        "free-trial": "Free Trials",
        "best-of": "Best-Of Lists",
        "guide": "Other Pages",
    }

    grouped: dict[str, list[tuple[str, str]]] = {t: [] for t in TYPE_ORDER}
    domain = get("SITE_DOMAIN", "https://saaspare.org")
    ga_id = get("GA_MEASUREMENT_ID", "G-RLYVYV8WQJ")

    for f in sorted(pages_dir.glob("*.html"), key=lambda p: p.stem):
        if f.stem in _PAGES_EXCLUDE:
            continue
        ptype = _detect_page_type(f.stem)
        label = _page_title_from_html(f)
        url = f"{domain}/pages/{f.stem}"
        grouped[ptype].append((label, url))

    total = sum(len(v) for v in grouped.values())
    filter_chip_parts = [
        f'    <button class="filter-chip active" data-type="all" type="button">All <span>{total}</span></button>'
    ]
    filter_chip_parts.extend(
        f'    <button class="filter-chip" data-type="{key}" type="button">{TYPE_LABELS[key]} <span>{len(grouped[key])}</span></button>'
        for key in TYPE_ORDER
        if grouped[key]
    )
    filter_chips = "\n".join(filter_chip_parts)
    page_cards = "\n".join(
        f'    <a class="page-card" href="{url}" data-type="{ptype}" data-title="{label.lower()}">'
        f'<span class="page-type">{TYPE_LABELS[ptype]}</span>'
        f'<span class="page-title">{label}</span>'
        f'<span class="page-arrow">-></span>'
        f'</a>'
        for ptype in TYPE_ORDER
        for label, url in grouped[ptype]
    )

    today = time.strftime("%B %d, %Y")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>All SaaS Comparisons & Guides | SaaSpare</title>
<meta name="description" content="Browse {total} B2B SaaS comparison pages, pricing guides, reviews and alternatives - all free.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{domain}/pages/">
<link rel="stylesheet" href="/assets/saaspare-ui.css">
<meta property="og:title" content="All SaaS Comparisons & Guides | SaaSpare">
<meta property="og:description" content="Browse {total} B2B SaaS comparison pages, pricing guides, reviews and alternatives - all free.">
<meta property="og:type" content="website">
<meta property="og:url" content="{domain}/pages/">
<style>
  :root{{--bg:#080810;--bg-soft:#11131a;--border:rgba(255,255,255,.08);--text:rgba(255,255,255,.84);--muted:rgba(255,255,255,.46);--accent:#e94560}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Plus Jakarta Sans',system-ui,sans-serif;background:radial-gradient(ellipse 120% 80% at 50% -10%,#1a0d12 0%,#0d0008 45%,#080810 80%);color:var(--text);line-height:1.6;min-height:100vh}}
  a{{color:inherit;text-decoration:none}}
  nav{{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:1rem;padding:1rem 1.5rem;background:rgba(8,8,16,.92);backdrop-filter:blur(24px);border-bottom:1px solid var(--border)}}
  nav a{{color:var(--muted);font-size:.9rem}}
  nav a:first-child{{margin-right:auto}}
  nav a:hover{{color:#fff}}
  .hero{{max-width:1100px;margin:0 auto;padding:4rem 1.5rem 2rem;text-align:center}}
  .hero h1{{font-size:clamp(2rem,5vw,3.2rem);color:#fff;letter-spacing:-.04em;margin-bottom:.75rem}}
  .hero p{{color:var(--muted);max-width:760px;margin:0 auto 1.5rem}}
  .search-shell{{max-width:680px;margin:0 auto 1rem;padding:.5rem;background:rgba(255,255,255,.06);border:1px solid var(--border);border-radius:999px;display:flex;gap:.5rem}}
  .search-shell input{{flex:1;background:transparent;border:none;color:#fff;padding:.85rem 1rem;outline:none;font:inherit}}
  .search-shell button{{border:none;border-radius:999px;background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.85rem 1.25rem;font:inherit;font-weight:700;cursor:pointer}}
  .stats{{display:flex;justify-content:center;gap:1rem;flex-wrap:wrap;margin-top:1rem}}
  .stat{{background:rgba(255,255,255,.05);border:1px solid var(--border);border-radius:999px;padding:.5rem .9rem;color:var(--muted);font-size:.85rem}}
  .container{{max-width:1100px;margin:0 auto;padding:1.5rem 1.5rem 4rem}}
  .filter-row{{display:flex;gap:.6rem;flex-wrap:wrap;align-items:center;margin-bottom:1.25rem}}
  .filter-chip{{border:1px solid var(--border);background:rgba(255,255,255,.04);color:var(--muted);border-radius:999px;padding:.5rem .8rem;cursor:pointer;font:inherit}}
  .filter-chip.active,.filter-chip:hover{{background:rgba(233,69,96,.14);border-color:rgba(233,69,96,.35);color:#fff}}
  .filter-chip span{{opacity:.7;margin-left:.25rem}}
  .results{{margin-left:auto;color:var(--muted);font-size:.85rem}}
  .pages-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:.75rem}}
  .page-card{{display:flex;flex-direction:column;gap:.5rem;padding:1rem 1.1rem;border-radius:18px;background:rgba(255,255,255,.04);border:1px solid var(--border);transition:transform .16s ease,border-color .16s ease,background .16s ease}}
  .page-card:hover{{transform:translateY(-2px);background:rgba(255,255,255,.06);border-color:rgba(233,69,96,.35)}}
  .page-card.hidden{{display:none}}
  .page-type{{font-size:.72rem;color:#ffb5c0;text-transform:uppercase;letter-spacing:.08em}}
  .page-title{{font-size:.95rem;color:#fff;font-weight:700;line-height:1.4}}
  .page-arrow{{font-size:.8rem;color:var(--muted);margin-top:auto}}
  .empty{{display:none;padding:2rem;text-align:center;color:var(--muted);border:1px dashed var(--border);border-radius:18px;background:rgba(255,255,255,.03)}}
  footer{{text-align:center;color:var(--muted);font-size:.85rem;margin-top:2rem;padding-top:2rem;border-top:1px solid var(--border)}}
  footer a{{color:#fff}}
  @media (max-width: 720px) {{
    nav {{padding:1rem}}
    .search-shell {{border-radius:20px;flex-direction:column}}
    .search-shell button {{width:100%}}
    .results {{width:100%;margin-left:0}}
    .pages-grid {{grid-template-columns:1fr}}
  }}
</style>
{"<script async src=\"https://www.googletagmanager.com/gtag/js?id=" + ga_id + "\"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','" + ga_id + "');</script>" if ga_id else ""}
</head>
<body>
<nav>
  <a href="{domain}">SaaSpare</a>
  <a href="{domain}/pages/">All Comparisons</a>
  <a href="{domain}/pages/saas-roi-calculator.html">ROI Calculator</a>
  <a href="{domain}/shortlist.html">Shortlist Builder</a>
  <a href="{domain}/about.html">About</a>
  <a href="{domain}/shortlist.html">Build Shortlist -></a>
</nav>
<div class="hero">
  <h1>All SaaS Comparisons & Guides</h1>
  <p>{total} pages covering pricing, comparisons, reviews and alternatives.</p>
  <div class="search-shell">
    <input id="page-search" type="text" placeholder="Search any tool, brand, or page type">
    <button type="button" id="search-button">Search</button>
  </div>
  <div class="stats">
    <div class="stat">{len(grouped['comparison'])} comparisons</div>
    <div class="stat">{len(grouped['pricing'])} pricing guides</div>
    <div class="stat">{len(grouped['review'])} reviews</div>
    <div class="stat">Updated {today}</div>
  </div>
</div>
<div class="container">
  <div class="filter-row">
{filter_chips}
    <div class="results" id="results-count"></div>
  </div>
  <div class="pages-grid" id="pages-grid">
{page_cards}
  </div>
  <div class="empty" id="empty-state">No pages matched that search. Try a product name like HubSpot, Ahrefs, or ClickUp.</div>
  <footer>
    <p>Last updated: {today} &nbsp;|&nbsp;
    <a href="{domain}/shortlist.html">Shortlist Builder</a> &nbsp;|&nbsp;
    <a href="{domain}/about.html">About</a> &nbsp;|&nbsp;
    <a href="{domain}/privacy.html">Privacy</a></p>
  </footer>
</div>
<script>
  const searchInput = document.getElementById('page-search');
  const resultsCount = document.getElementById('results-count');
  const emptyState = document.getElementById('empty-state');
  const cards = [...document.querySelectorAll('.page-card')];
  const chips = [...document.querySelectorAll('.filter-chip')];
  let activeType = 'all';

  function applyFilters() {{
    const query = searchInput.value.toLowerCase().trim();
    let visible = 0;
    for (const card of cards) {{
      const matchesType = activeType === 'all' || card.dataset.type === activeType;
      const matchesQuery = !query || card.dataset.title.includes(query) || card.dataset.type.includes(query);
      const show = matchesType && matchesQuery;
      card.classList.toggle('hidden', !show);
      if (show) visible += 1;
    }}
    resultsCount.textContent = visible ? `${{visible}} results` : '0 results';
    emptyState.style.display = visible ? 'none' : 'block';

    const params = new URLSearchParams(window.location.search);
    if (query) params.set('q', query); else params.delete('q');
    if (activeType && activeType !== 'all') params.set('type', activeType); else params.delete('type');
    history.replaceState(null, '', `${{window.location.pathname}}?${{params.toString()}}`);
  }}

  for (const chip of chips) {{
    chip.addEventListener('click', () => {{
      chips.forEach((item) => item.classList.remove('active'));
      chip.classList.add('active');
      activeType = chip.dataset.type;
      applyFilters();
    }});
  }}
  searchInput.addEventListener('input', applyFilters);
  document.getElementById('search-button').addEventListener('click', applyFilters);

  const params = new URLSearchParams(window.location.search);
  const initialQuery = params.get('q');
  const initialType = params.get('type');
  if (initialQuery) searchInput.value = initialQuery;
  if (initialType && chips.some((chip) => chip.dataset.type === initialType)) {{
    activeType = initialType;
    chips.forEach((chip) => chip.classList.toggle('active', chip.dataset.type === initialType));
  }}
  applyFilters();
</script>
<script defer src="/assets/saaspare-ui.js"></script>
</body>
</html>
"""
    out = pages_dir / "index.html"
    out.write_text(html, encoding="utf-8")
    log.info(f"Pages index rebuilt: {total} pages across {sum(1 for v in grouped.values() if v)} groups -> {out}")


def _ping_indexnow(site_repo: Path):
    domain = get("SITE_DOMAIN", "https://saaspare.org")
    key = get("INDEXNOW_KEY", "")
    if not key:
        log.debug("INDEXNOW_KEY not set — skipping IndexNow ping")
        return
    pages_dir = site_repo / "pages"
    pages = [f"{domain}/pages/{p.stem}" for p in pages_dir.glob("*.html")] if pages_dir.exists() else []
    if not pages:
        return
    try:
        resp = httpx.post("https://api.indexnow.org/IndexNow", json={
            "host": domain.replace("https://", "").replace("http://", ""),
            "key": key,
            "keyLocation": f"{domain}/{key}.txt",
            "urlList": pages[:500],
        }, timeout=15)
        log.info(f"IndexNow: submitted {len(pages)} URLs — status {resp.status_code}")
    except Exception as e:
        log.warning(f"IndexNow ping failed: {e}")
