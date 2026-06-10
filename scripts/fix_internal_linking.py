"""
Fix the 73 orphan pages by injecting contextual internal links from related pages.

Top priorities (per the May 2026 audit):
1. Category hub pages (best-crm-software-2026 etc.) — 0 incoming links each
2. Pricing history pages (shopify, salesforce, stripe, clickup) — orphaned
3. Best-devtools- pages — orphaned
4. New pricing-moat pages (price-hike-watch, grandfathered, cheaper-alts)

Strategy:
- Inject a "Related from SaaSpare" block in the footer area of every page
- Link cluster pages to their category hub (CRM pages → /best-crm-software-2026)
- Link pricing pages to their pricing-history sibling
- Link comparison pages to both tools' alternatives pages
"""
import re
from pathlib import Path

ROOT  = Path(__file__).resolve().parents[1]
SITE  = ROOT / "site"
PAGES = SITE / "pages"

# Map tool keywords to their category hub
TOOL_TO_HUB = {
    # CRM
    "hubspot": "best-crm-software-2026",
    "salesforce": "best-crm-software-2026",
    "pipedrive": "best-crm-software-2026",
    "zoho-crm": "best-crm-software-2026",
    "monday-sales-crm": "best-crm-software-2026",
    # Project management
    "asana": "best-project-management-software-2026",
    "monday": "best-project-management-software-2026",
    "clickup": "best-project-management-software-2026",
    "trello": "best-project-management-software-2026",
    "notion": "best-project-management-software-2026",
    "linear": "best-project-management-software-2026",
    "jira": "best-project-management-software-2026",
    "wrike": "best-project-management-software-2026",
    "basecamp": "best-project-management-software-2026",
    "smartsheet": "best-project-management-software-2026",
    # SEO tools
    "semrush": "best-seo-tools-2026",
    "ahrefs": "best-seo-tools-2026",
    "moz-pro": "best-seo-tools-2026",
    "moz": "best-seo-tools-2026",
    "surfer-seo": "best-seo-tools-2026",
    "surfer": "best-seo-tools-2026",
    "se-ranking": "best-seo-tools-2026",
    "frase-io": "best-seo-tools-2026",
    "frase": "best-seo-tools-2026",
    "spyfu": "best-seo-tools-2026",
    "rankmath": "best-seo-tools-2026",
    "kwfinder": "best-seo-tools-2026",
    "mangools": "best-seo-tools-2026",
    "clearscope": "best-seo-tools-2026",
    # Password managers
    "1password": "best-password-manager-business-2026",
    "lastpass": "best-password-manager-business-2026",
    "bitwarden": "best-password-manager-business-2026",
    "dashlane": "best-password-manager-business-2026",
    "keeper": "best-password-manager-business-2026",
    "nordpass": "best-password-manager-business-2026",
    "roboform": "best-password-manager-business-2026",
    "sticky-password": "best-password-manager-business-2026",
    # Video conferencing
    "zoom": "best-video-conferencing-software-2026",
    "webex": "best-video-conferencing-software-2026",
    "google-meet": "best-video-conferencing-software-2026",
    "ms-teams": "best-video-conferencing-software-2026",
    "microsoft-teams": "best-video-conferencing-software-2026",
    "around": "best-video-conferencing-software-2026",
    "whereby": "best-video-conferencing-software-2026",
    "riverside-fm": "best-video-conferencing-software-2026",
    "streamyard": "best-video-conferencing-software-2026",
    "loom": "best-video-conferencing-software-2026",
    # Marketing automation
    "mailchimp": "best-marketing-automation-software-2026",
    "activecampaign": "best-marketing-automation-software-2026",
    "klaviyo": "best-marketing-automation-software-2026",
    "getresponse": "best-marketing-automation-software-2026",
    "brevo": "best-marketing-automation-software-2026",
    "marketo": "best-marketing-automation-software-2026",
    # VPN / security
    "nordlayer": "best-vpn-for-business-2026",
    "perimeter-81": "best-vpn-for-business-2026",
    "twingate": "best-vpn-for-business-2026",
    "tailscale": "best-vpn-for-business-2026",
    "zscaler": "best-vpn-for-business-2026",
    "expressvpn-business": "best-vpn-for-business-2026",
    "openvpn": "best-vpn-for-business-2026",
    "wireguard": "best-vpn-for-business-2026",
    "cisco-anyconnect": "best-vpn-for-business-2026",
    "cloudflare-access": "best-vpn-for-business-2026",
    # HR
    "bamboohr": "best-hr-software-2026",
    "gusto": "best-hr-software-2026",
    "rippling": "best-hr-software-2026",
    "deel": "best-hr-software-2026",
    "remote-com": "best-hr-software-2026",
    "remote": "best-hr-software-2026",
    "workday": "best-hr-software-2026",
    "adp": "best-hr-software-2026",
    "lattice": "best-hr-software-2026",
    "culture-amp": "best-hr-software-2026",
}

HUB_DISPLAY = {
    "best-crm-software-2026": "Best CRM Software 2026",
    "best-project-management-software-2026": "Best Project Management Software 2026",
    "best-seo-tools-2026": "Best SEO Tools 2026",
    "best-password-manager-business-2026": "Best Business Password Manager 2026",
    "best-video-conferencing-software-2026": "Best Video Conferencing Software 2026",
    "best-marketing-automation-software-2026": "Best Marketing Automation Software 2026",
    "best-vpn-for-business-2026": "Best VPN for Business 2026",
    "best-hr-software-2026": "Best HR Software 2026",
}

