"""
Fix CTR titles using slug-derived keywords (accurate, no mismatches).
Runs after analyze_gsc_and_fix_ctr.py to correct any wrong keyword matches.
Also handles the big opportunities identified in the GSC report.
"""
import re, json
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
YR = str(date.today().year)

# ── Slug parser: derive tool names and page type from slug ────────────────────
def slug_to_keyword_and_type(slug):
    s = slug
    # Strip common suffixes
    for suffix in [f"-which-is-better-in-{YR}", f"-which-is-better-in-2025",
                   f"-{YR}", "-2025", "-full-breakdown", "-step-by-step",
                   "-honest-verdict", "-is-it-worth-it",
                   "-plans-costs-what-you-actually-pay",
                   "-verified-discounts"]:
        s = s.replace(suffix, "")

    # VS page
    if "-vs-" in s:
        parts = s.split("-vs-", 1)
        a = parts[0].replace("-", " ").title()
        b = parts[1].replace("-", " ").title()
        return f"{a} vs {b}", "vs"

    # Free plan page
    if s.startswith("does-") and ("-free-plan" in s or "-free-trial" in s):
        tool = s.replace("does-", "").replace("-have-a-free-plan", "").replace("-have-a-free-trial", "")
        tool = tool.replace("-", " ").title()
        return f"{tool} free plan", "free_plan"

    # Free trial page
    if "-free-trial" in s:
        tool = s.replace("-free-trial", "").replace("-", " ").title()
        return f"{tool} free trial", "free_trial"

    # Pricing page
    if "-pricing" in s:
        tool = s.replace("-pricing", "").replace("-", " ").title()
        return f"{tool} pricing", "pricing"

    # Review page
    if "-review" in s:
        tool = s.replace("-review", "").replace("-", " ").title()
        return f"{tool} review", "review"

    # Coupon/promo page
    if "-coupon-code" in s or "-promo-code" in s:
        tool = re.sub(r"-(coupon|promo).*", "", s).replace("-", " ").title()
        return f"{tool} coupon code", "coupon"

    # Best X page
    if s.startswith("best-"):
        kw = s.replace("-", " ")
        return kw, "best"

    # Alternative page
    if "-alternative" in s:
        tool = s.split("-alternative")[0].replace("-", " ").title()
        return f"{tool} alternatives", "alternative"

    # Generic
    return s.replace("-", " "), "generic"


def make_title(slug, kw, page_type, old_title):
    t = old_title.strip().rstrip(".")

    if page_type == "vs":
        parts = kw.split(" vs ")
        if len(parts) == 2:
            a, b = parts[0].strip(), parts[1].strip()
            return f"{a} vs {b} ({YR}): Honest Head-to-Head Verdict"

    if page_type in ("free_plan", "free_trial"):
        tool = kw.replace(" free plan", "").replace(" free trial", "").strip().title()
        return f"Does {tool} Have a Free Plan in {YR}? Full Breakdown"

    if page_type == "pricing":
        tool = kw.replace(" pricing", "").strip().title()
        return f"{tool} Pricing ({YR}): All Plans, Hidden Fees & What You Actually Pay"

    if page_type == "review":
        tool = kw.replace(" review", "").strip().title()
        return f"{tool} Review ({YR}): Is It Worth It? Honest Verdict"

    if page_type == "coupon":
        tool = kw.replace(" coupon code", "").replace(" promo code", "").strip().title()
        return f"{tool} Coupon Codes ({YR}): Verified Discounts That Actually Work"

    if page_type == "best":
        topic = kw.replace("best ", "").replace(f" {YR}", "").strip()
        if YR not in t:
            return f"Best {topic.title()} ({YR}) — Ranked & Reviewed by Experts"
        return t + " [Expert Picks]" if "[" not in t else t

    if page_type == "alternative":
        tool = kw.replace(" alternatives", "").strip().title()
        return f"Best {tool} Alternatives ({YR}) — Cheaper Options Ranked"

    # Generic: just ensure year + hook
    if YR not in t:
        return f"{t} ({YR})"
    return t


