"""
Rewrites em-dashes and a small set of overused AI-tell words in site/pages/*.html
and top-level site/*.html. Idempotent; safe to re-run.

Usage: uv run python scripts/humanize_text.py
"""
import re
from pathlib import Path

SITE = Path("site")

WORD_SWAPS = [
    (r'\bseamlessly\b', 'smoothly'),
    (r'\bseamless\b', 'smooth'),
    (r'\brobust\b', 'strong'),
]


def _case_match(repl):
    def _r(m):
        w = m.group(0)
        if w.isupper():
            return repl.upper()
        if w[0].isupper():
            return repl.capitalize()
        return repl
    return _r


def fix_emdashes(html: str) -> str:
    html = html.replace('&mdash;', '\u2014')

    def heading_swap(m):
        return re.sub(r'\s*\u2014\s*', ': ', m.group(0))

    html = re.sub(r'<title>.*?</title>', heading_swap, html, flags=re.DOTALL)
    html = re.sub(r'<h[1-3][^>]*>.*?</h[1-3]>', heading_swap, html, flags=re.DOTALL)
    html = re.sub(r'\s*\u2014\s*', ', ', html)
    html = re.sub(r',\s*,', ',', html)
    html = re.sub(r'\s+,', ',', html)
    return html


def fix_ai_words(html: str) -> str:
    for pat, repl in WORD_SWAPS:
        html = re.sub(pat, _case_match(repl), html, flags=re.IGNORECASE)
    return html


def main() -> None:
    targets = [f for f in SITE.rglob("*.html") if "assets" not in f.parts and "templates" not in f.parts]
    changed = 0
    for f in targets:
        h = f.read_text(encoding="utf-8", errors="replace")
        out = fix_ai_words(fix_emdashes(h))
        if out != h:
            f.write_text(out, encoding="utf-8")
            changed += 1
    print(f"humanize_text: {changed}/{len(targets)} files changed")


if __name__ == "__main__":
    main()
