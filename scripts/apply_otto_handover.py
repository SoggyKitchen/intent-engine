"""Bake SearchAtlas/OTTO handover SEO into static files.

This is intentionally safe and repeatable:
  - removes the OTTO dynamic optimization pixel from static HTML
  - applies exact exported title/meta rows when available
  - applies pattern-generated title/meta to generated comparison pages

Run after importing a fresh SearchAtlas CSV export:
  python scripts/apply_otto_handover.py
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT))

from publisher.seo_tags import get_seo_tags
OTTO_PIXEL_RE = re.compile(r'\s*<script[^>]*id="sa-dynamic-optimization"[^>]*></script>', re.IGNORECASE)


def _url_for_file(path: Path) -> str:
    rel = path.relative_to(SITE).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[:-10].strip("/")
    if rel.endswith(".html"):
        rel = rel[:-5]
    return "/" + rel.strip("/")


def _replace_or_insert_meta(source: str, name: str, content: str) -> str:
    escaped = html.escape(content, quote=True)
    pattern = re.compile(
        rf'<meta\s+name="{re.escape(name)}"\s+content="[^"]*"\s*/?>',
        re.IGNORECASE,
    )
    replacement = f'<meta name="{name}" content="{escaped}">'
    if pattern.search(source):
        return pattern.sub(replacement, source, count=1)
    return source.replace("</title>", f"</title>\n{replacement}", 1)


def _replace_or_insert_og(source: str, prop: str, content: str) -> str:
    escaped = html.escape(content, quote=True)
    pattern = re.compile(
        rf'<meta\s+property="{re.escape(prop)}"\s+content="[^"]*"\s*/?>',
        re.IGNORECASE,
    )
    replacement = f'<meta property="{prop}" content="{escaped}">'
    if pattern.search(source):
        return pattern.sub(replacement, source, count=1)
    return source.replace("</head>", f"{replacement}\n</head>", 1)


def _patch_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8", errors="ignore")
    source = OTTO_PIXEL_RE.sub("", original)
    url_path = _url_for_file(path)

    current_title = ""
    title_match = re.search(r"<title>([^<]*)</title>", source, re.IGNORECASE)
    if title_match:
        current_title = html.unescape(title_match.group(1)).removesuffix(" | SaaSpare")
    meta_match = re.search(
        r'<meta\s+name="description"\s+content="([^"]*)"\s*/?>',
        source,
        re.IGNORECASE,
    )
    current_meta = html.unescape(meta_match.group(1)) if meta_match else ""

    tags = get_seo_tags(
        url_path,
        product_name=None,
        fallback_title=current_title,
        fallback_meta=current_meta,
    )
    title = tags["title"]
    if not title.endswith("| SaaSpare"):
        title = f"{title} | SaaSpare"
    title = html.escape(title, quote=False)
    if title_match:
        source = re.sub(r"<title>[^<]*</title>", f"<title>{title}</title>", source, count=1, flags=re.IGNORECASE)
    else:
        source = source.replace("<head>", f"<head>\n<title>{title}</title>", 1)

    source = _replace_or_insert_meta(source, "description", tags["meta_description"])
    source = _replace_or_insert_og(source, "og:title", html.unescape(title))
    source = _replace_or_insert_og(source, "og:description", tags["meta_description"])

    if source != original:
        path.write_text(source, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for path in sorted(SITE.glob("*.html")) + sorted((SITE / "pages").glob("*.html")):
        if _patch_file(path):
            changed += 1
    print(f"OTTO handover applied to {changed} HTML files")


if __name__ == "__main__":
    main()
