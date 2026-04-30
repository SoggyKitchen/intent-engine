from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from html import escape, unescape
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from publisher.seo_tags import get_seo_tags
except Exception:  # pragma: no cover - script should still report if import is broken.
    get_seo_tags = None

DEFAULT_CONFIG = {
    "siteUrl": "https://saaspare.org",
    "siteDir": "site",
    "reportsDir": "seo/reports",
    "snapshotsDir": "seo/snapshots",
    "ottoImportsDir": "seo/otto-imports",
    "excludePathPatterns": [r"^/ph-preview-\d+$", r"^/pages/(thanks|verification)$"],
    "thresholds": {"thinWords": 800, "titleMin": 30, "titleMax": 70, "metaMin": 90, "metaMax": 170},
}

PAGE_TYPE_PATTERNS = [
    ("comparison", re.compile(r"-vs-|which-is-better", re.I)),
    ("pricing", re.compile(r"pricing|cost", re.I)),
    ("free_trial", re.compile(r"free-trial|free-plan|free-tier", re.I)),
    ("coupon", re.compile(r"coupon|promo|discount|deal", re.I)),
    ("review", re.compile(r"review|verdict", re.I)),
    ("alternatives", re.compile(r"alternatives", re.I)),
    ("best_of", re.compile(r"^best-|/best-", re.I)),
]

SEVERE_ISSUES = {
    "missing_title",
    "missing_meta",
    "invalid_canonical",
    "canonical_homepage_conflict",
    "no_h1",
    "duplicate_h1",
    "invalid_jsonld",
    "broken_internal_link",
}

DEFAULT_OG_IMAGE = "https://saaspare.org/og-default.png"
TWITTER_SITE = "@SaaSpare"
ORG_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "SaaSpare",
    "url": "https://saaspare.org/",
    "logo": DEFAULT_OG_IMAGE,
    "description": "Independent B2B SaaS comparisons, pricing guides, free-trial checks, alternatives, and buyer tools.",
    "sameAs": [],
}


@dataclass
class PageAudit:
    path: str
    file: str
    url: str
    page_type: str
    title: str = ""
    title_length: int = 0
    meta_description: str = ""
    meta_length: int = 0
    canonical: str = ""
    robots: str = ""
    h1: list[str] = field(default_factory=list)
    h2: list[str] = field(default_factory=list)
    word_count: int = 0
    internal_links: list[str] = field(default_factory=list)
    external_links: list[str] = field(default_factory=list)
    affiliate_links: list[str] = field(default_factory=list)
    broken_internal_links: list[str] = field(default_factory=list)
    images: int = 0
    images_missing_alt: int = 0
    jsonld_blocks: int = 0
    schema_types: list[str] = field(default_factory=list)
    has_faq: bool = False
    has_faq_schema: bool = False
    has_pricing_table: bool = False
    has_comparison_table: bool = False
    has_trust_box: bool = False
    has_related_pages: bool = False
    has_affiliate_disclosure: bool = False
    has_methodology: bool = False
    has_correction: bool = False
    has_last_verified: bool = False
    has_pricing_source: bool = False
    has_email_capture: bool = False
    has_cta: bool = False
    has_sticky_cta: bool = False
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    score: dict[str, float] = field(default_factory=dict)


def load_config() -> dict:
    path = ROOT / "seo" / "config.json"
    if not path.exists():
        return DEFAULT_CONFIG.copy()
    config = DEFAULT_CONFIG.copy()
    config.update(json.loads(path.read_text(encoding="utf-8")))
    config["thresholds"] = {**DEFAULT_CONFIG["thresholds"], **config.get("thresholds", {})}
    return config


def ensure_dirs(config: dict) -> None:
    for key in ("reportsDir", "snapshotsDir", "ottoImportsDir"):
        (ROOT / config[key]).mkdir(parents=True, exist_ok=True)
    (ROOT / config["ottoImportsDir"] / "normalized").mkdir(parents=True, exist_ok=True)
    (ROOT / "seo" / "data").mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def normalize_path(value: str) -> str:
    if not value:
        return "/"
    if value.startswith("http://") or value.startswith("https://"):
        value = urlparse(value).path or "/"
    value = value.split("#", 1)[0].split("?", 1)[0]
    if value.endswith("index.html"):
        value = value[: -len("index.html")]
    if value.endswith(".html"):
        value = value[:-5]
    if not value.startswith("/"):
        value = "/" + value
    return value.rstrip("/") or "/"


def file_to_path(file: Path, site_dir: Path) -> str:
    relative = file.relative_to(site_dir).as_posix()
    if relative == "index.html":
        return "/"
    if relative.endswith("/index.html"):
        relative = relative[: -len("/index.html")]
    elif relative.endswith(".html"):
        relative = relative[:-5]
    return "/" + relative


def public_url(site_url: str, path: str) -> str:
    return site_url.rstrip("/") + normalize_path(path)


def classify_page_type(path: str, html: str = "") -> str:
    if path in {"/about", "/contact", "/privacy", "/methodology", "/affiliate-disclosure"}:
        return "trust"
    combined = f"{path} {strip_tags(html[:5000])}"
    for page_type, pattern in PAGE_TYPE_PATTERNS:
        if pattern.search(combined):
            return page_type
    return "other"


def strip_tags(html: str) -> str:
    text = re.sub(r"<script\b.*?</script>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def html_clean(value: str) -> str:
    previous = value
    for _ in range(5):
        current = unescape(previous)
        if current == previous:
            return current
        previous = current
    return previous


def first_match(pattern: str, html: str, flags: int = re.I | re.S) -> str:
    match = re.search(pattern, html, flags)
    return html_clean(re.sub(r"\s+", " ", match.group(1)).strip()) if match else ""


def all_matches(pattern: str, html: str, flags: int = re.I | re.S) -> list[str]:
    return [html_clean(re.sub(r"\s+", " ", m).strip()) for m in re.findall(pattern, html, flags)]


def attr_value(tag: str, attr: str) -> str:
    match = re.search(rf'\b{re.escape(attr)}=["\']([^"\']+)["\']', tag, re.I)
    return html_clean(match.group(1).strip()) if match else ""


def discover_repo(config: dict) -> dict:
    files = {p.name for p in ROOT.iterdir()}
    workflows = sorted(p.name for p in (ROOT / ".github" / "workflows").glob("*.yml")) if (ROOT / ".github" / "workflows").exists() else []
    site_dir = ROOT / config["siteDir"]
    pages_dir = site_dir / "pages"
    routes = sorted(file_to_path(p, site_dir) for p in site_dir.glob("*.html")) if site_dir.exists() else []
    generated_pages = sorted(file_to_path(p, site_dir) for p in pages_dir.glob("*.html")) if pages_dir.exists() else []
    package_manager = "uv" if (ROOT / "uv.lock").exists() else ("npm" if (ROOT / "package-lock.json").exists() else "unknown")
    framework = "static HTML generated by Python"
    if "next.config.js" in files or "next.config.mjs" in files:
        framework = "Next.js"
    elif "astro.config.mjs" in files:
        framework = "Astro"
    elif "vite.config.ts" in files or "vite.config.js" in files:
        framework = "Vite/static app"

    redirects = (site_dir / "_redirects").read_text(encoding="utf-8", errors="ignore") if (site_dir / "_redirects").exists() else ""
    discovery = {
        "generatedAt": now_iso(),
        "framework": framework,
        "packageManager": package_manager,
        "buildCommand": "uv run python -m pytest / publisher workflows; static site already committed",
        "testCommand": "uv run pytest -q",
        "siteDir": rel(site_dir),
        "staticRoutes": routes,
        "generatedPageCount": len(generated_pages),
        "sampleGeneratedPages": generated_pages[:25],
        "workflows": workflows,
        "metadataSystem": "publisher/seo_tags.py plus static HTML head tags",
        "schemaImplementation": "inline JSON-LD in generated/static HTML",
        "sitemap": "site/sitemap.xml" if (site_dir / "sitemap.xml").exists() else None,
        "robots": "site/robots.txt" if (site_dir / "robots.txt").exists() else None,
        "affiliateRedirectLayer": "site/_redirects /go/*" if "/go/" in redirects else None,
        "analytics": detect_analytics(site_dir),
        "emailCapture": detect_email_capture(site_dir),
        "adPlacement": detect_ads(site_dir),
        "pageTypeCounts": Counter(classify_page_type(path) for path in generated_pages),
    }
    write_json(ROOT / config["snapshotsDir"] / "repo-map.json", discovery)
    write_md(ROOT / config["reportsDir"] / "repo-discovery.md", repo_discovery_md(discovery))
    return discovery


def detect_analytics(site_dir: Path) -> dict:
    html = "\n".join(p.read_text(encoding="utf-8", errors="ignore")[:2500] for p in site_dir.glob("*.html"))
    return {
        "googleAnalytics": "googletagmanager.com/gtag/js" in html or "gtag(" in html,
        "measurementIds": sorted(set(re.findall(r"G-[A-Z0-9]+", html))),
    }


def detect_email_capture(site_dir: Path) -> dict:
    html = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in site_dir.glob("*.html"))
    return {"formsubmit": "formsubmit.co" in html, "mailto": "mailto:" in html}


