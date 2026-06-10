"""Remove orphaned </script> tails left behind by partial JSON-LD removals.

Some past cleanup deleted the opening `<script type="application/ld+json">{...`
of a JSON-LD block but left its tail (e.g. `  ]</script>`) in the <head>.
Browsers relocate that stray `]` text node into <body>, where it renders as a
visible "]" in the top-left corner of the page.

This walks each file's <script> open/close tags; any </script> with no matching
opener is removed, along with stray `]`/`}` bracket characters immediately
preceding it.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

TOKEN = re.compile(r"<script\b[^>]*>|</script>", re.I)
# stray bracket/whitespace run directly before the orphan close tag
TAIL = re.compile(r"[\s\]\}]*$")


def fix_text(html: str) -> str:
    depth = 0
    drops: list[tuple[int, int]] = []  # (start, end) spans to delete
    for m in TOKEN.finditer(html):
        if m.group(0).lower().startswith("</"):
            if depth == 0:
                # orphan close tag — also eat stray brackets right before it
                start = TAIL.search(html, 0, m.start()).start()
                drops.append((start, m.end()))
            else:
                depth -= 1
        else:
            depth += 1
    for start, end in reversed(drops):
        html = html[:start] + "\n" + html[end:]
    return html


def main():
    fixed = 0
    for p in SITE.rglob("*.html"):
        html = p.read_text(encoding="utf-8")
        out = fix_text(html)
        if out != html:
            p.write_text(out, encoding="utf-8")
            fixed += 1
    print(f"fix_orphan_script_tails: {fixed} pages cleaned")


if __name__ == "__main__":
    main()
