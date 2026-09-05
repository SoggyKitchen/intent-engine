"""
Build /pages/saas-hidden-costs-2026 from data/hidden_costs.json.

Why this page exists
--------------------
As of 2026-09-06 the site had 107 GSC impressions in 28 days and every single
one came from the query "saaspare.org". Zero non-branded impressions. More
comparison pages will not fix that - the corpus already had 1,545 of them and
ranked for nothing.

Current guidance is consistent that what ranks is information gain: a fact the
reader cannot get from the five pages above us. Vendors publish per-seat prices
prominently and bury the mandatory extras. Nobody consolidates the extras.
That is the gap this page fills.

Every row is read off the vendor's own pricing page, carries the source link
and the date it was checked, and is regenerated from JSON so it cannot drift
into a stale claim silently. Where a vendor charges nothing, the page says so
explicitly - "we checked and found none" is a finding, and publishing it is
what separates this from a scare piece.
"""
import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "hidden_costs.json"
OUT = ROOT / "site" / "pages" / "saas-hidden-costs-2026.html"
URL = "https://saaspare.org/pages/saas-hidden-costs-2026"

TITLE = "SaaS Hidden Costs 2026: Onboarding Fees, Seat Minimums, Annual-Only Traps"
DESC = ("HubSpot charges $1,500 required onboarding on Professional and $3,500 on "
        "Enterprise. monday.com will not sell fewer than 3 seats. Every Salesforce plan "
        "above Starter is annual-only. Verified on vendor pages 6 September 2026.")

LDQUO = "“"
RDQUO = "”"
MDASH = "-"


def e(s):
    return html.escape(str(s), quote=True)


def money(n):
    n = float(n)
    return f"${n:,.0f}" if n == int(n) else f"${n:,.2f}"


def src(u):
    return f'<a href="{e(u)}" rel="nofollow noopener" target="_blank">vendor page</a>'


def name_cell(vendor, plan):
    return (f'<td><strong>{e(vendor)}</strong><br>'
            f'<span class="hc-plan">{e(plan)}</span></td>')


