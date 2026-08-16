"""
Fix CTR batch 4 — revenue-hunter 2026-08-16

Target pages from data/gsc_pages.csv (high impressions, low CTR):
- ramp-pricing-2026        1687 impr, pos 10.2, 0.59% CTR
- mixpanel-pricing-2026     742 impr, pos 13.7, 0.00% CTR
- does-notion-free-plan     557 impr, pos  9.4, 0.00% CTR

Strategy: at pos 7-14 with near-0 CTR, AI Overviews answer the basic question.
Beat them by making the title promise decision-helping specifics:
exact limits, month-named update, "when to upgrade" framing.

Ramp: "change [month] 2026" queries drive 400+ impressions — move update signal
forward in the title. Notion: "limits 2026" variants need that keyword in title.
Mixpanel: page 2 position means title must earn a back-of-page click.
"""
import re
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
TODAY = date.today().isoformat()


def _patch(p, title=None, og_title=None, meta_desc=None):
    if not p.exists():
        print(f"  SKIP: {p.name} not found")
        return False
    html = p.read_text(encoding="utf-8")
    if title:
        html = re.sub(r'<title>[^<]+</title>', f'<title>{title}</title>', html)
    if og_title:
        html = re.sub(
            r'(<meta property="og:title" content=")[^"]*(")',
            rf'\g<1>{og_title}\2', html,
        )
    if meta_desc:
        html = re.sub(
            r'<meta name="description" content="[^"]*">',
            f'<meta name="description" content="{meta_desc}">',
            html,
        )
    html = re.sub(r'"dateModified":\s*"[^"]*"', f'"dateModified": "{TODAY}"', html)
    p.write_text(html, encoding="utf-8")
    print(f"  FIXED: {p.name}")
    return True


def main():
    print(f"CTR batch 4 fixes ({TODAY})...\n")

    # 1. Ramp pricing — 1687 impr, pos 10.2, 0.59% CTR
    # Top queries: "ramp pricing change may 2026" (279 imp), "ramp pricing change april 2026" (141 imp)
    # "ramp pricing change june 2026" at pos 3.7 but 0 clicks → AI Overview eating those clicks.
    # Move [August Update] forward so freshness signal beats cached AI results.
    _patch(
        PAGES / "ramp-pricing-2026-plans-costs-what-you-actually-pay.html",
        title="Ramp Pricing 2026 [August Update]: Every Change Logged — Free Card to $12–15/User",
        og_title="Ramp Pricing 2026 [August Update]: Every Plan Change, Bill Pay Fees & Real Cost",
        meta_desc=(
            "Ramp Core card = $0 forever. Plus = $12/user/mo (annual) or $15/user/mo (monthly). "
            "Bill Pay fee tiers added June 2026. Every pricing change tracked with exact dates and source. "
            "Updated August 2026."
        ),
    )

    # 2. Mixpanel pricing — 742 impr, pos 13.7, 0.00% CTR
    # Page 2 result needs a title that earns back-of-page clicks.
    # "mixpanel pricing official 2026" at pos 8.71 shows intent: people want authoritative data.
    # Lead with the specifics (20M events) + the pain point (event-volume cliff).
    _patch(
        PAGES / "mixpanel-pricing-2026-plans-costs-what-you-actually-pay.html",
        title="Mixpanel Pricing 2026 [August]: Free 20M Events → $28/mo — Event Limits & Hidden Costs",
        og_title="Mixpanel Pricing 2026: Free → $28/mo Growth — The Event-Volume Cliff Explained",
        meta_desc=(
            "Updated August 2026. Mixpanel pricing: Free (20M events/mo, 90-day retention), "
            "Growth from $28/mo (100M events, annual), Enterprise custom. "
            "The event-volume cliff that catches fast-scaling teams — and the cheapest way past it."
        ),
    )

    # 3. Notion free plan — 557 impr, pos 9.4, 0.00% CTR
    # Top queries: "notion free plan limits 2026" (pos 11), "notion free plan block limit 2026" (pos 9.69)
    # "Limits" is the dominant search term — add it to title.
    # 0% CTR at pos 9.4 suggests AI Overview answers the basic question; title must promise more specifics.
    _patch(
        PAGES / "does-notion-have-a-free-plan-2026-full-breakdown.html",
        title="Notion Free Plan Limits 2026: 10-Guest Cap, 7-Day History & What's Actually Blocked [August]",
        og_title="Notion Free Plan Limits 2026: 10 Guests, 7-Day History — Full Breakdown",
        meta_desc=(
            "Updated August 2026. Notion free plan limits: 10-guest cap, 7-day version history, "
            "no analytics dashboard, no SAML SSO. Unlimited blocks and pages. "
            "Exactly which features you lose vs Plus ($10/user/mo) — and when the cap actually bites."
        ),
    )

    print("\nDone.")


if __name__ == "__main__":
    main()
