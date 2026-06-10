"""Repair quick-answer paragraphs where the H1 topic was glued together.

blast_off.py used to strip H1 tags with no replacement, so a <br> inside the
H1 produced topics like "Best Semrush DiscountRight Now". For each page,
recompute the correctly-spaced topic from the H1 and substitute the glued
variant wherever it appears. One-off repair; the generator is fixed.
"""
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)


def topics(h1_inner: str) -> tuple[str, str]:
    glued = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", h1_inner)).strip()
    spaced = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h1_inner)).strip()
    return glued, spaced


def main() -> int:
    files = total = 0
    for p in SITE.rglob("*.html"):
        html = p.read_text(encoding="utf-8", errors="ignore")
        m = H1_RE.search(html)
        if not m:
            continue
        glued, spaced = topics(m.group(1))
        if glued == spaced or glued not in html:
            continue
        # Only replace outside the h1 itself (the h1 keeps its markup)
        head, tail = html[: m.end()], html[m.end():]
        n = tail.count(glued)
        if not n:
            continue
        p.write_text(head + tail.replace(glued, spaced), encoding="utf-8")
        files += 1
        total += n
    print(f"fix_glued_quick_answers: fixed {total} occurrences across {files} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
