"""Weekly SaaS Deal Digest newsletter page."""
from ._helpers import (
    page_shell, hero_h1_with_glint, breadcrumb_html,
    write_page, CRUMB_HOME,
)


def build():
    h1 = hero_h1_with_glint("The 7 best SaaS deals of the week, in your inbox", "best SaaS deals")
    body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-dots"></div>
  <div class="page-hero-orb"></div>
  <div class="page-hero-content">
    {breadcrumb_html([CRUMB_HOME, ("/pages/weekly-saas-deal-digest", "Weekly Deal Digest")])}
    <div class="page-eyebrow">Every Friday · Free forever</div>
    <h1>{h1}</h1>
    <p class="page-sub">Verified discounts, expiring free trials, fresh entrants worth watching, and quiet price hikes nobody else is tracking. 3-minute read. One email per week. Never sold, never shared.</p>
    <form class="email-row" action="https://formsubmit.co/smithelly30121@gmail.com" method="POST">
      <input type="email" name="email" placeholder="you@company.com" required>
      <input type="hidden" name="_subject" value="Newsletter signup: Weekly SaaS Deal Digest">
      <input type="hidden" name="_captcha" value="false">
      <input type="hidden" name="_next" value="https://saaspare.org/pages/weekly-saas-deal-digest?ok=1">
      <button type="submit">Join 2,000+ buyers →</button>
    </form>
    <p style="font-size:.76rem;margin-top:.8rem;color:var(--dim)">One-click unsubscribe. Zero affiliate spam disguised as deals.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <span class="ps-eyebrow">Inside every issue</span>
    <h2 class="ps-title">Six sections. All evidence. No filler.</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>Verified deals</h3><p>Only coupons we have personally tested on the real vendor checkout this week. If the discount did not apply when we tried it, it does not make the email.</p></div>
      <div class="ps-card"><h3>Expiring trials</h3><p>Free trials ending soon — especially the rare no-credit-card ones worth grabbing before they go behind a sales call.</p></div>
      <div class="ps-card"><h3>One launch worth watching</h3><p>One new B2B tool we actually find interesting, usually with launch-week discounts nobody else is tracking yet.</p></div>
      <div class="ps-card"><h3>Quiet price changes</h3><p>Which vendors pushed up pricing this week. Which killed a plan. Which added a hidden seat minimum at renewal.</p></div>
      <div class="ps-card"><h3>Swap of the week</h3><p>One overpriced tool, one cheaper alternative, the real switching cost, and whether we would actually do it ourselves.</p></div>
      <div class="ps-card"><h3>Reader Q&amp;A</h3><p>One buyer question answered each week. Reply to any email to submit yours — if it runs, we credit you.</p></div>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Past issues</span>
    <h2 class="ps-title">A taste of what to expect</h2>
    <div class="ps-card">
      <div class="ps-body">
        <ul>
          <li><strong>Issue #28:</strong> HubSpot Marketing Pro dropping 20% — and why it is a trap if you are under 1,000 contacts</li>
          <li><strong>Issue #27:</strong> 3 DocuSign alternatives under A$10/mo that hold up in court</li>
          <li><strong>Issue #26:</strong> Why Ramp's "free" card gets expensive past 50 employees (and why Brex is not the answer)</li>
          <li><strong>Issue #25:</strong> 6 tools that quietly raised prices last month — check your renewal dates</li>
          <li><strong>Issue #24:</strong> The cheapest SaaS analytics stack we have ever seen (Amplitude + Segment replacement under A$50/mo)</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="ps reveal">
    <div class="cta-big">
      <h3>Free forever. Always has been.</h3>
      <p>Join 2,000+ founders, CTOs and ops leaders who use the digest to save A$5k–A$50k/year on SaaS they no longer need.</p>
      <form class="email-row" action="https://formsubmit.co/smithelly30121@gmail.com" method="POST">
        <input type="email" name="email" placeholder="you@company.com" required>
        <input type="hidden" name="_subject" value="Newsletter signup (CTA): Weekly SaaS Deal Digest">
        <input type="hidden" name="_captcha" value="false">
        <button type="submit">Subscribe free →</button>
      </form>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Frequent questions</span>
    <h2 class="ps-title">FAQs</h2>
    <details class="faq"><summary>How often will I get emails?</summary><p>Once per week, every Friday at 9 AM UTC. No drip sequences. No "P.S. did you see this?" follow-ups. No upsell blasts.</p></details>
    <details class="faq"><summary>Do you sell my email?</summary><p>Never. We are allergic to list brokers. See our <a href="/privacy">privacy policy</a>.</p></details>
    <details class="faq"><summary>Are the deals actually good?</summary><p>We only include deals we would personally use. If a coupon does not work when we test it, we do not send it. If a "free trial" is not genuinely free, we do not list it.</p></details>
    <details class="faq"><summary>Can I submit a tip?</summary><p>Reply to any email. We read every response. If your tip runs, we credit you.</p></details>
  </div>

</main>
"""
    schema = (
        '{"@context":"https://schema.org","@type":"WebPage",'
        '"name":"Weekly SaaS Deal Digest",'
        '"description":"Free weekly newsletter rounding up the best B2B SaaS deals, free trials and price changes."}'
    )
    html = page_shell(
        slug="weekly-saas-deal-digest",
        title="Weekly SaaS Deal Digest — Best B2B SaaS Deals Every Friday",
        desc="Join 2,000+ founders getting the best verified B2B SaaS deals, price changes and free trials every Friday. Free, one email per week.",
        body=body, accent="digest",
        crumbs=[CRUMB_HOME, ("/pages/weekly-saas-deal-digest", "Weekly Deal Digest")],
        schema_extra=schema,
    )
    write_page("weekly-saas-deal-digest", html)
