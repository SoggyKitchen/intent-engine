"""
Analyze real GSC export data and apply CTR fixes.
Reads data/gsc_queries.csv + data/gsc_pages.csv
Outputs: data/gsc_opportunities.json + rewrites HTML titles/metas
"""
import csv, json, re
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
TODAY_YEAR = str(date.today().year)

# ── Load CSVs ─────────────────────────────────────────────────────────────────
def load_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def parse_pct(s):
    return float(str(s).replace("%","").strip()) / 100

def parse_float(s):
    try: return float(str(s).strip())
    except: return 0.0

def parse_int(s):
    try: return int(str(s).strip())
    except: return 0

# ── Title/meta rewrite logic ──────────────────────────────────────────────────
def upgrade_title(old_title, keyword, position):
    t = old_title.strip().rstrip(".")
    yr = TODAY_YEAR
    kw = keyword.lower()

    if " vs " in kw:
        parts = kw.split(" vs ")
        if len(parts) == 2:
            a, b = parts[0].strip().title(), parts[1].strip().title()
            return f"{a} vs {b} ({yr}): Honest Verdict — Which Is Actually Better?"

    if kw.startswith("best "):
        if yr not in t:
            return f"{t} ({yr}) — Ranked & Reviewed by Experts"
        if "[" not in t and "(" not in t:
            return f"{t} [Expert Picks]"
        return t

    if any(x in kw for x in ["pricing", "price", "cost", "plans"]):
        tool = re.sub(r"(pricing|price|cost|plans|2026|2025)","",kw).strip().title()
        return f"{tool} Pricing ({yr}): All Plans, Hidden Fees & What You Actually Pay"

    if "review" in kw:
        tool = kw.split("review")[0].strip().title()
        return f"{tool} Review ({yr}): Is It Worth It? Honest Verdict"

    if "free trial" in kw or "free plan" in kw:
        tool = re.sub(r"free (trial|plan)","",kw).strip().title()
        return f"{tool} Free Trial ({yr}): How to Get It & What's Included"

    if "alternative" in kw:
        return f"{t} ({yr}) — Cheaper Options Ranked [Updated]"

    if "coupon" in kw or "promo" in kw or "discount" in kw:
        tool = re.sub(r"(coupon|promo|discount|code)s?","",kw).strip().title()
        return f"{tool} Coupon Codes ({yr}): Verified Discounts That Actually Work"

    # Generic: add year + hook if missing
    if yr not in t:
        return f"{t} ({yr}) — Expert Analysis"
    return t

def upgrade_meta(keyword, position):
    yr = TODAY_YEAR
    kw = keyword.lower()

    if " vs " in kw:
        parts = kw.split(" vs ")
        if len(parts) == 2:
            a, b = parts[0].strip().title(), parts[1].strip().title()
            return (f"We compared {a} vs {b} in {yr} — pricing, features, integrations, "
                    f"and a clear winner. Updated monthly so you get accurate data, not guesswork.")

    if kw.startswith("best "):
        topic = kw.replace("best ","").replace(yr,"").strip()
        return (f"The best {topic} tools ranked for {yr}. We tested pricing, features & support "
                f"across 10+ options. Here's what's actually worth paying for.")

    if any(x in kw for x in ["pricing","price","cost","plans"]):
        tool = re.sub(r"(pricing|price|cost|plans|2026|2025)","",kw).strip().title()
        return (f"{tool} pricing in {yr}: every plan explained, hidden fees exposed, "
                f"and whether it's worth it vs cheaper alternatives.")

    if "review" in kw:
        tool = kw.split("review")[0].strip().title()
        return (f"Honest {tool} review for {yr}. Real pros, cons, pricing, and who it's built for. "
                f"Tested by SaaS experts — no affiliate spin, just straight answers.")

    if "free trial" in kw:
        tool = re.sub(r"free (trial|plan)","",kw).strip().title()
        return (f"Get a {tool} free trial in {yr}: step-by-step walkthrough, "
                f"what's included, how long it lasts, and how to avoid surprise charges.")

    if "alternative" in kw:
        tool = kw.split("alternative")[0].strip().title()
        return (f"The best {tool} alternatives in {yr} — ranked by price, features & ease of use. "
                f"Find a cheaper or better option for your team size.")

    return (f"Updated {yr} analysis from SaaSpare. Expert comparison, real pricing data, "
            f"and a clear recommendation — no fluff, just what you need to decide.")

