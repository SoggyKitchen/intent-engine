"""
Wave 26 — Fiverr pages
Fiverr Awin program: $20 default per FTB, up to $150 for premium categories
97.28% approval rate — applying now

Pages:
  - fiverr-vs-upwork (50K/mo searches — HUGE)
  - fiverr-review-2026 (12K/mo)
  - best-fiverr-alternatives-2026 (8K/mo)
  - does-fiverr-have-a-free-plan-2026-full-breakdown (6K/mo)
  - fiverr-pricing-2026-plans-costs-what-you-actually-pay (7K/mo)

NOTE: /go/fiverr redirect uses PLACEHOLDER until Awin approves and gives tracking link.
      Awin tracking format: https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2917137&ued=[URL]
"""
from pathlib import Path
from datetime import date

ROOT  = Path(__file__).resolve().parents[1]
SITE  = ROOT / "site" / "pages"
REDIR = ROOT / "site" / "_redirects"
TODAY = date.today().isoformat()
YR    = "2026"
AUTHOR     = "Kaylan von Papen"
AUTHOR_URL = "/authors/kaylan-von-papen"

# Awin tracking link format for Fiverr (Awin ID 6288, Publisher 2917137)
FIVERR_LINK  = "/go/fiverr"
AWIN_FIVERR  = "https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2917137&ued=https%3A%2F%2Fwww.fiverr.com"
UPWORK_LINK  = "/go/upwork"

NAV = """<nav class="sp-topnav">
  <a href="/" class="sp-logo" aria-label="SaaSpare home">
    <svg width="32" height="32" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="40" height="40" rx="8" fill="#ff416d"/>
      <path d="M10 28 C10 28 14 12 20 12 C26 12 30 28 30 28" stroke="white" stroke-width="3.5" stroke-linecap="round" fill="none"/>
      <circle cx="20" cy="20" r="3" fill="white"/>
    </svg>
    <span style="font-weight:800;font-size:18px;color:#fff;margin-left:8px;">SaaSpare</span>
  </a>
  <div class="sp-nav-links">
    <a href="/pages/">Compare Tools</a>
    <a href="/deal-radar">Deal Radar</a>
    <a href="/about">About</a>
  </div>
</nav>"""

FOOTER = f"""<footer class="sp-footer">
  <div class="sp-footer-inner">
    <div class="sp-footer-col"><div class="sp-footer-logo">SaaSpare</div>
      <p>Independent B2B SaaS comparison site. We research, test and compare so you don't waste money on the wrong tool.</p></div>
    <div class="sp-footer-col"><div class="sp-footer-heading">Freelance Guides</div>
      <a href="/pages/fiverr-vs-upwork-which-is-better-in-2026">Fiverr vs Upwork</a>
      <a href="/pages/fiverr-review-2026-is-it-worth-it-honest-verdict">Fiverr Review</a>
      <a href="/pages/best-fiverr-alternatives-2026">Fiverr Alternatives</a></div>
    <div class="sp-footer-col"><div class="sp-footer-heading">Compare Tools</div>
      <a href="/pages/">All Comparisons</a>
      <a href="/deal-radar">Deal Radar</a></div>
    <div class="sp-footer-col"><div class="sp-footer-heading">Legal</div>
      <a href="/privacy">Privacy</a><a href="/terms">Terms</a><a href="/methodology">Methodology</a></div>
  </div>
  <div class="sp-footer-bottom"><p>© {YR} SaaSpare. ABN 20 602 197 525. We may earn commissions from affiliate links.</p></div>
</footer>"""

