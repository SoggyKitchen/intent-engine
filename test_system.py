#!/usr/bin/env python
"""Sanity check the local token distribution and content inventory."""

import sqlite3
import sys
import time
from datetime import UTC, datetime
from pathlib import Path


def collect_system_status() -> dict:
    db = sqlite3.connect("data/intent.db")
    db.row_factory = sqlite3.Row
    try:
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        quota_rows = db.execute(
            "SELECT provider, tokens_used FROM daily_quota WHERE date = ? ORDER BY provider",
            (today,),
        ).fetchall()
        clusters = db.execute(
            """
            SELECT vertical, COUNT(*) as cnt
            FROM scored_signals
            WHERE monetization_path IN ('affiliate', 'lead_pack')
              AND intent >= 35
              AND ts >= ?
            GROUP BY vertical
            ORDER BY cnt DESC
            """,
            (int(time.time()) - 7 * 86400,),
        ).fetchall()
        pages = db.execute("SELECT COUNT(*) as cnt FROM outputs WHERE type = 'seo_page'").fetchone()["cnt"]
    finally:
        db.close()

    score_yaml = Path(".github/workflows/score_publish.yml").read_text(encoding="utf-8")
    programmatic_yaml = Path(".github/workflows/programmatic.yml").read_text(encoding="utf-8")

    score_tokens = 40 * 4000 * 4
    publish_tokens = 150_000
    programmatic_tokens = 130 * 5000 * 5
    total_tokens = score_tokens + publish_tokens + programmatic_tokens
    capacity = 4_750_000

    return {
        "today": today,
        "quota_rows": quota_rows,
        "clusters": clusters,
        "pages": pages,
        "score_yaml": score_yaml,
        "programmatic_yaml": programmatic_yaml,
        "score_tokens": score_tokens,
        "publish_tokens": publish_tokens,
        "programmatic_tokens": programmatic_tokens,
        "total_tokens": total_tokens,
        "capacity": capacity,
    }


def render_status(status: dict):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 60)
    print("SYSTEM TEST: 80/20 Token Distribution")
    print("=" * 60)

    print("\n[1] QUOTA STATUS")
    print(f"    Today: {status['today']}")
    print(f"    Quota records: {len(status['quota_rows'])}")
    total_used = sum(row["tokens_used"] for row in status["quota_rows"])
    print(f"    Total tokens used: {total_used:,}")
    print(f"    Capacity: {status['capacity']:,}")
    print(f"    Utilization: {(total_used / status['capacity']) * 100:.1f}%")

    print("\n[2] SIGNAL CLUSTERS (7-day window)")
    if status["clusters"]:
        total_signals = sum(row["cnt"] for row in status["clusters"])
        print(f"    Total signals: {total_signals:,}")
        print(f"    Verticals with clusters: {len(status['clusters'])}")
        for row in status["clusters"][:5]:
            print(f"      - {row['vertical']}: {row['cnt']} signals")
    else:
        print("    WARNING: No clusters - programmatic may generate 0 pages")

    print("\n[3] EXISTING PAGES")
    print(f"    Current portfolio: {status['pages']:,} pages")

    print("\n[4] CONFIGURATION CHECK")
    print(
        "    "
        + ("OK" if 'SCORE_BATCH_SIZE: "40"' in status["score_yaml"] else "FAIL")
        + " Score batch size = 40"
    )
    print(
        "    "
        + ("OK" if "max_pages || '130'" in status["programmatic_yaml"] else "FAIL")
        + " Programmatic max = 130"
    )

    print("\n[5] BUDGET ALLOCATION")
    print(f"    Scoring:      {status['score_tokens']:>10,} tokens")
    print(f"    Publishing:   {status['publish_tokens']:>10,} tokens")
    print(f"    Programmatic: {status['programmatic_tokens']:>10,} tokens")
    print(f"    Total:        {status['total_tokens']:>10,} tokens")
    print(f"    Buffer:       {status['capacity'] - status['total_tokens']:>10,} tokens")


def test_quota_and_clusters():
    status = collect_system_status()
    assert 'SCORE_BATCH_SIZE: "40"' in status["score_yaml"]
    assert "max_pages || '130'" in status["programmatic_yaml"]
    assert status["total_tokens"] < status["capacity"]
    assert (status["capacity"] - status["total_tokens"]) / status["capacity"] > 0.10


if __name__ == "__main__":
    system_status = collect_system_status()
    render_status(system_status)
    try:
        test_quota_and_clusters()
    except AssertionError:
        sys.exit(1)
    sys.exit(0)
