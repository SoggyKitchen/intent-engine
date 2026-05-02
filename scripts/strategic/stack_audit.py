"""SaaS Stack Audit (productized) + checkout flow."""
from ._helpers import (
    page_shell, hero_h1_with_glint, breadcrumb_html,
    bar, write_page, CRUMB_HOME, PAGES,
)


def build():
    h1 = hero_h1_with_glint("Find the SaaS you forgot you were paying for", "you forgot")
    body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-dots"></div>
  <div class="page-hero-orb"></div><div class="page-hero-orb2"></div>
  <div class="page-hero-content">
    {breadcrumb_html([CRUMB_HOME, ("/pages/saas-spend-audit", "SaaS Stack Audit")])}
    <div class="page-eyebrow">Productized Audit · 5–7 day turnaround</div>
    <h1>{h1}</h1>
    <p class="page-sub">An independent audit of your full SaaS stack. We hunt down ghost subscriptions, overlapping tools, unused seats, and weak renewals — then hand you an itemised receipt of every dollar you can recover this year.</p>
    <div class="page-hero-actions">
      <a href="/pages/saas-stack-audit-checkout?tier=audit" class="btn">Start the Stack Audit · A$99</a>
      <a href="#tiers" class="btn ghost">Compare tiers</a>
    </div>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <div class="ps-stat-row">
      <div class="ps-stat"><strong>27%</strong><span>Avg savings found</span></div>
      <div class="ps-stat"><strong>5–7 days</strong><span>Turnaround</span></div>
      <div class="ps-stat"><strong>1,017+</strong><span>Tools tracked</span></div>
      <div class="ps-stat"><strong>30 day</strong><span>Money-back guarantee</span></div>
    </div>
  </div>

  <div class="ps reveal" id="tiers">
    <span class="ps-eyebrow">Three tiers · One-off pricing</span>
    <h2 class="ps-title">Pick the depth that fits your stack</h2>
    <p class="ps-body" style="margin-bottom:1rem">Flat fee, no retainer, no "book a call" gate. If we cannot identify at least 3Ã— the audit cost in recoverable annual savings we refund in full.</p>
    <div class="plan-grid">

      <div class="plan">
        <div class="plan-name">Tier 01 · DIY toolkit</div>
        <div class="plan-tag">Stack <em>Brief</em></div>
        <div class="plan-pitch">Everything you need to audit your own stack in one afternoon. No human review.</div>
        <div class="plan-price">A$29<small> one-time</small></div>
        <ul class="plan-list">
          <li>Audit spreadsheet template</li>
          <li>40+ vendor renewal scripts</li>
          <li>Hidden seat-minimum checklist</li>
          <li>Renewal calendar tracker</li>
          <li>Pricing database (1,017 tools)</li>
          <li class="x">No human review</li>
        </ul>
        <a href="/pages/saas-stack-audit-checkout?tier=brief" class="plan-cta" data-tier="brief">Get the toolkit â†’</a>
      </div>

      <div class="plan featured">
        <div class="plan-name">Tier 02 · Most picked</div>
        <div class="plan-tag">Stack <em>Audit</em></div>
        <div class="plan-pitch">You send us your stack. We send back a 20-page report of what to cancel, switch, and renegotiate.</div>
        <div class="plan-price">A$99<small> one-time</small></div>
        <ul class="plan-list">
          <li>Everything in Stack Brief</li>
          <li>Manual review of your full stack</li>
          <li>Shadow-SaaS detection (personal-card subs)</li>
          <li>Ranked savings report (PDF + CSV)</li>
          <li>Usage-matched alternatives</li>
          <li>20-min strategy call</li>
          <li>14-day email follow-up</li>
        </ul>
        <a href="/pages/saas-stack-audit-checkout?tier=audit" class="plan-cta" data-tier="audit">Start the Stack Audit â†’</a>
      </div>

      <div class="plan">
        <div class="plan-name">Tier 03 · Done for you</div>
        <div class="plan-tag">Stack <em>Concierge</em></div>
        <div class="plan-pitch">For teams of 20+. We pick up the phone, call vendors, and renegotiate on your behalf.</div>
        <div class="plan-price">A$299<small> one-time</small></div>
        <ul class="plan-list">
          <li>Everything in Stack Audit</li>
          <li>We contact 3 vendors on your behalf</li>
          <li>Renewal-calendar automation setup</li>
          <li>Stack health scorecard dashboard</li>
          <li>30-day follow-up + second review</li>
          <li>Guaranteed savings or full refund</li>
          <li>Mutual NDA available</li>
        </ul>
        <a href="/pages/saas-stack-audit-checkout?tier=concierge" class="plan-cta" data-tier="concierge">Request Concierge â†’</a>
      </div>

    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">What competitors miss</span>
    <h2 class="ps-title">Five differentiators Ramp, Brex and spreadsheets cannot replicate</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>Shadow SaaS detection</h3><p>We surface subscriptions paid on personal cards and expensed back. The average mid-size startup hides A$400/mo this way.</p></div>
      <div class="ps-card"><h3>Renewal calendar</h3><p>Every auto-renewal date, notice window and cancellation clause extracted into one calendar so a surprise auto-renewal never costs you another year.</p></div>
      <div class="ps-card"><h3>Stack health scorecard</h3><p>Your stack scored across cost, overlap, usage and security posture. You learn the three tools to kill first for the biggest payback.</p></div>
      <div class="ps-card"><h3>Usage-matched alternatives</h3><p>We match your real seat count, feature usage and integrations to a realistic switching cost — not a generic "try Linear" recommendation.</p></div>
      <div class="ps-card"><h3>Forwardable savings receipt</h3><p>You receive a dollar-exact receipt showing every dollar recoverable in the next 12 months, ranked by difficulty. Forwardable straight to your CFO.</p></div>
      <div class="ps-card"><h3>Negotiation scripts</h3><p>The exact email and phone scripts that unlock 10–30% off at renewal. Tested on Salesforce, HubSpot, Slack, Notion, Atlassian and 30+ more.</p></div>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">A real scorecard</span>
    <h2 class="ps-title">What the Stack Audit hands back</h2>
    <div class="ps-card">
      <h4>Sample scorecard (anonymised)</h4>
      <div class="ps-body" style="margin-top:.6rem">
        {bar("Cost efficiency", 2.4, "red")}
        {bar("Tool overlap", 1.8, "red")}
        {bar("Unused seats", 2.9, "warn")}
        {bar("Negotiation leverage", 3.6, "warn")}
        {bar("Security posture", 4.2, "green")}
        <p style="margin-top:1rem;color:var(--muted);font-size:.86rem">This client had A$5,200/mo of SaaS. We found A$1,480/mo of it was recoverable within 90 days. Audit cost: A$99.</p>
      </div>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Transparent process</span>
    <h2 class="ps-title">How an audit runs end-to-end</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>1. Intake (Day 0)</h3><p>You complete a short form: stack list, seat counts, contract terms, pain points. Takes ~10 minutes.</p></div>
      <div class="ps-card"><h3>2. Cross-check (Days 1–3)</h3><p>We verify pricing against vendor pages, our database of 1,017 tools, and Wayback archives for hidden hikes.</p></div>
      <div class="ps-card"><h3>3. Synthesis (Days 3–5)</h3><p>Findings ranked by recoverable dollars and switching difficulty. You get the report as PDF + CSV.</p></div>
      <div class="ps-card"><h3>4. Strategy call (Day 5–7)</h3><p>We walk through the report, prioritise the top three actions, and answer questions. 20 min, recorded if you want.</p></div>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Frequent questions</span>
    <h2 class="ps-title">FAQs</h2>
    <details class="faq"><summary>How much can I realistically save?</summary><p>Across 1,017 tracked tools, the typical B2B stack has 20–40% of spend recoverable. A team spending A$5k/month usually finds A$1,000–A$2,000/month within 90 days.</p></details>
    <details class="faq"><summary>Do I have to actually cancel anything?</summary><p>No. Most savings come from (1) dropping unused seats, (2) renegotiating renewals, (3) downgrading plans you have outgrown. Switching tools is a last resort — the first year of switching cost usually outweighs the savings.</p></details>
    <details class="faq"><summary>Is the A$29 Stack Brief enough on its own?</summary><p>For founders with 5–15 tools and under 10 people, yes. For larger stacks the A$99 Stack Audit pays for itself in the first renewal you touch.</p></details>
    <details class="faq"><summary>Will you sign an NDA?</summary><p>Yes — standard mutual NDA available on Stack Audit and Stack Concierge. Email <a href="mailto:audit@saaspare.org">audit@saaspare.org</a>.</p></details>
    <details class="faq"><summary>What if you find nothing?</summary><p>Stack Audit and Stack Concierge come with a 30-day money-back guarantee. If we cannot identify at least 3Ã— your audit fee in recoverable annual savings, full refund.</p></details>
    <details class="faq"><summary>How is this different from Vendr, Tropic or Sastrify?</summary><p>Those are enterprise procurement platforms charging A$10k+/year to manage your stack ongoing. The Stack Audit is a one-off audit for founders and ops leads who want the savings without the platform contract.</p></details>
    <details class="faq"><summary>Is my data safe?</summary><p>All audit data is processed in the EU/AU and deleted 30 days after delivery unless you request retention. NDA available on request.</p></details>
  </div>

  <div class="ps reveal">
    <div class="cta-big">
      <h3>Most audits pay for themselves on the first renewal you touch</h3>
      <p>Average savings per audit: A$3,000–A$15,000 in the first year. The A$99 Stack Audit pays back inside the first renewal cycle.</p>
      <a href="/pages/saas-stack-audit-checkout?tier=audit" class="btn">Start the Stack Audit · A$99</a>
      <a href="/pages/saas-stack-audit-checkout?tier=brief" class="btn ghost" style="margin-left:.6rem">Or try Stack Brief · A$29</a>
    </div>
  </div>

