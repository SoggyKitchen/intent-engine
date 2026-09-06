"""
Build the Cost Transparency Scores experience: ranked reviews page + homepage block.

Design follows the two mockups Kaylan supplied on 2026-09-06: hero with a badge
pill, split white/pink headline, dual CTA, a three-item proof row and a floating
dashboard card; then a filterable ranked list with a category sidebar.

Two elements of those mockups are deliberately NOT reproduced, and what replaced
them:

  "4.8 (1.2k reviews)"          -> "8 of 10 criteria passed"
  "Trusted by 10,000+ teams"    -> the real corpus line: tools, plans, date

We host no user reviews and have no traffic, so a review count and a
social-proof number would both be invented. Everything else - layout,
composition, palette, the score-out-of-ten headline, the breakdown bars, the
trend chart, the sidebar - is matched.

Tool logos are generated letter-marks rather than fetched brand assets. Two
reasons: hotlinking third-party logos into a "trusted by" style row implies an
endorsement that does not exist, and remote logo services break. The marks are
tinted per category so the list still reads as varied.

Schema: Article only. Per-tool Review nodes live on each tool's own page via
inject_tool_reviews.py, because Google rejects Review nested under a
multi-item Article. No aggregateRating anywhere.
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORES = ROOT / "data" / "transparency_scores.json"
VERDICTS = ROOT / "data" / "editorial_verdicts.json"
SEED = ROOT / "data" / "pricing_seed.json"
PAGE = ROOT / "site" / "pages" / "saas-pricing-transparency-scores-2026.html"
HOME = ROOT / "site" / "index.html"
URL = "https://saaspare.org/pages/saas-pricing-transparency-scores-2026"

START = "<!-- sp-transparency-block:start -->"
END = "<!-- sp-transparency-block:end -->"

TITLE = "SaaS Pricing Transparency Scores 2026: 41 Tools Ranked on What They Hide"
DESC = ("We ranked 41 B2B SaaS vendors on ten things buyers get caught by: setup fees, "
        "seat minimums, annual-only billing, card-up-front trials, metered charges and "
        "intro-price cliffs. Editorial scores from verified pricing, with a written "
        "verdict on every tool.")

CAT = {"crm": "CRM", "seo": "SEO tools", "project-mgmt": "Project management",
       "dev-tools": "Development", "security": "Security", "finance": "Finance",
       "ecommerce": "E-commerce", "collaboration": "Collaboration",
       "productivity": "Productivity", "marketing": "Marketing",
       "support": "Support", "design": "Design", "publishing": "Publishing"}

# Per-category accent so a list of letter-marks still reads as varied.
TINT = {"crm": "#ff416d", "seo": "#ff7a9a", "project-mgmt": "#7c9cff",
        "dev-tools": "#36e6a1", "security": "#4fd1c5", "finance": "#f5b942",
        "ecommerce": "#c084fc", "collaboration": "#60a5fa",
        "productivity": "#f472b6", "marketing": "#fb923c",
        "support": "#34d399", "design": "#a78bfa", "publishing": "#facc15"}


def e(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def stars(v, size=14):
    out = []
    for i in range(1, 6):
        f = ("var(--pink)" if v >= i else
             "url(#sp-half)" if v >= i - 0.5 else "rgba(255,247,248,.16)")
        out.append(f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="{f}"'
                   f' aria-hidden="true"><path d="M12 2l3 6.9 7.5.8-5.6 5 1.6 7.3L12 18.3'
                   f' 5.5 22l1.6-7.3-5.6-5 7.5-.8z"/></svg>')
    return "".join(out)


DEFS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
        '<linearGradient id="sp-half"><stop offset="50%" stop-color="var(--pink)"/>'
        '<stop offset="50%" stop-color="rgba(255,247,248,.16)"/></linearGradient>'
        "</defs></svg>")


def mark(vendor, cat, size=40):
    """Letter-mark tile. Two initials where the name has two words."""
    parts = re.split(r"[\s.\-]+", vendor)
    ini = (parts[0][0] + (parts[1][0] if len(parts) > 1 and parts[1] else "")).upper()
    c = TINT.get(cat, "#ff416d")
    return (f'<span class="rv-mark" style="--m:{c};width:{size}px;height:{size}px;'
            f'font-size:{max(12, size // 2 - 3)}px">{e(ini)}</span>')


def tags(s, labels):
    """Up to three honest badges, derived from the score itself."""
    t = [CAT.get(s["category"], s["category"] or "")]
    if s["points"] == s["max_points"]:
        t.append("Full marks")
    elif s["score10"] >= 9:
        t.append("Top rated")
    fails = [labels[k] for k, v in s["criteria"].items() if v == 0]
    if fails:
        t.append(fails[0])
    elif s["criteria"].get("free_tier") == 2:
        t.append("Free tier")
    return "".join(f'<span class="rv-tag">{e(x)}</span>' for x in t[:3])


def hero(meta, n_tools, n_plans, pretty, eyebrow, h1a, h1b, sub, cta1, scores, labels):
    top = scores[:5]
    rows = "".join(
        f'<div class="dash-row"><span class="dash-n">{i}</span>'
        f'{mark(s["vendor"], s["category"], 22)}'
        f'<span class="dash-name">{e(s["vendor"])}'
        f'<em>{e(CAT.get(s["category"], ""))}</em></span>'
        f'<span class="dash-score">{s["score10"]}<i>/10</i></span>'
        f'<span class="dash-stars">{stars(s["stars"], 11)}</span></div>'
        for i, s in enumerate(top, 1))

    # Breakdown bars: the share of all 41 tools passing each criterion cleanly.
    bars = ""
    for c in meta["criteria"][:4]:
        k = c["key"]
        pct = round(sum(1 for s in scores if s["criteria"].get(k) == 2) / len(scores) * 100)
        bars += (f'<div class="bar-row"><span>{e(c["label"])}</span>'
                 f'<div class="bar"><i style="width:{pct}%"></i></div>'
                 f'<b>{pct}%</b></div>')

    # Trend: distribution of scores, drawn as a sparkline. Real data, not decor.
    buckets = [sum(1 for s in scores if lo <= s["score10"] < lo + 1)
               for lo in range(5, 11)]
    mx = max(buckets) or 1
    pts = " ".join(f"{i * 40},{46 - (b / mx) * 38:.0f}" for i, b in enumerate(buckets))

    return f"""<section class="rv-hero">
  <div class="rv-hero-l">
    <p class="rv-badge"><span></span>{e(eyebrow)}</p>
    <h1>{e(h1a)}<br><span>{e(h1b)}</span></h1>
    <p class="rv-sub">{e(sub)}</p>
    <div class="rv-cta">
      <a class="rv-btn-a" href="#ranking">{e(cta1)} <span>&rarr;</span></a>
      <a class="rv-btn-b" href="#how">How We Score</a>
    </div>
    <div class="rv-proof">
      <div><b>Real pricing data</b><span>Read from vendor pages</span></div>
      <div><b>No paid placements</b><span>Nobody can buy a score</span></div>
      <div><b>Recomputed nightly</b><span>Fix your page, score rises</span></div>
    </div>
  </div>
  <div class="rv-hero-r">
    <div class="dash">
      <div class="dash-head"><span class="dash-logo">S</span>
        <b>SaaS Pricing Transparency Scores</b><span class="dash-yr">2026</span></div>
      <p class="dash-sub">Verified pricing. Computed scores. No user reviews.</p>
      {rows}
    </div>
    <div class="dash-side">
      <div class="panel">
        <b>How the {n_tools} score</b>
        {bars}
      </div>
      <div class="panel">
        <b>Score distribution</b>
        <svg viewBox="0 0 200 50" class="spark" preserveAspectRatio="none">
          <polyline points="{pts}" fill="none" stroke="var(--pink)" stroke-width="2"
            stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span class="panel-x">5<i>/10</i> &rarr; 10<i>/10</i></span>
      </div>
    </div>
  </div>
