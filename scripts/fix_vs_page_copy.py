"""One-off repair of vs-page copy issues now fixed in rebuild_vs_pages_v2.py.

- "in our testing" was a fabricated claim (scores are editorial) -> "in our
  editorial scoring", site-wide.
- Fallback tool tags leaked placeholder copy into sentences ("Choose X for
  X — B2B SaaS tool") -> honest generic fit phrase.
- Tied scores still declared a winner ("X wins overall — scoring 8.5/10"
  when both score 8.5) -> tie wording in quick answer, meta and FAQ.
- blast_off quick answers on comparison pages injected the full H1 as the
  topic ("pick Amplitude vs Mixpanel 2026: Which Is Better? if ...") ->
  just tool A's name.
- Two identical adjacent "Compare in Shortlist Builder" fallback buttons ->
  one.
"""
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"
FIT = "teams already invested in its ecosystem"

PLACEHOLDER_FIT_RE = re.compile(
    r"((?:for|if|choice if)\s)(?:<strong>)?[A-Z][\w .&+\-]*? — B2B SaaS tool(?:</strong>)?(?=[.,<])"
)
FAQ_SCORES_RE = re.compile(r"scores ([\d.]+)/10 vs [^\"<]*?s ([\d.]+)/10")
QA_WIN_RE = re.compile(
    r"<strong>([^<]+)</strong> wins overall — scoring ([\d.]+)/10 in our editorial scoring\."
)
META_WIN_RE = re.compile(r"Bottom line: ([^(]+) wins \(([\d.]+)/10\)\.")
PICK_TITLE_RE = re.compile(r"pick ([^<]*? vs [^<]*?\d{4}: Which Is Better\??) if you prioritise")
DUP_BTN_RE = re.compile(
    r'(<a href="/shortlist"[^>]*>Compare in Shortlist Builder →</a>)\s*'
    r'<a href="/shortlist"[^>]*>Compare in Shortlist Builder →</a>'
)


def fix(html: str) -> str:
    html = html.replace("in our testing", "in our editorial scoring")
    html = PLACEHOLDER_FIT_RE.sub(lambda m: m.group(1) + FIT, html)
    html = DUP_BTN_RE.sub(r"\1", html)

    # "pick <full H1 title> if you prioritise" -> "pick <tool A> if ..."
    def pick(m: re.Match) -> str:
        tool_a = m.group(1).split(" vs ")[0].strip()
        return f"pick {tool_a} if you prioritise"

    html = PICK_TITLE_RE.sub(pick, html)

    # Tie repair: only when the FAQ shows identical scores for both tools.
    fs = FAQ_SCORES_RE.search(html)
    if fs and fs.group(1) == fs.group(2):
        s = fs.group(1)
        html = QA_WIN_RE.sub(
            f"It's a tie — both score {s}/10 in our editorial scoring.", html
        )
        html = META_WIN_RE.sub(f"Bottom line: it's a tie ({s}/10 each).", html)
        html = re.sub(
            r"(>|&quot;|\")Yes — (?=[\w &.+\-]+ scores " + re.escape(s) + r"/10)",
            r"\1It is close — ",
            html,
        )
    return html


def main() -> int:
    changed = 0
    for p in SITE.rglob("*.html"):
        html = p.read_text(encoding="utf-8", errors="ignore")
        out = fix(html)
        if out != html:
            p.write_text(out, encoding="utf-8")
            changed += 1
    print(f"fix_vs_page_copy: updated {changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
