"""
Add a sticky bottom CTA bar + trust badge to all review and pricing pages.

The sticky bar shows:
  - Tool name + star rating (from existing JSON-LD)
  - Primary CTA button → /go/{slug}

Also adds a small "✓ Verified · Updated May 2026" trust badge above
existing primary CTA buttons.

Idempotent: pages already having sticky-cta are skipped.

Run: uv run python scripts/add_sticky_cta.py
"""
import re, json
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
TODAY = date.today().isoformat()
MONTH_YEAR = "May 2026"

# Pages to process
TARGET_PATTERNS = ["-review-", "-pricing-"]

# Map tool slug → /go/ slug (for tools where they differ)
GO_OVERRIDES = {
    "semrush": "semrush",
    "shopify": "shopify",
    "nordvpn": "nordvpn",
    "nordpass": "nordpass",
    "surfshark": "surfshark",
    "tresorit": "tresorit",
    "1password": "1password",
    "hubspot": "hubspot",
    "clickup": "clickup",
    "asana": "asana",
    "moz-pro": "moz-pro",
    "pipedrive": "pipedrive",
    "ahrefs": "ahrefs",
    "contabo": "contabo",
    "hetzner": "hetzner",
    "digitalocean": "digitalocean",
    "supabase": "supabase",
    "stripe": "stripe",
    "gusto": "gusto",
    "ramp": "ramp",
    "se-ranking": "se-ranking",
}

JSONLD_PAT = re.compile(
    r'type="application/ld\+json"[^>]*>([\s\S]*?)</script>',
    re.IGNORECASE
)

TRUST_BADGE_HTML = (
    '<div class="trust-badge" style="font-size:.8rem;color:#16a34a;font-weight:600;'
    'margin-bottom:.4rem;display:flex;align-items:center;gap:.4rem;">'
    '<span>&#10003;</span>'
    f'<span>Verified &middot; Updated {MONTH_YEAR} &middot; No paid rankings</span>'
    '</div>'
)

# Patterns that identify the primary affiliate CTA wrapper
CTA_PATTERNS = [
    re.compile(r'(<a[^>]+class="[^"]*(?:money-cta|cta-btn|btn-primary|cta-primary|affiliate-btn)[^"]*"[^>]*>)', re.IGNORECASE),
    re.compile(r'(<a[^>]+rel="[^"]*(?:sponsored|nofollow)[^"]*"[^>]+href="/go/[^"]*"[^>]*>)', re.IGNORECASE),
]


def get_tool_info(html: str, page_stem: str) -> dict:
    """Extract tool name, rating, and /go/ slug from page content."""
    info = {"name": None, "rating": None, "rating_count": None, "go_slug": None}

    # Try JSON-LD first
    for m in JSONLD_PAT.finditer(html):
        try:
            data = json.loads(m.group(1).strip())
            # Handle @graph
            items = data.get("@graph", [data])
            for item in items if isinstance(items, list) else [items]:
                t = item.get("@type", "")
                if t in ("SoftwareApplication", "Product", "Service"):
                    info["name"] = item.get("name") or info["name"]
                    ar = item.get("aggregateRating", {})
                    if ar:
                        info["rating"]       = ar.get("ratingValue") or info["rating"]
                        info["rating_count"] = ar.get("ratingCount") or info["rating_count"]
                if t == "Article":
                    pass  # article name is the page title, not tool name
        except Exception:
            pass

    # Derive go_slug from page stem
    # e.g. "semrush-pricing-2026-..." → "semrush"
    slug_m = re.match(r'^([a-z0-9-]+?)(?:-pricing|-review|-coupon|-free-trial|-alternatives)', page_stem)
    if slug_m:
        tool_slug = slug_m.group(1)
        info["go_slug"] = GO_OVERRIDES.get(tool_slug, tool_slug)

    # Fallback: try to get name from <h1>
    if not info["name"]:
        h1_m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
        if h1_m:
            raw = h1_m.group(1).strip()
            # Strip suffixes like "Review 2026: Is It Worth It?"
            name_m = re.match(r'^([A-Za-z0-9][A-Za-z0-9 .+-]*?)(?:\s+(?:Review|Pricing|Coupon|Free Trial|vs\b|Alternatives))', raw)
            if name_m:
                info["name"] = name_m.group(1).strip()
            else:
                info["name"] = raw[:40]

    return info


