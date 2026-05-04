"""
Canonical KPI sync for SaaSpare public pages.

Reads data/public_kpis.json and rewrites the inconsistent 986/990/1009
mentions scattered across site/index.html, site/about.html,
site/media-kit.html and site/pages/index.html with a single, accurate,
defensible set of numbers.

Also recomputes the true page counts from the filesystem so the
"source of truth" is always based on what is actually shipped.
"""
from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
KPI_FILE = ROOT / "data" / "public_kpis.json"

# Files we will normalise
TARGETS = [
    SITE / "index.html",
    SITE / "about.html",
    SITE / "media-kit.html",
    SITE / "pages" / "index.html",
]


def count_pages() -> dict[str, int]:
    pages_dir = SITE / "pages"
    all_pages = [
        p
        for p in pages_dir.glob("*.html")
        if p.is_file() and p.name != "index.html"
    ]
    names = [p.name for p in all_pages]

    def _count(predicate) -> int:
        return sum(1 for n in names if predicate(n))

    return {
        "total_buyer_pages": len(all_pages),
        "comparison_pages": _count(lambda n: "-vs-" in n and "which-is-better" in n),
        "pricing_pages": _count(lambda n: "pricing-2026" in n),
        "free_trial_pages": _count(lambda n: "free-trial-2026" in n),
        "alternatives_pages": _count(lambda n: "alternatives-in-2026" in n),
        "coupon_pages": _count(lambda n: "coupon" in n or "promo-code" in n),
        "review_pages": _count(lambda n: "review-2026" in n),
        "verticals": 16,
    }


def with_thousands(n: int) -> str:
    return f"{n:,}"


def build_display_strings(counts: dict[str, int]) -> dict[str, str]:
    total = counts["total_buyer_pages"]
    cmp_ = counts["comparison_pages"]
    return {
        "badge_live": f"{with_thousands(total)} buyer pages live",
        "stat_buyer_pages": f"{with_thousands(total)}+",
        "stat_verticals": "16",
        "hero_headline_pages": f"{with_thousands(total)} comparison, pricing, review, trial, and coupon pages across 16 verticals",
        "library_stat_pages": f"{with_thousands(total)} buyer pages",
        "media_kit_indexed": f"{with_thousands(total)}+ indexed pages",
        "about_stat_pages": f"{with_thousands(total)}+ comparison, pricing, review, trial, alternatives, and coupon pages",
        "comparison_count": f"{with_thousands(cmp_)}+ side-by-side comparisons",
    }


def update_kpi_file(counts: dict[str, int], display: dict[str, str]) -> None:
    KPI_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_comment": "Single source of truth for public-facing KPI counts. Regenerate via scripts/sync_public_kpis.py.",
        "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "page_counts": counts,
        "display_strings": display,
    }
    KPI_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


# Rewrite rules for the HTML surfaces. Each entry is (regex, replacement)
# applied in order. Kept conservative so we only match the specific stat
# strings we mean to change.
def rewrite_html(html: str, counts: dict[str, int], display: dict[str, str]) -> str:
    total = counts["total_buyer_pages"]
    cmp_ = counts["comparison_pages"]
    total_fmt = with_thousands(total)
    # Use a sentinel so later rules don't re-match the value we just inserted
    TOTAL_TOKEN = "\u0000BUYER_PAGES_TOTAL\u0000"

    # "NNN comparisons live" (homepage badge)
    html = re.sub(
        r"\b(\d{1,3}(?:,\d{3})*|\d{3,5})\s+comparisons live\b",
        f"{TOTAL_TOKEN} buyer pages live",
        html,
    )

    # "NNN buyer pages" (homepage badge / library)
    html = re.sub(
        r"\b(\d{1,3}(?:,\d{3})*|\d{3,5})\s+buyer pages\b",
        f"{TOTAL_TOKEN} buyer pages",
        html,
    )

    # data-count="986" on homepage
    html = re.sub(
        r'data-count="\d{3,5}"(?=\s+id="stat-pages")',
        f'data-count="{total}"',
        html,
    )

    # Visible span integer that follows data-count="...", e.g.
    # <span class="stat-val" data-count="1012" id="stat-pages">986<span>+</span></span>
    # We need to rewrite that visible "986" as "1,012" so JS animation
    # lands on the right number and the pre-JS fallback also looks right.
    html = re.sub(
        r'(data-count="\d{3,5}"\s+id="stat-pages">)\s*[\d,]+(\s*<span>\+)',
        lambda m: m.group(1) + total_fmt + m.group(2),
        html,
    )

    # "986+" or "990+" standalone inline text
    html = re.sub(r"\b(98[0-9]|99[0-9]|1009|1010|1011|1012)\+ comparison pages\b",
                  f"{TOTAL_TOKEN}+ comparison, pricing, review and trial pages",
                  html)

    # Library hero headline "1009 comparison, pricing..."
    html = re.sub(r"\b(98[0-9]|99[0-9]|1009|1010|1011|1012)\s+comparison,\s*pricing",
                  f"{TOTAL_TOKEN} comparison, pricing",
                  html)

    # Body: "986+ comparison pages across 16 verticals"
    html = re.sub(
        r"Pick from\s+(\d{3,5})\+\s+comparison pages across (\d+)\s+verticals\.",
        f"Pick from {TOTAL_TOKEN}+ buyer pages across 16 verticals.",
        html,
    )

    # Media kit: "297 indexed pages"
    html = re.sub(
        r"<div class=\"stat-num\">\d{3,5}\+?</div><div class=\"stat-label\">Indexed Pages</div>",
        f'<div class="stat-num">{TOTAL_TOKEN}+</div><div class="stat-label">Indexed Pages</div>',
        html,
    )

    # Also normalise "297 indexed" in plain text if it appears
    html = re.sub(
        r"\b(29[0-9]|30[0-9])\+?\s+indexed pages\b",
        f"{TOTAL_TOKEN}+ indexed pages",
        html,
        flags=re.IGNORECASE,
    )

    # Media kit: risky "7m+ Avg Session Duration" — replace with a defensible
    # metric. We swap it for "16 SaaS verticals covered" (publicly verifiable
    # by anyone who visits the site) rather than an unauditable time stat.
    html = re.sub(
        r"<div class=\"stat-num\">7m\+?</div><div class=\"stat-label\">Avg Session Duration</div>",
        '<div class="stat-num">16</div><div class="stat-label">SaaS verticals covered</div>',
        html,
    )

    # Substitute sentinel with the real number LAST so the value we insert
    # never matches any earlier rule.
    return html.replace(TOTAL_TOKEN, total_fmt)


def main() -> None:
    counts = count_pages()
    display = build_display_strings(counts)
    update_kpi_file(counts, display)

    changed: list[str] = []
    for path in TARGETS:
        if not path.exists():
            continue
        before = path.read_text(encoding="utf-8")
        after = rewrite_html(before, counts, display)
        if after != before:
            path.write_text(after, encoding="utf-8", newline="")
            changed.append(str(path.relative_to(ROOT)).replace("\\", "/"))
    print(
        "canonical_kpis=", json.dumps(counts), "changed=", changed, sep="\n"
    )


if __name__ == "__main__":
    main()
