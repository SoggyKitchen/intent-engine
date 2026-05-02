"""Trust pages: coupon policy, ranking methodology."""
from ._helpers import (
    page_shell, hero_h1_with_glint, breadcrumb_html,
    bar, write_page, CRUMB_HOME,
)


def build_coupon_policy():
    h1 = hero_h1_with_glint("Our Coupon Verification Policy", "Coupon Verification")
    body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-dots"></div>
  <div class="page-hero-orb"></div><div class="page-hero-orb2"></div>
  <div class="page-hero-content">
    {breadcrumb_html([CRUMB_HOME, ("/pages/coupon-verification-policy", "Coupon Policy")])}
    <div class="page-eyebrow">Trust Page</div>
    <h1>{h1}</h1>
    <p class="page-sub">How we verify every discount, promo code, and deal listed on SaaSpare â€” and exactly what happens when a coupon breaks or expires.</p>
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
      <div class="ps-card"><h3>4. Timestamped</h3><p>Every coupon page shows a "last verified" date. If we have not re-checked in 30+ days, the coupon is flagged "may be expired".</p></div>
    </div>
    <div class="ps-card" style="margin-top:1rem"><h3>5. Active monitoring</h3><p>Our bot re-tests every coupon weekly. Broken codes are removed within 24 hours. If something slips through, <a href="mailto:coupons@saaspare.org">tell us</a> and we fix it same day.</p></div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">What "verified" means</span>
    <h2 class="ps-title">The badges, decoded</h2>
    <div class="ps-value-grid">
      <div class="ps-value"><strong><span class="badge g">âœ“ Verified</span></strong><span>We personally entered it at checkout in the last 30 days and the discount applied. Terms are published on the page.</span></div>
      <div class="ps-value"><strong><span class="badge y">âš  May be expired</span></strong><span>We have not re-verified in 30+ days but have no evidence it is broken. Worth trying but not guaranteed.</span></div>
      <div class="ps-value"><strong><span class="badge r">âœ— Broken</span></strong><span>Re-verification failed or a reader flagged it. We remove within 24h.</span></div>
      <div class="ps-value"><strong>ðŸ”’ Affiliate disclosed</strong><span>Some coupons are tracked through affiliate links that earn us a commission. Earnings never affect which codes we list.</span></div>
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
      <p>Tell us. We verify and remove broken codes within 24 hours, and replace them with a working one if we can find one.</p>
      <a href="mailto:coupons@saaspare.org?subject=Broken%20Coupon" class="btn">Report a coupon â†’</a>
    </div>
  </div>