def detect_ads(site_dir: Path) -> dict:
    html = "\n".join(p.read_text(encoding="utf-8", errors="ignore")[:5000] for p in site_dir.glob("*.html"))
    return {"adsense": "adsbygoogle" in html or "pagead2.googlesyndication.com" in html}


def import_otto(config: dict) -> dict:
    imports_dir = ROOT / config["ottoImportsDir"]
    normalized: list[dict] = []
    for file in sorted(imports_dir.glob("*")):
        if file.is_dir():
            continue
        if file.suffix.lower() == ".csv":
            normalized.extend(normalize_csv_rows(file))
        elif file.suffix.lower() == ".xlsx":
            normalized.extend(normalize_xlsx_rows(file))

    buckets = {
        "title-fixes": [],
        "meta-description-fixes": [],
        "canonical-fixes": [],
        "social-fixes": [],
        "link-fixes": [],
        "heading-fixes": [],
        "content-fixes": [],
        "manual-review-needed": [],
    }
    for item in normalized:
        issue = item["issueType"]
        if item["needsHumanReview"]:
            buckets["manual-review-needed"].append(item)
        elif "title" in issue:
            buckets["title-fixes"].append(item)
        elif "description" in issue or "meta" in issue:
            buckets["meta-description-fixes"].append(item)
        elif "canonical" in issue:
            buckets["canonical-fixes"].append(item)
        elif "og" in issue or "twitter" in issue:
            buckets["social-fixes"].append(item)
        elif "link" in issue:
            buckets["link-fixes"].append(item)
        elif "h1" in issue or "h2" in issue or "heading" in issue:
            buckets["heading-fixes"].append(item)
        else:
            buckets["content-fixes"].append(item)

    normalized_dir = imports_dir / "normalized"
    write_json(normalized_dir / "otto-summary.json", {"generatedAt": now_iso(), "items": normalized, "count": len(normalized)})
    for name, rows in buckets.items():
        write_json(normalized_dir / f"{name}.json", rows)
    return {"count": len(normalized), "buckets": {k: len(v) for k, v in buckets.items()}}


def normalize_csv_rows(file: Path) -> list[dict]:
    rows = []
    with file.open(newline="", encoding="utf-8-sig", errors="ignore") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows.append(normalize_otto_row(file, file.stem, row))
    return rows


def normalize_xlsx_rows(file: Path) -> list[dict]:
    try:
        import openpyxl  # type: ignore
    except Exception:
        return [
            {
                "path": "",
                "url": "",
                "issueType": "xlsx_import_skipped",
                "currentValue": "",
                "recommendedValue": "",
                "sourceFile": rel(file),
                "sheetName": "",
                "severity": "warning",
                "confidence": 0.3,
                "safeToApply": False,
                "reason": "openpyxl is not installed; CSV exports are still supported.",
                "needsHumanReview": True,
            }
        ]
    wb = openpyxl.load_workbook(file, read_only=True, data_only=True)
    rows = []
    for ws in wb.worksheets:
        values = list(ws.iter_rows(values_only=True))
        if not values:
            continue
        headers = [str(v or "").strip() for v in values[0]]
        for raw in values[1:]:
            row = {headers[i]: raw[i] if i < len(raw) else "" for i in range(len(headers))}
            rows.append(normalize_otto_row(file, ws.title, row))
    return rows


def normalize_otto_row(file: Path, sheet: str, row: dict) -> dict:
    lowered = {str(k).strip().lower(): "" if v is None else str(v).strip() for k, v in row.items()}
    url = first_existing(lowered, ["url", "page url", "page", "address", "loc", "path"])
    issue_type = first_existing(lowered, ["issue", "issue type", "fix type", "type", "field", "optimization"]) or sheet
    current = first_existing(lowered, ["current", "current value", "old value", "detected", "from"])
    recommended = first_existing(lowered, ["recommended", "recommended value", "recommended fix", "new value", "suggestion", "to", "value"])
    path = normalize_path(url) if url else ""
    safe, reason = safe_to_apply(issue_type, current, recommended)
    return {
        "path": path,
        "url": url,
        "issueType": issue_type.lower().replace(" ", "_"),
        "currentValue": current,
        "recommendedValue": recommended,
        "sourceFile": rel(file),
        "sheetName": sheet,
        "severity": "warning" if safe else "review",
        "confidence": 0.8 if safe else 0.45,
        "safeToApply": safe,
        "reason": reason,
        "needsHumanReview": not safe,
    }


def first_existing(row: dict, keys: list[str]) -> str:
    for key in keys:
        if row.get(key):
            return row[key]
    return ""


def safe_to_apply(issue_type: str, current: str, recommended: str) -> tuple[bool, str]:
    issue = issue_type.lower()
    unsafe_issue = ["coupon", "discount", "review_rating", "rating", "hands-on", "delete", "noindex", "affiliate"]
    if any(token in issue for token in unsafe_issue):
        return False, "Potential factual, monetization, or indexability claim requires manual review."
    safe = ["title", "meta", "description", "canonical", "og", "twitter", "card", "internal link", "h1", "h2"]
    if recommended and any(token in issue for token in safe):
        return True, "On-page metadata/link/heading fix is safe if it targets an existing page."
    return False, "Unknown recommendation type or missing recommended value."


def crawl_site(config: dict) -> list[PageAudit]:
    site_dir = ROOT / config["siteDir"]
    files = sorted(site_dir.glob("*.html")) + sorted((site_dir / "pages").glob("*.html"))
    files = [file for file in files if not should_exclude_path(file_to_path(file, site_dir), config)]
    existing_paths = {file_to_path(file, site_dir) for file in files}
    audits = [audit_file(file, site_dir, existing_paths, config) for file in files]
    write_json(ROOT / config["snapshotsDir"] / "pages.json", [asdict(a) for a in audits])
    return audits


def should_exclude_path(path: str, config: dict) -> bool:
    return any(re.search(pattern, path) for pattern in config.get("excludePathPatterns", []))


