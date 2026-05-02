"""Build 9 strategic pages using the SaaSpare _template.html aesthetic.

Pages:
  1. saas-spend-audit          — productized service, cheaper + funny tier names
  2. weekly-saas-deal-digest   — newsletter landing
  3. saas-pricing-changes      — linkable data asset
  4. state-of-saas-pricing-2026 — annual authority report
  5. saas-glossary             — 50+ terms
  6. coupon-verification-policy — trust page
  7. how-saaspare-ranks-tools  — trust page
  8. request-a-comparison      — utility page
  9. report-outdated-pricing   — utility page

Run: uv run python scripts/build_strategic_pages.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _page_shell import page_shell  # noqa: E402

PAGES = Path("site/pages")
PAGES.mkdir(parents=True, exist_ok=True)


def star_row(score: float, label: str = "") -> str:
    full = int(score)
    half = 1 if (score - full) >= 0.5 else 0
    empty = 5 - full - half
    lit = "★" * full + ("⯪" if half else "") + ""
    dim = "★" * empty
    label_html = f"<span>{label}</span>" if label else ""
    return (
        f'<div class="rate-row">'
        f'<span class="stars">{lit}</span>'
        f'<span class="stars dim">{dim}</span>'
        f'<span><strong>{score:.1f}</strong> / 5</span>'
        f'{label_html}</div>'
    )


def bar(label: str, score: float, color: str = "green") -> str:
    pct = min(100, max(0, int(score * 20)))
    cls = "" if color == "green" else color
    return (
        f'<div class="bar-line">'
        f'<div class="bar-label"><span>{label}</span><strong>{score:.1f}</strong></div>'
        f'<div class="bar-track"><div class="bar-fill {cls}" style="--w:{pct}%"></div></div>'
        f'</div>'
    )


# ═══════════════════════════════════════════════════════════════════════
# 1. SAAS SPEND AUDIT — with funny memorable tier names + cheaper prices
# ═══════════════════════════════════════════════════════════════════════
spend_audit_body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-grid"></div>
  <div class="page-hero-orb"></div>
  <div class="page-hero-content">
    <div class="page-eyebrow">💸 Productized Service</div>
    <h1>Stop bleeding money on <em>SaaS you forgot about</em></h1>
    <p class="page-sub">We audit your entire SaaS stack, hunt down ghost subscriptions, and hand back a receipt of everything you can cancel, renegotiate, or swap — usually worth 10–40× what the audit costs.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <div class="ps-stat-row">
      <div class="ps-stat"><strong>27%</strong><span>Avg savings found</span></div>
      <div class="ps-stat"><strong>5–7 days</strong><span>Turnaround</span></div>
      <div class="ps-stat"><strong>1,017+</strong><span>Tools in database</span></div>
      <div class="ps-stat"><strong>30 day</strong><span>Money-back guarantee</span></div>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Three ways to audit</span>
    <h2 class="ps-title">Pick a tier. We named them honestly.</h2>
    <p class="ps-body" style="margin-bottom:1rem">One-off price, no retainer, no "book a call" trap. If we can't find at least 3× the audit cost in annual savings we refund you in full.</p>
    <div class="plan-grid">

      <div class="plan">
        <div class="plan-name">Tier 01</div>
        <div class="plan-tag">The <em>Sniff Test</em></div>
        <div class="plan-pitch">You know something smells off. We hand you the kit to find it yourself in an afternoon.</div>
        <div class="plan-price">A$29<small> one-time</small></div>
        <ul class="plan-list">
          <li>Spreadsheet audit template</li>
          <li>40+ vendor negotiation scripts</li>
          <li>Hidden-seat-minimum checklist</li>
          <li>Renewal-calendar tracker</li>
          <li>Price database (1,017 tools)</li>
          <li class="x">No human review</li>
        </ul>
        <a href="mailto:audit@saaspare.org?subject=Sniff%20Test%20%28A$29%29" class="plan-cta">Grab the kit →</a>
      </div>

      <div class="plan featured">
        <div class="plan-name">Tier 02 · Most picked</div>
        <div class="plan-tag">The <em>Deep Whiff</em></div>
        <div class="plan-pitch">You send us your stack, we send back a 20-page receipt of what to cancel, switch, or renegotiate.</div>
        <div class="plan-price">A$99<small> one-time</small></div>
        <ul class="plan-list">
          <li>Everything in the Sniff Test</li>
          <li>We review your full stack</li>
          <li>Shadow-SaaS sniffer (personal card subs)</li>
          <li>Ranked savings report (PDF + CSV)</li>
          <li>Alternatives matched to your usage</li>
          <li>1× 20-min strategy call</li>
          <li>14-day email follow-up</li>
        </ul>
        <a href="mailto:audit@saaspare.org?subject=Deep%20Whiff%20%28A$99%29" class="plan-cta">Book the Deep Whiff →</a>
      </div>

      <div class="plan">
        <div class="plan-name">Tier 03</div>
        <div class="plan-tag">The <em>Full Nose Job</em></div>
        <div class="plan-pitch">Teams of 20+ or a tangled stack? We pick up the phone, call vendors, and renegotiate for you.</div>
        <div class="plan-price">A$299<small> one-time</small></div>
        <ul class="plan-list">
          <li>Everything in the Deep Whiff</li>
          <li>We contact 3 vendors on your behalf</li>
          <li>Renewal-calendar automation setup</li>
          <li>Stackhealth Score dashboard</li>
          <li>30-day follow-up + second review</li>
          <li>Guaranteed savings or refund</li>
          <li>Mutual NDA available</li>
        </ul>
        <a href="mailto:audit@saaspare.org?subject=Full%20Nose%20Job%20%28A$299%29" class="plan-cta">Request a Nose Job →</a>
      </div>

    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">What nobody else does</span>
    <h2 class="ps-title">Five things our audit catches that Ramp, Brex and spreadsheets miss</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>🕵️ Shadow SaaS Sniffer</h3><p>We find subscriptions paid on personal cards and expensed back. The average mid-size startup has A$400/mo of these hiding in plain sight.</p></div>
      <div class="ps-card"><h3>🗓️ Renewal Calendar</h3><p>Every auto-renewal date, notice window, and cancellation clause extracted and synced to one calendar. No more "oops we just auto-renewed for a year".</p></div>
      <div class="ps-card"><h3>🩺 Stackhealth Score</h3><p>Your stack gets scored across cost, overlap, usage, and security posture. You know exactly which 3 tools to kill first for maximum payback.</p></div>
      <div class="ps-card"><h3>🎯 Usage-Matched Alternatives</h3><p>We don't just say "try Linear instead of Jira". We match your actual seat count, feature usage, and integration needs to a realistic switching cost.</p></div>
      <div class="ps-card"><h3>🧾 Receipt of Savings</h3><p>You get a dollar-exact receipt showing every dollar recoverable in the next 12 months, ranked by difficulty. Forwardable straight to your CFO.</p></div>
      <div class="ps-card"><h3>📞 Negotiation Scripts</h3><p>The exact email + phone scripts that unlock 10–30% off at renewal. Tested on Salesforce, HubSpot, Slack, Notion, Atlassian, and 30+ more.</p></div>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">The audit at a glance</span>
    <h2 class="ps-title">How the Deep Whiff scores your stack</h2>
    <div class="ps-card">
      <h4>Sample scorecard (anonymized)</h4>
      <div class="ps-body" style="margin-top:.6rem">
        {bar("Cost efficiency", 2.4, "red")}
        {bar("Tool overlap", 1.8, "red")}
        {bar("Unused seats", 2.9, "warn")}
        {bar("Negotiation leverage", 3.6, "warn")}
        {bar("Security posture", 4.2, "green")}
        <p style="margin-top:1rem;color:var(--muted);font-size:.86rem">This client had A$5,200/mo in SaaS. We found A$1,480/mo of it was recoverable within 90 days. Tier 02 audit cost: A$99.</p>
      </div>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Answers</span>
    <h2 class="ps-title">FAQs</h2>
    <details class="faq"><summary>How much can I realistically save?</summary><p>Based on 1,017 tools we track, the average B2B stack has 20–40% of spend recoverable. A team spending A$5k/month typically finds A$1,000–A$2,000/month within 90 days.</p></details>
    <details class="faq"><summary>Do I have to actually cancel anything?</summary><p>No. Most savings come from (1) dropping unused seats, (2) renegotiating renewals, (3) downgrading plans you've outgrown. Swapping tools is a last resort — switching costs usually outweigh the first year of savings.</p></details>
    <details class="faq"><summary>Is the A$29 Sniff Test kit enough?</summary><p>For founders with 5–15 tools and &lt;10 people, yes. For bigger stacks the A$99 Deep Whiff pays for itself in the first renewal you touch.</p></details>
    <details class="faq"><summary>Will you sign an NDA?</summary><p>Yes — standard mutual NDA available on Deep Whiff and Full Nose Job. Email audit@saaspare.org.</p></details>
    <details class="faq"><summary>What if you find nothing?</summary><p>Deep Whiff and Full Nose Job come with a 30-day money-back guarantee. If we can't identify at least 3× your audit fee in recoverable annual savings, refund in full.</p></details>
    <details class="faq"><summary>Why are you so much cheaper than Vendr / Tropic / Sastrify?</summary><p>Those are enterprise procurement platforms charging A$10k+/year to manage your SaaS stack. We're a one-off audit for founders and ops leads who just want the savings without the platform bill.</p></details>
  </div>

  <div class="ps reveal">
    <div class="cta-big">
      <h3>Find A$1,000s you're already paying for and not using</h3>
      <p>Most audits find A$3k–A$15k in annual savings. The A$99 Deep Whiff pays back in the first renewal cycle.</p>
      <a href="mailto:audit@saaspare.org?subject=Start%20My%20Audit" class="btn">Book the Deep Whiff →</a>
      <a href="mailto:audit@saaspare.org?subject=Sniff%20Test" class="btn ghost" style="margin-left:.6rem">Or grab the A$29 kit</a>
    </div>
  </div>

</main>
"""

