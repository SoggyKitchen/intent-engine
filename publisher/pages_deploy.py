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

        for html_file in PAGES_DIR.glob("*.html"):
            dest = site_repo / html_file.name
            dest.write_text(html_file.read_text(encoding="utf-8"), encoding="utf-8")

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


def _rebuild_sitemap(site_repo: Path):
    pages = list(site_repo.glob("*.html"))
    domain = get("SITE_DOMAIN", "https://yourdomain.com")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in pages:
        if p.name == "index.html":
            continue
        slug = p.stem
        lines.append(f"  <url><loc>{domain}/{slug}</loc><lastmod>{time.strftime('%Y-%m-%d')}</lastmod></url>")
    lines.append("</urlset>")
    (site_repo / "sitemap.xml").write_text("\n".join(lines))


def _ping_indexnow(site_repo: Path):
    domain = get("SITE_DOMAIN", "https://yourdomain.com")
    key = get("INDEXNOW_KEY", "")
    if not key:
        return
    pages = [f"{domain}/{p.stem}" for p in site_repo.glob("*.html") if p.name != "index.html"]
    if not pages:
        return
    try:
        httpx.post("https://api.indexnow.org/IndexNow", json={
            "host": domain.replace("https://", ""),
            "key": key,
            "urlList": pages[:100],
        }, timeout=15)
        log.info(f"IndexNow pinged {len(pages)} URLs")
    except Exception as e:
        log.warning(f"IndexNow ping failed: {e}")