</section>
<p class="rv-corpus">{n_tools} tools &middot; {n_plans} plans &middot; every figure read from
the vendor&rsquo;s own pricing page on {e(pretty)}</p>"""


def review_row(s, v, rank, labels):
    passed = sum(1 for x in s["criteria"].values() if x == 2)
    pills = "".join(
        f'<span class="rv-pill rv-{ {2: "ok", 1: "mid", 0: "bad"}[x] }">'
        f'{ {2: "&#10003;", 1: "~", 0: "&#10007;"}[x] } {e(labels[k])}</span>'
        for k, x in s["criteria"].items())
    return f"""  <article class="rv-row" id="{s['tool']}" data-cat="{e(s['category'] or '')}"
    data-name="{e(s['vendor'].lower())}" data-score="{s['score10']}" data-rank="{rank}">
    <div class="rv-rank">#{rank}</div>
    {mark(s['vendor'], s['category'])}
    <div class="rv-main">
      <div class="rv-title"><h3>{e(s['vendor'])}</h3>
        <span>{e(CAT.get(s['category'], s['category'] or ''))}</span></div>
      <p class="rv-quote">&ldquo;{e(v['headline'])}. {e(v['body'])}&rdquo;</p>
      <div class="rv-tags">{tags(s, labels)}</div>
      <details class="rv-more"><summary>Full verdict and scoring</summary>
        <div class="rv-cols">
          <p><b>Best for</b>{e(v['best_for'])}</p>
          <p class="w"><b>Watch for</b>{e(v['watch_for'])}</p>
        </div>
        <div class="rv-pills">{pills}</div>
        <a class="rv-src" href="{e(s['source_url'])}" rel="nofollow noopener"
           target="_blank">Vendor pricing page &rarr;</a>
      </details>
    </div>
    <div class="rv-score">
      <b>{s['score10']}<i>/10</i></b>
      <span class="rv-stars">{stars(s['stars'])}</span>
      <em>{passed} of {len(s['criteria'])} criteria passed</em>
    </div>
  </article>