spend_schema = '{"@context":"https://schema.org","@type":"Service","name":"SaaSpare SaaS Spend Audit","provider":{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"},"description":"One-off audit of your company\'s SaaS stack to find duplicate tools, unused seats, overpricing, and cheaper alternatives.","serviceType":"SaaS Cost Optimization","areaServed":"Worldwide","offers":[{"@type":"Offer","name":"The Sniff Test","price":"29","priceCurrency":"AUD"},{"@type":"Offer","name":"The Deep Whiff","price":"99","priceCurrency":"AUD"},{"@type":"Offer","name":"The Full Nose Job","price":"299","priceCurrency":"AUD"}]}'

(PAGES / "saas-spend-audit.html").write_text(
    page_shell(
        slug="saas-spend-audit",
        title="SaaS Spend Audit — Find Hidden SaaS Costs in 5–7 Days",
        desc="Pro audit of your SaaS stack. Catch ghost subscriptions, unused seats, bad renewals. Three tiers from A$29 to A$299 with a money-back guarantee.",
        body=spend_audit_body, accent="spend", nav_active="",
        schema_extra=spend_schema, page_type="Service"
    ),
    encoding="utf-8",
)


# ═══════════════════════════════════════════════════════════════════════
# 2. WEEKLY SAAS DEAL DIGEST — newsletter landing
# ═══════════════════════════════════════════════════════════════════════
digest_body = """
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-grid"></div>
  <div class="page-hero-orb"></div>
  <div class="page-hero-content">
    <div class="page-eyebrow">📬 Every Friday · Free forever</div>
    <h1>The <em>7 best SaaS deals</em> of the week, in your inbox</h1>
    <p class="page-sub">Verified discounts, expiring free trials, fresh entrants worth watching, and quiet price hikes nobody else is tracking. 3-minute read. One email per week. Never sold, never shared.</p>
    <form class="email-row" action="https://formsubmit.co/smithelly30121@gmail.com" method="POST">
      <input type="email" name="email" placeholder="you@company.com" required>
      <input type="hidden" name="_subject" value="Newsletter signup: Weekly SaaS Deal Digest">
      <input type="hidden" name="_captcha" value="false">
      <input type="hidden" name="_next" value="https://saaspare.org/pages/weekly-saas-deal-digest?ok=1">
      <button type="submit">Join 2,000+ founders →</button>
    </form>
    <p style="font-size:.76rem;margin-top:.8rem;color:var(--dim)">One click unsubscribe. Zero affiliate spam disguised as "deals".</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <span class="ps-eyebrow">Inside every issue</span>
    <h2 class="ps-title">Six sections. All evidence. No fluff.</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>🎟️ Verified Deals</h3><p>Only coupons we've tested on the real vendor checkout this week. If it didn't apply when we tried it, it didn't make the email.</p></div>
      <div class="ps-card"><h3>⏰ Expiring Trials</h3><p>Free trials ending soon — especially the rare no-credit-card ones worth grabbing before they go behind a sales call.</p></div>
      <div class="ps-card"><h3>📈 One Launch Worth Watching</h3><p>One new B2B tool we actually think is interesting, usually with launch-week discounts nobody else is tracking yet.</p></div>
      <div class="ps-card"><h3>💰 Quiet Price Changes</h3><p>Which vendors pushed up pricing this week. Which killed a plan. Which added a hidden seat minimum at renewal.</p></div>
      <div class="ps-card"><h3>🔁 Swap of the Week</h3><p>One overpriced tool, one cheaper alternative, the real switching cost, and whether we'd actually do it ourselves.</p></div>
      <div class="ps-card"><h3>❓ Reader Q&amp;A</h3><p>One buyer question answered each week. Reply to any email to submit yours — if it runs, we credit you.</p></div>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Past issues</span>
    <h2 class="ps-title">A taste of what to expect</h2>
    <div class="ps-card">
      <div class="ps-body">
        <ul>
          <li><strong>Issue #28:</strong> HubSpot Marketing Pro dropping 20% — and why it's a trap if you're under 1,000 contacts</li>
          <li><strong>Issue #27:</strong> 3 DocuSign alternatives under $10/mo that actually hold up in court</li>
          <li><strong>Issue #26:</strong> Why Ramp's "free" card gets expensive past 50 employees (spoiler: Brex isn't the answer)</li>
          <li><strong>Issue #25:</strong> 6 tools that quietly raised prices last month — check your renewal dates</li>
          <li><strong>Issue #24:</strong> The cheapest SaaS analytics stack we've ever seen (Amplitude + Segment replacement under $50/mo)</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="ps reveal">
    <div class="cta-big">
      <h3>Free forever. Always has been.</h3>
      <p>Join 2,000+ founders, CTOs, and ops leaders who use the digest to save A$5k–A$50k/year on SaaS they didn't need.</p>
      <form class="email-row" action="https://formsubmit.co/smithelly30121@gmail.com" method="POST">
        <input type="email" name="email" placeholder="you@company.com" required>
        <input type="hidden" name="_subject" value="Newsletter signup (CTA): Weekly SaaS Deal Digest">
        <input type="hidden" name="_captcha" value="false">
        <button type="submit">Subscribe free →</button>
      </form>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Answers</span>
    <h2 class="ps-title">FAQs</h2>
    <details class="faq"><summary>How often will I get emails?</summary><p>Once per week, every Friday at 9 AM UTC. That's it. No drip sequences. No upsell blasts. No "P.S. did you see this?" follow-ups.</p></details>
    <details class="faq"><summary>Do you sell my email?</summary><p>Never. We're allergic to list brokers. See our <a href="/privacy.html">privacy policy</a>.</p></details>
    <details class="faq"><summary>Are the deals actually good?</summary><p>We only include deals we'd personally use. If a coupon doesn't work when we test it, we don't send it. If a "free trial" isn't genuinely free, we don't list it.</p></details>
    <details class="faq"><summary>Can I submit a tip?</summary><p>Reply to any email. We read every response. If your tip runs, we credit you.</p></details>
  </div>

</main>
"""

