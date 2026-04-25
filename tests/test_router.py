import importlib
import os


def test_router_refund_persists_to_db(monkeypatch, tmp_path):
    db_path = tmp_path / "intent.db"
    monkeypatch.setenv("DB_PATH", str(db_path))
    monkeypatch.setenv("CEREBRAS_API_KEY", "test-key")
    for idx in range(2, 8):
        monkeypatch.delenv(f"CEREBRAS_API_KEY_{idx}", raising=False)

    from core.db import migrate, db

    migrate()

    import llm.router as router

    router = importlib.reload(router)
    provider = router._get_ordered_providers()[0][0]

    assert router._try_charge(provider, 4000) is True
    router._refund(provider, 4000)

    with db() as conn:
        row = conn.execute(
            "SELECT tokens_used FROM daily_quota WHERE date = ? AND provider = ?",
            (router._today(), provider),
        ).fetchone()

    assert row["tokens_used"] == 0