"""


def build_page(d, vd, seed):
    scores, meta = d["scores"], d["_meta"]
    labels = {c["key"]: c["label"] for c in meta["criteria"]}
    V = vd["verdicts"]
    verified = meta["pricing_verified_on"]
    pretty = date.fromisoformat(verified).strftime("%d %B %Y").lstrip("0")
    n_plans = sum(len(t["plans"]) for t in seed["tools"])

    counts = {}
    for s in scores:
        counts[s["category"]] = counts.get(s["category"], 0) + 1
    side = (f'<button class="rv-cat is-on" data-f="all">All Categories'
            f'<i>{len(scores)}</i></button>')
    side += "".join(
        f'<button class="rv-cat" data-f="{e(c)}">{e(CAT.get(c, c))}<i>{n}</i></button>'
        for c, n in sorted(counts.items(), key=lambda x: -x[1]))

    rows = "".join(review_row(s, V[s["tool"]], i, labels)
                   for i, s in enumerate(scores, 1))

    rubric = "".join(
        f'<div class="how-c"><b>{e(c["label"])}</b><span>{e(c["test"])}</span></div>'
        for c in meta["criteria"])

    article = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": TITLE, "description": DESC, "url": URL,
        "datePublished": verified, "dateModified": verified,
        "author": {"@type": "Person", "name": "Kaylan von Papen",
                   "url": "https://saaspare.org/authors/kaylan-von-papen"},
        "publisher": {"@type": "Organization", "name": "SaaSpare",
                      "url": "https://saaspare.org/",
                      "@id": "https://saaspare.org/#organization"},
    }
    ld = ('<script type="application/ld+json">\n'
          + json.dumps(article, indent=2, ensure_ascii=False) + "\n</script>")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(TITLE)}</title>
<meta name="description" content="{e(DESC)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="{URL}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="apple-touch-icon" sizes="512x512" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#07070d">
<meta property="og:type" content="article">
<meta property="og:url" content="{URL}">
<meta property="og:title" content="{e(TITLE)}">
<meta property="og:description" content="{e(DESC)}">
<meta property="og:image" content="https://saaspare.org/og/default.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(TITLE)}">
<meta name="twitter:description" content="{e(DESC)}">
<meta name="twitter:image" content="https://saaspare.org/og/default.svg">
<link rel="stylesheet" href="/assets/saaspare-v2.css">
<link rel="stylesheet" href="/assets/saaspare-ui.css">
<link rel="stylesheet" href="/assets/motion.css">
{ld}
<style>{CSS}</style>
</head>
<body style="background:#050407;color:rgba(255,248,245,.88)">
{DEFS}
<main class="rv-wrap">
{hero(meta, len(scores), n_plans, pretty, "REAL DATA. REAL SCORES. NO BIAS.",
      "SaaS Pricing Transparency", "Scores 2026",
      "We read every vendor's pricing page and score what they publish, what they "
      "bury and what they charge you later. Ten tests, one number, a written verdict "
      "on all " + str(len(scores)) + " tools.",
      "Explore the Rankings", scores, labels)}

  <section class="rv-list" id="ranking">
    <aside class="rv-side">
      <input class="rv-search" type="search" placeholder="Search for a tool..."
             aria-label="Search tools">
      <p class="rv-side-h">Filter by category</p>
      {side}
    </aside>
    <div class="rv-body">
      <div class="rv-bar">
        <div><h2>All Reviews</h2><p><span id="rv-count">{len(scores)}</span> tools</p></div>
        <label class="rv-sort">Sort by
          <select id="rv-sort">
            <option value="score">Highest Transparency Score</option>
            <option value="low">Lowest Transparency Score</option>
            <option value="az">Name A&ndash;Z</option>
          </select>
        </label>
      </div>
      <div id="rv-rows">
{rows}      </div>
      <p class="rv-empty" id="rv-empty" hidden>No tools match that filter.</p>
    </div>
  </section>

  <section class="rv-how" id="how">
    <h2>How we score</h2>
    <p class="rv-how-sub">Ten tests, two points each, twenty points total, reported out
    of ten. Nothing weighted, nothing subjective. A vendor who fixes their pricing page
    scores higher on the next run automatically.</p>
    <div class="how-grid">{rubric}</div>
  </section>

  <p class="rv-method">
    <strong>What this is and isn&rsquo;t.</strong> These are editorial scores published by
    SaaSpare, not ratings submitted by users. We host no user reviews, so we publish no
    user rating, and we do not republish other sites&rsquo; review scores as our own. The
    score measures pricing transparency only, not whether the software is good. Inputs
    come from <a href="/pages/saas-hidden-costs-2026">our verified hidden-costs data</a>
    and vendor pricing pages read on {e(pretty)}. Method:
    <a href="/methodology">methodology</a> &middot;
    <a href="/corrections">corrections policy</a>. Think a score is wrong?
    <a href="/contact">Tell us</a> and we will recheck and log it.
    By <a href="/authors/kaylan-von-papen">Kaylan von Papen</a>.
  </p>
</main>
<script>{JS}</script>
</body>
</html>
"""