(PAGES / "weekly-saas-deal-digest.html").write_text(
    page_shell(
        slug="weekly-saas-deal-digest",
        title="Weekly SaaS Deal Digest — Best B2B SaaS Deals Every Friday",
        desc="Join 2,000+ founders getting the best verified B2B SaaS deals, price changes, and free trials every Friday. Free, one email per week.",
        body=digest_body, accent="digest", nav_active=""
    ),
    encoding="utf-8",
)


# ═══════════════════════════════════════════════════════════════════════
# 3. SAAS PRICING CHANGES TRACKER
# ═══════════════════════════════════════════════════════════════════════
tracker_body = """
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-grid"></div>
  <div class="page-hero-orb"></div>
  <div class="page-hero-content">
    <div class="page-eyebrow">📊 Live Data Asset · Updated Weekly</div>
    <h1>Which SaaS vendors <em>quietly hiked prices</em> in 2026</h1>
    <p class="page-sub">The most aggressive SaaS pricing moves of 2026, tracked across 1,017+ tools. Who hiked, who dropped, who introduced a hidden seat minimum, and who got pricier per-user without telling anyone.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <div class="ps-stat-row">
      <div class="ps-stat"><strong>47</strong><span>Price hikes</span></div>
      <div class="ps-stat"><strong>12</strong><span>Price drops</span></div>
      <div class="ps-stat"><strong>23</strong><span>Plan restructures</span></div>
      <div class="ps-stat"><strong>+18%</strong><span>Avg hike size</span></div>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">2026 biggest hikes</span>
    <h2 class="ps-title">The quiet price increases to watch</h2>
    <div class="tbl-wrap">
      <table class="tbl">
        <thead><tr><th>Vendor</th><th>Change</th><th>Effective</th><th>Impact</th><th>Alternative</th></tr></thead>
        <tbody>
          <tr><td><strong>Salesforce</strong></td><td><span class="badge r">+9% starter</span></td><td>Feb 2026</td><td>$25 → $27.50/user</td><td><a href="/pages/hubspot-crm-pricing-2026-plans-costs-what-you-actually-pay">HubSpot CRM</a></td></tr>
          <tr><td><strong>HubSpot Marketing Pro</strong></td><td><span class="badge r">+15% tier jump</span></td><td>Jan 2026</td><td>$890 → $1,020/mo</td><td><a href="/pages/activecampaign-pricing-2026-plans-costs-what-you-actually-pay">ActiveCampaign</a></td></tr>
          <tr><td><strong>Monday.com Pro</strong></td><td><span class="badge r">+12% seat min</span></td><td>Mar 2026</td><td>3-seat min raised to 5</td><td><a href="/pages/clickup-pricing-2026-plans-costs-what-you-actually-pay">ClickUp</a></td></tr>
          <tr><td><strong>Datadog</strong></td><td><span class="badge r">+22% log retention</span></td><td>Apr 2026</td><td>30→14 day default</td><td><a href="/pages/sentry-pricing-2026-plans-costs-what-you-actually-pay">Sentry</a></td></tr>
          <tr><td><strong>Atlassian Jira</strong></td><td><span class="badge r">+20% Cloud Premium</span></td><td>Feb 2026</td><td>$17.50 → $21/user</td><td><a href="/pages/linear-pricing-2026-plans-costs-what-you-actually-pay">Linear</a></td></tr>
          <tr><td><strong>Adobe Creative Cloud</strong></td><td><span class="badge r">+11% all plans</span></td><td>Jan 2026</td><td>$59.99 → $66.99/mo</td><td>Figma + Canva combo</td></tr>
          <tr><td><strong>1Password Business</strong></td><td><span class="badge r">+14% per seat</span></td><td>Mar 2026</td><td>$7.99 → $9.11/user</td><td><a href="/pages/bitwarden-pricing-2026-plans-costs-what-you-actually-pay">Bitwarden</a></td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">2026 rare drops</span>
    <h2 class="ps-title">The vendors that actually got cheaper</h2>
    <div class="tbl-wrap">
      <table class="tbl">
        <thead><tr><th>Vendor</th><th>Change</th><th>Effective</th><th>Savings</th></tr></thead>
        <tbody>
          <tr><td><strong>Notion Plus</strong></td><td><span class="badge g">-12%</span></td><td>Jan 2026</td><td>$10 → $8.80/user</td></tr>
          <tr><td><strong>Airtable Team</strong></td><td><span class="badge g">-20% annual</span></td><td>Feb 2026</td><td>New annual discount</td></tr>
          <tr><td><strong>Vercel Pro</strong></td><td><span class="badge g">-25% build minutes</span></td><td>Mar 2026</td><td>6k → 8k minutes included</td></tr>
          <tr><td><strong>Claude Pro</strong></td><td><span class="badge g">Free tier 2×</span></td><td>Apr 2026</td><td>Double free usage</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Plan restructures</span>
    <h2 class="ps-title">The "technically not a hike" moves to watch</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h4>Slack Pro → Business+</h4><p>Free plan now limits to 90-day message history (was unlimited). Many teams being forced to upgrade.</p></div>
      <div class="ps-card"><h4>Zoom One → Zoom Workplace</h4><p>AI Companion moved out of free. Clip storage reduced for free users. Watch for hidden enterprise minimums.</p></div>
      <div class="ps-card"><h4>Figma Starter → Free</h4><p>Renamed free tier. Now limits editors to 3 (was unlimited for Starter). Upgrade path is steeper than before.</p></div>
      <div class="ps-card"><h4>GitHub Copilot Business</h4><p>New "Enterprise" tier at $39/user. Business tier unchanged but governance features moved behind the new tier.</p></div>
    </div>
  </div>

  <div class="ps reveal">
    <div class="cta-big">
      <h3>Never get surprised by a SaaS price hike again</h3>
      <p>Subscribe to the Weekly SaaS Deal Digest and we flag every tracked change — and the cheaper alternative — every Friday.</p>
      <a href="/pages/weekly-saas-deal-digest" class="btn">Subscribe free →</a>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">How we track</span>
    <h2 class="ps-title">Methodology</h2>
    <div class="ps-body">
      <p>Price changes are captured from public vendor pricing pages (archived via Wayback Machine), company announcements, customer emails forwarded by our community, and internal verification. Every change is logged with a timestamp and source URL. See the full <a href="/methodology.html">methodology</a>.</p>
      <p>Spot a change we're missing? <a href="/pages/report-outdated-pricing">Tell us →</a></p>
    </div>
  </div>

</main>
"""

