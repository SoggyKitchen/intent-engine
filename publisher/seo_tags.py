import csv
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SEO_DIR = ROOT / "data" / "seo"
OPTIMIZATIONS_CSV = SEO_DIR / "deployed_optimizations.csv"
PATTERNS_CSV = SEO_DIR / "bot_patterns.csv"

STATIC_SEO = {
    "/pages": {
        "title": "SaaS Comparison Library: Pricing, Reviews, Free Trials & Alternatives | SaaSpare",
        "meta_description": (
            "Browse SaaSpare's full SaaS comparison library with pricing guides, reviews, "
            "free trials, promo codes and alternatives for B2B software buyers."
        ),
    }
}

BRAND_FIXES = {
    "1password": "1Password",
    "activecampaign": "ActiveCampaign",
    "ahrefs": "Ahrefs",
    "api": "API",
    "aws": "AWS",
    "brevo": "Brevo",
    "clickup": "ClickUp",
    "copy ai": "Copy.ai",
    "crm": "CRM",
    "docusign": "DocuSign",
    "frase io": "Frase.io",
    "github": "GitHub",
    "google": "Google",
    "hubspot": "HubSpot",
    "jasper ai": "Jasper AI",
    "jira": "Jira",
    "klaviyo": "Klaviyo",
    "mailchimp": "Mailchimp",
    "monday com": "Monday.com",
    "moz": "Moz",
    "nordpass": "NordPass",
    "okta": "Okta",
    "pipedrive": "Pipedrive",
    "quickbooks": "QuickBooks",
    "rankmath": "RankMath",
    "salesforce": "Salesforce",
    "saas": "SaaS",
    "semrush": "Semrush",
    "seo": "SEO",
    "shopify": "Shopify",
    "spyfu": "SpyFu",
    "surfer seo": "Surfer SEO",
    "xero": "Xero",
}


def _clean(value: str) -> str:
    return " ".join((value or "").replace("\n", " ").split())


def _normalize_path(url: str) -> str:
    value = _clean(url)
    if not value:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        value = parsed.path or "/"
    if value.endswith(".html"):
        value = value[:-5]
    value = value.rstrip("/") or "/"
    return value


def _title_case_slug(value: str) -> str:
    label = value.replace("-", " ").replace("_", " ").strip()
    label = re.sub(r"\b20\d{2}\b", "", label)
    label = " ".join(part.capitalize() for part in label.split())
    for wrong, right in BRAND_FIXES.items():
        label = re.sub(rf"\b{re.escape(wrong)}\b", right, label, flags=re.IGNORECASE)
    return _clean(label)


def _category_label(category: str | None) -> str:
    if not category:
        return "Software"
    label = category.replace("_", " ").replace("-", " ")
    return _title_case_slug(label)


def _infer_parts(url_path: str, product_name: str | None) -> tuple[str, str | None]:
    stem = Path(_normalize_path(url_path)).name
    if product_name:
        product = _clean(product_name)
    else:
        product = stem
        product = re.sub(r"-?which-is-better-in-20\d{2}$", "", product)
        product = re.sub(r"^\d+-best-", "", product)
        product = re.sub(r"^best-", "", product)
        product = re.sub(r"-alternatives-in-20\d{2}.*$", "", product)
        product = re.sub(r"-pricing-20\d{2}.*$", "", product)
        product = re.sub(r"-free-trial-20\d{2}.*$", "", product)
        product = re.sub(r"-review-20\d{2}.*$", "", product)
        product = re.sub(r"-(promo-code|coupon-code|promo-codes|discounts).*20\d{2}.*$", "", product)
        product = re.sub(r"^does-", "", product)
        product = re.sub(r"-have-a-free-plan.*$", "", product)
        product = _title_case_slug(product)

    comparison = None
    if "-vs-" in stem:
        left, right = stem.split("-vs-", 1)
        right = re.sub(r"-which-is-better-in-20\d{2}$", "", right)
        comparison = f"{_title_case_slug(left)} vs. {_title_case_slug(right)}"
    return product, comparison


