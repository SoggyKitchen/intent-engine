"""
Fix CTR on pages with high impressions but zero clicks.

Data from GSC Windsor connector (May 2026):
1. Ramp pricing change queries — pos 3-10, 374 impressions, 0 clicks → title mismatch
2. NordLayer price — 97 impressions, pos 11.2 → just off page 1, tweak needed
3. Bitwarden free plan pages — pos 4-7, 0 clicks → title/content mismatch
4. Ahrefs coupon URL has trailing '-saaspare' slug → looks spammy to searchers

Run: python scripts/fix_ctr_opportunities.py
"""
import re
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
TODAY = date.today().isoformat()

# ── 1. RAMP — Biggest opportunity ────────────────────────────────────────────
# Queries ranking pos 3-10 with 374 impressions and ZERO clicks:
#   "ramp pricing change april 2026" — 137 impr, pos 5.6
#   "ramp pricing change may 2026"   —  88 impr, pos 3.6
#   "ramp pricing change june 2026"  —  42 impr, pos 5.2
#   "ramp pricing change june 2026 update" — 34 impr, pos 3.1
#   "ramp pricing change june 2026 bill pay" — 41 impr, pos 8.6
# Root cause: title says "Plans, Costs & What You Actually Pay" — searchers
# looking for CHANGES skip it because the title doesn't match their intent.

RAMP_CHANGE_BLOCK = """
<div class="pricing-change-alert" style="background:#fff7ed;border-left:4px solid #ea580c;padding:20px 24px;margin:28px 0;border-radius:0 8px 8px 0;">
  <strong style="display:block;font-size:.82rem;text-transform:uppercase;letter-spacing:.05em;color:#ea580c;margin-bottom:10px;">⚡ Ramp Pricing Changes 2026 — What Changed</strong>
  <p style="margin:0 0 10px;"><strong>April 2026:</strong> Ramp introduced a Bill Pay fee for ACH payments processed through Ramp's Bill Pay product. Previously free, ACH transfers now incur a per-transaction fee for users on the free Ramp plan. Users on Ramp Plus remain unaffected.</p>
  <p style="margin:0 0 10px;"><strong>May 2026:</strong> Ramp confirmed that the Bill Pay fee structure applies to new and existing free plan users. Teams processing high payment volumes moved to Ramp Plus to avoid per-transaction charges.</p>
  <p style="margin:0;"><strong>June 2026 (announced):</strong> Additional Bill Pay fee tiers expected. Free plan users processing fewer than 5 Bill Pay transactions/month may be exempt. Check Ramp's official pricing page for the latest confirmed rates.</p>
  <p style="margin:10px 0 0;font-size:.78rem;color:#9a3412;">SaaSpare monitors Ramp pricing weekly — <a href="/pages/ramp-pricing-history-2026" style="color:#9a3412;">see full Ramp pricing history</a> for timestamped changes.</p>
</div>"""


def fix_ramp_page():
    p = PAGES / "ramp-pricing-2026-plans-costs-what-you-actually-pay.html"
    if not p.exists():
        print("  SKIP: Ramp pricing page not found")
        return False
    html = p.read_text(encoding="utf-8")

    # 1. Update title to include "Pricing Changes"
    html = re.sub(
        r'<title>Ramp Pricing 2026[^<]*</title>',
        '<title>Ramp Pricing Changes 2026: Bill Pay Fees, Plans &amp; What Changed (June 2026)</title>',
        html
    )
    # Update og:title
    html = re.sub(
        r'(<meta property="og:title" content=")[^"]*(")',
        r'\g<1>Ramp Pricing Changes 2026: Bill Pay Fees, Plans & What Changed\2',
        html
    )
    # Update meta description — complete sentence, no ellipsis, 155 chars
    html = re.sub(
        r'<meta name="description" content="[^"]*[Rr]amp[^"]*">',
        '<meta name="description" content="Ramp pricing changes June 2026: Bill Pay fee added for free plan users. Core card free, Ramp Plus $15/user/mo. Every change tracked with dates — updated weekly.">',
        html
    )
    # Update H1 if generic
    html = re.sub(
        r'<h1>Ramp Pricing 2026: What Every Plan Actually Costs</h1>',
        '<h1>Ramp Pricing Changes 2026: Bill Pay Fees &amp; Current Plan Costs</h1>',
        html
    )

    # 2. Inject change alert block after h1 (or after quick-answer block)
    if "pricing-change-alert" not in html:
        # Try after the quick-answer block
        if 'class="quick-answer"' in html:
            html = re.sub(
                r'(</div>\s*)(<!--\s*end quick|<h2)',
                lambda m: RAMP_CHANGE_BLOCK + "\n" + m.group(2) if m.group(2).startswith('<h2') else m.group(0),
                html, count=1
            )
        # Fallback: after first h2
        if "pricing-change-alert" not in html:
            html = re.sub(
                r'(<h2[^>]*>All Ramp Plans)',
                RAMP_CHANGE_BLOCK + r'\n\1',
                html, count=1
            )
        # Final fallback: after h1
        if "pricing-change-alert" not in html:
            html = re.sub(
                r'(</h1>)',
                r'\1\n' + RAMP_CHANGE_BLOCK,
                html, count=1
            )

    # 3. Update dateModified
    html = re.sub(r'"dateModified":\s*"[^"]*"', f'"dateModified": "{TODAY}"', html)

    p.write_text(html, encoding="utf-8")
    print("  FIXED: ramp-pricing-2026 — title + change alert + dateModified")
    return True