CSS = """
:root{--m:#ff416d}
.rv-wrap{max-width:1240px;margin:0 auto;padding:32px 20px 96px}
.rv-hero{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:48px;align-items:center;padding:28px 0 8px}
.rv-badge{display:inline-flex;align-items:center;gap:9px;border:1px solid var(--line-pink);border-radius:var(--r-full);padding:7px 16px;color:var(--pink);font-size:11.5px;font-weight:700;letter-spacing:.12em;margin:0 0 26px;background:rgba(255,65,109,.06)}
.rv-badge span{width:6px;height:6px;border-radius:50%;background:var(--pink);box-shadow:0 0 10px var(--pink)}
.rv-hero h1{font-size:clamp(38px,5.2vw,64px);line-height:1.02;letter-spacing:-.035em;font-weight:800;margin:0 0 20px;color:var(--ink)}
.rv-hero h1 span{color:var(--pink)}
.rv-sub{color:var(--ink-3);font-size:17px;line-height:1.65;max-width:520px;margin:0 0 30px}
.rv-cta{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:34px}
.rv-btn-a{display:inline-flex;align-items:center;gap:9px;background:var(--pink);color:#fff;font-weight:700;font-size:15px;padding:14px 26px;border-radius:var(--r-full);text-decoration:none;box-shadow:var(--shadow-cta);transition:background .18s,transform .18s}
.rv-btn-a:hover{background:var(--pink-soft);transform:translateY(-1px)}
.rv-btn-b{display:inline-flex;align-items:center;padding:14px 24px;border:1px solid var(--line);border-radius:var(--r-full);color:var(--ink-2);font-weight:600;font-size:15px;text-decoration:none;transition:border-color .18s}
.rv-btn-b:hover{border-color:var(--line-pink);color:var(--ink)}
.rv-proof{display:flex;flex-wrap:wrap;gap:26px}
.rv-proof div{display:flex;flex-direction:column;gap:2px;padding-left:13px;border-left:2px solid var(--line-pink)}
.rv-proof b{color:var(--ink);font-size:13.5px}
.rv-proof span{color:var(--ink-4);font-size:12px}
.rv-hero-r{display:grid;gap:14px;grid-template-columns:1.35fr .85fr;align-items:start}
.dash{grid-column:1/-1;background:linear-gradient(180deg,rgba(24,10,18,.96),rgba(10,6,10,.98));border:1px solid var(--line-pink);border-radius:var(--r-lg);padding:18px;box-shadow:var(--shadow-pink)}
.dash-head{display:flex;align-items:center;gap:9px;margin-bottom:4px}
.dash-logo{width:20px;height:20px;border-radius:6px;background:var(--pink);color:#fff;font-weight:800;font-size:12px;display:grid;place-items:center}
.dash-head b{color:var(--ink);font-size:14px}
.dash-yr{margin-left:auto;font-size:11px;color:var(--pink);border:1px solid var(--line-pink);border-radius:var(--r-full);padding:2px 9px}
.dash-sub{color:var(--ink-4);font-size:11.5px;margin:0 0 12px}
.dash-row{display:flex;align-items:center;gap:10px;padding:9px 0;border-top:1px solid var(--line-soft)}
.dash-n{color:var(--ink-5);font-size:11px;font-weight:800;min-width:12px}
.dash-name{flex:1;color:var(--ink);font-size:13px;font-weight:600;display:flex;flex-direction:column;line-height:1.25;min-width:0}
.dash-name em{color:var(--ink-4);font-size:10.5px;font-style:normal}
.dash-score{color:var(--pink);font-weight:800;font-size:14px}
.dash-score i{color:var(--ink-5);font-size:10px;font-style:normal}
.dash-stars{display:flex;gap:1px}
.panel{background:var(--glass);border:1px solid var(--line);border-radius:var(--r-md);padding:14px}
.panel>b{display:block;color:var(--ink);font-size:12px;margin-bottom:10px}
.bar-row{display:grid;grid-template-columns:1fr 52px 30px;gap:7px;align-items:center;margin-bottom:7px}
.bar-row span{color:var(--ink-4);font-size:10.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bar{height:5px;border-radius:3px;background:rgba(255,255,255,.07);overflow:hidden}
.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--pink-deep),var(--pink))}
.bar-row b{color:var(--ink-2);font-size:10.5px;text-align:right}
.spark{width:100%;height:46px;display:block}
.panel-x{color:var(--ink-5);font-size:10px}
.panel-x i{font-style:normal}
.rv-corpus{text-align:center;color:var(--ink-4);font-size:13px;margin:26px 0 0;padding-bottom:8px}
.rv-list{display:grid;grid-template-columns:236px minmax(0,1fr);gap:26px;margin-top:56px;scroll-margin-top:80px}
.rv-side{position:sticky;top:88px;align-self:start}
.rv-search{width:100%;background:var(--bg-rise);border:1px solid var(--line);border-radius:var(--r-md);padding:11px 14px;color:var(--ink);font-size:13.5px;font-family:inherit;margin-bottom:20px}
.rv-search:focus{outline:none;border-color:var(--line-pink)}
.rv-side-h{color:var(--ink-4);font-size:11px;text-transform:uppercase;letter-spacing:.08em;margin:0 0 10px}
.rv-cat{display:flex;width:100%;align-items:center;justify-content:space-between;gap:8px;background:none;border:0;border-left:2px solid transparent;padding:9px 12px;color:var(--ink-3);font-size:13.5px;font-family:inherit;cursor:pointer;border-radius:0 var(--r-sm) var(--r-sm) 0;text-align:left;transition:background .15s,color .15s}
.rv-cat:hover{background:rgba(255,255,255,.03);color:var(--ink)}
.rv-cat.is-on{background:rgba(255,65,109,.09);border-left-color:var(--pink);color:var(--ink)}
.rv-cat i{color:var(--ink-5);font-size:12px;font-style:normal}
.rv-cat.is-on i{color:var(--pink)}
.rv-bar{display:flex;flex-wrap:wrap;gap:14px;align-items:flex-end;justify-content:space-between;margin-bottom:18px}
.rv-bar h2{margin:0;font-size:26px;color:var(--ink);letter-spacing:-.02em}
.rv-bar p{margin:3px 0 0;color:var(--ink-4);font-size:13px}
.rv-sort{color:var(--ink-4);font-size:12.5px;display:flex;align-items:center;gap:9px}
.rv-sort select{background:var(--bg-rise);border:1px solid var(--line);border-radius:var(--r-sm);color:var(--ink-2);padding:9px 12px;font-family:inherit;font-size:13px}
.rv-row{display:grid;grid-template-columns:34px 40px minmax(0,1fr) 150px;gap:14px;align-items:start;background:var(--glass);border:1px solid var(--line);border-radius:var(--r-md);padding:18px 20px;margin-bottom:12px;box-shadow:var(--shadow-card);scroll-margin-top:90px;transition:border-color .18s,transform .18s}
.rv-row:hover{border-color:var(--line-pink);transform:translateY(-1px)}
.rv-rank{color:var(--ink-5);font-weight:800;font-size:13px;padding-top:9px}
.rv-mark{display:grid;place-items:center;border-radius:11px;background:color-mix(in srgb,var(--m) 16%,transparent);border:1px solid color-mix(in srgb,var(--m) 38%,transparent);color:var(--m);font-weight:800;letter-spacing:-.02em;flex:none}
.rv-title{display:flex;align-items:baseline;gap:9px;flex-wrap:wrap}
.rv-title h3{margin:0;font-size:17px;color:var(--ink)}
.rv-title span{color:var(--ink-4);font-size:12px}
.rv-quote{margin:7px 0 10px;color:var(--ink-2);font-size:14.5px;line-height:1.65}
.rv-tags{display:flex;flex-wrap:wrap;gap:6px}
.rv-tag{font-size:11px;padding:4px 10px;border-radius:var(--r-full);background:rgba(255,255,255,.05);border:1px solid var(--line);color:var(--ink-3)}
.rv-score{text-align:right;display:flex;flex-direction:column;align-items:flex-end;gap:5px;padding-top:4px}
.rv-score b{color:var(--pink);font-size:25px;font-weight:800;line-height:1}
.rv-score b i{color:var(--ink-5);font-size:12px;font-style:normal;font-weight:600}
.rv-stars{display:flex;gap:2px}
.rv-score em{color:var(--ink-4);font-size:11px;font-style:normal;text-align:right}
.rv-more{margin-top:12px}
.rv-more summary{cursor:pointer;color:var(--ink-4);font-size:12.5px;list-style:none}
.rv-more summary::-webkit-details-marker{display:none}
.rv-more summary::before{content:"+ ";color:var(--pink)}
.rv-more[open] summary::before{content:"\\2013 "}
.rv-cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px;margin:12px 0}
.rv-cols p{margin:0;padding:11px 13px;background:rgba(255,255,255,.03);border-radius:var(--r-sm);border-left:2px solid var(--green);color:var(--ink-3);font-size:13px;line-height:1.55}
.rv-cols p.w{border-left-color:var(--amber)}
.rv-cols b{display:block;color:var(--ink-4);font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;margin-bottom:3px}
.rv-pills{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:11px}
.rv-pill{font-size:11px;padding:4px 9px;border-radius:var(--r-full);border:1px solid var(--line);color:var(--ink-4);white-space:nowrap}
.rv-ok{color:var(--green);border-color:rgba(54,230,161,.28);background:var(--green-soft)}
.rv-mid{color:var(--amber);border-color:rgba(245,185,66,.28);background:rgba(245,185,66,.08)}
.rv-bad{color:var(--pink);border-color:var(--line-pink);background:rgba(255,65,109,.08)}
.rv-src{color:var(--ink-4);font-size:12.5px;text-decoration:none}
.rv-src:hover{color:var(--pink)}
.rv-empty{color:var(--ink-4);text-align:center;padding:36px 0}
.rv-how{margin-top:64px;scroll-margin-top:80px}
.rv-how h2{font-size:26px;color:var(--ink);margin:0 0 8px;letter-spacing:-.02em}
.rv-how-sub{color:var(--ink-4);font-size:14px;line-height:1.6;max-width:720px;margin:0 0 22px}
.how-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}
.how-c{background:var(--glass);border:1px solid var(--line);border-radius:var(--r-md);padding:16px 18px}
.how-c b{display:block;color:var(--ink);font-size:14px;margin-bottom:5px}
.how-c span{color:var(--ink-4);font-size:12.5px;line-height:1.55}
.rv-method{margin-top:56px;padding-top:24px;border-top:1px solid var(--line);color:var(--ink-4);font-size:13.5px;line-height:1.75}
.rv-method a{color:var(--ink-3)}
@media(max-width:1080px){.rv-hero{grid-template-columns:1fr;gap:34px}.rv-hero-r{grid-template-columns:1fr 1fr}}
@media(max-width:860px){.rv-list{grid-template-columns:1fr}.rv-side{position:static}
  .rv-row{grid-template-columns:28px 36px minmax(0,1fr)}
  .rv-score{grid-column:1/-1;flex-direction:row;align-items:center;justify-content:flex-start;gap:12px;text-align:left;padding-top:10px}
  .rv-score em{text-align:left}}
@media(max-width:560px){.rv-hero-r{grid-template-columns:1fr}}
"""

