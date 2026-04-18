import csv
import hashlib
import os
import time
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from core.db import db
from core.logger import log
from core.secrets import DRY_RUN, MONETIZATION_MODE

OUTPUT_DIR = Path("outputs/generated")
TEMPLATE_DIR = Path(__file__).parent / "templates"


def generate(vertical: str, days_back: int = 7) -> Optional[str]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    since_ts = int(time.time()) - (days_back * 86400)

    with db() as conn:
        rows = conn.execute("""
            SELECT s.*, r.url, r.title as r_title, r.body, r.source, r.author, r.subreddit
            FROM scored_signals s
            JOIN raw_signals r ON r.id = s.raw_id
            WHERE s.vertical = ?
              AND s.ts >= ?
              AND s.profit_score >= 8
              AND s.monetization_path IN ('lead_pack', 'affiliate')
            ORDER BY s.profit_score DESC
            LIMIT 200
        """, (vertical, since_ts)).fetchall()

    if len(rows) < 10:
        log.info(f"Not enough signals for {vertical} lead pack ({len(rows)} found, need 10)")
        return None

    timestamp = time.strftime("%Y-%m-%d")
    pack_id = hashlib.sha256(f"{vertical}:{timestamp}".encode()).hexdigest()[:8]
    csv_path = OUTPUT_DIR / f"leadpack_{vertical}_{timestamp}_{pack_id}.csv"
    md_path = OUTPUT_DIR / f"leadpack_{vertical}_{timestamp}_{pack_id}.md"

    _write_csv(rows, csv_path, vertical)
    _write_summary(rows, md_path, vertical, timestamp)

    if DRY_RUN:
        log.info(f"[DRY RUN] Lead pack would be published: {csv_path}")
        return str(csv_path)

    log.info(f"Lead pack ready: {csv_path} ({len(rows)} signals)")

    with db() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO outputs (id, type, vertical, title, file_path, created_at)
            VALUES (?, 'lead_pack', ?, ?, ?, ?)
        """, (pack_id, vertical, f"{vertical.title()} Intent Pack {timestamp}",
              str(csv_path), int(time.time())))

    return str(csv_path)


def _write_csv(rows, path: Path, vertical: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "signal_id", "source", "vertical", "buyer_role",
            "intent_score", "budget_score", "urgency_score", "profit_score",
            "estimated_deal_usd", "url", "title", "key_insight",
            "recommended_action", "signal_date",
        ])
        for row in rows:
            writer.writerow([
                row["raw_id"],
                row["source"],
                vertical,
                row["buyer_role"],
                row["intent"],
                row["budget_signal"],
                row["urgency"],
                round(row["profit_score"], 1),
                row["estimated_deal_usd"],
                row["url"],
                row["r_title"][:120],
                row["llm_reasoning"][:200],
                _recommended_action(row["buyer_role"], vertical),
                time.strftime("%Y-%m-%d", time.localtime(row["ts"])),
            ])


def _write_summary(rows, path: Path, vertical: str, timestamp: str):
    total_deal_value = sum(r["estimated_deal_usd"] for r in rows)
    avg_intent = sum(r["intent"] for r in rows) / len(rows)
    top_roles = {}
    for r in rows:
        top_roles[r["buyer_role"]] = top_roles.get(r["buyer_role"], 0) + 1
    top_role = max(top_roles, key=top_roles.get)

    lines = [
        f"# {vertical.replace('_', ' ').title()} Buyer Intent Pack — {timestamp}\n",
        f"**{len(rows)} verified buying signals** | Avg intent score: {avg_intent:.0f}/100\n",
        f"**Total addressable deal value (estimated):** ${total_deal_value:,}\n",
        f"**Primary buyer role:** {top_role}\n\n",
        "## What's Inside\n",
        "- Verified B2B buying intent signals from Reddit, HackerNews, GitHub, and StackOverflow\n",
        "- Each signal includes: source URL, intent/budget/urgency scores, estimated deal size\n",
        "- Recommended outreach angle per signal\n",
        "- Signals are max 7 days old\n\n",
        "## Top 5 Signals This Week\n",
    ]
    for row in rows[:5]:
        lines.append(
            f"- **[{row['r_title'][:80]}]({row['url']})** "
            f"| Intent: {row['intent']}/100 | ${row['estimated_deal_usd']:,} deal\n"
        )

    path.write_text("".join(lines), encoding="utf-8")


def _recommended_action(role: str, vertical: str) -> str:
    actions = {
        "founder": f"Reach out with ROI-focused pitch for {vertical} solution",
        "cto": f"Send technical comparison doc showing {vertical} migration path",
        "developer": f"Share free trial or open-source alternative for {vertical}",
        "marketer": f"Offer {vertical} case study with conversion metrics",
        "hr_manager": f"Book a {vertical} demo focused on compliance + reporting",
        "security_engineer": f"Send {vertical} security audit checklist",
        "data_scientist": f"Share {vertical} benchmark results + notebooks",
        "unknown": f"Send value-focused intro email for {vertical} solution",
    }
    return actions.get(role, actions["unknown"])
