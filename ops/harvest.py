import hashlib
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterator

from adapters.hn import HNAdapter
from adapters.reddit import RedditAdapter
from adapters.rss import RSSAdapter
from adapters.github_adapter import GithubAdapter
from adapters.stackoverflow import StackOverflowAdapter
from core.db import db
from core.logger import log
from core.models import RawSignal
from core.secrets import get

LOOKBACK_HOURS = int(get("LOOKBACK_HOURS", "6"))


def run():
    since_ts = int(time.time()) - (LOOKBACK_HOURS * 3600)
    run_id = str(uuid.uuid4())[:8]
    started = int(time.time())

    with db() as conn:
        conn.execute(
            "INSERT INTO runs (id, job, started_at) VALUES (?, 'harvest', ?)",
            (run_id, started)
        )

    adapters = [HNAdapter(), RSSAdapter()]

    if get("GROQ_API_KEY") or get("REDDIT_CLIENT_ID"):
        try:
            adapters.append(RedditAdapter())
        except Exception as e:
            log.warning(f"Reddit adapter init failed: {e}")

    if get("GITHUB_TOKEN"):
        adapters.append(GithubAdapter())

    adapters.append(StackOverflowAdapter())

    total_new = 0
    with ThreadPoolExecutor(max_workers=len(adapters)) as pool:
        futures = {pool.submit(_run_adapter, adapter, since_ts): adapter.name
                   for adapter in adapters}
        for future in as_completed(futures):
            name = futures[future]
            try:
                count = future.result()
                total_new += count
                log.info(f"{name}: {count} new signals")
            except Exception as e:
                log.error(f"Adapter {name} failed: {e}")

    with db() as conn:
        conn.execute("""
            UPDATE runs SET ended_at = ?, status = 'ok', signals_in = ?
            WHERE id = ?
        """, (int(time.time()), total_new, run_id))

    log.info(f"Harvest complete: {total_new} new signals stored")
    _ping_health("harvest")
    return total_new


def _run_adapter(adapter, since_ts: int) -> int:
    count = 0
    try:
        for signal in adapter.fetch(since_ts):
            if _save_signal(signal):
                count += 1
    except Exception as e:
        log.error(f"Adapter {adapter.name} error mid-run: {e}")
    return count


def _save_signal(signal: RawSignal) -> bool:
    with db() as conn:
        result = conn.execute("""
            INSERT OR IGNORE INTO raw_signals
            (id, source, url, title, body, author, subreddit, score, ts, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (signal.id, signal.source, signal.url, signal.title, signal.body,
              signal.author, signal.subreddit, signal.score, signal.ts, int(time.time())))
        return result.rowcount > 0


def _ping_health(job: str):
    url = get("HEALTHCHECKS_URL")
    if not url:
        return
    try:
        from core.http import get as http_get
        http_get(f"{url}/{job}", skip_robots=True)
    except Exception:
        pass
