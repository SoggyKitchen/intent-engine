import hashlib
import json
import re
import time
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader
from python_slugify import slugify

from core.db import db
from core.logger import log
from core.secrets import DRY_RUN, get
from llm.router import complete_json
from publisher.affiliate_registry import get_links_for_vertical, get_best_programs_for_vertical

TEMPLATE_DIR = Path(__file__).parent / "templates"
SITE_DIR = Path("site/pages")
AMAZON_TAG = get("AMAZON_ASSOCIATE_TAG", "yourtag-22")


def _affiliate_url(tool_name: str, base_url: str, vertical: str = "") -> str:
    if "amazon.com" in base_url:
        sep = "&" if "?" in base_url else "?"
        return f"{base_url}{sep}tag={AMAZON_TAG}"
    if vertical:
        links = get_links_for_vertical(vertical, [tool_name])
        if tool_name in links and links[tool_name] != base_url:
            return links[tool_name]
    return base_url


def generate_from_cluster(vertical: str, topic_cluster: list[dict]) -> Optional[str]:
    titles = [s["title"] for s in topic_cluster[:8]]
    bodies = [s["body"] for s in topic_cluster[:4]]
    context = "\n---\n".join(f"Title: {t}\nBody: {b[:400]}" for t, b in zip(titles, bodies))

    prompt = f"""You are an expert SEO content strategist for B2B software.

Analyze these public discussions about {vertical.replace('_', ' ')} tools:

{context}

Generate a comparison page structure. Return JSON exactly:
{{
  "page_title": "<compelling comparison title, e.g. 'Best X for Y in 2025'>",
  "meta_description": "<160-char SEO meta description>",
  "subtitle": "<one sentence explaining what this page covers>",
  "tldr": "<2-sentence verdict a busy reader can act on>",
  "tools": [
    {{
      "name": "<tool name>",
      "description": "<2-3 sentence description>",
      "pros": ["<pro1>", "<pro2>", "<pro3>"],
      "cons": ["<con1>", "<con2>"],
      "pricing": "<brief pricing summary>",
      "homepage": "<official homepage url>",
      "winner": <true for the top recommendation, false for others>
    }}
  ],
  "comparison_features": [
    {{"name": "<feature>", "values": ["<tool1 val>", "<tool2 val>"]}}
  ],
  "verdict": "<2-3 sentence overall recommendation>",
  "faqs": [
    {{"question": "<question>", "answer": "<answer>"}}
  ],
  "cta_text": "<call to action paragraph>",
  "cta_button": "<button text like 'Start Free Trial'>",
  "primary_keyword": "<main SEO keyword>",
  "secondary_keywords": ["<kw2>", "<kw3>"]
}}

Include 2-4 real tools the community is discussing. Make it genuinely useful.
"""
    result = complete_json(prompt)
    if not result:
        return None

    return _render_and_save(result, vertical)


def _render_and_save(data: dict, vertical: str) -> Optional[str]:
    SITE_DIR.mkdir(parents=True, exist_ok=True)

    title = data.get("page_title", "")
    if not title:
        return None

    slug = slugify(title)
    out_path = SITE_DIR / f"{slug}.html"

    winner = next((t for t in data.get("tools", []) if t.get("winner")), None)
    cta_tool = winner or (data["tools"][0] if data.get("tools") else None)

    if cta_tool:
        data["cta_url"] = _affiliate_url(cta_tool["name"], cta_tool.get("homepage", "#"), vertical)
        for tool in data.get("tools", []):
            tool["affiliate_url"] = _affiliate_url(tool["name"], tool.get("homepage", "#"), vertical)

    data["canonical_url"] = f"https://yourdomain.com/{slug}"
    data["updated_date"] = time.strftime("%B %d, %Y")
    data["schema_json"] = _build_schema(data)

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    tmpl = env.get_template("comparison_page.html.j2")
    html = tmpl.render(**data)

    if DRY_RUN:
        log.info(f"[DRY RUN] Would write SEO page: {out_path}")
        return str(out_path)

    out_path.write_text(html, encoding="utf-8")
    log.info(f"SEO page written: {out_path}")

    page_id = hashlib.sha256(slug.encode()).hexdigest()[:12]
    with db() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO outputs (id, type, vertical, title, file_path, created_at)
            VALUES (?, 'seo_page', ?, ?, ?, ?)
        """, (page_id, vertical, title, str(out_path), int(time.time())))

    return str(out_path)


def _build_schema(data: dict) -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": data.get("page_title", ""),
        "description": data.get("meta_description", ""),
        "dateModified": time.strftime("%Y-%m-%d"),
        "author": {"@type": "Organization", "name": "IntentEngine"},
    }
    return json.dumps(schema)


def find_clusters(vertical: str, min_size: int = 5) -> list[list[dict]]:
    since_ts = int(time.time()) - 7 * 86400
    with db() as conn:
        rows = conn.execute("""
            SELECT s.vertical, s.profit_score, r.title, r.body, r.url, r.source
            FROM scored_signals s
            JOIN raw_signals r ON r.id = s.raw_id
            WHERE s.vertical = ?
              AND s.ts >= ?
              AND s.monetization_path IN ('affiliate', 'lead_pack')
              AND s.intent >= 50
            ORDER BY s.profit_score DESC
            LIMIT 100
        """, (vertical, since_ts)).fetchall()

    if len(rows) < min_size:
        return []

    clusters = [list(map(dict, rows))]
    return clusters
