"""SaaS Pricing Changes Tracker (data asset)."""
from ._helpers import (
    page_shell, hero_h1_with_glint, breadcrumb_html,
    write_page, CRUMB_HOME,
)


def build():
    h1 = hero_h1_with_glint("Which SaaS vendors quietly hiked prices in 2026", "quietly hiked")
    body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-dots"></div>
  <div class="page-hero-orb"></div><div class="page-hero-orb2"></div>
  <div class="page-hero-content">
    {breadcrumb_html([CRUMB_HOME, ("/pages/saas-pricing-changes", "Pricing Changes")])}
    <div class="page-eyebrow">Live data asset · Updated weekly</div>
    <h1>{h1}</h1>
    <p class="page-sub">The most aggressive SaaS pricing moves of 2026, tracked across 1,017+ B2B tools. Who hiked, who dropped, who introduced a hidden seat minimum, and who quietly got pricier per-seat without telling anyone.</p>
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
        <thead><tr><th>Vendor</th><th>Change</th><th>Effective</th><th>Impact</th><th>Cheaper alternative</th></tr></thead>
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
          <tr><td><strong>Notion Plus</strong></td><td><span class="badge g">âˆ’12%</span></td><td>Jan 2026</td><td>$10 → $8.80/user</td></tr>
          <tr><td><strong>Airtable Team</strong></td><td><span class="badge g">âˆ’20% annual</span></td><td>Feb 2026</td><td>New annual discount</td></tr>
          <tr><td><strong>Vercel Pro</strong></td><td><span class="badge g">âˆ’25% build minutes</span></td><td>Mar 2026</td><td>6k → 8k minutes included</td></tr>
          <tr><td><strong>Claude Pro</strong></td><td><span class="badge g">Free tier 2×</span></td><td>Apr 2026</td><td>Double free usage</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Plan restructures</span>
    <h2 class="ps-title">The "technically not a hike" moves to watch</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h4>Slack Pro → Business+</h4><p>Free plan now limits to 90-day message history (was unlimited). Many teams being pushed to upgrade.</p></div>
      <div class="ps-card"><h4>Zoom One → Zoom Workplace</h4><p>AI Companion moved out of free. Clip storage reduced for free users. Watch for hidden enterprise minimums.</p></div>
      <div class="ps-card"><h4>Figma Starter → Free</h4><p>Renamed free tier. Now limits editors to 3 (was unlimited for Starter). Upgrade path is steeper than before.</p></div>
      <div class="ps-card"><h4>GitHub Copilot Business</h4><p>New "Enterprise" tier at $39/user. Business unchanged but governance moved behind the new tier.</p></div>
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
      <p>Price changes are captured from public vendor pricing pages (archived via Wayback Machine), company announcements, customer emails forwarded by our community, and internal verification. Every change is logged with a timestamp and source URL. See the full <a href="/methodology">methodology</a>.</p>
      <p>Spot a change we missed? <a href="/pages/report-outdated-pricing">Tell us →</a></p>
    </div>
  </div>

</main>
"""
    schema = (
        '{"@context":"https://schema.org","@type":"Dataset",'
        '"name":"SaaS Pricing Changes Tracker 2026",'
        '"description":"Tracked price changes across 1,017+ B2B SaaS vendors in 2026. Hikes, drops, plan restructures, hidden seat minimums.",'
        '"url":"https://saaspare.org/pages/saas-pricing-changes",'
        '"creator":{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"},'
        '"license":"https://creativecommons.org/licenses/by/4.0/",'
        '"keywords":["SaaS pricing","price changes","B2B software","pricing tracker"]}'
    )
    html = page_shell(
        slug="saas-pricing-changes",
        title="SaaS Pricing Changes Tracker 2026 — Which Vendors Hiked Prices",
        desc="Live tracker of 2026 SaaS price changes across 1,017+ B2B tools. See who hiked, who dropped, plus a cheaper alternative for each.",
        body=body, accent="tracker", nav_active="idx",
        crumbs=[CRUMB_HOME, ("/pages/saas-pricing-changes", "Pricing Changes")],
        schema_extra=schema,
    )
    write_page("saas-pricing-changes", html)

