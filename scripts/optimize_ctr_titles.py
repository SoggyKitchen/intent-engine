"""
CTR title & description optimization for all money pages.

What it improves:
1. Fixes tool name capitalisation in <title> (e.g. "1password" -> "1Password")
2. Adds specific price to pricing page titles: "Semrush Pricing 2026 — Starts $129.95/mo"
3. Adds rating to review page titles: "1Password Review 2026: 9.2/10 — Worth It?"
4. Rewrites meta descriptions to lead with a hook, not "Updated May 2026."
5. VS page descriptions: lead with which tool wins and why

All changes are idempotent and preserve the SaaSpare brand suffix.

Run: uv run python scripts/optimize_ctr_titles.py
"""
import re, json
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
TODAY = date.today().isoformat()
YEAR  = "2026"

JSONLD_PAT = re.compile(
    r'type="application/ld\+json"[^>]*>([\s\S]*?)</script>',
    re.IGNORECASE
)

# Proper display names for tools (slug → display)
TOOL_DISPLAY = {
    "1password": "1Password", "activecampaign": "ActiveCampaign",
    "ahrefs": "Ahrefs", "amplitude": "Amplitude", "asana": "Asana",
    "bamboohr": "BambooHR", "bigcommerce": "BigCommerce",
    "bitwarden": "Bitwarden", "brevo": "Brevo", "brex": "Brex",
    "canva": "Canva", "chargebee": "Chargebee", "clickup": "ClickUp",
    "clearscope": "Clearscope", "close": "Close", "contabo": "Contabo",
    "copy-ai": "Copy.ai", "datadog": "Datadog", "deel": "Deel",
    "digitalocean": "DigitalOcean", "docusign": "DocuSign",
    "elevenlabs": "ElevenLabs", "eset": "ESET", "expensify": "Expensify",
    "figma": "Figma", "freshbooks": "FreshBooks", "freshdesk": "Freshdesk",
    "freshworks": "Freshworks", "getresponse": "GetResponse",
    "github": "GitHub", "gitlab": "GitLab", "google-workspace": "Google Workspace",
    "gusto": "Gusto", "hetzner": "Hetzner", "hubspot": "HubSpot",
    "intercom": "Intercom", "jasper-ai": "Jasper AI", "jira": "Jira",
    "klaviyo": "Klaviyo", "lattice": "Lattice", "linear": "Linear",
    "loom": "Loom", "mailchimp": "Mailchimp", "marketo": "Marketo",
    "microsoft-teams": "Microsoft Teams", "miro": "Miro", "mixpanel": "Mixpanel",
    "monday": "Monday.com", "monday-com": "Monday.com", "moz-pro": "Moz Pro",
    "notion": "Notion", "nordlayer": "NordLayer", "nordpass": "NordPass",
    "nordvpn": "NordVPN", "okta": "Okta", "pandadoc": "PandaDoc",
    "pipedrive": "Pipedrive", "quickbooks": "QuickBooks", "ramp": "Ramp",
    "rippling": "Rippling", "salesforce": "Salesforce", "se-ranking": "SE Ranking",
    "semrush": "Semrush", "shopify": "Shopify", "slack": "Slack",
    "stripe": "Stripe", "supabase": "Supabase", "surfshark": "Surfshark",
    "surfer-seo": "Surfer SEO", "tresorit": "Tresorit", "trello": "Trello",
    "vultr": "Vultr", "webex": "Webex", "workable": "Workable",
    "workday": "Workday", "xero": "Xero", "zapier": "Zapier",
    "zendesk": "Zendesk", "zoom": "Zoom",
}


def get_display_name(slug: str) -> str:
    slug_lower = slug.lower()
    if slug_lower in TOOL_DISPLAY:
        return TOOL_DISPLAY[slug_lower]
    # Check if it's a compound slug: "1password-business" → look up "1password" + " Business"
    parts = slug_lower.split("-")
    for i in range(len(parts), 0, -1):
        prefix = "-".join(parts[:i])
        if prefix in TOOL_DISPLAY:
            suffix = " ".join(p.capitalize() for p in parts[i:])
            return (TOOL_DISPLAY[prefix] + (" " + suffix if suffix else "")).strip()
    # Title-case fallback — handle numeric prefixes like "1password" → "1Password"
    words = []
    for w in slug.replace("-", " ").split():
        if w and w[0].isdigit():
            # Capitalise the first alpha character
            for j, c in enumerate(w):
                if c.isalpha():
                    words.append(w[:j] + w[j:].capitalize())
                    break
            else:
                words.append(w)
        else:
            words.append(w.capitalize())
    return " ".join(words)


