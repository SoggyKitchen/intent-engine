#!/usr/bin/env python
"""Test the optimized token distribution system."""

import sqlite3
import time
from datetime import datetime
from pathlib import Path

def test_quota_and_clusters():
    """Check quota status and signal clusters."""
    db = sqlite3.connect('data/intent.db')
    db.row_factory = sqlite3.Row

    today = datetime.utcnow().strftime('%Y-%m-%d')

    print("=" * 60)
    print("SYSTEM TEST: 80/20 Token Distribution")
    print("=" * 60)

    # Check quota
    print(f"\n[1] QUOTA STATUS")
    rows = db.execute("SELECT COUNT(*) as cnt FROM daily_quota WHERE date=?", (today,)).fetchone()
    quota_records = rows['cnt']
    print(f"    Today: {today}")
    print(f"    Quota records: {quota_records}")

    if quota_records > 0:
        quota_data = db.execute(
            "SELECT provider, tokens_used FROM daily_quota WHERE date=? ORDER BY provider",
            (today,)
        ).fetchall()
        total_used = 0
        for row in quota_data:
            total_used += row['tokens_used']
        print(f"    Total tokens used: {total_used:,}")
        print(f"    Capacity: 4,750,000")
        pct = (total_used / 4_750_000) * 100
        print(f"    Utilization: {pct:.1f}%")

        if pct > 85:
            print(f"    ⚠️  WARNING: Approaching safe limit!")
    else:
        print(f"    ✓ Clean slate - first run today")

    # Check clusters
    print(f"\n[2] SIGNAL CLUSTERS (7-day window)")
    clusters = db.execute("""
        SELECT vertical, COUNT(*) as cnt
        FROM scored_signals
        WHERE monetization_path IN ('affiliate', 'lead_pack')
        AND intent >= 35
        AND ts >= ?
        GROUP BY vertical
        ORDER BY cnt DESC
    """, (int(time.time()) - 7*86400,)).fetchall()

    if clusters:
        total_signals = sum(c['cnt'] for c in clusters)
        print(f"    Total signals: {total_signals:,}")
        print(f"    Verticals with clusters: {len(clusters)}")
        for row in clusters[:5]:
            print(f"      - {row['vertical']}: {row['cnt']} signals")
        if len(clusters) > 5:
            print(f"      ... and {len(clusters) - 5} more verticals")
    else:
        print(f"    ⚠️  No clusters - programmatic may generate 0 pages")

    # Check pages
    print(f"\n[3] EXISTING PAGES")
    pages = db.execute("SELECT COUNT(*) as cnt FROM outputs WHERE type='seo_page'").fetchone()
    print(f"    Current portfolio: {pages['cnt']:,} pages")

    # Check batch sizes in code
    print(f"\n[4] CONFIGURATION CHECK")

    score_yaml = Path('.github/workflows/score_publish.yml').read_text()
    if 'SCORE_BATCH_SIZE: "40"' in score_yaml:
        print(f"    ✓ Score batch size: 40 (40 × 4K × 4 = 640K tokens)")
    else:
        print(f"    ✗ Score batch size not 40!")

    programmatic_yaml = Path('.github/workflows/programmatic.yml').read_text()
    if "max_pages || '130'" in programmatic_yaml:
        print(f"    ✓ Programmatic max: 130 (130 × 5 × 5K = 3.25M tokens)")
    else:
        print(f"    ✗ Programmatic max not 130!")

    # Budget calculation
    print(f"\n[5] BUDGET ALLOCATION")
    score_tokens = 40 * 4000 * 4  # 40 batch × 4K tokens × 4 runs
    publish_tokens = 150_000  # estimate
    programmatic_tokens = 130 * 5000 * 5  # 130 pages × 5K avg × 5 runs
    total = score_tokens + publish_tokens + programmatic_tokens

    print(f"    Scoring: {score_tokens:>11,} tokens (13.5%)")
    print(f"    Publishing: {publish_tokens:>7,} tokens (3.2%)")
    print(f"    Programmatic: {programmatic_tokens:>5,} tokens (68.4%)")
    print(f"    ─────────────────────────────")
    print(f"    Total: {total:>15,} tokens (85.1%)")
    print(f"    Capacity: 4,750,000 tokens")
    print(f"    Buffer: {4_750_000 - total:>14,} tokens (14.9%)")

    if total <= 4_000_000:
        print(f"    ✓ SAFE: Well under 4.75M limit")
    elif total <= 4_400_000:
        print(f"    ✓ OK: Under limit with buffer")
    else:
        print(f"    ✗ WARNING: Exceeds safe allocation!")

    print(f"\n[6] EXPECTED DAILY OUTPUT")
    print(f"    Pages generated: 650 (130 × 5)")
    print(f"    Signals scored: 160 (40 × 4)")
    print(f"    Signals found in clusters: ~20-30")
    print(f"    Total deployments: ~680 per day")

    print(f"\n[7] SUCCESS CRITERIA")
    checks = {
        "✓ Buffer > 10%": (4_750_000 - total) / 4_750_000 > 0.10,
        "✓ Batch size = 40": 'SCORE_BATCH_SIZE: "40"' in score_yaml,
        "✓ Max pages = 130": "max_pages || '130'" in programmatic_yaml,
        "✓ Have clusters": len(clusters) > 0,
        "✓ Under 85% budget": total / 4_750_000 < 0.85,
    }

    for check, result in checks.items():
        symbol = "✓" if result else "✗"
        print(f"    {symbol} {check}")

    all_pass = all(checks.values())

    print("\n" + "=" * 60)
    if all_pass:
        print("✓✓✓ ALL TESTS PASSED - SYSTEM READY ✓✓✓")
    else:
        print("✗ SOME TESTS FAILED - CHECK ABOVE")
    print("=" * 60)

    db.close()
    return all_pass

if __name__ == '__main__':
    import sys
    sys.exit(0 if test_quota_and_clusters() else 1)
