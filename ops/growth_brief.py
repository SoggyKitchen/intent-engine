import json
import re
import time
from pathlib import Path

from core.db import db
from core.secrets import get
from ops.profit_audit import collect_profit_audit

OUT_DIR = Path("outputs/generated")
SOCIAL_PACK = Path("outputs/generated/social/social_pack_latest.json")
AFFILIATE_REPORT = Path("data/affiliate_url_report.md")


def _read_affiliate_validation() -> dict:
    if not AFFILIATE_REPORT.exists():
        return {"ok": 0, "warn": 0, "prog": 0, "dead": 0, "warn_paths": [], "dead_paths": []}
    text = AFFILIATE_REPORT.read_text(encoding="utf-8", errors="ignore")
    counts = {
        "ok": _extract_count(text, "OK"),
        "warn": _extract_count(text, "WARN"),
        "prog": _extract_count(text, "PROG"),
        "dead": _extract_count(text, "DEAD"),
    }
    counts["warn_paths"] = re.findall(r"## WARN `([^`]+)`", text)[:8]
    counts["dead_paths"] = re.findall(r"## (?:DEAD|PROG) `([^`]+)`", text)[:8]
    return counts


def _extract_count(text: str, label: str) -> int:
    match = re.search(rf"- {re.escape(label)}:\s*(\d+)", text)
    return int(match.group(1)) if match else 0


def _latest_social_items(limit: int = 5) -> list[dict]:
    if not SOCIAL_PACK.exists():
        return []
    try:
        payload = json.loads(SOCIAL_PACK.read_text(encoding="utf-8"))
    except Exception:
        return []
    return payload[:limit] if isinstance(payload, list) else []


def _recent_pages(limit: int = 8) -> list[dict]:
    try:
        with db() as conn:
            rows = conn.execute(
                """
                SELECT title, published_url, vertical, created_at
                FROM outputs
                WHERE type = 'seo_page' AND published_url IS NOT NULL AND published_url != ''
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]
    except Exception:
        return []


def _network_tasks(audit: dict) -> list[str]:
    tasks: list[str] = []
    for network in audit.get("network_signups", []):
        tools = ", ".join(network.get("tools", [])[:8])
        tasks.append(f"- Apply or re-check {network['name']}: {tools}")
    if not tasks:
        tasks.append("- No new network gaps detected from the current registry.")
    return tasks


def _traffic_tasks(social_items: list[dict], recent_pages: list[dict]) -> list[str]:
    tasks: list[str] = []
    for item in social_items[:3]:
        title = item.get("title", "Untitled page")
        url = item.get("url", "")
        tasks.append(f"- Post: {title} ({url})")
    for page in recent_pages[:2]:
        tasks.append(f"- Internally link or share recent page: {page.get('title')} ({page.get('published_url')})")
    return tasks or ["- Generate a fresh social pack with `uv run engine social` before posting."]


def generate_growth_brief() -> str:
    """Create the weekly owner brief: partner work, link health, and posting queue."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    domain = get("SITE_DOMAIN", "https://saaspare.org")
    audit = collect_profit_audit(max_gap_items=8)
    validation = _read_affiliate_validation()
    social_items = _latest_social_items()
    recent_pages = _recent_pages()
    stamp = time.strftime("%Y-%m-%d")

    lines = [
        f"# SaaSpare Growth Brief - {stamp}",
        "",
        "## Scoreboard",
        f"- Site: {domain}",
        f"- SEO pages scanned: {audit['page_count']}",
        f"- CTA coverage: {audit['cta_coverage_pct']:.1f}%",
        f"- Redirects available: {audit['redirect_count']}",
        f"- Imported affiliate advertisers: {audit['imported_affiliate_count']}",
        f"- Redirect validation: OK={validation['ok']} WARN={validation['warn']} PROG={validation['prog']} DEAD={validation['dead']}",
        "",
        "## Do First",
    ]

    if validation["dead"] or validation["prog"]:
        lines.extend(f"- Fix redirect path {path}" for path in validation["dead_paths"])
    else:
        lines.append("- Keep redirects clean: no dead or partner-program destinations detected in the latest report.")

    if audit["missing_partner_targets_total"]:
        for item in audit["missing_partner_targets"][:5]:
            lines.append(f"- Find partner coverage for {item['tool']} ({item['vertical']}, {item['page_count']} pages)")
    else:
        lines.append("- Partner coverage is complete for the tracked high-value page targets.")

    lines.extend([
        "",
        "## Partner Applications",
        *_network_tasks(audit),
        "",
        "## Post This Week",
        *_traffic_tasks(social_items, recent_pages),
        "",
        "## Watchlist",
    ])

    if validation["warn_paths"]:
        lines.extend(f"- Recheck anti-bot or host-mismatch warning: {path}" for path in validation["warn_paths"])
    else:
        lines.append("- No redirect warnings in the latest report.")

    lines.extend([
        "",
        "## Operating Rule",
        "- New affiliate CSV received: run `uv run engine import-links --csv \"C:\\Users\\smith\\Downloads\\links.csv\"`, then let GitHub Actions rebuild the site.",
        "- New social credentials received: add them as GitHub secrets, then run `uv run engine social` or trigger Score & Publish.",
    ])

    output = "\n".join(lines) + "\n"
    dated = OUT_DIR / f"growth_brief_{stamp}.md"
    latest = OUT_DIR / "growth_brief_latest.md"
    dated.write_text(output, encoding="utf-8")
    latest.write_text(output, encoding="utf-8")
    return str(latest)
