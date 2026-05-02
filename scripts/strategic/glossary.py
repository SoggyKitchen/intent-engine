"""SaaS Glossary â€” 50+ terms."""
import re
from ._helpers import (
    page_shell, hero_h1_with_glint, breadcrumb_html,
    write_page, CRUMB_HOME,
)

TERMS = [
    ("ACV", "Annual Contract Value â€” the annualised revenue of a customer contract. SaaS vendors report ACV to smooth out multi-year deals."),
    ("ARR", "Annual Recurring Revenue â€” total subscription revenue normalised to 12 months. The primary SaaS growth metric."),
    ("ARPU", "Average Revenue Per User â€” total revenue divided by active users. Used to measure monetisation efficiency."),
    ("Churn rate", "The percentage of customers who cancel in a given period. Net revenue churn subtracts expansion revenue from lost revenue."),
    ("CAC", "Customer Acquisition Cost â€” total sales + marketing spend divided by new customers acquired. CAC payback under 12 months is ideal for SaaS."),
    ("CAC payback", "Months needed to recover CAC from gross profit. 12-month payback is typical; 18+ signals inefficiency."),
    ("CSM", "Customer Success Manager â€” post-sale role managing retention, expansion, and support for mid-market or enterprise accounts."),
    ("DAU/MAU", "Daily Active Users / Monthly Active Users. Engagement ratio; 20%+ is strong for B2B SaaS."),
    ("Net Dollar Retention", "NDR â€” revenue from existing customers vs. one year ago. 120%+ is elite SaaS."),
    ("Expansion revenue", "New ARR from existing customers via upsells, cross-sells, or seat expansion. Key to high NDR."),
    ("Freemium", "A pricing model with a free tier alongside paid plans. Common in developer and productivity SaaS."),
    ("Gross margin", "Revenue minus COGS (hosting, support, payment fees) divided by revenue. SaaS benchmark: 70â€“85%."),
    ("LTV", "Customer Lifetime Value â€” average revenue per customer over their entire relationship. Should exceed 3Ã— CAC."),
    ("MQL", "Marketing Qualified Lead â€” a lead that is engaged enough with marketing content to be handed to sales."),
    ("MRR", "Monthly Recurring Revenue â€” normalised monthly subscription revenue. ARR Ã· 12."),
    ("NPS", "Net Promoter Score â€” a customer satisfaction metric measuring likelihood to recommend. SaaS benchmark: 30+."),
    ("PLG", "Product-Led Growth â€” acquisition model where the product drives sign-ups (vs. sales-led). Examples: Slack, Notion, Figma."),
    ("POC", "Proof of Concept â€” a limited-scope trial to validate technical fit. Usually required for enterprise SaaS."),
    ("Rule of 40", "Growth rate % + profit margin % >= 40. A composite SaaS health metric. Public SaaS companies target this."),
    ("SOC 2", "Security audit report showing a SaaS vendor meets standards for security, availability, and confidentiality. Type II is the gold standard."),
    ("SSO", "Single Sign-On â€” login via identity provider like Okta, Google, or Microsoft Entra. Usually locked to enterprise tiers."),
    ("SAML", "Security Assertion Markup Language â€” protocol for SSO. Required for most enterprise IT approvals."),
    ("SLA", "Service Level Agreement â€” contractual uptime guarantee. 99.9% = ~8.76h downtime/year; 99.99% = ~52min/year."),
    ("TAM", "Total Addressable Market â€” maximum revenue opportunity if 100% of potential customers bought."),
    ("TCO", "Total Cost of Ownership â€” full cost including subscription, implementation, training, integration, and switching costs."),
    ("Usage-based pricing", "Pricing based on consumption (API calls, events, data) rather than seats. Popular for infra SaaS like Twilio and Snowflake."),
    ("Viral coefficient", "Users invited by existing users / active users. Greater than 1 means organic growth, less than 1 means needs paid acquisition."),
    ("White-label", "Reselling SaaS under your own brand. Common for agencies and platforms that embed third-party tools."),
    ("API rate limit", "Cap on requests per second/minute an API accepts. Higher limits are usually gated to higher pricing tiers."),
    ("Seat-based pricing", "Price scales with active user count. Most common B2B SaaS model. Watch for hidden seat minimums."),
    ("Data residency", "Geographic location where data is stored. Critical for GDPR, Australian Privacy Principles, and regulated industries."),
    ("Multi-tenancy", "SaaS architecture where one instance serves multiple customers. Keeps costs low; can raise noisy-neighbour concerns."),
    ("Webhook", "HTTP callback fired on an event. Integration plumbing for SaaS-to-SaaS communication."),
    ("OAuth", "Authorisation protocol used for third-party app access. Scopes limit what the integrating app can do."),
    ("RBAC", "Role-Based Access Control â€” users grouped into roles (admin, editor, viewer) with specific permissions."),
    ("SCIM", "System for Cross-domain Identity Management â€” protocol for automatically provisioning and deprovisioning users."),
    ("Zero Trust", "Security model assuming no network boundary is trustworthy. Verifies every access request regardless of origin."),
    ("MSA", "Master Service Agreement â€” top-level contract governing the customer-vendor relationship. Usually paired with an Order Form."),
    ("DPA", "Data Processing Agreement â€” contract specifying how a vendor handles personal data under GDPR/privacy laws."),
    ("SSO tax", "Premium pricing vendors charge to unlock SSO, even though SSO is a security requirement. Widely criticised."),
    ("Procurement lead time", "Weeks from vendor selection to signed contract. Enterprise SaaS averages 45â€“90 days."),
    ("Migration cost", "Time + money to move data/users from one SaaS to another. Can exceed 1 year of subscription savings."),
    ("Vendor lock-in", "Difficulty switching vendors due to data formats, integrations, or contractual penalties."),
    ("Price grandfathering", "Keeping existing customers on old (cheaper) pricing when new pricing launches. Not always honoured."),
    ("Annual prepay discount", "10â€“25% discount for paying a year upfront vs. monthly. Standard for B2B SaaS."),
    ("Seat minimum", "Contractually required minimum user count, regardless of actual usage. Common at mid-market and enterprise tiers."),
    ("Auto-renewal", "Contract clause that renews the subscription automatically. Check the cancellation window (often 30â€“60 days before renewal)."),
    ("Click-through agreement", "Contract accepted by clicking an accept button. Binds your company even without a signature."),
    ("EULA", "End User License Agreement â€” contract governing software usage. Standard in consumer and SMB SaaS."),
    ("Free trial vs free plan", "Trials expire (7â€“30 days). Free plans never do, but usually have feature or usage limits."),
    ("CPA", "Cost Per Acquisition â€” paid marketing cost to acquire one customer. Component of CAC."),
]