def build_sticky_html(info: dict) -> str:
    name  = info.get("name") or "This Tool"
    go    = info.get("go_slug") or ""
    rating = info.get("rating")
    count  = info.get("rating_count")

    rating_html = ""
    if rating:
        try:
            r = float(str(rating))
            stars = "&#9733;" * int(r) + ("&#9734;" * (5 - int(r)))
            rating_html = f'<span style="color:#f59e0b;">{stars}</span> <span style="color:#94a3b8;font-size:.8rem;">{r}/5'
            if count:
                rating_html += f" &middot; {int(count):,} reviews"
            rating_html += "</span>"
        except Exception:
            pass

    go_href = f"/go/{go}" if go else "#"

    return (
        '\n<div id="sticky-cta" style="position:fixed;bottom:0;left:0;right:0;'
        "background:#0f172a;border-top:2px solid #0ea5e9;padding:.75rem 1.5rem;"
        "display:flex;justify-content:space-between;align-items:center;z-index:999;"
        'box-shadow:0 -4px 20px rgba(0,0,0,.4);gap:1rem;">\n'
        f'  <div style="display:flex;flex-direction:column;gap:.15rem;">\n'
        f'    <span style="color:#fff;font-weight:700;">{name}</span>\n'
        f'    <span>{rating_html}</span>\n'
        "  </div>\n"
        f'  <a href="{go_href}" rel="nofollow sponsored" target="_blank" '
        'style="background:#0ea5e9;color:#fff;padding:.6rem 1.4rem;border-radius:6px;'
        'font-weight:700;font-size:.9rem;white-space:nowrap;text-decoration:none;flex-shrink:0;">'
        f"Try {name} Free &rarr;</a>\n"
        "</div>\n"
        "<style>"
        "#sticky-cta{display:none}"
        "@media(min-width:640px){#sticky-cta{display:flex}}"
        "</style>\n"
    )


def add_trust_badge(html: str) -> str:
    """Insert trust badge before the first affiliate CTA link found."""
    for pat in CTA_PATTERNS:
        m = pat.search(html)
        if m:
            # Only add if not already there nearby
            surrounding = html[max(0, m.start()-200):m.start()]
            if "trust-badge" not in surrounding:
                return html[:m.start()] + TRUST_BADGE_HTML + html[m.start():]
    return html


def process_page(path: Path) -> bool:
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False

    # Skip if already has sticky CTA
    if 'id="sticky-cta"' in html:
        return False

    info = get_tool_info(html, path.stem)

    # Only add if we have at least a name and go_slug
    if not info["go_slug"]:
        return False

    # Add trust badge above primary CTA
    html = add_trust_badge(html)

    # Inject sticky bar before </body>
    sticky = build_sticky_html(info)
    if "</body>" in html:
        html = html.replace("</body>", sticky + "</body>", 1)
    else:
        html = html + sticky

    path.write_text(html, encoding="utf-8")
    return True


if __name__ == "__main__":
    targets = [
        p for p in sorted(PAGES.glob("*.html"))
        if any(pat in p.name for pat in TARGET_PATTERNS)
    ]
    print(f"Processing {len(targets)} review/pricing pages...")

    added = 0
    skipped = 0
    for p in targets:
        if process_page(p):
            added += 1
        else:
            skipped += 1

    print(f"Sticky CTA added: {added}")
    print(f"Skipped (no slug or already done): {skipped}")
    print("\nDone.")
