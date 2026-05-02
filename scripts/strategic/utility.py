"""Utility forms: request-a-comparison, report-outdated-pricing."""
from ._helpers import (
    page_shell, hero_h1_with_glint, breadcrumb_html,
    write_page, CRUMB_HOME,
)


def build_request():
    h1 = hero_h1_with_glint("Request a SaaS comparison", "comparison")
    body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-dots"></div>
  <div class="page-hero-orb"></div><div class="page-hero-orb2"></div>
  <div class="page-hero-content">
    {breadcrumb_html([CRUMB_HOME, ("/pages/request-a-comparison", "Request a comparison")])}
    <div class="page-eyebrow">Tell us what to compare next</div>
    <h1>{h1}</h1>
    <p class="page-sub">Stuck choosing between two SaaS tools and cannot find an honest, side-by-side, deeply-researched comparison? Tell us. The most-requested comparisons jump the queue and we publish them in 7–14 days.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <span class="ps-eyebrow">Submit a request</span>
    <h2 class="ps-title">What should we compare?</h2>
    <p class="ps-body" style="margin-bottom:1.4rem">Free, unbiased, and we credit you when the comparison ships. Most-requested pairs jump the queue.</p>
    <form class="form" action="https://formsubmit.co/requests@saaspare.org" method="POST">
      <input type="hidden" name="_subject" value="New comparison request">
      <input type="hidden" name="_captcha" value="false">
      <input type="hidden" name="_next" value="https://saaspare.org/pages/request-a-comparison?ok=1">

      <label>Tool A<input type="text" name="tool_a" required placeholder="e.g. Linear"></label>
      <label>Tool B<input type="text" name="tool_b" required placeholder="e.g. Jira"></label>
      <label>Or 3+ tools (optional)<input type="text" name="more_tools" placeholder="e.g. ClickUp, Monday, Asana"></label>

      <label>Your role
        <select name="role">
          <option value="">—</option>
          <option>Founder / CEO</option>
          <option>Engineering / Dev</option>
          <option>Product</option>
          <option>Marketing</option>
          <option>Sales</option>
          <option>Operations / Finance</option>
          <option>Other</option>
        </select>
      </label>

      <label>Team size
        <select name="team_size">
          <option value="">—</option>
          <option>1–5</option>
          <option>6–25</option>
          <option>26–100</option>
          <option>101–500</option>
          <option>500+</option>
        </select>
      </label>

      <label>What is the deciding question for you? (optional)<textarea name="context" rows="4" placeholder="e.g. We're scaling to 50 engineers and Jira's pricing is brutal. Linear looks great but I'm worried about the migration cost..."></textarea></label>

      <label>Email (so we can credit you)<input type="email" name="email" placeholder="you@company.com"></label>

      <button type="submit" class="btn" style="align-self:flex-start;margin-top:.4rem">Submit request →</button>
      <p style="font-size:.74rem;color:var(--dim);margin:0">By submitting you agree to our <a href="/privacy">privacy policy</a>.</p>
    </form>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">What happens next</span>
    <h2 class="ps-title">The 14-day path from request to publish</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>Day 0 · Logged</h3><p>We log your request and add a vote. Identical pairs aggregate so popular requests jump the queue.</p></div>
      <div class="ps-card"><h3>Day 1–3 · Hands-on test</h3><p>We sign up for both tools and complete the core workflow. We document friction points with screenshots.</p></div>
      <div class="ps-card"><h3>Day 3–10 · Synthesis</h3><p>Pricing modelled, support tested, status page reviewed, dissent recorded. Then drafted.</p></div>
      <div class="ps-card"><h3>Day 10–14 · Publish</h3><p>Comparison published, you receive an email with the link, and you are credited as the requester (or anonymous if preferred).</p></div>
    </div>
  </div>