stats = {"hub_links_added": 0, "history_links_added": 0, "moat_links_added": 0, "total_changed": 0}


def get_hub_for_page(filename: str) -> str | None:
    """Match a page filename to its parent category hub."""
    name = filename.replace(".html", "").lower()
    # Sort by key length so longer matches win
    for key in sorted(TOOL_TO_HUB.keys(), key=len, reverse=True):
        if key in name:
            return TOOL_TO_HUB[key]
    return None


def inject_hub_link(html: str, hub_slug: str, current_slug: str) -> tuple[str, bool]:
    """Add a link to the parent category hub in the page footer area."""
    # Skip if the page IS the hub
    if current_slug == hub_slug:
        return html, False
    # Skip if hub link already present
    if f"/{hub_slug}" in html:
        return html, False

    hub_label = HUB_DISPLAY.get(hub_slug, hub_slug.replace("-", " ").title())
    link_block = f'\n<aside style="margin:32px 0;padding:18px 22px;background:rgba(255,255,255,.06);border-radius:8px;font-size:.92rem;"><strong>Category guide:</strong> See our editorial roundup → <a href="/{hub_slug}">{hub_label}</a></aside>\n'

    # Inject before <main> closing tag, or before </article>, or before footer
    for marker in ["</main>", "</article>", '<footer'.lower(), "</body>"]:
        if marker in html:
            html = html.replace(marker, link_block + marker, 1)
            return html, True
    return html, False


def inject_history_link(html: str, current_slug: str) -> tuple[str, bool]:
    """If this is a pricing page, link to its sibling pricing-history page."""
    m = re.match(r'^([\w-]+?)-pricing-(\d{4})-plans-costs-what-you-actually-pay$', current_slug)
    if not m:
        return html, False
    tool = m.group(1)
    year = m.group(2)
    history_slug = f"{tool}-pricing-history-{year}"
    history_path = PAGES / f"{history_slug}.html"
    if not history_path.exists():
        return html, False
    if f"/{history_slug}" in html:
        return html, False

    link_block = f'\n<aside style="margin:24px 0;padding:16px 20px;background:rgba(234,88,12,.12);border-left:4px solid #ea580c;border-radius:0 8px 8px 0;font-size:.92rem;"><strong>📊 See pricing history:</strong> Every change to {tool.replace("-", " ").title()} pricing in {year}, timestamped → <a href="/pages/{history_slug}" style="color:#fdba74;font-weight:700;">{tool.replace("-", " ").title()} Pricing History {year}</a></aside>\n'
    for marker in ["</main>", "</article>", "</body>"]:
        if marker in html:
            html = html.replace(marker, link_block + marker, 1)
            return html, True
    return html, False


def inject_moat_link(html: str, current_slug: str) -> tuple[str, bool]:
    """Link from pricing/review pages to the price-hike-watch page."""
    moat_slug = "saas-price-hike-watch-may-2026"
    if "/saas-price-hike-watch-may-2026" in html:
        return html, False
    if current_slug == moat_slug:
        return html, False
    # Only inject on pricing and review pages
    if "pricing" not in current_slug and "review" not in current_slug:
        return html, False

    link_block = '\n<aside style="margin:24px 0;padding:14px 18px;background:rgba(220,38,38,.12);border-left:4px solid #dc2626;border-radius:0 6px 6px 0;font-size:.88rem;">⚡ <strong>Did this tool raise prices in 2026?</strong> See our <a href="/pages/saas-price-hike-watch-may-2026" style="color:#fca5a5;font-weight:700;">SaaS Price Hike Watch</a> for every confirmed 2026 price increase.</aside>\n'
    for marker in ["</main>", "</article>", "</body>"]:
        if marker in html:
            html = html.replace(marker, link_block + marker, 1)
            return html, True
    return html, False


def patch_page(path: Path) -> bool:
    try:
        html = path.read_text(encoding="utf-8")
    except Exception:
        return False
    original = html
    slug = path.stem

    # 1. Add hub link
    hub = get_hub_for_page(path.name)
    if hub:
        html, did = inject_hub_link(html, hub, slug)
        if did:
            stats["hub_links_added"] += 1

    # 2. Add pricing-history sibling link
    html, did = inject_history_link(html, slug)
    if did:
        stats["history_links_added"] += 1

    # 3. Add moat link (price-hike-watch) on pricing/review pages
    html, did = inject_moat_link(html, slug)
    if did:
        stats["moat_links_added"] += 1

    if html != original:
        path.write_text(html, encoding="utf-8")
        stats["total_changed"] += 1
        return True
    return False


def main():
    targets = list(PAGES.glob("*.html")) + list(SITE.glob("best-*-2026.html"))
    print(f"Processing {len(targets)} pages...")
    for p in targets:
        patch_page(p)
    print()
    print("=== RESULTS ===")
    print(f"  Category hub links added:    {stats['hub_links_added']}")
    print(f"  Pricing history links added: {stats['history_links_added']}")
    print(f"  Price-hike-watch links:      {stats['moat_links_added']}")
    print(f"  TOTAL pages changed:         {stats['total_changed']}")


if __name__ == "__main__":
    main()
