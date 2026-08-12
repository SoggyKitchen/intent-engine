"""
Fix CTR batch 3 — revenue-hunter 2026-08-12

Target pages from data/gsc_pages.csv (position 7-12, high impressions, 0% CTR):
- does-sentry-have-a-free-plan     528 impr, pos 7.5,  0.00%
- does-loom-have-a-free-plan       255 impr, pos 10.9, 0.00%
- aws-vs-supabase                  286 impr, pos 10.1, 0.00%

Strategy: at pos 7-10 with 0 clicks, Google AI Overview is answering the basic
question inline. Beat it by promising more than the snippet shows:
decision help, real usage data, when-to-upgrade context.
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
            rf'\g<1>{og_title}\2', html,
        )
    if meta_desc:
        html = re.sub(
            r'<meta name="description" content="[^"]*">',
            f'<meta name="description" content="{meta_desc}">',
            html,
        )
    html = re.sub(r'"dateModified":\s*"[^"]*"', f'"dateModified": "{TODAY}"', html)
    p.write_text(html, encoding="utf-8")
    print(f"  FIXED: {p.name}")
    return True


def main():
    print(f"CTR batch 3 fixes ({TODAY})...\n")

    # 1. Sentry free plan — 528 impr, pos 7.5, 0 CTR
    # Current: "Sentry Free Plan 2026: 5K Events/Month, 1 Seat, 7-Day Retention — Is It Enough?"
    # SGE shows the basic limits. Title needs to promise decision help beyond what SGE shows.
    _patch(
        PAGES / "does-sentry-have-a-free-plan-2026-full-breakdown.html",
        title="Sentry Free Plan 2026: 5K Events — Exactly When You'll Hit the Limit [Dev Guide]",
        og_title="Sentry Free Plan 2026: 5K Events/Month — When You'll Actually Run Out",
        meta_desc=(
            "Updated August 2026. Sentry's free plan: 5,000 error events/month, "
            "1 seat, 7-day retention. How fast real projects exhaust the quota — "
            "and the cheapest upgrade path when they do."
        ),
    )

    # 2. Loom free plan — 255 impr, pos 10.9, 0 CTR
    # Current: "Does Loom Have a Free Plan? (2026) — Yes, But Only 5 Videos & 5-Min Cap"
    # SGE answers the basic yes/no. Title needs the 'what catches you' hook.
    _patch(
        PAGES / "does-loom-have-a-free-plan-2026-full-breakdown.html",
        title="Loom Free Plan 2026: 5-Video Cap + 5-Min Limit — The Catch Every New User Hits",
        og_title="Loom Free Plan 2026: 5-Video Cap — What Trips Up Every New User",
        meta_desc=(
            "Updated August 2026. Loom's free plan: 5 videos max, 5-minute limit per "
            "video, 720p only. Which limit you'll hit first, and whether Business at "
            "$12.50/user is worth the jump."
        ),
    )

    # 3. AWS vs Supabase — 286 impr, pos 10.1, 0 CTR
    # Current title is already in TITLE_OVERRIDES in rebuild_vs_pages_v2.py.
    # Meta desc can be more decision-focused to beat SGE comparison tables.
    _patch(
        PAGES / "aws-vs-supabase-which-is-better-in-2026.html",
        meta_desc=(
            "AWS wins at scale (9.0/10), Supabase wins on speed (8.8/10). "
            "Real pricing: AWS free tier → $0.023/GB/mo, Supabase free → $25/mo Pro. "
            "The one decision rule that picks the right one for your stack. August 2026."
        ),
    )

    print("\nDone.")


if __name__ == "__main__":
    main()