</main>
<script>
(function(){{
  var p=new URLSearchParams(location.search);
  if(p.get('ok')==='1'){{
    var box=document.createElement('div');
    box.style.cssText='position:fixed;top:90px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#65d6a3,#4eb88a);color:#0c1f16;padding:.85rem 1.4rem;border-radius:100px;font-weight:800;z-index:300;box-shadow:0 10px 36px rgba(0,0,0,.3);font-size:.88rem';
    box.textContent='\u2713 Got it. We\\'ll email you when the comparison ships.';
    document.body.appendChild(box);
    setTimeout(function(){{box.style.transition='opacity .4s';box.style.opacity='0';}},6000);
  }}
}})();
</script>
"""
    html = page_shell(
        slug="request-a-comparison",
        title="Request a SaaS Comparison — Tell SaaSpare What to Compare Next",
        desc="Stuck choosing between two SaaS tools? Submit a comparison request. We publish requested comparisons in 7–14 days, free and unbiased.",
        body=body, accent="request",
        crumbs=[CRUMB_HOME, ("/pages/request-a-comparison", "Request a comparison")],
    )
    write_page("request-a-comparison", html)


def build_report_pricing():
    h1 = hero_h1_with_glint("Report outdated SaaS pricing", "outdated SaaS pricing")
    body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-dots"></div>
  <div class="page-hero-orb"></div><div class="page-hero-orb2"></div>
  <div class="page-hero-content">
    {breadcrumb_html([CRUMB_HOME, ("/pages/report-outdated-pricing", "Report pricing")])}
    <div class="page-eyebrow">Help us stay accurate</div>
    <h1>{h1}</h1>
    <p class="page-sub">Spotted a vendor that changed pricing, killed a plan, raised a seat minimum, or quietly hiked at renewal? Tell us. We re-verify within 24 hours and update the live page within 48.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <span class="ps-eyebrow">Report a change</span>
    <h2 class="ps-title">What did the vendor change?</h2>
    <form class="form" action="https://formsubmit.co/pricing@saaspare.org" method="POST">
      <input type="hidden" name="_subject" value="Outdated pricing report">
      <input type="hidden" name="_captcha" value="false">
      <input type="hidden" name="_next" value="https://saaspare.org/pages/report-outdated-pricing?ok=1">

      <label>Vendor<input type="text" name="vendor" required placeholder="e.g. HubSpot"></label>

      <label>Type of change
        <select name="change_type" required>
          <option value="">—</option>
          <option>Price hike</option>
          <option>Price drop</option>
          <option>Plan restructure / renamed</option>
          <option>Plan killed / removed</option>
          <option>Hidden seat minimum added</option>
          <option>Free tier reduced</option>
          <option>Free trial rules changed</option>
          <option>Other</option>
        </select>
      </label>

      <label>What changed (be specific)<textarea name="change_detail" rows="5" required placeholder="e.g. Marketing Pro went from $890/mo to $1,020/mo on Jan 15. New annual prepay discount is now 14% (was 10%). Saw it on their pricing page today."></textarea></label>

      <label>Source link (pricing page, announcement, screenshot URL)<input type="url" name="source" placeholder="https://..."></label>

      <label>Page on saaspare.org we should update (optional)<input type="text" name="page" placeholder="e.g. /pages/hubspot-pricing-2026..."></label>

      <label>Your email (so we can credit you)<input type="email" name="email" placeholder="you@company.com"></label>

      <button type="submit" class="btn" style="align-self:flex-start;margin-top:.4rem">Submit report →</button>
      <p style="font-size:.74rem;color:var(--dim);margin:0">We verify every report. Verified reporters get credited on the updated page (or stay anonymous, your call).</p>
    </form>
  </div>

  <div class="ps reveal">
    <div class="ps-callout">
      <p><strong>Faster path:</strong> if you have a screenshot or a customer email from the vendor, attach it via a free image host (Imgur, etc.) and paste the link in the source field. Visual evidence cuts our verification time in half.</p>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">What happens next</span>
    <h2 class="ps-title">From your report to a corrected page</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>1. Logged within 1 hour</h3><p>Your report is logged automatically and emailed to the editorial team.</p></div>
      <div class="ps-card"><h3>2. Verified within 24h</h3><p>We cross-check the vendor's pricing page, the Wayback archive, and any source you sent us.</p></div>
      <div class="ps-card"><h3>3. Page updated within 48h</h3><p>If verified, the live page is updated and added to the <a href="/pages/saas-pricing-changes">tracker</a>.</p></div>
      <div class="ps-card"><h3>4. You get credit</h3><p>We email you with the link and credit you on the page (or skip the credit if you prefer).</p></div>
    </div>
  </div>

</main>
<script>
(function(){{
  var p=new URLSearchParams(location.search);
  if(p.get('ok')==='1'){{
    var box=document.createElement('div');
    box.style.cssText='position:fixed;top:90px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#65d6a3,#4eb88a);color:#0c1f16;padding:.85rem 1.4rem;border-radius:100px;font-weight:800;z-index:300;box-shadow:0 10px 36px rgba(0,0,0,.3);font-size:.88rem';
    box.textContent='\u2713 Thanks. We\\'ll verify and update within 48 hours.';
    document.body.appendChild(box);
    setTimeout(function(){{box.style.transition='opacity .4s';box.style.opacity='0';}},6000);
  }}
}})();
</script>
"""
    html = page_shell(
        slug="report-outdated-pricing",
        title="Report Outdated SaaS Pricing — Help Keep SaaSpare Accurate",
        desc="Spotted a vendor that changed pricing? Tell us. We re-verify within 24 hours and update the live page within 48.",
        body=body, accent="report2",
        crumbs=[CRUMB_HOME, ("/pages/report-outdated-pricing", "Report pricing")],
    )
    write_page("report-outdated-pricing", html)

