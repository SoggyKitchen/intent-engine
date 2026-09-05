"""
Publish the Cost Transparency Score: a ratings page, plus a homepage block.

The ask was "reviews on the homepage with stars, like the competitor". The
competitor's reviews are fabricated (their owner said so), and Google's
structured-data policy forbids marking up ratings collected elsewhere, so
copying either half of that is a bad trade against a clean record.

This is the version that stands up: a published editorial rating, of the kind
a consumer magazine runs, computed by scripts/compute_transparency_score.py
from pricing we verified ourselves. Stars on the homepage, a full rubric on
the page, and every input auditable.

Schema note: the Review nodes name SaaSpare as the author, which is what
Google's guidance permits for editorial reviews. There is deliberately no
aggregateRating anywhere - we have no user ratings to aggregate, and inventing
one is the exact failure mode this whole rebuild is recovering from.

Idempotent. The homepage block is delimited by HTML comment markers so a
re-run replaces it rather than stacking copies.
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORES = ROOT / "data" / "transparency_scores.json"
PAGE = ROOT / "site" / "pages" / "saas-pricing-transparency-scores-2026.html"
HOME = ROOT / "site" / "index.html"
URL = "https://saaspare.org/pages/saas-pricing-transparency-scores-2026"

START = "<!-- sp-transparency-block:start -->"
END = "<!-- sp-transparency-block:end -->"

TITLE = ("SaaS Pricing Transparency Scores 2026: 15 Tools Rated on What They "
         "Hide")
DESC = ("We scored 15 B2B SaaS vendors on five things buyers actually get caught "
        "by: published prices, setup fees, seat minimums, monthly billing and "
        "free trials. Editorial scores computed from verified pricing, not user "
        "reviews.")


def stars_svg(value, size=18):
    """Five stars, half-star resolution, drawn inline so nothing extra loads."""
    out = []
    for i in range(1, 6):
        if value >= i:
            fill = "var(--pink)"
        elif value >= i - 0.5:
            fill = "url(#sp-half)"
        else:
            fill = "rgba(255,247,248,.18)"
        out.append(
            f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" '
            f'fill="{fill}" aria-hidden="true" style="flex:none">'
            f'<path d="M12 2l3 6.9 7.5.8-5.6 5 1.6 7.3L12 18.3 5.5 22l1.6-7.3'
            f'-5.6-5 7.5-.8z"/></svg>'
        )
    return "".join(out)


DEFS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true">'
        '<defs><linearGradient id="sp-half"><stop offset="50%" stop-color="var(--pink)"/>'
        '<stop offset="50%" stop-color="rgba(255,247,248,.18)"/></linearGradient></defs></svg>')


def card(s, crit_labels):
    wins = [crit_labels[k] for k, v in s["criteria"].items() if v == 2]
    flags = [crit_labels[k] for k, v in s["criteria"].items() if v < 2]
    flag_html = ""
    if flags:
        flag_html = ('<p class="tr-flag">Loses points on: '
                     + ", ".join(f.lower() for f in flags) + "</p>")
    return f"""    <article class="tr-card">
      <div class="tr-card-top">
        <div>
          <h3>{s['vendor']}</h3>
          <p class="tr-cat">{(s['category'] or '').replace('-', ' ')}</p>
        </div>
        <div class="tr-score">{s['stars']}<span>/5</span></div>
      </div>
      <div class="tr-stars" role="img" aria-label="{s['stars']} out of 5">{stars_svg(s['stars'])}</div>
      <p class="tr-pts">{s['points']} of {s['max_points']} points</p>
      <p class="tr-wins">{len(wins)} of 5 criteria passed cleanly.</p>
      {flag_html}
      <a class="tr-src" href="{s['source_url']}" rel="nofollow noopener" target="_blank">Vendor pricing page</a>
    </article>