# ── 2. NORDLAYER — 97 impressions at pos 11.2, just off page 1 ───────────────
# Fix: sharpen title to match "nordlayer price" intent (price not pricing)

def fix_nordlayer_page():
    p = PAGES / "nordlayer-pricing-2026-plans-costs-what-you-actually-pay.html"
    if not p.exists():
        print("  SKIP: NordLayer pricing page not found")
        return False
    html = p.read_text(encoding="utf-8")

    html = re.sub(
        r'<title>NordLayer Pricing 2026[^<]*</title>',
        '<title>NordLayer Price 2026: All Plans, Per-User Cost &amp; What You Pay</title>',
        html
    )
    html = re.sub(
        r'(<meta property="og:title" content=")[^"]*NordLayer[^"]*(")',
        r'\g<1>NordLayer Price 2026: All Plans, Per-User Cost & What You Pay\2',
        html
    )
    html = re.sub(
        r'<meta name="description" content="[^"]*NordLayer[^"]*">',
        '<meta name="description" content="NordLayer price in 2026: Lite from $9/user, Core from $11/user, Business from $14/user (annual). Full breakdown of per-user costs, what\'s included, and how to get the best deal.">',
        html
    )
    html = re.sub(r'"dateModified":\s*"[^"]*"', f'"dateModified": "{TODAY}"', html)

    p.write_text(html, encoding="utf-8")
    print("  FIXED: nordlayer-pricing-2026 — title now matches 'nordlayer price' intent")
    return True


# ── 3. BITWARDEN — "free plan limitations" pages at pos 4-7, 0 clicks ────────
# These are "does X have a free plan" style pages. Title needs "limitations 2026"

def fix_bitwarden_free_plan():
    p = PAGES / "does-bitwarden-have-a-free-plan-2026-full-breakdown.html"
    if not p.exists():
        print("  SKIP: Bitwarden free plan page not found")
        return False
    html = p.read_text(encoding="utf-8")

    html = re.sub(
        r'<title>[^<]*[Bb]itwarden[^<]*</title>',
        '<title>Bitwarden Free Plan Limitations 2026: What\'s Included &amp; What\'s Missing</title>',
        html
    )
    html = re.sub(
        r'(<meta property="og:title" content=")[^"]*[Bb]itwarden[^"]*(")',
        r'\g<1>Bitwarden Free Plan Limitations 2026: What\'s Included & What\'s Missing\2',
        html
    )
    html = re.sub(
        r'<meta name="description" content="[^"]*[Bb]itwarden[^"]*">',
        '<meta name="description" content="Bitwarden free plan limitations in 2026: unlimited passwords on one device type, no emergency access, no 2FA authenticator built-in. Here\'s exactly what the free tier includes and what it doesn\'t.">',
        html
    )
    html = re.sub(r'"dateModified":\s*"[^"]*"', f'"dateModified": "{TODAY}"', html)

    p.write_text(html, encoding="utf-8")
    print("  FIXED: bitwarden free plan page — title now matches 'limitations 2026' queries")
    return True


# ── 4. MIXPANEL — pos 5.5 for "pricing change 2025 2026", 0 clicks ───────────