def audit_file(file: Path, site_dir: Path, existing_paths: set[str], config: dict) -> PageAudit:
    html = file.read_text(encoding="utf-8", errors="ignore")
    path = file_to_path(file, site_dir)
    title = first_match(r"<title[^>]*>(.*?)</title>", html)
    meta = first_match(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)["\']', html)
    canonical = attr_value(first_match(r"(<link[^>]+rel=[\"']canonical[\"'][^>]*>)", html), "href")
    robots = attr_value(first_match(r"(<meta[^>]+name=[\"']robots[\"'][^>]*>)", html), "content")
    h1 = all_matches(r"<h1[^>]*>(.*?)</h1>", html)
    h2 = all_matches(r"<h2[^>]*>(.*?)</h2>", html)
    links = [attr_value(tag, "href") for tag in re.findall(r"<a\b[^>]*>", html, re.I)]
    links = [l for l in links if l and not l.startswith("#") and not l.startswith("mailto:") and not l.startswith("tel:")]
    internal, external, affiliate = split_links(links)
    broken = find_broken_internal_links(internal, existing_paths)
    image_tags = re.findall(r"<img\b[^>]*>", html, re.I)
    jsonld_blocks = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.I | re.S)
    schema_types, invalid_jsonld = schema_types_from_blocks(jsonld_blocks)
    text = strip_tags(html)
    audit = PageAudit(
        path=path,
        file=rel(file),
        url=public_url(config["siteUrl"], path),
        page_type=classify_page_type(path, html),
        title=title,
        title_length=len(title),
        meta_description=meta,
        meta_length=len(meta),
        canonical=canonical,
        robots=robots,
        h1=h1,
        h2=h2,
        word_count=len(re.findall(r"\b\w+\b", text)),
        internal_links=internal,
        external_links=external,
        affiliate_links=affiliate,
        broken_internal_links=broken,
        images=len(image_tags),
        images_missing_alt=sum(1 for tag in image_tags if not attr_value(tag, "alt")),
        jsonld_blocks=len(jsonld_blocks),
        schema_types=schema_types,
        has_faq=bool(re.search(r"\bFAQ\b|frequently asked", text, re.I)),
        has_faq_schema="FAQPage" in schema_types,
        has_pricing_table=bool(re.search(r"<table|pricing|plan", html, re.I)),
        has_comparison_table=bool(re.search(r"<table|comparison|side-by-side|vs", html, re.I)),
        has_trust_box=bool(re.search(r"trustbox|trust box|no paid rankings|vendors cannot buy", html, re.I)),
        has_related_pages=bool(re.search(r"related pages|related comparisons|you may also", html, re.I)),
        has_affiliate_disclosure=bool(re.search(r"affiliate disclosure|commission|affiliate links", html, re.I)),
        has_methodology=bool(re.search(r"methodology", html, re.I)),
        has_correction=bool(re.search(r"correction|outdated pricing|report an error", html, re.I)),
        has_last_verified=bool(re.search(r"last verified|last checked|verified", html, re.I)),
        has_pricing_source=bool(re.search(r"pricing source|source:", html, re.I)),
        has_email_capture=bool(re.search(r'type=["\']email["\']|newsletter|digest', html, re.I)),
        has_cta=bool(re.search(r"try free|start free|start trial|open offer|view pricing|compare alternatives|build shortlist|href=[\"']/go/", html, re.I)),
        has_sticky_cta=bool(re.search(r"sticky.*cta|position:\s*fixed", html, re.I | re.S)),
    )
    audit.issues, audit.warnings = classify_issues(audit, invalid_jsonld, config)
    audit.score = score_page(audit)
    return audit


def split_links(links: list[str]) -> tuple[list[str], list[str], list[str]]:
    internal, external, affiliate = [], [], []
    for link in links:
        if link.startswith("/go/") or "/go/" in link:
            affiliate.append(link)
            internal.append(link)
        elif link.startswith("/") or link.startswith("https://saaspare.org") or link.startswith("http://saaspare.org"):
            internal.append(link)
        elif link.startswith("http://") or link.startswith("https://"):
            external.append(link)
    return sorted(set(internal)), sorted(set(external)), sorted(set(affiliate))


def find_broken_internal_links(links: list[str], existing_paths: set[str]) -> list[str]:
    broken = []
    allowed_prefixes = ("/go/", "/assets/", "/favicon", "/_redirects")
    for link in links:
        path = normalize_path(link)
        if path.startswith(allowed_prefixes):
            continue
        if path not in existing_paths and path.rstrip("/") not in existing_paths:
            broken.append(link)
    return sorted(set(broken))


def schema_types_from_blocks(blocks: list[str]) -> tuple[list[str], bool]:
    types = []
    invalid = False
    for block in blocks:
        try:
            data = json.loads(block.strip())
        except Exception:
            invalid = True
            continue
        collect_schema_types(data, types)
    return sorted(set(types)), invalid


def collect_schema_types(value, types: list[str]) -> None:
    if isinstance(value, dict):
        t = value.get("@type")
        if isinstance(t, str):
            types.append(t)
        elif isinstance(t, list):
            types.extend(str(item) for item in t)
        for child in value.values():
            collect_schema_types(child, types)
    elif isinstance(value, list):
        for child in value:
            collect_schema_types(child, types)


def classify_issues(audit: PageAudit, invalid_jsonld: bool, config: dict) -> tuple[list[str], list[str]]:
    thresholds = config["thresholds"]
    issues, warnings = [], []
    if not audit.title:
        issues.append("missing_title")
    elif audit.title_length < thresholds["titleMin"] or audit.title_length > thresholds["titleMax"]:
        warnings.append("title_length_outside_target")
    if not audit.meta_description:
        issues.append("missing_meta")
    elif audit.meta_length < thresholds["metaMin"] or audit.meta_length > thresholds["metaMax"]:
        warnings.append("meta_length_outside_target")
    if not audit.canonical:
        issues.append("invalid_canonical")
    elif normalize_path(audit.canonical) != audit.path:
        if normalize_path(audit.canonical) == "/" and audit.path != "/":
            issues.append("canonical_homepage_conflict")
        else:
            warnings.append("canonical_mismatch")
    if len(audit.h1) == 0:
        issues.append("no_h1")
    elif len(audit.h1) > 1:
        issues.append("duplicate_h1")
    if invalid_jsonld:
        issues.append("invalid_jsonld")
    if audit.broken_internal_links:
        issues.append("broken_internal_link")
    if audit.word_count < thresholds["thinWords"] and audit.page_type in {"pricing", "free_trial", "coupon", "review", "alternatives", "comparison", "best_of"}:
        warnings.append("thin_buyer_page")
    if audit.images_missing_alt:
        warnings.append("images_missing_alt")
    if audit.affiliate_links and not audit.has_affiliate_disclosure:
        warnings.append("affiliate_cta_missing_visible_disclosure")
    if audit.page_type in {"pricing", "free_trial", "coupon", "review", "alternatives", "comparison", "best_of"}:
        for flag, warning in [
            (audit.has_trust_box, "missing_trustbox"),
            (audit.has_related_pages, "missing_related_pages"),
            (audit.has_last_verified, "missing_last_verified"),
            (audit.has_methodology, "missing_methodology"),
            (audit.has_correction, "missing_correction_cta"),
        ]:
            if not flag:
                warnings.append(warning)
    return sorted(set(issues)), sorted(set(warnings))


