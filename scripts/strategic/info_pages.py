"""About + Privacy rebuilt with the shared shell."""
from ._helpers import (
    page_shell, hero_h1_with_glint, breadcrumb_html,
    write_page, CRUMB_HOME, SITE,
)


def build_about():
    h1 = hero_h1_with_glint("About SaaSpare", "SaaSpare")
    body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-dots"></div>
  <div class="page-hero-orb"></div><div class="page-hero-orb2"></div>
  <div class="page-hero-content">
    {breadcrumb_html([CRUMB_HOME, ("/about", "About")])}
    <div class="page-eyebrow">Independent · Australian-owned · Built since 2024</div>
    <h1>{h1}</h1>
    <p class="page-sub">Honest, hands-on B2B SaaS comparisons with one rule we will not break: we do not sell rankings. Started in 2024 because every "Top 10 SaaS Tools" list on Google was secretly an affiliate ad in disguise.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <span class="ps-eyebrow">The team</span>
    <h2 class="ps-title">Built by Kaylan von Papen</h2>
    <div class="ps-card">
      <p style="color:rgba(255,255,255,.78);font-size:1rem;line-height:1.7">Hi, I'm Kaylan — founder and lead reviewer at SaaSpare. I built this after spending six years in B2B SaaS ops and getting tired of "review" sites that were really paid placement schemes. SaaSpare is the comparison resource I wish existed when I was making procurement decisions: hands-on tested, transparently scored, fully disclosed.</p>
      <p style="color:rgba(255,255,255,.78);font-size:1rem;line-height:1.7;margin-top:1rem">Based in Australia. Reachable at <a href="mailto:hello@saaspare.org">hello@saaspare.org</a>.</p>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">What we publish</span>
    <h2 class="ps-title">Five things you will find on SaaSpare</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>Tool-vs-tool comparisons</h3><p>Side-by-side breakdowns of competing SaaS, scored against the SaaSpare 6-factor rubric. Every comparison declares its target buyer.</p></div>
      <div class="ps-card"><h3>Pricing pages</h3><p>Plain-English breakdowns of each vendor's pricing, including the seat minimums and gotchas they bury in the fine print.</p></div>
      <div class="ps-card"><h3>Best-of roundups</h3><p>Category roundups for buyers researching their first or fifth tool in a category.</p></div>
      <div class="ps-card"><h3>The pricing tracker</h3><p>Live data on which SaaS vendors hiked, dropped, or restructured prices each month.</p></div>
      <div class="ps-card"><h3>The Stack Audit</h3><p>Our paid productised service: a full audit of your SaaS stack, delivered in 5–7 days, with savings receipts.</p></div>
      <div class="ps-card"><h3>The Weekly Digest</h3><p>One email each Friday with the best verified deals, expiring trials, and price changes of the week.</p></div>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Editorial principles</span>
    <h2 class="ps-title">What we will and will not do</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>We will</h3><p>Publish dissent inline. Re-score quarterly. Flag affiliate links. Update pages within 48h of a verified change. Recommend tools we have not paid for. Refund audits that find nothing.</p></div>
      <div class="ps-card"><h3>We will not</h3><p>Sell rankings. Take payment for placement. Rewrite a verdict because a vendor complained. Hide affiliate disclosures. Use AI-generated comparisons without a hands-on test.</p></div>
    </div>
  </div>

  <div class="ps reveal">
    <div class="ps-callout">
      <p><strong>How we make money:</strong> a small fraction of comparisons earn affiliate commissions when readers click through and sign up. The Stack Audit is a paid service. We are exploring sponsored content with a clear "Sponsored" tag — but only for vendors we already independently rated above 4/5. See our <a href="/affiliate-disclosure">affiliate disclosure</a>.</p>
    </div>
  </div>

  <div class="ps reveal">
    <div class="cta-big">
      <h3>Got a question?</h3>
      <p>Editorial questions, partnership requests, or just want to say hi — we read every email.</p>
      <a href="mailto:hello@saaspare.org" class="btn">hello@saaspare.org</a>
      <a href="/contact" class="btn ghost" style="margin-left:.6rem">Contact form</a>
    </div>
  </div>

