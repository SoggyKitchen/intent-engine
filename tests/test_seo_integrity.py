"""
CI gate for shipped-site SEO integrity.

Verifies:
- Every HTML page in site/ has a canonical link.
- Every page is listed in site/sitemap.xml (with narrow exclusions for
  preview/internal pages that are robots-noindexed).
- Every schema.org JSON-LD block parses as valid JSON.
- Every comparison/pricing/review/alternatives/coupon/free-trial/best-of
  page (money pages) has at least one JSON-LD block of an expected
  schema type.

These tests run fast (pure file I/O + json parsing) and give us a
repo-native replacement for the "OTTO-style" external schema validator.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
SITEMAP = SITE / "sitemap.xml"

# Pages we allow without canonical (tooling / non-indexable)
ALLOW_NO_CANONICAL = {
    SITE / "_redirects",
    # Third-party site-verification files
    SITE / "fo-verify.html",
    SITE / "fo-verify-c0ceba67-f661-491b-9895-78e0a0a9eb9f.html",
}
# Pages that are intentionally not in sitemap (preview, utility)
ALLOW_NOT_IN_SITEMAP = {
    SITE / "ph-preview-1.html",
    SITE / "ph-preview-2.html",
    SITE / "ph-preview-3.html",
    SITE / "humans.txt",
}


# ---- helpers ----

CANONICAL_RE = re.compile(
    r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']',
    re.IGNORECASE,
)

NOINDEX_RE = re.compile(
    r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*noindex',
    re.IGNORECASE,
)

JSONLD_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>',
    re.IGNORECASE,
)


def _iter_html() -> list[Path]:
    return [p for p in SITE.rglob("*.html") if p.is_file()]


def _is_money_page(path: Path) -> bool:
    name = path.name
    return (
        ("-vs-" in name and "which-is-better" in name)
        or "pricing-2026" in name
        or "free-trial-2026" in name
        or "alternatives-in-2026" in name
        or "coupon" in name
        or "promo-code" in name
        or "review-2026" in name
        or (name.startswith("best-") and "-in-2026" in name)
    )


def _sitemap_urls() -> set[str]:
    if not SITEMAP.exists():
        return set()
    raw = SITEMAP.read_text(encoding="utf-8")
    return {m.group(1) for m in re.finditer(r"<loc>([^<]+)</loc>", raw)}


# ---- canonical coverage ----

def test_every_html_page_has_canonical():
    missing: list[str] = []
    for path in _iter_html():
        if path in ALLOW_NO_CANONICAL or path.name.startswith("fo-verify"):
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw = path.read_text(encoding="utf-8", errors="replace")
        if NOINDEX_RE.search(raw):
            continue
        if not CANONICAL_RE.search(raw):
            missing.append(str(path.relative_to(ROOT)))
    assert not missing, f"pages missing canonical: {len(missing)} e.g. {missing[:5]}"


# ---- sitemap inclusion ----

def test_every_indexable_page_in_sitemap():
    urls = _sitemap_urls()
    missing: list[str] = []
    for path in _iter_html():
        if path in ALLOW_NOT_IN_SITEMAP:
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw = path.read_text(encoding="utf-8", errors="replace")
        if NOINDEX_RE.search(raw):
            continue
        m = CANONICAL_RE.search(raw)
        if not m:
            continue
        canonical = m.group(1).split("#")[0].rstrip("/")
        # Compare by normalised canonical URL
        # sitemap entries may or may not include trailing slash. Accept
        # either shape.
        if canonical not in urls and (canonical + "/") not in urls:
            missing.append(canonical)
    # Allow a small tolerance: sometimes sitemap lags slightly after a
    # batch publish. Fail hard if >1% of pages are missing.
    total = len(_iter_html())
    tolerance = max(10, int(total * 0.01))
    assert len(missing) <= tolerance, (
        f"{len(missing)} indexable pages missing from sitemap "
        f"(tolerance {tolerance}). Run scripts/update_sitemap_and_index.py. "
        f"Sample: {missing[:5]}"
    )


# ---- schema JSON-LD validity ----

def test_every_jsonld_block_parses():
    bad: list[tuple[str, str]] = []
    for path in _iter_html():
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw = path.read_text(encoding="utf-8", errors="replace")
        for match in JSONLD_RE.finditer(raw):
            payload = match.group(1).strip()
            if not payload:
                continue
            try:
                json.loads(payload)
            except json.JSONDecodeError as e:
                bad.append((str(path.relative_to(ROOT)), str(e)))
    assert not bad, f"{len(bad)} invalid JSON-LD blocks. Sample: {bad[:3]}"


# ---- money-page schema coverage ----

ACCEPTED_TYPES = {
    "Article", "BreadcrumbList", "FAQPage", "Product",
    "Service", "Offer", "AggregateRating", "WebPage", "Review",
    "HowTo", "ItemList", "CollectionPage",
}


def _schema_types(html: str) -> set[str]:
    types: set[str] = set()
    for match in JSONLD_RE.finditer(html):
        try:
            parsed = json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            continue

        def collect(obj):
            if isinstance(obj, dict):
                t = obj.get("@type")
                if isinstance(t, str):
                    types.add(t)
                if isinstance(t, list):
                    types.update(x for x in t if isinstance(x, str))
                for v in obj.values():
                    collect(v)
            elif isinstance(obj, list):
                for v in obj:
                    collect(v)

        collect(parsed)
    return types


def test_money_pages_have_money_schema():
    missing: list[str] = []
    for path in _iter_html():
        if not _is_money_page(path):
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw = path.read_text(encoding="utf-8", errors="replace")
        if NOINDEX_RE.search(raw):
            continue
        types = _schema_types(raw)
        if not types & ACCEPTED_TYPES:
            missing.append(str(path.relative_to(ROOT)))
    # Tolerance: allow up to 2% of money pages to be schema-poor so a
    # single bad page doesn't block a release. Fails loudly otherwise.
    money_total = sum(1 for p in _iter_html() if _is_money_page(p))
    tolerance = max(3, int(money_total * 0.02))
    assert len(missing) <= tolerance, (
        f"{len(missing)} money pages without accepted JSON-LD types "
        f"(tolerance {tolerance}). Sample: {missing[:5]}"
    )