def score_page(audit: PageAudit) -> dict[str, float]:
    technical = 20
    for issue in audit.issues:
        technical -= 3 if issue in SEVERE_ISSUES else 1
    for warning in ["title_length_outside_target", "meta_length_outside_target", "canonical_mismatch", "images_missing_alt"]:
        if warning in audit.warnings:
            technical -= 1
    technical = clamp(technical, 0, 20)

    content = 0
    content += 4 if audit.word_count >= 800 else max(0, audit.word_count / 200)
    content += 3 if audit.has_faq else 0
    content += 3 if audit.has_pricing_table else 0
    content += 3 if audit.has_comparison_table else 0
    content += 3 if audit.has_cta else 0
    content += 4 if audit.h2 else 0

    trust = sum(
        2.5
        for ok in [
            audit.has_trust_box,
            audit.has_last_verified,
            audit.has_pricing_source,
            audit.has_affiliate_disclosure,
            audit.has_methodology,
            audit.has_correction,
            "Organization" in audit.schema_types or "WebSite" in audit.schema_types,
            not audit.affiliate_links or audit.has_affiliate_disclosure,
        ]
        if ok
    )

    internal = 0
    internal += min(7, len(audit.internal_links) * 0.45)
    internal += 3 if audit.has_related_pages else 0
    internal += 3 if not audit.broken_internal_links else 0
    internal += 2 if any("/pages/" in link for link in audit.internal_links) else 0

    schema = 0
    schema += 3 if audit.jsonld_blocks else 0
    schema += 2 if "BreadcrumbList" in audit.schema_types else 0
    schema += 2 if audit.has_faq and audit.has_faq_schema else 0
    schema += 2 if audit.canonical else 0
    schema += 1 if "noindex" not in audit.robots.lower() else 0

    conversion = 0
    conversion += 3 if audit.has_cta else 0
    conversion += 2 if audit.affiliate_links else 0
    conversion += 2 if audit.has_email_capture else 0
    conversion += 2 if audit.has_sticky_cta else 0
    conversion += 1 if audit.has_affiliate_disclosure else 0

    ux = 5
    if audit.images_missing_alt:
        ux -= 1
    if audit.word_count < 250 and audit.page_type not in {"other", "trust"}:
        ux -= 1

    total = technical + min(content, 20) + min(trust, 20) + min(internal, 15) + min(schema, 10) + min(conversion, 10) + clamp(ux, 0, 5)
    return {
        "technical": round(technical, 2),
        "content": round(min(content, 20), 2),
        "trust": round(min(trust, 20), 2),
        "internalLinking": round(min(internal, 15), 2),
        "schemaIndexability": round(min(schema, 10), 2),
        "conversionRevenue": round(min(conversion, 10), 2),
        "performanceUx": round(clamp(ux, 0, 5), 2),
        "overall": round(clamp(total, 0, 100), 2),
    }


def apply_safe_fixes(config: dict, audits: list[PageAudit]) -> list[dict]:
    applied = []
    for audit in audits:
        file = ROOT / audit.file
        html = file.read_text(encoding="utf-8", errors="ignore")
        original = html
        fixes = []
        seo = get_page_seo(audit, config)
        html = upsert_title(html, seo["title"])
        html = upsert_meta(html, "description", seo["meta_description"])
        html = upsert_meta(html, "keywords", build_meta_keywords(audit, seo))
        html = upsert_link_rel(html, "canonical", audit.url)
        html = upsert_property(html, "og:title", seo["title"])
        html = upsert_property(html, "og:description", seo["meta_description"])
        html = upsert_property(html, "og:url", audit.url)
        html = upsert_property(html, "og:type", "website" if audit.page_type in {"other", "trust"} else "article")
        html = upsert_property(html, "og:image", DEFAULT_OG_IMAGE)
        html = upsert_meta(html, "twitter:card", "summary_large_image")
        html = upsert_meta(html, "twitter:site", TWITTER_SITE)
        html = upsert_meta(html, "twitter:title", seo["title"])
        html = upsert_meta(html, "twitter:description", seo["meta_description"])
        html = upsert_meta(html, "twitter:image", DEFAULT_OG_IMAGE)
        html = fix_internal_html_links(html)
        html = fix_saaspare_suffix_links(html)
        html = fix_known_broken_internal_links(html)
        html = add_missing_image_alt(html, audit)
        html = ensure_organization_schema(html)
        html = strip_unsupported_review_schema(html)
        html = inject_buyer_trust_block(html, audit, config)
        html = inject_related_actions_block(html, audit, config)
        if html != original:
            file.write_text(html, encoding="utf-8")
            fixes.extend(["metadata", "canonical", "social", "internal_links", "image_alt", "organization_schema", "trust_block", "schema_safety"])
            applied.append({"file": audit.file, "path": audit.path, "fixes": sorted(set(fixes))})
    write_json(ROOT / config["reportsDir"] / "applied-fixes.json", applied)
    write_md(ROOT / config["reportsDir"] / "applied-fixes.md", applied_fixes_md(applied))
    return applied


def get_page_seo(audit: PageAudit, config: dict) -> dict[str, str]:
    if get_seo_tags:
        return get_seo_tags(audit.path, fallback_title=audit.title, fallback_meta=audit.meta_description)
    title = audit.title or f"{audit.path.strip('/').replace('-', ' ').title()} | SaaSpare"
    meta = audit.meta_description or f"Compare software pricing, trials and alternatives for {title.replace(' | SaaSpare', '')} on SaaSpare."
    return {"title": title, "meta_description": meta}


def build_meta_keywords(audit: PageAudit, seo: dict[str, str]) -> str:
    """Meta keywords are ignored by Google, but some SEO tools still audit them."""
    title = seo.get("title") or audit.title or ""
    base = [
        title.replace("| SaaSpare", "").strip(),
        audit.page_type.replace("_", " "),
        "SaaS pricing",
        "software comparison",
        "free trial",
        "alternatives",
        "SaaSpare",
    ]
    words = []
    for item in base:
        item = re.sub(r"\s+", " ", item).strip(" ,-|")
        if item and item.lower() not in {w.lower() for w in words}:
            words.append(item)
    return ", ".join(words[:10])


def upsert_title(html: str, value: str) -> str:
    value = escape(html_clean(value), quote=False)
    if re.search(r"<title[^>]*>.*?</title>", html, re.I | re.S):
        return re.sub(r"<title[^>]*>.*?</title>", f"<title>{value}</title>", html, count=1, flags=re.I | re.S)
    return html.replace("</head>", f"<title>{value}</title>\n</head>", 1)


def upsert_meta(html: str, name: str, value: str) -> str:
    value = escape(html_clean(value), quote=True)
    pattern = rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]*>'
    tag = f'<meta name="{name}" content="{value}">'
    if re.search(pattern, html, re.I):
        return re.sub(pattern, tag, html, count=1, flags=re.I)
    return html.replace("</head>", f"{tag}\n</head>", 1)


def upsert_property(html: str, prop: str, value: str) -> str:
    value = escape(html_clean(value), quote=True)
    pattern = rf'<meta[^>]+property=["\']{re.escape(prop)}["\'][^>]*>'
    tag = f'<meta property="{prop}" content="{value}">'
    if re.search(pattern, html, re.I):
        return re.sub(pattern, tag, html, count=1, flags=re.I)
    return html.replace("</head>", f"{tag}\n</head>", 1)


def upsert_link_rel(html: str, rel_name: str, href: str) -> str:
    href = escape(href, quote=True)
    pattern = rf'<link[^>]+rel=["\']{re.escape(rel_name)}["\'][^>]*>'
    tag = f'<link rel="{rel_name}" href="{href}">'
    if re.search(pattern, html, re.I):
        return re.sub(pattern, tag, html, count=1, flags=re.I)
    return html.replace("</head>", f"{tag}\n</head>", 1)


def add_missing_image_alt(html: str, audit: PageAudit) -> str:
    default_alt = escape(f"SaaSpare {audit.page_type.replace('_', ' ')} page visual", quote=True)

    def repl(match: re.Match) -> str:
        tag = match.group(0)
        if attr_value(tag, "alt"):
            return tag
        insert_at = tag.rfind(">")
        if insert_at == -1:
            return tag
        slash = " /" if tag[:insert_at].rstrip().endswith("/") else ""
        body = tag[:insert_at].rstrip().rstrip("/")
        return f'{body} alt="{default_alt}"{slash}>'

    return re.sub(r"<img\b[^>]*>", repl, html, flags=re.I)


