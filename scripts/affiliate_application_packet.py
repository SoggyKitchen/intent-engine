"""
Generate a pre-filled affiliate network application packet.

For each network / direct program, outputs:
  - All standard form fields pre-answered (copy-paste)
  - The right promotional methods to tick
  - The specific pages to list as traffic sources
  - The right tone/angle for each reviewer's priorities

Usage:
    uv run python scripts/affiliate_application_packet.py [--network NAME]
    uv run python scripts/affiliate_application_packet.py --list

Outputs to: data/affiliate-applications/[network]-packet.txt
"""
import argparse, json, pathlib, sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT  = ROOT / "data" / "affiliate-applications"
OUT.mkdir(parents=True, exist_ok=True)

# ── Site constants ────────────────────────────────────────────────────────────
SITE = {
    "name":         "SaaSpare",
    "url":          "https://saaspare.org",
    "owner":        "Smith Elly",
    "email":        "hello@saaspare.org",
    "country":      "Australia",
    "niche":        "B2B SaaS comparison and pricing",
    "pages":        "1,034",
    "verticals":    "16",
    "launch":       "April 2026",
    "gsc_impr":     "6,540 impressions (Apr 21 – May 7 2026)",
    "audience":     "Founders, operators, and procurement leads evaluating B2B software",
    "promo_methods": "Editorial reviews, comparison pages, pricing guides, free trial guides, alternatives roundups",
    "traffic_sources": "Google organic search (primary), Reddit brand mentions, direct/social",
    "social": {
        "twitter": "https://x.com/SaaSpare",
        "linkedin": "https://www.linkedin.com/company/saaspare/",
    },
    "unique_asset": (
        "Price Intelligence Engine: weekly pricing snapshots for 15+ SaaS tools with diff logs. "
        "Original timestamped data not available elsewhere."
    ),
}

# ── Per-network packet generators ─────────────────────────────────────────────
def packet_semrush() -> str:
    return f"""
═══════════════════════════════════════════════════════════
  SEMRUSH AFFILIATE APPLICATION PACKET — saaspare.org
  Generated: {date.today()}
═══════════════════════════════════════════════════════════

Apply at: https://www.semrush.com/affiliates/
Contact backup: affiliates@semrush.com

── FORM FIELDS ────────────────────────────────────────────

First name:         Smith
Last name:          Elly
Email:              hello@saaspare.org
Website URL:        https://saaspare.org
Website name:       SaaSpare
Country:            Australia

Website description (copy-paste):
  SaaSpare is an independent B2B SaaS comparison and pricing platform.
  We publish 1,034 buyer-intent pages across 16 verticals including CRM,
  SEO tools, project management, and security software. We run a Price
  Intelligence Engine that tracks weekly pricing changes for 15+ SaaS tools
  and publishes timestamped diff logs — original data not available on
  G2, Capterra, or GetApp.

How will you promote Semrush? (copy-paste):
  Via two channels:
  1. Our dedicated Semrush pages: /pages/semrush-pricing-2026-plans-costs-what-you-actually-pay,
     /pages/semrush-review-2026-is-it-worth-it-honest-verdict, and
     /pages/ahrefs-vs-semrush-which-is-better-in-2026 — these rank for
     commercial-intent queries from buyers actively comparing SEO tools.
  2. Our SaaS Pricing Changes page (/pages/saas-pricing-changes) which
     tracks Semrush pricing history and routes high-intent readers directly
     to Semrush's trial page.

Monthly visitors:   Ramping — launched April 2026. 6,500+ GSC impressions in first 17 days.
Traffic source:     Organic search (primary), editorial referrals
Audience:           B2B operators and marketers evaluating SEO tools

Promotional methods (tick these):
  ✅ Blog / content marketing
  ✅ SEO / organic search
  ✅ Product comparison / review sites
  ❌ Paid advertising
  ❌ Email marketing
  ❌ Social media only

── STRONGEST PAGES TO MENTION ─────────────────────────────
  https://saaspare.org/pages/semrush-review-2026-is-it-worth-it-honest-verdict
  https://saaspare.org/pages/ahrefs-vs-semrush-which-is-better-in-2026
  https://saaspare.org/pages/semrush-pricing-2026-plans-costs-what-you-actually-pay
  https://saaspare.org/pages/semrush-vs-moz-pro-which-is-better-in-2026

── WHY THIS SHOULD GET APPROVED ───────────────────────────
  Semrush's affiliate team specifically targets SEO/comparison sites. SaaSpare
  is exactly that. The pricing pages include real plan breakdowns that convert
  readers who are in the final evaluation stage. Commission: $200/sale + $10/trial.
"""