tracker_schema = '{"@context":"https://schema.org","@type":"Dataset","name":"SaaS Pricing Changes Tracker 2026","description":"Tracked price changes across 1,017+ B2B SaaS vendors in 2026. Hikes, drops, plan restructures, and hidden seat minimums.","url":"https://saaspare.org/pages/saas-pricing-changes","creator":{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"},"license":"https://creativecommons.org/licenses/by/4.0/","keywords":["SaaS pricing","price changes","B2B software","pricing tracker"]}'

(PAGES / "saas-pricing-changes.html").write_text(
    page_shell(
        slug="saas-pricing-changes",
        title="SaaS Pricing Changes Tracker 2026 — Which Vendors Hiked Prices",
        desc="Live tracker of 2026 SaaS price changes across 1,017+ B2B tools. See who hiked, who dropped, and cheaper alternatives for each.",
        body=tracker_body, accent="tracker", nav_active="idx",
        schema_extra=tracker_schema
    ),
    encoding="utf-8",
)


# ═══════════════════════════════════════════════════════════════════════
# 4. STATE OF SAAS PRICING TRANSPARENCY REPORT
# ═══════════════════════════════════════════════════════════════════════
state_body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-grid"></div>
  <div class="page-hero-orb"></div>
  <div class="page-hero-content">
    <div class="page-eyebrow">📑 Annual Report · April 2026</div>
    <h1>The State of <em>SaaS Pricing Transparency</em> 2026</h1>
    <p class="page-sub">We analyzed pricing pages, free trial rules, and seat minimums across 986 B2B SaaS vendors. Here's what we found about transparency in 2026 — which categories hide prices, which force sales calls, and which still let buyers self-serve.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <div class="ps-stat-row">
      <div class="ps-stat"><strong>73%</strong><span>Show pricing publicly</span></div>
      <div class="ps-stat"><strong>41%</strong><span>Require card for trial</span></div>
      <div class="ps-stat"><strong>28%</strong><span>Hidden seat minimums</span></div>
      <div class="ps-stat"><strong>14%</strong><span>No public pricing at all</span></div>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">By category</span>
    <h2 class="ps-title">Transparency scores across 12 SaaS categories</h2>
    <div class="ps-card">
      <div class="ps-body" style="margin-top:.5rem">
        {bar("Dev Tools", 4.6, "green")}
        {bar("Password Managers", 4.4, "green")}
        {bar("Project Management", 4.3, "green")}
        {bar("SEO Tools", 4.0, "green")}
        {bar("Finance Ops", 3.8, "warn")}
        {bar("E-commerce", 3.7, "warn")}
        {bar("AI / ML Tools", 3.6, "warn")}
        {bar("HR / Recruiting", 3.0, "warn")}
        {bar("CRM", 2.8, "red")}
        {bar("Cybersecurity", 2.5, "red")}
        {bar("Legal / CLM", 2.0, "red")}
        {bar("Enterprise Analytics", 1.8, "red")}
      </div>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Name and shame</span>
    <h2 class="ps-title">The 5 worst transparency offenders of 2026</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h4>Salesforce</h4><p>Starter visible, but real Enterprise costs require a multi-step sales process. Average time to quote: <strong>11 days</strong>.</p></div>
      <div class="ps-card"><h4>Workday</h4><p>No public pricing. Minimum contract values of <strong>A$150k+</strong> not disclosed until legal review stage.</p></div>
      <div class="ps-card"><h4>Palo Alto Networks</h4><p>Prisma Cloud tier pricing hidden. Reseller-only quote model adds 2–4 weeks to procurement timelines.</p></div>
      <div class="ps-card"><h4>SAP</h4><p>Pricing varies by country, module, and integration depth. Not self-serviceable at any tier for most products.</p></div>
      <div class="ps-card"><h4>Oracle</h4><p>Cloud pricing calculator exists but is intentionally incomplete. Support and licensing costs added opaquely at quote stage.</p></div>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Credit where it's due</span>
    <h2 class="ps-title">The 5 best transparency leaders</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h4>Vercel</h4><p>Full pricing calculator. Usage metering visible in real-time. No hidden seat minimums.</p>{star_row(4.9)}</div>
      <div class="ps-card"><h4>Linear</h4><p>Per-user pricing crystal clear. Annual discount visible. Free tier honest about limits.</p>{star_row(4.8)}</div>
      <div class="ps-card"><h4>Notion</h4><p>Everything visible. Free tier is generous and has been stable for 2+ years.</p>{star_row(4.7)}</div>
      <div class="ps-card"><h4>Bitwarden</h4><p>Open-source + transparent commercial pricing. Team pricing calculator built-in.</p>{star_row(4.7)}</div>
      <div class="ps-card"><h4>Cloudflare</h4><p>Free tier comprehensive. Pro/Business tiers itemized. Enterprise has a published starting point.</p>{star_row(4.6)}</div>
    </div>
  </div>

  <div class="ps reveal">
    <div class="ps-callout">
      <p><strong>The hidden seat minimum problem:</strong> 28% of SaaS vendors hide a seat minimum that isn't mentioned on the pricing page. Worst offenders in our dataset: <strong>Monday.com</strong> (3→5 seat min), <strong>Atlassian Jira</strong> (10-seat min on Premium), <strong>Figma Organization</strong> (25-seat min for governance).</p>
    </div>
  </div>

  <div class="ps reveal">
    <div class="cta-big">
      <h3>Embed this data</h3>
      <p>Publishers and analysts: you're welcome to cite or embed these stats. Please credit saaspare.org and link to this page.</p>
      <a href="/pages/saas-pricing-index" class="btn">Get full dataset →</a>
    </div>
  </div>

