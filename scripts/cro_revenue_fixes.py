"""
CRO Revenue Fixes — Audit-Driven Execution

Fixes in priority order:
  1. Contabo coupon page: replace direct URL with /go/contabo CJ tracking
  2. Add sticky CTA + FAQ schema to 3 Wave-7 review pages (nordvpn/sucuri/surfshark)
  3. Inject sticky CTAs into all pages with tracked affiliate links that are missing them
  4. Add FAQ schema to pricing-history pages (rich snippet opportunity)
  5. Fix nav CTA on any page using wrong tool's affiliate link

Run: uv run python scripts/cro_revenue_fixes.py
"""
from __future__ import annotations
import re, json, pathlib, sys
from datetime import date

ROOT  = pathlib.Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
TODAY = date.today().isoformat()

# ── Tool configuration (tracked affiliate programs) ───────────────────────────
TOOLS = {
    "nordvpn": {
        "display": "NordVPN",
        "tagline": "6,400+ servers in 111 countries — world's most trusted VPN",
        "affiliate_url": "/go/nordvpn",
        "affiliate_label": "Get NordVPN (72% off)",
        "price_start": "$3.39/month",
    },
    "surfshark": {
        "display": "Surfshark",
        "tagline": "Unlimited devices VPN — best value at $2.19/month",
        "affiliate_url": "/go/surfshark",
        "affiliate_label": "Get Surfshark (80% off)",
        "price_start": "$2.19/month",
    },
    "sucuri": {
        "display": "Sucuri",
        "tagline": "Website firewall, malware removal & CDN — enterprise site security",
        "affiliate_url": "/go/sucuri",
        "affiliate_label": "Get Sucuri",
        "price_start": "$199.99/year",
    },
    "nordpass": {
        "display": "NordPass",
        "tagline": "Zero-knowledge password manager — free plan available",
        "affiliate_url": "/go/nordpass",
        "affiliate_label": "Get NordPass Free",
        "price_start": "Free / $1.99/month",
    },
    "contabo": {
        "display": "Contabo",
        "tagline": "Best budget VPS hosting — 4 vCPU + 4GB RAM from $6.99/month",
        "affiliate_url": "/go/contabo",
        "affiliate_label": "Get Contabo",
        "price_start": "$6.99/month",
    },
    "semrush": {
        "display": "Semrush",
        "tagline": "All-in-one SEO platform — keyword research, site audit, competitor intel",
        "affiliate_url": "/go/semrush",
        "affiliate_label": "Try Semrush Free",
        "price_start": "$139.95/month",
    },
    "shopify": {
        "display": "Shopify",
        "tagline": "Best ecommerce platform — 4M+ stores, 8,000+ apps",
        "affiliate_url": "/go/shopify",
        "affiliate_label": "Try Shopify Free",
        "price_start": "$39/month",
    },
    "elevenlabs": {
        "display": "ElevenLabs",
        "tagline": "Best AI voice generator — free plan, 32 languages",
        "affiliate_url": "/go/elevenlabs",
        "affiliate_label": "Try ElevenLabs Free",
        "price_start": "Free / from $5/month",
    },
    "hostpapa": {
        "display": "HostPapa",
        "tagline": "Best shared hosting for small business — free domain included",
        "affiliate_url": "/go/hostpapa",
        "affiliate_label": "Get HostPapa",
        "price_start": "$2.95/month",
    },
}

# Slug keywords to tool mapping for auto-detection
SLUG_MAP = {
    "nordvpn": "nordvpn",
    "surfshark": "surfshark",
    "sucuri": "sucuri",
    "nordpass": "nordpass",
    "contabo": "contabo",
    "semrush": "semrush",
    "shopify": "shopify",
    "elevenlabs": "elevenlabs",
    "eleven-labs": "elevenlabs",
    "hostpapa": "hostpapa",
}


def detect_tool(fname: str, html: str) -> str | None:
    """Detect which tracked tool a page belongs to."""
    fname_lower = fname.lower()
    for kw, tool in SLUG_MAP.items():
        if kw in fname_lower:
            return tool
    # Fallback: check which /go/ links are most common
    counts = {}
    for slug in TOOLS:
        c = len(re.findall(rf'/go/{slug}', html, re.I))
        if c > 0:
            counts[slug] = c
    if counts:
        return max(counts, key=counts.get)
    return None


