import time
import uuid
from core.db import db
from core.logger import log
from core.secrets import get
from scorer.prefilter import passes
from scorer.llm_scorer import score
from core.models import RawSignal

BATCH_SIZE = int(get("SCORE_BATCH_SIZE", "100"))


def run():
    run_id = str(uuid.uuid4())[:8]
    with db() as conn:
        conn.execute(
            "INSERT INTO runs (id, job, started_at) VALUES (?, 'score', ?)",
            (run_id, int(time.time()))
        )
        rows = conn.execute("""
            SELECT * FROM raw_signals
            WHERE processed = 0
            ORDER BY ts DESC
            LIMIT ?
        """, (BATCH_SIZE,)).fetchall()

    log.info(f"Scoring {len(rows)} unprocessed signals")
    scored_count = 0
    skipped_prefilter = 0

    for row in rows:
        signal = RawSignal(
            id=row["id"],
            source=row["source"],
            url=row["url"] or "",
            title=row["title"] or "",
            body=row["body"] or "",
            author=row["author"] or "",
            subreddit=row["subreddit"] or "",
            score=row["score"] or 0,
            ts=row["ts"],
        )

        if not passes(signal):
            skipped_prefilter += 1
            _mark_processed(row["id"])
            continue

        scored = score(signal)
        if scored:
            _save_scored(scored)
            scored_count += 1
            _mark_processed(row["id"])
        # If LLM failed (transient), leave unprocessed so next run retries

    with db() as conn:
        conn.execute("""
            UPDATE runs SET ended_at = ?, status = 'ok', signals_in = ?, signals_out = ?
            WHERE id = ?
        """, (int(time.time()), len(rows), scored_count, run_id))

    log.info(f"Scoring done: {scored_count} scored, {skipped_prefilter} filtered out")
    return scored_count


def _mark_processed(signal_id: str):
    with db() as conn:
        conn.execute("UPDATE raw_signals SET processed = 1 WHERE id = ?", (signal_id,))


def _save_scored(scored):
    with db() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO scored_signals
            (id, raw_id, intent, budget_signal, urgency, vertical, buyer_role,
             estimated_deal_usd, monetization_path, confidence, profit_score, llm_reasoning, ts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (scored.id, scored.raw_id, scored.intent, scored.budget_signal,
              scored.urgency, scored.vertical, scored.buyer_role,
              scored.estimated_deal_usd, scored.monetization_path,
              scored.confidence, scored.profit_score, scored.llm_reasoning, scored.ts))
