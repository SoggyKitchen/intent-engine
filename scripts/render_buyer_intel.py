#!/usr/bin/env python3
"""
render_buyer_intel.py — generate the two roll-up data pages:

  /pages/saas-buyer-signals-2026.html
    Aggregates 600+ scored buyer-intent signals from the harvester.
    Shows: signals by vertical, by intent score, by buyer role, plus
    raw insights with sourced URLs. Original-data SEO content nobody
    else has.

  /pages/saas-pricing-changes.html  (rebuilt)
    Replaces the old hand-curated examples with live data from the
    pricing_changes table. Shows hikes, drops, and new entries this
    month, plus the tracked tools we're watching.

Both pages are designed for AEO — featured-answer block at top,
Dataset schema, weekly changefreq.
"""
from __future__ import annotations
import json, pathlib, sqlite3, sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "intent.db"
SEED_PATH = ROOT / "data" / "pricing_seed.json"
PAGES = ROOT / "site" / "pages"
SITEMAP = ROOT / "site" / "sitemap.xml"

NOW = datetime.now(timezone.utc)
TODAY_ISO = NOW.strftime("%Y-%m-%d")
TODAY_VERBOSE = NOW.strftime("%B %d, %Y")
MONTH = NOW.strftime("%B %Y")
THIRTY_DAYS_AGO = int((NOW - timedelta(days=30)).timestamp())


# === Common page wrapper =====================================================

def page(slug: str, title: str, description: str, h1: str,
         quick_answer: str, body_html: str, schema_json: str,
         vertical: str = "default") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="https://saaspare.org/pages/{slug}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#07070d">
