"""
Fix remaining bare JSON-LD blocks - wraps every untagged {"@context":... line in <head>.
Run: uv run python scripts/fix_jsonld_v2.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

fixed = 0
all_html = (
    list((SITE / "pages").glob("*.html")) +
    list((SITE / "blog").glob("*.html")) +
    list((SITE / "authors").glob("*.html"))
)

for fp in sorted(all_html):
    try:
        content = fp.read_text(encoding="utf-8", errors="replace")
        original = content

        # Split into lines, find bare JSON-LD lines in head section
        lines = content.split("\n")
        new_lines = []
        in_head = False
        in_script = False
        changed = False

        for line in lines:
            stripped = line.strip()

            if "<head" in line.lower():
                in_head = True
            if "</head>" in line.lower():
                in_head = False
            if "<script" in line.lower():
                in_script = True
            if "</script>" in line.lower():
                in_script = False

            # If we're in head, not in a script tag, and line is raw JSON-LD
            if (in_head and not in_script and
                    stripped.startswith('{"@context":"https://schema.org"') and
                    not line.strip().startswith('<')):
                indent = len(line) - len(line.lstrip())
                pad = " " * indent
                new_lines.append(f'{pad}<script type="application/ld+json">{stripped}</script>')
                changed = True
            else:
                new_lines.append(line)

        if changed:
            fp.write_text("\n".join(new_lines), encoding="utf-8")
            fixed += 1
    except Exception as e:
        print(f"  ERROR {fp.name}: {e}")

print(f"Fixed bare JSON-LD on {fixed} pages")
