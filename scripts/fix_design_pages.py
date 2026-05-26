"""
Fix three issues with the new design pages:

1. Library page — nightly injected old library-shell content before the new hero
2. Footer logo — all new design pages use the demo "S" mark; replace with real SVG logo
3. Real data — wire actual page counts, real affiliate deals, real comparison links

Run: uv run python scripts/fix_design_pages.py
"""
import re
from pathlib import Path

ROOT  = Path(__file__).resolve().parents[1]
SITE  = ROOT / "site"
PAGES = SITE / "pages"

# ── Real SVG logo (same as existing nav) ──────────────────────────────────
FOOTER_LOGO_HTML = '''<a href="/" style="display:flex;align-items:center;gap:9px;text-decoration:none;margin-bottom:.75rem">
      <svg style="height:26px;width:auto;flex-shrink:0" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs><clipPath id="ftct"><path d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></clipPath><clipPath id="ftcb"><path d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/></clipPath></defs><path fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/><path fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></svg>
      <span style="font-weight:800;font-size:1.05rem;letter-spacing:-.4px;color:#fff">Saa<em style="color:#e94560;font-style:normal">Spare</em></span>
    </a>'''

# ── Real deal data for Deal Radar ──────────────────────────────────────────
# Only use deals from our APPROVED affiliate programs
REAL_DEALS = [
    {
        "slug":     "nordvpn",
        "name":     "NordVPN",
        "icon_url": "https://cdn.simpleicons.org/nordvpn/4687ff",
        "desc":     "The world's leading VPN service. 6,400+ servers in 111 countries.",
        "tags":     ["VPN", "Security", "Privacy"],
        "discount": "72% OFF",
        "price":    "$3.39",
        "price_unit": "/mo",
        "billing":  "Billed every 2 years",
        "go_slug":  "nordvpn",
        "badge":    "Best Deal",
    },
    {
        "slug":     "nordpass",
        "name":     "NordPass",
        "icon_url": "https://cdn.simpleicons.org/nordpass/4687ff",
        "desc":     "Business password manager with zero-knowledge architecture.",
        "tags":     ["Password Mgmt", "Security", "Teams"],
        "discount": "55% OFF",
        "price":    "$1.79",
        "price_unit": "/user/mo",
        "billing":  "Billed annually, min 5 users",
        "go_slug":  "nordpass",
        "badge":    "",
    },
    {
        "slug":     "surfshark",
        "name":     "Surfshark",
        "icon_url": "https://cdn.simpleicons.org/surfshark/1abcfe",
        "desc":     "Unlimited devices VPN with ad blocker and breach alert.",
        "tags":     ["VPN", "Security", "Unlimited Devices"],
        "discount": "80% OFF",
        "price":    "$2.19",
        "price_unit": "/mo",
        "billing":  "Billed every 2 years",
        "go_slug":  "surfshark",
        "badge":    "",
    },
    {
        "slug":     "contabo",
        "name":     "Contabo",
        "icon_url": "https://cdn.simpleicons.org/linux/ffffff",
        "desc":     "Best-value VPS hosting — 4GB RAM from $5.50/mo in EU &amp; US.",
        "tags":     ["Cloud Hosting", "VPS", "Developer"],
        "discount": "From $5.50",
        "price":    "$5.50",
        "price_unit": "/mo",
        "billing":  "Monthly billing available",
        "go_slug":  "contabo",
        "badge":    "Best Value",
    },
    {
        "slug":     "sucuri",
        "name":     "Sucuri",
        "icon_url": "https://cdn.simpleicons.org/sucuri/4a9e4b",
        "desc":     "Website firewall, malware removal &amp; CDN for businesses.",
        "tags":     ["Security", "WAF", "CDN"],
        "discount": "Annual Save",
        "price":    "$199.99",
        "price_unit": "/yr",
        "billing":  "Billed annually",
        "go_slug":  "sucuri",
        "badge":    "",
    },
]

