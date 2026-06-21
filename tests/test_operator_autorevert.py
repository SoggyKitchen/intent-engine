"""Tests for the autonomous-operator auto-revert decision logic."""
import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "seo"))

import operator_autorevert as ar  # noqa: E402

TODAY = dt.date(2026, 7, 15)


def _baseline(clicks, days_ago, url="https://saaspare.org/pages/foo", status=ar.PENDING):
    return {
        "path": "site/pages/foo.html",
        "url": url,
        "baseline_clicks": clicks,
        "baseline_date": (TODAY - dt.timedelta(days=days_ago)).isoformat(),
        "pre_blob": "deadbeef",
        "status": status,
    }


# ── path_to_url ──────────────────────────────────────────────────────────────
def test_path_to_url_strips_site_and_html():
    assert ar.path_to_url("site/pages/foo.html") == "https://saaspare.org/pages/foo"


def test_path_to_url_root_index():
    assert ar.path_to_url("site/index.html") == "https://saaspare.org"


def test_lookup_clicks_tolerates_trailing_slash():
    pc = {"https://saaspare.org/pages/foo/": 30.0}
    assert ar.lookup_clicks("https://saaspare.org/pages/foo", pc) == 30.0


def test_lookup_clicks_missing_returns_none():
    assert ar.lookup_clicks("https://saaspare.org/pages/foo", {}) is None


# ── decide ───────────────────────────────────────────────────────────────────
def test_too_young_waits():
    d = ar.decide(_baseline(100, days_ago=10), {"https://saaspare.org/pages/foo": 10}, TODAY)
    assert d["action"] == "wait"


def test_big_drop_after_window_reverts():
    d = ar.decide(_baseline(100, days_ago=22), {"https://saaspare.org/pages/foo": 50}, TODAY)
    assert d["action"] == "revert"
    assert d["drop_pct"] == 50.0


def test_small_drop_is_kept():
    # 5% drop — within noise, keep.
    d = ar.decide(_baseline(100, days_ago=22), {"https://saaspare.org/pages/foo": 95}, TODAY)
    assert d["action"] == "keep"


def test_exactly_threshold_is_kept():
    # Exactly 10% down -> floor is 90; current 90 is NOT below floor -> keep.
    d = ar.decide(_baseline(100, days_ago=22), {"https://saaspare.org/pages/foo": 90}, TODAY)
    assert d["action"] == "keep"


def test_gain_is_kept():
    d = ar.decide(_baseline(100, days_ago=30), {"https://saaspare.org/pages/foo": 140}, TODAY)
    assert d["action"] == "keep"


def test_low_traffic_page_never_reverts():
    # Page had only 8 clicks at baseline — below MIN_CLICKS, too noisy to judge.
    d = ar.decide(_baseline(8, days_ago=30), {"https://saaspare.org/pages/foo": 0}, TODAY)
    assert d["action"] == "low_traffic"


def test_no_current_data_is_inconclusive():
    d = ar.decide(_baseline(100, days_ago=30), {}, TODAY)
    assert d["action"] == "inconclusive"


# ── select_reverts (status transitions + circuit-breaker input) ───────────────
def test_select_reverts_updates_statuses_and_leaves_pending():
    baselines = [
        _baseline(100, 30, url="https://saaspare.org/pages/loser"),   # reverts
        _baseline(100, 30, url="https://saaspare.org/pages/winner"),  # kept
        _baseline(100, 5, url="https://saaspare.org/pages/young"),    # waits -> pending
        _baseline(100, 30, url="https://saaspare.org/pages/nodata"),  # inconclusive -> pending
    ]
    page_clicks = {
        "https://saaspare.org/pages/loser": 40,
        "https://saaspare.org/pages/winner": 120,
        "https://saaspare.org/pages/young": 10,
    }
    decisions, updated = ar.select_reverts(baselines, page_clicks, TODAY)
    actions = sorted(d["action"] for d in decisions)
    assert actions == ["inconclusive", "keep", "revert", "wait"]
    status_by_url = {u["url"]: u["status"] for u in updated}
    assert status_by_url["https://saaspare.org/pages/loser"] == ar.REVERTED
    assert status_by_url["https://saaspare.org/pages/winner"] == ar.KEPT
    assert status_by_url["https://saaspare.org/pages/young"] == ar.PENDING
    assert status_by_url["https://saaspare.org/pages/nodata"] == ar.PENDING


def test_already_resolved_baselines_are_skipped():
    baselines = [_baseline(100, 30, status=ar.KEPT)]
    decisions, updated = ar.select_reverts(baselines, {"https://saaspare.org/pages/foo": 10}, TODAY)
    assert decisions == []
    assert updated[0]["status"] == ar.KEPT


def test_circuit_breaker_counts_reverts_over_budget():
    # 26 losing pages — caller (cmd_evaluate) must abort when > MAX_REVERTS.
    baselines = [
        _baseline(100, 30, url=f"https://saaspare.org/pages/p{i}") for i in range(ar.MAX_REVERTS + 1)
    ]
    page_clicks = {f"https://saaspare.org/pages/p{i}": 10 for i in range(ar.MAX_REVERTS + 1)}
    decisions, _ = ar.select_reverts(baselines, page_clicks, TODAY)
    reverts = [d for d in decisions if d["action"] == "revert"]
    assert len(reverts) > ar.MAX_REVERTS