def ensure_organization_schema(html: str) -> str:
    if re.search(r'"@type"\s*:\s*"Organization"', html):
        return html
    script = '<script type="application/ld+json">' + json.dumps(ORG_SCHEMA, ensure_ascii=False) + "</script>"
    return html.replace("</head>", f"{script}\n</head>", 1)


def fix_internal_html_links(html: str) -> str:
    def repl(match: re.Match) -> str:
        quote = match.group(1)
        href = match.group(2)
        if href.startswith("http") and "saaspare.org" not in href:
            return match.group(0)
        if "/go/" in href:
            return match.group(0)
        clean = href.replace("/index.html", "/")
        clean = re.sub(r"\.html(?=([?#]|$))", "", clean)
        return f"href={quote}{clean}{quote}"

    return re.sub(r'href=(["\'])([^"\']+\.html(?:[?#][^"\']*)?)\1', repl, html)


def fix_saaspare_suffix_links(html: str) -> str:
    return re.sub(r'(?<=href=["\'])(https://saaspare\.org/pages/[^"\']+?)-saaspare(?=["\'])', r"\1", html)


def fix_known_broken_internal_links(html: str) -> str:
    replacements = {
        "https://saaspare.org/pages/hubspot-alternatives-2026-best-tools-compared": "https://saaspare.org/pages/best-hubspot-alternatives-in-2026-free-paid",
        "https://saaspare.org/pages/notion-alternatives-2026-best-tools-compared": "https://saaspare.org/pages/best-notion-alternatives-in-2026-free-paid",
        "https://saaspare.org/pages/best-crm-for-startups-2026": "https://saaspare.org/pages/best-crm-software-for-startups-in-2026-free-paid",
    }
    for old, new in replacements.items():
        html = html.replace(old, new)
    return html