def make_sticky_bar(tool_slug: str) -> str:
    t = TOOLS[tool_slug]
    return f"""<div class="sticky-cta" id="sticky-bar" style="position:fixed;bottom:0;left:0;right:0;z-index:199;background:rgba(7,7,13,.95);border-top:1px solid rgba(233,69,96,.2);padding:.75rem 1.5rem;display:none;align-items:center;gap:1rem;flex-wrap:wrap">
  <span style="flex:1;font-size:.88rem;color:rgba(255,248,245,.7)"><strong style="color:#fff">{t['display']}</strong> &mdash; {t['tagline']}</span>
  <a href="{t['affiliate_url']}" target="_blank" rel="noopener sponsored" style="background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.6rem 1.25rem;border-radius:100px;font-weight:700;font-size:.84rem;white-space:nowrap">{t['affiliate_label']}</a>
  <button onclick="this.parentElement.style.display='none'" style="background:none;border:none;color:rgba(255,255,255,.4);cursor:pointer;font-size:1.2rem">&times;</button>
</div>
<script>setTimeout(function(){{var b=document.getElementById('sticky-bar');if(b)b.style.display='flex';}},3500);</script>"""


def make_faq_schema(pairs: list[tuple[str, str]]) -> str:
    items = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]
    schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items}
    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'


def inject_sticky(html: str, tool_slug: str) -> str:
    """Inject sticky bar before </body> if not present."""
    if "sticky-cta" in html or "sticky_cta" in html:
        return html
    bar = make_sticky_bar(tool_slug)
    return html.replace("</body>", bar + "\n</body>", 1)


def inject_faq_before_body(html: str, pairs: list[tuple[str, str]]) -> str:
    """Inject FAQ schema before </head> if FAQPage not present."""
    if '"FAQPage"' in html:
        return html
    schema = make_faq_schema(pairs)
    return html.replace("</head>", schema + "\n</head>", 1)


# ── Fixes ─────────────────────────────────────────────────────────────────────

fixes_applied = []


def fix(path: pathlib.Path, html: str, label: str) -> str:
    fixes_applied.append((label, path.name))
    return html


# ── FIX 1: Contabo coupon page — replace direct URL with /go/contabo ──────────

def fix_contabo_coupon():
    f = PAGES / "contabo-coupon-2026-discount-codes-promo.html"
    if not f.exists():
        print("  SKIP: contabo-coupon not found")
        return
    html = f.read_text(encoding="utf-8")

    # 1. Fix the direct href to contabo.com → /go/contabo
    if 'href="https://contabo.com/' in html:
        html = re.sub(
            r'href="https://contabo\.com/[^"]*"',
            'href="/go/contabo?utm_source=saaspare&utm_medium=affiliate&utm_campaign=coupon" rel="sponsored noopener"',
            html
        )
        # Remove duplicate rel if already there
        html = html.replace('rel="nofollow sponsored" rel="sponsored noopener"', 'rel="noopener sponsored"')
        html = re.sub(r'\brel="[^"]*"\s+rel="[^"]*"', 'rel="noopener sponsored"', html)
        fixes_applied.append(("fix_direct_url_to_tracked", f.name))

    # 2. Update the CTA button style
    html = html.replace(
        'style="background:#f59e0b;color:#fff;padding:.75rem 1.5rem;border-radius:6px;text-decoration:none;font-weight:700;"',
        'style="background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.8rem 1.6rem;border-radius:100px;font-weight:700;font-size:.95rem;display:inline-block;box-shadow:0 8px 24px rgba(233,69,96,.35)"'
    )

    # 3. Add affiliate tracking event script if not present
    if "affiliate_click" not in html:
        tracking = """<script>
(function(){document.addEventListener('click',function(e){var a=e.target.closest('a[href*="/go/"]');if(a&&window.gtag)gtag('event','affiliate_click',{tool_slug:'contabo',page_path:window.location.pathname,link_href:a.getAttribute('href')});},{capture:true,passive:true});})();
</script>"""
        html = html.replace("</body>", tracking + "\n</body>", 1)
        fixes_applied.append(("inject_affiliate_tracking", f.name))

    # 4. Add sticky CTA
    html = inject_sticky(html, "contabo")
    fixes_applied.append(("inject_sticky_cta", f.name))

    # 5. Fix nav CTA if it points to nordvpn instead of contabo
    if '/go/nordvpn' in html[:2000]:  # nav area
        # Replace first occurrence (in nav) only
        html = html.replace(
            'href="/go/nordvpn"',
            'href="/go/contabo"',
            1
        )
        html = html.replace('Get NordVPN (72% off)', 'Get Contabo', 1)
        fixes_applied.append(("fix_wrong_nav_cta", f.name))

    f.write_text(html, encoding="utf-8")
    print(f"  FIXED: {f.name}")


