import random
import time
from typing import Optional

from core.db import db
from core.logger import log


def record_conversion(arm: str, revenue: float):
    now = int(time.time())
    with db() as conn:
        conn.execute("""
            INSERT INTO bandit_arms (arm, alpha, beta_, trials, revenue, conversions, updated_at)
            VALUES (?, 1.0, 1.0, 1, ?, 1, ?)
            ON CONFLICT(arm) DO UPDATE SET
                alpha = alpha + 1,
                trials = trials + 1,
                revenue = revenue + excluded.revenue,
                conversions = conversions + 1,
                updated_at = excluded.updated_at
        """, (arm, revenue, now))


def record_trial(arm: str):
    now = int(time.time())
    with db() as conn:
        conn.execute("""
            INSERT INTO bandit_arms (arm, alpha, beta_, trials, revenue, conversions, updated_at)
            VALUES (?, 1.0, 1.0, 1, 0, 0, ?)
            ON CONFLICT(arm) DO UPDATE SET
                beta_ = beta_ + 1,
                trials = trials + 1,
                updated_at = excluded.updated_at
        """, (arm, now))


def thompson_sample(arms: list[str]) -> str:
    if not arms:
        return ""
    samples = {}
    with db() as conn:
        for arm in arms:
            row = conn.execute(
                "SELECT alpha, beta_ FROM bandit_arms WHERE arm = ?", (arm,)
            ).fetchone()
            a = row["alpha"] if row else 1.0
            b = row["beta_"] if row else 1.0
            samples[arm] = random.betavariate(a, b)
    return max(samples, key=samples.get)


def get_budget_allocation(verticals: list[str], total_signals: int = 1000) -> dict[str, int]:
    if not verticals:
        return {}

    arms = [f"{v}:all" for v in verticals]
    samples = {}
    with db() as conn:
        for arm in arms:
            row = conn.execute(
                "SELECT alpha, beta_ FROM bandit_arms WHERE arm = ?", (arm,)
            ).fetchone()
            a = row["alpha"] if row else 1.0
            b = row["beta_"] if row else 1.0
            samples[arm] = random.betavariate(a, b)

    total_weight = sum(samples.values()) or 1.0
    explore_floor = max(1, int(total_signals * 0.05))
    remaining = total_signals - explore_floor * len(verticals)

    allocation = {}
    for v, arm in zip(verticals, arms):
        share = samples[arm] / total_weight
        allocation[v] = explore_floor + int(remaining * share)

    log.info(f"Bandit allocation: {allocation}")
    return allocation


def get_arm_stats() -> list[dict]:
    with db() as conn:
        rows = conn.execute("""
            SELECT arm, alpha, beta_, trials, revenue, conversions,
                   CASE WHEN trials > 0 THEN revenue / trials ELSE 0 END as rps
            FROM bandit_arms
            ORDER BY rps DESC
        """).fetchall()
    return [dict(r) for r in rows]


def should_kill_arm(arm: str, min_trials: int = 200) -> bool:
    with db() as conn:
        row = conn.execute(
            "SELECT trials, revenue FROM bandit_arms WHERE arm = ?", (arm,)
        ).fetchone()
    if not row or row["trials"] < min_trials:
        return False
    median_rps = _get_median_rps()
    arm_rps = row["revenue"] / row["trials"] if row["trials"] > 0 else 0
    return arm_rps < median_rps * 0.5


def _get_median_rps() -> float:
    with db() as conn:
        rows = conn.execute(
            "SELECT revenue, trials FROM bandit_arms WHERE trials > 0"
        ).fetchall()
    if not rows:
        return 0.0
    rpss = sorted([r["revenue"] / r["trials"] for r in rows])
    mid = len(rpss) // 2
    return rpss[mid] if rpss else 0.0
