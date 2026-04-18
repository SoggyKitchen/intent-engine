import mimetypes
import time
from pathlib import Path
from typing import Optional

import httpx

from core.db import db
from core.logger import log
from core.secrets import DRY_RUN, get, MONETIZATION_MODE

GUMROAD_API = "https://api.gumroad.com/v2"


def _headers() -> dict:
    return {"Authorization": f"Bearer {get('GUMROAD_ACCESS_TOKEN')}"}


def publish_lead_pack(csv_path: str, vertical: str, title: str) -> Optional[str]:
    if MONETIZATION_MODE not in ("full", "parent_holds_account"):
        log.info(f"Gumroad publish skipped (mode={MONETIZATION_MODE})")
        return None

    if DRY_RUN:
        log.info(f"[DRY RUN] Would publish lead pack to Gumroad: {title}")
        return "dry-run-id"

    token = get("GUMROAD_ACCESS_TOKEN")
    if not token:
        log.warning("GUMROAD_ACCESS_TOKEN not set — skipping Gumroad publish")
        return None

    price = _calc_price(vertical)
    description = _build_description(vertical, csv_path)

    try:
        resp = httpx.post(f"{GUMROAD_API}/products", headers=_headers(), data={
            "name": title,
            "description": description,
            "price": price,
            "currency": "usd",
            "published": "true",
            "tags[]": [vertical, "b2b", "leads", "intent"],
        }, timeout=30)
        resp.raise_for_status()
        product = resp.json()["product"]
        product_id = product["id"]
        log.info(f"Gumroad product created: {product_id}")

        file_path = Path(csv_path)
        if file_path.exists():
            with open(file_path, "rb") as f:
                upload = httpx.put(
                    f"{GUMROAD_API}/products/{product_id}/files",
                    headers=_headers(),
                    files={"file": (file_path.name, f, "text/csv")},
                    timeout=60,
                )
                upload.raise_for_status()

        md_path = Path(csv_path).with_suffix(".md")
        if md_path.exists():
            with open(md_path, "rb") as f:
                httpx.put(
                    f"{GUMROAD_API}/products/{product_id}/files",
                    headers=_headers(),
                    files={"file": (md_path.name, f, "text/markdown")},
                    timeout=60,
                )

        product_url = f"https://app.gumroad.com/products/{product_id}"
        with db() as conn:
            conn.execute("""
                UPDATE outputs SET gumroad_id = ?, published_url = ?
                WHERE file_path = ?
            """, (product_id, product_url, csv_path))

        return product_url

    except Exception as e:
        log.error(f"Gumroad publish failed: {e}")
        return None


def _calc_price(vertical: str) -> int:
    prices = {
        "devtools": 2900,
        "saas_analytics": 3900,
        "marketing_automation": 2900,
        "cloud_infra": 4900,
        "cybersecurity": 4900,
        "hr_recruiting": 2900,
        "ecommerce_tools": 1900,
        "ai_ml_tools": 3900,
    }
    return prices.get(vertical, 1900)


def _build_description(vertical: str, csv_path: str) -> str:
    with db() as conn:
        row = conn.execute("""
            SELECT COUNT(*) as cnt FROM outputs WHERE vertical = ? AND type = 'lead_pack'
        """, (vertical,)).fetchone()
        count = row["cnt"] if row else 0

    v_display = vertical.replace("_", " ").title()
    return f"""
## {v_display} Buyer Intent Pack

**What you get:** A fresh CSV of {v_display} companies and individuals who are actively looking for a solution — pulled from Reddit, HackerNews, GitHub, and StackOverflow in the last 7 days.

Each lead includes:
- Source URL (so you can see the context)
- Intent score (0-100)
- Estimated deal value
- Buyer role
- Recommended outreach angle

**Who buys this:** Agencies, consultants, and SaaS companies looking for warm prospects who have already expressed interest in their category.

**Updated:** Weekly. This is pack #{count + 1} for this vertical.

**Refund policy:** 7-day full refund if you're unsatisfied with signal quality.
""".strip()
