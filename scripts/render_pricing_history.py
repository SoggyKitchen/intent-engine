#!/usr/bin/env python3
"""
render_pricing_history.py — generates /pages/[tool]-pricing-history-2026.html
for every tracked tool, plus rebuilds /pages/saas-pricing-changes.html
from real change data.

Reads from pricing_snapshots + pricing_changes tables (track_pricing.py
populates them). Original-data SEO/AEO pages — exactly what Google's
helpful-content guidance rewards.

Run:  uv run python scripts/render_pricing_history.py
"""
from __future__ import annotations
import json, pathlib, re, sqlite3, sys, time
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "intent.db"
SEED_PATH = ROOT / "data" / "pricing_seed.json"
PAGES = ROOT / "site" / "pages"
PAGES.mkdir(parents=True, exist_ok=True)
SITEMAP = ROOT / "site" / "sitemap.xml"

NOW = datetime.now(timezone.utc)
TODAY_ISO = NOW.strftime("%Y-%m-%d")
TODAY_VERBOSE = NOW.strftime("%B %d, %Y")
MONTH_LABEL = NOW.strftime("%B %Y")


# === Page template ===========================================================

TEMPLATE = """<!DOCTYPE html>
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
<link rel="stylesheet" href="/assets/saaspare-ui.css">
<style>
  body{{background:#07070d;color:#f4f4f8;font-family:-apple-system,Segoe UI,system-ui,sans-serif;margin:0;line-height:1.6}}
  main{{max-width:920px;margin:0 auto;padding:2rem 1.5rem}}
  h1{{font-size:2.2rem;line-height:1.2;margin:1.2rem 0 .6rem 0}}
  h2{{font-size:1.4rem;margin:2rem 0 .8rem 0;color:#e94560}}
  table{{width:100%;border-collapse:collapse;margin:1rem 0;font-size:.92rem}}
  th, td{{padding:.65rem .9rem;text-align:left;border-bottom:1px solid rgba(255,255,255,.06)}}
  th{{background:rgba(233,69,96,.08);color:#fff;font-weight:700;font-size:.85rem;letter-spacing:.5px}}
  .featured-answer{{background:rgba(233,69,96,.08);border:1px solid rgba(233,69,96,.18);padding:1rem 1.3rem;border-radius:10px;margin:1.5rem 0}}
  .aff-disclosure-pill{{font-size:.78rem;color:rgba(255,255,255,.55);background:rgba(233,69,96,.08);border:1px solid rgba(233,69,96,.18);padding:.55rem .9rem;border-radius:8px;margin:1rem 0}}
  .source{{font-size:.85rem;color:rgba(255,255,255,.55)}}
  .badge{{display:inline-block;font-size:.74rem;padding:.18rem .55rem;border-radius:4px;font-weight:700}}
  .badge.h{{background:#3a1818;color:#ff8b9c}}
  .badge.d{{background:#0e3a28;color:#7fe6b8}}
  .badge.n{{background:#1f2540;color:#9bb8ff}}
  a{{color:#e94560}}
  .cta{{display:inline-block;padding:.7rem 1.4rem;background:#e94560;color:#fff;border-radius:8px;text-decoration:none;font-weight:700;margin:1rem .4rem 1rem 0}}
  nav{{padding:1.4rem 1.5rem;background:#07070d;border-bottom:1px solid rgba(255,255,255,.05)}}
  nav a{{color:#fff;text-decoration:none;font-weight:700}}
</style>
<!-- Microsoft Clarity -->
<script id="clarity-ms">
(function(c,l,a,r,i,t,y){{c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i+"?ref=bwt";y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);}})(window,document,"clarity","script","wne1kku7w1");
</script>
<!-- GA4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-RLYVYV8WQJ');</script>
</head>
<body>

<nav><a href="/">SaaSpare</a> &middot; <a href="/pages/">Compare</a> &middot; <a href="/pages/saas-pricing-changes">Price Changes</a></nav>

<main>
  <h1>{h1}</h1>

  <p class="aff-disclosure-pill"><strong style="color:rgba(255,255,255,.78)">Affiliate disclosure:</strong> Some links earn SaaSpare a commission if you buy. Editorial verdicts and price tracking are independent — vendors cannot pay to change either. Read our <a href="/affiliate-disclosure">full disclosure</a>.</p>

  <div class="featured-answer" data-aeo-answer>
    <p><strong>Quick answer ({month}):</strong> {quick_answer}</p>
  </div>

  {body_html}

  <h2>Why this data exists</h2>
  <p>SaaSpare tracks public pricing pages so buyers can spot hikes, plan
  restructures, and disappearing free trials before they sign. Every value
  is sourced from the vendor's official page (linked) and time-stamped.
  Found something stale? <a href="/pages/report-outdated-pricing">Report outdated pricing</a>.</p>

  <p class="source">Last verified: {today} · Vendor source: <a href="{source_url}" rel="noopener nofollow">{source_url}</a></p>

  <p style="margin-top:2rem">
    <a class="cta" href="/go/{affiliate_slug}" rel="sponsored nofollow noopener">See current {vendor} plans &rarr;</a>
    <a class="cta" href="/pages/{vendor_slug}-pricing-2026-plans-costs-what-you-actually-pay" style="background:#222;color:#fff">Full pricing breakdown</a>
  </p>
</main>

</body>
</html>
"""


