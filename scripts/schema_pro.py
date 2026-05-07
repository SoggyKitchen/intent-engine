#!/usr/bin/env python3
"""
schema_pro.py — second-pass schema upgrade.

Phase-2 audit (May 2026) found:
- SoftwareApplication on only 4% of pages (rich snippets gap)
- HowTo on 1 page (free-trial pages should have it)
- ItemList on 1 page (every best-of page should have it)
- Review on 0 pages (every review page should have it, without fake aggregateRating)
- Affiliate disclosure not visible above the first affiliate link (FTC + trust)

This script injects the right schema by page kind, plus an above-fold
visible disclosure pill on every money page. Idempotent.

Run: uv run python scripts/schema_pro.py [--check]
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / "site" / "pages"
OUTPUTS = ROOT / "outputs" / "seo"
OUTPUTS.mkdir(parents=True, exist_ok=True)

H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)

# Page-kind detection from filename
KIND_PATTERNS = {
    "pricing":     re.compile(r"^(?P<tool>.+?)-pricing-2026"),
    "review":      re.compile(r"^(?P<tool>.+?)-review-2026"),
    "free_trial":  re.compile(r"^(?P<tool>.+?)-free-trial-2026"),
    "free_plan":   re.compile(r"^does-(?P<tool>.+?)-have-a-free-plan-2026"),
    "coupon":      re.compile(r"^(?P<tool>.+?)-coupon-(?:code-)?2026"),
    "alternatives":re.compile(r"^(?:\d+-)?best-(?P<tool>.+?)-alternatives-in-2026|^(?P<tool2>.+?)-alternatives-2026"),
    "comparison":  re.compile(r"^(?P<tool>.+?)-vs-(?P<tool2>.+?)-which-is-better-in-2026"),
    "bestof":      re.compile(r"^(?:\d+-)?best-(?P<topic>.+?)-(?:software|tools)-(?:for-(?P<audience>.+?)-)?in-2026"),
}


def detect(filename: str) -> tuple[str, dict]:
    base = filename.lower().removesuffix(".html")
    for kind, pat in KIND_PATTERNS.items():
        m = pat.match(base)
        if m:
            return kind, {k: v for k, v in (m.groupdict() or {}).items() if v}
    return "default", {}


# === Schema generators =======================================================

def software_app_schema(tool: str, url: str) -> str:
    name = " ".join(w.capitalize() for w in tool.replace("-", " ").split())
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": name,
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web, iOS, Android",
        "description": f"{name} is a B2B SaaS tool covered by SaaSpare with verified pricing and an honest editorial verdict.",
        "url": url,
        "offers": {
            "@type": "AggregateOffer",
            "priceCurrency": "USD",
            "lowPrice": "0",
            "offerCount": "3",
            "availability": "https://schema.org/InStock"
        }
    }, indent=2)


def review_schema(tool: str, url: str) -> str:
    name = " ".join(w.capitalize() for w in tool.replace("-", " ").split())
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "Review",
        "itemReviewed": {
            "@type": "SoftwareApplication",
            "name": name,
            "applicationCategory": "BusinessApplication"
        },
        "author": {
            "@type": "Organization",
            "name": "SaaSpare",
            "url": "https://saaspare.org"
        },
        "publisher": {
            "@type": "Organization",
            "name": "SaaSpare",
            "url": "https://saaspare.org"
        },
        "url": url,
        "name": f"{name} Review 2026",
        "reviewBody": f"SaaSpare's independent editorial review of {name} — covering real pricing, hidden fees, free-trial path, ideal team size, and honest verdict. No paid placements; commission-disclosed affiliate links do not affect the verdict."
    }, indent=2)


def howto_schema(tool: str, url: str) -> str:
    name = " ".join(w.capitalize() for w in tool.replace("-", " ").split())
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": f"How to Get {name} Free Trial in 2026",
        "url": url,
        "totalTime": "PT5M",
        "step": [
            {"@type": "HowToStep", "position": 1,
             "name": f"Open the {name} sign-up page",
             "text": f"Click through to the {name} sign-up form linked on this page. Some vendors hide the trial CTA — we link directly to the trial path that does not require a sales call."},
            {"@type": "HowToStep", "position": 2,
             "name": "Use a real work email",
             "text": "Most B2B vendors block free-mail providers. Use your actual work email so the trial activates correctly and your data persists if you upgrade."},
            {"@type": "HowToStep", "position": 3,
             "name": "Skip credit card if possible",
             "text": f"Where {name} offers a no-card trial, choose that path. Card-required trials auto-convert to paid; we flag which trials convert vs which expire."},
            {"@type": "HowToStep", "position": 4,
             "name": "Test the actual workflow you'll buy for",
             "text": "Don't tour the demo data — load your real workflow. The trial reveals integration gaps, performance limits, and feature coverage faster than any demo."},
            {"@type": "HowToStep", "position": 5,
             "name": "Compare against alternatives during the trial",
             "text": f"While in the {name} trial, run a parallel free trial of the closest alternative. Decision-quality is highest when you have both tools open at once."}
        ]
    }, indent=2)


def itemlist_schema(topic: str, url: str, item_count: int = 9) -> str:
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"Best {topic.replace('-', ' ').title()} 2026",
        "url": url,
        "numberOfItems": item_count,
        "itemListOrder": "https://schema.org/ItemListOrderAscending",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": f"{url}#tool-{i+1}"}
            for i in range(item_count)
        ]
    }, indent=2)


# === Disclosure pill (above-fold visible affiliate disclosure) ===============

DISCLOSURE_PILL_MARKER = '<p class="aff-disclosure-pill"'
DISCLOSURE_PILL_HTML = (
    '<p class="aff-disclosure-pill" '
    'style="font-size:.78rem;color:rgba(255,255,255,.55);background:rgba(233,69,96,.08);'
    'border:1px solid rgba(233,69,96,.18);padding:.55rem .9rem;border-radius:8px;'
    'margin:1rem 0 1.2rem 0;line-height:1.5;max-width:880px">'
    '<strong style="color:rgba(255,255,255,.78)">Affiliate disclosure:</strong> '
    'Some links on this page are commission-bearing. We may earn if you buy after '
    'clicking — this never changes our editorial verdict. Read our '
    '<a href="/affiliate-disclosure" style="color:#e94560">full disclosure</a>.'
    '</p>\n'
)


def inject_disclosure_pill(html: str) -> str:
    if DISCLOSURE_PILL_MARKER in html:
        return html
    # insert immediately after first </h1>
    m = re.search(r"</h1>", html, re.I)
    if not m:
        return html
    return html[:m.end()] + "\n" + DISCLOSURE_PILL_HTML + html[m.end():]


# === Schema injection helpers ================================================

SCHEMA_PRO_MARKER = "schema-pro-injected"
SCRIPT_TAG_END = "</script>"


def has_schema_type(html: str, schema_type: str) -> bool:
    pattern = re.compile(rf'"@type"\s*:\s*"{schema_type}"')
    return bool(pattern.search(html))


def inject_schema(html: str, schema_json: str, schema_id: str) -> str:
    """Inject a JSON-LD script before </head>. Marks with id for idempotency."""
    if f'id="{schema_id}"' in html:
        return html
    script = (
        f'\n<script type="application/ld+json" id="{schema_id}" data-{SCHEMA_PRO_MARKER}="1">\n'
        f"{schema_json}\n"
        f"</script>\n"
    )
    return html.replace("</head>", script + "</head>", 1)


# === Main runner =============================================================

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args(argv)

    report = {
        "files_scanned": 0,
        "software_added": 0,
        "review_added": 0,
        "howto_added": 0,
        "itemlist_added": 0,
        "disclosure_added": 0,
        "skipped_already_present": 0,
    }

    for fp in sorted(PAGES.glob("*.html")):
        if fp.name in {"index.html", "thanks.html", "verification.html"}:
            continue
        report["files_scanned"] += 1
        html = fp.read_text(encoding="utf-8", errors="replace")
        if "noindex" in html[:4000].lower():
            continue

        kind, parts = detect(fp.name)
        url = f"https://saaspare.org/pages/{fp.stem}"
        original = html

        # Inject SoftwareApplication on pricing/review/free_trial/free_plan/coupon
        if kind in {"pricing", "review", "free_trial", "free_plan", "coupon"}:
            tool = parts.get("tool") or parts.get("tool2") or "tool"
            if not has_schema_type(html, "SoftwareApplication"):
                html = inject_schema(html, software_app_schema(tool, url), "schema-software-app")
                report["software_added"] += 1

        # Inject Review on review pages
        if kind == "review" and not has_schema_type(html, "Review"):
            tool = parts.get("tool", "tool")
            html = inject_schema(html, review_schema(tool, url), "schema-review")
            report["review_added"] += 1

        # Inject HowTo on free_trial / free_plan pages
        if kind in {"free_trial", "free_plan"} and not has_schema_type(html, "HowTo"):
            tool = parts.get("tool", "tool")
            html = inject_schema(html, howto_schema(tool, url), "schema-howto")
            report["howto_added"] += 1

        # Inject ItemList on bestof pages
        if kind == "bestof" and not has_schema_type(html, "ItemList"):
            topic = parts.get("topic", "saas")
            html = inject_schema(html, itemlist_schema(topic, url), "schema-itemlist")
            report["itemlist_added"] += 1

        # Inject visible disclosure pill ABOVE first affiliate link
        # (only on pages that have any /go/ links)
        if "/go/" in html and DISCLOSURE_PILL_MARKER not in html:
            html = inject_disclosure_pill(html)
            report["disclosure_added"] += 1

        if html != original and not args.check:
            fp.write_text(html, encoding="utf-8")
        elif html == original:
            report["skipped_already_present"] += 1

    (OUTPUTS / "schema_pro.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print("=== schema_pro ===")
    for k, v in report.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
