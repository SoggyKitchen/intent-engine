import time
import uuid
from pathlib import Path

import yaml

from core.db import db
from core.logger import log
from core.secrets import MONETIZATION_MODE
from outputs.lead_pack import generate as gen_lead_pack
from outputs.seo_page import generate_from_cluster, find_clusters
from publisher.gumroad import publish_lead_pack
from publisher.pages_deploy import deploy_all

NICHES_FILE = Path("config/niches.yaml")


def run():
    run_id = str(uuid.uuid4())[:8]
    with db() as conn:
        conn.execute(
            "INSERT INTO runs (id, job, started_at) VALUES (?, 'publish', ?)",
            (run_id, int(time.time())),
        )

    niches = _load_active_niches()
    seo_pages_generated = 0
    lead_packs_generated = 0
    deployed = False

    try:
        for niche in niches:
            vertical = niche["vertical"]
            log.info(f"Processing vertical: {vertical}")

            clusters = find_clusters(vertical, min_size=3)
            pages_today = _seo_count_today(vertical)
            max_pages_per_vertical_per_day = 4

            for cluster in clusters:
                if pages_today >= max_pages_per_vertical_per_day:
                    break
                page_path = generate_from_cluster(vertical, cluster)
                if page_path:
                    seo_pages_generated += 1
                    pages_today += 1
                    log.info(f"SEO page: {page_path}")

            if MONETIZATION_MODE in ("full", "parent_holds_account") and _enough_signals_for_pack(vertical):
                pack_path = gen_lead_pack(vertical)
                if pack_path:
                    title = f"{vertical.replace('_', ' ').title()} Buyer Intent Pack - {time.strftime('%b %d')}"
                    url = publish_lead_pack(pack_path, vertical, title)
                    if url:
                        lead_packs_generated += 1
                        log.info(f"Lead pack published: {url}")

        if seo_pages_generated > 0:
            deployed = deploy_all()

        with db() as conn:
            conn.execute(
                """
                UPDATE runs SET ended_at = ?, status = 'ok', signals_in = ?, signals_out = ?
                WHERE id = ?
                """,
                (int(time.time()), len(niches), seo_pages_generated + lead_packs_generated, run_id),
            )

        log.info(
            f"Publish job done: {seo_pages_generated} SEO pages, "
            f"{lead_packs_generated} lead packs, deployed={deployed}"
        )
    except Exception as e:
        with db() as conn:
            conn.execute(
                """
                UPDATE runs SET ended_at = ?, status = 'error', signals_in = ?, signals_out = ?, error = ?
                WHERE id = ?
                """,
                (
                    int(time.time()),
                    len(niches),
                    seo_pages_generated + lead_packs_generated,
                    str(e)[:500],
                    run_id,
                ),
            )
        raise


def _load_active_niches() -> list[dict]:
    if not NICHES_FILE.exists():
        return []
    with open(NICHES_FILE) as f:
        cfg = yaml.safe_load(f)
    return [n for n in cfg.get("niches", []) if n.get("active", True)]


def _seo_count_today(vertical: str) -> int:
    today_start = int(time.time()) - 86400
    with db() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) FROM outputs
            WHERE vertical = ? AND type = 'seo_page' AND created_at >= ?
            """,
            (vertical, today_start),
        ).fetchone()
    return row[0]


def _enough_signals_for_pack(vertical: str) -> bool:
    since_ts = int(time.time()) - 7 * 86400
    with db() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) FROM scored_signals
            WHERE vertical = ? AND ts >= ? AND profit_score >= 8
            """,
            (vertical, since_ts),
        ).fetchone()
    return row[0] >= 10