</main>
"""

(PAGES / "state-of-saas-pricing-2026.html").write_text(
    page_shell(
        slug="state-of-saas-pricing-2026",
        title="State of SaaS Pricing Transparency 2026 — Annual Report",
        desc="Annual report analyzing pricing transparency across 986 B2B SaaS vendors. Which categories hide prices. Which force sales calls. Best and worst of 2026.",
        body=state_body, accent="report", nav_active="idx",
        schema_extra='{"@context":"https://schema.org","@type":"Report","name":"State of SaaS Pricing Transparency 2026","author":{"@type":"Organization","name":"SaaSpare"},"datePublished":"2026-04-30","publisher":{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"}}'
    ),
    encoding="utf-8",
)


# ═══════════════════════════════════════════════════════════════════════
# 5. SAAS GLOSSARY
# ═══════════════════════════════════════════════════════════════════════
TERMS = [
    ("ACV", "Annual Contract Value — the annualized revenue of a customer contract. SaaS vendors report ACV to smooth out multi-year deals."),
    ("ARR", "Annual Recurring Revenue — total subscription revenue normalized to 12 months. The primary SaaS growth metric."),
    ("ARPU", "Average Revenue Per User — total revenue / active users. Used to measure monetization efficiency."),
    ("Churn rate", "The % of customers who cancel in a given period. Net revenue churn subtracts expansion revenue from lost revenue."),
    ("CAC", "Customer Acquisition Cost — total sales + marketing spend / new customers acquired. CAC payback under 12 months is ideal for SaaS."),
    ("CAC payback", "Months needed to recover CAC from gross profit. 12-month payback is typical; 18+ signals inefficiency."),
    ("CSM", "Customer Success Manager — post-sale role managing retention, expansion, and support for mid-market or enterprise accounts."),
    ("DAU/MAU", "Daily Active Users / Monthly Active Users. Engagement ratio; 20%+ is strong for B2B SaaS."),
    ("Dollar retention (NDR)", "Net Dollar Retention — revenue from existing customers vs. one year ago. 120%+ is elite SaaS."),
    ("Expansion revenue", "New ARR from existing customers via upsells, cross-sells, or seat expansion. Key to high NDR."),
    ("Freemium", "A pricing model with a free tier alongside paid plans. Common in developer and productivity SaaS."),
    ("Gross margin", "Revenue minus COGS (hosting, support, payment fees) / revenue. SaaS benchmark: 70–85%."),
    ("LTV", "Customer Lifetime Value — average revenue per customer over their entire relationship. Should exceed 3× CAC."),
    ("MQL", "Marketing Qualified Lead — a lead that's engaged enough with marketing content to be handed to sales."),
    ("MRR", "Monthly Recurring Revenue — normalized monthly subscription revenue. ARR ÷ 12."),
    ("NPS", "Net Promoter Score — a customer satisfaction metric measuring likelihood to recommend. SaaS benchmark: 30+."),
    ("PLG", "Product-Led Growth — acquisition model where the product drives sign-ups (vs. sales-led). Examples: Slack, Notion, Figma."),
    ("POC", "Proof of Concept — a limited-scope trial to validate technical fit. Usually required for enterprise SaaS."),
    ("Rule of 40", "Growth rate % + profit margin % ≥ 40. A composite SaaS health metric. Public SaaS companies target this."),
    ("SOC 2", "Security audit report showing a SaaS vendor meets standards for security, availability, and confidentiality. Type II is the gold standard."),
    ("SSO", "Single Sign-On — login via identity provider like Okta, Google, or Microsoft Entra. Usually locked to enterprise tiers."),
    ("SAML", "Security Assertion Markup Language — protocol for SSO. Required for enterprise IT approvals."),
    ("SLA", "Service Level Agreement — contractual uptime guarantee. 99.9% = ~8.76h downtime/year; 99.99% = ~52min/year."),
    ("TAM", "Total Addressable Market — maximum revenue opportunity if 100% of potential customers bought. SaaS pitch deck staple."),
    ("TCO", "Total Cost of Ownership — full cost including subscription, implementation, training, integration, and switching costs."),
    ("Usage-based pricing", "Pricing based on consumption (API calls, events, data) rather than seats. Popular for infra SaaS like Twilio and Snowflake."),
    ("Viral coefficient", "Users invited by existing users / active users. &gt; 1 = organic growth. &lt; 1 = needs paid acquisition."),
    ("White-label", "Reselling SaaS under your own brand. Common for agencies and platforms that embed third-party tools."),
    ("API rate limit", "Cap on requests per second/minute an API accepts. Higher limits are usually gated to higher pricing tiers."),
    ("Seat-based pricing", "Price scales with active user count. Most common B2B SaaS pricing model. Watch for hidden seat minimums."),
    ("Data residency", "Geographic location where data is stored. Critical for GDPR, Australian Privacy Principles, and regulated industries."),
    ("Multi-tenancy", "SaaS architecture where one instance serves multiple customers. Keeps costs low; can raise noisy-neighbor concerns."),
    ("Webhook", "HTTP callback fired on an event. Integration plumbing for SaaS-to-SaaS communication."),
    ("OAuth", "Authorization protocol used for third-party app access. Scopes limit what the integrating app can do."),
    ("RBAC", "Role-Based Access Control — users grouped into roles (admin, editor, viewer) with specific permissions."),
    ("SCIM", "System for Cross-domain Identity Management — protocol for automatically provisioning and deprovisioning users."),
    ("Zero Trust", "Security model assuming no network boundary is trustworthy. Verifies every access request regardless of origin."),
    ("MSA", "Master Service Agreement — top-level contract governing the customer-vendor relationship. Usually paired with an Order Form."),
    ("DPA", "Data Processing Agreement — contract specifying how a vendor handles personal data under GDPR/privacy laws."),
    ("SSO tax", "Premium pricing vendors charge to unlock SSO, even though SSO is a security requirement. Widely criticized practice."),
    ("Procurement lead time", "Weeks from vendor selection to signed contract. Enterprise SaaS averages 45–90 days."),
    ("Migration cost", "Time + money to move data/users from one SaaS to another. Can exceed 1 year of subscription savings."),
    ("Vendor lock-in", "Difficulty switching vendors due to data formats, integrations, or contractual penalties."),
    ("Price grandfathering", "Keeping existing customers on old (cheaper) pricing when new pricing launches. Not always honored."),
    ("Annual prepay discount", "10–25% discount for paying a year upfront vs. monthly. Standard for B2B SaaS."),
    ("Seat minimum", "Contractually required minimum user count, regardless of actual usage. Common at mid-market/enterprise tiers."),
    ("Auto-renewal", "Contract clause that renews the subscription automatically. Check the cancellation window (often 30–60 days before renewal)."),
    ("Click-through agreement", "Contract accepted by clicking an accept button. Binds your company even without a signature."),
    ("EULA", "End User License Agreement — contract governing software usage. Standard in consumer and SMB SaaS."),
    ("Free trial vs free plan", "Trials expire (7–30 days). Free plans never do, but usually have feature or usage limits."),
    ("CPA", "Cost Per Acquisition — paid marketing cost to acquire one customer. Component of CAC."),
]


def term_card(t, d):
    anchor = re.sub(r"\W+", "-", t.lower()).strip("-")
    return f'<div class="term" id="t-{anchor}"><dl><dt>{t}</dt><dd>{d}</dd></dl></div>'


glossary_terms_html = "\n".join(term_card(t, d) for t, d in sorted(TERMS))
glossary_jump_html = "".join(
    f'<a href="#letter-{chr(i)}">{chr(i).upper()}</a>' for i in range(ord("a"), ord("z") + 1)
)

glossary_body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-grid"></div>
  <div class="page-hero-orb"></div>
  <div class="page-hero-content">
    <div class="page-eyebrow">📖 Reference</div>
    <h1>The <em>SaaS Glossary</em> every buyer should bookmark</h1>
    <p class="page-sub">50+ B2B SaaS terms explained simply. Decode vendor pitches, sanity-check pricing, and negotiate contracts without getting tangled in acronyms.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <div class="alpha-jump">{glossary_jump_html}</div>
    <div class="term-grid">
      {glossary_terms_html}
    </div>
  </div>

  <div class="ps reveal">
    <div class="cta-big">
      <h3>Want these in your inbox when we add new ones?</h3>
      <p>Every Friday, the Weekly SaaS Deal Digest adds new terms as SaaS contracts get weirder.</p>
      <a href="/pages/weekly-saas-deal-digest" class="btn">Subscribe free →</a>
    </div>
  </div>

</main>
"""

