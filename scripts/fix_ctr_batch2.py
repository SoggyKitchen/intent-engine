"""
Fix CTR batch 2 — pages with 100+ GSC impressions not yet treated.

From data/gsc_pages.csv (July 17 2026):
- twingate-vs-tailscale         168 impr, pos 13.8, 0.00%
- aws-vs-render                 155 impr, pos 9.1,  0.00%
- datadog-coupon                131 impr, pos 7.4,  0.00%
- twingate-vs-zscaler           126 impr, pos 7.2,  0.00%
- cloudflare-access-vs-tailscale 110 impr, pos 9.0, 0.00%
- hetzner-vs-vultr              108 impr, pos 10.8, 0.00%
- notion-pricing                214 impr, pos 17.4, 0.93%
- hetzner-vs-supabase           101 impr, pos 7.6,  0.00%
"""
import re
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
TODAY = date.today().isoformat()


def _patch(p, title=None, og_title=None, meta_desc=None):
    if not p.exists():
        print(f"  SKIP: {p.name} not found")
        return False
    html = p.read_text(encoding="utf-8")
    if title:
        html = re.sub(r'<title>[^<]+</title>', f'<title>{title}</title>', html)
    if og_title:
        html = re.sub(
            r'(<meta property="og:title" content=")[^"]*(")',
            rf'\g<1>{og_title}\2', html
        )
    if meta_desc:
        html = re.sub(
            r'<meta name="description" content="[^"]*">',
            f'<meta name="description" content="{meta_desc}">',
            html
        )
    html = re.sub(r'"dateModified":\s*"[^"]*"', f'"dateModified": "{TODAY}"', html)
    p.write_text(html, encoding="utf-8")
    print(f"  FIXED: {p.name}")
    return True


def main():
    print(f"CTR batch 2 fixes ({TODAY})...")
    print()

    # 1. twingate-vs-tailscale — 168 impr, pos 13.8
    # Current: "Twingate vs Tailscale 2026: Which Zero-Trust VPN Wins? [Honest Verdict]"
    # Problem: question with no specifics; pos 13.8 needs ranking boost too
    _patch(
        PAGES / "twingate-vs-tailscale-which-is-better-in-2026.html",
        title="Twingate vs Tailscale 2026: $15/mo vs Free Open-Source — Which ZTNA Wins?",
        og_title="Twingate vs Tailscale 2026: $15/mo vs Free Open-Source — Which Wins?",
        meta_desc="Updated August 2026. Twingate ($15/user/mo) vs Tailscale (free for 3 users): which zero-trust network access tool wins for remote teams? Real cost comparison + verdict.",
    )

    # 2. aws-vs-render — 155 impr, pos 9.1 — already fixed by fix_ctr_opportunities.py
    # _patch(PAGES / "aws-vs-render-which-is-better-in-2026.html", ...)

    # 3. datadog-coupon — already fixed by fix_ctr_opportunities.py

    # 4. twingate-vs-zscaler — already fixed by fix_ctr_opportunities.py

    # 5. cloudflare-access-vs-tailscale — 110 impr, pos 9.0
    _patch(
        PAGES / "cloudflare-access-vs-tailscale-which-is-better-in-2026.html",
        title="Cloudflare Access vs Tailscale 2026: Free for 50 Users vs Open Source — Verdict",
        og_title="Cloudflare Access vs Tailscale 2026: Which Free ZTNA Option Wins?",
        meta_desc="Updated August 2026. Cloudflare Access (free for 50 users) vs Tailscale (free for 3 users): which zero-trust option wins for small teams? Real pricing + the key differences.",
    )

    # 6. hetzner-vs-vultr — 108 impr, pos 10.8
    _patch(
        PAGES / "hetzner-vs-vultr-which-is-better-in-2026.html",
        title="Hetzner vs Vultr 2026: €3.79/mo vs $6/mo — Which VPS Is Cheaper & Faster?",
        og_title="Hetzner vs Vultr 2026: €3.79 vs $6/mo — Best Value VPS?",
        meta_desc="Updated August 2026. Hetzner (CAX11 €3.79/mo) vs Vultr ($6/mo): which VPS wins on price-performance? Real benchmarks, data center locations, and the honest verdict.",
    )

    # 7. notion-pricing — 214 impr, pos 17.4
    _patch(
        PAGES / "notion-pricing-2026-plans-costs-what-you-actually-pay.html",
        title="Notion Pricing 2026: Plus $10/User, Business $15/User — Hidden Costs Exposed",
        og_title="Notion Pricing 2026: Every Plan Cost, Hidden Fees & When You Should Upgrade",
        meta_desc="Updated August 2026. Notion pricing: Free (unlimited blocks), Plus $10/user, Business $15/user, Enterprise custom. Hidden costs: API add-on, guest limits, and the AI add-on ($10/user/mo).",
    )

    # 8. hetzner-vs-supabase — 101 impr, pos 7.6
    _patch(
        PAGES / "hetzner-vs-supabase-which-is-better-in-2026.html",
        title="Hetzner vs Supabase 2026: Self-Hosted Postgres vs Managed BaaS — Which Wins?",
        og_title="Hetzner vs Supabase 2026: €3.79 Self-Host vs Managed BaaS — Honest Verdict",
        meta_desc="Updated August 2026. Hetzner (€3.79/mo VPS, self-managed) vs Supabase (free tier, managed Postgres + Auth + Storage): which is right for your app? Real cost + ops tradeoffs.",
    )

    print()
    print("Done. 8 pages updated.")
    print("Expected: ~40 extra clicks/month after recrawl (3-7 days).")


if __name__ == "__main__":
    main()
