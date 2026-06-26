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

# === MISSING-ROUTE BACKFILL (2026-06-25 audit) ===
# Pages link to these /go/ routes but they were never defined → every click 404s.
# No approved affiliate program for these yet, so they point to the vendor's real
# homepage with utm tags: a working link (no fake tracking). Swap for tracked
# network links the moment each program is approved.
BACKFILL_ROUTES = {
    "/go/bitwarden-pricing": "https://bitwarden.com/pricing/",
    "/go/canva": "https://www.canva.com/",
    "/go/coda": "https://coda.io/",
    "/go/coda-pricing": "https://coda.io/pricing",
    "/go/confluence": "https://www.atlassian.com/software/confluence",
    "/go/confluence-pricing": "https://www.atlassian.com/software/confluence/pricing",
    "/go/constant-contact-trial": "https://www.constantcontact.com/",
    "/go/dynatrace": "https://www.dynatrace.com/",
    "/go/dynatrace-pricing": "https://www.dynatrace.com/pricing/",
    "/go/fraseio": "https://www.frase.io/",
    "/go/getresponse-email": "https://www.getresponse.com/",
    "/go/github-issues-pricing": "https://github.com/pricing",
    "/go/google-meet": "https://workspace.google.com/products/meet/",
    "/go/google-meet-pricing": "https://workspace.google.com/pricing",
    "/go/grafana": "https://grafana.com/",
    "/go/grafana-pricing": "https://grafana.com/pricing/",
    "/go/hubspot-crm-pricing": "https://www.hubspot.com/pricing/crm",
    "/go/jira": "https://www.atlassian.com/software/jira",
    "/go/jira-pricing": "https://www.atlassian.com/software/jira/pricing",
    "/go/marketmuse": "https://www.marketmuse.com/",
    "/go/marketmuse-pricing": "https://www.marketmuse.com/pricing/",
    "/go/microsoft-teams": "https://www.microsoft.com/microsoft-teams/group-chat-software",
    "/go/microsoft-teams-pricing": "https://www.microsoft.com/microsoft-teams/compare-microsoft-teams-options",
    "/go/miro": "https://miro.com/",
    "/go/moz": "https://moz.com/",
    "/go/myob": "https://www.myob.com/",
    "/go/myob-pricing": "https://www.myob.com/au/pricing",
    "/go/netlify": "https://www.netlify.com/",
    "/go/netlify-pricing": "https://www.netlify.com/pricing/",
    "/go/new-relic": "https://newrelic.com/",
    "/go/new-relic-pricing": "https://newrelic.com/pricing",
    "/go/partnerstack": "https://partnerstack.com/",
    "/go/quickbooks-pricing": "https://quickbooks.intuit.com/pricing/",
    "/go/remotecom": "https://remote.com/",
    "/go/remotecom-pricing": "https://remote.com/pricing",
    "/go/slack": "https://slack.com/",
    "/go/stripe": "https://stripe.com/",
    "/go/upwork": "https://www.upwork.com/",
    "/go/vercel": "https://vercel.com/",
    "/go/wave": "https://www.waveapps.com/",
    "/go/wave-pricing": "https://www.waveapps.com/pricing",
    "/go/webex": "https://www.webex.com/",
    "/go/webex-pricing": "https://www.webex.com/pricing.html",
    "/go/wix": "https://www.wix.com/",
    "/go/wix-ecommerce-pricing": "https://www.wix.com/ecommerce/website",
    "/go/woocommerce": "https://woocommerce.com/",
    "/go/woocommerce-pricing": "https://woocommerce.com/pricing/",
    "/go/workday": "https://www.workday.com/",
    "/go/workday-pricing": "https://www.workday.com/en-us/pricing.html",
    "/go/zendesk": "https://www.zendesk.com/",
}

current = REDIRECTS.read_text(encoding="utf-8")

# Only add if not already present
if "/go/expressvpn " not in current:
    current = current.rstrip() + NEW_ROUTES
    print(f"Added {len(NEW_ROUTES.strip().splitlines())} new routes to _redirects")
else:
    print("Pending routes already present — skipped")

# Backfill missing routes (idempotent per-route check)
defined = {line.split()[0] for line in current.splitlines() if line.startswith("/go/")}
added = []
backfill_lines = ["\n\n# === MISSING-ROUTE BACKFILL (2026-06-25 audit — vendor homepages, swap when approved) ==="]
for route, url in sorted(BACKFILL_ROUTES.items()):
    if route not in defined:
        sep = "&" if "?" in url else "?"
        backfill_lines.append(f"{route} {url}{sep}utm_source=saaspare&utm_medium=affiliate&utm_campaign=go 302")
        added.append(route)
if added:
    current = current.rstrip() + "\n".join(backfill_lines) + "\n"
    print(f"Backfilled {len(added)} missing routes: {', '.join(added)}")
else:
    print("Backfill routes already present — skipped")

REDIRECTS.write_text(current, encoding="utf-8")