</main>
"""
    schema = (
        '{"@context":"https://schema.org","@type":"AboutPage",'
        '"name":"About SaaSpare",'
        '"description":"Independent, hands-on B2B SaaS comparisons. Founded by Kaylan von Papen in 2024.",'
        '"mainEntity":{"@type":"Person","name":"Kaylan von Papen","url":"https://saaspare.org/about","jobTitle":"Founder","worksFor":{"@type":"Organization","name":"SaaSpare"}}}'
    )
    html = page_shell(
        slug="about",
        title="About SaaSpare — Independent B2B SaaS Comparisons",
        desc="SaaSpare is independent, hands-on B2B SaaS comparison platform. Founded by Kaylan von Papen in 2024. We do not sell rankings.",
        body=body, accent="about",
        crumbs=[CRUMB_HOME, ("/about", "About")],
        canonical_path="/about",
        schema_extra=schema, page_type="AboutPage",
    )
    (SITE / "about.html").write_text(html, encoding="utf-8")


def build_privacy():
    h1 = hero_h1_with_glint("Privacy Policy", "Privacy")
    body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-dots"></div>
  <div class="page-hero-orb"></div><div class="page-hero-orb2"></div>
  <div class="page-hero-content">
    {breadcrumb_html([CRUMB_HOME, ("/privacy", "Privacy Policy")])}
    <div class="page-eyebrow">Last updated · April 2026</div>
    <h1>{h1}</h1>
    <p class="page-sub">The plain-English version: we collect the minimum needed to run the site, never sell your data, and give you full control to delete anything we hold. The legal version is below.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <span class="ps-eyebrow">TL;DR</span>
    <h2 class="ps-title">Plain-English summary</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>What we collect</h3><p>Anonymous analytics (Google Analytics 4), email if you subscribe to the newsletter, form submissions if you contact us or buy a Stack Audit. That's it.</p></div>
      <div class="ps-card"><h3>What we do not collect</h3><p>We do not collect your IP-linked browsing history, we do not run fingerprinting scripts, and we do not share data with brokers, list rentals, or "co-marketing" partners.</p></div>
      <div class="ps-card"><h3>Your rights</h3><p>You can request deletion of any personal data we hold by emailing <a href="mailto:privacy@saaspare.org">privacy@saaspare.org</a>. We action requests within 14 days.</p></div>
      <div class="ps-card"><h3>Cookies</h3><p>We use Google Analytics + Google AdSense cookies. EU/UK visitors see a consent banner. Adblockers and DNT signals are honoured.</p></div>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Full policy</span>
    <h2 class="ps-title">1. Who we are</h2>
    <div class="ps-body">
      <p>SaaSpare is operated by Kaylan von Papen, ABN 51 824 753 556, registered in Australia. Contact: <a href="mailto:privacy@saaspare.org">privacy@saaspare.org</a>.</p>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">2. What we collect</h2>
    <div class="ps-body">
      <p><strong>Analytics:</strong> Google Analytics 4 collects anonymised page views, device type, country, and referrer. We use this only to understand which articles are useful.</p>
      <p><strong>Newsletter:</strong> if you subscribe to the Weekly SaaS Deal Digest we collect your email address. Stored with FormSubmit + our internal CRM. Used only to send the newsletter you signed up for.</p>
      <p><strong>Forms:</strong> contact form, Stack Audit intake, comparison requests, pricing reports — these collect what you tell them. Submissions are emailed to us via FormSubmit and retained for as long as needed to act on them.</p>
      <p><strong>Affiliate clicks:</strong> when you click through to a vendor we may add an affiliate tracking parameter. The vendor sees the click, not us.</p>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">3. What we do not collect</h2>
    <div class="ps-body">
      <ul>
        <li>No fingerprinting scripts, no session replay, no heatmap tools.</li>
        <li>No data brokers, no list rentals, no "co-marketing" partners.</li>
        <li>No selling of email lists. Ever.</li>
        <li>No cross-site tracking pixels beyond Google Analytics + AdSense (which Chrome and Safari already restrict).</li>
      </ul>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">4. Cookies</h2>
    <div class="ps-body">
      <p>We use the following cookies: <strong>_ga</strong> and <strong>_ga_*</strong> (Google Analytics), Google AdSense ad-personalisation cookies (where consent is given), and a single first-party preference cookie that remembers if you have dismissed the cookie banner.</p>
      <p>EU/UK visitors see a consent banner. Do Not Track headers are honoured.</p>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">5. Your rights</h2>
    <div class="ps-body">
      <p>Under GDPR (if you are in the EU), the UK Data Protection Act, the Australian Privacy Principles, and the CCPA (if you are in California), you have the right to:</p>
      <ul>
        <li>Access any personal data we hold about you.</li>
        <li>Request correction of inaccurate data.</li>
        <li>Request deletion of your data ("right to be forgotten").</li>
        <li>Opt out of processing for marketing.</li>
        <li>Lodge a complaint with your data protection authority.</li>
      </ul>
      <p>Email <a href="mailto:privacy@saaspare.org">privacy@saaspare.org</a> with your request. We respond within 14 days.</p>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">6. Data retention</h2>
    <div class="ps-body">
      <p>Newsletter subscriptions: kept until you unsubscribe. Stack Audit data: deleted 30 days after delivery unless you request retention. Form submissions: kept up to 24 months for support and abuse-prevention. Analytics: anonymised; standard GA4 retention (14 months).</p>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">7. Changes to this policy</h2>
    <div class="ps-body">
      <p>We update this page when our practices change. The last-updated date at the top reflects the most recent revision. Substantive changes are announced in the Weekly SaaS Deal Digest.</p>
    </div>
  </div>

  <div class="ps reveal">
    <div class="cta-big">
      <h3>Privacy questions?</h3>
      <p>Email <a href="mailto:privacy@saaspare.org">privacy@saaspare.org</a> — we read and respond to every privacy request within 14 days.</p>
      <a href="mailto:privacy@saaspare.org" class="btn">privacy@saaspare.org</a>
    </div>
  </div>

</main>
"""
    html = page_shell(
        slug="privacy",
        title="Privacy Policy — SaaSpare",
        desc="SaaSpare's plain-English privacy policy. We collect the minimum needed, never sell your data, and give you full control to delete anything we hold.",
        body=body, accent="trust",
        crumbs=[CRUMB_HOME, ("/privacy", "Privacy Policy")],
        canonical_path="/privacy",
    )
    (SITE / "privacy.html").write_text(html, encoding="utf-8")


