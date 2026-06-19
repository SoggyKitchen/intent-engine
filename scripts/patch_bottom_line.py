"""
One-off patch: inject a visible "Bottom line:" paragraph into all premium
pricing pages that already have the sticky-bottom-cta markup.

AEO rationale: "Bottom line:" bolded at top of a section gets quoted by AI
models (Perplexity, Google AI Overviews). Currently the sticky text is only
in a JS-hidden footer — invisible to crawlers. This surfaces it as a real
first-paragraph signal right above the plans table.

Idempotent — pages already containing pr-bottom-line are skipped.
"""
from pathlib import Path
import re

SITE = Path(__file__).resolve().parents[1] / "site" / "pages"

# Marker that indicates a premium pricing page (generator skip pattern)
PREMIUM_MARKER = "pr-layout"

# Anchor: inject before the plans table
INSERT_BEFORE = '<div id="plans">'

# Snippet to extract the sticky verdict text
STICKY_RE = re.compile(
    r'<strong>[^<]+ Pricing 2026</strong>\s*[—–-]\s*(.+?)\s*</div>',
    re.DOTALL
)

BOTTOM_LINE_HTML = '<p class="pr-bottom-line"><strong>Bottom line:</strong> {text}</p>\n\n        '


def patch_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="replace")

    # Only touch premium pricing pages
    if PREMIUM_MARKER not in html:
        return False

    # Skip if already patched
    if "pr-bottom-line" in html:
        return False

    # Skip if no insert anchor
    if INSERT_BEFORE not in html:
        return False

    # Extract sticky verdict text
    m = STICKY_RE.search(html)
    if not m:
        return False

    verdict = m.group(1).strip()
    if not verdict or len(verdict) < 10:
        return False

    # Inject
    block = BOTTOM_LINE_HTML.format(text=verdict)
    html = html.replace(INSERT_BEFORE, block + INSERT_BEFORE, 1)
    path.write_text(html, encoding="utf-8")
    return True


def main():
    pages = list(SITE.glob("*-pricing-*.html"))
    patched = skipped = 0
    for p in pages:
        if patch_file(p):
            patched += 1
        else:
            skipped += 1
    print(f"Patched {patched} pricing pages, {skipped} skipped.")


if __name__ == "__main__":
    main()
