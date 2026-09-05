"""
Link the hidden-costs research from the pricing cluster.

An orphan page is a page Google has little reason to recrawl or trust, and this
one carries the site's only genuinely original dataset. The 22 pricing-history
pages and the pricing-changes tracker are the most topically adjacent surface we
have, so the link sits there rather than being sprayed site-wide.

Idempotent: skips any page that already carries the link.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
TARGET = "/pages/saas-hidden-costs-2026"

BLOCK = (
    '\n  <p class="hc-crosslink" style="margin:24px 0 0;padding:16px 20px;'
    'border:1px solid rgba(255,75,115,.25);border-radius:14px;'
    'background:linear-gradient(180deg,rgba(60,9,24,.82),rgba(22,9,15,.92));'
    'color:rgba(255,247,248,.82);line-height:1.6">'
    'The sticker price is not the invoice. See our verified list of '
    f'<a href="{TARGET}" style="color:#ff416d;font-weight:600">'
    'required onboarding fees, seat minimums and annual-only plans</a> '
    'read straight off the vendors\' own pricing pages.</p>\n'
)


def targets():
    yield from sorted(PAGES.glob("*-pricing-history-2026.html"))
    p = PAGES / "saas-pricing-changes.html"
    if p.exists():
        yield p


def main():
    added = already = noindexed = 0
    for p in targets():
        html = p.read_text(encoding="utf-8", errors="replace")
        if TARGET in html:
            already += 1
            continue
        if "noindex" in html:
            # A noindexed page still passes link value under "follow", but the
            # crawl signal we want comes from indexable surface.
            noindexed += 1
            continue
        # The pricing-history pages ship no <main>, so fall back to </body>.
        anchor = "</main>" if "</main>" in html else "</body>"
        if anchor not in html:
            continue
        p.write_text(html.replace(anchor, BLOCK + anchor, 1), encoding="utf-8")
        added += 1
    print(f"hidden-costs link: {added} added, {already} already linked, "
          f"{noindexed} skipped (noindexed)")


if __name__ == "__main__":
    main()