# ── FIX 2: Add sticky CTA + FAQ schema to Wave-7 review pages ─────────────────

REVIEW_FAQ = {
    "nordvpn": [
        ("Is NordVPN worth it in 2026?", "Yes — NordVPN is the best all-round VPN for most users. The 2-year plan at $3.39/month is exceptional value. PwC-audited no-logs, 6,400+ servers, and NordLynx (WireGuard) speeds make it the most trusted VPN available."),
        ("Does NordVPN keep logs?", "No — NordVPN has a verified no-logs policy, independently audited by PwC. No browsing data, connection timestamps, or IP addresses are stored."),
        ("Is NordVPN faster than ExpressVPN?", "NordLynx (WireGuard-based) protocol makes NordVPN comparable to ExpressVPN and sometimes faster on long-distance connections. ExpressVPN's Lightway protocol is slightly faster on some benchmarks, but the difference is negligible for most users."),
        ("How many devices can NordVPN cover?", "NordVPN allows up to 10 simultaneous device connections on the Complete plan. Basic plan allows 6 devices. One account works on Windows, Mac, iOS, Android, Linux, and routers."),
        ("Does NordVPN have a free trial?", "NordVPN offers a 30-day money-back guarantee on all plans — effectively a risk-free trial. No completely free tier is available."),
    ],
    "sucuri": [
        ("Is Sucuri worth it for WordPress?", "Yes — if your site handles payments, user data, or receives significant traffic, Sucuri's unlimited malware removal and edge WAF justify the $199.99/year cost. For personal blogs, consider Wordfence free first."),
        ("Does Sucuri actually remove malware?", "Yes — Sucuri's security team manually removes malware from your site under SLA. Basic Platform promises removal within 12 hours; Business Platform guarantees 6-hour response."),
        ("Is Sucuri better than Wordfence?", "Sucuri is better for edge-level protection — its WAF blocks attacks before they hit your server. Wordfence is better for WordPress-specific hardening at the server level. For sites under active attack, Sucuri is the right choice."),
        ("Does Sucuri slow down my website?", "No — Sucuri's CDN typically speeds up your site by 20-60% because all traffic routes through Sucuri's globally distributed Anycast network. The WAF filtering adds negligible latency."),
        ("How much does Sucuri cost per year?", "Sucuri Basic Platform costs $199.99/year ($16.67/month). Pro Platform is $299.99/year. Business Platform is $499.99/year. All plans include unlimited malware removal."),
    ],
    "surfshark": [
        ("Is Surfshark worth it in 2026?", "Yes — Surfshark is the best value VPN on the market. Unlimited device connections, $2.19/month on the 2-year plan, and a 30-day money-back guarantee make it the #1 choice for families and households."),
        ("How many devices can Surfshark connect at once?", "Unlimited — Surfshark allows unlimited simultaneous device connections on all plans. This makes it the best VPN for households with many devices."),
        ("Is Surfshark as good as NordVPN?", "Surfshark is slightly less fast and has a smaller server network (3,200 vs NordVPN's 6,400). However, Surfshark is cheaper ($2.19/month vs $3.39/month) and supports unlimited devices. For families on a budget, Surfshark wins."),
        ("Does Surfshark have a free trial?", "Surfshark offers a 7-day free trial on iOS and Android (no credit card required) plus a 30-day money-back guarantee on all plans."),
        ("Is Surfshark safe to use?", "Yes — Surfshark uses AES-256-GCM encryption, a verified no-logs policy audited by Cure53, and RAM-only servers that wipe data on reboot."),
    ],
}