JS = """
(function(){
  var rows=[].slice.call(document.querySelectorAll('.rv-row')),
      box=document.getElementById('rv-rows'),
      cnt=document.getElementById('rv-count'),
      empty=document.getElementById('rv-empty'),
      search=document.querySelector('.rv-search'),
      sort=document.getElementById('rv-sort'),
      cats=[].slice.call(document.querySelectorAll('.rv-cat')),
      cat='all', q='';
  function apply(){
    var shown=0;
    rows.forEach(function(r){
      var okC = cat==='all' || r.dataset.cat===cat,
          okQ = !q || r.dataset.name.indexOf(q)>-1;
      r.hidden = !(okC&&okQ);
      if(okC&&okQ) shown++;
    });
    cnt.textContent=shown; empty.hidden=shown>0;
  }
  function order(){
    var m=sort.value, s=rows.slice();
    s.sort(function(a,b){
      if(m==='az') return a.dataset.name.localeCompare(b.dataset.name);
      var d=parseFloat(b.dataset.score)-parseFloat(a.dataset.score);
      if(m==='low') d=-d;
      return d || (+a.dataset.rank)-(+b.dataset.rank);
    });
    s.forEach(function(r){box.appendChild(r);});
  }
  cats.forEach(function(c){c.addEventListener('click',function(){
    cats.forEach(function(x){x.classList.remove('is-on');});
    c.classList.add('is-on'); cat=c.dataset.f; apply();
  });});
  search.addEventListener('input',function(){q=this.value.trim().toLowerCase();apply();});
  sort.addEventListener('change',order);
})();
"""


