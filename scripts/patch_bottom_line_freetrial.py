"""
Patch: inject "Bottom line:" AEO paragraph into all live free-trial pages.

Extracts the sticky CTA text (already per-tool) and surfaces it as a visible
first paragraph before the "how to start" section. AI models pull the first
bolded "Bottom line:" sentence for AI Overviews and Perplexity citations.

Idempotent — pages already containing pr-bottom-line are skipped.
"""
from pathlib import Path
import re

SITE = Path(__file__).resolve().parents[1] / "site" / "pages"
INSERT_BEFORE = '<div id="how-to-start"'
STICKY_RE = re.compile(
    r'<div class="sticky-bottom-cta-text">\s*(.+?)\s*</div>',
    re.DOTALL
)
BOTTOM_LINE_TMPL = '<p class="pr-bottom-line"><strong>Bottom line:</strong> {text}</p>\n\n    '


def extract_text(html: str) -> str:
    m = STICKY_RE.search(html)
    if not m:
        return ""
    raw = re.sub(r'<[^>]+>', '', m.group(1))
    return re.sub(r'\s+', ' ', raw).strip()


def patch_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="replace")

    if "pr-bottom-line" in html:
        return False
    if INSERT_BEFORE not in html:
        return False

    text = extract_text(html)
    if not text or len(text) < 10:
        return False

    block = BOTTOM_LINE_TMPL.format(text=text)
    html = html.replace(INSERT_BEFORE, block + INSERT_BEFORE, 1)
    path.write_text(html, encoding="utf-8")
    return True


def main():
    pages = [p for p in SITE.glob("*free-trial*.html") if "database" not in p.name]
    patched = skipped = 0
    for p in pages:
        if patch_file(p):
            patched += 1
        else:
            skipped += 1
    print(f"Patched {patched} free-trial pages, {skipped} skipped.")


if __name__ == "__main__":
    main()