</main>
"""
    schema = (
        '{"@context":"https://schema.org","@type":"Service",'
        '"name":"SaaSpare Stack Audit",'
        '"provider":{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"},'
        '"description":"Independent productised audit of your B2B SaaS stack. Identify duplicate tools, unused seats, overpricing, and cheaper alternatives.",'
        '"serviceType":"SaaS Cost Optimisation","areaServed":"Worldwide",'
        '"offers":[{"@type":"Offer","name":"Stack Brief","price":"29","priceCurrency":"AUD","url":"https://saaspare.org/pages/saas-stack-audit-checkout?tier=brief"},'
        '{"@type":"Offer","name":"Stack Audit","price":"99","priceCurrency":"AUD","url":"https://saaspare.org/pages/saas-stack-audit-checkout?tier=audit"},'
        '{"@type":"Offer","name":"Stack Concierge","price":"299","priceCurrency":"AUD","url":"https://saaspare.org/pages/saas-stack-audit-checkout?tier=concierge"}]}'
    )
    html = page_shell(
        slug="saas-spend-audit",
        title="SaaS Stack Audit — Find Hidden SaaS Costs in 5–7 Days",
        desc="Independent audit of your full SaaS stack. Catch ghost subscriptions, unused seats, weak renewals. Three tiers from A$29 to A$299. 30-day money-back guarantee.",
        body=body, accent="spend",
        crumbs=[CRUMB_HOME, ("/pages/saas-spend-audit", "SaaS Stack Audit")],
        schema_extra=schema, page_type="Service",
    )
    write_page("saas-spend-audit", html)


def build_checkout():
    h1 = hero_h1_with_glint("Start your SaaS Stack Audit", "Stack Audit")
    body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-dots"></div>
  <div class="page-hero-orb"></div><div class="page-hero-orb2"></div>
  <div class="page-hero-content">
    {breadcrumb_html([CRUMB_HOME, ("/pages/saas-spend-audit", "SaaS Stack Audit"), ("/pages/saas-stack-audit-checkout", "Start audit")])}
    <div class="page-eyebrow">Secure intake · Pay after we confirm</div>
    <h1>{h1}</h1>
    <p class="page-sub">Tell us your stack and pick a tier. We confirm fit by email within 1 business day, send a single Stripe payment link, and start work the day payment clears.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <span class="ps-eyebrow">Step 1 · Intake</span>
    <h2 class="ps-title">Stack Audit intake form</h2>
    <p class="ps-body" style="margin-bottom:1.4rem">All fields are private. We only use this to build the audit. <strong>No payment is taken at this step.</strong></p>
    <form class="form" action="https://formsubmit.co/audit@saaspare.org" method="POST">
      <input type="hidden" name="_subject" value="New SaaS Stack Audit intake">
      <input type="hidden" name="_captcha" value="false">
      <input type="hidden" name="_template" value="table">
      <input type="hidden" name="_next" value="https://saaspare.org/pages/saas-stack-audit-checkout?ok=1">
      <input type="hidden" name="_autoresponse" value="Thanks. We confirm your Stack Audit fit within 1 business day and send a single Stripe payment link. Reply with any questions to audit@saaspare.org. — SaaSpare">

      <label>Tier
        <select name="tier" id="tier" required>
          <option value="brief">Stack Brief — A$29 (DIY toolkit)</option>
          <option value="audit" selected>Stack Audit — A$99 (most picked)</option>
          <option value="concierge">Stack Concierge — A$299 (done for you)</option>
        </select>
      </label>

      <label>Your name<input type="text" name="name" required placeholder="Jane Founder"></label>
      <label>Work email<input type="email" name="email" required placeholder="jane@company.com"></label>
      <label>Company<input type="text" name="company" required placeholder="Acme Pty Ltd"></label>
      <label>Country<input type="text" name="country" placeholder="Australia"></label>

      <label>Approx. SaaS tools in your stack
        <select name="stack_size" required>
          <option value="">—</option>
          <option value="1-10">1–10 tools</option>
          <option value="11-25">11–25 tools</option>
          <option value="26-50">26–50 tools</option>
          <option value="51+">51+ tools</option>
        </select>
      </label>

      <label>Approx. monthly SaaS spend (AUD)
        <select name="spend" required>
          <option value="">—</option>
          <option value="under-1k">Under A$1,000</option>
          <option value="1k-5k">A$1,000 – A$5,000</option>
          <option value="5k-15k">A$5,000 – A$15,000</option>
          <option value="15k-50k">A$15,000 – A$50,000</option>
          <option value="50k+">A$50,000+</option>
        </select>
      </label>

      <label>Biggest pain point (optional)<textarea name="pain" rows="4" placeholder="e.g. We just got hit with a 28% Salesforce hike and have 7 overlapping tools we cannot untangle..."></textarea></label>

      <label style="flex-direction:row;align-items:flex-start;gap:.6rem;font-weight:500;font-size:.84rem;color:var(--muted)">
        <input type="checkbox" name="nda" value="yes" style="margin-top:4px;width:auto;flex:0 0 auto"> I would like a mutual NDA before sharing my stack list (no extra cost).
      </label>

      <button type="submit" class="btn" style="align-self:flex-start;margin-top:.4rem">Submit intake â†’</button>
      <p style="font-size:.74rem;color:var(--dim);margin:0">By submitting you agree to our <a href="/privacy">privacy policy</a>. We confirm fit before charging anything.</p>
    </form>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">What happens next</span>
    <h2 class="ps-title">From intake to delivery</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>Day 0 · Confirm fit</h3><p>You receive a confirmation email within 1 business day. We answer any questions and send a single Stripe payment link for the tier you picked.</p></div>
      <div class="ps-card"><h3>Day 0–1 · Payment</h3><p>One-click Stripe checkout. Apple Pay, Google Pay, card. Receipt issued automatically. Australian GST applied where applicable.</p></div>
      <div class="ps-card"><h3>Day 1–5 · Audit</h3><p>We verify every line of your stack against pricing pages, our database, and (for Concierge) the vendors themselves.</p></div>
      <div class="ps-card"><h3>Day 5–7 · Delivery</h3><p>You get the report (PDF + CSV) and a 20-minute strategy call. Concierge tier includes a second review at day 30.</p></div>
    </div>
  </div>

  <div class="ps reveal">
    <div class="ps-callout">
      <p><strong>30-day money-back guarantee.</strong> Stack Audit and Stack Concierge: if we cannot identify at least 3Ã— your audit fee in recoverable annual savings, full refund — no questions, no fine print.</p>
    </div>
  </div>

  <div class="ps reveal">
    <div class="cta-big">
      <h3>Prefer to chat first?</h3>
      <p>Email <a href="mailto:audit@saaspare.org">audit@saaspare.org</a> with your situation and we will reply within 1 business day with a recommendation.</p>
      <a href="mailto:audit@saaspare.org?subject=Stack%20Audit%20question" class="btn ghost">Email us instead</a>
    </div>
  </div>

</main>
<script>
(function(){{
  var params=new URLSearchParams(location.search);
  var t=params.get('tier');
  if(t&&document.getElementById('tier')){{document.getElementById('tier').value=t;}}
  if(params.get('ok')==='1'){{
    var box=document.createElement('div');
    box.style.cssText='position:fixed;top:90px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#65d6a3,#4eb88a);color:#0c1f16;padding:.85rem 1.4rem;border-radius:100px;font-weight:800;z-index:300;box-shadow:0 10px 36px rgba(0,0,0,.3);font-size:.88rem';
    box.textContent='\u2713 Intake received. Watch your inbox for the payment link.';
    document.body.appendChild(box);
    setTimeout(function(){{box.style.transition='opacity .4s';box.style.opacity='0';}},6000);
  }}
}})();
</script>
"""
    schema = (
        '{"@context":"https://schema.org","@type":"WebPage",'
        '"name":"Start your SaaS Stack Audit",'
        '"description":"Intake form for the SaaSpare Stack Audit. Pick a tier and we confirm fit within 1 business day before any payment is taken.",'
        '"potentialAction":{"@type":"OrderAction","target":"https://saaspare.org/pages/saas-stack-audit-checkout","name":"Start the Stack Audit"}}'
    )
    html = page_shell(
        slug="saas-stack-audit-checkout",
        title="Start your SaaS Stack Audit — SaaSpare Checkout",
        desc="Intake form for the SaaSpare Stack Audit. Pick a tier (A$29 / A$99 / A$299), submit your stack, get a Stripe payment link within 1 business day.",
        body=body, accent="checkout",
        crumbs=[CRUMB_HOME, ("/pages/saas-spend-audit", "SaaS Stack Audit"), ("/pages/saas-stack-audit-checkout", "Start audit")],
        schema_extra=schema, page_type="WebPage",
    )
    write_page("saas-stack-audit-checkout", html)