def build_home_block(d, vd, seed):
    scores, meta = d["scores"], d["_meta"]
    labels = {c["key"]: c["label"] for c in meta["criteria"]}
    verified = meta["pricing_verified_on"]
    pretty = date.fromisoformat(verified).strftime("%B %Y")
    n_plans = sum(len(t["plans"]) for t in seed["tools"])
    V = vd["verdicts"]
    top = scores[:5]

    rows = "".join(
        f'<a class="hx-row" href="{URL}#{s["tool"]}">'
        f'<span class="hx-n">{i}</span>{mark(s["vendor"], s["category"], 26)}'
        f'<span class="hx-name">{e(s["vendor"])}'
        f'<em>{e(V[s["tool"]]["headline"])}</em></span>'
        f'<span class="hx-stars">{stars(s["stars"], 12)}</span>'
        f'<span class="hx-sc">{s["score10"]}<i>/10</i></span></a>'
        for i, s in enumerate(top, 1))

    bars = ""
    for c in meta["criteria"][:4]:
        k = c["key"]
        pct = round(sum(1 for s in scores if s["criteria"].get(k) == 2) / len(scores) * 100)
        bars += (f'<div class="hx-bar"><span>{e(c["label"])}</span>'
                 f'<div class="hx-t"><i style="width:{pct}%"></i></div><b>{pct}%</b></div>')

    worst = scores[-1]
    return f"""{START}
<section class="hx" aria-labelledby="hx-h">
  {DEFS}
  <style>
    .hx{{padding:7.5rem clamp(1.25rem,4vw,3rem) 4.5rem;max-width:1240px;margin:0 auto;position:relative;z-index:2}}
    .hx-grid{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.02fr);gap:46px;align-items:center}}
    .hx-badge{{display:inline-flex;align-items:center;gap:9px;border:1px solid rgba(255,75,115,.3);border-radius:9999px;padding:7px 16px;color:#ff416d;font-size:11.5px;font-weight:700;letter-spacing:.12em;margin:0 0 24px;background:rgba(255,65,109,.06)}}
    .hx-badge s{{width:6px;height:6px;border-radius:50%;background:#ff416d;text-decoration:none;box-shadow:0 0 10px #ff416d}}
    .hx h2{{font-size:clamp(34px,4.6vw,58px);line-height:1.02;letter-spacing:-.035em;font-weight:800;margin:0 0 18px;color:#fff7f8}}
    .hx h2 span{{color:#ff416d}}
    .hx-sub{{color:rgba(255,247,248,.64);font-size:16.5px;line-height:1.65;max-width:500px;margin:0 0 28px}}
    .hx-cta{{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:30px}}
    .hx-a{{display:inline-flex;align-items:center;gap:9px;background:#ff416d;color:#fff;font-weight:700;font-size:15px;padding:14px 26px;border-radius:9999px;text-decoration:none;box-shadow:0 10px 30px rgba(255,65,109,.45)}}
    .hx-a:hover{{background:#ff557c}}
    .hx-b{{display:inline-flex;align-items:center;padding:14px 24px;border:1px solid rgba(255,255,255,.09);border-radius:9999px;color:rgba(255,247,248,.82);font-weight:600;font-size:15px;text-decoration:none}}
    .hx-b:hover{{border-color:rgba(255,75,115,.3);color:#fff7f8}}
    .hx-proof{{display:flex;flex-wrap:wrap;gap:24px}}
    .hx-proof div{{display:flex;flex-direction:column;gap:2px;padding-left:13px;border-left:2px solid rgba(255,75,115,.3)}}
    .hx-proof b{{color:#fff7f8;font-size:13.5px}}
    .hx-proof i{{color:rgba(255,247,248,.42);font-size:12px;font-style:normal}}
    .hx-card{{background:linear-gradient(180deg,rgba(24,10,18,.96),rgba(10,6,10,.98));border:1px solid rgba(255,75,115,.25);border-radius:20px;padding:18px;box-shadow:0 30px 90px rgba(255,45,92,.16),inset 0 1px 0 rgba(255,255,255,.06);margin-bottom:12px}}
    .hx-head{{display:flex;align-items:center;gap:9px;margin-bottom:12px}}
    .hx-logo{{width:20px;height:20px;border-radius:6px;background:#ff416d;color:#fff;font-weight:800;font-size:12px;display:grid;place-items:center}}
    .hx-head b{{color:#fff7f8;font-size:14px}}
    .hx-head s{{margin-left:auto;font-size:11px;color:#ff416d;border:1px solid rgba(255,75,115,.3);border-radius:9999px;padding:2px 9px;text-decoration:none}}
    .hx-row{{display:flex;align-items:center;gap:10px;padding:10px 0;border-top:1px solid rgba(255,255,255,.05);text-decoration:none;transition:background .16s}}
    .hx-row:hover{{background:rgba(255,75,115,.06)}}
    .hx-n{{color:rgba(255,247,248,.22);font-size:11px;font-weight:800;min-width:12px}}
    .hx-name{{flex:1;min-width:0;display:flex;flex-direction:column;gap:1px;color:#fff7f8;font-size:13.5px;font-weight:600}}
    .hx-name em{{color:rgba(255,247,248,.42);font-size:11.5px;font-style:normal;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
    .hx-stars{{display:flex;gap:1px;flex:none}}
    .hx-sc{{color:#ff416d;font-weight:800;font-size:15px;min-width:44px;text-align:right}}
    .hx-sc i{{color:rgba(255,247,248,.22);font-size:10px;font-style:normal}}
    .hx-panel{{background:linear-gradient(180deg,rgba(255,255,255,.055),rgba(255,255,255,.025));border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:14px}}
    .hx-panel>b{{display:block;color:#fff7f8;font-size:12px;margin-bottom:10px}}
    .hx-bar{{display:grid;grid-template-columns:1fr 54px 30px;gap:7px;align-items:center;margin-bottom:7px}}
    .hx-bar span{{color:rgba(255,247,248,.42);font-size:10.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
    .hx-t{{height:5px;border-radius:3px;background:rgba(255,255,255,.07);overflow:hidden}}
    .hx-t i{{display:block;height:100%;background:linear-gradient(90deg,#c92950,#ff416d)}}
    .hx-bar b{{color:rgba(255,247,248,.82);font-size:10.5px;text-align:right}}
    .hx-foot{{margin:16px 0 0;color:rgba(255,247,248,.42);font-size:12.5px;line-height:1.55}}
    @media(max-width:1080px){{.hx-grid{{grid-template-columns:1fr;gap:32px}}}}
  </style>
  <div class="hx-grid">
    <div>
      <p class="hx-badge"><s></s>TRANSPARENCY. BETTER DECISIONS.</p>
      <h2 id="hx-h">Real SaaS Pricing.<br><span>No Guesswork.</span></h2>
      <p class="hx-sub">We read {len(scores)} vendors&rsquo; pricing pages and score what they
      publish, what they bury and what they charge you later. One number out of ten, and a
      written verdict on every tool.</p>
      <div class="hx-cta">
        <a class="hx-a" href="{URL}">Explore Rankings <span>&rarr;</span></a>
        <a class="hx-b" href="{URL}#how">How It Works</a>
      </div>
      <div class="hx-proof">
        <div><b>Real pricing data</b><i>From vendor pages</i></div>
        <div><b>No paid placements</b><i>Nobody can buy a score</i></div>
        <div><b>Recomputed nightly</b><i>Fix your page, score rises</i></div>
      </div>
    </div>
    <div>
      <div class="hx-card">
        <div class="hx-head"><span class="hx-logo">S</span>
          <b>SaaS Pricing Transparency Scores</b><s>2026</s></div>
        {rows}
      </div>
      <div class="hx-panel">
        <b>How the {len(scores)} score</b>
        {bars}
      </div>
      <p class="hx-foot">{len(scores)} tools &middot; {n_plans} plans &middot; verified
      {e(pretty)}. Editorial scores, not user reviews &mdash; we host none, so we publish
      no user rating. Lowest scorer: <strong style="color:rgba(255,247,248,.64)">
      {e(worst['vendor'])}</strong>, {worst['score10']}/10.</p>
    </div>
  </div>
</section>
{END}"""


