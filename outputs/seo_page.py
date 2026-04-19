import hashlib
import json
import re
import time
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader
from slugify import slugify

from core.db import db
from core.logger import log
from core.secrets import DRY_RUN, get
from llm.router import complete_json
from publisher.affiliate_registry import get_go_url, get_links_for_vertical, get_best_programs_for_vertical

TEMPLATE_DIR = Path(__file__).parent / "templates"
SITE_DIR = Path("site/pages")
AMAZON_TAG = get("AMAZON_ASSOCIATE_TAG", "yourtag-22")
_JINJA_ENV = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


def _affiliate_url(tool_name: str, base_url: str, vertical: str = "", page_type: str = "comparison") -> str:
    utm = f"utm_source=saaspare&utm_medium=affiliate&utm_campaign={page_type}&utm_content={slugify(tool_name)}"
    if "amazon.com" in base_url:
        sep = "&" if "?" in base_url else "?"
        return f"{base_url}{sep}tag={AMAZON_TAG}&{utm}"
    go = get_go_url(tool_name)
    if go:
        return f"{go}?{utm}"
    if vertical:
        links = get_links_for_vertical(vertical, [tool_name])
        if tool_name in links and links[tool_name] != base_url:
            url = links[tool_name]
            sep = "&" if "?" in url else "?"
            return f"{url}{sep}{utm}"
    if base_url and base_url != "#":
        sep = "&" if "?" in base_url else "?"
        return f"{base_url}{sep}{utm}"
    return base_url


def _get_related_pages(vertical: str, current_slug: str, limit: int = 6) -> list[dict]:
    try:
        domain = get("SITE_DOMAIN", "https://saaspare.org")
        with db() as conn:
            rows = conn.execute("""
                SELECT title FROM outputs
                WHERE vertical = ? AND type = 'seo_page' AND title NOT LIKE ?
                ORDER BY created_at DESC LIMIT ?
            """, (vertical, f"%{current_slug[:20]}%", limit)).fetchall()
        result = []
        for row in rows:
            s = slugify(row[0])
            result.append({"title": row[0], "url": f"{domain}/pages/{s}"})
        return result
    except Exception:
        return []


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
      "winner": <true for top recommendation, false for others>
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

Include 2-4 real tools. Make it genuinely useful.
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

    pk = data.get("primary_keyword", title).lower()
    page_type = (
        "comparison" if " vs " in pk else
        "pricing"    if "pricing" in pk or "cost" in pk else
        "review"     if "review" in pk else
        "coupon"     if "coupon" in pk or "promo" in pk else
        "bestof"     if "best " in pk else
        "alternatives" if "alternative" in pk else "page"
    )

    if cta_tool:
        data["cta_url"] = _affiliate_url(cta_tool["name"], cta_tool.get("homepage", "#"), vertical, page_type)
        for tool in data.get("tools", []):
            tool["affiliate_url"] = _affiliate_url(tool["name"], tool.get("homepage", "#"), vertical, page_type)

    domain = get("SITE_DOMAIN", "https://saaspare.org")
    canonical = f"{domain}/pages/{slug}"
    data["canonical_url"] = canonical
    data["title"] = title
    data["page_type"] = page_type
    data["updated_date"] = time.strftime("%B %d, %Y")
    data["updated_iso"] = time.strftime("%Y-%m-%d")
    data["site_domain"] = domain
    data["schema_json"] = _build_schema(data, domain, canonical)
    data["related_pages"] = _get_related_pages(vertical, slug)
    data["brevo_form_id"] = get("BREVO_FORM_ID", "")
    data["ga_id"] = get("GA_MEASUREMENT_ID", "")

    tmpl = _JINJA_ENV.get_template("comparison_page.html.j2")
    html = tmpl.render(**data)

    if DRY_RUN:
        log.info(f"[DRY RUN] Would write SEO page: {out_path}")
        return str(out_path)

    out_path.write_text(html, encoding="utf-8")
    log.info(f"SEO page written: {out_path}")

    page_id = hashlib.sha256(slug.encode()).hexdigest()[:12]
    with db() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO outputs
              (id, type, vertical, title, file_path, published_url, created_at)
            VALUES (?, 'seo_page', ?, ?, ?, ?, ?)
        """, (page_id, vertical, title, str(out_path), canonical, int(time.time())))

    return str(out_path)


def _build_schema(data: dict, domain: str = "https://saaspare.org", canonical: str = "") -> str:
    tools = data.get("tools", [])
    reviews = []
    for i, t in enumerate(tools):
        reviews.append({
            "@type": "Review",
            "itemReviewed": {"@type": "SoftwareApplication", "name": t.get("name", ""),
                             "applicationCategory": "BusinessApplication"},
            "reviewRating": {"@type": "Rating", "ratingValue": round(5 - i * 0.3, 1), "bestRating": 5},
            "author": {"@type": "Organization", "name": "SaaSpare"},
            "reviewBody": t.get("description", "")[:400],
        })
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": data.get("page_title", ""),
        "description": data.get("meta_description", ""),
        "datePublished": time.strftime("%Y-%m-%d"),
        "dateModified": time.strftime("%Y-%m-%d"),
        "author": {"@type": "Organization", "name": "SaaSpare",
                   "url": get("SITE_DOMAIN", "https://saaspare.org")},
        "publisher": {"@type": "Organization", "name": "SaaSpare",
                      "logo": {"@type": "ImageObject",
                               "url": f"{get('SITE_DOMAIN', 'https://saaspare.org')}/logo.png"}},
        "review": reviews,
    }
    if data.get("faqs"):
        schema["mainEntity"] = [
            {"@type": "Question", "name": f["question"],
             "acceptedAnswer": {"@type": "Answer", "text": f["answer"]}}
            for f in data["faqs"]
        ]
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": domain},
            {"@type": "ListItem", "position": 2, "name": "Comparisons", "item": f"{domain}/pages/"},
            {"@type": "ListItem", "position": 3, "name": data.get("page_title", ""), "item": canonical or domain},
        ]
    }
    return json.dumps([schema, breadcrumb])


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
              AND s.intent >= 35
            ORDER BY s.profit_score DESC
            LIMIT 100
        """, (vertical, since_ts)).fetchall()

    if len(rows) < min_size:
        return []

    rows_list = [dict(r) for r in rows]
    clusters = []
    chunk = max(min_size, 8)
    for i in range(0, len(rows_list), chunk):
        c = rows_list[i:i + chunk]
        if len(c) >= min_size:
            clusters.append(c)
        if len(clusters) >= 4:
            break
    return clusters