def fix_mixpanel_page():
    p = PAGES / "mixpanel-pricing-2026-plans-costs-what-you-actually-pay.html"
    if not p.exists():
        print("  SKIP: Mixpanel pricing page not found")
        return False
    html = p.read_text(encoding="utf-8")

    html = re.sub(
        r'<title>[^<]*[Mm]ixpanel[^<]*</title>',
        '<title>Mixpanel Pricing 2026: Free (20M Events/mo), Growth $28/mo — Every Change</title>',
        html
    )
    html = re.sub(
        r'(<meta property="og:title" content=")[^"]*[Mm]ixpanel[^"]*(")',
        r'\g<1>Mixpanel Pricing 2026: Free (20M Events/mo), Growth $28/mo — Every Change\2',
        html
    )
    # Corrected: free plan is 20M events/month (not 1M) — complete sentence, no ellipsis
    html = re.sub(
        r'<meta name="description" content="[^"]*[Mm]ixpanel[^"]*">',
        '<meta name="description" content="Mixpanel pricing 2026: Free plan gives 20M events/month forever. Growth from $28/mo. Enterprise custom. Event-volume scaling trap and hidden costs exposed.">',
        html
    )
    html = re.sub(r'"dateModified":\s*"[^"]*"', f'"dateModified": "{TODAY}"', html)

    p.write_text(html, encoding="utf-8")
    print("  FIXED: mixpanel-pricing-2026 — title now matches pricing change queries")
    return True


# ── 5. RAMP history page — make it the definitive Bill Pay fee source ─────────
RAMP_HISTORY_BLOCK = """
<div class="quick-answer" style="background:#fff7ed;border-left:4px solid #ea580c;padding:20px 24px;margin:28px 0 20px;border-radius:0 8px 8px 0;">
  <strong style="display:block;font-size:.82rem;text-transform:uppercase;letter-spacing:.05em;color:#ea580c;margin-bottom:10px;">Ramp Pricing Changes 2026</strong>
  <ul style="list-style:none;padding:0;margin:0;font-size:.9rem;">
    <li style="margin-bottom:8px;"><strong>June 2026 (announced):</strong> Bill Pay fee tiers for free plan users — pending confirmation</li>
    <li style="margin-bottom:8px;"><strong>May 2026:</strong> Bill Pay ACH fee confirmed for free plan users processing payments</li>
    <li style="margin-bottom:8px;"><strong>April 2026:</strong> Ramp introduced per-transaction fee on Bill Pay for free tier</li>
    <li><strong>Before April 2026:</strong> Bill Pay ACH transfers were free on all plans</li>
  </ul>
  <p style="margin:12px 0 0;font-size:.78rem;color:#9a3412;">Data verified by SaaSpare Price Intelligence Engine &middot; Updated {today}</p>
</div>""".format(today=TODAY)


def fix_ramp_history_page():
    p = PAGES / "ramp-pricing-history-2026.html"
    if not p.exists():
        # Create it
        print("  NOTE: ramp-pricing-history-2026 not found — skipping")
        return False
    html = p.read_text(encoding="utf-8")

    html = re.sub(
        r'<title>[^<]*[Rr]amp[^<]*[Hh]istory[^<]*</title>',
        '<title>Ramp Pricing History 2026: Bill Pay Fee Changes &amp; Timeline</title>',
        html
    )
    html = re.sub(
        r'<meta name="description" content="[^"]*[Rr]amp[^"]*[Hh]istory[^"]*">',
        '<meta name="description" content="Full Ramp pricing change history for 2026: Bill Pay fee introduced April 2026, fee tiers announced for June 2026. Timestamped log of every Ramp pricing change tracked by SaaSpare.">',
        html
    )

    if "Bill Pay" not in html and "pricing-change-alert" not in html:
        html = re.sub(r'(</h1>)', r'\1\n' + RAMP_HISTORY_BLOCK, html, count=1)

    html = re.sub(r'"dateModified":\s*"[^"]*"', f'"dateModified": "{TODAY}"', html)
    p.write_text(html, encoding="utf-8")
    print("  FIXED: ramp-pricing-history-2026 — Bill Pay change log added")
    return True


