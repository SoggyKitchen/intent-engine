"""
Publish the Cost Transparency Scores: ranked page, written verdicts, homepage block.

The ask was star ratings like saaspare.com's. Theirs are fabricated (their owner
said so), and Google's structured-data guidance forbids marking up ratings
collected elsewhere, so copying either half trades a clean record for a widget.

This is the version that stands up to a reviewer: a published editorial rating
of the kind a consumer magazine runs. Scores come from
scripts/compute_transparency_score.py, computed off pricing we verified
ourselves. The written verdicts live in data/editorial_verdicts.json and are
hand-written, not templated - template-generated verdicts are exactly the thin
pattern that got 1,053 pages noindexed, and fifteen tools is small enough to
write properly.

Schema: Review nodes authored by the SaaSpare Organization, which is what
Google permits for editorial reviews, with the real verdict as reviewBody.
There is deliberately no aggregateRating anywhere - we host no user reviews,
and inventing one is the failure mode this rebuild is recovering from.

Idempotent. The homepage block is delimited by comment markers so a re-run
replaces it rather than stacking copies.
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORES = ROOT / "data" / "transparency_scores.json"
VERDICTS = ROOT / "data" / "editorial_verdicts.json"
PAGE = ROOT / "site" / "pages" / "saas-pricing-transparency-scores-2026.html"
HOME = ROOT / "site" / "index.html"
URL = "https://saaspare.org/pages/saas-pricing-transparency-scores-2026"

START = "<!-- sp-transparency-block:start -->"
END = "<!-- sp-transparency-block:end -->"

TITLE = ("SaaS Pricing Transparency Scores 2026: 15 Tools Ranked on What They Hide")
DESC = ("We ranked 15 B2B SaaS vendors on eight things buyers get caught by: setup "
        "fees, seat minimums, annual-only billing, card-up-front trials and seat "
        "surcharges. Editorial scores from verified pricing, with a written verdict "
        "on every tool.")

CAT_LABELS = {
    "crm": "CRM", "seo": "SEO tools", "project-mgmt": "Project management",
    "dev-tools": "Dev tools", "security": "Security", "finance": "Finance",
    "ecommerce": "E-commerce",
}

DEFS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
        '<linearGradient id="sp-half"><stop offset="50%" stop-color="var(--pink)"/>'
        '<stop offset="50%" stop-color="rgba(255,247,248,.18)"/></linearGradient>'
        "</defs></svg>")


def stars_svg(value, size=18):
    out = []
    for i in range(1, 6):
        if value >= i:
            fill = "var(--pink)"
        elif value >= i - 0.5:
            fill = "url(#sp-half)"
        else:
            fill = "rgba(255,247,248,.18)"
        out.append(
            f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="{fill}" '
            f'aria-hidden="true" style="flex:none"><path d="M12 2l3 6.9 7.5.8-5.6 5 '
            f'1.6 7.3L12 18.3 5.5 22l1.6-7.3-5.6-5 7.5-.8z"/></svg>'
        )
    return "".join(out)


def pills(criteria, labels):
    out = []
    for k, v in criteria.items():
        cls = {2: "ok", 1: "mid", 0: "bad"}[v]
        mark = {2: "&#10003;", 1: "~", 0: "&#10007;"}[v]
        out.append(f'<span class="tr-pill tr-{cls}">{mark} {labels[k]}</span>')
    return "".join(out)


def verdict_block(s, v, labels, rank):
    if not v:
        return ""
    return f"""  <article class="tr-v" id="{s['tool']}">
    <div class="tr-v-head">
      <span class="tr-rank">#{rank}</span>
      <div class="tr-v-title">
        <h3>{s['vendor']}</h3>
        <p class="tr-cat">{CAT_LABELS.get(s['category'], s['category'] or '')}</p>
      </div>
      <div class="tr-v-score">
        <div class="tr-stars" role="img" aria-label="{s['stars']} out of 5">{stars_svg(s['stars'], 16)}</div>
        <p class="tr-pts">{s['stars']} &middot; {s['points']}/{s['max_points']} points</p>
      </div>
    </div>
    <h4 class="tr-v-headline">{v['headline']}</h4>
    <p class="tr-v-body">{v['body']}</p>
    <div class="tr-v-cols">
      <p><b>Best for</b> {v['best_for']}</p>
      <p class="tr-warn"><b>Watch for</b> {v['watch_for']}</p>
    </div>
    <div class="tr-pills">{pills(s['criteria'], labels)}</div>
    <a class="tr-src" href="{s['source_url']}" rel="nofollow noopener" target="_blank">Vendor pricing page &rarr;</a>
  </article>