</main>
"""
    html = page_shell(
        slug="coupon-verification-policy",
        title="Coupon Verification Policy â€” How SaaSpare Verifies Every Promo Code",
        desc="SaaSpare's coupon verification policy: 5-step process, live testing, 30-day re-verification, and what 'verified' actually means.",
        body=body, accent="policy",
        crumbs=[CRUMB_HOME, ("/pages/coupon-verification-policy", "Coupon Policy")],
    )
    write_page("coupon-verification-policy", html)


def build_rank_methodology():
    h1 = hero_h1_with_glint("How SaaSpare ranks tools (and what we will not do)", "ranks tools")
    body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-dots"></div>
  <div class="page-hero-orb"></div><div class="page-hero-orb2"></div>
  <div class="page-hero-content">
    {breadcrumb_html([CRUMB_HOME, ("/pages/how-saaspare-ranks-tools", "How We Rank")])}
    <div class="page-eyebrow">Editorial Standards</div>
    <h1>{h1}</h1>
    <p class="page-sub">We do not sell rankings. We do not take payment for placement. Here is the exact 6-factor rubric we use to decide which tool wins each comparison â€” and what we deliberately exclude.</p>
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
        {bar("Onboarding & UX (15%)", 3, "warn")}
        {bar("Reliability (15%)", 3, "warn")}
        {bar("Support quality (15%)", 3, "warn")}
        {bar("Free tier / trial (10%)", 2, "red")}
      </div>
      <p style="margin-top:1rem;color:var(--muted);font-size:.85rem">Bars show relative weight, not quality score. Pricing value and feature fit dominate because that is what buyers actually optimise for.</p>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">In detail</span>
    <h2 class="ps-title">What each factor covers</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>Pricing value Â· 25%</h3><p>Plan value vs. direct competitors. Presence of hidden fees, seat minimums, annual-only discounts, or tiered traps. Lower total first-year cost scores higher.</p></div>
      <div class="ps-card"><h3>Feature fit Â· 20%</h3><p>Core features present vs. category standard. Weighted by buyer role â€” what a 10-person startup needs differs from what a 500-person enterprise needs.</p></div>
      <div class="ps-card"><h3>Onboarding & UX Â· 15%</h3><p>Time to first value. Learning curve. Mobile + desktop experience. Clean UI scores higher than "enterprisey" UI.</p></div>
      <div class="ps-card"><h3>Reliability Â· 15%</h3><p>Published SLAs, status page incident history, how transparent the vendor is about outages. We pull 12 months of status data.</p></div>
      <div class="ps-card"><h3>Support Â· 15%</h3><p>Response time, channels (chat / email / phone), documentation depth, community activity, and how quickly critical bugs get fixed.</p></div>
      <div class="ps-card"><h3>Free tier / trial Â· 10%</h3><p>Real free plans beat fake ones. No-card trials beat card-required trials. 30-day trials beat 7-day trials. Generous limits beat starter straitjackets.</p></div>
    </div>
  </div>

  <div class="ps reveal">
    <div class="ps-callout">
      <p><strong>What we deliberately do not score on:</strong> brand recognition, marketing budget, partnership status with us, or whether a vendor will pay for a "sponsored review". Affiliate revenue is disclosed on the affiliate page and never influences ranking.</p>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Reviewer process</span>
    <h2 class="ps-title">How a comparison gets built</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>1. Define the buyer</h3><p>Every comparison declares its target buyer (e.g. "10-person SaaS startup", "200-person agency"). Scoring is weighted to that buyer.</p></div>
      <div class="ps-card"><h3>2. Hands-on test</h3><p>We sign up for both tools, complete the core workflow, and document friction points with screenshots.</p></div>
      <div class="ps-card"><h3>3. Pricing reconstruction</h3><p>We model 1-year total cost for the declared buyer, including known seat minimums and annual-only discounts.</p></div>
      <div class="ps-card"><h3>4. Cross-check sources</h3><p>Reviews, status pages, GitHub issues, community forums. We weight independent sources over vendor-provided ones.</p></div>
      <div class="ps-card"><h3>5. Verdict + dissent</h3><p>Final verdict written. If two reviewers disagree we publish the dissent inline rather than averaging it away.</p></div>
      <div class="ps-card"><h3>6. Annual re-review</h3><p>Every comparison is re-scored at least once a year. Most are re-scored quarterly. Stale comparisons are flagged.</p></div>
    </div>
  </div>

  <div class="ps reveal">
    <div class="cta-big">
      <h3>Spot a comparison that needs updating?</h3>
      <p>If a vendor changed pricing or shipped a major feature, we want to know â€” and re-score within 14 days.</p>
      <a href="/pages/report-outdated-pricing" class="btn">Report it â†’</a>
    </div>
  </div>

</main>
"""
    html = page_shell(
        slug="how-saaspare-ranks-tools",
        title="How SaaSpare Ranks Tools â€” Editorial Standards & Methodology",
        desc="Our 6-factor ranking rubric, hands-on test process, and what we deliberately do NOT score on. Editorial independence at SaaSpare.",
        body=body, accent="rank",
        crumbs=[CRUMB_HOME, ("/pages/how-saaspare-ranks-tools", "How We Rank")],
    )
    write_page("how-saaspare-ranks-tools", html)