def inject_home(block):
    html = HOME.read_text(encoding="utf-8")
    if START in html and END in html:
        HOME.write_text(html.split(START)[0] + block + html.split(END)[1], encoding="utf-8")
        return "replaced"
    hero_i = html.find('<section class="hero">')
    if hero_i == -1:
        return "hero not found - homepage NOT changed"
    close = html.find("</section>", hero_i)
    if close == -1:
        return "hero not closed - homepage NOT changed"
    at = close + len("</section>")
    HOME.write_text(html[:at] + "\n" + block + "\n" + html[at:], encoding="utf-8")
    return f"inserted after hero (offset {at})"


def main():
    d = json.loads(SCORES.read_text(encoding="utf-8"))
    vd = json.loads(VERDICTS.read_text(encoding="utf-8"))
    seed = json.loads(SEED.read_text(encoding="utf-8"))

    missing = [s["tool"] for s in d["scores"] if s["tool"] not in vd["verdicts"]]
    if missing:
        raise SystemExit(
            "No hand-written verdict for: " + ", ".join(missing) +
            "\nAdd them to data/editorial_verdicts.json. This build refuses to "
            "auto-generate verdict text - templated verdicts are the thin-content "
            "pattern we are recovering from.")

    PAGE.write_text(build_page(d, vd, seed), encoding="utf-8")
    print(f"wrote {PAGE.relative_to(ROOT)} ({PAGE.stat().st_size:,} bytes), "
          f"{len(d['scores'])} verdicts")
    print("homepage:", inject_home(build_home_block(d, vd, seed)))


if __name__ == "__main__":
    main()