"""


def build_page(d):
    scores = d["scores"]
    meta = d["_meta"]
    crit = {c["key"]: c["label"] for c in meta["criteria"]}
    verified = meta["pricing_verified_on"]
    pretty = date.fromisoformat(verified).strftime("%d %B %Y").lstrip("0")

    cards = "".join(card(s, crit) for s in scores)

    rubric = "".join(
        f"""      <tr><td><strong>{c['label']}</strong><br>
      <span class="tr-test">{c['test']}</span></td><td>0&ndash;2</td></tr>\n"""
        for c in meta["criteria"]
    )

    table = "".join(
        f"      <tr><td><strong>{s['vendor']}</strong></td>"
        + "".join(
            f'<td class="tr-c tr-c{v}">{v}</td>' for v in s["criteria"].values()
        )
        + f'<td class="tr-total">{s["points"]}</td>'
        + f'<td class="tr-total">{s["stars"]}</td></tr>\n'
        for s in scores
    )

    reviews = [{
        "@type": "Review",
        "itemReviewed": {"@type": "SoftwareApplication", "name": s["vendor"],
                         "applicationCategory": "BusinessApplication"},
        "reviewRating": {"@type": "Rating", "ratingValue": s["stars"],
                         "bestRating": 5, "worstRating": 0},
        "name": f"{s['vendor']} pricing transparency score",
        "author": {"@id": "https://saaspare.org/#organization"},
        "publisher": {"@id": "https://saaspare.org/#organization"},
        "datePublished": verified,
        "reviewBody": (
            f"{s['vendor']} scores {s['points']} of {s['max_points']} on SaaSpare's "
            "pricing transparency rubric: published pricing, absence of mandatory "
            "setup fees, single-seat availability, monthly billing, and try-before-"
            "you-buy. Computed from pricing verified on the vendor's own page."),
    } for s in scores]

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

    css = """
  .tr-wrap{max-width:1160px;margin:0 auto;padding:48px 20px 96px}
  .tr-eyebrow{color:var(--pink);font-weight:600;letter-spacing:.08em;text-transform:uppercase;font-size:12px;margin:0 0 12px}
  .tr-wrap h1{font-size:clamp(28px,4vw,44px);line-height:1.12;margin:0 0 16px;color:var(--ink)}
  .tr-sub{color:var(--ink-3);font-size:18px;line-height:1.6;max-width:780px;margin:0 0 24px}
  .tr-stamp{display:inline-flex;align-items:center;gap:8px;background:var(--glass);border:1px solid var(--line);border-radius:var(--r-full);padding:8px 16px;color:var(--ink-3);font-size:13px;margin-bottom:40px}
  .tr-stamp b{color:var(--green)}
  .tr-callout{background:var(--glass-pink);border:1px solid var(--line-pink);border-radius:var(--r-lg);padding:24px 28px;box-shadow:var(--shadow-pink);margin:0 0 48px}
  .tr-callout h2{margin:0 0 10px;font-size:20px;color:var(--ink)}
  .tr-callout p{margin:0 0 8px;color:var(--ink-2);line-height:1.65}
  .tr-wrap h2.tr-h{font-size:24px;margin:48px 0 8px;color:var(--ink)}
  .tr-note{color:var(--ink-4);font-size:14px;margin:0 0 20px;line-height:1.6;max-width:780px}
  .tr-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
  .tr-card{background:var(--glass);border:1px solid var(--line);border-radius:var(--r-md);padding:20px;box-shadow:var(--shadow-card)}
  .tr-card-top{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
  .tr-card h3{margin:0;font-size:17px;color:var(--ink)}
  .tr-cat{margin:2px 0 0;color:var(--ink-4);font-size:12px;text-transform:capitalize}
  .tr-score{font-size:24px;font-weight:800;color:var(--pink);line-height:1}
  .tr-score span{font-size:13px;color:var(--ink-4);font-weight:600}
  .tr-stars{display:flex;gap:3px;margin:12px 0 8px}
  .tr-pts{margin:0;color:var(--ink-4);font-size:12px}
  .tr-wins{margin:8px 0 0;color:var(--ink-2);font-size:14px;line-height:1.5}
  .tr-flag{margin:6px 0 0;color:var(--amber);font-size:13px;line-height:1.5}
  .tr-src{display:inline-block;margin-top:12px;color:var(--ink-4);font-size:12px}
  .tr-src:hover{color:var(--pink)}
  .tr-scroll{overflow-x:auto;border:1px solid var(--line);border-radius:var(--r-md);background:var(--bg-rise);box-shadow:var(--shadow-card)}
  table.tr{width:100%;border-collapse:collapse;font-size:14px;min-width:680px}
  table.tr th{text-align:left;padding:12px 14px;color:var(--ink-4);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid var(--line)}
  table.tr td{padding:13px 14px;border-bottom:1px solid var(--line-soft);color:var(--ink-2)}
  table.tr tr:last-child td{border-bottom:0}
  .tr-c{text-align:center;font-weight:700}
  .tr-c2{color:var(--green)}
  .tr-c1{color:var(--amber)}
  .tr-c0{color:var(--pink)}
  .tr-total{text-align:center;font-weight:800;color:var(--ink)}
  .tr-test{color:var(--ink-4);font-size:13px}
  .tr-method{margin-top:48px;padding-top:24px;border-top:1px solid var(--line);color:var(--ink-4);font-size:14px;line-height:1.7}
  .tr-method a{color:var(--ink-3)}
"""

    heads = "".join(f"<th>{c['label']}</th>" for c in meta["criteria"])
    best = [s for s in scores if s["points"] == max(x["points"] for x in scores)]
    worst = min(scores, key=lambda x: x["points"])

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
<style>{css}</style>
</head>
<body style="background:#050407;color:rgba(255,248,245,.88)">
{DEFS}
<main class="tr-wrap">
  <p class="tr-eyebrow">Editorial ratings</p>
  <h1>SaaS pricing transparency scores</h1>
  <p class="tr-sub">Not user reviews. This is our own score for one specific
  thing: how straight a vendor's pricing page is with the buyer. Five tests,
  two points each, ten points total. Every point traces back to a price we read
  off the vendor's own page.</p>

  <p class="tr-stamp">Computed from pricing verified <b>{pretty}</b> &middot;
  {len(scores)} vendors &middot; recomputed, never hand-set</p>

  <div class="tr-callout">
    <h2>What the scores say</h2>
    <p><strong>{', '.join(b['vendor'] for b in best)}</strong> score full marks:
    prices published, no setup fee, one seat is fine, pay monthly, try it first.</p>
    <p><strong>{worst['vendor']}</strong> comes last on {worst['points']}/10, held
    back by no free tier or trial and an annual commitment on its top plan.</p>
    <p><strong>HubSpot</strong> loses two points on one thing alone: the required
    onboarding fee, which is
    <a href="/pages/saas-hidden-costs-2026" style="color:#ff416d">$1,500 on Professional
    and $3,500 on Enterprise</a>.</p>
  </div>

  <div class="tr-grid">
{cards}  </div>

  <h2 class="tr-h">How the score is built</h2>
  <p class="tr-note">Five criteria, nothing weighted, nothing subjective. A vendor
  who fixes their pricing page scores higher on the next run automatically.</p>
  <div class="tr-scroll"><table class="tr">
    <thead><tr><th>Criterion</th><th>Points</th></tr></thead>
    <tbody>
{rubric}    </tbody>
  </table></div>

  <h2 class="tr-h">Every score, every criterion</h2>
  <p class="tr-note">Green is a clean pass, amber a partial, pink a fail.</p>
  <div class="tr-scroll"><table class="tr">
    <thead><tr><th>Vendor</th>{heads}<th>Total</th><th>Stars</th></tr></thead>
    <tbody>
{table}    </tbody>
  </table></div>

  <p class="tr-method">
    <strong>What this is and isn't.</strong> These are editorial scores published by
    SaaSpare, not ratings submitted by users. We do not host user reviews, so we do
    not publish a user rating, and we do not republish other sites' review scores as
    if they were ours. The score measures pricing transparency only; it is not a
    verdict on whether the software is good. Inputs come from
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


def build_home_block(d):
    scores = d["scores"][:6]
    verified = d["_meta"]["pricing_verified_on"]
    pretty = date.fromisoformat(verified).strftime("%B %Y")

    rows = "".join(
        f'<a class="sptr-row" href="{URL}">'
        f'<span class="sptr-name">{s["vendor"]}</span>'
        f'<span class="sptr-stars">{stars_svg(s["stars"], 15)}</span>'
        f'<span class="sptr-num">{s["stars"]}</span></a>'
        for s in scores
    )

    return f"""{START}
<section class="sptr" aria-labelledby="sptr-h">
  {DEFS}
  <style>
    .sptr{{padding:4.5rem clamp(1.25rem,4vw,3rem);max-width:1180px;margin:0 auto}}
    .sptr-head{{display:flex;flex-wrap:wrap;gap:20px;justify-content:space-between;align-items:flex-end;margin-bottom:28px}}
    .sptr-eyebrow{{color:#ff416d;font-weight:600;letter-spacing:.08em;text-transform:uppercase;font-size:12px;margin:0 0 8px}}
    .sptr h2{{font-size:clamp(26px,3vw,38px);line-height:1.1;margin:0;color:#fff7f8;font-weight:800;letter-spacing:-.02em}}
    .sptr-lede{{color:rgba(255,247,248,.64);margin:10px 0 0;max-width:620px;line-height:1.6}}
    .sptr-panel{{background:linear-gradient(180deg,rgba(255,255,255,.055),rgba(255,255,255,.025));border:1px solid rgba(255,255,255,.09);border-radius:20px;box-shadow:0 24px 80px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.08);overflow:hidden}}
    .sptr-row{{display:flex;align-items:center;gap:16px;padding:16px 22px;border-bottom:1px solid rgba(255,255,255,.05);text-decoration:none;transition:background .18s}}
    .sptr-row:last-child{{border-bottom:0}}
    .sptr-row:hover{{background:rgba(255,75,115,.06)}}
    .sptr-name{{flex:1;color:#fff7f8;font-weight:600;font-size:15px}}
    .sptr-stars{{display:flex;gap:2px}}
    .sptr-num{{color:#ff416d;font-weight:800;font-size:15px;min-width:34px;text-align:right}}
    .sptr-foot{{display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;padding:16px 22px;background:rgba(255,255,255,.02)}}
    .sptr-foot p{{margin:0;color:rgba(255,247,248,.42);font-size:13px;line-height:1.5}}
    .sptr-cta{{display:inline-block;background:#ff416d;color:#fff;font-weight:700;font-size:14px;padding:10px 20px;border-radius:9999px;text-decoration:none;box-shadow:0 10px 30px rgba(255,65,109,.45)}}
    .sptr-cta:hover{{background:#ff557c}}
  </style>
  <div class="sptr-head">
    <div>
      <p class="sptr-eyebrow">SaaSpare ratings</p>
      <h2 id="sptr-h">Cost transparency scores</h2>
      <p class="sptr-lede">Our editorial rating of how straight each vendor's pricing
      page is with you: published prices, no surprise setup fee, no seat minimum,
      monthly billing, and a way to try it first.</p>
    </div>
    <a class="sptr-cta" href="{URL}">See all {len(d['scores'])} scores</a>
  </div>
  <div class="sptr-panel">
    {rows}
    <div class="sptr-foot">
      <p>Computed from pricing we verified in {pretty}, not user reviews.
      We don't host user reviews, so we don't publish a user rating.</p>
    </div>
  </div>
</section>
{END}"""


def inject_home(block):
    html = HOME.read_text(encoding="utf-8")
    if START in html and END in html:
        pre = html.split(START)[0]
        post = html.split(END)[1]
        HOME.write_text(pre + block + post, encoding="utf-8")
        return "replaced"
    # Directly after the hero closes. Searching backwards from a later heading
    # walked past the hero and landed the block above it, pushing the hero off
    # the top of the page - so anchor forwards from the hero itself instead.
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
    PAGE.write_text(build_page(d), encoding="utf-8")
    print(f"wrote {PAGE.relative_to(ROOT)} ({PAGE.stat().st_size:,} bytes)")
    print("homepage:", inject_home(build_home_block(d)))


if __name__ == "__main__":
    main()