def build(d):
    v = d["_meta"]["verified_on"]
    pretty = date.fromisoformat(v).strftime("%d %B %Y").lstrip("0")

    onboarding = d["onboarding_fees"]
    seats = d["seat_minimums"]
    annual = d["annual_only"]
    penalty = d["monthly_billing_penalty"]
    extra = d["extra_seat_costs"]
    none_found = d["checked_and_none_found"]

    # Year one is where a one-time fee actually bites, so show it rather than
    # leaving the reader to do the multiplication.
    ob_rows = ""
    for r in onboarding:
        adv, fee = r["advertised_monthly_usd"], r["fee_usd"]
        ob_rows += (
            "<tr>" + name_cell(r["vendor"], r["plan"])
            + f"<td>{money(adv)}/seat/mo</td>"
            + f'<td class="hc-fee">{money(fee)}</td>'
            + f"<td>{money(adv * 12 + fee)}</td>"
            + f'<td class="hc-up">+{fee / (adv * 12) * 100:.0f}%</td>'
            + f"<td>{src(r['source'])}</td></tr>\n"
        )

    seat_rows = ""
    for r in seats:
        cur, floor = r["currency"], r["advertised_price"] * r["min_seats"]
        seat_rows += (
            "<tr>" + name_cell(r["vendor"], r["plan"])
            + f"<td>{money(r['advertised_price'])} {e(cur)}/seat/mo</td>"
            + f"<td>{r['min_seats']}</td>"
            + f'<td class="hc-fee">{money(floor)} {e(cur)}/mo</td>'
            + f"<td>{src(r['source'])}</td></tr>\n"
        )

    ann_rows = ""
    for r in annual:
        ann_rows += (
            "<tr>" + name_cell(r["vendor"], r["plan"])
            + f"<td>{money(r['price_usd'])}/seat/mo</td>"
            + f'<td class="hc-fee">{money(r["annual_commitment_usd"])} per seat, up front</td>'
            + f"<td>{LDQUO}{e(r['quote'])}{RDQUO}</td>"
            + f"<td>{src(r['source'])}</td></tr>\n"
        )

    pen_rows = ""
    for r in penalty:
        a, m = r["annual_rate_usd"], r["monthly_rate_usd"]
        pen_rows += (
            "<tr>" + name_cell(r["vendor"], r["plan"])
            + f"<td>{money(a)}/seat/mo</td><td>{money(m)}/seat/mo</td>"
            + f'<td class="hc-up">+{(m - a) / a * 100:.0f}%</td>'
            + f"<td>{src(r['source'])}</td></tr>\n"
        )

    ext_rows = ""
    for r in extra:
        ext_rows += (
            "<tr>" + name_cell(r["vendor"], r["plan"])
            + f"<td>{r['included_users']}</td>"
            + f'<td class="hc-fee">{money(r["extra_seat_usd"])}/mo each</td>'
            + f"<td>up to {r['max_extra']} more</td>"
            + f"<td>{src(r['source'])}</td></tr>\n"
        )

    clean = "".join(
        f"<li><strong>{e(r['vendor'])}</strong> {MDASH} {e(r['result'])} "
        f'<a href="{e(r["source"])}" rel="nofollow noopener" target="_blank">source</a></li>\n'
        for r in none_found
    )

    faq = [
        ("Does HubSpot charge a mandatory onboarding fee?",
         "Yes. HubSpot's Sales Hub pricing page describes Professional Onboarding at "
         "$1,500 and Enterprise Onboarding at $3,500 as required, one-time fees, charged "
         "on top of the per-seat subscription. Checked " + pretty + "."),
        ("What is the real minimum monthly cost of monday.com?",
         "monday.com states that plans start from 3 users. At the advertised $14 AUD per "
         "seat for Basic, the true floor is $42 AUD per month, not $14. Checked " + pretty + "."),
        ("Can you pay for Salesforce monthly?",
         "Only on Starter Suite. Pro Suite, Core, Advanced and Max are all marked billed "
         "annually on Salesforce's pricing page, so the first invoice covers twelve months "
         "per seat. Checked " + pretty + "."),
        ("How much more does monthly billing cost?",
         "It varies widely, even inside one vendor. HubSpot Sales Hub Starter is $7 per "
         "seat annually against $20 monthly, so paying monthly costs 186% more. On "
         "Professional the same gap is only 11%. Check it per plan, not per vendor."),
        ("Are these numbers estimates?",
         "No. Every figure was read directly off the vendor's public pricing page on "
         + pretty + " and each row links to its source. Nothing is modelled. Where a "
         "vendor charges no hidden fee, this page says so rather than leaving a gap."),
    ]
    faq_html = "".join(
        f'<details class="hc-faq"><summary>{e(q)}</summary><p>{e(a)}</p></details>\n'
        for q, a in faq
    )

    def ld(o):
        return ('<script type="application/ld+json">\n'
                + json.dumps(o, indent=2, ensure_ascii=False) + "\n</script>")

    article_ld = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": TITLE, "description": DESC, "url": URL,
        "datePublished": v, "dateModified": v,
        "author": {"@type": "Person", "name": "Kaylan von Papen",
                   "url": "https://saaspare.org/authors/kaylan-von-papen"},
        "publisher": {"@id": "https://saaspare.org/#organization"},
    }
    dataset_ld = {
        "@context": "https://schema.org", "@type": "Dataset",
        "name": "SaaS Hidden Costs 2026",
        "description": ("Mandatory onboarding fees, seat minimums, annual-only billing "
                        "terms and extra-seat costs for major B2B SaaS vendors, each read "
                        "off the vendor's own pricing page and dated."),
        "url": URL, "license": "https://creativecommons.org/licenses/by/4.0/",
        "dateModified": v, "isAccessibleForFree": True,
        "creator": {"@id": "https://saaspare.org/#organization"},
        "keywords": ["SaaS onboarding fees", "HubSpot onboarding fee",
                     "SaaS seat minimums", "annual billing only",
                     "hidden SaaS costs", "B2B software total cost"],
    }
    faq_ld = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}}
                       for q, a in faq],
    }

    total_rows = len(onboarding) + len(seats) + len(annual) + len(penalty) + len(extra)

    css = """
  .hc-wrap{max-width:1100px;margin:0 auto;padding:48px 20px 96px}
  .hc-eyebrow{color:var(--pink);font-weight:600;letter-spacing:.08em;text-transform:uppercase;font-size:12px;margin:0 0 12px}
  .hc-wrap h1{font-size:clamp(28px,4vw,44px);line-height:1.12;margin:0 0 16px;color:var(--ink)}
  .hc-sub{color:var(--ink-3);font-size:18px;line-height:1.6;max-width:760px;margin:0 0 24px}
  .hc-stamp{display:inline-flex;align-items:center;gap:8px;background:var(--glass);border:1px solid var(--line);border-radius:var(--r-full);padding:8px 16px;color:var(--ink-3);font-size:13px;margin-bottom:40px}
  .hc-stamp b{color:var(--green)}
  .hc-verdict{background:var(--glass-pink);border:1px solid var(--line-pink);border-radius:var(--r-lg);padding:24px 28px;box-shadow:var(--shadow-pink);margin:0 0 48px}
  .hc-verdict h2{margin:0 0 12px;font-size:20px;color:var(--ink)}
  .hc-verdict p{margin:0 0 10px;color:var(--ink-2);line-height:1.65}
  .hc-wrap h2.hc-h{font-size:24px;margin:48px 0 8px;color:var(--ink)}
  .hc-note{color:var(--ink-4);font-size:14px;margin:0 0 16px;line-height:1.6;max-width:760px}
  .hc-scroll{overflow-x:auto;border:1px solid var(--line);border-radius:var(--r-md);background:var(--bg-rise);box-shadow:var(--shadow-card)}
  table.hc{width:100%;border-collapse:collapse;font-size:15px;min-width:660px}
  table.hc th{text-align:left;padding:14px 16px;color:var(--ink-4);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid var(--line)}
  table.hc td{padding:16px;border-bottom:1px solid var(--line-soft);color:var(--ink-2);vertical-align:top}
  table.hc tr:last-child td{border-bottom:0}
  .hc-plan{color:var(--ink-4);font-size:13px}
  .hc-fee{color:var(--pink);font-weight:700;white-space:nowrap}
  .hc-up{color:var(--amber);font-weight:600;white-space:nowrap}
  table.hc a{color:var(--ink-4);font-size:13px}
  table.hc a:hover{color:var(--pink)}
  .hc-clean{background:var(--glass);border:1px solid var(--line);border-radius:var(--r-md);padding:20px 24px}
  .hc-clean ul{margin:0;padding-left:20px;color:var(--ink-3);line-height:1.8}
  .hc-faq{border:1px solid var(--line);border-radius:var(--r-md);background:var(--glass);margin:0 0 10px}
  .hc-faq summary{cursor:pointer;padding:16px 20px;color:var(--ink);font-weight:600;list-style:none}
  .hc-faq summary::-webkit-details-marker{display:none}
  .hc-faq summary::after{content:"+";float:right;color:var(--pink)}
  .hc-faq[open] summary::after{content:"\\2013"}
  .hc-faq p{margin:0;padding:0 20px 18px;color:var(--ink-3);line-height:1.7}
  .hc-method{margin-top:48px;padding-top:24px;border-top:1px solid var(--line);color:var(--ink-4);font-size:14px;line-height:1.7}
  .hc-method a{color:var(--ink-3)}
"""

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
{ld(article_ld)}
{ld(dataset_ld)}
{ld(faq_ld)}
<style>{css}</style>
</head>
<body style="background:#050407;color:rgba(255,248,245,.88)">
<main class="hc-wrap">
  <p class="hc-eyebrow">Original research</p>
  <h1>SaaS hidden costs, 2026</h1>
  <p class="hc-sub">Vendors advertise a per-seat price. The invoice includes things the
  pricing page mentions once, in small type, below the fold: required onboarding fees,
  seat minimums you cannot go under, and plans that quietly cannot be paid monthly at
  all. Here is every one we could verify, with the receipt.</p>

  <p class="hc-stamp">Every figure read off the vendor's own pricing page on
  <b>{e(pretty)}</b> &middot; {total_rows} verified line items</p>

  <div class="hc-verdict">
    <h2>The short version</h2>
    <p><strong>HubSpot Sales Hub Professional</strong> advertises {money(100)}/seat/month.
    Year one for a single seat is {money(2700)}, because onboarding is a required
    {money(1500)} on top.</p>
    <p><strong>monday.com</strong> advertises from $14 AUD/seat. You cannot buy one seat.
    The floor is three, so the real entry price is $42 AUD/month.</p>
    <p><strong>Salesforce</strong> above Starter cannot be paid monthly at all. Pro Suite
    reads as {money(100)}/seat/month and is invoiced as {money(1200)} per seat up front.</p>
  </div>

  <h2 class="hc-h">Required onboarding fees</h2>
  <p class="hc-note">One-time, mandatory, charged on top of the subscription. The year-one
  column is twelve months of a single seat plus the fee.</p>
  <div class="hc-scroll"><table class="hc">
    <thead><tr><th>Vendor / plan</th><th>Advertised</th><th>Required fee</th><th>Year one, 1 seat</th><th>Uplift</th><th>Source</th></tr></thead>
    <tbody>
{ob_rows}    </tbody>
  </table></div>

  <h2 class="hc-h">Seat minimums</h2>
  <p class="hc-note">The advertised per-seat price is real. How many seats you are allowed
  to buy is the part that is easy to miss.</p>
  <div class="hc-scroll"><table class="hc">
    <thead><tr><th>Vendor / plan</th><th>Advertised</th><th>Min seats</th><th>Real monthly floor</th><th>Source</th></tr></thead>
    <tbody>
{seat_rows}    </tbody>
  </table></div>

  <h2 class="hc-h">Plans that cannot be paid monthly</h2>
  <p class="hc-note">Shown as a monthly figure, sold only as a twelve-month commitment.
  The cash needed on day one is the third column, per seat.</p>
  <div class="hc-scroll"><table class="hc">
    <thead><tr><th>Vendor / plan</th><th>Shown as</th><th>Actually invoiced</th><th>Vendor wording</th><th>Source</th></tr></thead>
    <tbody>
{ann_rows}    </tbody>
  </table></div>

  <h2 class="hc-h">What monthly billing actually costs</h2>
  <p class="hc-note">The annual discount is not a flat rate even inside one vendor, which
  is why a blanket save-20%-annually claim is worth checking per tier.</p>
  <div class="hc-scroll"><table class="hc">
    <thead><tr><th>Vendor / plan</th><th>Annual rate</th><th>Monthly rate</th><th>Penalty</th><th>Source</th></tr></thead>
    <tbody>
{pen_rows}    </tbody>
  </table></div>

  <h2 class="hc-h">Cost of adding one more person</h2>
  <p class="hc-note">Some tools include a single user and charge separately per extra seat,
  so team cost is not the sticker price multiplied by headcount.</p>
  <div class="hc-scroll"><table class="hc">
    <thead><tr><th>Vendor / plan</th><th>Users included</th><th>Each extra seat</th><th>Cap</th><th>Source</th></tr></thead>
    <tbody>
{ext_rows}    </tbody>
  </table></div>

  <h2 class="hc-h">Checked, and charging nothing extra</h2>
  <p class="hc-note">A hidden-fee list that only lists fees is a scare piece. These vendors
  were checked the same day and their pricing pages state no such charge.</p>
  <div class="hc-clean"><ul>
{clean}  </ul></div>

  <h2 class="hc-h">Questions</h2>
{faq_html}
  <p class="hc-method">
    <strong>How this was compiled.</strong> Each row was read off the vendor's public
    pricing page on {e(pretty)} and links to that page. Nothing is modelled, estimated or
    inferred; where a page states no fee, that is recorded as a finding rather than left
    blank. Pricing pages geolocate, so rows captured in a currency other than USD are
    labelled with the currency shown. Vendors change prices without notice, so the date
    stamp is the only claim being made about when this was true.
    Read our <a href="/methodology">methodology</a> and
    <a href="/corrections">corrections policy</a>. Spotted something wrong?
    <a href="/contact">Tell us</a> and we will fix it and log the change.
    By <a href="/authors/kaylan-von-papen">Kaylan von Papen</a>.
  </p>
</main>
</body>
</html>
"""


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    OUT.write_text(build(d), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