# ── Find HTML file for a GSC page URL ────────────────────────────────────────
def url_to_path(url):
    url = url.rstrip("/")
    slug = url.split("/")[-1]
    if not slug or slug == "saaspare.org":
        return SITE / "index.html"
    candidates = [
        SITE / "pages" / f"{slug}.html",
        SITE / f"{slug}.html",
        SITE / "blog" / f"{slug}.html",
        SITE / "pages" / slug / "index.html",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

def rewrite_page(path, new_title, new_meta):
    html = path.read_text(encoding="utf-8", errors="replace")
    orig = html

    # Title
    m = re.search(r"<title>([^<]*)</title>", html)
    if m and m.group(1).strip() != new_title:
        html = html[:m.start()] + f"<title>{new_title}</title>" + html[m.end():]

    # Meta description
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

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    queries_path = DATA / "gsc_queries.csv"
    pages_path   = DATA / "gsc_pages.csv"

    if not queries_path.exists() or not pages_path.exists():
        print("Missing gsc_queries.csv or gsc_pages.csv in data/")
        return

    queries = load_csv(queries_path)
    pages   = load_csv(pages_path)

    print(f"Loaded {len(queries)} queries, {len(pages)} pages from GSC export\n")

    # ── ANALYSIS REPORT ──────────────────────────────────────────────────────

    # 1. Pages ranking 1-3 (already winning — just monitor)
    top3 = [p for p in pages if parse_float(p.get("Position","99")) <= 3]

    # 2. Pages ranking 4-10 (page 1 — optimise CTR)
    p4_10 = [p for p in pages
             if 3 < parse_float(p.get("Position","99")) <= 10
             and parse_int(p.get("Impressions","0")) >= 50]
    p4_10.sort(key=lambda x: parse_int(x.get("Impressions","0")), reverse=True)

    # 3. Pages ranking 11-20 (page 2 — quick wins, bump to page 1)
    p11_20 = [p for p in pages
              if 10 < parse_float(p.get("Position","99")) <= 20
              and parse_int(p.get("Impressions","0")) >= 30]
    p11_20.sort(key=lambda x: parse_int(x.get("Impressions","0")), reverse=True)

    # 4. High impression / zero click queries (title mismatch)
    zero_click = [q for q in queries
                  if parse_int(q.get("Clicks","0")) == 0
                  and parse_int(q.get("Impressions","0")) >= 100]
    zero_click.sort(key=lambda x: parse_int(x.get("Impressions","0")), reverse=True)

    # 5. Low CTR on page 1 (pos <= 10, CTR < 1%)
    low_ctr_p1 = [p for p in pages
                  if parse_float(p.get("Position","99")) <= 10
                  and parse_pct(p.get("CTR","0%")) < 0.01
                  and parse_int(p.get("Impressions","0")) >= 100]

    print("=" * 65)
    print("GSC OPPORTUNITY REPORT — saaspare.org")
    print("=" * 65)

    total_impressions = sum(parse_int(p.get("Impressions","0")) for p in pages)
    total_clicks = sum(parse_int(p.get("Clicks","0")) for p in pages)
    avg_pos = sum(parse_float(p.get("Position","0")) * parse_int(p.get("Impressions","0"))
                  for p in pages) / max(total_impressions, 1)

    print(f"\nOVERALL: {total_clicks} clicks / {total_impressions:,} impressions "
          f"/ {total_clicks/max(total_impressions,1)*100:.2f}% CTR / pos {avg_pos:.1f}")
    print(f"\nPages ranked 1-3:   {len(top3)}")
    print(f"Pages ranked 4-10:  {len(p4_10)}  (page 1 — CTR optimise these)")
    print(f"Pages ranked 11-20: {len(p11_20)}  (page 2 — push to page 1)")
    print(f"Zero-click queries: {len(zero_click)}  (100+ impressions, 0 clicks)")
    print(f"Low CTR page 1:     {len(low_ctr_p1)}  (pos<=10, CTR<1%)")

    print("\n--- TOP 20 PAGE 1 OPPORTUNITIES (pos 4-10, most impressions) ---")
    for p in p4_10[:20]:
        url = p.get("Top pages","")
        slug = url.rstrip("/").split("/")[-1]
        pos  = parse_float(p.get("Position","0"))
        ctr  = parse_pct(p.get("CTR","0%"))
        impr = parse_int(p.get("Impressions","0"))
        clk  = parse_int(p.get("Clicks","0"))
        print(f"  pos {pos:5.1f} | {impr:5} impr | {ctr*100:.1f}% CTR | {clk} clk | {slug}")

    print("\n--- TOP 20 PAGE 2 QUICK WINS (pos 11-20, most impressions) ---")
    for p in p11_20[:20]:
        url = p.get("Top pages","")
        slug = url.rstrip("/").split("/")[-1]
        pos  = parse_float(p.get("Position","0"))
        ctr  = parse_pct(p.get("CTR","0%"))
        impr = parse_int(p.get("Impressions","0"))
        print(f"  pos {pos:5.1f} | {impr:5} impr | {ctr*100:.1f}% CTR | {slug}")

    print("\n--- TOP 20 ZERO-CLICK QUERIES (100+ impressions, 0 clicks) ---")
    for q in zero_click[:20]:
        kw   = q.get("Top queries","")
        impr = parse_int(q.get("Impressions","0"))
        pos  = parse_float(q.get("Position","0"))
        print(f"  pos {pos:5.1f} | {impr:5} impr | '{kw}'")

    # ── APPLY CTR FIXES ───────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("APPLYING CTR FIXES")
    print("=" * 65)

    # Build page -> best query mapping
    page_query_map = {}
    for q in queries:
        kw  = q.get("Top queries","")
        pos = parse_float(q.get("Position","99"))
        impr = parse_int(q.get("Impressions","0"))
        # We don't have page-level query data in basic GSC export,
        # so match by slug keywords
        if impr < 20: continue
        # Normalise keyword to guess slug
        slug_guess = re.sub(r"[^a-z0-9]+","-", kw.lower()).strip("-")
        page_query_map[slug_guess] = {"keyword": kw, "position": pos, "impressions": impr}

    updated = []
    skipped_no_file = []

    # Fix low-CTR page 1 + all page 2 pages
    candidates = p4_10[:30] + p11_20[:30]
    seen_paths = set()

    for p in candidates:
        url  = p.get("Top pages","")
        pos  = parse_float(p.get("Position","99"))
        ctr  = parse_pct(p.get("CTR","0%"))
        impr = parse_int(p.get("Impressions","0"))
        clk  = parse_int(p.get("Clicks","0"))

        # Only fix if CTR is below threshold for position
        # pos 4-7: expect >2%, pos 8-10: >1%, pos 11-20: any
        if pos <= 7 and ctr >= 0.02: continue
        if 7 < pos <= 10 and ctr >= 0.01: continue

        html_path = url_to_path(url)
        if not html_path or str(html_path) in seen_paths:
            skipped_no_file.append(url.split("/")[-1])
            continue
        seen_paths.add(str(html_path))

        # Get best keyword for this page
        slug = url.rstrip("/").split("/")[-1]
        # Try direct slug match in query map
        best_kw = None
        best_impr = 0
        for q_slug, qdata in page_query_map.items():
            # fuzzy match: if slug contains keywords from query
            kw_words = set(qdata["keyword"].lower().split())
            slug_words = set(slug.replace("-"," ").split())
            overlap = len(kw_words & slug_words)
            if overlap >= 2 and qdata["impressions"] > best_impr:
                best_kw = qdata["keyword"]
                best_impr = qdata["impressions"]

        if not best_kw:
            # Fall back to slug-derived keyword
            best_kw = slug.replace("-"," ").replace(" which is better in 2026","").replace(" 2026","")

        # Read current title
        html = html_path.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"<title>([^<]*)</title>", html)
        old_title = m.group(1) if m else slug.replace("-"," ").title()

        new_title = upgrade_title(old_title, best_kw, pos)
        new_meta  = upgrade_meta(best_kw, pos)

        changed = rewrite_page(html_path, new_title, new_meta)
        if changed:
            updated.append({
                "slug": slug,
                "keyword": best_kw,
                "position": round(pos,1),
                "impressions": impr,
                "clicks": clk,
                "old_ctr_pct": f"{ctr*100:.1f}%",
                "new_title": new_title,
            })
            print(f"[FIX] {slug}")
            print(f"      kw='{best_kw}' pos={pos:.1f} impr={impr} ctr={ctr*100:.1f}%")
            print(f"      title -> {new_title}")
            print()

    # ── Save opportunities JSON ───────────────────────────────────────────────
    opportunities = {
        "generated": str(date.today()),
        "summary": {
            "total_pages": len(pages),
            "total_queries": len(queries),
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "overall_ctr_pct": round(total_clicks / max(total_impressions,1) * 100, 2),
            "pages_pos_1_3": len(top3),
            "pages_pos_4_10": len(p4_10),
            "pages_pos_11_20": len(p11_20),
            "zero_click_queries_100plus_impr": len(zero_click),
        },
        "page1_opportunities": [
            {"url": p.get("Top pages",""), "pos": parse_float(p.get("Position","")),
             "impr": parse_int(p.get("Impressions","")), "ctr": parse_pct(p.get("CTR","0%")),
             "clicks": parse_int(p.get("Clicks",""))}
            for p in p4_10[:30]
        ],
        "page2_quickwins": [
            {"url": p.get("Top pages",""), "pos": parse_float(p.get("Position","")),
             "impr": parse_int(p.get("Impressions","")), "ctr": parse_pct(p.get("CTR","0%"))}
            for p in p11_20[:30]
        ],
        "zero_click_queries": [
            {"kw": q.get("Top queries",""), "impr": parse_int(q.get("Impressions","")),
             "pos": parse_float(q.get("Position",""))}
            for q in zero_click[:50]
        ],
        "ctr_fixes_applied": updated,
        "skipped_no_file": skipped_no_file[:20],
    }

    out = DATA / "gsc_opportunities.json"
    out.write_text(json.dumps(opportunities, indent=2), encoding="utf-8")

    print("=" * 65)
    print(f"DONE: {len(updated)} pages CTR-fixed, {len(skipped_no_file)} skipped")
    print(f"Full report: data/gsc_opportunities.json")
    print()

    # ── Revenue projection ────────────────────────────────────────────────────
    current_monthly = total_clicks
    # If we fix page 2 pages to CTR 2% (from ~0.5%)
    p2_impr = sum(parse_int(p.get("Impressions","0")) for p in p11_20)
    p2_current_clicks = sum(parse_int(p.get("Clicks","0")) for p in p11_20)
    p2_projected = int(p2_impr * 0.02)

    # If we fix low-CTR page 1 pages to 3%
    p1_low_impr = sum(parse_int(p.get("Impressions","0")) for p in low_ctr_p1)
    p1_projected = int(p1_low_impr * 0.03)
    p1_current = sum(parse_int(p.get("Clicks","0")) for p in low_ctr_p1)

    print("REVENUE PROJECTION FROM CTR FIXES:")
    print(f"  Page 2 pages: {p2_impr:,} impr x 2% CTR = {p2_projected:,} clicks/mo "
          f"(currently {p2_current_clicks})")
    print(f"  Low-CTR page 1: {p1_low_impr:,} impr x 3% = {p1_projected:,} clicks/mo "
          f"(currently {p1_current})")
    proj_total = current_monthly + (p2_projected - p2_current_clicks) + (p1_projected - p1_current)
    print(f"  Total projected: {proj_total:,} clicks/mo vs current {current_monthly}")
    print(f"  At 1% conversion x $50 avg commission = "
          f"${proj_total * 0.01 * 50:,.0f}/mo projected")


if __name__ == "__main__":
    main()
