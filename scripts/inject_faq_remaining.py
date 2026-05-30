"""
Inject FAQ schema into the remaining 29 pages missing it.
Focuses on alternatives, best-hub, and coupon pages with affiliate links.

Run: uv run python scripts/inject_faq_remaining.py
"""
from __future__ import annotations
import json, re, pathlib

ROOT  = pathlib.Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"

def has_faq(html: str) -> bool:
    return '"FAQPage"' in html

def inject_faq(html: str, pairs: list[tuple[str,str]]) -> str:
    if has_faq(html):
        return html
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]
    })
    block = f'<script type="application/ld+json">\n{schema}\n</script>'
    return html.replace("</head>", block + "\n</head>", 1)

# FAQ pairs keyed by filename pattern
# Format: (slug_pattern, [(question, answer), ...])
FAQ_INJECTIONS = [
    # Alternatives pages that are missing FAQ
    ("best-nordvpn-alternatives", [
        ("What is the best alternative to NordVPN?", "Surfshark is the best NordVPN alternative — unlimited device connections and lower price at $2.19/month vs NordVPN's $3.39/month. For the fastest speeds, ExpressVPN. For the most privacy-focused, ProtonVPN."),
        ("Is there a free alternative to NordVPN?", "ProtonVPN is the only trustworthy free VPN — unlimited bandwidth on 3 servers. Windscribe free plan gives 10GB/month. Both have limited features vs NordVPN paid."),
        ("Is Surfshark better than NordVPN?", "Surfshark is better for households (unlimited devices, lower price). NordVPN is better for individuals who want the largest server network and independent no-logs audit."),
    ]),
    ("best-surfshark-alternatives", [
        ("What is the best alternative to Surfshark?", "NordVPN is the best Surfshark alternative — larger server network (6,400 vs 3,200 servers), PwC-audited no-logs, and slightly faster speeds. Costs a bit more at $3.39/month vs Surfshark's $2.19/month."),
        ("Is there a cheaper VPN than Surfshark?", "CyberGhost is cheaper at $2.03/month on the 2-year plan. However, CyberGhost has a less transparent privacy policy than Surfshark."),
        ("Is NordVPN better than Surfshark?", "NordVPN is better for security and speed; Surfshark is better for households (unlimited devices) and value. Both are excellent — choose NordVPN for quality, Surfshark for budget and multi-device use."),
    ]),
    ("best-sucuri-alternatives", [
        ("What is the best alternative to Sucuri?", "Wordfence is the best free alternative for WordPress sites — powerful firewall and malware scanner at no cost. Cloudflare is the best free CDN/DDoS alternative. MalCare is the best paid alternative at $99/year."),
        ("Is Wordfence better than Sucuri?", "Wordfence is better for server-level WordPress protection at lower cost (free plan). Sucuri is better when you need edge-level WAF protection that blocks attacks before they reach your server, and professional malware removal."),
        ("Is there a free alternative to Sucuri?", "Wordfence has a powerful free plan for WordPress. Cloudflare's free plan offers CDN and basic DDoS protection. Neither includes professional malware removal like Sucuri."),
    ]),
    ("best-nordpass-alternatives", [
        ("What is the best alternative to NordPass?", "1Password is the best NordPass alternative — better family plan, Travel Mode, and Apple ecosystem integration. Bitwarden is the best free alternative with unlimited devices and open-source code."),
        ("Is Bitwarden better than NordPass?", "Bitwarden is better if you want free cross-device sync and open-source transparency. NordPass is better if you want XChaCha20 encryption (more modern than Bitwarden's AES-256) and Nord Security's ecosystem."),
        ("Is there a free NordPass alternative?", "Bitwarden is the best free password manager — unlimited passwords across unlimited devices at zero cost. NordPass free covers only 1 active device."),
    ]),
    ("best-elevenlabs-alternatives", [
        ("What is the best alternative to ElevenLabs?", "Murf AI is the best ElevenLabs alternative for team collaboration. Play.ht is the best API-focused alternative. For free options, Google Cloud TTS and Azure Neural TTS both offer generous free tiers."),
        ("Is Murf AI as good as ElevenLabs?", "Murf AI has better team collaboration features and a simpler UI. ElevenLabs produces more realistic voices and better voice cloning. For pure voice quality, ElevenLabs wins. For team workflow, Murf AI is easier."),
        ("What is the cheapest ElevenLabs alternative?", "ElevenLabs itself has the best free plan (10,000 characters/month). Among paid alternatives, Play.ht starts at $29/month. Google Cloud TTS charges per character with a generous free tier."),
    ]),
    # Best-hub pages missing FAQ
    ("best-email-marketing-software", [
        ("What is the best email marketing software?", "HubSpot is the best all-in-one email marketing platform. Brevo is the best free option (unlimited contacts). ActiveCampaign is best for automation depth. Klaviyo is best for eCommerce."),
        ("Which email marketing tool is cheapest?", "Brevo has the most generous free plan — 300 emails/day to unlimited contacts. MailerLite starts at $9/month for the cheapest paid plan with full features."),
        ("Can I do email marketing for free?", "Yes — Brevo, HubSpot, Mailchimp, and MailerLite all have free plans. Brevo allows unlimited contacts (limited daily sends). HubSpot free CRM includes 2,000 email sends/month."),
    ]),
    ("best-ecommerce-platform", [
        ("What is the best ecommerce platform in 2026?", "Shopify is the best for most businesses — fastest setup, best app ecosystem, highest-converting checkout. WooCommerce is best if you're already on WordPress. Cloudflare Pages is free for static/digital product stores."),
        ("What ecommerce platform has no transaction fees?", "WooCommerce has no platform transaction fees (only payment processor fees). BigCommerce has no additional transaction fees on any plan. Shopify charges 0.5-2% unless you use Shopify Payments."),
        ("Is Shopify worth it for a small business?", "Yes — Shopify Basic at $39/month includes unlimited products, professional checkout, SSL, and 24/7 support. The 3-day free trial lets you test before committing."),
    ]),
    ("best-accounting-software-for-small-business", [
        ("What is the best accounting software for small business?", "FreshBooks is best for service businesses and freelancers — superior invoicing and time tracking. QuickBooks is best for product businesses with inventory. Wave is completely free for basic accounting."),
        ("Is there free accounting software for small business?", "Wave Accounting is genuinely free with no time limits — invoicing, bank reconciliation, and basic reporting at zero cost. It charges only for payroll and payment processing."),
        ("QuickBooks vs FreshBooks: which is better for freelancers?", "FreshBooks is better for freelancers — superior invoicing with automatic payment reminders, time tracking, and client portal. QuickBooks is better for businesses with inventory or complex payroll."),
    ]),
    ("best-crm-software-2026", [
        ("What is the best CRM for small business?", "HubSpot CRM is the best free CRM — unlimited users, contacts, and deals at zero cost. Pipedrive is the best visual pipeline CRM for pure sales teams. Zoho CRM has the most features per dollar."),
        ("Is HubSpot CRM really free?", "Yes — HubSpot CRM is permanently free with unlimited users, contact management, deal pipeline, email tracking, and live chat. Paid plans add automation and advanced reporting."),
        ("What CRM is best for startups?", "HubSpot CRM for most startups — free to start, easy to use, scales well. Pipedrive for early B2B sales teams needing visual pipeline management. Salesforce for Series B+ companies with complex sales processes."),
    ]),
    ("best-project-management-software-2026", [
        ("What is the best project management software?", "ClickUp is the most feature-complete with the most generous free plan. Asana is best for structured workflow management. Notion is best for documentation-heavy teams. Jira is the standard for software development."),
        ("Which project management tool is free?", "ClickUp Free: unlimited tasks, unlimited users. Trello Free: unlimited cards, 10 boards. Notion Free: unlimited blocks. Asana Free: unlimited tasks, up to 15 users."),
        ("Is ClickUp better than Asana?", "ClickUp is more feature-rich and better value — more generous free plan, lower paid plan costs, and more customisation. Asana is simpler and better for teams that want structured workflow without a learning curve."),
    ]),
    ("best-web-hosting-2026", [
        ("What is the best web hosting in 2026?", "Contabo is best for budget VPS hosting (4 vCPU, 4GB RAM for $6.99/month). HostPapa is best for small business shared hosting. SiteGround is best for WordPress. Cloudflare Pages is free for static sites."),
        ("Which web host is cheapest?", "Contabo is the cheapest VPS at $6.99/month with the best specs. Cloudflare Pages is free for static sites. HostPapa shared hosting starts at $2.95/month on promotion."),
        ("What is the best web hosting for WordPress?", "SiteGround for performance and support (from $2.99/month). Kinsta for high-traffic WordPress sites (from $35/month). HostPapa for budget-conscious small businesses needing managed WordPress."),
    ]),
    ("best-cheap-vps-hosting", [
        ("What is the cheapest VPS hosting?", "Contabo is the cheapest VPS with the best specs — 4 vCPU + 4GB RAM + 100GB NVMe for $6.99/month. Hetzner is the cheapest EU VPS at €3.79/month."),
        ("Is cheap VPS hosting reliable?", "Contabo and Hetzner are both highly reliable despite low prices. They operate efficient large-scale data centres rather than cutting corners. Both have 99.9%+ uptime track records."),
        ("What can I run on a $7/month VPS?", "Multiple WordPress sites, Node.js or Python apps, game servers, VPN servers (WireGuard), development environments, monitoring tools, and small databases. A Contabo VPS-1 handles most small-medium workloads."),
    ]),
    ("best-password-manager-2026", [
        ("What is the best password manager in 2026?", "NordPass is the best for security (XChaCha20 encryption, zero-knowledge). 1Password is best for families and Apple users. Bitwarden is the best free option with unlimited device sync."),
        ("Is there a free password manager?", "Bitwarden is the best free password manager — unlimited passwords across unlimited devices, open-source code, and independently audited. NordPass free covers 1 active device. LastPass free limits you to 1 device type."),
        ("Why should I avoid LastPass?", "LastPass suffered a major breach in 2022 where encrypted user vaults were stolen. Switch to NordPass, Bitwarden, or 1Password immediately if you use LastPass."),
    ]),
    ("best-vpn-for-privacy-and-security", [
        ("What is the best VPN in 2026?", "NordVPN is the best all-round VPN — PwC-audited no-logs, 6,400+ servers, NordLynx (WireGuard) speeds, and 30-day money-back. Surfshark is best for households (unlimited devices, lowest price at $2.19/month)."),
        ("Which VPN is cheapest?", "Surfshark at $2.19/month (2-year plan) is the cheapest premium VPN. CyberGhost at $2.03/month is slightly cheaper. NordVPN is $3.39/month — more expensive but better server network and audited privacy policy."),
        ("Is there a trustworthy free VPN?", "ProtonVPN is the only genuinely trustworthy free VPN — Swiss-based, open-source, unlimited bandwidth on 3 servers. Most free VPNs sell your data. Avoid them."),
    ]),
    ("best-seo-tools-2026", [
        ("What is the best SEO tool in 2026?", "Semrush is the best all-in-one SEO platform — 25B+ keyword database, 43T+ backlink index, site audit, and competitor analysis. Ahrefs is the best for backlink research. Google Search Console is the essential free tool."),
        ("Is Semrush worth the money?", "Yes — for agencies and businesses spending $2,000+/month on SEO, Semrush's $139.95/month Pro plan pays for itself quickly. The competitor intelligence alone uncovers opportunities worth more than the subscription cost."),
        ("What free SEO tools should I use?", "Google Search Console (mandatory), Google Analytics 4 (traffic analysis), Google Keyword Planner (basic keyword data), Screaming Frog free (500 URL crawl), and Ubersuggest free plan (3 searches/day)."),
    ]),
    ("best-ai-voice-generator", [
        ("What is the best AI voice generator in 2026?", "ElevenLabs is the best AI voice generator — most realistic voices, professional voice cloning from 1-minute audio sample, 32 languages, and a free plan (10,000 characters/month, no card required)."),
        ("Is there a free AI voice generator?", "Yes — ElevenLabs free plan gives 10,000 characters/month (about 7-8 minutes of audio) with no credit card required. Murf AI free gives 10 minutes/month. Google Cloud TTS has a generous API free tier."),
        ("Can AI voice generators replace professional voice actors?", "For narration content, yes — ElevenLabs quality passes human perception tests in double-blind studies. For complex character acting, human voice actors still have an edge on nuanced emotional performance."),
    ]),
]

updated = 0
for pattern, faq_pairs in FAQ_INJECTIONS:
    # Find matching files
    for f in PAGES.glob("*.html"):
        if pattern in f.name:
            html = f.read_text(encoding="utf-8", errors="replace")
            new_html = inject_faq(html, faq_pairs)
            if new_html != html:
                f.write_text(new_html, encoding="utf-8")
                updated += 1
                print(f"  Injected FAQ: {f.name}")

print(f"\nTotal updated: {updated}")
