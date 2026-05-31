"""
Fix body background: add inline dark background to ALL pages so dark theme
is instantaneous and not dependent on CSS variable resolution timing.

Also adds class="sp-bg" to body for the overlay gradient.

Run: uv run python scripts/fix_body_background.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

# The fix: replace plain <body> or <body class="sp-bg"> with a version
# that has both the class AND an inline background color
BODY_WITH_BG = '<body class="sp-bg" style="background:#050407;color:#fff7f8">'

fixed = 0
skipped = 0

all_html = list((SITE / "pages").glob("*.html")) + \
           list((SITE / "blog").glob("*.html")) + \
           list((SITE / "authors").glob("*.html"))

for fp in sorted(all_html):
    content = fp.read_text(encoding="utf-8", errors="replace")

    # Skip if already has inline background on body
    if 'style="background:#050407' in content:
        skipped += 1
        continue

    # Skip noindex preview/utility pages
    if "v3-preview" in fp.name:
        skipped += 1
        continue

    original = content

    # Replace all body tag variants with the fixed version
    # Handles: <body>, <body class="sp-bg">, <body class="sp-bg" style="...">
    content = re.sub(
        r'<body(?:\s+class="sp-bg")?(?:\s+style="[^"]*")?(?:\s*)>',
        BODY_WITH_BG,
        content,
        count=1
    )

    # Also ensure saaspare-v2 pages have --bg-deep as a CSS var fallback
    # in case CSS hasn't loaded yet
    if content != original:
        fp.write_text(content, encoding="utf-8")
        fixed += 1

print(f"Fixed body background: {fixed} pages")
print(f"Already correct / skipped: {skipped}")
