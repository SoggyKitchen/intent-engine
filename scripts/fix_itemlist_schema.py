"""
Add ItemList schema to all 7-best and *-alternatives pages.

Extracts tool names from H2 headings, creates ListItem entries pointing
to each tool's pricing page. Google uses this for "Top picks" rich results.

Run: python scripts/fix_itemlist_schema.py
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASE_URL = "https://saaspare.org"

# H2s to skip — structural, not tool names
SKIP_H2_LOWER = {
    "quick comparison", "our top pick", "frequently asked questions",
    "how saaspare keeps this page useful", "related comparisons",
    "continue your evaluation", "ready to decide?", "ready to choose?",
    "subscribe to the deal digest", "before you go", "before you go — the honest saas deals weekly",
    "pricing breakdown", "key features worth knowing", "our verdict",
    "who should use it", "the bottom line", "alternatives we compared",
    "methodology", "how we ranked these", "what to look for",
    "get the weekly saas deal digest", "compare all options",
    "top pick", "editor's choice",
}

# Suffix patterns that signal a structural h2, not a tool
STRUCTURAL_PATTERNS = [
    r'^(?:get|see|compare|subscribe|sign|read|learn|find|start)\b',
    r'why\s+we',
    r'how\s+(we|to)',
    r'what\s+(is|are|to)',
    r'^\d{1,2}\.',      # numbered sections
    r'best\s+\w+\s+(for|if|when)\b',
    r'vs\.\s+',
    r'alternatives?\s+to\b',
]

stats = {"patched": 0, "already_done": 0, "skipped": 0}


def clean_h2(raw: str) -> str:
    """Strip HTML tags and common suffixes like 'Top Pick', 'Review'."""
    text = re.sub(r'<[^>]+>', '', raw).strip()
    text = re.sub(r'\s*(Top Pick|Review|\(Best\)|\(Recommended\)|\(Editor.*?\))$', '', text, flags=re.IGNORECASE).strip()
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&mdash;', '—', text)
    return text


def is_structural(h2: str) -> bool:
    low = h2.lower().strip()
    if low in SKIP_H2_LOWER:
        return True
    if len(low) < 3:
        return True
    for pat in STRUCTURAL_PATTERNS:
        if re.search(pat, low):
            return True
    return False


def tool_slug_from_name(name: str) -> str:
    """Convert tool name to URL slug."""
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')
    slug = re.sub(r'\.', '', slug)
    return slug


def find_tool_url(tool_name: str) -> str:
    """Look for an existing pricing page URL, fallback to search."""
    slug = tool_slug_from_name(tool_name)
    # Try pricing page first
    pricing_pattern = f"{slug}-pricing-"
    candidates = list((SITE / "pages").glob(f"{slug}-pricing-*.html"))
    if candidates:
        return f"{BASE_URL}/pages/{candidates[0].stem}"
    # Try review page
    review_candidates = list((SITE / "pages").glob(f"{slug}-review-*.html"))
    if review_candidates:
        return f"{BASE_URL}/pages/{review_candidates[0].stem}"
    # Fallback
    return f"{BASE_URL}/pages/{slug}-pricing-2026-plans-costs-what-you-actually-pay"


def extract_list_items(html: str, page_url: str) -> list:
    """Extract tool names from H2 headings on the page."""
    h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL)
    items = []
    position = 1
    for raw_h2 in h2s:
        name = clean_h2(raw_h2)
        if not name or is_structural(name):
            continue
        # Skip very long h2s (likely sentences, not tool names)
        if len(name) > 60:
            continue
        # Only include if looks like a proper noun / tool name (has capitals)
        if not re.search(r'[A-Z]', name):
            continue
        items.append({
            "@type": "ListItem",
            "position": position,
            "name": name,
            "url": find_tool_url(name),
        })
        position += 1
    return items


def patch_list_page(path: Path) -> bool:
    try:
        html = path.read_text(encoding="utf-8")
    except Exception:
        return False

    if "ItemList" in html:
        stats["already_done"] += 1
        return False

    page_url = f"{BASE_URL}/pages/{path.stem}"
    items = extract_list_items(html, page_url)

    if len(items) < 3:
        stats["skipped"] += 1
        return False

    # Build ItemList schema
    item_list_schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": re.sub(r'-', ' ', path.stem).title(),
        "url": page_url,
        "numberOfItems": len(items),
        "itemListElement": items,
    }
    new_block = f'\n<script type="application/ld+json">\n{json.dumps(item_list_schema, indent=2, ensure_ascii=False)}\n</script>'

    # Inject before </head>
    if "</head>" in html:
        html = html.replace("</head>", new_block + "\n</head>", 1)
    else:
        return False

    path.write_text(html, encoding="utf-8")
    stats["patched"] += 1
    return True


def main():
    targets = (
        list((SITE / "pages").glob("7-best-*.html")) +
        list((SITE / "pages").glob("*-alternatives-*.html"))
    )
    # Also patch category hub pages
    targets += list(SITE.glob("best-*-2026.html"))

    print(f"Processing {len(targets)} list pages...")
    for p in targets:
        patch_list_page(p)

    print(f"\nResults:")
    print(f"  ItemList schema added:     {stats['patched']}")
    print(f"  Already had ItemList:      {stats['already_done']}")
    print(f"  Skipped (<3 tool items):   {stats['skipped']}")


if __name__ == "__main__":
    main()
