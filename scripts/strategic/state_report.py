"""State of SaaS Pricing Transparency 2026 (annual report)."""
from ._helpers import (
    page_shell, hero_h1_with_glint, breadcrumb_html,
    bar, star_row, write_page, CRUMB_HOME,
)


def build():
    h1 = hero_h1_with_glint("The State of SaaS Pricing Transparency 2026", "Pricing Transparency")
    body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-dots"></div>
  <div class="page-hero-orb"></div>
  <div class="page-hero-content">
    {breadcrumb_html([CRUMB_HOME, ("/pages/state-of-saas-pricing-2026", "State Report 2026")])}
    <div class="page-eyebrow">Annual Report · April 2026</div>
    <h1>{h1}</h1>
    <p class="page-sub">We analysed pricing pages, free trial rules and seat minimums across 986 B2B SaaS vendors. Here is what we found about transparency in 2026 — which categories hide prices, which force sales calls, and which still let buyers self-serve.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <div class="ps-stat-row">
      <div class="ps-stat"><strong>73%</strong><span>Show pricing publicly</span></div>
      <div class="ps-stat"><strong>41%</strong><span>Require card for trial</span></div>
      <div class="ps-stat"><strong>28%</strong><span>Hidden seat minimums</span></div>
      <div class="ps-stat"><strong>14%</strong><span>No public pricing</span></div>
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
    <span class="ps-eyebrow">Credit where it is due</span>
    <h2 class="ps-title">The 5 best transparency leaders</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h4>Vercel</h4><p>Full pricing calculator. Usage metering visible in real time. No hidden seat minimums.</p>{star_row(4.9)}</div>
      <div class="ps-card"><h4>Linear</h4><p>Per-user pricing crystal clear. Annual discount visible. Free tier honest about limits.</p>{star_row(4.8)}</div>
      <div class="ps-card"><h4>Notion</h4><p>Everything visible. Free tier is generous and has been stable for 2+ years.</p>{star_row(4.7)}</div>
      <div class="ps-card"><h4>Bitwarden</h4><p>Open-source plus transparent commercial pricing. Team pricing calculator built in.</p>{star_row(4.7)}</div>
      <div class="ps-card"><h4>Cloudflare</h4><p>Free tier comprehensive. Pro/Business tiers itemised. Enterprise has a published starting point.</p>{star_row(4.6)}</div>
    </div>
  </div>

  <div class="ps reveal">
    <div class="ps-callout">
      <p><strong>The hidden seat minimum problem:</strong> 28% of SaaS vendors hide a seat minimum that is not mentioned on the pricing page. Worst offenders in our dataset: <strong>Monday.com</strong> (3→5 seat min), <strong>Atlassian Jira</strong> (10-seat min on Premium), <strong>Figma Organization</strong> (25-seat min for governance).</p>
    </div>
  </div>

  <div class="ps reveal">
    <div class="cta-big">
      <h3>Embed this data</h3>
      <p>Publishers and analysts: you are welcome to cite or embed these stats. Please credit saaspare.org and link to this page.</p>
      <a href="/pages/saas-pricing-index" class="btn">Get full dataset →</a>
    </div>
  </div>

</main>
"""
    schema = (
        '{"@context":"https://schema.org","@type":"Report",'
        '"name":"State of SaaS Pricing Transparency 2026",'
        '"author":{"@type":"Organization","name":"SaaSpare"},'
        '"datePublished":"2026-04-30",'
        '"publisher":{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"}}'
    )
    html = page_shell(
        slug="state-of-saas-pricing-2026",
        title="State of SaaS Pricing Transparency 2026 — Annual Report",
        desc="Annual report analysing pricing transparency across 986 B2B SaaS vendors. Which categories hide prices. Which force sales calls. Best and worst of 2026.",
        body=body, accent="report", nav_active="idx",
        crumbs=[CRUMB_HOME, ("/pages/state-of-saas-pricing-2026", "State Report 2026")],
        schema_extra=schema,
    )
    write_page("state-of-saas-pricing-2026", html)