def fix_wave7_review_pages():
    for tool_slug, faq_pairs in REVIEW_FAQ.items():
        fname = f"{tool_slug}-review-2026-is-it-worth-it-honest-verdict.html"
        f = PAGES / fname
        if not f.exists():
            print(f"  SKIP: {fname} not found")
            continue
        html = f.read_text(encoding="utf-8")
        changed = False

        # Add sticky CTA
        if "sticky-cta" not in html and "sticky_cta" not in html:
            html = inject_sticky(html, tool_slug)
            fixes_applied.append(("inject_sticky_cta", fname))
            changed = True

        # Add FAQ schema
        if '"FAQPage"' not in html:
            html = inject_faq_before_body(html, faq_pairs)
            fixes_applied.append(("inject_faq_schema", fname))
            changed = True

        if changed:
            f.write_text(html, encoding="utf-8")
            print(f"  FIXED: {fname}")
        else:
            print(f"  OK:    {fname}")


# ── FIX 3: Inject sticky CTAs across ALL tracked-affiliate pages missing them ──

def fix_missing_sticky_ctAs():
    """
    Find all pages that:
    1. Have at least one /go/{tracked_slug} link
    2. Are missing a sticky CTA
    3. Are not noindex
    """
    TRACKED = set(TOOLS.keys()) | {"nordvpn-kr", "surfshark-vpn", "semrush-one", "semrush-seo", "semrush-trial",
                                     "shopify-ecommerce", "shopify-plus", "shopify-store",
                                     "elevenlabs-ai", "elevenlabs-voice", "eleven-labs"}

    count = 0
    skipped = []

    for f in sorted(PAGES.glob("*.html")):
        html = f.read_text(encoding="utf-8", errors="replace")

        # Skip noindex, skip pages already with sticky
        if 'content="noindex' in html or "sticky-cta" in html or "sticky_cta" in html:
            continue

        # Find which tracked tool this page uses most
        tool_hits = {}
        for slug in TOOLS:
            c = len(re.findall(rf'/go/{re.escape(slug)}', html))
            if c > 0:
                tool_hits[slug] = c

        # Also count aliases
        alias_map = {
            "nordvpn-kr": "nordvpn", "surfshark-vpn": "surfshark",
            "semrush-one": "semrush", "semrush-seo": "semrush", "semrush-trial": "semrush",
            "shopify-ecommerce": "shopify", "shopify-plus": "shopify", "shopify-store": "shopify",
            "elevenlabs-ai": "elevenlabs", "elevenlabs-voice": "elevenlabs", "eleven-labs": "elevenlabs",
        }
        for alias, canonical in alias_map.items():
            c = len(re.findall(rf'/go/{re.escape(alias)}', html))
            if c > 0:
                tool_hits[canonical] = tool_hits.get(canonical, 0) + c

        if not tool_hits:
            continue

        # Pick the dominant tool
        tool_slug = max(tool_hits, key=tool_hits.get)

        # Inject sticky
        new_html = inject_sticky(html, tool_slug)
        if new_html != html:
            f.write_text(new_html, encoding="utf-8")
            count += 1
            fixes_applied.append(("inject_sticky_cta", f.name))

    print(f"  Injected sticky CTAs into {count} additional pages")


# ── FIX 4: Add FAQ schema to pricing-history pages ────────────────────────────