"""


def build_page(d, vd):
    scores, meta = d["scores"], d["_meta"]
    labels = {c["key"]: c["label"] for c in meta["criteria"]}
    verdicts = vd["verdicts"]
    verified = meta["pricing_verified_on"]
    pretty = date.fromisoformat(verified).strftime("%d %B %Y").lstrip("0")

    # Category winners. A single-entrant category has no contest to win, so it
    # is skipped rather than handed a trophy for turning up.
    by_cat = {}
    for s in scores:
        by_cat.setdefault(s["category"], []).append(s)
    awards = ""
    for cat, group in sorted(by_cat.items()):
        if len(group) < 2:
            continue
        w = max(group, key=lambda x: x["points"])
        awards += (
            f'<a class="tr-award" href="#{w["tool"]}">'
            f'<span class="tr-award-cat">{CAT_LABELS.get(cat, cat)}</span>'
            f'<span class="tr-award-name">{w["vendor"]}</span>'
            f'<span class="tr-award-stars">{stars_svg(w["stars"], 13)}</span></a>'
        )

    body = "".join(
        verdict_block(s, verdicts.get(s["tool"]), labels, i)
        for i, s in enumerate(scores, 1)
    )

    rubric = "".join(
        f"<tr><td><strong>{c['label']}</strong><br>"
        f"<span class=\"tr-test\">{c['test']}</span></td><td>0&ndash;2</td></tr>\n"
        for c in meta["criteria"]
    )

    heads = "".join(f'<th>{c["label"]}</th>' for c in meta["criteria"])
    table = "".join(
        f'<tr><td><a href="#{s["tool"]}"><strong>{s["vendor"]}</strong></a></td>'
        + "".join(f'<td class="tr-c tr-c{v}">{v}</td>' for v in s["criteria"].values())
        + f'<td class="tr-total">{s["points"]}</td><td class="tr-total">{s["stars"]}</td></tr>\n'
        for s in scores
    )

    reviews = []
    for s in scores:
        v = verdicts.get(s["tool"])
        if not v:
            continue
        pos = [labels[k] for k, x in s["criteria"].items() if x == 2]
        neg = [labels[k] for k, x in s["criteria"].items() if x == 0]
        r = {
            "@type": "Review",
            "itemReviewed": {"@type": "SoftwareApplication", "name": s["vendor"],
                             "applicationCategory": "BusinessApplication"},
            "reviewRating": {"@type": "Rating", "ratingValue": s["stars"],
                             "bestRating": 5, "worstRating": 0},
            "name": f"{s['vendor']}: {v['headline']}",
            "author": {"@id": "https://saaspare.org/#organization"},
            "publisher": {"@id": "https://saaspare.org/#organization"},
            "datePublished": verified,
            "reviewBody": v["body"] + " Best for: " + v["best_for"] +
                          " Watch for: " + v["watch_for"],
        }
        if pos:
            r["positiveNotes"] = {"@type": "ItemList", "itemListElement": [
                {"@type": "ListItem", "position": i, "name": p}
                for i, p in enumerate(pos, 1)]}
        if neg:
            r["negativeNotes"] = {"@type": "ItemList", "itemListElement": [
                {"@type": "ListItem", "position": i, "name": n}
                for i, n in enumerate(neg, 1)]}
        reviews.append(r)

    def ld(o):
        return ('<script type="application/ld+json">\n'
                + json.dumps(o, indent=2, ensure_ascii=False) + "\n</script>")

    article_ld = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": TITLE, "description": DESC, "url": URL,
        "datePublished": verified, "dateModified": verified,
        "author": {"@type": "Person", "name": "Kaylan von Papen",
                   "url": "https://saaspare.org/authors/kaylan-von-papen"},
        "publisher": {"@id": "https://saaspare.org/#organization"},
        "review": reviews,
    }

    top = scores[0]
    bottom = scores[-1]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="{URL}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="apple-touch-icon" sizes="512x512" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#07070d">
<meta property="og:type" content="article">
<meta property="og:url" content="{URL}">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:image" content="https://saaspare.org/og/default.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="https://saaspare.org/og/default.svg">
<link rel="stylesheet" href="/assets/saaspare-v2.css">
<link rel="stylesheet" href="/assets/saaspare-ui.css">
<link rel="stylesheet" href="/assets/motion.css">
{ld(article_ld)}
<style>{CSS}</style>
</head>
<body style="background:#050407;color:rgba(255,248,245,.88)">
{DEFS}
<main class="tr-wrap">
  <p class="tr-eyebrow">Editorial ratings</p>
  <h1>SaaS pricing transparency scores</h1>
  <p class="tr-sub">Not user reviews. Our own score for one thing: how straight a
  vendor's pricing page is with the buyer. Eight tests, two points each, sixteen
  points total. Every point traces back to a price we read off the vendor's own
  page, and every tool gets a written verdict.</p>

  <p class="tr-stamp">Pricing verified <b>{pretty}</b> &middot; {len(scores)} vendors
  &middot; {len(meta['criteria'])} criteria &middot; recomputed nightly, never hand-set</p>

  <div class="tr-callout">
    <h2>What the rankings say</h2>
    <p><strong>{top['vendor']}</strong> tops the table on {top['points']}/{top['max_points']}.
    <strong>{bottom['vendor']}</strong> comes last on {bottom['points']}/{bottom['max_points']}, and
    not for being expensive: no free tier, no trial, and $40&ndash;$80 a month for each
    extra seat.</p>
    <p><strong>HubSpot</strong> publishes $100 a seat and charges
    <a href="/pages/saas-hidden-costs-2026">a required $1,500 onboarding fee</a> on top,
    making year one $2,700 for a single seat.</p>
  </div>

  <h2 class="tr-h">Most transparent by category</h2>
  <p class="tr-note">Categories with only one tracked vendor are left out. A field of
  one has no winner.</p>
  <div class="tr-awards">{awards}</div>

  <h2 class="tr-h">The ranking, with verdicts</h2>
  <p class="tr-note">Written by hand, from the pricing data. These judge how a vendor
  sells, not how the software performs.</p>
{body}
  <h2 class="tr-h">How the score is built</h2>
  <p class="tr-note">Eight criteria, nothing weighted, nothing subjective. A vendor who
  fixes their pricing page scores higher on the next run automatically.</p>
  <div class="tr-scroll"><table class="tr">
    <thead><tr><th>Criterion</th><th>Points</th></tr></thead>
    <tbody>
{rubric}    </tbody>
  </table></div>

  <h2 class="tr-h">Every score, every criterion</h2>
  <p class="tr-note">Green passes, amber is partial, pink fails.</p>
  <div class="tr-scroll"><table class="tr">
    <thead><tr><th>Vendor</th>{heads}<th>Total</th><th>Stars</th></tr></thead>
    <tbody>
{table}    </tbody>
  </table></div>

  <p class="tr-method">
    <strong>What this is and isn't.</strong> Editorial scores published by SaaSpare,
    not ratings submitted by users. We host no user reviews, so we publish no user
    rating, and we do not republish other sites' review scores as our own. The score
    measures pricing transparency only. Inputs come from
    <a href="/pages/saas-hidden-costs-2026">our verified hidden-costs data</a> and
    vendor pricing pages read on {pretty}. Method:
    <a href="/methodology">methodology</a> &middot;
    <a href="/corrections">corrections policy</a>. Think a score is wrong?
    <a href="/contact">Tell us</a> and we will recheck and log it.
    By <a href="/authors/kaylan-von-papen">Kaylan von Papen</a>.
  </p>
</main>
</body>
</html>
"""