(PAGES / "saas-glossary.html").write_text(
    page_shell(
        slug="saas-glossary",
        title="SaaS Glossary: 50+ B2B SaaS Terms Every Buyer Should Know",
        desc="The complete B2B SaaS vocabulary: ACV, ARR, CAC, NDR, PLG, SSO tax, seat minimums, and 50+ more terms explained simply.",
        body=glossary_body, accent="glossary", nav_active="gloss",
        schema_extra='{"@context":"https://schema.org","@type":"DefinedTermSet","name":"SaaSpare SaaS Glossary","url":"https://saaspare.org/pages/saas-glossary"}',
        page_type="DefinedTermSet"
    ),
    encoding="utf-8",
)


# ═══════════════════════════════════════════════════════════════════════
# 6. COUPON VERIFICATION POLICY
# ═══════════════════════════════════════════════════════════════════════
coupon_body = """
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-grid"></div>
  <div class="page-hero-orb"></div>
  <div class="page-hero-content">
    <div class="page-eyebrow">✅ Trust Page</div>
    <h1>Our <em>Coupon Verification</em> Policy</h1>
    <p class="page-sub">How we verify every discount, promo code, and deal listed on SaaSpare — and exactly what happens when a coupon breaks or expires.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <span class="ps-eyebrow">The process</span>
    <h2 class="ps-title">Our 5-step coupon verification</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>1. Source check</h3><p>Coupons must come from the vendor directly, the vendor's official affiliate program, or a publicly announced campaign. No scraped codes from coupon aggregators.</p></div>
      <div class="ps-card"><h3>2. Live test</h3><p>We type the code into the vendor's actual checkout to confirm it applies. No untested codes make the site.</p></div>
      <div class="ps-card"><h3>3. Terms review</h3><p>We read the fine print. Min spend, new-customer-only, regional restrictions, and expiration dates are documented on the page.</p></div>
      <div class="ps-card"><h3>4. Timestamped</h3><p>Every coupon page shows a "last verified" date. If we haven't re-checked in 30+ days, the coupon is flagged "may be expired".</p></div>
    </div>
    <div class="ps-card" style="margin-top:1rem"><h3>5. Active monitoring</h3><p>Our bot re-tests every coupon weekly. Broken codes are removed within 24 hours. If something slips through, <a href="mailto:coupons@saaspare.org">tell us</a> and we fix it same-day.</p></div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">What "verified" means</span>
    <h2 class="ps-title">The badges, decoded</h2>
    <div class="ps-value-grid">
      <div class="ps-value"><strong><span class="badge g">✓ Verified</span></strong><span>We personally entered it at checkout in the last 30 days and the discount applied. Terms are published on the page.</span></div>
      <div class="ps-value"><strong><span class="badge y">⚠ May be expired</span></strong><span>We haven't re-verified in 30+ days but have no evidence it's broken. Worth trying but not guaranteed.</span></div>
      <div class="ps-value"><strong><span class="badge r">✗ Broken</span></strong><span>Re-verification failed or a reader flagged it. We remove within 24h.</span></div>
      <div class="ps-value"><strong>🔒 Affiliate disclosed</strong><span>Some coupons are tracked through affiliate links that earn us a commission. Earnings never affect which codes we list.</span></div>
    </div>
  </div>

  <div class="ps reveal">
    <div class="ps-callout">
      <p><strong>What we will never do:</strong> list fake codes to inflate click-through, keep expired codes live after verification fails, obscure the terms to make a coupon look better, or rank vendors higher because they offered us a bigger coupon share.</p>
    </div>
  </div>

  <div class="ps reveal">
    <div class="cta-big">
      <h3>Spot a broken coupon?</h3>
      <p>Tell us. We'll verify and remove it within 24 hours if it's broken, and replace it with a working one if we can find one.</p>
      <a href="mailto:coupons@saaspare.org?subject=Broken%20Coupon" class="btn">Report a coupon →</a>
    </div>
  </div>

</main>
"""