def make_meta(kw, page_type):
    yr = YR

    if page_type == "vs":
        parts = kw.split(" vs ")
        if len(parts) == 2:
            a, b = parts[0].strip().title(), parts[1].strip().title()
            return (f"We compared {a} vs {b} in {yr} — pricing, features, integrations, "
                    f"and a clear winner. Updated monthly with real pricing data.")

    if page_type in ("free_plan", "free_trial"):
        tool = kw.replace(" free plan","").replace(" free trial","").strip().title()
        return (f"Yes, {tool} has a free plan in {yr}. Here's exactly what's included, "
                f"what's locked behind paid tiers, and whether it's enough for your team.")

    if page_type == "pricing":
        tool = kw.replace(" pricing","").strip().title()
        return (f"{tool} pricing in {yr}: every plan explained clearly, "
                f"hidden fees exposed, and whether it's worth it vs cheaper alternatives.")

    if page_type == "review":
        tool = kw.replace(" review","").strip().title()
        return (f"Honest {tool} review for {yr}. Real pros, cons, pricing, and "
                f"who it's built for — tested by SaaS experts, no fluff.")

    if page_type == "coupon":
        tool = kw.replace(" coupon code","").replace(" promo code","").strip().title()
        return (f"Working {tool} coupon codes for {yr}. "
                f"Verified discounts, free trial links, and the cheapest way to get started.")

    if page_type == "best":
        return (f"The best tools ranked for {yr}. "
                f"We compared pricing, features & support — here's what's actually worth paying for.")

    if page_type == "alternative":
        tool = kw.replace(" alternatives","").strip().title()
        return (f"The best {tool} alternatives in {yr} — ranked by price, features & ease of use. "
                f"Find a cheaper or better option for your team.")

    return (f"Updated {yr} guide from SaaSpare — expert analysis, "
            f"real pricing data, and a clear recommendation.")


def rewrite_page(path, new_title, new_meta):
    html = path.read_text(encoding="utf-8", errors="replace")
    orig = html

    m = re.search(r"<title>([^<]*)</title>", html)
    if m:
        html = html[:m.start()] + f"<title>{new_title}</title>" + html[m.end():]

    m2 = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']*["\'][^>]*/?>',
                   html, re.IGNORECASE)
    if m2:
        html = html[:m2.start()] + f'<meta name="description" content="{new_meta}">' + html[m2.end():]
    else:
        html = html.replace("</title>",
            f'</title>\n  <meta name="description" content="{new_meta}">', 1)

    if html != orig:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def main():
    # Load GSC opportunities to know which pages to target
    opp_path = DATA / "gsc_opportunities.json"
    if not opp_path.exists():
        print("Run analyze_gsc_and_fix_ctr.py first")
        return

    opps = json.loads(opp_path.read_text(encoding="utf-8"))
    all_pages = (opps.get("page1_opportunities", []) +
                 opps.get("page2_quickwins", []))

    print(f"CTR Title Fixer — {len(all_pages)} opportunity pages\n")

    updated = []

    for p in all_pages:
        url = p.get("url", "")
        slug = url.rstrip("/").split("/")[-1]
        if not slug or slug in ("pages", "saaspare.org"):
            continue

        # Find file
        candidates = [
            SITE / "pages" / f"{slug}.html",
            SITE / f"{slug}.html",
            SITE / "blog" / f"{slug}.html",
        ]
        path = next((c for c in candidates if c.exists()), None)
        if not path:
            continue

        kw, page_type = slug_to_keyword_and_type(slug)

        html = path.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"<title>([^<]*)</title>", html)
        old_title = m.group(1) if m else slug.replace("-", " ").title()

        new_title = make_title(slug, kw, page_type, old_title)
        new_meta  = make_meta(kw, page_type)

        changed = rewrite_page(path, new_title, new_meta)
        if changed:
            updated.append({"slug": slug, "type": page_type,
                            "pos": p.get("pos"), "impr": p.get("impr"),
                            "new_title": new_title})
            print(f"[{page_type.upper()}] {slug}")
            print(f"  pos={p.get('pos'):.1f} | {p.get('impr')} impr | {p.get('ctr',0)*100:.1f}% CTR")
            print(f"  -> {new_title}")
            print()

    # Save report
    report_path = DATA / "ctr_fix_report.json"
    report_path.write_text(json.dumps({"date": str(date.today()),
                                        "updated": len(updated),
                                        "fixes": updated}, indent=2), encoding="utf-8")

    print(f"Done: {len(updated)} pages updated")
    print(f"Report: data/ctr_fix_report.json")


if __name__ == "__main__":
    main()