CSS = """
  .tr-wrap{max-width:1080px;margin:0 auto;padding:48px 20px 96px}
  .tr-eyebrow{color:var(--pink);font-weight:600;letter-spacing:.08em;text-transform:uppercase;font-size:12px;margin:0 0 12px}
  .tr-wrap h1{font-size:clamp(30px,4.4vw,48px);line-height:1.08;margin:0 0 16px;color:var(--ink);letter-spacing:-.025em}
  .tr-sub{color:var(--ink-3);font-size:18px;line-height:1.65;max-width:720px;margin:0 0 24px}
  .tr-stamp{display:inline-flex;flex-wrap:wrap;gap:6px;background:var(--glass);border:1px solid var(--line);border-radius:var(--r-full);padding:9px 18px;color:var(--ink-4);font-size:13px;margin-bottom:44px}
  .tr-stamp b{color:var(--green)}
  .tr-callout{background:var(--glass-pink);border:1px solid var(--line-pink);border-radius:var(--r-lg);padding:26px 30px;box-shadow:var(--shadow-pink);margin:0 0 12px}
  .tr-callout h2{margin:0 0 12px;font-size:20px;color:var(--ink)}
  .tr-callout p{margin:0 0 10px;color:var(--ink-2);line-height:1.7}
  .tr-callout p:last-child{margin-bottom:0}
  .tr-callout a{color:var(--pink)}
  .tr-wrap h2.tr-h{font-size:26px;margin:56px 0 8px;color:var(--ink);letter-spacing:-.02em}
  .tr-note{color:var(--ink-4);font-size:14px;margin:0 0 20px;line-height:1.6;max-width:720px}
  .tr-awards{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}
  .tr-award{display:flex;flex-direction:column;gap:6px;padding:16px 18px;background:var(--glass);border:1px solid var(--line);border-radius:var(--r-md);text-decoration:none;transition:border-color .18s,transform .18s}
  .tr-award:hover{border-color:var(--line-pink);transform:translateY(-2px)}
  .tr-award-cat{color:var(--ink-4);font-size:11px;text-transform:uppercase;letter-spacing:.06em}
  .tr-award-name{color:var(--ink);font-weight:700;font-size:16px}
  .tr-award-stars{display:flex;gap:2px}
  .tr-v{background:var(--glass);border:1px solid var(--line);border-radius:var(--r-lg);padding:24px 26px;margin:0 0 14px;box-shadow:var(--shadow-card);scroll-margin-top:90px}
  .tr-v-head{display:flex;align-items:flex-start;gap:16px;flex-wrap:wrap}
  .tr-rank{font-size:15px;font-weight:800;color:var(--ink-5);min-width:34px;padding-top:3px}
  .tr-v-title{flex:1;min-width:150px}
  .tr-v-title h3{margin:0;font-size:20px;color:var(--ink)}
  .tr-cat{margin:2px 0 0;color:var(--ink-4);font-size:12px}
  .tr-v-score{text-align:right}
  .tr-stars{display:flex;gap:2px;justify-content:flex-end}
  .tr-pts{margin:5px 0 0;color:var(--ink-4);font-size:12px}
  .tr-v-headline{margin:16px 0 8px;font-size:17px;color:var(--pink-light);font-weight:700;line-height:1.35}
  .tr-v-body{margin:0 0 16px;color:var(--ink-2);line-height:1.7;font-size:15px}
  .tr-v-cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin:0 0 16px}
  .tr-v-cols p{margin:0;color:var(--ink-3);font-size:14px;line-height:1.6;padding:12px 14px;background:rgba(255,255,255,.03);border-radius:var(--r-sm);border-left:2px solid var(--green)}
  .tr-v-cols p b{display:block;color:var(--ink-4);font-size:11px;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px}
  .tr-v-cols .tr-warn{border-left-color:var(--amber)}
  .tr-pills{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 14px}
  .tr-pill{font-size:11.5px;padding:5px 10px;border-radius:var(--r-full);border:1px solid var(--line);color:var(--ink-4);white-space:nowrap}
  .tr-ok{color:var(--green);border-color:rgba(54,230,161,.28);background:var(--green-soft)}
  .tr-mid{color:var(--amber);border-color:rgba(245,185,66,.28);background:rgba(245,185,66,.08)}
  .tr-bad{color:var(--pink);border-color:var(--line-pink);background:rgba(255,65,109,.08)}
  .tr-src{color:var(--ink-4);font-size:12.5px;text-decoration:none}
  .tr-src:hover{color:var(--pink)}
  .tr-scroll{overflow-x:auto;border:1px solid var(--line);border-radius:var(--r-md);background:var(--bg-rise);box-shadow:var(--shadow-card)}
  table.tr{width:100%;border-collapse:collapse;font-size:14px;min-width:720px}
  table.tr th{text-align:left;padding:12px 14px;color:var(--ink-4);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid var(--line)}
  table.tr td{padding:13px 14px;border-bottom:1px solid var(--line-soft);color:var(--ink-2)}
  table.tr tr:last-child td{border-bottom:0}
  table.tr a{color:var(--ink-2);text-decoration:none}
  table.tr a:hover{color:var(--pink)}
  .tr-c{text-align:center;font-weight:700}
  .tr-c2{color:var(--green)}
  .tr-c1{color:var(--amber)}
  .tr-c0{color:var(--pink)}
  .tr-total{text-align:center;font-weight:800;color:var(--ink)}
  .tr-test{color:var(--ink-4);font-size:13px}
  .tr-method{margin-top:56px;padding-top:24px;border-top:1px solid var(--line);color:var(--ink-4);font-size:14px;line-height:1.75}
  .tr-method a{color:var(--ink-3)}
  @media (max-width:560px){
    .tr-v-score{text-align:left;width:100%}
    .tr-stars{justify-content:flex-start}
  }
"""


