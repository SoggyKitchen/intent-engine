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