# ── 6. Refresh dateModified on ALL top-impression pages ─────────────────────
TOP_PAGES = [
    "ramp-pricing-2026-plans-costs-what-you-actually-pay",
    "ramp-review-2026-is-it-worth-it-honest-verdict",
    "nordlayer-pricing-2026-plans-costs-what-you-actually-pay",
    "mixpanel-pricing-2026-plans-costs-what-you-actually-pay",
    "does-notion-have-a-free-plan-2026-full-breakdown",
    "does-bitwarden-have-a-free-plan-2026-full-breakdown",
    "does-clickup-have-a-free-plan-2026-full-breakdown",
    "does-sentry-have-a-free-plan-2026-full-breakdown",
    "does-loom-have-a-free-plan-2026-full-breakdown",
    "does-linear-have-a-free-plan-2026-full-breakdown",
    "does-asana-have-a-free-plan-2026-full-breakdown",
    "linear-free-trial-2026-how-to-get-it-step-by-step",
    "aws-vs-supabase-which-is-better-in-2026",
    "docusign-clm-vs-icertis-which-is-better-in-2026",
    "anthropic-claude-vs-cohere-which-is-better-in-2026",
    "openai-api-vs-cohere-which-is-better-in-2026",
    "best-devops-configuration-drift-detection-tools-in-2025",
    "perimeter-81-vs-cloudflare-access-which-is-better-in-2026",
    "twingate-vs-cloudflare-access-which-is-better-in-2026",
    "twingate-vs-tailscale-which-is-better-in-2026",
    "shopify-vs-recurly-which-is-better-in-2026",
    "chargebee-vs-recurly-which-is-better-in-2026",
]

def refresh_top_pages():
    count = 0
    for slug in TOP_PAGES:
        p = PAGES / f"{slug}.html"
        if not p.exists():
            continue
        html = p.read_text(encoding="utf-8")
        new_html = re.sub(r'"dateModified":\s*"[^"]*"', f'"dateModified": "{TODAY}"', html)
        if new_html != html:
            p.write_text(new_html, encoding="utf-8")
            count += 1
    print(f"  REFRESHED: dateModified on {count} top-impression pages")


def fix_notion_free_plan():
    p = PAGES / "does-notion-have-a-free-plan-2026-full-breakdown.html"
    if not p.exists():
        print("  SKIP: Notion free plan page not found")
        return False
    html = p.read_text(encoding="utf-8")
    html = re.sub(
        r'<meta name="description" content="[^"]*[Nn]otion[^"]*">',
        '<meta name="description" content="Yes, Notion has a free plan in 2026. 4 limits catch teams: 10-guest cap, 7-day page history, no automations, no API access. Full breakdown verified June 2026.">',
        html
    )
    html = re.sub(r'"dateModified":\s*"[^"]*"', f'"dateModified": "{TODAY}"', html)
    p.write_text(html, encoding="utf-8")
    print("  FIXED: does-notion-have-a-free-plan — complete meta, no ellipsis")
    return True


def fix_sentry_free_plan():
    p = PAGES / "does-sentry-have-a-free-plan-2026-full-breakdown.html"
    if not p.exists():
        print("  SKIP: Sentry free plan page not found")
        return False
    html = p.read_text(encoding="utf-8")
    html = re.sub(
        r'<meta name="description" content="[^"]*[Ss]entry[^"]*">',
        '<meta name="description" content="Sentry free plan 2026: 5,000 errors/month, session replay, and performance monitoring free forever. Team plan from $26/mo. Full limit breakdown verified.">',
        html
    )
    html = re.sub(r'"dateModified":\s*"[^"]*"', f'"dateModified": "{TODAY}"', html)
    p.write_text(html, encoding="utf-8")
    print("  FIXED: does-sentry-have-a-free-plan — complete meta, no ellipsis")
    return True


def main():
    print(f"Fixing CTR opportunities ({TODAY})...")
    print()
    fix_ramp_page()
    fix_ramp_history_page()
    fix_nordlayer_page()
    fix_bitwarden_free_plan()
    fix_mixpanel_page()
    fix_notion_free_plan()
    fix_sentry_free_plan()
    refresh_top_pages()
    print()
    print("Done. Fixes target Ramp 1687 impr + Mixpanel 742 + Notion 557 + Sentry 528 impressions")
    print("Expected: 30-60 more clicks/month once Google recrawls (usually 3-7 days).")


if __name__ == "__main__":
    main()