def build_home_block(d, vd):
    scores = d["scores"][:5]
    verdicts = vd["verdicts"]
    pretty = date.fromisoformat(d["_meta"]["pricing_verified_on"]).strftime("%B %Y")
    worst = d["scores"][-1]

    rows = "".join(
        f'<a class="sptr-row" href="{URL}#{s["tool"]}">'
        f'<span class="sptr-rank">{i}</span>'
        f'<span class="sptr-main"><span class="sptr-name">{s["vendor"]}</span>'
        f'<span class="sptr-say">{verdicts.get(s["tool"], {}).get("headline", "")}</span></span>'
        f'<span class="sptr-stars">{stars_svg(s["stars"], 14)}</span>'
        f'<span class="sptr-num">{s["stars"]}</span></a>'
        for i, s in enumerate(scores, 1)
    )

    return f"""{START}
<section class="sptr" aria-labelledby="sptr-h">
  {DEFS}
  <style>
    .sptr{{padding:7.5rem clamp(1.25rem,4vw,3rem) 4.5rem;max-width:1180px;margin:0 auto;position:relative;z-index:2}}
    .sptr-head{{display:flex;flex-wrap:wrap;gap:24px;justify-content:space-between;align-items:flex-end;margin-bottom:26px}}
    .sptr-eyebrow{{color:#ff416d;font-weight:600;letter-spacing:.08em;text-transform:uppercase;font-size:12px;margin:0 0 8px}}
    .sptr h2{{font-size:clamp(27px,3vw,40px);line-height:1.08;margin:0;color:#fff7f8;font-weight:800;letter-spacing:-.025em}}
    .sptr-lede{{color:rgba(255,247,248,.64);margin:12px 0 0;max-width:600px;line-height:1.65}}
    .sptr-panel{{background:linear-gradient(180deg,rgba(255,255,255,.055),rgba(255,255,255,.025));border:1px solid rgba(255,255,255,.09);border-radius:20px;box-shadow:0 24px 80px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.08);overflow:hidden}}
    .sptr-row{{display:flex;align-items:center;gap:14px;padding:16px 22px;border-bottom:1px solid rgba(255,255,255,.05);text-decoration:none;transition:background .18s}}
    .sptr-row:last-of-type{{border-bottom:1px solid rgba(255,255,255,.05)}}
    .sptr-row:hover{{background:rgba(255,75,115,.06)}}
    .sptr-rank{{color:rgba(255,247,248,.22);font-weight:800;font-size:13px;min-width:18px}}
    .sptr-main{{flex:1;display:flex;flex-direction:column;gap:3px;min-width:0}}
    .sptr-name{{color:#fff7f8;font-weight:600;font-size:15px}}
    .sptr-say{{color:rgba(255,247,248,.42);font-size:12.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
    .sptr-stars{{display:flex;gap:2px;flex:none}}
    .sptr-num{{color:#ff416d;font-weight:800;font-size:15px;min-width:32px;text-align:right}}
    .sptr-foot{{display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;padding:16px 22px;background:rgba(255,255,255,.02)}}
    .sptr-foot p{{margin:0;color:rgba(255,247,248,.42);font-size:13px;line-height:1.55;max-width:640px}}
    .sptr-cta{{display:inline-block;background:#ff416d;color:#fff;font-weight:700;font-size:14px;padding:11px 22px;border-radius:9999px;text-decoration:none;box-shadow:0 10px 30px rgba(255,65,109,.45);flex:none}}
    .sptr-cta:hover{{background:#ff557c}}
    @media (max-width:620px){{.sptr-say{{display:none}}}}
  </style>
  <div class="sptr-head">
    <div>
      <p class="sptr-eyebrow">SaaSpare ratings</p>
      <h2 id="sptr-h">Cost transparency scores</h2>
      <p class="sptr-lede">We rank {len(d['scores'])} tools on eight things buyers get
      caught by: setup fees, seat minimums, annual-only billing, card-up-front trials
      and seat surcharges. Every tool gets a written verdict.</p>
    </div>
    <a class="sptr-cta" href="{URL}">See the full ranking</a>
  </div>
  <div class="sptr-panel">
    {rows}
    <div class="sptr-foot">
      <p>Editorial scores computed from pricing we verified in {pretty}, not user
      reviews. We don't host user reviews, so we don't publish a user rating.
      Lowest scorer: <strong style="color:rgba(255,247,248,.64)">{worst['vendor']}</strong>,
      {worst['stars']}/5.</p>
    </div>
  </div>
</section>
{END}"""


