"""
prune_thin_pages.py — de-index thin, template-generated pages.

Why: on 2026-09-01 the site had 1,545 pages, ~1,171 of them sitting in GSC's
"Crawled - currently not indexed". 943 were "X vs Y" pages and 922 of those were
under 700 words - a near-identical ~500-word template repeated hundreds of times.
A competitor (saaspare.com) with 42 pages, DR 0 and 20 backlinks ranks for 15
keywords while we, with DR 11 and 314 backlinks, rank for none. The corpus itself
is the liability.

What this does: adds `noindex, follow` to pages that fail the keep test and drops
them from the sitemap. It does NOT delete them - they stay live for anyone holding
a link, `follow` keeps their internal link equity flowing, and removing the meta
tag reverses the whole thing.

Keep test (a page survives if ANY holds):
  - it has GSC impressions, or
  - it links to an affiliate program in EARNING status (real revenue surface), or
  - it is a best-of / alternatives / pricing-history / hub page with >=700 words, or
  - it has >=900 words (genuinely substantial regardless of type)

Run:  uv run python scripts/prune_thin_pages.py --check   # report only
      uv run python scripts/prune_thin_pages.py           # apply
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
SITEMAP = ROOT / "site" / "sitemap.xml"
GSC = ROOT / "seo" / "reports" / "gsc-opportunities.json"

MARK = 'content="noindex, follow"'
NOINDEX_TAG = '<meta name="robots" content="noindex, follow">'
ROBOTS_RE = re.compile(r'<meta\s+name="robots"[^>]*>', re.I)

# Programs with live, paying affiliate links (PROGRAM_VALUE status == EARNING).
EARNING = {"nordvpn", "surfshark", "sucuri", "nordpass", "contabo", "hostpapa",
           "semrush", "shopify", "elevenlabs", "getresponse", "proton",
           "protonvpn", "elementor", "aweber", "parallels"}

BOILER = re.compile(
    r"<nav.*?</nav>|<footer.*?</footer>|<script.*?</script>|<style.*?</style>"
    r"|<!--.*?-->|<aside class=\"related-links\".*?</aside>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")
RICH_KINDS = {"best-of", "alternatives", "pricing-history", "other"}


def kind(slug: str) -> str:
    if re.search(r"-vs-", slug): return "vs"
    if "alternatives" in slug: return "alternatives"
    if "coupon" in slug or "promo-code" in slug: return "coupon"
    if "free-trial" in slug: return "trial"
    if "pricing-history" in slug: return "pricing-history"
    if "pricing" in slug: return "pricing"
    if "review" in slug: return "review"
    if slug.startswith("best-") or slug.startswith("7-best"): return "best-of"
    return "other"


def load_impressions() -> dict[str, float]:
    out: dict[str, float] = {}
    if not GSC.exists():
        return out
    data = json.loads(GSC.read_text(encoding="utf-8"))
    for o in data.get("opportunities", []):
        p = o.get("page", "").replace("https://saaspare.org", "").rstrip("/")
        out[p] = out.get(p, 0) + (o.get("impressions") or 0)
    return out


def body_words(html: str) -> int:
    return len(re.sub(r"\s+", " ", TAG.sub(" ", BOILER.sub(" ", html))).split())


def should_keep(slug, html, impressions) -> tuple[bool, str]:
    path = "/pages/" + slug
    if impressions.get(path, 0) > 0:
        return True, "has impressions"
    words = body_words(html)
    earning = bool({g.split("-")[0] for g in re.findall(r"/go/([a-z0-9-]+)", html)} & EARNING)
    if earning:
        return True, "links EARNING program"
    k = kind(slug)
    if k in RICH_KINDS and words >= 700:
        return True, f"{k} with {words}w"
    if words >= 900:
        return True, f"substantial ({words}w)"
    return False, f"thin {k} ({words}w)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, change nothing")
    args = ap.parse_args()

    impressions = load_impressions()
    keep, prune = [], []
    for f in sorted(PAGES.glob("*.html")):
        html = f.read_text(encoding="utf-8", errors="replace")
        ok, why = should_keep(f.stem, html, impressions)
        (keep if ok else prune).append((f, why, html))

    print(f"keep {len(keep)}  |  prune {len(prune)}  of {len(keep)+len(prune)}")
    if args.check:
        for f, why, _ in prune[:10]:
            print(f"  PRUNE {f.stem[:58]:60} {why}")
        return 0

    changed = 0
    for f, _why, html in prune:
        if MARK in html:
            continue
        if ROBOTS_RE.search(html):
            new = ROBOTS_RE.sub(NOINDEX_TAG, html, count=1)
        elif "</head>" in html:
            new = html.replace("</head>", "  " + NOINDEX_TAG + "\n</head>", 1)
        else:
            continue
        f.write_text(new, encoding="utf-8")
        changed += 1

    # Drop pruned URLs from the sitemap.
    removed = 0
    if SITEMAP.exists():
        sm = SITEMAP.read_text(encoding="utf-8")
        for f, _why, _h in prune:
            block = re.compile(
                r"\s*<url>\s*<loc>https://saaspare\.org/pages/"
                + re.escape(f.stem) + r"</loc>.*?</url>", re.S)
            sm, n = block.subn("", sm)
            removed += n
        SITEMAP.write_text(sm, encoding="utf-8")

    print(f"noindexed {changed} pages | removed {removed} sitemap entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
