"""
Wave 10: Patch internal links on existing NordVPN/Surfshark/NordPass pages
to cross-link to the new Wave 8/9 pages.

Updates the <!-- related-links-start --> block in each target page to include
the most relevant new comparison, free-trial, coupon, and alternatives pages.

Run: uv run python scripts/patch_wave8_internal_links.py
"""
from pathlib import Path
import re

ROOT  = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
YEAR  = "2026"

RELATED_BLOCK_RE = re.compile(
    r'<!-- related-links-start.*?-->.*?<!-- related-links-end -->',
    re.DOTALL
)


def make_related_block(links: list[tuple[str, str]]) -> str:
    """links: list of (href, label)"""
    items = "\n".join(
        f'    <li><a href="{href}">{label}</a></li>'
        for href, label in links
    )
    return f"""<!-- related-links-start (do not edit: managed by internal_links.py) -->
<aside class="related-links" aria-label="Related comparisons" style="max-width:920px;margin:3rem auto;padding:1.5rem;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:14px">
  <h2 style="font-size:1.1rem;margin:0 0 1rem 0;color:#e94560">Related comparisons &amp; guides</h2>
  <ul style="list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:.7rem">
{items}
  </ul>
</aside>
<!-- related-links-end -->"""


# ── Patches to apply ──────────────────────────────────────────────────────────