def inject_home(block):
    html = HOME.read_text(encoding="utf-8")
    if START in html and END in html:
        HOME.write_text(html.split(START)[0] + block + html.split(END)[1],
                        encoding="utf-8")
        return "replaced"
    # Directly after the hero closes. Searching backwards from a later heading
    # walked past the hero and landed the block above it, pushing the hero off
    # the top of the page - so anchor forwards from the hero itself.
    hero = html.find('<section class="hero">')
    if hero == -1:
        return "hero not found - homepage NOT changed"
    close = html.find("</section>", hero)
    if close == -1:
        return "hero not closed - homepage NOT changed"
    at = close + len("</section>")
    HOME.write_text(html[:at] + "\n" + block + "\n" + html[at:], encoding="utf-8")
    return f"inserted after hero (offset {at})"


def main():
    d = json.loads(SCORES.read_text(encoding="utf-8"))
    vd = json.loads(VERDICTS.read_text(encoding="utf-8"))

    missing = [s["tool"] for s in d["scores"] if s["tool"] not in vd["verdicts"]]
    if missing:
        raise SystemExit(
            "No hand-written verdict for: " + ", ".join(missing) +
            "\nAdd them to data/editorial_verdicts.json. This build refuses to "
            "auto-generate verdict text - templated verdicts are the thin-content "
            "pattern we are recovering from.")

    PAGE.write_text(build_page(d, vd), encoding="utf-8")
    print(f"wrote {PAGE.relative_to(ROOT)} ({PAGE.stat().st_size:,} bytes), "
          f"{len(d['scores'])} verdicts")
    print("homepage:", inject_home(build_home_block(d, vd)))


if __name__ == "__main__":
    main()
