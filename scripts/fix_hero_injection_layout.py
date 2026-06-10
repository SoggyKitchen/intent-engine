"""Move blocks injected inside the hero H1 flex row out of it.

Several injectors (featured-answer, affiliate disclosure pill, pricing-change
alerts) used `re.sub(r'(</h1>)', ...)` and landed INSIDE the hero's
logo+H1 flex container (`display:flex;align-items:center`). Inside a flex row
they render as a skinny squashed column. This relocates them to immediately
after the flex container so they render full-width below the H1.

Template-authored markup is indented (4 spaces); injected blocks start at
column 0, and the flex container's own closer is the first `\n    </div>`,
so the non-greedy capture is safe.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# </h1>, then one-or-more injected blocks (col-0 markup), then the indented
# closing </div> of the flex container.
PAT = re.compile(r"(</h1>)\s*\n(\S.*?)(\n    </div>)", re.S)


def fix_file(p: Path) -> bool:
    html = p.read_text(encoding="utf-8")

    def repl(m: re.Match) -> str:
        injected = m.group(2).strip("\n")
        if len(injected) > 12000 or "<h2" in injected:
            return m.group(0)  # too big / not an injected block — leave alone
        return f"{m.group(1)}{m.group(3)}\n{injected}\n"

    out = PAT.sub(repl, html, count=1)
    if out != html:
        p.write_text(out, encoding="utf-8")
        return True
    return False


def main():
    fixed = 0
    for p in SITE.rglob("*.html"):
        if fix_file(p):
            fixed += 1
    print(f"fix_hero_injection_layout: {fixed} pages relocated hero-injected blocks")


if __name__ == "__main__":
    main()
