"""
fix_otto_script.py — Inject the Search Atlas OTTO SEO dynamic-optimization
pixel into every page's <head>, with `defer` so it doesn't block rendering.

OTTO uses this script to detect and (with owner approval per-fix inside the
OTTO dashboard) live-apply SEO fixes - meta tags, schema, alt text - without
a code deploy. This script only installs the pixel; it does not grant OTTO
authority to auto-publish anything. Fixes are reviewed/approved in the
Search Atlas dashboard, not applied blind.

`defer` matters: the tag Search Atlas hands you has no async/defer, which
makes it a classic render-blocking third-party <script src> sitting in
<head> - measured contributing to a 6.3s mobile LCP on the HubSpot pricing
page. Every other third-party script on this site (GA4, motion.js,
saaspare-ui.js) already uses async/defer; this brings OTTO in line with
that, and `defer` still runs it before DOMContentLoaded so OTTO's
dashboard-approved fixes still land before the user interacts with the page.

Idempotent: safe to re-run in CI on every nightly build, same pattern as
fix_universal_nav.py and fix_inject_ui_css.py.
"""
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"

OTTO_MARKER = 'id="sa-dynamic-optimization"'
OTTO_SCRIPT = (
    '<script defer nowprocket nitro-exclude type="text/javascript" '
    'id="sa-dynamic-optimization" '
    'data-uuid="34c3284f-0872-48df-8c54-bb1a550278e6" '
    'src="https://dashboard.searchatlas.com/scripts/dynamic_optimization.js"></script>'
)
# Old, render-blocking form (no defer) - upgrade in place if found.
OTTO_SCRIPT_OLD = (
    '<script nowprocket nitro-exclude type="text/javascript" '
    'id="sa-dynamic-optimization" '
    'data-uuid="34c3284f-0872-48df-8c54-bb1a550278e6" '
    'src="https://dashboard.searchatlas.com/scripts/dynamic_optimization.js"></script>'
)

all_pages = list((SITE / "pages").glob("*.html"))
for subdir in ["blog", "authors"]:
    all_pages.extend((SITE / subdir).glob("*.html"))
for name in ["index.html", "about.html", "contact.html", "deal-radar.html",
             "shortlist.html", "newsletter.html", "404.html", "media-kit.html",
             "privacy.html", "terms.html", "methodology.html"]:
    p = SITE / name
    if p.exists():
        all_pages.append(p)

fixed = upgraded = skipped = errors = 0
for path in all_pages:
    try:
        html = path.read_text(encoding="utf-8", errors="replace")

        if OTTO_SCRIPT_OLD in html:
            html = html.replace(OTTO_SCRIPT_OLD, OTTO_SCRIPT, 1)
            path.write_text(html, encoding="utf-8")
            upgraded += 1
            continue

        if OTTO_MARKER in html:
            skipped += 1
            continue

        if "</head>" not in html:
            errors += 1
            print(f"  ERR no </head>: {path.name}")
            continue
        html = html.replace("</head>", "  " + OTTO_SCRIPT + "\n</head>", 1)
        path.write_text(html, encoding="utf-8")
        fixed += 1
    except Exception as e:
        errors += 1
        print(f"  ERR {path.name}: {e}")

print(f"Done: {fixed} newly installed | {upgraded} upgraded to defer | "
      f"{skipped} already correct | {errors} errors")
