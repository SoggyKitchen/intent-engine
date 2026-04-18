import os
import tempfile
import pytest

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DB_PATH"] = _tmp.name
_tmp.close()

from core.db import migrate, db


def test_migrate_runs_without_error():
    migrate()


def test_insert_raw_signal():
    migrate()
    with db() as conn:
        conn.execute("""
            INSERT INTO raw_signals (id, source, url, title, body, ts, fetched_at)
            VALUES ('test1', 'hn', 'http://x.com', 'Test', 'Body', 1000, 2000)
        """)
        row = conn.execute("SELECT * FROM raw_signals WHERE id = 'test1'").fetchone()
        assert row["source"] == "hn"
        assert row["processed"] == 0


def test_bandit_arm_upsert():
    migrate()
    with db() as conn:
        conn.execute("""
            INSERT INTO bandit_arms (arm, alpha, beta_, trials, revenue, conversions, updated_at)
            VALUES ('devtools:lead_pack', 1.0, 1.0, 0, 0, 0, 0)
            ON CONFLICT(arm) DO UPDATE SET trials = trials + 1
        """)
        conn.execute("""
            INSERT INTO bandit_arms (arm, alpha, beta_, trials, revenue, conversions, updated_at)
            VALUES ('devtools:lead_pack', 1.0, 1.0, 0, 0, 0, 0)
            ON CONFLICT(arm) DO UPDATE SET trials = trials + 1
        """)
        row = conn.execute("SELECT trials FROM bandit_arms WHERE arm = 'devtools:lead_pack'").fetchone()
        assert row["trials"] == 1