VERTICAL_MAP = {
    "crm": "crm", "seo": "seo", "project-mgmt": "project-mgmt",
    "hr": "hr", "finance": "finance", "dev-tools": "dev-tools",
    "security": "security", "ai": "ai", "marketing": "marketing",
    "analytics": "analytics", "ecommerce": "ecommerce", "cloud": "cloud",
    "legal": "legal", "video": "video", "vpn": "vpn",
}


def render_history_body(tool_seed: dict, snapshots: list, changes: list) -> tuple[str, str, str]:
    """Return (body_html, quick_answer, schema_json)."""
    name = tool_seed["vendor_name"]
    plans = tool_seed["plans"]
    rows = []
    for plan in plans:
        m = plan.get("monthly_usd")
        a = plan.get("annual_usd")
        ft = "Yes" if plan.get("free_trial") else "No"
        cc = "Yes" if plan.get("cc_required") else "No"
        seats = plan.get("seat_minimum", 1)
        notes = plan.get("notes", "")
        m_str = f"${m:,.2f}" if m else "—"
        a_str = f"${a:,.2f}" if a else "—"
        rows.append(
            f"<tr><td><strong>{plan['plan']}</strong></td>"
            f"<td>{m_str}/mo</td><td>{a_str}/yr</td>"
            f"<td>{ft}</td><td>{cc}</td><td>{seats}</td>"
            f"<td>{notes}</td></tr>"
        )
    plans_table = (
        "<h2>Current plans (verified " + MONTH_LABEL + ")</h2>"
        "<table><thead><tr>"
        "<th>Plan</th><th>Monthly</th><th>Annual</th><th>Free trial</th>"
        "<th>Card required</th><th>Min seats</th><th>Notes</th></tr></thead>"
        "<tbody>" + "".join(rows) + "</tbody></table>"
    )

    if changes:
        rows = []
        for c in sorted(changes, key=lambda r: r["detected_at"], reverse=True)[:30]:
            d = datetime.fromtimestamp(c["detected_at"], tz=timezone.utc).strftime("%Y-%m-%d")
            badge_class = {"hike": "h", "drop": "d", "new": "n", "removed": "h"}.get(c["direction"], "n")
            pct = f"{c['pct_change']:+.1f}%" if c.get("pct_change") is not None else ""
            rows.append(
                f"<tr><td>{d}</td><td>{c['plan']}</td>"
                f"<td><span class='badge {badge_class}'>{c['direction']}</span> {c['field']}</td>"
                f"<td>{c['old_value'] or ''} → {c['new_value']}</td>"
                f"<td>{pct}</td></tr>"
            )
        history_table = (
            "<h2>Pricing change log</h2>"
            "<p>Every change SaaSpare has detected on " + name + "'s pricing page. "
            "Older changes appear lower in the list.</p>"
            "<table><thead><tr><th>Detected</th><th>Plan</th>"
            "<th>What changed</th><th>From → To</th><th>%</th></tr></thead>"
            "<tbody>" + "".join(rows) + "</tbody></table>"
        )
    else:
        history_table = (
            "<h2>Pricing change log</h2>"
            "<p>No changes detected yet — SaaSpare started tracking " + name +
            " in " + MONTH_LABEL + ". Check back monthly; price hikes are usually announced quietly via the pricing page only.</p>"
        )

    monthlies = [p.get("monthly_usd") for p in plans if p.get("monthly_usd") is not None]
    lo = min(monthlies) if monthlies else 0
    hi = max(monthlies) if monthlies else 0
    quick_answer = (
        f"{name} has {len(plans)} pricing plans as of {MONTH_LABEL}, "
        f"ranging from ${lo:,.2f} to ${hi:,.2f} per month. "
        f"Source verified directly from the vendor's official pricing page on {TODAY_VERBOSE}. "
        f"All plans, free-trial terms, and seat minimums are tabulated below; SaaSpare logs every change."
    )

    schema = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": f"{name} pricing history 2026",
        "description": f"Time-stamped pricing snapshots for {name} across all plans. Each snapshot is sourced from the vendor's official pricing page and includes monthly + annual cost, free-trial status, credit-card requirement, and seat minimums.",
        "url": f"https://saaspare.org/pages/{tool_seed['tool']}-pricing-history-2026",
        "creator": {"@type": "Organization", "name": "SaaSpare", "url": "https://saaspare.org"},
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "keywords": [f"{name} pricing", f"{name} pricing history", f"{name} plans", "SaaS pricing tracker"],
        "dateModified": TODAY_ISO,
        "isAccessibleForFree": True,
        "creator": {"@type": "Organization", "name": "SaaSpare", "url": "https://saaspare.org"},
    }

    return plans_table + history_table, quick_answer, json.dumps(schema, indent=2)


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
            f"<priority>0.8</priority><changefreq>weekly</changefreq></url>\n"
        )
        sm = sm.replace("</urlset>", entry + "</urlset>")
    SITEMAP.write_text(sm, encoding="utf-8")