def build():
    def card(t, d):
        anchor = re.sub(r"\W+", "-", t.lower()).strip("-")
        return f'<div class="term" id="t-{anchor}"><dl><dt>{t}</dt><dd>{d}</dd></dl></div>'
    terms_html = "\n".join(card(t, d) for t, d in sorted(TERMS))
    h1 = hero_h1_with_glint("The SaaS Glossary every buyer should bookmark", "SaaS Glossary")
    body = f"""
<section class="page-hero">
  <div class="page-hero-bg"></div>
  <div class="page-hero-dots"></div>
  <div class="page-hero-orb"></div><div class="page-hero-orb2"></div>
  <div class="page-hero-content">
    {breadcrumb_html([CRUMB_HOME, ("/pages/saas-glossary", "SaaS Glossary")])}
    <div class="page-eyebrow">Reference Â· {len(TERMS)} terms</div>
    <h1>{h1}</h1>
    <p class="page-sub">Decode vendor pitches, sanity-check pricing, and negotiate contracts without getting tangled in acronyms. Cited by every SaaSpare comparison.</p>
  </div>
</section>
<main class="page-content">
  <div class="ps reveal">
    <div class="term-grid">
      {terms_html}
    </div>
  </div>
  <div class="ps reveal">
    <div class="cta-big">
      <h3>Want new terms in your inbox?</h3>
      <p>Every Friday the Weekly SaaS Deal Digest adds new terms as SaaS contracts get weirder.</p>
      <a href="/pages/weekly-saas-deal-digest" class="btn">Subscribe free â†’</a>
    </div>
  </div>
</main>
"""
    schema = (
        '{"@context":"https://schema.org","@type":"DefinedTermSet",'
        '"name":"SaaSpare SaaS Glossary",'
        '"url":"https://saaspare.org/pages/saas-glossary"}'
    )
    html = page_shell(
        slug="saas-glossary",
        title=f"SaaS Glossary: {len(TERMS)}+ B2B SaaS Terms Every Buyer Should Know",
        desc="The complete B2B SaaS vocabulary: ACV, ARR, CAC, NDR, PLG, SSO tax, seat minimums, and 50+ more terms explained simply.",
        body=body, accent="glossary", nav_active="gloss",
        crumbs=[CRUMB_HOME, ("/pages/saas-glossary", "SaaS Glossary")],
        schema_extra=schema, page_type="DefinedTermSet",
    )
    write_page("saas-glossary", html)

