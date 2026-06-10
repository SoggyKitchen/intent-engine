"""
Strip fabricated "Option #N" placeholder tool cards from best-of pages.

These come from generate_best_of_v3.py padding short tool lists to 6 entries
with invented names, scores (7.5) and pros/cons — a hard anti-fabrication
violation. This removes:
  - the <article> card blocks (and their "#N undefined" comments)
  - matching JSON-LD ListItem entries (with comma repair, scoped to ld+json)
  - sidebar "Quick Rankings" entries pointing at the removed cards
  - any leftover "Option #N" text fragments in comparison-table rows

Importable: strip_placeholder_html(html) -> str. Run directly to sweep site/.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"

_ARTICLE_RE = re.compile(
    r'(?:<!--\s*═+\s*#\d+\s+undefined\s*═+\s*-->\s*)?'
    r'<article class="tc premium-card[^>]*data-screen-label="\d+ Option #\d+">.*?</article>\s*',
    re.S,
)
_COMMENT_RE = re.compile(r'<!--\s*═+\s*#\d+\s+undefined\s*═+\s*-->\s*')
_SIDEBAR_RE = re.compile(r'<a href="#tool-\d+" class="rm-item">(?:(?!</a>).)*?Option #\d+.*?</a>\s*', re.S)
_LISTITEM_RE = re.compile(r'\{"@type":"ListItem","position":\d+,"name":"Option #\d+","url":"/go/option-#\d+"\},?\s*')
_TABLE_ROW_RE = re.compile(r'<tr>(?:(?!</tr>).)*?Option #\d+.*?</tr>\s*', re.S)
_CHIP_RE = re.compile(r'<span class="floating-chip"[^>]*>(?:(?!</span>).)*?Option #\d+</span>\s*', re.S)
_FAQ_SENT_RE = re.compile(r'\s*Option #\d+ is a strong alternative if you need different strengths\.')
_JCHIP_RE = re.compile(r'<a class="jchip"[^>]*>(?:(?!</a>).)*?Option #\d+</a>\s*', re.S)


def _clean_jsonld(html: str) -> str:
    def fix(m: re.Match) -> str:
        block = _LISTITEM_RE.sub("", m.group(0))
        return re.sub(r',(\s*\])', r'\1', block)
    return re.sub(r'<script type="application/ld\+json">.*?</script>', fix, html, flags=re.S)


def strip_placeholder_html(html: str) -> str:
    if "Option #" not in html:
        return html
    html = _ARTICLE_RE.sub("", html)
    html = _COMMENT_RE.sub("", html)
    html = _SIDEBAR_RE.sub("", html)
    html = _TABLE_ROW_RE.sub("", html)
    html = _CHIP_RE.sub("", html)
    html = _JCHIP_RE.sub("", html)
    html = _FAQ_SENT_RE.sub("", html)
    html = _clean_jsonld(html)
    return html


def main() -> int:
    changed = 0
    for f in SITE.rglob("*.html"):
        t = f.read_text(encoding="utf-8", errors="replace")
        new = strip_placeholder_html(t)
        if new != t:
            f.write_text(new, encoding="utf-8")
            changed += 1
    print(f"stripped placeholder cards from {changed} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
