"""
inject_itemlist_schema.py
Add ItemList schema to "7-best-*-alternatives-*" pages in site/pages/.
Extracts tool names from <div class="tool-card ..."><h2>...</h2> patterns.
Idempotent — skips pages that already contain ItemList schema.
"""
import re
import json
from pathlib import Path

SITE = Path(__file__).parent.parent / "site"
PAGES = SITE / "pages"
BASE = "https://saaspare.org"

TOOL_NAME_RE = re.compile(
    r'<div[^>]*class="[^"]*tool-card[^"]*"[^>]*>\s*<h2[^>]*>(.*?)</h2>',
    re.DOTALL | re.IGNORECASE,
)

injected = 0
skipped = 0

for html in sorted(PAGES.glob("7-best-*-alternatives-*.html")):
    text = html.read_text(encoding="utf-8", errors="replace")

    if "ItemList" in text:
        skipped += 1
        continue

    # Extract tool names
    names = []
    for m in TOOL_NAME_RE.finditer(text):
        raw = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip()
        if raw and raw not in names:
            names.append(raw)

    if len(names) < 2:
        print(f"  SKIP (no tools found): {html.name}")
        skipped += 1
        continue

    # Build ItemList schema
    # Derive the page canonical URL from the existing canonical link
    canonical_m = re.search(r'<link rel="canonical" href="([^"]+)"', text)
    page_url = canonical_m.group(1) if canonical_m else f"{BASE}/pages/{html.stem}"

    items = [
        {
            "@type": "ListItem",
            "position": i + 1,
            "name": name,
            "url": page_url,
        }
        for i, name in enumerate(names[:7])
    ]
    schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"Best Alternatives — {html.stem}",
        "url": page_url,
        "numberOfItems": len(items),
        "itemListElement": items,
    }
    block = (
        f'\n<script type="application/ld+json">'
        f"{json.dumps(schema, ensure_ascii=False)}"
        f"</script>"
        f"\n<!-- itemlist-v1 -->"
    )

    # Inject just before </head>
    if "</head>" not in text:
        print(f"  SKIP (no </head>): {html.name}")
        skipped += 1
        continue

    text = text.replace("</head>", block + "\n</head>", 1)
    html.write_text(text, encoding="utf-8")
    print(f"  injected ({len(items)} items): {html.name}")
    injected += 1

print(f"\nDone. Injected: {injected}  Skipped: {skipped}")
