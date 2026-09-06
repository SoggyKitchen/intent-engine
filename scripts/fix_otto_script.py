"""
fix_otto_script.py — REMOVE the Search Atlas OTTO dynamic-optimization pixel.

This script used to INSTALL the pixel. It now strips it, and the filename is
kept so the two existing nightly steps keep working.

Why it was removed (2026-09-06)
-------------------------------
The pixel rewrites the DOM client-side after load, so what a rendering crawler
sees is not what our HTML says. Verified in a browser on /about the same day:

    served by us : "...honest verdicts and free-trial guides for 490+ comparisons."
    seen in DOM  : "...verified pricing, and expert insights for 1,400+ tools."

We have 494 indexable pages and 15 tools with verified pricing. OTTO was
live-injecting a corpus claim we had just finished removing from the HTML,
along with "Expert-Tested" headings for testing we have never run. Its queue
held more of the same, plus meta keywords for 525 pages - a tag Google has
ignored since 2009.

The previous docstring here claimed the pixel "does not grant OTTO authority to
auto-publish anything" because fixes are approved in the dashboard. In practice
ten meta descriptions were deployed and they carried fabricated claims, so that
reassurance did not hold. A third-party script that can silently rewrite our
pages is not compatible with a site whose entire pitch is verifiable facts.

The Search Atlas subscription is also being cancelled, which would leave this
script requesting a dead endpoint on all 1,571 pages on every page load.

Idempotent. Safe to re-run.
"""
import re
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"

# Matches the tag in any attribute order, deferred or not, so older installs
# are caught too.
OTTO_TAG = re.compile(
    r'\s*<script[^>]*id="sa-dynamic-optimization"[^>]*>\s*</script>',
    re.IGNORECASE,
)
# Belt and braces: any leftover reference to the loader.
OTTO_SRC = re.compile(
    r'\s*<script[^>]*dynamic_optimization\.js[^>]*>\s*</script>',
    re.IGNORECASE,
)


def main() -> None:
    removed = 0
    for p in SITE.rglob("*.html"):
        html = original = p.read_text(encoding="utf-8", errors="replace")
        html = OTTO_TAG.sub("", html)
        html = OTTO_SRC.sub("", html)
        if html != original:
            p.write_text(html, encoding="utf-8")
            removed += 1

    left = [
        str(p.relative_to(SITE))
        for p in SITE.rglob("*.html")
        if "sa-dynamic-optimization" in p.read_text(encoding="utf-8", errors="replace")
        or "dynamic_optimization.js" in p.read_text(encoding="utf-8", errors="replace")
    ]
    print(f"OTTO pixel removed from {removed} pages")
    print(f"VERIFY  pages still carrying it: {len(left)}")
    for f in left[:10]:
        print("  " + f)
    if left:
        raise SystemExit("fix_otto_script: did not converge")


if __name__ == "__main__":
    main()