def build_contact():
    h1 = hero_h1_with_glint("Contact SaaSpare", "SaaSpare")
    body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-dots"></div>
  <div class="page-hero-orb"></div><div class="page-hero-orb2"></div>
  <div class="page-hero-content">
    {breadcrumb_html([CRUMB_HOME, ("/contact", "Contact")])}
    <div class="page-eyebrow">Corrections · partnerships · requests</div>
    <h1>{h1}</h1>
    <p class="page-sub">Use the fastest path below so the right SaaSpare workflow gets your message: pricing corrections, comparison requests, partnership enquiries, or editorial questions.</p>
  </div>
</section>
<main class="page-content">

  <div class="ps reveal">
    <span class="ps-eyebrow">Fast routes</span>
    <h2 class="ps-title">What do you need?</h2>
    <div class="ps-grid-2">
      <a class="ps-card" href="/pages/report-outdated-pricing">
        <h3>Report outdated pricing</h3>
        <p>Send a vendor source and we will verify pricing, free-trial, coupon, or plan changes before updating affected pages.</p>
      </a>
      <a class="ps-card" href="/pages/request-a-comparison">
        <h3>Request a comparison</h3>
        <p>Ask for a tool-vs-tool, pricing, alternative, or free-trial guide. High-demand requests move up the queue.</p>
      </a>
      <a class="ps-card" href="mailto:partnerships@saaspare.org">
        <h3>Partnerships</h3>
        <p>For affiliate managers, SaaS vendors, networks, PR teams, and collaboration requests. Email partnerships@saaspare.org.</p>
      </a>
      <a class="ps-card" href="mailto:hello@saaspare.org">
        <h3>General editorial</h3>
        <p>Questions about methodology, page accuracy, research, or SaaSpare's buyer-first comparison policy.</p>
      </a>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Contact form</span>
    <h2 class="ps-title">Send a message</h2>
    <form class="form" action="https://formsubmit.co/hello@saaspare.org" method="POST">
      <input type="hidden" name="_subject" value="SaaSpare contact form">
      <input type="hidden" name="_captcha" value="false">
      <input type="hidden" name="_next" value="https://saaspare.org/contact?ok=1">
      <label>Your email<input type="email" name="email" required placeholder="you@company.com"></label>
      <label>Topic
        <select name="topic" required>
          <option value="">Choose one</option>
          <option>Pricing correction</option>
          <option>Comparison request</option>
          <option>Partnership / affiliate program</option>
          <option>Press / research</option>
          <option>General question</option>
        </select>
      </label>
      <label>Message<textarea name="message" rows="5" required placeholder="Tell us what changed, what you need compared, or which partnership program you want SaaSpare to review."></textarea></label>
      <button type="submit" class="btn" style="align-self:flex-start">Send message -></button>
      <p style="font-size:.74rem;color:var(--dim);margin:0">No spam. Your message is only used to reply or update SaaSpare content.</p>
    </form>
  </div>

  <div class="ps reveal">
    <div class="ps-callout">
      <p><strong>Important:</strong> partnerships@saaspare.org and hello@saaspare.org must exist in your email provider or Cloudflare Email Routing. The site can display them now, but inbox delivery depends on DNS/email routing being configured.</p>
    </div>
  </div>

</main>
<script>
(function(){{
  var p=new URLSearchParams(location.search);
  if(p.get('ok')==='1'){{
    var box=document.createElement('div');
    box.style.cssText='position:fixed;top:90px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#65d6a3,#4eb88a);color:#0c1f16;padding:.85rem 1.4rem;border-radius:100px;font-weight:800;z-index:300;box-shadow:0 10px 36px rgba(0,0,0,.3);font-size:.88rem';
    box.textContent='Message sent.';
    document.body.appendChild(box);
    setTimeout(function(){{box.style.transition='opacity .4s';box.style.opacity='0';}},6000);
  }}
}})();
</script>
"""
    schema = (
        '{"@context":"https://schema.org","@type":"ContactPage",'
        '"name":"Contact SaaSpare",'
        '"url":"https://saaspare.org/contact",'
        '"description":"Contact SaaSpare for pricing corrections, comparison requests, partnerships, and editorial questions.",'
        '"publisher":{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"}}'
    )
    html = page_shell(
        slug="contact",
        title="Contact SaaSpare — Corrections, Partnerships & Requests",
        desc="Contact SaaSpare for pricing corrections, comparison requests, partnership enquiries, and editorial questions.",
        body=body,
        accent="about",
        nav_active="",
        crumbs=[CRUMB_HOME, ("/contact", "Contact")],
        canonical_path="/contact",
        schema_extra=schema,
        page_type="ContactPage",
    )
    (SITE / "contact.html").write_text(html, encoding="utf-8")