# ── Real comparison pairs (verified pages exist) ───────────────────────────
REAL_COMPARISONS = [
    {
        "title":    "Semrush vs Ahrefs",
        "url":      "/pages/semrush-vs-ahrefs-which-is-better-in-2026",
        "icon_a":   "https://cdn.simpleicons.org/semrush/ff642d",
        "icon_b":   "https://cdn.simpleicons.org/ahrefs/006bff",
        "badges":   ["SEO", "Marketing"],
        "best_for": "Content teams",
    },
    {
        "title":    "ClickUp vs Asana",
        "url":      "/pages/clickup-vs-asana-which-is-better-in-2026",
        "icon_a":   "https://cdn.simpleicons.org/clickup/7b68ee",
        "icon_b":   "https://cdn.simpleicons.org/asana/f06a6a",
        "badges":   ["Project Mgmt", "Teams"],
        "best_for": "Agencies 5+",
    },
    {
        "title":    "1Password vs Bitwarden",
        "url":      "/pages/1password-vs-bitwarden-which-is-better-in-2026",
        "icon_a":   "https://cdn.simpleicons.org/1password/0094f5",
        "icon_b":   "https://cdn.simpleicons.org/bitwarden/175ddc",
        "badges":   ["Security", "Password Mgmt"],
        "best_for": "Premium UX",
    },
    {
        "title":    "Shopify vs BigCommerce",
        "url":      "/pages/shopify-vs-bigcommerce-which-is-better-in-2026",
        "icon_a":   "https://cdn.simpleicons.org/shopify/95bf47",
        "icon_b":   "https://cdn.simpleicons.org/bigcommerce/121118",
        "badges":   ["eCommerce", "Stores"],
        "best_for": "Direct-to-consumer",
    },
    {
        "title":    "HubSpot vs Zoho",
        "url":      "/pages/hubspot-vs-zoho-which-is-better-in-2026",
        "icon_a":   "https://cdn.simpleicons.org/hubspot/ff7a59",
        "icon_b":   "https://cdn.simpleicons.org/zoho/e42527",
        "badges":   ["CRM", "Sales"],
        "best_for": "SMB teams",
    },
    {
        "title":    "Notion vs ClickUp",
        "url":      "/pages/clickup-vs-notion-which-is-better-in-2026",
        "icon_a":   "https://cdn.simpleicons.org/notion/ffffff",
        "icon_b":   "https://cdn.simpleicons.org/clickup/7b68ee",
        "badges":   ["Docs", "Productivity"],
        "best_for": "Mixed teams",
    },
    {
        "title":    "NordVPN vs Surfshark",
        "url":      "/pages/nordvpn-vs-surfshark-which-is-better-in-2026",
        "icon_a":   "https://cdn.simpleicons.org/nordvpn/4687ff",
        "icon_b":   "https://cdn.simpleicons.org/surfshark/1abcfe",
        "badges":   ["VPN", "Security"],
        "best_for": "Privacy-first teams",
    },
]


def count_real_pages():
    """Count actual pages by type from site/pages/."""
    all_pages = list(PAGES.glob("*.html"))
    vs       = sum(1 for p in all_pages if "-vs-" in p.name)
    pricing  = sum(1 for p in all_pages if "-pricing-" in p.name and "history" not in p.name)
    reviews  = sum(1 for p in all_pages if "-review-" in p.name)
    total    = len(all_pages)
    return {"vs": vs, "pricing": pricing, "reviews": reviews, "total": total}


# ── Fix 1: Library page — strip injected old content ─────────────────────