def main() -> int:
    seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    written: list[str] = []

    for tool in seed["tools"]:
        slug = tool["tool"]
        page_slug = f"{slug}-pricing-history-2026"
        snapshots = [dict(r) for r in con.execute(
            "SELECT * FROM pricing_snapshots WHERE tool=? ORDER BY snapshot_at DESC", (slug,)
        ).fetchall()]
        changes = [dict(r) for r in con.execute(
            "SELECT * FROM pricing_changes WHERE tool=? ORDER BY detected_at DESC", (slug,)
        ).fetchall()]

        body_html, quick_answer, schema_json = render_history_body(tool, snapshots, changes)
        vertical = VERTICAL_MAP.get(tool["category"], "default")
        title = f"{tool['vendor_name']} Pricing History 2026 (Tracked {MONTH_LABEL}) — Real Plan Costs + Hikes"
        description = f"Updated {MONTH_LABEL}. Time-stamped {tool['vendor_name']} pricing data: every plan, every monthly/annual cost, every free-trial change, sourced from the vendor's official page. Updated continuously."
        if len(description) > 165:
            description = description[:162].rstrip() + "…"

        out = TEMPLATE.format(
            title=title[:70] if len(title) <= 70 else title[:67] + "…",
            description=description,
            slug=page_slug,
            vertical=vertical,
            schema_json=schema_json,
            h1=f"{tool['vendor_name']} Pricing History 2026",
            month=MONTH_LABEL,
            quick_answer=quick_answer,
            body_html=body_html,
            today=TODAY_VERBOSE,
            source_url=tool["source_url"],
            affiliate_slug=tool["affiliate_slug"],
            vendor=tool["vendor_name"],
            vendor_slug=slug,
        )
        (PAGES / f"{page_slug}.html").write_text(out, encoding="utf-8")
        written.append(page_slug)

    update_sitemap(written)
    con.close()
    print(f"=== render_pricing_history === wrote {len(written)} pages")
    for s in written:
        print(f"  /pages/{s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
