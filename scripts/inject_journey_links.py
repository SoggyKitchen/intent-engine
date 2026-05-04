"""
Intent-weighted internal-link engine for SaaSpare buyer pages.

The existing "Related Comparisons" blocks on comparison pages only link
to sibling comparisons. That keeps readers inside the same stage of the
buyer journey (evaluate) and misses the natural next steps:
    comparison -> pricing -> free trial -> alternatives -> coupon -> ROI / shortlist.

This script scans the site, indexes every buyer page by (brand, type),
and injects a "Continue your evaluation" block on each money page with
3-8 stage-relevant next-step links for the brands that page covers.
It is idempotent (marked with data-saaspare-journey-links="v1") and
safe to re-run after new pages are published.

Usage:
    python scripts/inject_journey_links.py           # apply
    python scripts/inject_journey_links.py --check   # report only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
PAGES = SITE / "pages"
OUT = ROOT / "outputs" / "seo" / "journey-links.json"
OUT.parent.mkdir(parents=True, exist_ok=True)


# --- slug parsing ---
# Keep brand parsing permissive: handles multi-word brands like
# "monday-com", "1password-business", "github-copilot".

COMPARISON_RE = re.compile(r"^(?P<a>.+?)-vs-(?P<b>.+?)-which-is-better-in-2026$")
PRICING_RE = re.compile(r"^(?P<brand>.+?)-pricing-2026-plans-costs-what-you-actually-pay$")
TRIAL_RE = re.compile(r"^(?P<brand>.+?)-free-trial-2026-how-to-get-it-step-by-step$")
REVIEW_RE = re.compile(r"^(?P<brand>.+?)-review-2026-is-it-worth-it-honest-verdict$")
ALT_RE = re.compile(r"^(?:\d+-)?best-(?P<brand>.+?)-alternatives-in-2026.*$")
COUPON_RE = re.compile(r"^(?P<brand>.+?)-(?:coupon-code-promo-codes-2026-verified-discounts|promo-code-2026-discounts-deals-that-actually-work)$")


def slug_to_brand(slug: str) -> str:
    # "monday-com" -> "monday.com" for display purposes is handled
    # elsewhere; for URL-matching we keep the slug form.
    return slug


def pretty_brand(slug: str) -> str:
    """Turn a slug brand into a display brand, e.g. "monday-com" -> "Monday.com"."""
    from publisher.normalise import apply_brand_capitalisation

    special = {
        "monday-com": "Monday.com",
        "zoho-crm": "Zoho CRM",
        "remote-com": "Remote.com",
        "copy-ai": "Copy.ai",
        "frase-io": "Frase.io",
        "riverside-fm": "Riverside.fm",
        "cloudflare-pages": "Cloudflare Pages",
        "google-cloud": "Google Cloud",
        "1password-business": "1Password Business",
        "github-copilot": "GitHub Copilot",
        "rankmath-pro": "RankMath Pro",
        "surfer-seo": "Surfer SEO",
        "sticky-password": "Sticky Password",
        "password-boss": "Password Boss",
        "keeper-security": "Keeper Security",
    }
    if slug in special:
        return special[slug]
    words = slug.replace("-", " ").title()
    return apply_brand_capitalisation(words)


def page_type_for(filename: str) -> tuple[str, list[str]] | None:
    name = filename.replace(".html", "")
    if m := COMPARISON_RE.match(name):
        return "comparison", [m.group("a"), m.group("b")]
    if m := PRICING_RE.match(name):
        return "pricing", [m.group("brand")]
    if m := TRIAL_RE.match(name):
        return "free_trial", [m.group("brand")]
    if m := REVIEW_RE.match(name):
        return "review", [m.group("brand")]
    if m := ALT_RE.match(name):
        return "alternatives", [m.group("brand")]
    if m := COUPON_RE.match(name):
        return "coupon", [m.group("brand")]
    return None


def build_index() -> dict[tuple[str, str], str]:
    """Return {(brand_slug, page_type): url_path}."""
    index: dict[tuple[str, str], str] = {}
    for path in PAGES.glob("*.html"):
        result = page_type_for(path.name)
        if result is None:
            continue
        page_type, brands = result
        if page_type == "comparison":
            continue  # handled separately as sibling links
        for brand in brands:
            key = (brand, page_type)
            if key not in index:
                index[key] = f"/pages/{path.stem}"
    return index


# Journey scoring: from current page stage -> preferred next stages.
NEXT_STAGE_PRIORITY: dict[str, list[str]] = {
    "comparison": ["pricing", "free_trial", "alternatives", "coupon", "review"],
    "pricing": ["free_trial", "coupon", "alternatives", "review"],
    "review": ["pricing", "free_trial", "alternatives"],
    "free_trial": ["pricing", "alternatives", "coupon"],
    "alternatives": ["pricing", "free_trial", "coupon"],
    "coupon": ["pricing", "free_trial", "review"],
}

STAGE_LABEL = {
    "pricing": "pricing breakdown",
    "free_trial": "free trial guide",
    "alternatives": "alternatives",
    "coupon": "coupons &amp; deals",
    "review": "full review",
}


def _brand_aliases(brand: str) -> list[str]:
    """Generate progressively shorter variants so that e.g.
    "1password-business" can find the "1password" pricing page when the
    tier-specific page is not published."""
    variants = [brand]
    parts = brand.split("-")
    while len(parts) > 1:
        parts = parts[:-1]
        variants.append("-".join(parts))
    # De-duplicate preserving order
    seen: set[str] = set()
    out: list[str] = []
    for v in variants:
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def next_step_links(
    current_type: str,
    brands: list[str],
    index: dict[tuple[str, str], str],
    max_links: int = 6,
) -> list[tuple[str, str]]:
    """Return a list of (href, label) for the next steps from this page."""
    results: list[tuple[str, str]] = []
    seen_urls: set[str] = set()
    for brand in brands:
        brand_display = pretty_brand(brand)
        for stage in NEXT_STAGE_PRIORITY.get(current_type, []):
            url = None
            matched_alias = None
            for alias in _brand_aliases(brand):
                if (alias, stage) in index:
                    url = index[(alias, stage)]
                    matched_alias = alias
                    break
            if url and url not in seen_urls:
                seen_urls.add(url)
                # Use the matched alias's pretty name if different, to
                # avoid "1Password Business pricing" linking to the
                # /1password-pricing page.
                if matched_alias and matched_alias != brand:
                    display = pretty_brand(matched_alias)
                else:
                    display = brand_display
                label = f"{display} {STAGE_LABEL[stage]}"
                results.append((url, label))
                if len(results) >= max_links:
                    return results
    # always offer shortlist + ROI tool as universal next steps
    if len(results) < max_links:
        results.append(("/shortlist", "Build a free shortlist"))
    if len(results) < max_links:
        results.append(
            ("/pages/saas-roi-calculator", "Run the SaaS ROI calculator")
        )
    return results[:max_links]


BLOCK_SENTINEL = 'data-saaspare-journey-links="v1"'


def render_block(links: list[tuple[str, str]]) -> str:
    items = "".join(
        f'<a href="{href}" data-journey-link>{label}</a>' for href, label in links
    )
    return (
        f'\n<section class="journey-links section" '
        f'{BLOCK_SENTINEL} data-seo-related>\n'
        f'  <h3>Continue your evaluation</h3>\n'
        f'  {items}\n'
        f'</section>\n'
    )


def inject_block(html: str, block: str) -> str:
    """Insert the block before the trust box, or before </footer>/</body>."""
    if "seo-trustbox" in html:
        return re.sub(
            r'(<section class="seo-trustbox)',
            block + r"\1",
            html,
            count=1,
        )
    if "</footer>" in html:
        return html.replace("<footer>", block + "\n<footer>", 1)
    if "</body>" in html:
        return html.replace("</body>", block + "\n</body>", 1)
    return html + block


def process_page(
    path: Path,
    index: dict[tuple[str, str], str],
    dry_run: bool,
) -> dict | None:
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw = path.read_text(encoding="utf-8", errors="replace")
    if BLOCK_SENTINEL in raw:
        return None
    result = page_type_for(path.name)
    if result is None:
        return None
    current_type, brands = result
    links = next_step_links(current_type, brands, index)
    if not links:
        return None
    block = render_block(links)
    new_html = inject_block(raw, block)
    if new_html == raw:
        return None
    if not dry_run:
        path.write_text(new_html, encoding="utf-8", newline="")
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "page_type": current_type,
        "brands": brands,
        "links_added": [lbl for _, lbl in links],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="report only")
    args = parser.parse_args()

    index = build_index()
    # Per-brand page_type stats
    per_brand: dict[str, set[str]] = defaultdict(set)
    for (brand, pt), _ in index.items():
        per_brand[brand].add(pt)

    changes: list[dict] = []
    pages = list(PAGES.glob("*.html"))
    for p in pages:
        r = process_page(p, index, dry_run=args.check)
        if r is not None:
            changes.append(r)

    report = {
        "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "pages_scanned": len(pages),
        "index_size": len(index),
        "brands_covered": len(per_brand),
        "pages_updated": len(changes),
        "mode": "check" if args.check else "apply",
        "sample_change": changes[0] if changes else None,
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    sys.exit(main())