def fix_library_page():
    lib = SITE / "pages" / "index.html"
    html = lib.read_text(encoding="utf-8", errors="replace")

    # Remove the old library-shell block injected by nightly scripts
    # Pattern: starts with <div class="library-shell"> and ends before the new <!-- POPULAR NOW --> or <!-- MAIN -->
    html = re.sub(
        r'<div class="library-shell">[\s\S]*?(?=<!-- POPULAR NOW -->|<!-- MAIN -->|<section class="sp-section"[^>]*data-screen-label="01)',
        '',
        html
    )

    # Also remove any stale <section ... data-screen-label="01 Library Hero"> if it got duplicated
    # Remove duplicate hero sections (keep only the lib-hero class one)
    lib_hero_matches = list(re.finditer(r'<section class="lib-hero"', html))
    if len(lib_hero_matches) > 1:
        # Keep only the first one
        second_start = lib_hero_matches[1].start()
        html = html[:second_start]

    # Update real stats in the lib-stats block
    counts = count_real_pages()
    html = re.sub(r'<strong>808</strong><span>Comparisons</span>',
                  f'<strong>{counts["vs"]}</strong><span>Comparisons</span>', html)
    html = re.sub(r'<strong>64</strong><span>Pricing Guides</span>',
                  f'<strong>{counts["pricing"]}</strong><span>Pricing Guides</span>', html)
    html = re.sub(r'<strong>34</strong><span>Reviews</span>',
                  f'<strong>{counts["reviews"]}</strong><span>Reviews</span>', html)
    html = re.sub(r'<strong>1,156</strong><span>Buyer Pages Indexed</span>',
                  f'<strong>{counts["total"]:,}</strong><span>Buyer Pages Indexed</span>', html)

    # Also update the hero eyebrow stat if present
    html = re.sub(r'1,195 buyer pages indexed', f'{counts["total"]:,} buyer pages indexed', html)

    # Wire real comparison links in "Popular right now"
    html = html.replace(
        '<a class="cat-chip" href="/pages/">HubSpot vs Salesforce</a>',
        '<a class="cat-chip" href="/pages/semrush-vs-ahrefs-which-is-better-in-2026">Semrush vs Ahrefs</a>'
    )
    html = html.replace(
        '<a class="cat-chip" href="/pages/">Notion vs Coda</a>',
        '<a class="cat-chip" href="/pages/clickup-vs-notion-which-is-better-in-2026">Notion vs ClickUp</a>'
    )
    html = html.replace(
        '<a class="cat-chip" href="/pages/">ClickUp vs Asana</a>',
        '<a class="cat-chip" href="/pages/clickup-vs-asana-which-is-better-in-2026">ClickUp vs Asana</a>'
    )
    html = html.replace(
        '<a class="cat-chip" href="/pages/">Pipedrive vs HubSpot</a>',
        '<a class="cat-chip" href="/pages/pipedrive-vs-hubspot-which-is-better-in-2026">Pipedrive vs HubSpot</a>'
    )

    # Wire real comparison rows in the main list
    new_rows = _build_comparison_rows()
    html = re.sub(
        r'<div class="lib-list stagger">[\s\S]*?<div class="lib-pagination">',
        '<div class="lib-list stagger">\n' + new_rows + '\n<div class="lib-pagination">',
        html, count=1
    )

    lib.write_text(html, encoding="utf-8")
    print(f"  library page fixed: {counts['vs']} comparisons, {counts['reviews']} reviews, {counts['total']:,} pages")


def _build_comparison_rows() -> str:
    arrow_svg = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
    rows = []
    for c in REAL_COMPARISONS:
        badges_html = "".join(
            f'<span class="sp-badge sp-badge-ghost">{b}</span>' for b in c["badges"]
        )
        rows.append(f'''        <a href="{c['url']}" class="lib-row premium-card">
          <div class="lib-row-logos">
            <span class="sp-logo"><img src="{c['icon_a']}"></span>
            <span class="sp-logo"><img src="{c['icon_b']}"></span>
          </div>
          <div>
            <div class="lib-row-title">{c['title']}</div>
            <div class="lib-row-meta">{badges_html}</div>
          </div>
          <div class="lib-row-best">Best for: <em>{c['best_for']}</em></div>
          <div class="lib-row-arrow">{arrow_svg}</div>
        </a>''')
    return "\n".join(rows)


# ── Fix 2: Fix footer logo on all new design pages ────────────────────────

