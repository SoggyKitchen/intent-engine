import json
import re
from pathlib import Path

from slugify import slugify

from publisher.affiliate_registry import get_all_redirects, get_go_url, get_network_signups
from publisher.pages_deploy import _detect_page_type

_SKIP_PAGE_STEMS = {"index", "thanks", "verification"}
_TITLE_RE = re.compile(r"<title>([^<]+)</title>", re.IGNORECASE)


def _page_files(site_dir: str | Path = "site/pages") -> list[Path]:
    base = Path(site_dir)
    if not base.exists():
        return []
    return [
        path for path in sorted(base.glob("*.html"))
        if path.stem not in _SKIP_PAGE_STEMS
    ]


def _page_title(path: Path) -> str:
    try:
        html = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return path.stem
    match = _TITLE_RE.search(html)
    if not match:
        return path.stem
    return match.group(1).replace("| SaaSpare", "").strip() or path.stem


def _pages_without_go_cta(page_files: list[Path]) -> list[dict]:
    missing: list[dict] = []
    for path in page_files:
        html = path.read_text(encoding="utf-8", errors="ignore")
        if "/go/" in html:
            continue
        missing.append({
            "slug": path.stem,
            "title": _page_title(path),
            "page_type": _detect_page_type(path.stem),
            "path": str(path),
        })
    return missing


def _imported_affiliate_count(path: str | Path = "data/affiliate_links.json") -> int:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return 0
    advertisers = payload.get("advertisers", {})
    return len(advertisers) if isinstance(advertisers, dict) else 0


def _tool_page_counts(page_files: list[Path], tool_targets: list[tuple[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    stems = [path.stem.lower() for path in page_files]
    for tool, _vertical in tool_targets:
        slug = slugify(tool)
        count = sum(1 for stem in stems if slug and slug in stem)
        if count:
            counts[tool] = count
    return counts


def _dedupe_targets(*groups: list[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[str] = set()
    items: list[tuple[str, str]] = []
    for group in groups:
        for tool, vertical in group:
            key = slugify(tool)
            if key in seen:
                continue
            seen.add(key)
            items.append((tool, vertical))
    return items


def collect_profit_audit(
    site_dir: str | Path = "site/pages",
    pricing_targets: list[tuple[str, str]] | None = None,
    coupon_targets: list[tuple[str, str]] | None = None,
    review_targets: list[tuple[str, str]] | None = None,
    free_plan_targets: list[tuple[str, str]] | None = None,
    max_gap_items: int = 12,
) -> dict:
    if pricing_targets is None or coupon_targets is None or review_targets is None or free_plan_targets is None:
        from outputs.programmatic import (
            FREE_PLAN_TARGETS,
            HIGH_VALUE_COUPON_TARGETS,
            HIGH_VALUE_PRICING_TARGETS,
            HIGH_VALUE_REVIEW_TARGETS,
        )
        pricing_targets = pricing_targets or HIGH_VALUE_PRICING_TARGETS
        coupon_targets = coupon_targets or HIGH_VALUE_COUPON_TARGETS
        review_targets = review_targets or HIGH_VALUE_REVIEW_TARGETS
        free_plan_targets = free_plan_targets or FREE_PLAN_TARGETS

    page_files = _page_files(site_dir)
    missing_ctas = _pages_without_go_cta(page_files)
    redirect_count = len(get_all_redirects())
    imported_affiliates = _imported_affiliate_count()

    all_targets = _dedupe_targets(pricing_targets, coupon_targets, review_targets, free_plan_targets)
    page_counts = _tool_page_counts(page_files, all_targets)

    missing_partner_targets: list[dict] = []
    for tool, vertical in all_targets:
        if get_go_url(tool):
            continue
        missing_partner_targets.append({
            "tool": tool,
            "vertical": vertical,
            "page_count": page_counts.get(tool, 0),
        })
    missing_partner_targets.sort(key=lambda item: (-item["page_count"], item["tool"]))

    missing_coupon_targets: list[dict] = []
    for tool, vertical in coupon_targets:
        if get_go_url(tool, page_type="coupon"):
            continue
        missing_coupon_targets.append({
            "tool": tool,
            "vertical": vertical,
            "page_count": page_counts.get(tool, 0),
        })
    missing_coupon_targets.sort(key=lambda item: (-item["page_count"], item["tool"]))

    page_count = len(page_files)
    pages_with_cta = page_count - len(missing_ctas)
    cta_coverage_pct = round((pages_with_cta / page_count) * 100, 1) if page_count else 0.0

    return {
        "page_count": page_count,
        "pages_with_cta": pages_with_cta,
        "cta_coverage_pct": cta_coverage_pct,
        "pages_without_go_cta": missing_ctas[:max_gap_items],
        "pages_without_go_cta_total": len(missing_ctas),
        "redirect_count": redirect_count,
        "imported_affiliate_count": imported_affiliates,
        "missing_partner_targets": missing_partner_targets[:max_gap_items],
        "missing_partner_targets_total": len(missing_partner_targets),
        "missing_coupon_targets": missing_coupon_targets[:max_gap_items],
        "missing_coupon_targets_total": len(missing_coupon_targets),
        "network_signups": get_network_signups(),
    }