def strip_unsupported_review_schema(html: str) -> str:
    def clean_value(value):
        if isinstance(value, list):
            cleaned = [clean_value(item) for item in value]
            return [item for item in cleaned if item is not None]
        if isinstance(value, dict):
            schema_type = value.get("@type")
            if schema_type == "Review" or schema_type == "AggregateRating":
                return None
            cleaned = {}
            for key, child in value.items():
                if key in {"review", "aggregateRating", "reviewRating"}:
                    continue
                cleaned_child = clean_value(child)
                if cleaned_child is not None:
                    cleaned[key] = cleaned_child
            return cleaned
        return value

    def repl(match: re.Match) -> str:
        raw = match.group(1)
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)
        cleaned = clean_value(parsed)
        if cleaned is None or cleaned == []:
            return ""
        return '<script type="application/ld+json">' + json.dumps(cleaned, ensure_ascii=False) + "</script>"

    return re.sub(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', repl, html, flags=re.I | re.S)


def inject_buyer_trust_block(html: str, audit: PageAudit, config: dict) -> str:
    buyer_types = {"pricing", "free_trial", "coupon", "review", "alternatives", "comparison", "best_of"}
    if audit.page_type not in buyer_types or "data-seo-trustbox" in html:
        return html
    site_url = config["siteUrl"].rstrip("/")
    source_line = "Pricing source: public vendor pages linked from this page where available; otherwise marked for verification."
    block = f"""
<section class="seo-trustbox section" data-seo-trustbox>
  <h2>How SaaSpare keeps this page useful</h2>
  <p><strong>No paid rankings:</strong> Vendors cannot buy placement or verdicts. SaaSpare may earn a commission when readers click some affiliate links, but that does not change the comparison order.</p>
  <p><strong>Last verified:</strong> {escape(audit.title[:80] or "This buyer page")} is checked during scheduled SEO and link audits. {source_line}</p>
  <p><strong>Methodology:</strong> We compare pricing signals, trial paths, buyer fit, alternatives, and visible vendor information. See <a href="{site_url}/methodology">our methodology</a> and <a href="{site_url}/affiliate-disclosure">affiliate disclosure</a>.</p>
  <p><strong>Correction CTA:</strong> See outdated pricing or an incorrect trial detail? <a href="{site_url}/contact">Report an error</a> and include the vendor source.</p>
</section>
"""
    if "</footer>" in html:
        return html.replace("<footer>", block + "\n<footer>", 1)
    if "</body>" in html:
        return html.replace("</body>", block + "\n</body>", 1)
    return html + block


def inject_related_actions_block(html: str, audit: PageAudit, config: dict) -> str:
    buyer_types = {"pricing", "free_trial", "coupon", "review", "alternatives", "comparison", "best_of"}
    if audit.page_type not in buyer_types or re.search(r"related pages|related comparisons|you may also|data-seo-related", html, re.I):
        return html
    site_url = config["siteUrl"].rstrip("/")
    block = f"""
<section class="related section" data-seo-related>
  <h3>Related Pages</h3>
  <a href="{site_url}/pages/">Browse all SaaS comparisons</a>
  <a href="{site_url}/deal-radar">Check current SaaS deals</a>
  <a href="{site_url}/shortlist">Build a shortlist</a>
  <a href="{site_url}/pages/saas-roi-calculator">Run the ROI calculator</a>
</section>
"""
    if '<section class="seo-trustbox' in html:
        return html.replace('<section class="seo-trustbox', block + '\n<section class="seo-trustbox', 1)
    if "</footer>" in html:
        return html.replace("<footer>", block + "\n<footer>", 1)
    if "</body>" in html:
        return html.replace("</body>", block + "\n</body>", 1)
    return html + block


def generate_reports(config: dict, audits: list[PageAudit], discovery: dict, otto: dict, applied: list[dict], mode: str) -> None:
    reports_dir = ROOT / config["reportsDir"]
    gsc = load_gsc_opportunities(config)
    write_json(reports_dir / "audit.json", [asdict(a) for a in audits])
    write_md(reports_dir / "audit.md", audit_md(audits))
    write_md(reports_dir / "severe-issues.md", issue_md(audits, severe=True))
    write_md(reports_dir / "warnings.md", issue_md(audits, severe=False))
    write_json(reports_dir / "page-quality-scores.json", [{"path": a.path, **a.score} for a in audits])
    write_csv(reports_dir / "page-quality-scores.csv", [{"path": a.path, "page_type": a.page_type, **a.score} for a in audits])
    write_md(reports_dir / "site-health.md", site_health_md(audits, discovery, otto, applied, mode))
    write_md(reports_dir / "top-100-fixes.md", top_fixes_md(audits))
    write_md(reports_dir / "manual-review-needed.md", manual_review_md(audits))
    write_md(reports_dir / "revenue-priorities.md", revenue_priorities_md(audits))
    write_json(reports_dir / "internal-link-map.json", internal_link_map(audits))
    write_json(reports_dir / "orphan-pages.json", orphan_pages(audits))
    write_md(reports_dir / "schema-validation.md", schema_validation_md(audits))
    write_json(reports_dir / "schema-coverage.json", schema_coverage(audits))
    write_md(reports_dir / "sitemap-report.md", sitemap_report_md(config, audits))
    write_json(reports_dir / "indexability-report.json", indexability_report(audits))
    write_md(reports_dir / "gsc-opportunities.md", gsc_report_md(gsc))
    write_json(reports_dir / "gsc-opportunities.json", gsc)
    write_md(reports_dir / "ai-suggestions.md", ai_suggestions_md(audits))
    write_json(reports_dir / "ai-suggestions.json", {"skipped": "CEREBRAS_API_KEY" not in os.environ, "suggestions": []})
    write_md(reports_dir / "conversion-issues.md", conversion_issues_md(audits))
    write_md(reports_dir / "analytics-events.md", analytics_events_md())
    write_md(reports_dir / "thin-pages.md", thin_pages_md(audits))
    write_md(reports_dir / "duplicate-intent.md", duplicate_intent_md(audits))
    write_md(reports_dir / "consolidation-candidates.md", duplicate_intent_md(audits))
    write_md(reports_dir / "noindex-candidates.md", noindex_candidates_md(audits))
    write_md(reports_dir / "hub-coverage.md", hub_coverage_md(audits))
    write_md(reports_dir / "link-cleanup.md", link_cleanup_md(audits))
    write_json(reports_dir / "unresolved-links.json", [{"path": a.path, "broken": a.broken_internal_links} for a in audits if a.broken_internal_links])
    write_md(reports_dir / "ux-performance.md", ux_performance_md(audits))


def repo_discovery_md(discovery: dict) -> str:
    return f"""# Repo Discovery

Generated: {discovery['generatedAt']}

## Stack
- Framework: {discovery['framework']}
- Package manager: {discovery['packageManager']}
- Build command: `{discovery['buildCommand']}`
- Test command: `{discovery['testCommand']}`
- Site directory: `{discovery['siteDir']}`

## SEO Surfaces
- Metadata system: {discovery['metadataSystem']}
- Schema: {discovery['schemaImplementation']}
- Sitemap: `{discovery['sitemap']}`
- Robots: `{discovery['robots']}`
- Affiliate redirect layer: {discovery['affiliateRedirectLayer']}
- Generated buyer pages: {discovery['generatedPageCount']}

## Analytics And Capture
- Google Analytics: {discovery['analytics']['googleAnalytics']} {discovery['analytics']['measurementIds']}
- Email capture: {discovery['emailCapture']}
- Ads detected: {discovery['adPlacement']}

## Page Type Counts
{dict_table(discovery['pageTypeCounts'])}
"""


def audit_md(audits: list[PageAudit]) -> str:
    counts = Counter(issue for a in audits for issue in a.issues)
    warnings = Counter(w for a in audits for w in a.warnings)
    return f"""# SEO Audit

Pages scanned: {len(audits)}

## Severe Issue Counts
{dict_table(counts)}

## Warning Counts
{dict_table(warnings)}

## Lowest Scoring Pages
{pages_table(sorted(audits, key=lambda a: a.score['overall'])[:50])}
"""


def issue_md(audits: list[PageAudit], severe: bool) -> str:
    title = "Severe Issues" if severe else "Warnings"
    rows = []
    for audit in audits:
        values = audit.issues if severe else audit.warnings
        if values:
            rows.append(f"- `{audit.path}` ({audit.page_type}, {audit.score['overall']}/100): {', '.join(values)}")
    return f"# {title}\n\n" + ("\n".join(rows[:300]) if rows else "No issues found.\n")


def site_health_md(audits: list[PageAudit], discovery: dict, otto: dict, applied: list[dict], mode: str) -> str:
    avg = average_scores(audits)
    level = health_level(avg["overall"])
    healthy = sum(1 for a in audits if a.score["overall"] >= 85)
    unhealthy = sum(1 for a in audits if a.score["overall"] < 55)
    return f"""# SaaSpare SEO Helper Health Dashboard

Generated: {now_iso()}
Mode: `{mode}`

## Current Score
- Overall SaaSpare Health Score: **{avg['overall']}/100**
- Level: **{level}**
- Technical SEO: {avg['technical']}/20
- Content usefulness: {avg['content']}/20
- Trust/E-E-A-T: {avg['trust']}/20
- Internal linking: {avg['internalLinking']}/15
- Schema/indexability: {avg['schemaIndexability']}/10
- Conversion/revenue: {avg['conversionRevenue']}/10
- Performance/UX: {avg['performanceUx']}/5

## Dashboard Summary
- Pages scanned: {len(audits)}
- Healthy pages (85+): {healthy}
- Unhealthy pages (<55): {unhealthy}
- OTTO import rows normalized: {otto.get('count', 0)}
- Safe fixes applied this run: {len(applied)}
- GSC: {gsc_skip_reason()}
- Cerebras AI suggestions: {"enabled" if "CEREBRAS_API_KEY" in os.environ else "skipped; CEREBRAS_API_KEY missing"}

## Fastest Path To 70
- Fix severe metadata/canonical/H1/schema errors reported in `top-100-fixes.md`.
- Add TrustBox, RelatedPages, visible source citations and correction CTAs to all buyer templates.
- Keep affiliate disclosures visible on every monetized page.

## Fastest Path To 85
- Enrich the top 100 revenue pages with page-specific pricing/trial/source sections.
- Build category hubs with crawlable links to pricing, comparison, coupon, free-trial and alternatives pages.
- Add schema only where matching visible content exists.

## What Is Required For 95+
- Real source-verified pricing/trial data at scale.
- Strong backlink/authority work outside the repo.
- GSC-driven title/meta and content upgrades every week.
- Manual review for pricing, coupon, review, rating and vendor claims.

## Top 25 Highest-Impact Fixes
{top_fixes_list(audits, 25)}

## Top 25 Revenue Opportunities
{revenue_list(audits, 25)}
"""


def top_fixes_md(audits: list[PageAudit]) -> str:
    return "# Top 100 Fixes\n\n" + top_fixes_list(audits, 100)


def manual_review_md(audits: list[PageAudit]) -> str:
    rows = []
    for a in sorted(audits, key=lambda x: x.score["overall"]):
        flags = [w for w in a.warnings if w in {"thin_buyer_page", "missing_last_verified", "missing_trustbox", "missing_methodology", "missing_correction_cta", "affiliate_cta_missing_visible_disclosure"}]
        if flags:
            rows.append(f"- `{a.path}`: {', '.join(flags)}")
    return "# Manual Review Needed\n\nThese are not safe to fake or mass rewrite.\n\n" + ("\n".join(rows[:200]) if rows else "No manual-review items found.\n")


def revenue_priorities_md(audits: list[PageAudit]) -> str:
    return "# Revenue Priorities\n\n" + revenue_list(audits, 100)


def internal_link_map(audits: list[PageAudit]) -> dict:
    inbound = defaultdict(list)
    for audit in audits:
        for link in audit.internal_links:
            inbound[normalize_path(link)].append(audit.path)
    return {a.path: {"outbound": a.internal_links, "inbound": inbound.get(a.path, [])} for a in audits}


def orphan_pages(audits: list[PageAudit]) -> list[dict]:
    link_map = internal_link_map(audits)
    return [{"path": p, "score": data} for p, data in link_map.items() if not data["inbound"] and p != "/"]


def schema_validation_md(audits: list[PageAudit]) -> str:
    missing = [a for a in audits if not a.jsonld_blocks]
    invalid = [a for a in audits if "invalid_jsonld" in a.issues]
    return f"""# Schema Validation

- Pages with JSON-LD: {sum(1 for a in audits if a.jsonld_blocks)}
- Pages missing JSON-LD: {len(missing)}
- Pages with invalid JSON-LD: {len(invalid)}

## Invalid JSON-LD
{pages_table(invalid[:50])}
"""


def schema_coverage(audits: list[PageAudit]) -> dict:
    return {"schemaTypes": Counter(t for a in audits for t in a.schema_types), "missingJsonLd": [a.path for a in audits if not a.jsonld_blocks]}


def sitemap_report_md(config: dict, audits: list[PageAudit]) -> str:
    sitemap = ROOT / config["siteDir"] / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8", errors="ignore") if sitemap.exists() else ""
    urls = set(re.findall(r"<loc>(.*?)</loc>", text))
    missing = [a.url for a in audits if a.url not in urls and a.path != "/"]
    return f"""# Sitemap Report

- Sitemap exists: {sitemap.exists()}
- Sitemap URL count: {len(urls)}
- Scanned HTML pages: {len(audits)}
- Scanned pages missing from sitemap: {len(missing)}

## Missing Examples
{chr(10).join(f"- {u}" for u in missing[:50]) if missing else "No missing pages detected."}
"""


def indexability_report(audits: list[PageAudit]) -> dict:
    return {"noindex": [a.path for a in audits if "noindex" in a.robots.lower()], "canonicalIssues": [a.path for a in audits if "canonical" in " ".join(a.issues + a.warnings)]}


def load_gsc_opportunities(config: dict) -> dict:
    if not has_gsc_credentials():
        return {"skipped": True, "reason": gsc_skip_reason(), "opportunities": []}
    try:
        from google.oauth2.credentials import Credentials as OAuthCredentials
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except Exception as exc:
        return {"skipped": True, "reason": f"google api libraries unavailable: {exc}", "opportunities": []}

    site_url = os.environ.get("GSC_SITE_URL") or config.get("siteUrl") or "https://saaspare.org"
    end_date = datetime.now(UTC).date() - timedelta(days=3)
    start_date = end_date - timedelta(days=int(os.environ.get("GSC_LOOKBACK_DAYS", "28")))
    scopes = ["https://www.googleapis.com/auth/webmasters.readonly"]
    try:
        oauth_refresh = os.environ.get("GSC_OAUTH_REFRESH_TOKEN")
        oauth_client_id = os.environ.get("GSC_OAUTH_CLIENT_ID")
        oauth_client_secret = os.environ.get("GSC_OAUTH_CLIENT_SECRET")
        credentials_source = os.environ.get("GSC_SERVICE_ACCOUNT_JSON") or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if oauth_refresh and oauth_client_id and oauth_client_secret:
            credentials = OAuthCredentials(
                token=None,
                refresh_token=oauth_refresh,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=oauth_client_id,
                client_secret=oauth_client_secret,
                scopes=scopes,
            )
        elif credentials_source:
            credentials_json = decode_possible_base64(credentials_source)
            info = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        elif credentials_path:
            credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=scopes)
        else:
            return {"skipped": True, "reason": gsc_skip_reason(), "opportunities": []}

        service = build("searchconsole", "v1", credentials=credentials, cache_discovery=False)
        rows = []
        for dimensions in (["page", "query"], ["page"]):
            response = (
                service.searchanalytics()
                .query(
                    siteUrl=site_url,
                    body={
                        "startDate": start_date.isoformat(),
                        "endDate": end_date.isoformat(),
                        "dimensions": dimensions,
                        "rowLimit": 2500,
                    },
                )
                .execute()
            )
            rows.extend(normalize_gsc_rows(response.get("rows", []), dimensions))
        opportunities = rank_gsc_opportunities(rows)
        return {
            "skipped": False,
            "siteUrl": site_url,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "rowsPulled": len(rows),
            "opportunities": opportunities,
        }
    except Exception as exc:
        return {"skipped": True, "reason": f"GSC API error: {exc}", "opportunities": []}