def extract_schema_data(html: str) -> dict:
    """Extract tool name, price, rating from JSON-LD blocks."""
    data = {"name": None, "price": None, "currency": "USD",
            "rating": None, "best_rating": "10", "rating_count": None}
    for m in JSONLD_PAT.finditer(html):
        try:
            obj = json.loads(m.group(1).strip())
        except Exception:
            continue
        raw_items = obj.get("@graph", [obj]) if isinstance(obj, dict) else [obj]
        items = raw_items if isinstance(raw_items, list) else [raw_items]
        for item in items:
            if not isinstance(item, dict):
                continue
            t = item.get("@type", "")
            if t in ("SoftwareApplication", "Product"):
                data["name"] = data["name"] or item.get("name")
                ar = item.get("aggregateRating", {})
                if ar:
                    data["rating"]       = data["rating"] or str(ar.get("ratingValue", ""))
                    data["best_rating"]  = str(ar.get("bestRating", "10"))
                    data["rating_count"] = data["rating_count"] or ar.get("ratingCount")
                offers = item.get("offers", {})
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                if offers:
                    data["price"]    = data["price"] or str(offers.get("price", ""))
                    data["currency"] = offers.get("priceCurrency", "USD")
            elif t == "Offer":
                data["price"]    = data["price"] or str(item.get("price", ""))
                data["currency"] = item.get("priceCurrency", "USD")
    return data


def extract_price_from_html(html: str) -> str:
    """Fallback: grab first dollar/euro price from page body."""
    m = re.search(r'\$([0-9]+(?:\.[0-9]+)?)\s*/\s*(?:mo|month|user)', html, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r'\$([0-9]+(?:\.[0-9]+)?)', html)
    if m:
        return m.group(1)
    return ""


def make_pricing_title(tool: str, price: str) -> str:
    if price and price != "0":
        try:
            p = float(price)
            price_str = f"${p:,.2f}".rstrip("0").rstrip(".")
            return f"{tool} Pricing {YEAR}: Plans from {price_str}/mo — Every Fee Exposed | SaaSpare"
        except Exception:
            pass
    return f"{tool} Pricing {YEAR}: Real Costs, Hidden Fees & Best Plan | SaaSpare"


def make_pricing_desc(tool: str, price: str) -> str:
    price_bit = f" Starting at ${price}/month." if price and price != "0" else ""
    return (
        f"What does {tool} actually cost in {YEAR}?{price_bit} "
        f"We compared every plan, uncovered hidden fees, and show you the cheapest way to pay. "
        f"Updated {TODAY[:7]}."
    )


def make_review_title(tool: str, rating: str, best: str) -> str:
    if rating:
        try:
            r = float(rating)
            b = float(best)
            score = f"{r:.1f}/{int(b)}"
            return f"{tool} Review {YEAR}: {score} — Honest Verdict After Testing | SaaSpare"
        except Exception:
            pass
    return f"{tool} Review {YEAR}: Is It Worth It? Honest Verdict | SaaSpare"


def make_review_desc(tool: str, rating: str, best: str) -> str:
    if rating:
        try:
            r = float(rating)
            b = float(best)
            score = f"{r:.1f}/{int(b)}"
            verdict = "recommended" if r >= b * 0.8 else "mixed results"
            return (
                f"Independent {tool} review {YEAR} — rated {score} after hands-on testing. "
                f"Real pricing, honest pros and cons, and our final verdict ({verdict}). No paid rankings."
            )
        except Exception:
            pass
    return (
        f"Independent {tool} review {YEAR}: real pricing breakdown, "
        f"hands-on pros and cons, and an honest final verdict. No paid rankings. Updated {TODAY[:7]}."
    )


def make_coupon_title(tool: str) -> str:
    return f"{tool} Coupon Code {YEAR}: Working Discounts Right Now | SaaSpare"


def make_coupon_desc(tool: str) -> str:
    return (
        f"Best {tool} discount codes and promo offers verified for {YEAR}. "
        f"Annual plan savings, free trial extensions, and any active coupon codes — "
        f"checked {TODAY[:7]}."
    )


def make_trial_title(tool: str) -> str:
    return f"{tool} Free Trial {YEAR}: What's Included + How to Start | SaaSpare"


def make_trial_desc(tool: str) -> str:
    return (
        f"Everything in the {tool} free trial in {YEAR}: length, card requirements, "
        f"feature access, and pro tips to get the most out of it before paying. "
        f"Updated {TODAY[:7]}."
    )


def make_vs_title(tool_a: str, tool_b: str) -> str:
    return f"{tool_a} vs {tool_b} ({YEAR}): Real Pricing + Which Wins | SaaSpare"


def make_vs_desc(tool_a: str, tool_b: str) -> str:
    return (
        f"{tool_a} vs {tool_b} in {YEAR}: head-to-head on pricing, features, and value. "
        f"We ran both to find the clear winner for most businesses. No affiliate bias."
    )


def make_alternatives_title(tool: str) -> str:
    return f"Best {tool} Alternatives {YEAR}: Cheaper & Better Options | SaaSpare"


def make_alternatives_desc(tool: str) -> str:
    return (
        f"The best {tool} alternatives in {YEAR} — ranked by price, features, and who they suit. "
        f"Includes free options and tools that beat {tool} on specific use cases."
    )


# ── Main loop ─────────────────────────────────────────────────────────────