def _match_pattern(stem: str, pattern: str) -> bool:
    p = pattern.lower()
    s = stem.lower()
    if "x-vs-y" in p:
        return "-vs-" in s and "which-is-better" in s
    if "best-x-alternatives" in p:
        return ("best-" in s) and "alternatives" in s
    if "x-pricing" in p:
        return "pricing" in s or "cost" in s
    if "x-free-trial" in p:
        return ("free-trial" in s or "free-tier" in s) and "free-plan" not in s
    if "does-x-have-a-free-plan" in p:
        return s.startswith("does-") and "free-plan" in s
    if "x-review" in p:
        return "review" in s
    if "x-promo-code" in p:
        return "promo" in s or "coupon" in s or "discount" in s
    if "best-x-for-y" in p:
        return s.startswith("best-")
    return p and p in s


@lru_cache(maxsize=1)
def _load_optimizations() -> dict[str, dict[str, str]]:
    optimizations: dict[str, dict[str, str]] = {}
    if not OPTIMIZATIONS_CSV.exists():
        return optimizations
    with OPTIMIZATIONS_CSV.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            path = _normalize_path(row.get("url", ""))
            title = _clean(row.get("page_title", ""))
            meta = _clean(row.get("meta_description", ""))
            if path and title and meta:
                optimizations[path] = {"title": title, "meta_description": meta}
    return optimizations


@lru_cache(maxsize=1)
def _load_patterns() -> list[dict[str, str]]:
    if not PATTERNS_CSV.exists():
        return []
    with PATTERNS_CSV.open(newline="", encoding="utf-8-sig") as fh:
        return [
            {
                "url_pattern": _clean(row.get("url_pattern", "")),
                "title_template": _clean(row.get("title_template", "")),
                "meta_template": _clean(row.get("meta_template", "")),
            }
            for row in csv.DictReader(fh)
            if _clean(row.get("title_template", "")) and _clean(row.get("meta_template", ""))
        ]


def get_seo_tags(
    url_path: str,
    product_name: str | None = None,
    category: str | None = None,
    fallback_title: str | None = None,
    fallback_meta: str | None = None,
) -> dict[str, str]:
    """Return hard-coded OTTO SEO tags first, then pattern-generated tags."""

    normalized = _normalize_path(url_path)
    optimizations = _load_optimizations()
    if normalized in optimizations:
        return optimizations[normalized].copy()
    if normalized in STATIC_SEO:
        return STATIC_SEO[normalized].copy()

    stem = Path(normalized).name
    product, comparison = _infer_parts(normalized, product_name)
    category_title = _category_label(category)
    category_meta = category_title.lower()

    for pattern in _load_patterns():
        if not _match_pattern(stem, pattern["url_pattern"]):
            continue
        x_value = comparison or product or fallback_title or "Product"
        title = pattern["title_template"].replace("X vs. Y", comparison or x_value)
        title = title.replace("X", x_value)
        title = title.replace("Y", category_title)
        title = title.replace("[Category]", category_title)
        meta = pattern["meta_template"].replace("X vs. Y", comparison or x_value)
        meta = meta.replace("X", x_value)
        meta = meta.replace("Y", category_meta)
        meta = meta.replace("[Category]", category_title)
        meta = meta.replace("[category]", category_meta)
        return {"title": _clean(title), "meta_description": _clean(meta)}

    title = _clean(fallback_title or product or "SaaS Comparison")
    meta = _clean(
        fallback_meta
        or f"Compare {title} on SaaSpare. Unbiased reviews, real pricing, free trials, alternatives and expert recommendations."
    )
    if "SaaSpare" not in title:
        title = f"{title} | SaaSpare"
    return {"title": title, "meta_description": meta}


def apply_seo_tags(data: dict, url_path: str, category: str | None = None) -> dict:
    seo = get_seo_tags(
        url_path,
        product_name=None,
        category=category or data.get("vertical"),
        fallback_title=data.get("page_title") or data.get("title"),
        fallback_meta=data.get("meta_description"),
    )
    data["page_title"] = seo["title"].removesuffix(" | SaaSpare")
    data["title"] = data["page_title"]
    data["meta_description"] = seo["meta_description"]
    return data