def fix_footer_logo(path: Path) -> bool:
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False

    # Pattern: the demo footer logo with .sp-nav-logo-mark "S" text
    old = re.compile(
        r'<div class="sp-nav-logo">\s*<span class="sp-nav-logo-mark">S</span>\s*Saa\s*<em[^>]*>Spare</em>\s*</div>',
        re.IGNORECASE
    )
    new_html = old.sub(FOOTER_LOGO_HTML, html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        return True
    return False


# ── Fix 3: Wire real deals into deal-radar.html ───────────────────────────

def build_deal_row(d: dict) -> str:
    badge_html = f'<span class="dr-deal-best">{d["badge"]}</span>' if d["badge"] else ""
    tags_html  = "".join(f'<span class="sp-badge sp-badge-ghost">{t}</span>' for t in d["tags"])
    verified   = '<span class="sp-badge sp-badge-green"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="m5 12 5 5L20 7"/></svg> Verified</span>'
    save_svg   = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 2 3 7 7 .5-5.5 4.5L18 22l-6-4-6 4 1.5-8L2 9.5 9 9z"/></svg>'

    return f'''          <article class="dr-deal premium-card">
            <span class="sp-logo sp-logo-lg"><img src="{d['icon_url']}"></span>
            <div class="dr-deal-body">
              <div class="dr-deal-head">
                <span class="dr-deal-name">{d['name']}</span>
                {verified}
              </div>
              <p class="dr-deal-desc">{d['desc']}</p>
              <div class="dr-deal-tags">{tags_html}</div>
            </div>
            <div class="dr-deal-disc-col">
              {badge_html}
              <div class="dr-deal-disc">{d['discount']}</div>
              <span class="dr-deal-price">{d['price']}<em>{d['price_unit']}</em></span>
              <span class="dr-deal-billing">{d['billing']}</span>
            </div>
            <div class="dr-deal-actions">
              <a href="/go/{d['go_slug']}" rel="nofollow sponsored" class="sp-btn sp-btn-primary glint-button">View Deal &rarr;</a>
              <button class="dr-deal-save" aria-label="Save to shortlist">{save_svg}</button>
            </div>
          </article>'''


def fix_deal_radar():
    dr = SITE / "deal-radar.html"
    html = dr.read_text(encoding="utf-8", errors="replace")

    # Replace all deal rows with real ones (remove fake countdown timers)
    new_deals = "\n".join(build_deal_row(d) for d in REAL_DEALS)
    html = re.sub(
        r'<div class="dr-deals">[\s\S]*?</div>\s*\n\s*<!-- Trust strip -->',
        f'<div class="dr-deals">\n{new_deals}\n          </div>\n\n        <!-- Trust strip -->',
        html, count=1
    )

    # Update hero badge count
    html = html.replace(
        '<span class="sp-badge sp-badge-pink">126 live deals</span>',
        f'<span class="sp-badge sp-badge-pink">{len(REAL_DEALS)} verified deals</span>'
    )
    html = html.replace(
        '<span class="sp-badge sp-badge-amber">Best deals ending soon</span>',
        '<span class="sp-badge sp-badge-amber">Updated daily &middot; Affiliate links</span>'
    )

    dr.write_text(html, encoding="utf-8")
    print(f"  deal-radar: {len(REAL_DEALS)} real deals wired")


# ── Fix 4: Update all sp-nav-logo footer marks ────────────────────────────

NEW_DESIGN_PAGES = [
    "pages/index.html",
    "about.html",
    "deal-radar.html",
    "roi.html",
    "shortlist.html",
    "newsletter.html",
    "contact.html",
    "404.html",
]


# ── main ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Fix 1: Library page — remove injected old content ===")
    fix_library_page()

    print("\n=== Fix 2: Footer logo — real SVG on all new design pages ===")
    fixed_logos = 0
    for rel in NEW_DESIGN_PAGES:
        p = SITE / rel
        if fix_footer_logo(p):
            fixed_logos += 1
            print(f"  fixed footer logo: {rel}")
    print(f"  {fixed_logos} pages updated")

    print("\n=== Fix 3: Deal Radar — wire real affiliate deals ===")
    fix_deal_radar()

    print("\n=== Done ===")