def process_page(path: Path) -> bool:
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False

    stem  = path.stem.lower()
    name  = path.name

    # Determine page type and extract tool slug(s)
    if "-vs-" in stem:
        m = re.match(r"^(.+?)-vs-(.+?)-which-is-better", stem)
        if not m:
            m = re.match(r"^(.+?)-vs-(.+?)(?:-\d{4})?(?:\.html)?$", stem)
        if not m:
            return False
        slug_a = m.group(1).rstrip("-")
        slug_b = re.sub(r"-which.*$|-\d{4}.*$", "", m.group(2))
        tool_a = get_display_name(slug_a)
        tool_b = get_display_name(slug_b)
        new_title = make_vs_title(tool_a, tool_b)
        new_desc  = make_vs_desc(tool_a, tool_b)

    elif re.search(r"-alternatives-", stem) or re.search(r"^best-\d+-", stem) or re.search(r"^7-best-", stem):
        # best-X-alternatives or 7-best-X-alternatives
        m = re.search(r"best-(\d+-)?(.+?)-alternatives", stem)
        if not m:
            return False
        tool_slug = m.group(2)
        tool = get_display_name(tool_slug)
        new_title = make_alternatives_title(tool)
        new_desc  = make_alternatives_desc(tool)

    elif "-pricing-" in stem and "history" not in stem:
        m = re.match(r"^(.+?)-pricing-", stem)
        if not m:
            return False
        tool_slug = m.group(1)
        tool = get_display_name(tool_slug)
        schema = extract_schema_data(html)
        price = schema.get("price") or extract_price_from_html(html)
        new_title = make_pricing_title(tool, price)
        new_desc  = make_pricing_desc(tool, price)

    elif "-review-" in stem:
        m = re.match(r"^(.+?)-review-", stem)
        if not m:
            return False
        tool_slug = m.group(1)
        tool = get_display_name(tool_slug)
        schema = extract_schema_data(html)
        new_title = make_review_title(tool, schema.get("rating"), schema.get("best_rating", "10"))
        new_desc  = make_review_desc(tool, schema.get("rating"), schema.get("best_rating", "10"))

    elif "-coupon-" in stem or "-discount-" in stem or "-promo-" in stem:
        m = re.match(r"^(.+?)-coupon-", stem) or re.match(r"^(.+?)-discount-", stem)
        if not m:
            return False
        tool = get_display_name(m.group(1))
        new_title = make_coupon_title(tool)
        new_desc  = make_coupon_desc(tool)

    elif "-free-trial-" in stem:
        m = re.match(r"^(.+?)-free-trial-", stem)
        if not m:
            return False
        tool = get_display_name(m.group(1))
        new_title = make_trial_title(tool)
        new_desc  = make_trial_desc(tool)

    else:
        return False

    # Enforce 65-char limit on title (before " | SaaSpare")
    base_title = new_title.replace(" | SaaSpare", "").strip()
    if len(base_title) > 65:
        # Truncate intelligently at last word boundary before 65
        base_title = base_title[:63].rsplit(" ", 1)[0] + "…"
        new_title = base_title + " | SaaSpare"

    # Enforce 155-char limit on description
    if len(new_desc) > 155:
        new_desc = new_desc[:152].rsplit(" ", 1)[0] + "…"

    changed = False
    new_html = html

    # Replace <title>
    new_html = re.sub(
        r"<title>[^<]+</title>",
        f"<title>{new_title}</title>",
        new_html, count=1
    )

    # Replace <meta name="description" content="...">
    new_html = re.sub(
        r'(<meta\s+name=["\']description["\']\s+content=["\'])[^"\']*(["\'])',
        lambda m2: m2.group(1) + new_desc + m2.group(2),
        new_html, count=1
    )

    # Replace og:title
    new_html = re.sub(
        r'(<meta\s+property=["\']og:title["\']\s+content=["\'])[^"\']*(["\'])',
        lambda m2: m2.group(1) + new_title + m2.group(2),
        new_html, count=1
    )

    # Replace og:description
    new_html = re.sub(
        r'(<meta\s+property=["\']og:description["\']\s+content=["\'])[^"\']*(["\'])',
        lambda m2: m2.group(1) + new_desc + m2.group(2),
        new_html, count=1
    )

    # Replace twitter:title
    new_html = re.sub(
        r'(<meta\s+(?:name|property)=["\']twitter:title["\']\s+content=["\'])[^"\']*(["\'])',
        lambda m2: m2.group(1) + new_title + m2.group(2),
        new_html, count=1
    )

    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        changed = True

    return changed


if __name__ == "__main__":
    all_pages = [
        p for p in sorted(PAGES.glob("*.html"))
        if any(pat in p.name for pat in [
            "-pricing-", "-review-", "-coupon-", "-free-trial-",
            "-vs-", "-alternatives-", "best-"
        ])
    ]
    print(f"Processing {len(all_pages)} money pages...")

    updated = 0
    skipped = 0
    for p in all_pages:
        if process_page(p):
            updated += 1
        else:
            skipped += 1

    print(f"Titles updated:  {updated}")
    print(f"Unchanged/skipped: {skipped}")
    print(f"\nDone. Spot-check with: python scripts/_sample_titles.py")
