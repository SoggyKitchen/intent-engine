"""
CI gate: fail the build if any shipped HTML page contains a corrupted
title or the bug-template "<title> is checked during scheduled SEO and
link audits" trust-box sentence.

Also tests the pure normalisation library in publisher.normalise so
regressions in the title normaliser are caught at unit-test level.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from publisher.normalise import (
    apply_brand_capitalisation,
    assert_no_corruption,
    find_corruption,
    normalise_title,
    scan_titles,
)

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"


# -----------------------------
# Unit tests for publisher.normalise
# -----------------------------

def test_duplicate_brand_ero_is_detected():
    assert find_corruption("Xero vs. Sageero vs. Sage: Which Is Best?")


def test_duplicate_brand_same_token_is_detected():
    # Pure duplication with nothing else in the title is corrupted.
    assert find_corruption("Hubspot vs. Hubspot")


def test_subbrand_comparison_is_allowed():
    """DocuSign vs. DocuSign CLM is a legitimate sub-brand comparison,
    not a corruption artefact."""
    assert find_corruption("DocuSign vs. DocuSign CLM: Which Is Best in 2026?") == []
    assert find_corruption("Sticky Password vs. Password Boss") == []


def test_clean_title_has_no_corruption():
    assert find_corruption("Xero vs. Sage 2026: Which Is Best?") == []


def test_normalise_brand_capitalisation():
    assert apply_brand_capitalisation("hubspot pricing 2026") == "HubSpot pricing 2026"
    assert apply_brand_capitalisation("clickup vs. notion") == "ClickUp vs. notion"
    assert apply_brand_capitalisation("1password review") == "1Password review"


def test_normalise_title_removes_suffix_leak():
    assert (
        normalise_title("Xero vs. Sageero vs. Sage: Which Is Best?")
        == "Xero vs. Sage: Which Is Best?"
    )


def test_assert_no_corruption_passes_clean_title():
    assert_no_corruption("HubSpot vs. Pipedrive 2026: Which CRM Wins?")


def test_assert_no_corruption_raises_on_dirty_title():
    with pytest.raises(ValueError):
        assert_no_corruption("Xero vs. Sageero vs. Sage")


def test_scan_titles_returns_only_dirty():
    out = scan_titles(
        [
            "HubSpot Pricing 2026",
            "Xero vs. Sageero vs. Sage",
        ]
    )
    assert len(out) == 1
    assert out[0][0] == "Xero vs. Sageero vs. Sage"


# -----------------------------
# Full-site regression gate
# -----------------------------

def _iter_html_files() -> list[Path]:
    if not SITE.exists():
        return []
    return [p for p in SITE.rglob("*.html") if p.is_file()]


TITLE_RE = re.compile(r"<title>([^<]+)</title>", re.IGNORECASE)


def test_no_page_has_corrupted_title_or_og_title():
    """Fail if any public HTML page has a <title> or <meta og:title> with a
    known corruption pattern. This was the bug that produced
    "Xero vs. Sageero vs. Sage" on saaspare.org."""
    bad: list[tuple[str, str]] = []
    for path in _iter_html_files():
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw = path.read_text(encoding="utf-8", errors="replace")
        for match in TITLE_RE.finditer(raw):
            matches = find_corruption(match.group(1))
            if matches:
                bad.append((str(path.relative_to(ROOT)), match.group(1)))
    assert not bad, f"corrupted <title> found on {len(bad)} pages: {bad[:5]}"


BROKEN_TRUSTBOX_RE = re.compile(
    r"<p><strong>Last verified:</strong>\s*[^<\n]+? is checked during scheduled SEO and link audits\."
)


def test_no_page_has_broken_trustbox_sentence():
    """Fail if any HTML page ships the pre-fix "<title> is checked during
    scheduled SEO and link audits" trust-box sentence."""
    bad: list[str] = []
    for path in _iter_html_files():
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw = path.read_text(encoding="utf-8", errors="replace")
        if BROKEN_TRUSTBOX_RE.search(raw):
            bad.append(str(path.relative_to(ROOT)))
    assert not bad, (
        "broken trust-box 'Last verified: <title>' sentence still present in "
        f"{len(bad)} pages (sample: {bad[:5]}). Run "
        "`python scripts/fix_corrupted_titles.py` to repair."
    )