def decode_possible_base64(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith("{"):
        return stripped
    try:
        decoded = base64.b64decode(stripped).decode("utf-8")
        if decoded.strip().startswith("{"):
            return decoded
    except Exception:
        pass
    return stripped


def normalize_gsc_rows(rows: list[dict], dimensions: list[str]) -> list[dict]:
    normalized = []
    for row in rows:
        keys = row.get("keys", [])
        data = {
            "page": keys[0] if keys else "",
            "query": keys[1] if len(keys) > 1 else "",
            "clicks": float(row.get("clicks", 0) or 0),
            "impressions": float(row.get("impressions", 0) or 0),
            "ctr": float(row.get("ctr", 0) or 0),
            "position": float(row.get("position", 0) or 0),
            "dimensions": dimensions,
        }
        normalized.append(data)
    return normalized


def rank_gsc_opportunities(rows: list[dict]) -> list[dict]:
    buyer_re = re.compile(r"\b(pricing|price|cost|free trial|trial|coupon|promo|discount|alternative|alternatives|vs|review|deal)\b", re.I)
    opportunities = []
    for row in rows:
        impressions = row["impressions"]
        ctr = row["ctr"]
        position = row["position"]
        query = row.get("query", "")
        score = 0.0
        if impressions >= 10:
            score += min(impressions / 50, 25)
        if 8 <= position <= 30:
            score += 30 - abs(position - 12)
        if ctr < 0.02 and impressions >= 20:
            score += 20
        if buyer_re.search(query) or buyer_re.search(row.get("page", "")):
            score += 25
        if score <= 0:
            continue
        opportunities.append(
            {
                "score": round(score, 2),
                "page": row.get("page", ""),
                "query": query,
                "clicks": row["clicks"],
                "impressions": row["impressions"],
                "ctr": round(row["ctr"], 4),
                "position": round(row["position"], 2),
                "recommendedAction": recommend_gsc_action(row),
            }
        )
    opportunities.sort(key=lambda item: item["score"], reverse=True)
    return opportunities[:200]


def recommend_gsc_action(row: dict) -> str:
    if row["impressions"] >= 20 and row["ctr"] < 0.02:
        return "Rewrite title/meta for stronger buyer-intent CTR; keep content factual."
    if 8 <= row["position"] <= 20:
        return "Add internal links, source-backed FAQ, and stronger above-fold verdict to push into top 10."
    if 20 < row["position"] <= 30:
        return "Add supporting links from category hubs and improve page-specific evidence."
    return "Monitor and prioritize if impressions continue rising."


def gsc_report_md(gsc: dict) -> str:
    if gsc.get("skipped"):
        return f"""# GSC Opportunities

Status: {gsc.get('reason', gsc_skip_reason())}

When credentials are available, this report prioritizes:
- high impressions / low CTR pages
- positions 8-30
- buyer intent queries
- pages losing clicks
- indexing and canonical issues
"""
    rows = gsc.get("opportunities", [])
    body = "\n".join(
        f"- Score {row['score']}: `{row['page']}` query `{row.get('query') or '(page rollup)'}` - impressions {row['impressions']}, CTR {row['ctr']}, position {row['position']}. {row['recommendedAction']}"
        for row in rows[:100]
    )
    return f"""# GSC Opportunities

Status: connected
Site: {gsc.get('siteUrl')}
Range: {gsc.get('startDate')} to {gsc.get('endDate')}
Rows pulled: {gsc.get('rowsPulled', 0)}

## Top Opportunities
{body if body else "No GSC opportunities found yet. This usually means the property is very new or has too few impressions."}
"""


def ai_suggestions_md(audits: list[PageAudit]) -> str:
    if "CEREBRAS_API_KEY" not in os.environ:
        return "# AI Suggestions\n\nSkipped: `CEREBRAS_API_KEY` is not set. No AI content was generated.\n"
    candidates = sorted(audits, key=lambda a: a.score["overall"])[:25]
    lines = [f"- `{a.path}`: suggest title/meta/FAQ/internal-link brief from existing visible content only." for a in candidates]
    return "# AI Suggestions\n\nCerebras key detected. Suggestions are queued for report-only use; no factual claims are auto-published.\n\n" + "\n".join(lines)


def conversion_issues_md(audits: list[PageAudit]) -> str:
    rows = [f"- `{a.path}`: CTA={a.has_cta}, sticky={a.has_sticky_cta}, email={a.has_email_capture}, disclosure={a.has_affiliate_disclosure}" for a in audits if a.page_type in {"coupon", "pricing", "free_trial", "alternatives", "comparison", "review"} and (not a.has_cta or not a.has_affiliate_disclosure)]
    return "# Conversion Issues\n\n" + ("\n".join(rows[:200]) if rows else "No major conversion issues detected.\n")


def analytics_events_md() -> str:
    events = ["affiliate_click", "cta_click", "comparison_table_click", "email_capture_submit", "deal_radar_click", "roi_calculator_start", "coupon_click", "pricing_source_click", "correction_submit", "related_page_click"]
    return "# Analytics Events\n\nRecommended event names for implementation/validation:\n\n" + "\n".join(f"- `{event}`" for event in events)


def thin_pages_md(audits: list[PageAudit]) -> str:
    rows = [f"- `{a.path}`: {a.word_count} words, score {a.score['overall']}" for a in audits if "thin_buyer_page" in a.warnings]
    return "# Thin Pages\n\n" + ("\n".join(rows[:300]) if rows else "No thin buyer pages detected.\n")


def duplicate_intent_md(audits: list[PageAudit]) -> str:
    by_title = defaultdict(list)
    by_meta = defaultdict(list)
    for a in audits:
        by_title[a.title].append(a.path)
        by_meta[a.meta_description].append(a.path)
    rows = []
    for label, group in [("Duplicate title", by_title), ("Duplicate meta", by_meta)]:
        for value, paths in group.items():
            if value and len(paths) > 1:
                rows.append(f"- {label}: `{value[:90]}` -> {', '.join(paths[:8])}")
    return "# Duplicate Intent\n\n" + ("\n".join(rows[:200]) if rows else "No duplicate title/meta clusters detected.\n")


def noindex_candidates_md(audits: list[PageAudit]) -> str:
    rows = [f"- `{a.path}`: low score {a.score['overall']}, issues {', '.join(a.issues + a.warnings)}" for a in sorted(audits, key=lambda x: x.score["overall"]) if a.score["overall"] < 35]
    return "# Noindex Candidates\n\nNo pages are noindexed automatically. Manual review only.\n\n" + ("\n".join(rows[:100]) if rows else "No candidates detected.\n")


def hub_coverage_md(audits: list[PageAudit]) -> str:
    categories = ["project-management", "crm", "seo", "accounting", "security", "developer", "ai", "hr", "ecommerce", "marketing"]
    rows = []
    for cat in categories:
        support = [a for a in audits if cat in a.path.lower() or cat.replace("-", " ") in a.title.lower()]
        rows.append(f"- {cat}: {len(support)} supporting pages detected")
    return "# Hub Coverage\n\n" + "\n".join(rows)


def link_cleanup_md(audits: list[PageAudit]) -> str:
    broken = [a for a in audits if a.broken_internal_links]
    html_links = sum(1 for a in audits for link in a.internal_links if ".html" in link)
    return f"""# Link Cleanup

- Pages with broken internal links: {len(broken)}
- Internal links still containing `.html`: {html_links}

## Broken Internal Links
{chr(10).join(f"- `{a.path}`: {', '.join(a.broken_internal_links[:5])}" for a in broken[:100]) if broken else "No broken internal links detected."}
"""


def ux_performance_md(audits: list[PageAudit]) -> str:
    alt = [a for a in audits if a.images_missing_alt]
    return f"""# UX / Performance

- Pages with images missing alt: {len(alt)}
- Pages with sticky CTA detected: {sum(1 for a in audits if a.has_sticky_cta)}
- Pages with email capture detected: {sum(1 for a in audits if a.has_email_capture)}

No browser performance trace was run in this static audit.
"""


def applied_fixes_md(applied: list[dict]) -> str:
    return "# Applied Safe Fixes\n\n" + ("\n".join(f"- `{a['path']}`: {', '.join(a['fixes'])}" for a in applied[:300]) if applied else "No safe fixes were applied.\n")


def top_fixes_list(audits: list[PageAudit], limit: int) -> str:
    candidates = sorted([a for a in audits if a.issues or a.warnings], key=lambda a: (len(a.issues) * -10 + a.score["overall"]))
    lines = []
    for a in candidates[:limit]:
        lines.append(f"- `{a.path}` ({a.score['overall']}/100): {', '.join(a.issues + a.warnings)}")
    return "\n".join(lines) if lines else "No fixes found."


def revenue_list(audits: list[PageAudit], limit: int) -> str:
    high = {"coupon": 10, "pricing": 9, "free_trial": 9, "alternatives": 8, "comparison": 8, "review": 7, "best_of": 6}
    ranked = sorted(audits, key=lambda a: (high.get(a.page_type, 1), bool(a.affiliate_links), -a.score["overall"]), reverse=True)
    return "\n".join(f"- `{a.path}` ({a.page_type}, score {a.score['overall']}): CTA={a.has_cta}, affiliateLinks={len(a.affiliate_links)}, disclosure={a.has_affiliate_disclosure}" for a in ranked[:limit])


def average_scores(audits: list[PageAudit]) -> dict[str, float]:
    keys = ["technical", "content", "trust", "internalLinking", "schemaIndexability", "conversionRevenue", "performanceUx", "overall"]
    if not audits:
        return {k: 0 for k in keys}
    return {k: round(sum(a.score[k] for a in audits) / len(audits), 2) for k in keys}


def health_level(score: float) -> str:
    if score < 20:
        return "Broken"
    if score < 40:
        return "Weak"
    if score < 55:
        return "Crawlable but under-trusted"
    if score < 70:
        return "Solid foundation"
    if score < 85:
        return "Competitive"
    if score < 95:
        return "Strong authority-ready"
    return "Elite SEO/revenue engine"


def pages_table(audits: list[PageAudit]) -> str:
    if not audits:
        return "No pages."
    return "\n".join(f"- `{a.path}`: {a.score.get('overall', 0)}/100, issues={', '.join(a.issues) or 'none'}" for a in audits)


def dict_table(counter) -> str:
    if not counter:
        return "No items."
    items = counter.items() if hasattr(counter, "items") else counter
    return "\n".join(f"- {k}: {v}" for k, v in sorted(items, key=lambda item: str(item[0])))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str), encoding="utf-8")


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def has_gsc_credentials() -> bool:
    has_oauth = bool(
        os.environ.get("GSC_OAUTH_REFRESH_TOKEN")
        and os.environ.get("GSC_OAUTH_CLIENT_ID")
        and os.environ.get("GSC_OAUTH_CLIENT_SECRET")
    )
    return has_oauth or bool(os.environ.get("GSC_SERVICE_ACCOUNT_JSON") or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON"))


def gsc_skip_reason() -> str:
    if has_gsc_credentials():
        return "credentials detected; live API pull enabled"
    return "skipped; add GSC OAuth secrets or GSC service account JSON to enable live Search Console pulls"


def run(mode: str, only: str | None) -> int:
    config = load_config()
    ensure_dirs(config)
    discovery = discover_repo(config)
    otto = import_otto(config)
    audits = crawl_site(config)
    applied: list[dict] = []
    if mode == "apply-safe":
        applied = apply_safe_fixes(config, audits)
        audits = crawl_site(config)
    generate_reports(config, audits, discovery, otto, applied, mode)
    avg = average_scores(audits)
    print(f"SaaSpare SEO Helper complete: mode={mode}, pages={len(audits)}, health={avg['overall']}/100 ({health_level(avg['overall'])}), applied={len(applied)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="SaaSpare repo-native SEO Helper")
    parser.add_argument("--mode", choices=["audit", "apply-safe"], default="audit")
    parser.add_argument("--only", default=None, help="Compatibility flag for package scripts; full first-stage pipeline still runs.")
    args = parser.parse_args()
    # npm on some Windows setups treats `npm run seo:agent -- --mode=apply-safe`
    # as npm_config_mode instead of forwarding it. Support both forms.
    env_mode = os.environ.get("npm_config_mode")
    if env_mode in {"audit", "apply-safe"} and args.mode == "audit":
        args.mode = env_mode
    return run(args.mode, args.only)


if __name__ == "__main__":
    raise SystemExit(main())