PRICING_HISTORY_FAQ = {
    "hubspot": ("HubSpot", "$45/month (Marketing Hub Starter)", "HubSpot was free initially and began pricing tiers in 2014. The platform has increased prices significantly since 2020, with the most recent increases in 2023-2024."),
    "clickup": ("ClickUp", "Free / $7/user/month (Unlimited)", "ClickUp launched with generous free plan pricing and has maintained relatively stable pricing, with incremental increases as features expanded."),
    "asana": ("Asana", "Free / $10.99/user/month (Premium)", "Asana has raised prices multiple times since going public in 2020. The Premium plan moved from $9.99 to $10.99/user/month, with Enterprise pricing now contact-only."),
    "ahrefs": ("Ahrefs", "$129/month (Lite)", "Ahrefs restructured pricing significantly in 2023, moving away from user-seat pricing to a flat subscription with usage limits. Prices have increased 15-30% across plans since 2022."),
    "notion": ("Notion", "Free / $8/user/month (Plus)", "Notion restructured pricing in 2023, reducing the Plus plan and adding an AI add-on. Pricing has been relatively stable for the base product."),
    "monday-com": ("Monday.com", "$9/seat/month (Basic)", "Monday.com has raised prices multiple times since IPO. The Basic plan increased from $8 to $9/seat/month. Pro plan moved from $16 to $19/seat/month."),
    "salesforce": ("Salesforce", "$25/user/month (Starter)", "Salesforce typically increases list prices 3-8% annually. The most significant recent change was the 2023 restructuring of product tiers."),
    "pipedrive": ("Pipedrive", "$14/user/month (Essential)", "Pipedrive raised prices by approximately 10% in 2022 and again in 2024. Essential plan moved from $9.90 to $14/user/month over the past 3 years."),
    "datadog": ("Datadog", "$15/host/month (Infrastructure)", "Datadog has maintained complex usage-based pricing. List prices have increased while expanded free tier and commitment discounts have partially offset the increases."),
    "linear": ("Linear", "Free / $8/user/month (Standard)", "Linear has maintained stable pricing since launch, with the team plan at $8/user/month remaining consistent."),
    "tresorit": ("Tresorit", "$12/user/month (Business Standard)", "Tresorit has increased prices approximately 15-20% since 2022 as a Swiss-based zero-knowledge cloud storage provider."),
    "1password": ("1Password", "$2.99/month (Individual)", "1Password raised team pricing in 2023 from $3.99 to $4.99/user/month. Individual pricing has remained at $2.99/month."),
}


def fix_pricing_history_pages():
    count = 0
    for slug, (display, current_price, history_note) in PRICING_HISTORY_FAQ.items():
        fname = f"{slug}-pricing-history-2026.html"
        f = PAGES / fname
        if not f.exists():
            continue
        html = f.read_text(encoding="utf-8", errors="replace")
        if '"FAQPage"' in html:
            continue

        faq_pairs = [
            (f"What is the current {display} price?", f"{display} currently starts at {current_price}. See the full breakdown: /pages/{slug}-pricing-2026-plans-costs-what-you-actually-pay"),
            (f"Has {display} increased its prices?", history_note),
            (f"How often does {display} change pricing?", f"{display} typically reviews pricing annually. Existing customers are usually grandfathered at their current rate for 12 months when increases occur."),
            (f"Will {display} raise prices in 2026?", f"Based on historical patterns, {display} may adjust pricing in 2026. Annual billing locks in the current rate and is always recommended when price stability matters."),
        ]

        html = inject_faq_before_body(html, faq_pairs)
        f.write_text(html, encoding="utf-8")
        count += 1
        fixes_applied.append(("inject_faq_pricing_history", fname))

    print(f"  Added FAQ schema to {count} pricing-history pages")


# ── FIX 5: Check pages with wrong nav CTAs and fix ────────────────────────────

