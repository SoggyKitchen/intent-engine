"""
Fix CTR on free-plan pages — revenue-hunter 2026-08-14

Problem: 11 pages use the pattern "Does X Have a Free Plan? Yes — [facts]"
Google AI Overview answers the basic yes/no inline, so users never click.

Fix: Remove "Yes —" confirmation framing. Lead with the tool name + the
*specific catch* that users can only learn by clicking through.

Pages targeted (ordered by impression volume):
- does-notion-have-a-free-plan       557 impr, pos 9.4, 0 CTR
- does-linear-have-a-free-plan       247 impr, pos 9.0, 0.8% CTR
- does-clickup-have-a-free-plan      GSC impressions, CTR low
- does-asana-have-a-free-plan        GSC impressions, CTR low
- does-protonmail-have-a-free-plan   GSC impressions, CTR low
- does-snyk-have-a-free-plan         GSC impressions, CTR low
- does-engagebay-have-a-free-plan    GSC impressions, CTR low
- does-getresponse-have-a-free-plan  GSC impressions, CTR low
- does-bitwarden-have-a-free-plan    GSC impressions, CTR low
- does-elevenlabs-have-a-free-plan   GSC impressions, CTR low
- does-elementor-have-a-free-plan    GSC impressions, CTR low
- does-protonvpn-have-a-free-plan    GSC impressions, CTR low
"""
import re
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
TODAY = date.today().isoformat()

