"""
Put each tool's editorial review on that tool's OWN page, where it can qualify.

Why this exists
---------------
The ranking page carried all 15 reviews nested under one Article. Google's Rich
Results Test rejected every one of them (2026-09-06, 15 invalid review snippets,
15 invalid software apps). Three real faults:

  1. `Multiple reviews without aggregateRating object` - a page reviewing many
     items is not a review-snippet pattern. Google's guidance says plainly:
     "Provide review information about a specific item, not about a category or
     a list of items."
  2. `author` / `publisher`: Missing field "name" - a bare {"@id": ...} pointer
     does not resolve for the parser when the Organization node lives in a
     different script block. Names have to be inline.
  3. `Invalid object type for field "<parent_node>"` - Review hanging off
     Article is the wrong parent.

So the reviews move to each tool's own page, as a top-level SoftwareApplication
with one review by us. There the tool IS the specific item, which is the shape
Google actually supports.

Google also requires the marked-up review to be "readily available to users
from the marked-up page", so this injects the VISIBLE verdict too, not just
schema. Marking up text a reader cannot see is cloaking, and we are not doing
that to chase a star.

Tools with no indexable page of their own get no review schema. No page, no
snippet - creating a page purely to host a rating is how the site earned 1,053
noindexed pages in the first place.

Idempotent: comment-delimited, so a re-run replaces rather than stacks.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
SCORES = ROOT / "data" / "transparency_scores.json"
VERDICTS = ROOT / "data" / "editorial_verdicts.json"
SEED = ROOT / "data" / "pricing_seed.json"
RANKING = "/pages/saas-pricing-transparency-scores-2026"

START = "<!-- sp-tool-review:start -->"
END = "<!-- sp-tool-review:end -->"

ORG = {"@type": "Organization", "name": "SaaSpare", "url": "https://saaspare.org/"}

# Prefer the page a buyer comparing cost would actually land on.
PREFERRED = ("-pricing-2026-plans-costs-what-you-actually-pay", "-pricing-history-2026")


def target_for(tool):
    for suffix in PREFERRED:
        p = PAGES / f"{tool}{suffix}.html"
        if p.exists() and "noindex" not in p.read_text(encoding="utf-8", errors="replace"):
            return p
    return None


def cheapest_paid(tool_seed):
    paid = [p for p in tool_seed["plans"] if (p.get("monthly_usd") or 0) > 0]
    return min(paid, key=lambda p: p["monthly_usd"]) if paid else None


def stars_svg(value, size=16):
    out = []
    for i in range(1, 6):
        if value >= i:
            fill = "#ff416d"
        elif value >= i - 0.5:
            fill = "url(#sp-tr-half)"
        else:
            fill = "rgba(255,247,248,.18)"
        out.append(
            f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="{fill}" '
            f'aria-hidden="true" style="flex:none"><path d="M12 2l3 6.9 7.5.8-5.6 5 '
            f'1.6 7.3L12 18.3 5.5 22l1.6-7.3-5.6-5 7.5-.8z"/></svg>'
        )
    return "".join(out)


def block(s, v, seed_tool, verified):
    plan = cheapest_paid(seed_tool)
    app = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": s["vendor"],
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web",
        "url": seed_tool.get("source_url"),
        "review": {
            "@type": "Review",
            "name": v["headline"],
            "reviewRating": {"@type": "Rating", "ratingValue": s["stars"],
                             "bestRating": 5, "worstRating": 1},
            "author": ORG,
            "publisher": ORG,
            "datePublished": verified,
            "reviewBody": (f"{v['body']} Best for: {v['best_for']} "
                           f"Watch for: {v['watch_for']}"),
        },
    }
    if plan:
        app["offers"] = {
            "@type": "Offer",
            "price": plan["monthly_usd"],
            "priceCurrency": "USD",
            "name": plan["plan"],
            "url": seed_tool.get("source_url"),
            "availability": "https://schema.org/InStock",
        }

    ld = ('<script type="application/ld+json">\n'
          + json.dumps(app, indent=2, ensure_ascii=False) + "\n</script>")

    # The visible half. Google requires marked-up review content to be readable
    # on the page; schema without visible text would be cloaking.
    return f"""{START}
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<linearGradient id="sp-tr-half"><stop offset="50%" stop-color="#ff416d"/>
<stop offset="50%" stop-color="rgba(255,247,248,.18)"/></linearGradient></defs></svg>
<section class="sptr-tool" aria-labelledby="sptr-tool-h">
  <style>
    .sptr-tool{{max-width:860px;margin:40px auto;padding:24px 26px;
      background:linear-gradient(180deg,rgba(60,9,24,.82),rgba(22,9,15,.92));
      border:1px solid rgba(255,75,115,.25);border-radius:20px;
      box-shadow:0 30px 90px rgba(255,45,92,.14),inset 0 1px 0 rgba(255,255,255,.06)}}
    .sptr-tool-top{{display:flex;flex-wrap:wrap;gap:12px;align-items:center;
      justify-content:space-between;margin-bottom:14px}}
    .sptr-tool-eyebrow{{color:#ff416d;font-weight:600;letter-spacing:.08em;
      text-transform:uppercase;font-size:11px;margin:0}}
    .sptr-tool h2{{font-size:19px;margin:4px 0 0;color:#fff7f8;font-weight:700}}
    .sptr-tool-rate{{display:flex;align-items:center;gap:10px}}
    .sptr-tool-stars{{display:flex;gap:2px}}
    .sptr-tool-num{{color:#ff416d;font-weight:800;font-size:20px}}
    .sptr-tool-num span{{color:rgba(255,247,248,.42);font-size:12px;font-weight:600}}
    .sptr-tool p.v{{margin:0 0 14px;color:rgba(255,248,245,.82);line-height:1.7;font-size:15px}}
    .sptr-tool-cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
      gap:10px;margin-bottom:14px}}
    .sptr-tool-cols p{{margin:0;padding:11px 13px;background:rgba(255,255,255,.03);
      border-radius:10px;border-left:2px solid #36e6a1;color:rgba(255,247,248,.64);
      font-size:13.5px;line-height:1.55}}
    .sptr-tool-cols p.w{{border-left-color:#f5b942}}
    .sptr-tool-cols b{{display:block;color:rgba(255,247,248,.42);font-size:10.5px;
      text-transform:uppercase;letter-spacing:.06em;margin-bottom:3px}}
    .sptr-tool-foot{{color:rgba(255,247,248,.42);font-size:12.5px;margin:0;line-height:1.55}}
    .sptr-tool-foot a{{color:#ff416d}}
  </style>
  <div class="sptr-tool-top">
    <div>
      <p class="sptr-tool-eyebrow">SaaSpare cost transparency score</p>
      <h2 id="sptr-tool-h">{v['headline']}</h2>
    </div>
    <div class="sptr-tool-rate">
      <span class="sptr-tool-stars" role="img" aria-label="{s['stars']} out of 5">{stars_svg(s['stars'])}</span>
      <span class="sptr-tool-num">{s['stars']}<span>/5</span></span>
    </div>
  </div>
  <p class="v">{v['body']}</p>
  <div class="sptr-tool-cols">
    <p><b>Best for</b>{v['best_for']}</p>
    <p class="w"><b>Watch for</b>{v['watch_for']}</p>
  </div>
  <p class="sptr-tool-foot">Editorial score by SaaSpare, not a user rating.
  {s['points']}/{s['max_points']} points across eight pricing-transparency tests,
  computed from pricing verified {verified}.
  <a href="{RANKING}">See how all 15 tools rank</a>.</p>
</section>
{ld}
{END}"""


def main():
    scores = json.loads(SCORES.read_text(encoding="utf-8"))["scores"]
    meta = json.loads(SCORES.read_text(encoding="utf-8"))["_meta"]
    verdicts = json.loads(VERDICTS.read_text(encoding="utf-8"))["verdicts"]
    seed = {t["tool"]: t for t in json.loads(SEED.read_text(encoding="utf-8"))["tools"]}
    verified = meta["pricing_verified_on"]

    done, skipped = [], []
    for s in scores:
        tool = s["tool"]
        v = verdicts.get(tool)
        p = target_for(tool)
        if not v or not p:
            skipped.append(tool)
            continue

        html = p.read_text(encoding="utf-8", errors="replace")
        b = block(s, v, seed[tool], verified)
        if START in html and END in html:
            html = html.split(START)[0] + b + html.split(END)[1]
        else:
            anchor = "</main>" if "</main>" in html else "</body>"
            if anchor not in html:
                skipped.append(tool)
                continue
            html = html.replace(anchor, b + "\n" + anchor, 1)
        p.write_text(html, encoding="utf-8")
        done.append(f"{tool} -> {p.name}")

    print(f"review schema + visible verdict on {len(done)} tool pages:")
    for d in done:
        print("  " + d)
    if skipped:
        print(f"\nno indexable dedicated page, deliberately skipped: {', '.join(skipped)}")


if __name__ == "__main__":
    main()