def fix_wrong_nav_ctas():
    """
    Some old pages have a mismatched nav CTA (e.g., contabo page has /go/nordvpn).
    Find and fix these.
    """
    count = 0
    nav_pattern = re.compile(
        r'<nav[^>]*>.*?</nav>',
        re.DOTALL | re.IGNORECASE
    )

    for f in sorted(PAGES.glob("*.html")):
        fname = f.name
        html = f.read_text(encoding="utf-8", errors="replace")

        # Only check pages that have a clear primary tool
        tool = None
        for slug in TOOLS:
            if fname.startswith(slug + "-") or f"-{slug}-" in fname:
                tool = slug
                break

        if not tool:
            continue

        t = TOOLS[tool]
        # Find nav element
        nav_match = nav_pattern.search(html)
        if not nav_match:
            continue

        nav_html = nav_match.group(0)

        # Check if nav CTA points to a DIFFERENT tool
        nav_go_links = re.findall(r'/go/([^\s"\'?]+)', nav_html)
        if not nav_go_links:
            continue

        nav_primary = nav_go_links[0].split("?")[0]
        # Normalize alias
        alias_map = {"nordvpn-kr": "nordvpn", "surfshark-vpn": "surfshark",
                     "semrush-one": "semrush", "shopify-ecommerce": "shopify"}
        nav_primary = alias_map.get(nav_primary, nav_primary)

        if nav_primary != tool and nav_primary in TOOLS:
            # Wrong tool in nav CTA — fix it
            wrong_tool = TOOLS[nav_primary]
            new_nav = nav_html.replace(
                wrong_tool["affiliate_url"],
                t["affiliate_url"]
            ).replace(
                wrong_tool["affiliate_label"],
                t["affiliate_label"]
            )
            if new_nav != nav_html:
                html = html.replace(nav_html, new_nav, 1)
                f.write_text(html, encoding="utf-8")
                count += 1
                fixes_applied.append(("fix_wrong_nav_cta", fname))

    print(f"  Fixed wrong nav CTAs on {count} pages")


# ── FIX 6: Add affiliate tracking event to pages missing it ───────────────────

TRACKING_SCRIPT_MARKER = "affiliate_click_tracking_v1"
TRACKING_TEMPLATE = """<script>/* affiliate_click_tracking_v1 */
(function(){{document.addEventListener('click',function(e){{var a=e.target.closest('a[href*="/go/"]');if(a&&window.gtag)gtag('event','affiliate_click',{{tool_slug:'{slug}',page_path:window.location.pathname,link_href:a.getAttribute('href')}});}},{{capture:true,passive:true}});}})();
</script>"""


def fix_missing_tracking():
    """Ensure every page with /go/ links has the affiliate_click event firing."""
    count = 0
    for f in sorted(PAGES.glob("*.html")):
        html = f.read_text(encoding="utf-8", errors="replace")
        if TRACKING_SCRIPT_MARKER in html:
            continue
        if '/go/' not in html:
            continue
        if 'content="noindex' in html:
            continue

        # Detect tool
        tool = detect_tool(f.name, html)
        if not tool:
            tool = "saaspare"

        script = TRACKING_TEMPLATE.format(slug=tool)
        html = html.replace("</body>", script + "\n</body>", 1)
        f.write_text(html, encoding="utf-8")
        count += 1
        fixes_applied.append(("inject_affiliate_tracking", f.name))

    print(f"  Injected affiliate_click tracking into {count} pages")


# ── RUN ALL FIXES ─────────────────────────────────────────────────────────────

print("=" * 60)
print("CRO REVENUE FIXES — EXECUTING")
print("=" * 60)

print("\n[1/6] Fix Contabo coupon page (direct URL -> CJ tracking)")
fix_contabo_coupon()

print("\n[2/6] Add sticky CTA + FAQ schema to Wave-7 review pages")
fix_wave7_review_pages()

print("\n[3/6] Inject sticky CTAs across all tracked pages missing them")
fix_missing_sticky_ctAs()

print("\n[4/6] Add FAQ schema to pricing-history pages")
fix_pricing_history_pages()

print("\n[5/6] Fix wrong nav CTAs")
fix_wrong_nav_ctas()

print("\n[6/6] Inject affiliate click tracking")
fix_missing_tracking()

# ── Summary ───────────────────────────────────────────────────────────────────

print()
print("=" * 60)
print("FIXES SUMMARY")
print("=" * 60)
from collections import Counter
by_type = Counter(label for label, _ in fixes_applied)
for fix_type, count in sorted(by_type.items(), key=lambda x: -x[1]):
    print(f"  {fix_type:<40} {count:4d} pages")
print(f"\nTotal fix operations: {len(fixes_applied)}")

# Save report
report_path = ROOT / "outputs" / "cro_fixes_applied.json"
report_path.parent.mkdir(parents=True, exist_ok=True)
report = [{"fix": l, "file": f} for l, f in fixes_applied]
report_path.write_text(json.dumps(report, indent=2))
print(f"Full report: {report_path}")
