"""Tests for the autonomous-operator only-improve guards."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "seo"))

import guards  # noqa: E402


# ── The real regression that triggered this work ─────────────────────────────
# apply-safe wanted to replace this tuned title with a generic templated one.
TUNED_TITLE = "Zoom vs Loom (2026): Honest Verdict & Who Wins"
GENERIC_TITLE = "Zoom vs. Loom: Which Software Is Best in 2026? | SaaSpare"

TUNED_META = (
    "Updated June 2026. Zoom vs Loom compared for 2026 — pricing, features, "
    "and which one wins for your use case. Score-based verdict, no paid placements."
)
GENERIC_META = (
    "Compare Zoom vs. Loom in 2026: pricing, features, free trials, and real "
    "user verdict. Find out which is right for your team."
)


def test_tuned_title_scores_higher_than_generic():
    assert guards.title_quality_score(TUNED_TITLE) > guards.title_quality_score(GENERIC_TITLE)


def test_generic_title_detected():
    assert guards.is_generic(GENERIC_TITLE)
    assert not guards.is_generic(TUNED_TITLE)


def test_never_replace_tuned_with_generic_title():
    # The core guard: this exact swap must be blocked.
    assert guards.should_replace(TUNED_TITLE, GENERIC_TITLE, "title") is False


def test_never_replace_tuned_with_generic_meta():
    assert guards.should_replace(TUNED_META, GENERIC_META, "meta") is False


def test_replace_empty_title():
    assert guards.should_replace("", GENERIC_TITLE, "title") is True
    assert guards.should_replace(None, "Anything Real 2026", "title") is True


def test_no_candidate_never_replaces():
    assert guards.should_replace(TUNED_TITLE, "", "title") is False
    assert guards.should_replace(TUNED_TITLE, None, "title") is False


def test_identical_is_noop():
    assert guards.should_replace(TUNED_TITLE, TUNED_TITLE, "title") is False


def test_weak_title_gets_improved():
    weak = "Zoom Loom"  # too short, no year, no signal
    better = "Zoom vs Loom 2026: Honest Verdict After Testing"
    assert guards.should_replace(weak, better, "title") is True


def test_strong_title_needs_clear_win_to_replace():
    # A marginally different but not clearly-better candidate must NOT replace.
    a = "Ramp Pricing 2026: Every Change, Real Cost & June Update"
    b = "Ramp Pricing 2026: Costs and Updates Explained"  # weaker
    assert guards.should_replace(a, b, "title") is False


def test_premium_page_skipped():
    assert guards.is_premium_page(
        title=TUNED_TITLE,
        meta=TUNED_META,
        word_count=900,
        has_faq_schema=True,
    ) is True


def test_thin_or_generic_page_not_premium():
    assert guards.is_premium_page(GENERIC_TITLE, GENERIC_META, 900, True) is False
    # Strong meta+title but thin content → not premium.
    assert guards.is_premium_page(TUNED_TITLE, TUNED_META, 200, True) is False


# ── Real downgrade pairs caught in the live apply-safe diff ───────────────────
REAL_DOWNGRADES = [
    ("1Password Coupon 2026 (Verified June 2026) — Real Working Codes",
     "1Password Promo Codes & Discounts 2026 | SaaSpare"),
    ("Asana Pricing History 2026: Every Price Change Tracked — SaaSpare",
     "Asana Pricing History Pricing 2026: Plans & Costs | SaaSpare"),
    ("BigCommerce Pricing 2026 (Verified June 2026) — Real Costs + Hidden Fees",
     "BigCommerce Pricing 2026: Plans & Costs | SaaSpare"),
    ("1Password vs Bitwarden — Which Is Better in 2026? [Full Comparison]",
     "1Password vs. Bitwarden in 2026: Which Password Manager Is Best? | SaaSpare"),
    ("Best Asana Alternatives 2026: Cheaper & Better Options — SaaSpare",
     "Best Asana Alternatives 2026: Free & Paid Options | SaaSpare"),
]


def test_template_candidates_detected_as_generic():
    for _cur, cand in REAL_DOWNGRADES:
        assert guards.is_generic(cand), f"should be generic: {cand}"


def test_no_real_downgrade_is_applied():
    for cur, cand in REAL_DOWNGRADES:
        assert guards.should_replace(cur, cand, "title") is False, f"downgrade slipped: {cur!r} -> {cand!r}"


def test_generic_template_never_overwrites_utility_page():
    # Real nonsense the operator produced on preview/utility pages.
    cases = [
        ("Page not found | SaaSpare",
         "V3 Preview 404 Review 2026: Honest Pricing & Verdict | SaaSpare"),
        ("Privacy Policy | SaaSpare",
         "V3 Preview Privacy Review 2026: Honest Pricing & Verdict | SaaSpare"),
        ("Contact SaaSpare | SaaSpare",
         "V3 Preview Contact Review 2026: Honest Pricing & Verdict | SaaSpare"),
    ]
    for cur, cand in cases:
        assert guards.should_replace(cur, cand, "title") is False, f"{cur!r} -> {cand!r}"


def test_generic_template_fills_empty_title():
    # A template is acceptable only when there's literally no title.
    assert guards.should_replace("", "X Pricing 2026: Plans & Costs | SaaSpare", "title") is True


def test_year_and_signal_boost_score():
    no_year = "Notion Pricing Explained"
    with_year = "Notion Pricing 2026 Explained: Real Cost"
    assert guards.title_quality_score(with_year) > guards.title_quality_score(no_year)
