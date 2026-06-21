"""
One-off patch: upgrade FAQ accordion questions from <div class="faq-q"> to
<h3 class="faq-q"> across all generated site pages.

AEO/GEO rationale: AI models (Perplexity, Google AI Overviews) extract FAQ
content from visible heading elements. A <div> is invisible to semantic parsing;
an <h3> signals "question" to both crawlers and LLM extractors.

CSS safety: motion.css/.faq-q now has margin:0 added, so browser H3 default
margins won't bleed into the accordion layout.

Safe to re-run — idempotent (already-patched files are skipped).
"""
from pathlib import Path
import re

SITE = Path(__file__).resolve().parents[1] / "site"

OPEN_OLD  = '<div class="faq-q">'
OPEN_NEW  = '<h3 class="faq-q">'
CLOSE_OLD = '</svg></div>'
CLOSE_NEW = '</svg></h3>'


def patch_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="replace")
    if OPEN_OLD not in html:
        return False
    html = html.replace(OPEN_OLD, OPEN_NEW)
    html = html.replace(CLOSE_OLD, CLOSE_NEW)
    path.write_text(html, encoding="utf-8")
    return True


def main():
    pages = list((SITE / "pages").glob("*.html"))
    patched = skipped = 0
    for p in pages:
        if patch_file(p):
            patched += 1
        else:
            skipped += 1
    print(f"Patched {patched} pages, {skipped} already clean.")


if __name__ == "__main__":
    main()
