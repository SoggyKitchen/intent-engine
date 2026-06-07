import os
import re
import subprocess
import time
from html import escape
from pathlib import Path

import httpx

from core.db import db
from core.logger import log
from core.secrets import DRY_RUN, get
from publisher.seo_tags import get_seo_tags

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
_SITEMAP_EXCLUDE_PREFIXES = ("ph-preview-",)

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
        html = _inject_once(
            html,
            "anrdoezrs.net/am/101733230/include/allCj/impressions/page/am.js",
            '<script src="https://www.anrdoezrs.net/am/101733230/include/allCj/impressions/page/am.js"></script>\n',
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
        ("Buyer pages live", page_count),
        ("SaaS categories", category_count),
        ("Offer paths tracked", _count_offer_paths(site_dir)),
    ]
    for label, count in replacements:
        html = re.sub(
            rf'(<span class="stat-val"[^>]*data-count=")\d+("[^>]*>)(?:\d+)(</span><span class="stat-label">{re.escape(label)}</span>)',
            lambda m: f"{m.group(1)}{count}{m.group(2)}{count}{m.group(3)}",
            html,
        )
    newsletter_form_action = get(
        "NEWSLETTER_FORM_ACTION",
        "https://formsubmit.co/hello@saaspare.org",
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
        r"(\.length\|\|)\d+(;)",
        lambda m: f"{m.group(1)}{page_count}{m.group(2)}",
        html,
        count=1,
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


def _count_offer_paths(site_dir: Path) -> int:
    redirects = site_dir / "_redirects"
    if not redirects.exists():
        return 0
    try:
        return sum(
            1
            for line in redirects.read_text(encoding="utf-8", errors="ignore").splitlines()
            if line.strip().startswith("/go/")
        )
    except Exception:
        return 0

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
        if p.stem not in _SITEMAP_EXCLUDE and not p.stem.startswith(_SITEMAP_EXCLUDE_PREFIXES):
            lines.append(f'  <url><loc>{domain}/{p.stem}</loc><lastmod>{today}</lastmod><priority>0.7</priority></url>')
    if (pages_dir / "index.html").exists():
        lines.append(f'  <url><loc>{domain}/pages</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>')
    for p in sorted(pages):
        if p.stem not in _SITEMAP_EXCLUDE and not p.stem.startswith(_SITEMAP_EXCLUDE_PREFIXES):
            slug = p.stem
            if any(k in slug for k in ("coupon-code", "promo-code", "pricing-2026")):
                pri = "0.9"
            elif any(k in slug for k in ("-review-", "free-trial", "free-plan", "alternatives")):
                pri = "0.85"
            else:
                pri = "0.8"
            lines.append(f'  <url><loc>{domain}/pages/{slug}</loc><lastmod>{today}</lastmod><priority>{pri}</priority></url>')
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
    # Category filter chips (label-only, matching the SaaSpare library design)
    cat_chip_parts = ['    <button class="cat-chip active" data-type="all" type="button">All</button>']
    cat_chip_parts.extend(
        f'    <button class="cat-chip" data-type="{key}" type="button">{TYPE_LABELS[key]}</button>'
        for key in TYPE_ORDER
        if grouped[key]
    )
    cat_chips = "\n".join(cat_chip_parts)

    # Real brand logos via Simple Icons CDN, with deterministic monogram fallback
    # (graceful onerror swap — never fabricates a logo, just falls back to the
    # same monogram avatar style used before if the brand isn't on Simple Icons)
    _palette = ["#e94560", "#3460e6", "#7b68ee", "#0e7490", "#16a34a", "#d97706",
                "#0070ad", "#c2410c", "#9333ea", "#0891b2", "#be123c", "#1d4ed8"]

    # Known slug overrides where the tool's URL-stem name doesn't match its
    # Simple Icons slug (verified against simpleicons.org)
    _SLUG_MAP = {
        "1password-business": "1password", "1password": "1password",
        "monday-com": "monday", "monday": "monday",
        "surfer-seo": "surferseo", "surfer": "surferseo",
        "duo-security": "duo", "duo": "duo",
        "sentinel-one": "sentinelone", "sentinelone": "sentinelone",
        "post-affiliate-pro": "postaffiliatepro",
        "google-ads": "googleads", "google-analytics": "googleanalytics",
        "microsoft-teams": "microsoftteams", "microsoft-365": "microsoft365",
        "adobe-acrobat": "adobeacrobat", "adobe-photoshop": "adobephotoshop",
        "salesforce": "salesforce", "hubspot": "hubspot", "zoho": "zoho",
        "activecampaign": "activecampaign", "mailchimp": "mailchimp",
        "semrush": "semrush", "ahrefs": "ahrefs", "moz": "moz",
        "clickup": "clickup", "asana": "asana", "notion": "notion",
        "trello": "trello", "monday-com-work-os": "monday",
        "shopify": "shopify", "bigcommerce": "bigcommerce", "wix": "wix",
        "squarespace": "squarespace", "webflow": "webflow",
        "slack": "slack", "zoom": "zoom", "loom": "loom",
        "figma": "figma", "canva": "canva", "airtable": "airtable",
        "zendesk": "zendesk", "intercom": "intercom", "freshdesk": "freshdesk",
        "stripe": "stripe", "paypal": "paypal", "quickbooks": "quickbooks",
        "freshbooks": "freshbooks", "xero": "xero", "wave": "wave",
        "nordvpn": "nordvpn", "surfshark": "surfshark", "expressvpn": "expressvpn",
        "bitwarden": "bitwarden", "dashlane": "dashlane", "lastpass": "lastpass",
        "okta": "okta", "auth0": "auth0", "onelogin": "onelogin",
        "cloudflare": "cloudflare", "contabo": "contabo",
        "google-workspace": "googleworkspace", "dropbox": "dropbox",
        "docusign": "docusign", "calendly": "calendly", "typeform": "typeform",
        "convertkit": "convertkit", "getresponse": "getresponse",
        "constant-contact": "constantcontact", "brevo": "brevo",
        "pipedrive": "pipedrive", "keap": "keap", "close": "close",
        "gusto": "gusto", "rippling": "rippling", "deel": "deel", "remote": "remote",
        "ramp": "ramp", "brex": "brex", "divvy": "divvy",
        "grammarly": "grammarly", "jasper": "jasper", "copy-ai": "copyai",
        "wordpress": "wordpress", "ghost": "ghost",
    }

    def _mono(seed: str) -> str:
        s = re.sub(r'[^a-z0-9]', '', seed.lower())
        return (s[:2].upper() or "SP")

    def _to_slug(name: str) -> str:
        key = name.lower().strip('-')
        if key in _SLUG_MAP:
            return _SLUG_MAP[key]
        return re.sub(r'[^a-z0-9]', '', key) or "sp"

    def _logo_chip(seed: str) -> str:
        """Real brand logo (Simple Icons CDN) with monogram-avatar fallback on error."""
        color = _palette[sum(ord(c) for c in seed) % len(_palette)] if seed else _palette[0]
        slug = _to_slug(seed)
        letter = _mono(seed)
        return (
            f'<span class="sp-logo lib-logo" style="background:{color}">'
            f'<img src="https://cdn.simpleicons.org/{slug}/ffffff" loading="lazy" alt="" '
            f'onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'inline\'">'
            f'<em style="display:none">{letter}</em></span>'
        )

    def _split_stem(stem: str) -> tuple[str, str | None]:
        """Strip the trailing '-which-is-better-in-2026' suffix and split on '-vs-'."""
        s = re.sub(r'-which-is-better-in-\d{4}$', '', stem)
        if '-vs-' in s:
            a, b = s.split('-vs-', 1)
            return a, b
        return s, None

    def _row_logos(stem: str) -> str:
        a, b = _split_stem(stem)
        if b is not None:
            return _logo_chip(a or stem) + _logo_chip(b or 'x')
        return _logo_chip(a or 'sp')

    def _row(label: str, url: str, ptype: str) -> str:
        stem = url.rsplit('/', 1)[-1]
        return (
            f'        <a href="{url}" class="lib-row premium-card" data-type="{ptype}" data-title="{escape(label.lower(), quote=True)}">'
            f'<div class="lib-row-logos">{_row_logos(stem)}</div>'
            f'<div><div class="lib-row-title">{escape(label, quote=False)}</div>'
            f'<div class="lib-row-meta"><span class="sp-badge sp-badge-ghost">{TYPE_LABELS[ptype]}</span></div></div>'
            f'<div class="lib-row-arrow"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M13 6l6 6-6 6"/></svg></div>'
            f'</a>'
        )

    lib_rows = "\n".join(
        _row(label, url, ptype)
        for ptype in TYPE_ORDER
        for label, url in grouped[ptype]
    )

    # "Popular right now" — real comparison pages (fallback to pricing)
    popular = (grouped['comparison'][:4] or grouped['pricing'][:4])
    pop_chips = "\n".join(
        f'        <a class="cat-chip" href="{url}">{escape(label, quote=False)}</a>'
        for label, url in popular
    )

    today = time.strftime("%B %d, %Y")
    seo = get_seo_tags(
        "/pages/",
        fallback_title=f"Compare {total} SaaS Tools | SaaSpare",
        fallback_meta=(
            f"Compare {total}+ SaaS products with real pricing data. Find unbiased "
            "reviews, alternatives, free trials, promo codes and buying guides."
        ),
    )
    seo_title = escape(seo["title"], quote=False)
    seo_meta = escape(seo["meta_description"], quote=True)
    seo_keywords = escape(
        "SaaS comparisons, SaaS pricing, software reviews, free trials, promo codes, alternatives, SaaSpare",
        quote=True,
    )
    # Sidebar buyer-intent quick filters → map each to a real page type we actually have.
    intent_rail = [
        ("comparison", "Compare top tools", "Side-by-side verdicts", '<path d="M3 12h18M3 6h18M3 18h18"/>'),
        ("pricing", "Find best value", "Real pricing &amp; lowest cost", '<path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'),
        ("free-trial", "Free trial available", "Try before you buy", '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>'),
        ("promo", "Coupons &amp; deals", "Verified working discounts", '<path d="M4 7h16v5H4z"/><path d="M12 22V7M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"/>'),
        ("best-of", "Best-of shortlists", "Top picks by use case", '<path d="M12 2l2.4 7.4H22l-6 4.6 2.3 7.4L12 17l-6.3 4.4L8 14 2 9.4h7.6z"/>'),
    ]
    intent_items = "\n".join(
        f'          <div class="intent-item" data-filter="{key}"><span class="sp-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">{svg}</svg></span>'
        f'<div><strong>{t}</strong><span>{s}</span></div></div>'
        for key, t, s, svg in intent_rail
        if grouped.get(key)
    )

    if ga_id:
        ga_snippet = (
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>'
            "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
            f"gtag('js',new Date());gtag('config','{ga_id}');</script>"
        )
    else:
        ga_snippet = ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{seo_title}</title>
<meta name="description" content="{seo_meta}">
<meta name="keywords" content="{seo_keywords}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{domain}/pages/">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta name="theme-color" content="#07070d">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
<noscript><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"></noscript>
<link rel="stylesheet" href="/assets/sp-shared.css">
<link rel="stylesheet" href="/assets/sp-motion.css">
<link rel="stylesheet" href="/assets/saaspare-ui.css">
<meta property="og:title" content="{escape(seo['title'], quote=True)}">
<meta property="og:description" content="{seo_meta}">
<meta property="og:type" content="website">
<meta property="og:url" content="{domain}/pages/">
<meta property="og:image" content="{domain}/og-default.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@SaaSpare">
<meta name="twitter:title" content="{escape(seo['title'], quote=True)}">
<meta name="twitter:description" content="{seo_meta}">
<meta name="twitter:image" content="{domain}/og-default.png">
<style>
  /* SaaSpare library — layered on sp-shared.css design system */
  .lib-hero{{text-align:center;padding:6.5rem 1.5rem 1.5rem;display:flex;flex-direction:column;align-items:center;gap:1.4rem;position:relative;isolation:isolate;overflow:hidden}}
  .lib-hero > *{{position:relative;z-index:2}}
  .lib-hero > .bg-orb,.lib-hero > .lib-hero-grid{{position:absolute!important;z-index:0}}
  .lib-hero-grid{{position:absolute;inset:-10% -5%;z-index:0;opacity:.35;pointer-events:none;
    background-image:linear-gradient(rgba(255,65,109,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(255,65,109,.07) 1px,transparent 1px);
    background-size:64px 64px;mask-image:radial-gradient(ellipse 60% 70% at 50% 30%,#000 30%,transparent 75%)}}
  .lib-hero h1{{font-size:clamp(2.4rem,5.5vw,3.6rem)}}
  .lib-stats{{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:.4rem}}
  .lib-stat{{display:inline-flex;align-items:baseline;gap:7px;padding:10px 20px;background:rgba(255,255,255,.045);border:1px solid var(--line);border-radius:var(--r-full);transition:all .25s cubic-bezier(.34,1.56,.64,1);backdrop-filter:blur(12px)}}
  .lib-stat:hover{{transform:translateY(-3px);border-color:var(--line-pink);box-shadow:0 12px 32px rgba(255,65,109,.18);background:rgba(255,65,109,.06)}}
  .lib-stat strong{{background:linear-gradient(135deg,var(--pink),var(--pink-light));-webkit-background-clip:text;background-clip:text;color:transparent;font-size:1.2rem;font-weight:900;letter-spacing:-.03em}}
  .lib-stat span{{font-size:.78rem;color:var(--ink-4);font-weight:600}}
  .lib-search{{display:flex;align-items:center;gap:8px;width:100%;max-width:620px;padding:6px 6px 6px 20px;background:rgba(255,255,255,.05);border:1px solid var(--line);border-radius:var(--r-full);backdrop-filter:blur(20px);box-shadow:0 30px 80px rgba(0,0,0,.5)}}
  .lib-search > svg{{color:var(--ink-4);flex-shrink:0}}
  .lib-search input{{flex:1;background:none;border:none;outline:none;padding:.9rem 0;font-size:.95rem;color:var(--ink)}}
  .lib-search input::placeholder{{color:var(--ink-5)}}
  .pop-now{{margin:2.5rem 0 1rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}}
  .pop-now strong{{color:var(--ink);font-weight:700;font-size:.95rem;letter-spacing:-.01em}}
  .pop-now span{{color:var(--ink-4);font-size:.82rem;margin-left:8px}}
  .pop-row{{display:flex;gap:8px;flex-wrap:wrap}}
  .lib-toolbar{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:1.5rem 0}}
  .lib-toolbar .sp-select{{min-width:160px;padding:.65rem 38px .65rem 14px;font-size:.85rem;border-radius:var(--r-md)}}
  .cat-chip{{padding:6px 14px;border-radius:var(--r-full);background:rgba(255,255,255,.05);border:1px solid var(--line);color:var(--ink-3);font-size:.82rem;font-weight:600;cursor:pointer;transition:all .15s;white-space:nowrap;font-family:inherit}}
  .cat-chip:hover{{color:var(--ink)}}
  .cat-chip.active{{background:linear-gradient(135deg,rgba(255,65,109,.22),rgba(201,41,80,.18));border-color:var(--line-pink);color:var(--ink)}}
  .results{{margin-left:auto;color:var(--ink-4);font-size:.84rem;font-weight:600}}
  .lib-main{{display:grid;grid-template-columns:1.1fr 280px;gap:24px;align-items:start}}
  .lib-list{{display:flex;flex-direction:column;gap:10px}}
  .lib-row{{display:grid;grid-template-columns:auto 1fr auto;gap:18px;align-items:center;padding:16px 20px;background:var(--glass);border:1px solid var(--line);border-radius:var(--r-md);transition:all .2s;text-decoration:none}}
  .lib-row.hidden{{display:none}}
  .lib-row:hover{{border-color:var(--line-pink);transform:translateY(-2px);box-shadow:0 16px 40px rgba(255,65,109,.08)}}
  .lib-row-logos{{display:flex;align-items:center}}
  .lib-row-logos .sp-logo{{width:38px;height:38px;border-radius:11px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:900;font-size:.8rem;letter-spacing:-.02em;border:1px solid rgba(255,255,255,.14);position:relative;transition:transform .25s cubic-bezier(.34,1.56,.64,1),box-shadow .25s}}
  .lib-row-logos .sp-logo:nth-child(2){{margin-left:-12px;z-index:1}}
  .lib-row-logos .sp-logo img{{width:20px;height:20px;object-fit:contain;filter:drop-shadow(0 1px 3px rgba(0,0,0,.35))}}
  .lib-row:hover .lib-row-logos .sp-logo{{transform:translateY(-3px) scale(1.06);box-shadow:0 10px 24px rgba(0,0,0,.4)}}
  .lib-row:hover .lib-row-logos .sp-logo:nth-child(2){{transform:translateY(-3px) translateX(2px) scale(1.06)}}
  .lib-row-title{{font-size:1.02rem;font-weight:700;color:var(--ink);letter-spacing:-.01em;margin-bottom:5px;line-height:1.35}}
  .lib-row-meta{{display:flex;gap:8px;flex-wrap:wrap;align-items:center}}
  .lib-row-arrow{{width:36px;height:36px;border-radius:10px;background:rgba(255,255,255,.05);border:1px solid var(--line);display:flex;align-items:center;justify-content:center;color:var(--ink-3);transition:all .2s}}
  .lib-row:hover .lib-row-arrow{{background:linear-gradient(135deg,var(--pink),var(--pink-deep));color:#fff;border-color:transparent}}
  .lib-side{{position:sticky;top:90px;display:flex;flex-direction:column;gap:16px}}
  .intent-card{{padding:22px;position:relative;overflow:hidden}}
  .intent-card h4{{font-size:.96rem;font-weight:700;color:var(--ink);margin-bottom:14px;letter-spacing:-.01em}}
  .intent-item{{display:flex;align-items:flex-start;gap:14px;padding:12px 10px;margin:0 -10px;border-radius:12px;cursor:pointer;transition:all .22s cubic-bezier(.34,1.56,.64,1)}}
  .intent-item:hover{{background:linear-gradient(135deg,rgba(255,65,109,.1),rgba(201,41,80,.04));transform:translateX(4px)}}
  .intent-item.active{{background:linear-gradient(135deg,rgba(255,65,109,.16),rgba(201,41,80,.06))}}
  .intent-item.active strong{{color:var(--pink-light)}}
  .intent-item .sp-icon{{width:38px;height:38px;border-radius:11px;flex-shrink:0;display:flex;align-items:center;justify-content:center;
    background:linear-gradient(135deg,rgba(255,65,109,.22),rgba(201,41,80,.1));border:1px solid rgba(255,65,109,.18);
    color:var(--pink-light);transition:all .25s cubic-bezier(.34,1.56,.64,1)}}
  .intent-item:hover .sp-icon,.intent-item.active .sp-icon{{transform:scale(1.12) rotate(-6deg);box-shadow:0 8px 22px rgba(255,65,109,.35);
    background:linear-gradient(135deg,var(--pink),var(--pink-deep));color:#fff;border-color:transparent}}
  .intent-item .sp-icon svg{{width:16px;height:16px}}
  .intent-item strong{{display:block;font-size:.88rem;color:var(--ink);font-weight:700;margin-bottom:2px;letter-spacing:-.01em}}
  .intent-item span{{font-size:.76rem;color:var(--ink-4);line-height:1.4}}
  .intent-clear{{display:block;width:100%;margin-top:14px;text-align:center;padding:.6rem;background:rgba(255,255,255,.04);border:none;border-radius:10px;color:var(--ink-3);font-size:.8rem;font-weight:600;cursor:pointer;transition:all .15s;font-family:inherit}}
  .intent-clear:hover{{background:rgba(255,65,109,.08);color:var(--pink-light)}}
  .empty{{display:none;padding:2.5rem 2rem;text-align:center;color:var(--ink-4);border:1px dashed var(--line);border-radius:var(--r-md);background:rgba(255,255,255,.03);margin-top:12px}}
  .lib-pagination{{display:flex;justify-content:center;align-items:center;gap:6px;margin-top:2rem;flex-wrap:wrap}}
  .lib-pg-btn{{min-width:36px;height:36px;padding:0 10px;border-radius:10px;border:1px solid var(--line);background:rgba(255,255,255,.04);color:var(--ink-3);font-size:.85rem;font-weight:600;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all .15s;font-family:inherit}}
  .lib-pg-btn:hover:not(:disabled){{color:var(--ink);border-color:var(--line-pink)}}
  .lib-pg-btn:disabled{{opacity:.35;cursor:default}}
  .lib-pg-btn.active{{background:linear-gradient(135deg,var(--pink),var(--pink-deep));color:#fff;border-color:transparent}}
  @media (max-width:900px){{.lib-main{{grid-template-columns:1fr}}.lib-side{{position:static}}}}
  @media (max-width:600px){{.lib-row{{grid-template-columns:auto 1fr;gap:12px}}.lib-row-arrow{{display:none}}.lib-hero{{padding-top:3.5rem}}}}
</style>
{ga_snippet}
</head>
<body>
<div class="sp-bg"></div>
<nav class="sp-nav">
  <a href="/" class="sp-nav-logo"><span class="sp-nav-logo-mark">S</span>Saa<em>Spare</em></a>
  <a href="/pages/" class="sp-nav-link active">Comparisons</a>
  <a href="/pages/saas-roi-calculator" class="sp-nav-link">ROI Calculator</a>
  <a href="/shortlist" class="sp-nav-link">Shortlist Builder</a>
  <a href="/deal-radar" class="sp-nav-link">Deal Radar</a>
  <a href="/about" class="sp-nav-link">About</a>
  <a href="/shortlist" class="sp-btn sp-btn-primary sp-btn-sm glint-button" style="margin-left:8px">Build Shortlist &#8594;</a>
</nav>

<section class="lib-hero">
  <div class="lib-hero-grid" aria-hidden="true"></div>
  <span class="bg-orb bg-orb-pink" style="width:420px;height:420px;top:-180px;left:-120px" aria-hidden="true"></span>
  <span class="bg-orb bg-orb-wine" style="width:340px;height:340px;top:-80px;right:-110px" aria-hidden="true"></span>
  <span class="sp-eyebrow sp-up"><span class="sp-eyebrow-dot"></span>Browse all comparisons</span>
  <h1 class="sp-h1 sp-up sp-up-1" style="max-width:880px">Find the right <span class="sp-accent">SaaS answer</span> faster.</h1>
  <p class="sp-lead sp-up sp-up-2" style="max-width:580px">Search pricing pages, comparison verdicts, trial paths, and alternatives without opening ten vendor tabs.</p>
  <div class="sp-up sp-up-3" style="width:100%;max-width:640px;display:flex;flex-direction:column;align-items:center;gap:10px">
    <form class="lib-search search-glow" onsubmit="event.preventDefault()" style="width:100%">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
      <input id="page-search" type="text" placeholder="Search tools, use cases, categories…">
      <button type="button" id="search-button" class="sp-btn sp-btn-primary glint-button">Search</button>
    </form>
  </div>
  <div class="lib-stats sp-up sp-up-4">
    <div class="lib-stat"><strong>{len(grouped['comparison'])}</strong><span>Comparisons</span></div>
    <div class="lib-stat"><strong>{len(grouped['pricing'])}</strong><span>Pricing Guides</span></div>
    <div class="lib-stat"><strong>{len(grouped['review'])}</strong><span>Reviews</span></div>
    <div class="lib-stat"><strong>{total}</strong><span>Buyer Pages Indexed</span></div>
  </div>
  <p style="font-size:.8rem;color:var(--ink-5);margin-top:2px">By <a href="/authors/smith-elly" style="color:var(--ink-4);font-weight:600">Smith Elly</a> &middot; Updated {today} &middot; <a href="/methodology" style="color:var(--ink-4)">Methodology</a></p>
</section>

<section class="sp-section" style="padding-top:1rem;padding-bottom:1rem">
  <div class="sp-container">
    <div class="pop-now">
      <div><strong>Popular right now</strong><span>&middot; updated hourly</span></div>
      <div class="pop-row">
{pop_chips}
      </div>
    </div>
  </div>
</section>

<section class="sp-section" style="padding-top:1rem">
  <div class="sp-container">
    <div class="lib-toolbar">
{cat_chips}
      <select class="sp-input sp-select" id="sort-select" style="margin-left:auto;width:auto" aria-label="Sort pages">
        <option value="recommended">Sort: Recommended</option>
        <option value="az">Sort: A &#8594; Z</option>
        <option value="popular">Sort: Most useful</option>
      </select>
      <div class="results" id="results-count"></div>
    </div>

    <div class="lib-main">
      <div class="lib-list stagger">
        <div id="pages-grid">
{lib_rows}
        </div>
        <div class="empty" id="empty-state">No pages matched that search. Try a product name like HubSpot, Ahrefs, or ClickUp.</div>
        <div class="lib-pagination" id="pagination"></div>
      </div>

      <aside class="lib-side">
        <div class="sp-glass intent-card">
          <h4>Buyer intent filters</h4>
{intent_items}
          <button type="button" class="intent-clear" id="intent-clear">Clear all filters</button>
        </div>
        <div class="sp-glass-pink intent-card">
          <h4 style="margin-bottom:8px">Need help deciding?</h4>
          <p class="sp-small" style="margin-bottom:14px;color:var(--ink-3)">Use Shortlist Builder to compare your top picks side-by-side.</p>
          <a href="/shortlist" class="sp-btn sp-btn-primary sp-btn-sm glint-button" style="width:100%">Open Shortlist Builder &#8594;</a>
        </div>
      </aside>
    </div>
  </div>
</section>

<footer class="sp-footer">
  <div class="sp-footer-inner">
    <div class="sp-footer-brand">
      <div class="sp-nav-logo"><span class="sp-nav-logo-mark">S</span>Saa<em>Spare</em></div>
      <p>The honest guide to SaaS. Independent research, weekly pricing verification, no paid rankings.</p>
    </div>
    <div class="sp-footer-col"><h4>Product</h4>
      <a href="/pages/">Comparisons</a><a href="/shortlist">Shortlist Builder</a><a href="/pages/saas-roi-calculator">ROI Calculator</a><a href="/deal-radar">Deal Radar</a>
    </div>
    <div class="sp-footer-col"><h4>Company</h4>
      <a href="/about">About</a><a href="/methodology">Methodology</a><a href="/contact">Contact</a>
    </div>
    <div class="sp-footer-col"><h4>Legal</h4>
      <a href="/affiliate-disclosure">Affiliate Disclosure</a><a href="/privacy">Privacy</a>
    </div>
  </div>
  <div class="sp-footer-bottom">
    <span>&copy; 2026 SaaSpare. All rights reserved.</span>
    <span>Made for buyers. Not vendors. &middot; Updated {today}</span>
  </div>
</footer>

<script>
  const PAGE_SIZE = 24;
  const searchInput = document.getElementById('page-search');
  const resultsCount = document.getElementById('results-count');
  const emptyState = document.getElementById('empty-state');
  const grid = document.getElementById('pages-grid');
  const pager = document.getElementById('pagination');
  const cards = [...document.querySelectorAll('.lib-row')];
  const chips = [...document.querySelectorAll('.cat-chip[data-type]')];
  const intents = [...document.querySelectorAll('.intent-item')];
  const sortSelect = document.getElementById('sort-select');
  let activeType = 'all';
  let currentPage = 1;
  const weight = {{'pricing':1,'free-trial':2,'promo':3,'comparison':4,'alternatives':5,'review':6,'best-of':7,'guide':8}};

  function matched() {{
    const q = searchInput.value.toLowerCase().trim();
    return cards.filter((c) => (activeType === 'all' || c.dataset.type === activeType) && (!q || c.dataset.title.includes(q) || c.dataset.type.includes(q)));
  }}
  function sortList(list) {{
    const mode = sortSelect ? sortSelect.value : 'recommended';
    return list.sort((a,b) => {{
      if(mode === 'az') return a.dataset.title.localeCompare(b.dataset.title);
      if(mode === 'popular') return (weight[a.dataset.type]||99) - (weight[b.dataset.type]||99);
      return (weight[a.dataset.type]||99) - (weight[b.dataset.type]||99) || a.dataset.title.localeCompare(b.dataset.title);
    }});
  }}
  function render() {{
    const list = sortList(matched());
    cards.forEach((c) => c.classList.add('hidden'));
    const pages = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
    if(currentPage > pages) currentPage = pages;
    const start = (currentPage - 1) * PAGE_SIZE;
    list.slice(start, start + PAGE_SIZE).forEach((c) => {{ c.classList.remove('hidden'); grid.appendChild(c); }});
    resultsCount.textContent = list.length ? `${{list.length}} results` : '0 results';
    emptyState.style.display = list.length ? 'none' : 'block';
    renderPager(pages);
    const params = new URLSearchParams(window.location.search);
    const q = searchInput.value.trim();
    if(q) params.set('q', q); else params.delete('q');
    if(activeType !== 'all') params.set('type', activeType); else params.delete('type');
    history.replaceState(null, '', `${{window.location.pathname}}?${{params.toString()}}`);
  }}
  function renderPager(pages) {{
    pager.innerHTML = '';
    if(pages <= 1) return;
    const mk = (label, page, opts) => {{
      opts = opts || {{}};
      const b = document.createElement('button');
      b.className = 'lib-pg-btn' + (opts.active ? ' active' : '');
      b.textContent = label;
      if(opts.disabled) b.disabled = true;
      if(!opts.disabled && !opts.active) b.onclick = () => {{ currentPage = page; render(); window.scrollTo({{top:0,behavior:'smooth'}}); }};
      return b;
    }};
    pager.appendChild(mk('‹', currentPage - 1, {{disabled: currentPage === 1}}));
    const win = [];
    [1, 2, pages - 1, pages, currentPage - 1, currentPage, currentPage + 1].forEach((p) => {{ if(p >= 1 && p <= pages && !win.includes(p)) win.push(p); }});
    win.sort((a,b) => a - b);
    let prev = 0;
    win.forEach((p) => {{
      if(p - prev > 1) {{ const s = document.createElement('span'); s.className = 'lib-pg-btn'; s.style.border = 'none'; s.style.background = 'none'; s.textContent = '…'; pager.appendChild(s); }}
      pager.appendChild(mk(String(p), p, {{active: p === currentPage}}));
      prev = p;
    }});
    pager.appendChild(mk('›', currentPage + 1, {{disabled: currentPage === pages}}));
  }}
  function setType(t) {{
    activeType = t; currentPage = 1;
    chips.forEach((c) => c.classList.toggle('active', c.dataset.type === t));
    intents.forEach((i) => i.classList.toggle('active', i.dataset.filter === t));
    render();
  }}
  chips.forEach((c) => c.addEventListener('click', () => setType(c.dataset.type)));
  intents.forEach((i) => i.addEventListener('click', () => {{ setType(i.dataset.filter); const tb = document.querySelector('.lib-toolbar'); if(tb) window.scrollTo({{top: tb.offsetTop - 80, behavior:'smooth'}}); }}));
  document.getElementById('intent-clear').addEventListener('click', () => {{ searchInput.value = ''; setType('all'); }});
  searchInput.addEventListener('input', () => {{ currentPage = 1; render(); }});
  document.getElementById('search-button').addEventListener('click', () => {{ currentPage = 1; render(); }});
  if(sortSelect) sortSelect.addEventListener('change', () => {{ currentPage = 1; render(); }});
  const params = new URLSearchParams(window.location.search);
  if(params.get('q')) searchInput.value = params.get('q');
  const it = params.get('type');
  if(it && chips.some((c) => c.dataset.type === it)) activeType = it;
  setType(activeType);
</script>
<script defer src="/assets/sp-motion.js"></script>
<script defer src="/assets/saaspare-ui.js"></script>
<script src="https://www.anrdoezrs.net/am/101733230/include/allCj/impressions/page/am.js"></script>
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
