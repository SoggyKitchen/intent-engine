"""
Bridge intent-engine's published pages to affiliate-engine's YouTube content.

Run: uv run python scripts/youtube_bridge.py

Exports a JSON file that affiliate-engine reads to inject saaspare.org
comparison page links into YouTube video descriptions, driving backlink
traffic from YouTube to the site.
"""
import json
import re
from pathlib import Path

from core.db import db
from core.secrets import get

AFFILIATE_ENGINE_DIR = Path(__file__).parent.parent.parent / "affiliate-engine"
BRIDGE_OUTPUT = AFFILIATE_ENGINE_DIR / "config" / "saaspare_links.json"
LOCAL_OUTPUT = Path("outputs/generated/youtube_bridge.json")


def slugify_simple(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-")


def build_page_index() -> dict:
    domain = get("SITE_DOMAIN", "https://saaspare.org")
    index: dict[str, str] = {}

    with db() as conn:
        pages = conn.execute(
            """
            SELECT title, published_url, vertical
            FROM outputs
            WHERE type = 'seo_page'
              AND published_url IS NOT NULL
            ORDER BY created_at DESC
        """
        ).fetchall()

    for page in pages:
        url = page["published_url"] or ""
        if not url:
            continue
        title = page["title"] or ""
        vertical = page["vertical"] or ""
        title_slug = slugify_simple(title)
        index[title_slug] = url
        if vertical:
            index.setdefault(vertical, url)
        words = [w for w in title_slug.split("-") if len(w) > 3]
        for word in words:
            index.setdefault(word, url)

    return {"site": domain, "pages": index, "total": len(pages)}


def main():
    data = build_page_index()

    LOCAL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {data['total']} pages → {LOCAL_OUTPUT}")

    if AFFILIATE_ENGINE_DIR.exists():
        config_dir = AFFILIATE_ENGINE_DIR / "config"
        config_dir.mkdir(exist_ok=True)
        BRIDGE_OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"Synced to affiliate-engine → {BRIDGE_OUTPUT}")
        _patch_affiliate_engine_descriptions()
    else:
        print("affiliate-engine not found at expected path — skipping sync")


def _patch_affiliate_engine_descriptions():
    """Inject saaspare.org link helper into affiliate-engine's content generator."""
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
    """Return saaspare.org comparison URL for a topic, or None."""
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
        return f"\\n\\n📊 Full software comparison & pricing breakdown: {link}"
    site = _data.get("site", "https://saaspare.org")
    return f"\\n\\n📊 More SaaS comparisons & pricing breakdowns: {site}"
''',
        encoding="utf-8",
    )
    print(f"Created saaspare_helper.py in affiliate-engine")


if __name__ == "__main__":
    main()