FIXES = [
    (
        "does-notion-have-a-free-plan-2026-full-breakdown.html",
        "Notion Free Plan 2026: What the 10-Guest Cap Actually Blocks [August Update]",
        "Notion Free Plan 2026: 10-Guest Cap — What It Actually Blocks",
        "Updated August 2026. Notion's free plan: unlimited blocks and pages, but capped at 10 guests "
        "and 7-day version history. What that breaks in practice — and the cheapest upgrade that fixes it.",
    ),
    (
        "does-linear-have-a-free-plan-2026-full-breakdown.html",
        "Linear Free Plan 2026: 3-Seat Cap [When It Breaks & Cheapest Upgrade Path]",
        "Linear Free Plan 2026: 3-Seat Cap — When It Breaks for Teams",
        "Updated August 2026. Linear's free plan: unlimited issues, 3 members max, 250 issues/project. "
        "How fast the 3-seat cap hits real engineering teams, and what Linear Plus ($8/user) adds.",
    ),
    (
        "does-clickup-have-a-free-plan-2026-full-breakdown.html",
        "ClickUp Free Plan 2026: Unlimited Tasks but 4 Limits [Which One Blocks Teams First]",
        "ClickUp Free Plan 2026: 4 Limits That Block Real Teams",
        "Updated August 2026. ClickUp Free: unlimited tasks, 100MB storage, limited dashboards, no "
        "time-tracking reports. Which of the 4 limits teams hit first — and whether Unlimited at $7/user "
        "is worth the jump.",
    ),
    (
        "does-asana-have-a-free-plan-2026-full-breakdown.html",
        "Asana Free Plan 2026: 15 Users Free — 4 Limits That Block Real Workflows [August]",
        "Asana Free Plan 2026: 15 Users Free — 4 Limits That Block Workflows",
        "Updated August 2026. Asana's free plan: 15 members, basic tasks and projects. The 4 limits "
        "(no Timeline, no Rules, no Reporting, no Portfolios) that block real team workflows — and "
        "whether Starter at $10.99/user fixes them.",
    ),
    (
        "does-protonmail-have-a-free-plan-2026-full-breakdown.html",
        "ProtonMail Free Plan 2026: 1GB & 150 Msg/Day [What You Get + When to Upgrade]",
        "ProtonMail Free Plan 2026: 1GB Storage & 150 Msg/Day — Exact Limits",
        "Updated August 2026. ProtonMail's free plan: 1 address, 1GB storage, 150 messages/day. "
        "Which real-world use cases fit and which require Mail Plus ($3.99/month).",
    ),
    (
        "does-snyk-have-a-free-plan-2026-full-breakdown.html",
        "Snyk Free Plan 2026: 200 Tests/Month [What Counts as a Test & Pro Threshold]",
        "Snyk Free Plan 2026: 200 Tests/Month — What Counts as a Test",
        "Updated August 2026. Snyk's free plan: 200 open-source tests/month, 1 contributor. "
        "What counts as one test, how fast CI pipelines exhaust the quota, and what Team adds.",
    ),
    (
        "does-engagebay-have-a-free-plan-2026-full-breakdown.html",
        "EngageBay Free Plan 2026: 250-Contact Cap [How Fast It Breaks & What to Do Next]",
        "EngageBay Free Plan 2026: 250-Contact Cap — How Fast It Fills",
        "Updated August 2026. EngageBay's free plan: 250 contacts, 1,000 branded emails/month, "
        "basic CRM. How fast the 250-contact cap fills for a growing list — and whether Basic at "
        "$11.99/month is worth it.",
    ),
    (
        "does-getresponse-have-a-free-plan-2026-full-breakdown.html",
        "GetResponse Free Plan 2026: 4 Limits That Trip Up Growing Email Lists [August 2026]",
        "GetResponse Free Plan 2026: 4 Limits That Trip Up Growing Lists",
        "Updated August 2026. GetResponse Free: 2,500 newsletters/month, 500-contact cap, no "
        "automations, no webinars. Which limit growing lists hit first and what Email Marketing "
        "at $19/month unlocks.",
    ),
    (
        "does-bitwarden-have-a-free-plan-2026-full-breakdown.html",
        "Bitwarden Free Plan 2026: Unlimited Passwords Free [What's Actually Missing vs Premium]",
        "Bitwarden Free Plan 2026: Unlimited Passwords — What's Missing",
        "Updated August 2026. Bitwarden's free plan: unlimited passwords, zero devices limit, "
        "end-to-end encryption. The 3 features only Premium ($10/year) unlocks — and whether "
        "any of them matter for most users.",
    ),
    (
        "does-elevenlabs-have-a-free-plan-2026-full-breakdown.html",
        "ElevenLabs Free Plan 2026: No Commercial Use, API Locked [Which Tier Unlocks What]",
        "ElevenLabs Free Plan 2026: No Commercial Use — Which Tier Unlocks It",
        "Updated August 2026. ElevenLabs free: 10,000 characters/month, no commercial rights, "
        "no API access. Which paid tier (Starter $5, Creator $22, Pro $99) unlocks each use case.",
    ),
    (
        "does-elementor-have-a-free-plan-2026-full-breakdown.html",
        "Elementor Free Plan 2026: 7 Pro Features You Don't Get [Real vs Essential Comparison]",
        "Elementor Free Plan 2026: 7 Pro Features Not Included",
        "Updated August 2026. Elementor's free plugin: 40+ basic widgets, full drag-and-drop. "
        "The 7 Pro features (Theme Builder, WooCommerce, Popups, A/B Testing, etc.) that require "
        "Essential at $59/year.",
    ),
    (
        "does-protonvpn-have-a-free-plan-2026-full-breakdown.html",
        "ProtonVPN Free Plan 2026: Unlimited Data, 5 Servers — The Actual Speed & Access Limits",
        "ProtonVPN Free Plan 2026: Unlimited Data — Actual Speed & Server Limits",
        "Updated August 2026. ProtonVPN free: unlimited bandwidth, 5 server locations, 1 device. "
        "Real-world speeds vs Plus ($4.99/month) — and the geo-unblocking limitations most users "
        "discover too late.",
    ),
]


def _patch(slug, title, og_title, meta_desc):
    p = PAGES / slug
    if not p.exists():
        print(f"  SKIP: {slug} not found")
        return False
    html = p.read_text(encoding="utf-8")
    changed = False

    new_html = re.sub(r'<title>[^<]+</title>', f'<title>{title}</title>', html)
    if new_html != html:
        changed = True
        html = new_html

    new_html = re.sub(
        r'(<meta property="og:title" content=")[^"]*(")',
        rf'\g<1>{og_title}\2', html,
    )
    if new_html != html:
        changed = True
        html = new_html

    new_html = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{meta_desc}">',
        html,
    )
    if new_html != html:
        changed = True
        html = new_html

    new_html = re.sub(r'"dateModified":\s*"[^"]*"', f'"dateModified": "{TODAY}"', html)
    if new_html != html:
        changed = True
        html = new_html

    if changed:
        p.write_text(html, encoding="utf-8")
        print(f"  FIXED: {slug}")
    else:
        print(f"  UNCHANGED: {slug}")
    return changed


def main():
    print(f"CTR free-plan fixes ({TODAY}) — removing 'Yes' confirmation framing...\n")
    fixed = 0
    for args in FIXES:
        if _patch(*args):
            fixed += 1
    print(f"\nDone. {fixed}/{len(FIXES)} pages updated.")


if __name__ == "__main__":
    main()
