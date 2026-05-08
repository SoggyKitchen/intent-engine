#!/usr/bin/env python3
"""
track_pricing.py — SaaSpare Price Intelligence Engine.

Reads data/pricing_seed.json (manually-verified seed prices), persists
snapshots into intent.db, and on subsequent runs detects diffs between
the latest snapshot and the seed (or between two snapshots).

This is the data layer for:
  - /pages/[tool]-pricing-history-2026.html  (per-tool history)
  - /pages/saas-pricing-changes               (rolled up "this month")
  - alternative-routing pages (when a price hike is detected)

How it works:
  1. Migrate: ensure pricing_snapshots + pricing_changes tables exist.
  2. For each tool in pricing_seed.json:
       - Compare each plan's current values vs. the most recent snapshot.
       - Insert a new snapshot row (always, for traceability).
       - If anything changed (price, free_trial, cc_required, seat_min,
         plan removed, plan added), insert a row into pricing_changes
         with field, old_value, new_value, direction, pct_change.
  3. Write a summary to outputs/seo/pricing_track.json.

This script DOES NOT scrape vendor pricing pages today. The scraper is
Phase 2 — it will populate pricing_seed.json from live vendor pages
nightly, but for now we treat the seed as our source of truth so we
can ship the public pages and start collecting historical data
immediately. Editing the seed JSON is how prices get updated.

Run:  uv run python scripts/track_pricing.py
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, sqlite3, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "intent.db"
SEED_PATH = ROOT / "data" / "pricing_seed.json"
OUTPUTS = ROOT / "outputs" / "seo"
OUTPUTS.mkdir(parents=True, exist_ok=True)

SCHEMA = """
CREATE TABLE IF NOT EXISTS pricing_snapshots (
    id            TEXT PRIMARY KEY,
    tool          TEXT NOT NULL,
    plan          TEXT NOT NULL,
    monthly_usd   REAL,
    annual_usd    REAL,
    seat_minimum  INTEGER,
    free_trial    INTEGER,
    cc_required   INTEGER,
    source_url    TEXT NOT NULL,
    snapshot_at   INTEGER NOT NULL,
    raw_json      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_snap_tool_plan ON pricing_snapshots (tool, plan, snapshot_at DESC);

CREATE TABLE IF NOT EXISTS pricing_changes (
    id          TEXT PRIMARY KEY,
    tool        TEXT NOT NULL,
    plan        TEXT NOT NULL,
    field       TEXT NOT NULL,
    old_value   TEXT,
    new_value   TEXT,
    direction   TEXT,
    pct_change  REAL,
    source_url  TEXT,
    detected_at INTEGER NOT NULL,
    confidence  REAL DEFAULT 1.0
);
CREATE INDEX IF NOT EXISTS idx_change_tool ON pricing_changes (tool, detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_change_recent ON pricing_changes (detected_at DESC);
"""

CHANGE_FIELDS = ["monthly_usd", "annual_usd", "seat_minimum", "free_trial", "cc_required"]


def migrate(con: sqlite3.Connection) -> None:
    for stmt in SCHEMA.strip().split(";"):
        s = stmt.strip()
        if s:
            con.execute(s)
    con.commit()


def latest_snapshot(con: sqlite3.Connection, tool: str, plan: str) -> dict | None:
    row = con.execute(
        "SELECT raw_json FROM pricing_snapshots "
        "WHERE tool=? AND plan=? ORDER BY snapshot_at DESC LIMIT 1",
        (tool, plan),
    ).fetchone()
    if not row:
        return None
    return json.loads(row[0])


def diff_plan(old: dict | None, new: dict) -> list[tuple[str, str | None, str, str, float | None]]:
    """Return list of (field, old_value, new_value, direction, pct_change)."""
    out = []
    if not old:
        return [("plan", None, json.dumps(new), "new", None)]
    for f in CHANGE_FIELDS:
        old_v = old.get(f)
        new_v = new.get(f)
        if old_v == new_v:
            continue
        if isinstance(old_v, (int, float)) and isinstance(new_v, (int, float)) and old_v:
            pct = (new_v - old_v) / old_v * 100
            direction = "hike" if new_v > old_v else "drop"
        else:
            pct = None
            if old_v is None and new_v is not None:
                direction = "new"
            elif old_v is not None and new_v is None:
                direction = "removed"
            elif old_v and not new_v:
                direction = "removed"
            elif not old_v and new_v:
                direction = "added"
            else:
                direction = "changed"
        out.append((f, json.dumps(old_v), json.dumps(new_v), direction, pct))
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args(argv)

    seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    now = int(time.time())

    con = sqlite3.connect(DB_PATH)
    migrate(con)

    report = {
        "snapshot_at": now,
        "tools_processed": 0,
        "snapshots_taken": 0,
        "changes_detected": 0,
        "changes_by_direction": {"hike": 0, "drop": 0, "new": 0, "removed": 0, "changed": 0, "added": 0},
        "examples": [],
    }

    for tool in seed["tools"]:
        report["tools_processed"] += 1
        slug = tool["tool"]
        for plan in tool["plans"]:
            row = {
                "tool": slug,
                "plan": plan["plan"],
                "monthly_usd": plan.get("monthly_usd"),
                "annual_usd": plan.get("annual_usd"),
                "seat_minimum": plan.get("seat_minimum", 1),
                "free_trial": int(bool(plan.get("free_trial"))),
                "cc_required": int(bool(plan.get("cc_required"))),
                "source_url": tool["source_url"],
                "notes": plan.get("notes", ""),
            }
            old = latest_snapshot(con, slug, plan["plan"])
            diffs = diff_plan(old, row)
            # Record snapshot every run (history matters)
            sid = hashlib.md5(f"{slug}|{plan['plan']}|{now}".encode()).hexdigest()[:16]
            if not args.check:
                con.execute(
                    "INSERT OR IGNORE INTO pricing_snapshots "
                    "(id, tool, plan, monthly_usd, annual_usd, seat_minimum, "
                    "free_trial, cc_required, source_url, snapshot_at, raw_json) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (sid, slug, plan["plan"], row["monthly_usd"], row["annual_usd"],
                     row["seat_minimum"], row["free_trial"], row["cc_required"],
                     row["source_url"], now, json.dumps(row)),
                )
            report["snapshots_taken"] += 1
            for field, old_v, new_v, direction, pct in diffs:
                report["changes_detected"] += 1
                report["changes_by_direction"][direction] = (
                    report["changes_by_direction"].get(direction, 0) + 1
                )
                cid = hashlib.md5(
                    f"{slug}|{plan['plan']}|{field}|{now}".encode()
                ).hexdigest()[:16]
                if not args.check:
                    con.execute(
                        "INSERT OR IGNORE INTO pricing_changes "
                        "(id, tool, plan, field, old_value, new_value, direction, "
                        "pct_change, source_url, detected_at, confidence) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (cid, slug, plan["plan"], field, old_v, new_v,
                         direction, pct, tool["source_url"], now, 1.0),
                    )
                if len(report["examples"]) < 8:
                    report["examples"].append({
                        "tool": slug, "plan": plan["plan"], "field": field,
                        "old": old_v, "new": new_v,
                        "direction": direction, "pct_change": pct,
                    })

    if not args.check:
        con.commit()
    con.close()

    (OUTPUTS / "pricing_track.json").write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8"
    )
    print("=== track_pricing ===")
    print(f"  tools processed   : {report['tools_processed']}")
    print(f"  snapshots taken   : {report['snapshots_taken']}")
    print(f"  changes detected  : {report['changes_detected']}")
    print(f"  by direction      : {report['changes_by_direction']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