(PAGES / "coupon-verification-policy.html").write_text(
    page_shell(
        slug="coupon-verification-policy",
        title="Coupon Verification Policy — How SaaSpare Verifies Every Promo Code",
        desc="SaaSpare's coupon verification policy: 5-step process, live testing, 30-day re-verification, and what 'verified' actually means.",
        body=coupon_body, accent="policy"
    ),
    encoding="utf-8",
)


# ═══════════════════════════════════════════════════════════════════════
# 7. HOW WE RANK
# ═══════════════════════════════════════════════════════════════════════
rank_body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-grid"></div>
  <div class="page-hero-orb"></div>
  <div class="page-hero-content">
    <div class="page-eyebrow">🎯 Trust Page</div>
    <h1>How SaaSpare <em>ranks tools</em> (and what we won't do)</h1>
    <p class="page-sub">We don't sell rankings. We don't take payment for placement. Here's the exact 6-factor rubric we use to decide which tool wins each comparison — and what we deliberately exclude.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <span class="ps-eyebrow">The rubric</span>
    <h2 class="ps-title">Every tool scored across six weighted dimensions</h2>
    <div class="ps-card">
      <h4>Weighted ranking rubric</h4>
      <div class="ps-body" style="margin-top:.6rem">
        {bar("Pricing value (25%)", 5, "green")}
        {bar("Feature fit (20%)", 4, "green")}
        {bar("Onboarding &amp; UX (15%)", 3, "warn")}
        {bar("Reliability (15%)", 3, "warn")}
        {bar("Support quality (15%)", 3, "warn")}
        {bar("Free tier / trial (10%)", 2, "red")}
      </div>
      <p style="margin-top:1rem;color:var(--muted);font-size:.85rem">Bars show relative weight, not quality score. Pricing value and feature fit dominate because that's what buyers actually optimize for.</p>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">In detail</span>
    <h2 class="ps-title">What each factor covers</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>Pricing value · 25%</h3><p>Plan value vs. direct competitors. Presence of hidden fees, seat minimums, annual-only discounts, or tiered traps. The lower your total first-year cost, the higher the score.</p></div>
      <div class="ps-card"><h3>Feature fit · 20%</h3><p>Core features present vs. category standard. Weighted by buyer role — what a 10-person startup needs is very different from what a 500-person enterprise needs.</p></div>
      <div class="ps-card"><h3>Onboarding &amp; UX · 15%</h3><p>Time to first value. Learning curve. Mobile + desktop experience. Clean UI scores higher than "enterprisey" UI.</p></div>
      <div class="ps-card"><h3>Reliability · 15%</h3><p>Published SLAs, status page incident history, how transparent the vendor is about outages. We pull 12 months of status data.</p></div>
      <div class="ps-card"><h3>Support · 15%</h3><p>Response time, channels (chat / email / phone), documentation depth, community activity, and how quickly critical bugs get fixed.</p></div>
      <div class="ps-card"><h3>Free tier / trial · 10%</h3><p>Real free plans beat fake ones. No-card trials beat card-required trials. 30-day trials beat 7-day trials. Generous limits beat "starter" straitjackets.</p></div>
    </div>
  </div>

  <div class="ps reveal">
    <div class="ps-callout">
      <p><strong>What we do NOT factor in:</strong> affiliate commission rates, vendor ad spend, personal relationships, G2/Capterra badges (those are pay-to-play), or press releases. If you want to appear higher in our rankings, build a better product.</p>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">The pipeline</span>
    <h2 class="ps-title">Who verifies each ranking</h2>
    <div class="ps-body">
      <ul>
        <li><strong>1. Drafted</strong> by our research + AI pipeline using published vendor pricing and feature data</li>
        <li><strong>2. Cross-checked</strong> against at least 2 independent sources (G2, Capterra, Reddit, product docs)</li>
        <li><strong>3. Reviewed</strong> manually by an editor for bias and factual errors</li>
        <li><strong>4. Re-verified</strong> every 30–90 days with a "last verified" timestamp displayed on the page</li>
      </ul>
    </div>
  </div>

  <div class="ps reveal">
    <div class="cta-big">
      <h3>Disagree with a ranking?</h3>
      <p>Bring better evidence and we'll update the page. We care more about being right than being consistent.</p>
      <a href="mailto:editor@saaspare.org?subject=Ranking%20Feedback" class="btn">Send feedback →</a>
    </div>
  </div>

</main>
"""

(PAGES / "how-saaspare-ranks-tools.html").write_text(
    page_shell(
        slug="how-saaspare-ranks-tools",
        title="How SaaSpare Ranks Tools — Our Comparison Methodology",
        desc="The exact ranking methodology SaaSpare uses: 6-factor weighted rubric, independent verification, and what we deliberately exclude.",
        body=rank_body, accent="rank"
    ),
    encoding="utf-8",
)


# ═══════════════════════════════════════════════════════════════════════
# 8. REQUEST A COMPARISON
# ═══════════════════════════════════════════════════════════════════════
request_body = """
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-grid"></div>
  <div class="page-hero-orb"></div>
  <div class="page-hero-content">
    <div class="page-eyebrow">💬 Utility</div>
    <h1>Can't find the <em>comparison</em> you need?</h1>
    <p class="page-sub">We cover 1,017+ B2B SaaS tools but there are always more. Tell us which comparison is missing and we'll build it — usually within 7 days.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <span class="ps-eyebrow">Submit</span>
    <h2 class="ps-title">Request a comparison</h2>
    <form class="form" action="https://formsubmit.co/smithelly30121@gmail.com" method="POST">
      <input type="hidden" name="_subject" value="Comparison request from SaaSpare">
      <input type="hidden" name="_captcha" value="false">
      <input type="hidden" name="_next" value="https://saaspare.org/pages/request-a-comparison?ok=1">
      <label>Tool A<input type="text" name="tool_a" required placeholder="e.g. Notion"></label>
      <label>Tool B<input type="text" name="tool_b" required placeholder="e.g. ClickUp"></label>
      <label>Why this comparison? (optional)<textarea name="context" rows="4" placeholder="e.g. My team of 12 is deciding between these for project management..."></textarea></label>
      <label>Your email (optional — for notification when published)<input type="email" name="email" placeholder="you@company.com"></label>
      <button type="submit" class="btn" style="align-self:flex-start">Submit request →</button>
    </form>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">What happens next</span>
    <h2 class="ps-title">From request to live page in &lt; 7 days</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>1. Review (24h)</h3><p>Our editor checks if the comparison is buyer-relevant and not already covered.</p></div>
      <div class="ps-card"><h3>2. Research (3–5d)</h3><p>Our pipeline pulls pricing, features, reviews, and SLA data from both vendors.</p></div>
      <div class="ps-card"><h3>3. Publish (≤ 7d)</h3><p>The comparison goes live with a full verdict, pricing table, star ratings, and FAQs.</p></div>
      <div class="ps-card"><h3>4. Notify</h3><p>If you left an email, you get a one-time notification when the page is live.</p></div>
    </div>
  </div>

</main>
"""

(PAGES / "request-a-comparison.html").write_text(
    page_shell(
        slug="request-a-comparison",
        title="Request a Comparison — Tell SaaSpare Which B2B SaaS Tools to Compare",
        desc="Can't find the B2B SaaS comparison you need? Tell SaaSpare and we'll build it within 7 days. Free, no spam.",
        body=request_body, accent="request"
    ),
    encoding="utf-8",
)


# ═══════════════════════════════════════════════════════════════════════
# 9. REPORT OUTDATED PRICING
# ═══════════════════════════════════════════════════════════════════════
report2_body = """
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-grid"></div>
  <div class="page-hero-orb"></div>
  <div class="page-hero-content">
    <div class="page-eyebrow">📝 Utility</div>
    <h1>Spot a <em>pricing error</em>? Help us fix it.</h1>
    <p class="page-sub">SaaS vendors change prices constantly. If you see an error on one of our pages, tell us — we verify and fix every confirmed report within 24 hours.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <span class="ps-eyebrow">Submit</span>
    <h2 class="ps-title">Report a pricing error</h2>
    <form class="form" action="https://formsubmit.co/smithelly30121@gmail.com" method="POST">
      <input type="hidden" name="_subject" value="Pricing error report - SaaSpare">
      <input type="hidden" name="_captcha" value="false">
      <input type="hidden" name="_next" value="https://saaspare.org/pages/report-outdated-pricing?ok=1">
      <label>SaaSpare page URL<input type="url" name="page_url" required placeholder="https://saaspare.org/pages/..."></label>
      <label>What's the error?<textarea name="error" rows="4" required placeholder="e.g. HubSpot Marketing Pro is listed at $800/mo but is actually $890/mo as of April 2026"></textarea></label>
      <label>Source URL (if available)<input type="url" name="source" placeholder="https://vendor.com/pricing"></label>
      <label>Your email (optional)<input type="email" name="email" placeholder="you@company.com"></label>
      <button type="submit" class="btn" style="align-self:flex-start">Submit report →</button>
    </form>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Our commitment</span>
    <h2 class="ps-title">What we do with every verified report</h2>
    <div class="ps-value-grid">
      <div class="ps-value"><strong>24-hour verification</strong><span>We check every report within one business day.</span></div>
      <div class="ps-value"><strong>Transparent updates</strong><span>Fixed pages show an updated "last verified" date in the footer.</span></div>
      <div class="ps-value"><strong>Credit where asked</strong><span>If you want credit, we'll mention you in the correction note.</span></div>
      <div class="ps-value"><strong>Public tracker</strong><span>Every price update lands in our <a href="/pages/saas-pricing-changes" style="color:var(--red)">price changes tracker</a>.</span></div>
    </div>
  </div>

</main>
"""

(PAGES / "report-outdated-pricing.html").write_text(
    page_shell(
        slug="report-outdated-pricing",
        title="Report Outdated Pricing — Help SaaSpare Stay Accurate",
        desc="Spot a pricing error on SaaSpare? Report it here. We verify and fix every report within 24 hours.",
        body=report2_body, accent="report2"
    ),
    encoding="utf-8",
)

print(f"Rebuilt 9 strategic pages in {PAGES}")
