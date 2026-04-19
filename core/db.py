import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager

_DB_PATH = Path(os.getenv("DB_PATH", "data/intent.db"))


def get_db() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def db():
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS raw_signals (
    id          TEXT PRIMARY KEY,
    source      TEXT NOT NULL,
    url         TEXT,
    title       TEXT,
    body        TEXT,
    author      TEXT,
    subreddit   TEXT,
    score       INTEGER DEFAULT 0,
    ts          INTEGER NOT NULL,
    fetched_at  INTEGER NOT NULL,
    processed   INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_raw_ts ON raw_signals(ts DESC);
CREATE INDEX IF NOT EXISTS idx_raw_processed ON raw_signals(processed);

CREATE TABLE IF NOT EXISTS scored_signals (
    id                  TEXT PRIMARY KEY,
    raw_id              TEXT NOT NULL REFERENCES raw_signals(id),
    intent              INTEGER,
    budget_signal       INTEGER,
    urgency             INTEGER,
    vertical            TEXT,
    buyer_role          TEXT,
    estimated_deal_usd  INTEGER,
    monetization_path   TEXT,
    confidence          REAL,
    profit_score        REAL,
    llm_reasoning       TEXT,
    ts                  INTEGER NOT NULL,
    UNIQUE(raw_id)
);

CREATE INDEX IF NOT EXISTS idx_scored_vertical ON scored_signals(vertical);
CREATE INDEX IF NOT EXISTS idx_scored_profit ON scored_signals(profit_score DESC);

CREATE TABLE IF NOT EXISTS outputs (
    id              TEXT PRIMARY KEY,
    type            TEXT NOT NULL,
    vertical        TEXT,
    title           TEXT,
    file_path       TEXT,
    published_url   TEXT,
    gumroad_id      TEXT,
    created_at      INTEGER NOT NULL,
    revenue         REAL DEFAULT 0,
    views           INTEGER DEFAULT 0,
    conversions     INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_outputs_vertical_type ON outputs(vertical, type, created_at DESC);

CREATE TABLE IF NOT EXISTS bandit_arms (
    arm             TEXT PRIMARY KEY,
    alpha           REAL DEFAULT 1.0,
    beta_           REAL DEFAULT 1.0,
    trials          INTEGER DEFAULT 0,
    revenue         REAL DEFAULT 0,
    conversions     INTEGER DEFAULT 0,
    updated_at      INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS niche_perf (
    vertical        TEXT PRIMARY KEY,
    signals_today   INTEGER DEFAULT 0,
    signals_total   INTEGER DEFAULT 0,
    outputs_total   INTEGER DEFAULT 0,
    revenue_total   REAL DEFAULT 0,
    profit_per_sig  REAL DEFAULT 0,
    last_run        INTEGER
);

CREATE TABLE IF NOT EXISTS daily_quota (
    date        TEXT NOT NULL,
    provider    TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    PRIMARY KEY (date, provider)
);

CREATE TABLE IF NOT EXISTS runs (
    id          TEXT PRIMARY KEY,
    job         TEXT NOT NULL,
    started_at  INTEGER NOT NULL,
    ended_at    INTEGER,
    status      TEXT DEFAULT 'running',
    signals_in  INTEGER DEFAULT 0,
    signals_out INTEGER DEFAULT 0,
    error       TEXT
);
"""


def migrate():
    with db() as conn:
        conn.executescript(SCHEMA)