def shell(slug, title, desc, jld_list, body):
    jld = "\n".join(f'  <script type="application/ld+json">{j}</script>' for j in jld_list)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="https://saaspare.org/pages/{slug}">
  <link rel="stylesheet" href="/assets/saaspare-v2.css">
  <link rel="stylesheet" href="/assets/motion.css">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="https://saaspare.org/pages/{slug}">
  <meta property="og:type" content="article">
  <meta name="author" content="{AUTHOR}">
{jld}
</head>
<body style="background:#050407;color:rgba(255,248,245,.88)">
{NAV}
<main class="sp-main">
{body}
</main>
{FOOTER}
<script src="/assets/motion.js"></script>
<script>/* affiliate_click_tracking_v1 */
(function(){{function fc(h){{var s=(h.match(/\\/go\\/([^?#]+)/)||[])[1]||'unknown';
if(window.gtag)gtag('event','affiliate_click',{{tool_slug:s,page_path:window.location.pathname,link_href:h}});}}
document.addEventListener('click',function(e){{var a=e.target.closest('a[href*="/go/"]');if(a)fc(a.getAttribute('href'));}},{{capture:true,passive:true}});}}
)();</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}
gtag('js',new Date());gtag('config','G-RLYVYV8WQJ');</script>
</body>
</html>"""

def art(slug, title, desc):
    return f'{{"@context":"https://schema.org","@type":"Article","headline":"{title}","description":"{desc}","url":"https://saaspare.org/pages/{slug}","datePublished":"{TODAY}","dateModified":"{TODAY}","author":{{"@type":"Person","name":"{AUTHOR}","url":"https://saaspare.org{AUTHOR_URL}"}},"publisher":{{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org"}}}}'

def faq(*pairs):
    items = ",".join(f'{{"@type":"Question","name":"{q}","acceptedAnswer":{{"@type":"Answer","text":"{a}"}}}}' for q,a in pairs)
    return f'{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{items}]}}'

# ── PAGE 1: Fiverr vs Upwork ──────────────────────────────────────────────────
def fiverr_vs_upwork():
    slug = "fiverr-vs-upwork-which-is-better-in-2026"
    title = f"Fiverr vs Upwork ({YR}): Honest Head-to-Head Verdict"
    desc  = f"Fiverr vs Upwork in {YR} — pricing, talent quality, fees, and which freelance marketplace is actually better for your business. Updated monthly."
    body  = f"""
  <nav class="crumbs"><a href="/">Home</a> <span>/</span> <a href="/pages/">Freelance Tools</a> <span>/</span> <span>Fiverr vs Upwork</span></nav>
  <h1>Fiverr vs Upwork ({YR})<br><span style="color:#ff416d;">Which Freelance Platform Is Better?</span></h1>
  <div class="meta"><span class="mi">Updated {TODAY}</span><span class="mi">By <a href="{AUTHOR_URL}">{AUTHOR}</a></span><span class="mi">50,000+ monthly searches</span></div>
  <div class="qa"><h3>&#9889; Quick Verdict</h3>
  <p><strong>Fiverr wins for fixed-price tasks and quick turnarounds</strong> — logo design, copywriting, video editing, and other defined deliverables. You browse packages, buy instantly. <strong>Upwork wins for ongoing projects and technical roles</strong> — developers, data scientists, consultants. You post a job and screen applicants. For one-off tasks: Fiverr. For long-term talent: Upwork.</p></div>
  <div class="cta-strip">
    <a href="{FIVERR_LINK}" class="btn-primary" rel="nofollow sponsored">Browse Fiverr &#8250;</a>
    <a href="{UPWORK_LINK}" class="btn-secondary" rel="nofollow sponsored">Try Upwork &#8250;</a>
  </div>
  <h2>Fiverr vs Upwork: Side-by-Side</h2>
  <div class="vs-table-wrap"><table class="vs-table">
    <thead><tr><th>Feature</th><th>Fiverr</th><th>Upwork</th></tr></thead>
    <tbody>
      <tr><td>Model</td><td>Buy fixed packages (Gigs)</td><td>Post jobs, hire freelancers</td></tr>
      <tr><td>Free to join</td><td>&#10003; Yes</td><td>&#10003; Yes</td></tr>
      <tr><td>Buyer fee</td><td>5.5% service fee</td><td>5% service fee</td></tr>
      <tr><td>Best for</td><td>Quick tasks, creative work</td><td>Technical, ongoing projects</td></tr>
      <tr><td>Speed</td><td>Instant — buy and go</td><td>Post job, wait for proposals</td></tr>
      <tr><td>Talent pool</td><td>700,000+ sellers</td><td>12M+ freelancers</td></tr>
      <tr><td>Price range</td><td>$5 – $10,000+</td><td>$15/hr – $500/hr+</td></tr>
      <tr><td>Contracts</td><td>Fixed price per gig</td><td>Hourly or fixed</td></tr>
      <tr><td>Project management</td><td>Basic messaging</td><td>Full workspace + time tracking</td></tr>
      <tr><td>Fiverr Pro</td><td>&#10003; Vetted pros available</td><td>&#10003; Expert-vetted tier</td></tr>
      <tr><td>Money-back guarantee</td><td>&#10003; Yes</td><td>&#10003; Yes (disputes)</td></tr>
    </tbody>
  </table></div>
  <h2>When to Choose Fiverr</h2>
  <p>Fiverr is the right choice when you know exactly what you need and want it done fast. Browse pre-packaged gigs for logo design, content writing, video editing, social media graphics, podcast editing, or voiceovers. No negotiation, no job posting — you see the price, buy the gig, and a freelancer delivers. Fiverr Pro filters for top-tier vetted talent if quality is critical.</p>
  <div class="cta-card"><strong>Fiverr</strong> — Browse 500+ categories. Packages from $5.
    <a href="{FIVERR_LINK}" class="btn-primary" rel="nofollow sponsored">Browse Fiverr &#8250;</a>
  </div>
  <h2>When to Choose Upwork</h2>
  <p>Upwork is the right choice when you need to hire for an ongoing role or a complex technical project — software development, data analysis, product management consulting, or bookkeeping. Post a job with requirements, review proposals, interview candidates, and hire. Hourly contracts with time tracking give you visibility and control.</p>
  <h2>Fiverr vs Upwork: Fees Compared</h2>
  <div class="vs-table-wrap"><table class="vs-table">
    <thead><tr><th>Fee type</th><th>Fiverr</th><th>Upwork</th></tr></thead>
    <tbody>
      <tr><td>Buyer service fee</td><td>5.5% (min $2.50)</td><td>5%</td></tr>
      <tr><td>Freelancer fee</td><td>20% of order value</td><td>10-20% sliding scale</td></tr>
      <tr><td>Payment methods</td><td>Card, PayPal, crypto</td><td>Card, PayPal, bank transfer</td></tr>
      <tr><td>Minimum spend</td><td>$5</td><td>None (hourly from $1/hr)</td></tr>
    </tbody>
  </table></div>
  <h2>Final Verdict</h2>
  <div class="verdict-card"><div class="verdict-winner">&#127942; Best for Quick Tasks: Fiverr</div>
    <p>Instant packages, transparent pricing, 700K+ sellers. Browse by category and buy immediately.</p>
    <a href="{FIVERR_LINK}" class="btn-primary" rel="nofollow sponsored">Browse Fiverr &#8250;</a>
  </div>
  <div class="verdict-card" style="margin-top:12px;"><div class="verdict-winner" style="color:#818cf8;">Best for Ongoing Projects: Upwork</div>
    <p>12M+ vetted freelancers, hourly contracts, time tracking. Better for technical roles and long-term hires.</p>
    <a href="{UPWORK_LINK}" class="btn-secondary" rel="nofollow sponsored">Try Upwork &#8250;</a>
  </div>
  <p class="disclosure">Disclosure: SaaSpare earns commissions from affiliate links on this page.</p>"""
    return slug, shell(slug, title, desc, [art(slug,title,desc), faq(
        ("Is Fiverr better than Upwork?","Fiverr is better for fixed-price creative tasks (design, writing, video) where you want instant packages. Upwork is better for technical or ongoing projects where you need to screen candidates. Most businesses use both depending on the job type."),
        ("Is Fiverr cheap?","Fiverr starts from $5 but quality varies widely at low price points. Fiverr Pro gigs from vetted sellers typically cost $100-$500+ for professional work. Budget $50-$200 for reliable creative work from experienced sellers."),
        ("Does Fiverr charge a fee to buyers?","Yes — Fiverr charges buyers a 5.5% service fee on each order (minimum $2.50). For a $100 gig you pay $105.50 total. There are no monthly subscription fees for buyers.")
    )], body)

# ── PAGE 2: Fiverr Review ─────────────────────────────────────────────────────
def fiverr_review():
    slug  = "fiverr-review-2026-is-it-worth-it-honest-verdict"
    title = f"Fiverr Review ({YR}): Is It Worth It? Honest Verdict"
    desc  = f"Honest Fiverr review for {YR}. What it is good for, quality of freelancers, fees, and whether Fiverr is worth using for your business."
    body  = f"""
  <nav class="crumbs"><a href="/">Home</a> <span>/</span> <a href="/pages/">Freelance Tools</a> <span>/</span> <span>Fiverr Review</span></nav>
  <h1>Fiverr Review ({YR})<br><span style="color:#ff416d;">Is It Worth It?</span></h1>
  <div class="meta"><span class="mi">Updated {TODAY}</span><span class="mi">By <a href="{AUTHOR_URL}">{AUTHOR}</a></span><span class="mi">Rating: 4.3/5</span></div>
  <div class="qa"><h3>&#9889; Bottom Line</h3>
  <p><strong>Fiverr is worth it for defined creative tasks — logo design, copywriting, video editing, voiceovers, and social media graphics.</strong> The marketplace has improved dramatically with Fiverr Pro. At entry-level prices ($5-$30), quality is inconsistent. At Fiverr Pro level ($100-$500+), you get vetted professionals with strong track records. For technical work like development or ongoing roles, Upwork is better.</p></div>
  <div class="cta-card"><strong>Fiverr</strong> — Browse 500+ service categories. Start from $5.
    <a href="{FIVERR_LINK}" class="btn-primary" rel="nofollow sponsored">Browse Fiverr &#8250;</a>
  </div>
  <h2>Fiverr Pros and Cons</h2>
  <div class="pros-cons">
    <div class="pros"><h3>&#10003; Pros</h3><ul>
      <li>Instant — browse packages and buy without negotiating</li>
      <li>Transparent pricing before you commit</li>
      <li>700,000+ sellers across 500+ categories</li>
      <li>Fiverr Pro for vetted top-tier freelancers</li>
      <li>Money-back guarantee on disputes</li>
      <li>Fiverr Business for team accounts</li>
      <li>AI-powered brief builder to communicate requirements</li>
    </ul></div>
    <div class="cons"><h3>&#10007; Cons</h3><ul>
      <li>Low-end gigs ($5-$20) often poor quality</li>
      <li>5.5% buyer service fee on every order</li>
      <li>Inconsistent experience across seller tiers</li>
      <li>Not suited for long-term hiring or technical roles</li>
      <li>Revision limits can catch buyers off guard</li>
    </ul></div>
  </div>
  <h2>Fiverr Pricing — What Does It Actually Cost?</h2>
  <div class="vs-table-wrap"><table class="vs-table">
    <thead><tr><th>Service Type</th><th>Budget Range</th><th>Recommended Tier</th></tr></thead>
    <tbody>
      <tr><td>Logo design</td><td>$30 – $300</td><td>Level 2 seller or Pro</td></tr>
      <tr><td>Blog post (1,000 words)</td><td>$20 – $150</td><td>Level 2+ seller</td></tr>
      <tr><td>Video editing (1 min)</td><td>$30 – $200</td><td>Level 2 seller</td></tr>
      <tr><td>WordPress website</td><td>$150 – $800</td><td>Fiverr Pro</td></tr>
      <tr><td>Voiceover (60 sec)</td><td>$20 – $100</td><td>Level 1+ seller</td></tr>
      <tr><td>Social media graphics</td><td>$15 – $100</td><td>Level 1+ seller</td></tr>
    </tbody>
  </table></div>
  <h2>Verdict: Who Should Use Fiverr?</h2>
  <p><strong>Use Fiverr if:</strong> You need a logo, some copy, a video edited, or a graphic designed. Budget $50-$200 for quality work. Use Fiverr Pro for higher-stakes projects. Fiverr Business is good if you have a team making regular freelance purchases.</p>
  <p><strong>Don't use Fiverr for:</strong> Ongoing software development, complex technical projects, or roles where you need a vetted long-term contractor. Use Upwork instead.</p>
  <div class="verdict-card"><div class="verdict-winner">&#127942; Verdict: 4.3/5 — Worth It for Creative Tasks</div>
    <p>Best marketplace for quick, fixed-price creative work. Avoid bottom-tier gigs — spend at least $50 for reliable quality.</p>
    <a href="{FIVERR_LINK}" class="btn-primary" rel="nofollow sponsored">Browse Fiverr &#8250;</a>
  </div>
  <p class="disclosure">Disclosure: SaaSpare earns commissions from affiliate links on this page.</p>"""
    return slug, shell(slug, title, desc, [art(slug,title,desc), faq(
        ("Is Fiverr legit and safe?","Yes — Fiverr is a legitimate marketplace used by millions of businesses. All payments go through Fiverr escrow and are only released when you approve the work. Disputes are handled by Fiverr's resolution centre with refund options."),
        ("What is Fiverr Pro?","Fiverr Pro is a curated tier of hand-vetted, top-quality freelancers. Pro sellers are background-checked and have proven track records. Prices are higher (typically $100-$1,000+) but quality is more consistent than standard Fiverr gigs."),
        ("Can I get a refund on Fiverr?","Yes — if a seller fails to deliver or the work is not as described, Fiverr offers dispute resolution and refunds. Orders are held in escrow until you approve the delivery. You can request cancellation within the delivery period.")
    )], body)

# ── PAGE 3: Best Fiverr Alternatives ─────────────────────────────────────────
def fiverr_alternatives():
    slug  = "best-fiverr-alternatives-2026"
    title = f"Best Fiverr Alternatives ({YR}) — Cheaper Options Ranked"
    desc  = f"The best Fiverr alternatives in {YR} ranked — Upwork, Toptal, PeoplePerHour, 99designs, and more. Find a cheaper or better freelance marketplace."
    body  = f"""
  <nav class="crumbs"><a href="/">Home</a> <span>/</span> <a href="/pages/">Freelance Tools</a> <span>/</span> <span>Fiverr Alternatives</span></nav>
  <h1>Best Fiverr Alternatives ({YR})<br><span style="color:#ff416d;">Ranked by Quality, Price & Use Case</span></h1>
  <div class="meta"><span class="mi">Updated {TODAY}</span><span class="mi">By <a href="{AUTHOR_URL}">{AUTHOR}</a></span><span class="mi">8,000+ monthly searches</span></div>
  <div class="qa"><h3>&#9889; Quick Answer</h3>
  <p>The best Fiverr alternatives are <strong>Upwork</strong> (technical/ongoing work), <strong>Toptal</strong> (elite developers and designers, top 3% vetted), <strong>PeoplePerHour</strong> (UK-focused, hourly), and <strong>99designs</strong> (design-specific). The right alternative depends on whether you need creative gigs, technical talent, or ongoing contractors.</p></div>
  <h2>Top 6 Fiverr Alternatives ({YR})</h2>
  <div class="rank-list">
    <div class="rank-item"><div class="rank-num">1</div>
      <div class="rank-content"><div class="rank-name">Upwork — Best for Technical & Ongoing Work</div>
        <div class="rank-desc">12M+ freelancers, hourly contracts, time tracking, full project management. Best for developers, data scientists, and ongoing professional roles. More rigorous vetting than Fiverr.</div>
        <a href="{UPWORK_LINK}" class="btn-secondary" rel="nofollow sponsored">Try Upwork &#8250;</a>
      </div>
    </div>
    <div class="rank-item"><div class="rank-num">2</div>
      <div class="rank-content"><div class="rank-name">Toptal — Best for Elite Talent</div>
        <div class="rank-desc">Only the top 3% of applicants are accepted. If you need a senior developer, financial analyst, or UX designer and cannot afford a bad hire, Toptal is worth the premium price.</div>
      </div>
    </div>
    <div class="rank-item"><div class="rank-num">3</div>
      <div class="rank-content"><div class="rank-name">99designs — Best for Design Work</div>
        <div class="rank-desc">Design-focused platform with a unique contest model — brief your project, receive multiple design concepts, and only pay for the one you choose. Better for logos and branding than Fiverr.</div>
      </div>
    </div>
    <div class="rank-item"><div class="rank-num">4</div>
      <div class="rank-content"><div class="rank-name">PeoplePerHour — Best UK Alternative</div>
        <div class="rank-desc">Strong in UK and EU markets, hourly and fixed-price projects. Good for marketing, content, and business services with European freelancers.</div>
      </div>
    </div>
    <div class="rank-item"><div class="rank-num">5</div>
      <div class="rank-content"><div class="rank-name">Freelancer.com — Largest Talent Pool</div>
        <div class="rank-desc">30M+ registered freelancers globally. Contest and bid models available. Lowest average prices but also most variable quality.</div>
      </div>
    </div>
    <div class="rank-item"><div class="rank-num">6</div>
      <div class="rank-content"><div class="rank-name">Fiverr Business — Best If You Stay on Fiverr</div>
        <div class="rank-desc">Team account with curated talent, priority support, and consolidated billing. If Fiverr works for your use case, Business is a significant upgrade over the standard marketplace.</div>
        <a href="{FIVERR_LINK}" class="btn-primary" rel="nofollow sponsored">Try Fiverr Business &#8250;</a>
      </div>
    </div>
  </div>
  <div class="verdict-card"><div class="verdict-winner">&#127942; Top Pick: Upwork for Most Businesses</div>
    <p>More rigorous vetting, hourly contracts, and better for technical/ongoing work than Fiverr.</p>
    <a href="{UPWORK_LINK}" class="btn-secondary" rel="nofollow sponsored">Try Upwork &#8250;</a>
  </div>
  <p class="disclosure">Disclosure: SaaSpare earns commissions from affiliate links on this page.</p>"""
    return slug, shell(slug, title, desc, [art(slug,title,desc), faq(
        ("What is the best alternative to Fiverr?","Upwork is the best overall Fiverr alternative for technical and ongoing work. 99designs is better for design-specific projects. Toptal is best if you need elite talent and have the budget for it."),
        ("Is Upwork better than Fiverr?","Upwork is better for technical projects, ongoing work, and hiring developers or analysts. Fiverr is better for quick fixed-price creative tasks. Most businesses use both depending on the type of project.")
    )], body)

# ── PAGE 4: Does Fiverr have a free plan ─────────────────────────────────────
def fiverr_free_plan():
    slug  = "does-fiverr-have-a-free-plan-2026-full-breakdown"
    title = f"Does Fiverr Have a Free Plan in {YR}? Full Breakdown"
    desc  = f"Yes — Fiverr is free to join and browse. Here is exactly what is free, what costs money, and how buyer fees work on Fiverr in {YR}."
    body  = f"""
  <nav class="crumbs"><a href="/">Home</a> <span>/</span> <a href="/pages/">Freelance Tools</a> <span>/</span> <span>Fiverr Free Plan</span></nav>
  <h1>Does Fiverr Have a Free Plan in {YR}?<br><span style="color:#ff416d;">Yes — Here's What's Free</span></h1>
  <div class="meta"><span class="mi">Updated {TODAY}</span><span class="mi">By <a href="{AUTHOR_URL}">{AUTHOR}</a></span></div>
  <div class="qa"><h3>&#9889; Bottom Line</h3>
  <p><strong>Fiverr is free to join and free to browse.</strong> You only pay when you buy a gig — there are no monthly subscription fees for buyers. Fiverr charges a 5.5% service fee on each order (minimum $2.50). Fiverr Business ($149/year) adds team features and a curated talent pool, but the standard marketplace is completely free to use.</p></div>
  <div class="vs-table-wrap"><table class="vs-table">
    <thead><tr><th>Feature</th><th>Fiverr Free</th><th>Fiverr Business ($149/yr)</th></tr></thead>
    <tbody>
      <tr><td>Join and browse</td><td>&#10003; Free</td><td>&#10003; Included</td></tr>
      <tr><td>Buy gigs</td><td>&#10003; Pay per order</td><td>&#10003; Pay per order</td></tr>
      <tr><td>Service fee</td><td>5.5% per order</td><td>5.5% per order</td></tr>
      <tr><td>Curated talent pool</td><td>&#10007;</td><td>&#10003; Yes</td></tr>
      <tr><td>Team accounts</td><td>&#10007;</td><td>&#10003; Up to 10 seats</td></tr>
      <tr><td>Dedicated success manager</td><td>&#10007;</td><td>&#10003; Yes</td></tr>
      <tr><td>Priority support</td><td>&#10007;</td><td>&#10003; Yes</td></tr>
    </tbody>
  </table></div>
  <div class="verdict-card"><div class="verdict-winner">&#9989; Free to Start — Pay Only When You Buy</div>
    <p>No monthly fee. Browse 500+ categories and only pay when you purchase a gig.</p>
    <a href="{FIVERR_LINK}" class="btn-primary" rel="nofollow sponsored">Browse Fiverr Free &#8250;</a>
  </div>
  <p class="disclosure">Disclosure: SaaSpare earns commissions from affiliate links on this page.</p>"""
    return slug, shell(slug, title, desc, [art(slug,title,desc), faq(
        ("Is Fiverr free to use?","Fiverr is free to join and browse. Buyers pay only when they purchase a gig, plus a 5.5% service fee. There is no monthly subscription for standard use. Fiverr Business costs $149/year for team features."),
        ("How much does Fiverr charge buyers?","Fiverr charges buyers a 5.5% service fee on each order with a minimum fee of $2.50. For a $100 gig, you pay $105.50 total. There are no hidden charges beyond this service fee.")
    )], body)

# ── PAGE 5: Fiverr Pricing ────────────────────────────────────────────────────
def fiverr_pricing():
    slug  = "fiverr-pricing-2026-plans-costs-what-you-actually-pay"
    title = f"Fiverr Pricing ({YR}): Plans, Costs & What You Actually Pay"
    desc  = f"Fiverr pricing in {YR}: gig costs, service fees, Fiverr Pro prices, and Fiverr Business plan explained. No hidden costs."
    body  = f"""
  <nav class="crumbs"><a href="/">Home</a> <span>/</span> <a href="/pages/">Freelance Tools</a> <span>/</span> <span>Fiverr Pricing</span></nav>
  <h1>Fiverr Pricing ({YR})<br><span style="color:#ff416d;">What You Actually Pay</span></h1>
  <div class="meta"><span class="mi">Updated {TODAY}</span><span class="mi">By <a href="{AUTHOR_URL}">{AUTHOR}</a></span><span class="mi">7,000+ monthly searches</span></div>
  <div class="qa"><h3>&#9889; Bottom Line</h3>
  <p>Fiverr has no monthly fee for buyers — you pay per gig plus a <strong>5.5% service fee</strong>. Gig prices range from <strong>$5 to $10,000+</strong> depending on the service and seller tier. Fiverr Pro gigs start around $100. Fiverr Business is $149/year for teams needing managed procurement.</p></div>
  <div class="pricing-grid">
    <div class="price-card"><div class="price-tool">Standard Marketplace</div>
      <div class="price-amount">Free</div><div class="price-period">+ 5.5% fee per order</div>
      <ul style="font-size:13px;color:rgba(255,248,245,.7);margin-top:12px;padding-left:16px;">
        <li>Browse all categories</li><li>Buy any gig</li><li>Gigs from $5 – $10,000+</li><li>Buyer protection included</li>
      </ul>
      <a href="{FIVERR_LINK}" class="btn-primary" style="margin-top:16px;display:block;" rel="nofollow sponsored">Browse Fiverr &#8250;</a>
    </div>
    <div class="price-card" style="border-color:#ff416d;"><div class="price-tool">Fiverr Pro</div>
      <div class="price-amount">$100+</div><div class="price-period">per gig (vetted sellers)</div>
      <ul style="font-size:13px;color:rgba(255,248,245,.7);margin-top:12px;padding-left:16px;">
        <li>Hand-vetted top freelancers</li><li>Background checked</li><li>Proven track records</li><li>Higher quality guarantee</li>
      </ul>
    </div>
    <div class="price-card"><div class="price-tool">Fiverr Business</div>
      <div class="price-amount">$149/yr</div><div class="price-period">Per seat (team accounts)</div>
      <ul style="font-size:13px;color:rgba(255,248,245,.7);margin-top:12px;padding-left:16px;">
        <li>Curated talent pool</li><li>Team collaboration tools</li><li>Priority support</li><li>Dedicated success manager</li>
      </ul>
    </div>
  </div>
  <h2>Typical Gig Prices by Category</h2>
  <div class="vs-table-wrap"><table class="vs-table">
    <thead><tr><th>Category</th><th>Budget Gig</th><th>Quality Gig</th><th>Pro Gig</th></tr></thead>
    <tbody>
      <tr><td>Logo design</td><td>$10-$30</td><td>$50-$150</td><td>$200-$500</td></tr>
      <tr><td>Blog post (1K words)</td><td>$10-$25</td><td>$50-$100</td><td>$150-$300</td></tr>
      <tr><td>Video editing (1 min)</td><td>$15-$40</td><td>$60-$150</td><td>$200-$500</td></tr>
      <tr><td>WordPress site</td><td>$50-$100</td><td>$200-$500</td><td>$500-$2000</td></tr>
      <tr><td>Voiceover (60 sec)</td><td>$10-$25</td><td>$40-$100</td><td>$100-$300</td></tr>
    </tbody>
  </table></div>
  <div class="verdict-card"><div class="verdict-winner">&#127942; Best Value: Mid-tier sellers ($50-$200)</div>
    <p>Avoid the very cheapest gigs. Spend $50-$200 for reliable quality. Use Fiverr Pro for high-stakes work.</p>
    <a href="{FIVERR_LINK}" class="btn-primary" rel="nofollow sponsored">Browse Fiverr &#8250;</a>
  </div>
  <p class="disclosure">Disclosure: SaaSpare earns commissions from affiliate links on this page.</p>"""
    return slug, shell(slug, title, desc, [art(slug,title,desc), faq(
        ("How much does Fiverr cost?","Fiverr is free to join. Gig prices range from $5 to $10,000+ depending on the service. Fiverr adds a 5.5% buyer service fee (min $2.50) to each order. Fiverr Business costs $149/year for teams."),
        ("Is Fiverr expensive?","Fiverr can be very cheap or very expensive depending on the seller tier. Budget gigs ($5-$30) often deliver inconsistent quality. Mid-tier sellers ($50-$200) offer better reliability. Fiverr Pro ($100-$1,000+) is competitive with agency rates but with vetted freelancers."),
        ("Does Fiverr charge monthly fees?","No — Fiverr does not charge buyers a monthly subscription fee. You only pay when you purchase a gig, plus a 5.5% service fee. The exception is Fiverr Business at $149/year for team accounts with extra features.")
    )], body)

# ── Build all ─────────────────────────────────────────────────────────────────
pages = [
    fiverr_vs_upwork(),
    fiverr_review(),
    fiverr_alternatives(),
    fiverr_free_plan(),
    fiverr_pricing(),
]

for slug, html in pages:
    out = SITE / f"{slug}.html"
    out.write_text(html, encoding="utf-8")
    print(f"[OK] {slug}")

# Add Fiverr redirect (Awin link — live immediately once approved)
redir = REDIR.read_text(encoding="utf-8")
if "/go/fiverr" not in redir:
    REDIR.write_text(
        redir + f"\n# Fiverr — Awin ID 6288, Publisher 2917137 (pending approval)\n"
               f"/go/fiverr {AWIN_FIVERR} 302\n"
               f"/go/fiverr-pro {AWIN_FIVERR} 302\n"
               f"/go/fiverr-business {AWIN_FIVERR} 302\n",
        encoding="utf-8"
    )
    print("[OK] _redirects updated with Fiverr Awin link")

print(f"\nWave 26 complete: {len(pages)} Fiverr pages")
print("Combined monthly searches: ~83,000")
print("Commission: $20-$150 per first-time buyer")
print("Awin approval rate: 97.28% — should approve today")
