import time
from core.db import db
from core.logger import log
from learn.bandit import record_conversion, record_trial, get_arm_stats, should_kill_arm


def run_daily_optimization():
    log.info("Running daily optimization pass")
    _update_niche_performance()
    _feed_bandit_from_outputs()
    _kill_low_performers()
    _print_report()


def _update_niche_performance():
    with db() as conn:
        verticals = [r["vertical"] for r in conn.execute(
            "SELECT DISTINCT vertical FROM scored_signals"
        ).fetchall()]
        today_start = int(time.time()) - 86400
        for v in verticals:
            signals_today = conn.execute(
                "SELECT COUNT(*) FROM scored_signals WHERE vertical = ? AND ts >= ?",
                (v, today_start)
            ).fetchone()[0]
            signals_total = conn.execute(
                "SELECT COUNT(*) FROM scored_signals WHERE vertical = ?", (v,)
            ).fetchone()[0]
            outputs_total = conn.execute(
                "SELECT COUNT(*) FROM outputs WHERE vertical = ?", (v,)
            ).fetchone()[0]
            revenue = conn.execute(
                "SELECT COALESCE(SUM(revenue), 0) FROM outputs WHERE vertical = ?", (v,)
            ).fetchone()[0]
            pps = revenue / signals_total if signals_total > 0 else 0
            conn.execute("""
                INSERT INTO niche_perf (vertical, signals_today, signals_total, outputs_total, revenue_total, profit_per_sig, last_run)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(vertical) DO UPDATE SET
                    signals_today = excluded.signals_today,
                    signals_total = excluded.signals_total,
                    outputs_total = excluded.outputs_total,
                    revenue_total = excluded.revenue_total,
                    profit_per_sig = excluded.profit_per_sig,
                    last_run = excluded.last_run
            """, (v, signals_today, signals_total, outputs_total, revenue, pps, int(time.time())))


def _feed_bandit_from_outputs():
    with db() as conn:
        outputs = conn.execute("""
            SELECT vertical, type, revenue, conversions, views
            FROM outputs
            WHERE created_at >= ?
        """, (int(time.time()) - 7 * 86400,)).fetchall()
        for o in outputs:
            arm = f"{o['vertical']}:{o['type']}"
            if o["revenue"] > 0:
                record_conversion(arm, o["revenue"])
            elif o["views"] > 50:
                record_trial(arm)


def _kill_low_performers():
    stats = get_arm_stats()
    for arm_stat in stats:
        arm = arm_stat["arm"]
        if should_kill_arm(arm):
            log.warning(f"Low-performer arm paused: {arm} (rps={arm_stat['rps']:.2f})")


def _print_report():
    stats = get_arm_stats()
    with db() as conn:
        total_revenue = conn.execute(
            "SELECT COALESCE(SUM(revenue), 0) FROM outputs"
        ).fetchone()[0]
        total_outputs = conn.execute(
            "SELECT COUNT(*) FROM outputs"
        ).fetchone()[0]
        total_signals = conn.execute(
            "SELECT COUNT(*) FROM scored_signals"
        ).fetchone()[0]

    log.info("=" * 50)
    log.info(f"DAILY REPORT")
    log.info(f"Total revenue:  ${total_revenue:.2f}")
    log.info(f"Total outputs:  {total_outputs}")
    log.info(f"Total signals:  {total_signals}")
    log.info("Top arms:")
    for s in stats[:5]:
        log.info(f"  {s['arm']}: ${s['revenue']:.2f} / {s['trials']} trials = ${s['rps']:.3f}/trial")
    log.info("=" * 50)
