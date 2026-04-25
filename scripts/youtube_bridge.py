"""
Bridge intent-engine's published pages to the sibling affiliate-engine's YouTube
content flow.

This writes a canonical manifest inside this repo and, when a sibling
`affiliate-engine` checkout exists, syncs a copy there as well.
"""
import json
import re
import time
from pathlib import Path

from core.db import db
from core.secrets import get

AFFILIATE_ENGINE_DIR = Path(__file__).parent.parent.parent / "affiliate-engine"
BRIDGE_OUTPUT = AFFILIATE_ENGINE_DIR / "config" / "saaspare_links.json"
LOCAL_OUTPUT = Path("outputs/generated/youtube_bridge.json")

STOPWORDS = {
    "2026", "2025", "saaspare", "pricing", "review", "reviews", "coupon",
    "code", "promo", "plans", "costs", "what", "actually", "pay",
    "which", "better", "best", "free", "paid", "full", "breakdown",
    "vs", "software", "tool", "tools", "comparison", "comparisons",
    "alternative", "alternatives", "trial", "guide", "honest", "verdict",
}


def slugify_simple(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-")


def clean_title(title: str) -> str:
    return re.sub(r"\s*\|\s*SaaSpare\s*$", "", (title or "").strip(), flags=re.IGNORECASE)


def infer_page_type(title: str) -> str:
    lowered = title.lower()
    if " vs " in lowered:
        return "comparison"
    if "pricing" in lowered or "cost" in lowered:
        return "pricing"
    if "review" in lowered:
        return "review"
    if "coupon" in lowered or "promo" in lowered:
        return "coupon"
    if "alternative" in lowered:
        return "alternatives"
    if "free plan" in lowered or "free trial" in lowered:
        return "free_plan"
    if lowered.startswith("best "):
        return "bestof"
    return "page"


def page_keywords(title: str, vertical: str) -> list[str]:
    tokens = []
    for token in slugify_simple(title).split("-"):
        if len(token) < 4 or token in STOPWORDS:
            continue
        if token not in tokens:
            tokens.append(token)
    if vertical and vertical not in tokens:
        tokens.append(vertical)
    return tokens[:10]


def _load_pages() -> list[dict]:
    with db() as conn:
        rows = conn.execute(
            """
            SELECT title, published_url, vertical, created_at
            FROM outputs
            WHERE type = 'seo_page'
              AND published_url IS NOT NULL
            ORDER BY created_at DESC
        """
        ).fetchall()

    seen_urls: set[str] = set()
    pages: list[dict] = []
    for row in rows:
        url = (row["published_url"] or "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        title = clean_title(row["title"] or "")
        slug = url.rstrip("/").split("/")[-1]
        pages.append(
            {
                "title": title,
                "url": url,
                "slug": slug,
                "vertical": row["vertical"] or "unknown",
                "page_type": infer_page_type(title),
                "keywords": page_keywords(title, row["vertical"] or "unknown"),
            }
        )
    return pages


def build_page_index() -> dict:
    domain = get("SITE_DOMAIN", "https://saaspare.org")
    pages = _load_pages()
    lookup: dict[str, str] = {}

    for page in pages:
        url = page["url"]
        title_slug = slugify_simple(clean_title(page["title"]))
        if title_slug:
            lookup.setdefault(title_slug, url)
        if page["slug"]:
            lookup.setdefault(page["slug"], url)
        for keyword in page["keywords"]:
            lookup.setdefault(keyword, url)

    return {
        "site": domain,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total": len(pages),
        "pages": lookup,
        "records": pages,
    }


def write_manifest() -> dict:
    data = build_page_index()
    LOCAL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {data['total']} canonical pages -> {LOCAL_OUTPUT}")

    if AFFILIATE_ENGINE_DIR.exists():
        config_dir = AFFILIATE_ENGINE_DIR / "config"
        config_dir.mkdir(exist_ok=True)
        BRIDGE_OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"Synced to affiliate-engine -> {BRIDGE_OUTPUT}")
        _patch_affiliate_engine_descriptions()
    else:
        print("affiliate-engine not found at expected path - skipped sibling sync")
    return data


def _patch_affiliate_engine_descriptions():
    """Create the helper module consumed by the sibling content engine."""
    helper_path = AFFILIATE_ENGINE_DIR / "core" / "saaspare_helper.py"
    if helper_path.exists():
        return

    helper_path.write_text(
        '''"""
Injects saaspare.org comparison page links into YouTube video descriptions.
Loaded automatically by content_generator.py if present.
"""
import json
from pathlib import Path

_BRIDGE_PATH = Path(__file__).parent.parent / "config" / "saaspare_links.json"
_data: dict = {}


def _load():
    global _data
    if _data:
        return
    if _BRIDGE_PATH.exists():
        try:
            _data = json.loads(_BRIDGE_PATH.read_text(encoding="utf-8"))
        except Exception:
            _data = {}


def get_comparison_link(topic: str) -> str | None:
    _load()
    pages = _data.get("pages", {})
    slug = topic.lower().strip().replace(" ", "-")
    if slug in pages:
        return pages[slug]
    for word in slug.split("-"):
        if len(word) > 4 and word in pages:
            return pages[word]
    return None


def description_footer(topic: str) -> str:
    link = get_comparison_link(topic)
    if link:
        return f"\\n\\nFull software comparison & pricing breakdown: {link}"
    site = _data.get("site", "https://saaspare.org")
    return f"\\n\\nMore SaaS comparisons & pricing breakdowns: {site}"
''',
        encoding="utf-8",
    )
    print("Created saaspare_helper.py in affiliate-engine")


def main():
    write_manifest()


if __name__ == "__main__":
    main()