PATCHES = {
    # NordVPN review → link to VS pages + free-trial + coupon
    f"nordvpn-review-{YEAR}-is-it-worth-it-honest-verdict.html": [
        (f"/pages/nordvpn-pricing-{YEAR}-plans-costs-what-you-actually-pay", "NordVPN Pricing 2026: Every Plan & Real Costs"),
        (f"/pages/nordvpn-free-trial-{YEAR}-how-to-get-it-step-by-step", "NordVPN Free Trial 2026: How to Get It"),
        (f"/pages/nordvpn-coupon-code-promo-codes-{YEAR}-verified-discounts", "NordVPN Coupon Codes 2026: Verified Deals"),
        (f"/pages/nordvpn-vs-surfshark-which-is-better-in-{YEAR}", "NordVPN vs Surfshark 2026: Which Is Better?"),
        (f"/pages/nordvpn-vs-expressvpn-which-is-better-in-{YEAR}", "NordVPN vs ExpressVPN 2026: Full Comparison"),
        (f"/pages/nordvpn-vs-cyberghost-which-is-better-in-{YEAR}", "NordVPN vs CyberGhost 2026: Which Wins?"),
        (f"/pages/best-nordvpn-alternatives-in-{YEAR}-free-paid", "7 Best NordVPN Alternatives 2026"),
        (f"/pages/best-vpn-for-privacy-and-security-{YEAR}", "Best VPN 2026: Top 5 Tested & Ranked"),
    ],
    # NordVPN pricing → link to review + VS pages + alternatives
    f"nordvpn-pricing-{YEAR}-plans-costs-what-you-actually-pay.html": [
        (f"/pages/nordvpn-review-{YEAR}-is-it-worth-it-honest-verdict", "NordVPN Review 2026: Honest Verdict"),
        (f"/pages/nordvpn-free-trial-{YEAR}-how-to-get-it-step-by-step", "NordVPN Free Trial 2026: Step-by-Step"),
        (f"/pages/nordvpn-coupon-code-promo-codes-{YEAR}-verified-discounts", "NordVPN Coupon Codes 2026"),
        (f"/pages/nordvpn-vs-surfshark-which-is-better-in-{YEAR}", "NordVPN vs Surfshark 2026"),
        (f"/pages/surfshark-pricing-{YEAR}-plans-costs-what-you-actually-pay", "Surfshark Pricing 2026: Compare Plans"),
        (f"/pages/best-vpn-for-privacy-and-security-{YEAR}", "Best VPN for Privacy 2026"),
    ],
    # Surfshark review
    f"surfshark-review-{YEAR}-is-it-worth-it-honest-verdict.html": [
        (f"/pages/surfshark-pricing-{YEAR}-plans-costs-what-you-actually-pay", "Surfshark Pricing 2026: Every Plan"),
        (f"/pages/surfshark-free-trial-{YEAR}-how-to-get-it-step-by-step", "Surfshark Free Trial 2026: How to Get It"),
        (f"/pages/surfshark-coupon-code-promo-codes-{YEAR}-verified-discounts", "Surfshark Coupon Codes 2026"),
        (f"/pages/surfshark-vs-nordvpn-which-is-better-in-{YEAR}", "Surfshark vs NordVPN 2026: Which Wins?"),
        (f"/pages/surfshark-vs-expressvpn-which-is-better-in-{YEAR}", "Surfshark vs ExpressVPN 2026"),
        (f"/pages/best-surfshark-alternatives-in-{YEAR}-free-paid", "7 Best Surfshark Alternatives 2026"),
        (f"/pages/best-vpn-for-privacy-and-security-{YEAR}", "Best VPN 2026: Top 5 Ranked"),
    ],
    # Surfshark pricing
    f"surfshark-pricing-{YEAR}-plans-costs-what-you-actually-pay.html": [
        (f"/pages/surfshark-review-{YEAR}-is-it-worth-it-honest-verdict", "Surfshark Review 2026: Honest Verdict"),
        (f"/pages/surfshark-free-trial-{YEAR}-how-to-get-it-step-by-step", "Surfshark Free Trial 2026"),
        (f"/pages/surfshark-coupon-code-promo-codes-{YEAR}-verified-discounts", "Surfshark Coupon Codes 2026"),
        (f"/pages/surfshark-vs-nordvpn-which-is-better-in-{YEAR}", "Surfshark vs NordVPN 2026"),
        (f"/pages/nordvpn-pricing-{YEAR}-plans-costs-what-you-actually-pay", "NordVPN Pricing 2026: Compare Plans"),
        (f"/pages/best-vpn-for-privacy-and-security-{YEAR}", "Best VPN for Privacy 2026"),
    ],
    # Sucuri review
    f"sucuri-review-{YEAR}-is-it-worth-it-honest-verdict.html": [
        (f"/pages/sucuri-pricing-{YEAR}-plans-costs-what-you-actually-pay", "Sucuri Pricing 2026: Every Plan"),
        (f"/pages/sucuri-coupon-code-promo-codes-{YEAR}-verified-discounts", "Sucuri Coupon Codes 2026"),
        (f"/pages/sucuri-vs-wordfence-which-is-better-in-{YEAR}", "Sucuri vs Wordfence 2026: Which Is Better?"),
        (f"/pages/sucuri-vs-cloudflare-which-is-better-in-{YEAR}", "Sucuri vs Cloudflare 2026"),
        (f"/pages/best-sucuri-alternatives-in-{YEAR}-free-paid", "7 Best Sucuri Alternatives 2026"),
    ],
    # Sucuri pricing
    f"sucuri-pricing-{YEAR}-plans-costs-what-you-actually-pay.html": [
        (f"/pages/sucuri-review-{YEAR}-is-it-worth-it-honest-verdict", "Sucuri Review 2026: Honest Verdict"),
        (f"/pages/sucuri-coupon-code-promo-codes-{YEAR}-verified-discounts", "Sucuri Coupon Codes 2026"),
        (f"/pages/sucuri-vs-wordfence-which-is-better-in-{YEAR}", "Sucuri vs Wordfence 2026"),
        (f"/pages/sucuri-vs-cloudflare-which-is-better-in-{YEAR}", "Sucuri vs Cloudflare 2026"),
        (f"/pages/best-sucuri-alternatives-in-{YEAR}-free-paid", "7 Best Sucuri Alternatives"),
    ],
    # NordPass VS comparison pages — link to the new review/pricing pages
    f"1password-vs-nordpass-which-is-better-in-{YEAR}.html": [
        (f"/pages/nordpass-review-{YEAR}-is-it-worth-it-honest-verdict", "NordPass Review 2026: Full Verdict"),
        (f"/pages/nordpass-pricing-{YEAR}-plans-costs-what-you-actually-pay", "NordPass Pricing 2026"),
        (f"/pages/nordpass-free-trial-{YEAR}-how-to-get-it-step-by-step", "NordPass Free Trial 2026"),
        (f"/pages/1password-review-{YEAR}-is-it-worth-it-honest-verdict", "1Password Review 2026"),
        (f"/pages/best-nordpass-alternatives-in-{YEAR}-free-paid", "Best NordPass Alternatives"),
    ],
    f"bitwarden-vs-nordpass-which-is-better-in-{YEAR}.html": [
        (f"/pages/nordpass-review-{YEAR}-is-it-worth-it-honest-verdict", "NordPass Review 2026: Full Verdict"),
        (f"/pages/nordpass-pricing-{YEAR}-plans-costs-what-you-actually-pay", "NordPass Pricing 2026"),
        (f"/pages/nordpass-free-trial-{YEAR}-how-to-get-it-step-by-step", "NordPass Free Trial 2026"),
        (f"/pages/best-nordpass-alternatives-in-{YEAR}-free-paid", "Best NordPass Alternatives"),
    ],
    f"dashlane-vs-nordpass-which-is-better-in-{YEAR}.html": [
        (f"/pages/nordpass-review-{YEAR}-is-it-worth-it-honest-verdict", "NordPass Review 2026: Full Verdict"),
        (f"/pages/nordpass-pricing-{YEAR}-plans-costs-what-you-actually-pay", "NordPass Pricing 2026"),
        (f"/pages/best-nordpass-alternatives-in-{YEAR}-free-paid", "Best NordPass Alternatives"),
    ],
    f"keeper-vs-nordpass-which-is-better-in-{YEAR}.html": [
        (f"/pages/nordpass-review-{YEAR}-is-it-worth-it-honest-verdict", "NordPass Review 2026: Full Verdict"),
        (f"/pages/nordpass-pricing-{YEAR}-plans-costs-what-you-actually-pay", "NordPass Pricing 2026"),
        (f"/pages/best-nordpass-alternatives-in-{YEAR}-free-paid", "Best NordPass Alternatives"),
    ],
    f"lastpass-vs-nordpass-which-is-better-in-{YEAR}.html": [
        (f"/pages/nordpass-review-{YEAR}-is-it-worth-it-honest-verdict", "NordPass Review 2026: Full Verdict"),
        (f"/pages/nordpass-pricing-{YEAR}-plans-costs-what-you-actually-pay", "NordPass Pricing 2026"),
        (f"/pages/best-nordpass-alternatives-in-{YEAR}-free-paid", "Best NordPass Alternatives"),
    ],
    f"nordpass-vs-enpass-which-is-better-in-{YEAR}.html": [
        (f"/pages/nordpass-review-{YEAR}-is-it-worth-it-honest-verdict", "NordPass Review 2026: Full Verdict"),
        (f"/pages/nordpass-pricing-{YEAR}-plans-costs-what-you-actually-pay", "NordPass Pricing 2026"),
        (f"/pages/nordpass-free-trial-{YEAR}-how-to-get-it-step-by-step", "NordPass Free Trial 2026"),
        (f"/pages/best-nordpass-alternatives-in-{YEAR}-free-paid", "Best NordPass Alternatives"),
    ],
    f"nordpass-vs-password-boss-which-is-better-in-{YEAR}.html": [
        (f"/pages/nordpass-review-{YEAR}-is-it-worth-it-honest-verdict", "NordPass Review 2026: Full Verdict"),
        (f"/pages/nordpass-pricing-{YEAR}-plans-costs-what-you-actually-pay", "NordPass Pricing 2026"),
        (f"/pages/best-nordpass-alternatives-in-{YEAR}-free-paid", "Best NordPass Alternatives"),
    ],
    f"nordpass-vs-roboform-which-is-better-in-{YEAR}.html": [
        (f"/pages/nordpass-review-{YEAR}-is-it-worth-it-honest-verdict", "NordPass Review 2026: Full Verdict"),
        (f"/pages/nordpass-pricing-{YEAR}-plans-costs-what-you-actually-pay", "NordPass Pricing 2026"),
        (f"/pages/best-nordpass-alternatives-in-{YEAR}-free-paid", "Best NordPass Alternatives"),
    ],
    f"nordpass-vs-sticky-password-which-is-better-in-{YEAR}.html": [
        (f"/pages/nordpass-review-{YEAR}-is-it-worth-it-honest-verdict", "NordPass Review 2026: Full Verdict"),
        (f"/pages/nordpass-pricing-{YEAR}-plans-costs-what-you-actually-pay", "NordPass Pricing 2026"),
        (f"/pages/best-nordpass-alternatives-in-{YEAR}-free-paid", "Best NordPass Alternatives"),
    ],
}

# ── Apply patches ─────────────────────────────────────────────────────────────

updated, skipped, missing = [], [], []

for fname, links in PATCHES.items():
    p = PAGES / fname
    if not p.exists():
        missing.append(fname)
        print(f"  Missing: {fname}")
        continue

    html = p.read_text(encoding="utf-8")
    new_block = make_related_block(links)

    if RELATED_BLOCK_RE.search(html):
        new_html = RELATED_BLOCK_RE.sub(new_block, html, count=1)
        if new_html != html:
            p.write_text(new_html, encoding="utf-8")
            updated.append(fname)
            print(f"  Updated: {fname}")
        else:
            skipped.append(fname)
            print(f"  No change: {fname}")
    else:
        # Inject before </main>
        if "</main>" in html:
            new_html = html.replace("</main>", new_block + "\n</main>", 1)
            p.write_text(new_html, encoding="utf-8")
            updated.append(fname)
            print(f"  Injected: {fname}")
        else:
            skipped.append(fname)
            print(f"  Skipped (no </main>): {fname}")

print(f"\nDone. {len(updated)} updated, {len(skipped)} skipped, {len(missing)} missing.")
