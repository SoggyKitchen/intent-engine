"""
Content-gap finder scoped to programs that ALREADY earn commission (status=EARNING
in revenue_intelligence.PROGRAM_VALUE), so new-content sessions build pages for
tools that pay, before spending effort on PLACEHOLDER/LOCKED programs.

revenue_intelligence.py ranks EXISTING pages by $ opportunity using live GSC data.
It cannot recommend a page that doesn't exist yet (no impressions to rank on).
This script closes that gap: for each earning program, check which standard
page types are missing entirely, so they can be built first.

Run: uv run python scripts/seo/earning_program_gaps.py
Output: seo/reports/earning-program-content-gaps.md
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from revenue_intelligence import PROGRAM_VALUE  # noqa: E402

PAGES = Path("site/pages")
REPORT = Path("seo/reports/earning-program-content-gaps.md")

# Standard buyer-intent page types this site produces per tool, and the slug
# suffix pattern used to detect an existing page (checked as substring match
# against the program slug prefix).
PAGE_TYPES = [
    ("Pricing breakdown", "-pricing-2026-plans-costs-what-you-actually-pay"),
    ("Pricing history",   "-pricing-history-2026"),
    ("Review/verdict",    "-review-2026-is-it-worth-it-honest-verdict"),
    ("Coupon/promo code", "-coupon-code-promo-codes-2026-verified-discounts"),
    ("Free trial guide",  "-free-trial-2026-how-to-get-it-step-by-step"),
    ("Free plan check",   "does-{slug}-have-a-free-plan-2026-full-breakdown"),
    ("Alternatives list", "best-{slug}-alternatives-in-2026-free-paid"),
]


def existing_slugs() -> set[str]:
    return {p.stem for p in PAGES.glob("*.html")}


def find_gaps():
    slugs = existing_slugs()
    earning = {k: v for k, v in PROGRAM_VALUE.items() if v["status"] == "EARNING"}
    rows = []
    for slug, prog in sorted(earning.items(), key=lambda kv: -kv[1]["value_usd"]):
        missing = []
        for label, pattern in PAGE_TYPES:
            target = pattern.format(slug=slug) if "{slug}" in pattern else f"{slug}{pattern}"
            if target not in slugs:
                missing.append(label)
        vs_count = sum(1 for s in slugs if s.startswith(f"{slug}-vs-") or f"-vs-{slug}-" in s)
        rows.append((slug, prog, missing, vs_count))
    return rows


def main():
    rows = find_gaps()
    lines = [
        "# Earning-Program Content Gaps",
        "",
        "New-page priority list, scoped to programs that ALREADY earn commission "
        "(status=EARNING in `revenue_intelligence.PROGRAM_VALUE`). Build these before "
        "spending effort on PLACEHOLDER/LOCKED programs — every page here can earn "
        "the day it's indexed, no approval wait required.",
        "",
        "Dollar values are MODELLED commission-per-conversion benchmarks (see CLAUDE.md), "
        "not live earnings.",
        "",
    ]
    total_gaps = 0
    for slug, prog, missing, vs_count in rows:
        total_gaps += len(missing)
        flag = " ⚠️ ZERO PAGES" if vs_count == 0 and missing == [t[0] for t in PAGE_TYPES] else ""
        lines.append(f"## {prog['name']} — ${prog['value_usd']}/conv ({prog['network']}){flag}")
        lines.append(f"- {vs_count} head-to-head comparison pages live")
        if missing:
            lines.append(f"- **Missing page types:** {', '.join(missing)}")
        else:
            lines.append("- All standard page types exist — gap is comparison coverage, not core pages")
        lines.append("")
    lines.append(f"**Total missing standard pages across earning programs: {total_gaps}**")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"earning_program_gaps: {len(rows)} earning programs scanned, {total_gaps} missing pages -> {REPORT}")


if __name__ == "__main__":
    main()