def packet_shopify() -> str:
    return f"""
═══════════════════════════════════════════════════════════
  SHOPIFY AFFILIATE APPLICATION PACKET — saaspare.org
  Generated: {date.today()}
═══════════════════════════════════════════════════════════

Apply at: https://www.shopify.com/affiliates
(Use the direct Shopify form — NOT via Impact, different review team)

── FORM FIELDS ────────────────────────────────────────────

Name:               Smith Elly
Email:              hello@saaspare.org
Website:            https://saaspare.org
Country:            Australia

What type of content do you create?
  Comparison and review content for B2B software buyers. Specifically:
  independent pricing analysis, head-to-head comparisons, and free trial
  guides for ecommerce platforms and SaaS tools.

How will you promote Shopify?
  Via our dedicated Shopify pages which rank for commercial-intent queries:
  - /pages/shopify-pricing-2026-plans-costs-what-you-actually-pay
  - /pages/7-best-shopify-alternatives-in-2026-free-paid
  - /pages/shopify-review-2026-is-it-worth-it-honest-verdict
  - /pages/shopify-vs-bigcommerce-which-is-better-in-2026
  These pages target buyers who are actively evaluating ecommerce platforms
  and are 1-2 clicks from starting a trial.

Audience:           Founders and operators evaluating ecommerce platforms,
                    especially those switching from WooCommerce or BigCommerce.

── STRONGEST PAGES TO MENTION ─────────────────────────────
  https://saaspare.org/pages/shopify-pricing-2026-plans-costs-what-you-actually-pay
  https://saaspare.org/pages/shopify-review-2026-is-it-worth-it-honest-verdict
  https://saaspare.org/pages/7-best-shopify-alternatives-in-2026-free-paid

── NOTE ───────────────────────────────────────────────────
  Shopify is one of the easiest affiliate programs to get into. $150/conversion
  is strong. Should be approved within 3-5 business days.
"""

def packet_pipedrive() -> str:
    return f"""
═══════════════════════════════════════════════════════════
  PIPEDRIVE AFFILIATE APPLICATION PACKET — saaspare.org
  Generated: {date.today()}
═══════════════════════════════════════════════════════════

Apply at: https://www.pipedrive.com/en/partners/affiliates
Contact: partnerships@pipedrive.com

── FORM FIELDS ────────────────────────────────────────────

Full name:          Smith Elly
Email:              hello@saaspare.org
Company / Site:     SaaSpare (saaspare.org)
Country:            Australia

Website description:
  Independent B2B SaaS comparison and pricing platform. We publish pricing
  histories, side-by-side comparisons, and buyer-intent content for CRM tools
  including a dedicated Pipedrive pricing history tracker
  (saaspare.org/pages/pipedrive-pricing-history-2026).

How you'll promote Pipedrive:
  1. Dedicated Pipedrive pricing history page with weekly snapshot data
  2. Inclusion in all CRM alternatives roundups as a recommended pick
  3. Multiple Salesforce/HubSpot comparison pages where Pipedrive is recommended
     as the "best value for sales teams" option

Estimated monthly visitors: Ramping. Launched April 2026.
Traffic type: Organic search — CRM comparison queries

── WHY THIS GETS APPROVED ─────────────────────────────────
  Pipedrive's direct program has no traffic minimum. 33% recurring for 12 months
  is the best CRM commission rate available. Easy win.
"""

def packet_hubspot() -> str:
    return f"""
═══════════════════════════════════════════════════════════
  HUBSPOT AFFILIATE APPLICATION PACKET — saaspare.org
  Generated: {date.today()}
═══════════════════════════════════════════════════════════

Apply at: https://www.hubspot.com/partners/affiliates
(NOT the Solutions Partner Program — that's for agencies)

── FORM FIELDS ────────────────────────────────────────────

Name:               Smith Elly
Email:              hello@saaspare.org
Website:            https://saaspare.org
Company size:       Solo founder
Country:            Australia

Website type: Review / comparison / pricing intelligence

How will you promote HubSpot?
  SaaSpare tracks HubSpot's pricing weekly via our Price Intelligence Engine.
  We publish /pages/hubspot-pricing-history-2026 — a timestamped log of every
  HubSpot pricing change we've detected, with source URLs to HubSpot's official
  pricing pages. This page ranks for "HubSpot pricing history" and "HubSpot
  price increase" queries from buyers in the final evaluation stage.

  We also publish:
  - /pages/hubspot-pricing-2026-plans-costs-what-you-actually-pay
  - /pages/7-best-hubspot-alternatives-in-2026-free-paid
  - /pages/hubspot-review-2026-is-it-worth-it-honest-verdict
  - Multiple CRM comparison pages featuring HubSpot

Target audience:    SMB founders and sales leaders evaluating CRM tools.

── KEY DIFFERENTIATOR TO MENTION ──────────────────────────
  The pricing history page is what makes this application stand out. No other
  comparison site has timestamped pricing diff data. HubSpot's affiliate team
  will recognise this is a bottom-of-funnel page with high purchase intent.
"""