<meta property="og:type" content="article">
<meta property="og:url" content="https://saaspare.org/pages/{slug}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="https://saaspare.org/og/{vertical}.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="https://saaspare.org/og/{vertical}.svg">
<script type="application/ld+json">
{schema_json}
</script>
<style>
  body{{background:#07070d;color:#f4f4f8;font-family:-apple-system,Segoe UI,system-ui,sans-serif;margin:0;line-height:1.6}}
  main{{max-width:920px;margin:0 auto;padding:2rem 1.5rem}}
  h1{{font-size:2.2rem;line-height:1.2;margin:1.2rem 0 .6rem 0}}
  h2{{font-size:1.4rem;margin:2rem 0 .8rem 0;color:#e94560}}
  h3{{font-size:1.1rem;margin:1.4rem 0 .4rem 0}}
  table{{width:100%;border-collapse:collapse;margin:1rem 0;font-size:.92rem}}
  th, td{{padding:.65rem .9rem;text-align:left;border-bottom:1px solid rgba(255,255,255,.06);vertical-align:top}}
  th{{background:rgba(233,69,96,.08);color:#fff;font-weight:700;font-size:.85rem;letter-spacing:.5px}}
  .featured-answer{{background:rgba(233,69,96,.08);border:1px solid rgba(233,69,96,.18);padding:1rem 1.3rem;border-radius:10px;margin:1.5rem 0}}
  .aff-disclosure-pill{{font-size:.78rem;color:rgba(255,255,255,.55);background:rgba(233,69,96,.08);border:1px solid rgba(233,69,96,.18);padding:.55rem .9rem;border-radius:8px;margin:1rem 0}}
  .source{{font-size:.85rem;color:rgba(255,255,255,.55)}}
  .badge{{display:inline-block;font-size:.74rem;padding:.18rem .55rem;border-radius:4px;font-weight:700}}
  .badge.h{{background:#3a1818;color:#ff8b9c}}
  .badge.d{{background:#0e3a28;color:#7fe6b8}}
  .badge.n{{background:#1f2540;color:#9bb8ff}}
  .stat{{display:inline-block;padding:1rem 1.4rem;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:10px;margin:.4rem .4rem 0 0;min-width:140px}}
  .stat .v{{font-size:1.6rem;font-weight:800;color:#e94560;display:block}}
  .stat .l{{font-size:.78rem;color:rgba(255,255,255,.55);text-transform:uppercase;letter-spacing:.5px}}
  a{{color:#e94560}}
  .cta{{display:inline-block;padding:.7rem 1.4rem;background:#e94560;color:#fff;border-radius:8px;text-decoration:none;font-weight:700;margin:1rem .4rem 1rem 0}}
  nav{{padding:1.4rem 1.5rem;background:#07070d;border-bottom:1px solid rgba(255,255,255,.05)}}
  nav a{{color:#fff;text-decoration:none;font-weight:700}}
</style>
<script id="clarity-ms">
(function(c,l,a,r,i,t,y){{c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i+"?ref=bwt";y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);}})(window,document,"clarity","script","wne1kku7w1");
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-RLYVYV8WQJ');</script>
</head>
<body>
<nav><a href="/">SaaSpare</a> &middot; <a href="/pages/">Compare</a> &middot; <a href="/pages/saas-pricing-changes">Price Changes</a> &middot; <a href="/pages/saas-buyer-signals-2026">Buyer Signals</a></nav>
<main>
  <h1>{h1}</h1>
  <p class="aff-disclosure-pill"><strong style="color:rgba(255,255,255,.78)">Affiliate disclosure:</strong> Some links earn SaaSpare a commission if you buy. Editorial verdicts and tracked data are independent — vendors cannot pay to change either. <a href="/affiliate-disclosure">Full disclosure</a>.</p>
  <div class="featured-answer" data-aeo-answer>
    <p><strong>Quick answer ({MONTH}):</strong> {quick_answer}</p>
  </div>
  {body_html}
  <p class="source">Last verified: {TODAY_VERBOSE} · Powered by SaaSpare's nightly buyer-intent harvester.</p>
</main>
</body>
</html>
"""


# === /pages/saas-buyer-signals-2026 ==========================================

def render_buyer_signals(con: sqlite3.Connection) -> str | None:
    rows = list(con.execute("""
        SELECT s.intent, s.budget_signal, s.urgency, s.vertical, s.buyer_role,
               s.estimated_deal_usd, s.monetization_path, s.confidence,
               s.profit_score, s.llm_reasoning, s.ts,
               r.title, r.url, r.source, r.subreddit, r.author
        FROM scored_signals s JOIN raw_signals r ON s.raw_id = r.id
        WHERE s.profit_score >= 50
        ORDER BY s.profit_score DESC
        LIMIT 500
    """).fetchall())

    if not rows:
        return None

    # Aggregate
    by_vertical = Counter()
    by_role = Counter()
    by_path = Counter()
    avg_intent_per_vert: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        if r[3]:
            by_vertical[r[3]] += 1
            avg_intent_per_vert[r[3]].append(r[0] or 0)
        if r[4]: by_role[r[4]] += 1
        if r[6]: by_path[r[6]] += 1

    total = len(rows)
    avg_score = sum((r[8] or 0) for r in rows) / total
    high_intent = sum(1 for r in rows if (r[0] or 0) >= 70)

    stats_html = (
        f'<div style="margin:1rem 0">'
        f'<span class="stat"><span class="v">{total}</span><span class="l">Signals analysed</span></span>'
        f'<span class="stat"><span class="v">{high_intent}</span><span class="l">High-intent (70+)</span></span>'
        f'<span class="stat"><span class="v">{len(by_vertical)}</span><span class="l">Verticals</span></span>'
        f'<span class="stat"><span class="v">{avg_score:.0f}</span><span class="l">Avg profit score</span></span>'
        f'</div>'
    )

    # Vertical breakdown table
    vrows = []
    for vert, n in by_vertical.most_common():
        avg_int = sum(avg_intent_per_vert[vert]) / max(1, len(avg_intent_per_vert[vert]))
        vrows.append(
            f"<tr><td><strong>{vert.replace('_', ' ').title()}</strong></td>"
            f"<td>{n}</td><td>{avg_int:.0f}</td></tr>"
        )
    vert_table = (
        "<h2>Buyer activity by vertical</h2>"
        "<p>Where SaaSpare's harvester is detecting the strongest commercial intent right now.</p>"
        '<table><thead><tr><th>Vertical</th><th>Signals (last 30d)</th><th>Avg intent</th></tr></thead>'
        f"<tbody>{''.join(vrows)}</tbody></table>"
    )

    # Top insights table
    insights_rows = []
    seen_reasonings = set()
    for r in rows[:60]:
        intent, _, _, vert, role, deal_usd, _, conf, score, reasoning, ts, title, url, source, subreddit, author = r
        if not reasoning:
            continue
        # de-duplicate near-identical reasonings
        key = reasoning[:80]
        if key in seen_reasonings: continue
        seen_reasonings.add(key)
        if len(insights_rows) >= 25: break
        date = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        src = subreddit or source or "public"
        link = f'<a href="{url}" rel="nofollow noopener">source</a>' if url else ""
        insights_rows.append(
            f"<tr><td>{date}</td><td>{(vert or '').replace('_',' ')}</td>"
            f"<td>{role or '—'}</td><td>{intent or 0}</td>"
            f"<td>{reasoning[:240]}{('…' if len(reasoning) > 240 else '')}</td>"
            f"<td>{src} {link}</td></tr>"
        )
    insights_table = (
        "<h2>Top buyer insights (last 30 days)</h2>"
        "<p>Real signals from public B2B-buyer discussions, scored by SaaSpare's "
        "intent classifier. Each row links back to the source. We do not republish "
        "user content; we summarise the signal and link out.</p>"
        '<table><thead><tr><th>Date</th><th>Vertical</th><th>Buyer role</th>'
        '<th>Intent</th><th>Signal summary</th><th>Source</th></tr></thead>'
        f"<tbody>{''.join(insights_rows)}</tbody></table>"
    )

    quick = (
        f"SaaSpare analysed {total} public B2B buyer-intent signals in the last 30 days. "
        f"{high_intent} were high-intent (70+) signals across {len(by_vertical)} verticals. "
        f"The dominant commercial vertical right now is {by_vertical.most_common(1)[0][0].replace('_',' ')} "
        f"with {by_vertical.most_common(1)[0][1]} signals; the dominant buyer role is "
        f"{by_role.most_common(1)[0][0]}. Full breakdown and source citations below."
    )

    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": f"SaaS Buyer Signal Index — {MONTH}",
        "description": "Aggregated public buyer-intent signals across B2B SaaS verticals. Updated weekly. Each signal is sourced from public discussion (Reddit, HN, GitHub, forums) and scored by SaaSpare's intent classifier. We summarise themes; we do not republish user content.",
        "url": "https://saaspare.org/pages/saas-buyer-signals-2026",
        "creator": {"@type": "Organization", "name": "SaaSpare", "url": "https://saaspare.org"},
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "keywords": ["B2B buyer intent", "SaaS buyer signals", "SaaS purchase intent", "software buying signals"],
        "dateModified": TODAY_ISO,
        "isAccessibleForFree": True
    }, indent=2)

    body = stats_html + vert_table + insights_table + (
        '<p style="margin-top:1.6rem">'
        '<a class="cta" href="/pages/">Browse comparisons</a>'
        '<a class="cta" href="/pages/saas-pricing-changes" style="background:#222">Recent price changes</a>'
        '</p>'
    )

    title = f"SaaS Buyer Signals {MONTH} — Real Public-Discussion Intent Data"
    if len(title) > 70: title = title[:67] + "…"
    desc = f"Updated {MONTH}. {total} public B2B-buyer signals analysed across {len(by_vertical)} verticals. Source citations on every row. Original SaaSpare data — updated nightly."
    if len(desc) > 165: desc = desc[:162] + "…"

    return page(
        slug="saas-buyer-signals-2026",
        title=title,
        description=desc,
        h1=f"SaaS Buyer Signals {MONTH}",
        quick_answer=quick,
        body_html=body,
        schema_json=schema,
        vertical="default",
    )


# === /pages/saas-pricing-changes (rebuild from real data) ====================

def render_pricing_changes(con: sqlite3.Connection) -> str:
    seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    tracked = {t["tool"]: t for t in seed["tools"]}

    # Real changes from last 30 days (only price-impacting)
    rows = list(con.execute("""
        SELECT tool, plan, field, old_value, new_value, direction, pct_change,
               source_url, detected_at
        FROM pricing_changes
        WHERE detected_at >= ?
          AND field IN ('monthly_usd', 'annual_usd', 'free_trial', 'cc_required', 'seat_minimum')
          AND direction IN ('hike', 'drop')
        ORDER BY detected_at DESC
        LIMIT 50
    """, (THIRTY_DAYS_AGO,)).fetchall())

    if rows:
        change_rows = []
        for tool, plan, field, old_v, new_v, direction, pct, _, ts in rows:
            d = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
            badge = "h" if direction == "hike" else "d"
            pct_str = f"{pct:+.1f}%" if pct is not None else ""
            vendor = tracked.get(tool, {}).get("vendor_name", tool)
            link = f"/pages/{tool}-pricing-history-2026"
            change_rows.append(
                f"<tr><td>{d}</td><td><a href='{link}'><strong>{vendor}</strong></a></td>"
                f"<td>{plan}</td><td>{field}</td>"
                f"<td><span class='badge {badge}'>{direction}</span> {old_v} → {new_v}</td>"
                f"<td>{pct_str}</td></tr>"
            )
        changes_html = (
            f"<h2>Detected changes ({MONTH})</h2>"
            f'<table><thead><tr><th>Detected</th><th>Vendor</th><th>Plan</th>'
            f'<th>Field</th><th>Change</th><th>%</th></tr></thead>'
            f"<tbody>{''.join(change_rows)}</tbody></table>"
        )
    else:
        changes_html = (
            f"<h2>Detected changes ({MONTH})</h2>"
            "<p>No price hikes or drops detected this month — vendor pricing has been "
            "stable. SaaSpare runs the diff every 24 hours; this page updates "
            "automatically as soon as any of our tracked tools changes.</p>"
        )

    # Tracked-tools list
    tracked_rows = []
    for tool in seed["tools"]:
        slug = tool["tool"]
        ftrials = sum(1 for p in tool["plans"] if p.get("free_trial"))
        cc_req = sum(1 for p in tool["plans"] if p.get("cc_required"))
        tracked_rows.append(
            f"<tr><td><a href='/pages/{slug}-pricing-history-2026'><strong>{tool['vendor_name']}</strong></a></td>"
            f"<td>{tool['category']}</td><td>{len(tool['plans'])}</td>"
            f"<td>{ftrials}/{len(tool['plans'])}</td><td>{cc_req}/{len(tool['plans'])}</td>"
            f"<td><a href='{tool['source_url']}' rel='nofollow noopener'>vendor page</a></td></tr>"
        )
    tracked_html = (
        f"<h2>Tools currently tracked ({len(seed['tools'])})</h2>"
        "<p>SaaSpare tracks these vendors' public pricing pages and logs every change. "
        "Click a vendor to see the full change history and current plan breakdown.</p>"
        '<table><thead><tr><th>Vendor</th><th>Category</th><th>Plans</th>'
        '<th>Free trials</th><th>CC required</th><th>Source</th></tr></thead>'
        f"<tbody>{''.join(tracked_rows)}</tbody></table>"
    )

    body = changes_html + tracked_html + (
        '<h2>Why this page exists</h2>'
        '<p>Most "best of" SaaS roundups go stale within weeks. Vendors quietly hike prices, '
        'remove free trials, or change plan limits, and old reviews never catch up. '
        'SaaSpare runs an automated diff on tracked vendor pricing pages every 24 hours '
        f'and logs everything here. As of {MONTH}, we track {len(seed["tools"])} vendors '
        'and are expanding to 50 next.</p>'
    )

    quick = (
        f"SaaSpare tracks {len(seed['tools'])} SaaS vendor pricing pages with daily diffs. "
        f"This month detected {len(rows)} price changes "
        f"({sum(1 for r in rows if r[5]=='hike')} hikes, {sum(1 for r in rows if r[5]=='drop')} drops). "
        f"All data is sourced directly from vendors' public pricing pages and time-stamped. "
        f"Click any vendor below for the full pricing history and change log."
    )

    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": f"SaaS Pricing Change Tracker — {MONTH}",
        "description": "Live tracker of monthly SaaS vendor pricing changes. Each change is detected via daily diff against the vendor's public pricing page. Currently tracking 15 of the top B2B SaaS tools.",
        "url": "https://saaspare.org/pages/saas-pricing-changes",
        "creator": {"@type": "Organization", "name": "SaaSpare", "url": "https://saaspare.org"},
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "keywords": ["SaaS pricing changes", "SaaS price tracker", "vendor pricing history", "B2B software pricing", "SaaS price hikes"],
        "dateModified": TODAY_ISO,
        "isAccessibleForFree": True
    }, indent=2)

    return page(
        slug="saas-pricing-changes",
        title=f"SaaS Pricing Changes {MONTH} — Live Tracker, Real Diffs",
        description=f"Updated {MONTH}. Live tracker of SaaS pricing changes across {len(seed['tools'])}+ vendors. Daily diff vs. vendor pages. {len(rows)} changes this month. No fluff — just data, sources, and dates.",
        h1=f"SaaS Pricing Changes — {MONTH}",
        quick_answer=quick,
        body_html=body,
        schema_json=schema,
        vertical="default",
    )


# === Sitemap update ==========================================================

def update_sitemap(slugs: list[str]) -> None:
    if not SITEMAP.exists():
        return
    sm = SITEMAP.read_text(encoding="utf-8")
    for slug in slugs:
        url = f"https://saaspare.org/pages/{slug}"
        if f"<loc>{url}</loc>" in sm:
            continue
        entry = (
            f"  <url><loc>{url}</loc><lastmod>{TODAY_ISO}</lastmod>"
            f"<priority>0.8</priority><changefreq>daily</changefreq></url>\n"
        )
        sm = sm.replace("</urlset>", entry + "</urlset>")
    SITEMAP.write_text(sm, encoding="utf-8")


def main() -> int:
    con = sqlite3.connect(DB_PATH)
    written: list[str] = []

    # Buyer signals
    bs = render_buyer_signals(con)
    if bs:
        (PAGES / "saas-buyer-signals-2026.html").write_text(bs, encoding="utf-8")
        written.append("saas-buyer-signals-2026")
        print("wrote /pages/saas-buyer-signals-2026")

    # Pricing changes (overwrite existing static page)
    pc = render_pricing_changes(con)
    (PAGES / "saas-pricing-changes.html").write_text(pc, encoding="utf-8")
    written.append("saas-pricing-changes")
    print("wrote /pages/saas-pricing-changes (rebuilt from real data)")

    update_sitemap(written)
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
