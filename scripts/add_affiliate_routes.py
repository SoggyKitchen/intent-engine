"""
Add new affiliate program redirect routes to site/_redirects.
Uses Python to avoid PowerShell encoding issues.

These are PENDING routes — direct URLs now, CJ/Impact tracking links when approved.
Apply to programs at:
  - FreshBooks: CJ Affiliate (ID 101733230) — you're already approved as publisher
  - HubSpot: impact.com
  - ClickUp: clickup.com/affiliates
  - ExpressVPN: CJ Affiliate
  - CyberGhost: CJ Affiliate
  - ProtonVPN: proton.me/business/affiliate
  - QuickBooks: CJ Affiliate
  - Dashlane: CJ Affiliate
  - Monday.com: impact.com
  - Teachable, Kajabi: CJ Affiliate

Run: uv run python scripts/add_affiliate_routes.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REDIRECTS = ROOT / "site" / "_redirects"

NEW_ROUTES = """

# === PENDING AFFILIATE APPROVAL ===
# Apply at CJ (ID: 101733230) or Impact — swap direct URLs for tracked links when approved
# FreshBooks CJ: $200/sale, 91 pages currently earning $0 — FASTEST WIN (you're already on CJ)
/go/freshbooks-trial https://my.freshbooks.com/#/signup?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302
# HubSpot Impact: $250-1000/sale, 187 pages currently earning $0
/go/hubspot-crm https://www.hubspot.com/products/crm?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302
# ClickUp Direct: ~$30/sale, 115 pages
/go/clickup-trial https://clickup.com/signup?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302
# 1Password ShareASale: 168 pages
/go/1password-trial https://1password.com/sign-up/?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302
# ActiveCampaign CJ: $100/referral, 80 pages
/go/activecampaign-trial https://www.activecampaign.com/free-crm-tools/?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302
# QuickBooks CJ: ~$50/signup
/go/quickbooks https://quickbooks.intuit.com/?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302
/go/quickbooks-trial https://quickbooks.intuit.com/signup/?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302
# Xero CJ: ~$40/signup (adding trial variant alongside existing /go/xero)
/go/xero-trial https://www.xero.com/signup/?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302
# Monday.com Impact: ~$30/conversion
/go/monday https://monday.com/?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302
# Dashlane CJ: adding trial variant
/go/dashlane-trial https://www.dashlane.com/download?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302

# === NEW VPN PROGRAM ROUTES (apply at CJ Affiliate ID 101733230) ===
# ExpressVPN CJ: ~$13/signup — high VPN traffic
/go/expressvpn https://www.expressvpn.com/?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302
# CyberGhost CJ: ~$10/signup — streaming VPN queries
/go/cyberghost https://www.cyberghostvpn.com/?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302
# ProtonVPN: CJ LIVE — see Wave 24 block in _redirects (anrdoezrs.net CJ link, $119.51 EPC)
# Bitdefender CJ: security cluster
/go/bitdefender https://www.bitdefender.com/?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302
# Malwarebytes CJ: security cluster
/go/malwarebytes https://www.malwarebytes.com/?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302

# === HIGH-COMMISSION CREATOR TOOLS (CJ Affiliate) ===
# Teachable CJ: 30% commission, course creator niche
/go/teachable https://teachable.com/?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302
# Kajabi CJ: 30% commission, ~$100/sale
/go/kajabi https://kajabi.com/?utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302
"""

current = REDIRECTS.read_text(encoding="utf-8")

# Only add if not already present
if "/go/expressvpn " not in current:
    updated = current.rstrip() + NEW_ROUTES
    REDIRECTS.write_text(updated, encoding="utf-8")
    print(f"Added {len(NEW_ROUTES.strip().splitlines())} new routes to _redirects")
else:
    print("Routes already present — skipped")