def packet_tresorit() -> str:
    return f"""
═══════════════════════════════════════════════════════════
  TRESORIT AFFILIATE APPLICATION PACKET — saaspare.org
  Generated: {date.today()}
═══════════════════════════════════════════════════════════

Apply at: https://tresorit.com/affiliate-program
Contact: affiliates@tresorit.com

── FORM FIELDS ────────────────────────────────────────────

Name:               Smith Elly
Email:              hello@saaspare.org
Website:            https://saaspare.org
Country:            Australia

Description:
  SaaSpare is a B2B software comparison platform focused on security and
  privacy tools among other verticals. We publish a dedicated Tresorit
  pricing history tracker and comparison pages against 1Password and other
  enterprise security tools.

Promotional approach:
  Editorial — Tresorit is featured in our security vertical comparisons
  as the top pick for teams with strict data compliance requirements.
  Our pricing history page gives buyers confidence that Tresorit's pricing
  is stable (an important factor for compliance-sensitive procurement).
"""

def packet_shareasale() -> str:
    return f"""
═══════════════════════════════════════════════════════════
  SHAREASALE APPLICATION PACKET — saaspare.org
  Generated: {date.today()}
═══════════════════════════════════════════════════════════

Apply at: https://account.shareasale.com/shareasale.cfm
This is one of the lowest-barrier networks. Should be approved quickly.

── FORM FIELDS ────────────────────────────────────────────

Website URL:        https://saaspare.org
Website name:       SaaSpare
Primary category:   Computers & Technology / Software
Promotion method:   Content / Comparison site

Website description (250 chars):
  Independent B2B SaaS comparison and pricing platform. 1,034 buyer pages
  across 16 verticals. Weekly pricing intelligence, head-to-head comparisons,
  free trial guides, and honest reviews. No paid placements.

Traffic description:
  Organic search (primary). Audience: founders and operators evaluating
  B2B software. Launched April 2026, growing rapidly.

Primary country:    Australia (global audience)

── KEY MERCHANTS TO JOIN AFTER APPROVAL ───────────────────
  Once approved at ShareASale, search for and join these merchants:
  - WP Engine (web hosting)
  - Freshbooks (accounting)
  - Fiverr Business
  - Any backup/security software merchants

── NOTE ───────────────────────────────────────────────────
  ShareASale is straightforward. Apply with the description above.
  You'll likely be approved within 1-3 business days.
"""

def packet_commission_factory() -> str:
    return f"""
═══════════════════════════════════════════════════════════
  COMMISSION FACTORY APPLICATION PACKET — saaspare.org
  Generated: {date.today()}
═══════════════════════════════════════════════════════════

Apply at: https://www.commissionfactory.com/affiliates/register
Australian network — strong advantage as an AU-based publisher.

── FORM FIELDS ────────────────────────────────────────────

Name:               Smith Elly
Email:              hello@saaspare.org
Website:            https://saaspare.org
ABN (if asked):     (your ABN — required for AU publishers)
Country:            Australia

Website category:   Technology / Software / B2B
Website description:
  Australian-run B2B SaaS comparison platform. 1,034 pages covering software
  pricing, comparisons, free trials, and reviews across 16 verticals.
  Independent editorial — no paid placements. Target audience: Australian
  and global SMBs evaluating business software.

── NOTE ───────────────────────────────────────────────────
  Commission Factory has lower traffic minimums than Awin/Impact and actively
  recruits Australian publishers. Being AU-based is a strong advantage here.
  After approval, look for: hosting providers, cloud storage, any SaaS tools
  with APAC programs.
"""


PACKETS = {
    "semrush":             packet_semrush,
    "shopify":             packet_shopify,
    "pipedrive":           packet_pipedrive,
    "hubspot":             packet_hubspot,
    "tresorit":            packet_tresorit,
    "shareasale":          packet_shareasale,
    "commission-factory":  packet_commission_factory,
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate affiliate application packets")
    ap.add_argument("--network", help="Specific network (or 'all')", default="all")
    ap.add_argument("--list", action="store_true", help="List available networks")
    args = ap.parse_args()

    if args.list:
        print("Available networks:")
        for k in PACKETS:
            print(f"  {k}")
        return 0

    targets = list(PACKETS.keys()) if args.network == "all" else [args.network]

    for name in targets:
        if name not in PACKETS:
            print(f"Unknown network: {name}. Use --list to see options.")
            continue
        content = PACKETS[name]()
        out_path = OUT / f"{name}-packet.txt"
        out_path.write_text(content, encoding="utf-8")
        print(f"  Written: {out_path}")

    print(f"\nAll packets in: {OUT}")
    print("Each packet has copy-paste answers for every form field.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
