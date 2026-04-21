import os
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
    _rebuild_sitemap(SITE_DIR)
    _rebuild_homepage(SITE_DIR)
    _rebuild_pages_index(SITE_DIR)
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
_PAGES_EXCLUDE = {"thanks", "verification"}

def _page_label(stem: str) -> str:
    import re as _re
    label = stem.replace("-", " ").title()
    label = _re.sub(r'\s+Pricing\s+\d{4}.*$', ' Pricing', label)
    label = _re.sub(r'\s+\d{4}.*$', '', label)
    label = _re.sub(r'\s+(Plans?|Costs?|What You Actually Pay)\b.*$', '', label, flags=_re.IGNORECASE)
    return label.strip()

def _rebuild_homepage(site_dir: Path):
    index_path = site_dir / "index.html"
    if not index_path.exists():
        return
    pages_dir = site_dir / "pages"
    pages = [p for p in sorted(pages_dir.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)
             if p.stem not in _PAGES_EXCLUDE] if pages_dir.exists() else []
    domain = get("SITE_DOMAIN", "https://saaspare.org")
    pills = "\n".join(
        f'    <a class="tool-pill" href="{domain}/pages/{p.stem}">{_page_label(p.stem)}</a>'
        for p in pages[:24]
    )
    html = index_path.read_text(encoding="utf-8")
    import re
    html = re.sub(
        r'(<div class="tools-grid"[^>]*>)(.*?)(</div>)',
        lambda m: m.group(1) + "\n" + pills + "\n  " + m.group(3),
        html, count=1, flags=re.DOTALL
    )
    index_path.write_text(html, encoding="utf-8")
    log.info(f"Homepage updated with {len(pages[:24])} page links")

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
    import re as _re
    pages_dir = site_dir if site_dir.name == "pages" else site_dir / "pages"
    if not pages_dir.exists():
        log.warning("_rebuild_pages_index: pages dir not found")
        return

    TYPE_ORDER = ["vs", "pricing", "alternatives", "review", "coupon", "free", "best"]
    TYPE_LABELS = {
        "vs": "Comparisons",
        "pricing": "Pricing Guides",
        "alternatives": "Alternatives",
        "review": "Reviews",
        "coupon": "Coupon & Promo Codes",
        "free": "Free Plan Guides",
        "best": "Best-Of Lists",
        "other": "Other Pages",
    }

    def _detect_type(stem: str) -> str:
        s = stem.lower()
        if "-vs-" in s:
            return "vs"
        if "pricing" in s or "-cost" in s:
            return "pricing"
        if "alternatives" in s or "alternative" in s:
            return "alternatives"
        if "review" in s:
            return "review"
        if "coupon" in s or "promo" in s or "discount" in s:
            return "coupon"
        if "free-plan" in s or "free-tier" in s or "does-" in s:
            return "free"
        if s.startswith("best-"):
            return "best"
        return "other"

    grouped: dict[str, list[tuple[str, str]]] = {t: [] for t in TYPE_ORDER + ["other"]}
    domain = get("SITE_DOMAIN", "https://saaspare.org")

    for f in sorted(pages_dir.glob("*.html"), key=lambda p: p.stem):
        if f.stem in _PAGES_EXCLUDE:
            continue
        ptype = _detect_type(f.stem)
        label = _page_label(f.stem)
        url = f"{domain}/pages/{f.stem}"
        grouped[ptype].append((label, url))

    total = sum(len(v) for v in grouped.values())

    sections_html = ""
    for ptype in TYPE_ORDER + ["other"]:
        pages = grouped.get(ptype, [])
        if not pages:
            continue
        heading = TYPE_LABELS.get(ptype, ptype.title())
        items = "\n".join(
            f'          <li><a href="{url}">{label}</a></li>'
            for label, url in pages
        )
        sections_html += f"""
      <section class="page-group">
        <h2>{heading} <span class="count">({len(pages)})</span></h2>
        <ul>
{items}
        </ul>
      </section>"""

    today = time.strftime("%B %d, %Y")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>All SaaS Comparisons & Guides | SaaSpare</title>
<meta name="description" content="Browse {total} B2B SaaS comparison pages, pricing guides, reviews and alternatives — all free.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{domain}/pages/">
<style>
  :root{{--primary:#1a1a2e;--accent:#e94560;--bg:#f8f9fa;--text:#333}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);line-height:1.6}}
  nav{{background:var(--primary);padding:.7rem 1rem;display:flex;align-items:center;gap:1.5rem}}
  nav a{{color:#ccc;text-decoration:none;font-size:.9rem}}
  nav a:first-child{{color:#fff;font-weight:700;font-size:1.1rem;margin-right:auto}}
  nav a:hover{{color:#fff}}
  .hero{{background:var(--primary);color:#fff;padding:3rem 1rem;text-align:center}}
  .hero h1{{font-size:2rem;margin-bottom:.5rem}}
  .hero p{{color:#aaa;font-size:1.1rem}}
  .container{{max-width:960px;margin:0 auto;padding:2rem 1rem}}
  .page-group{{background:#fff;border-radius:8px;padding:1.5rem 2rem;margin:1.5rem 0;box-shadow:0 1px 4px rgba(0,0,0,.08)}}
  .page-group h2{{color:var(--primary);font-size:1.25rem;margin-bottom:1rem;border-bottom:2px solid var(--accent);padding-bottom:.4rem;display:flex;align-items:center;gap:.5rem}}
  .count{{font-size:.85rem;font-weight:400;color:#888}}
  .page-group ul{{list-style:none;display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:.4rem}}
  .page-group li a{{display:block;padding:.35rem .6rem;border-radius:4px;text-decoration:none;color:#333;font-size:.9rem;transition:background .15s}}
  .page-group li a:hover{{background:#f0f0f0;color:var(--accent)}}
  footer{{text-align:center;color:#999;font-size:.85rem;margin-top:3rem;padding-top:2rem;border-top:1px solid #eee}}
  footer a{{color:#aaa;text-decoration:none}}
</style>
</head>
<body>
<nav>
  <a href="{domain}">SaaSpare</a>
  <a href="{domain}/pages/">All Comparisons</a>
  <a href="{domain}/about.html">About</a>
</nav>
<div class="hero">
  <h1>All SaaS Comparisons & Guides</h1>
  <p>{total} pages covering pricing, comparisons, reviews and alternatives</p>
</div>
<div class="container">
{sections_html}
  <footer>
    <p>Last updated: {today} &nbsp;·&nbsp;
    <a href="{domain}/about.html">About</a> &nbsp;·&nbsp;
    <a href="{domain}/privacy.html">Privacy</a></p>
  </footer>
</div>
</body>
</html>
"""
    out = pages_dir / "index.html"
    out.write_text(html, encoding="utf-8")
    log.info(f"Pages index rebuilt: {total} pages across {sum(1 for v in grouped.values() if v)} categories -> {out}")


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
