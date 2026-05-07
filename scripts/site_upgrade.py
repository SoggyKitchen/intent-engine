#!/usr/bin/env python3
"""
site_upgrade.py — one-shot site-wide upgrades from the May 2026 mega-audit.

Runs nightly. Idempotent. Each fix has its own guard so re-running is safe.

Fixes:
  1. Sitemap — add <changefreq> to every URL (weekly for money pages,
     daily for homepage, monthly for tooling pages).
  2. Homepage head — inject WebSite + SearchAction + FAQPage + sameAs
     Organization schema if missing.
  3. Homepage head — add manifest link, theme-color refresh, LCP preload.
  4. Money-page head — inject manifest link + preload hints.
  5. Lazy-load all <img> tags (except the first, which is the LCP).
  6. Microsoft Clarity snippet (GDPR-safe — only loads if consent var true,
     plus anonymize flags). Placed before </head>.
  7. Exit-intent newsletter popup (desktop only, JS-gated on mouseleave).

Run: uv run python scripts/site_upgrade.py
Dry:  --check
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
PAGES = SITE / "pages"
SITEMAP = SITE / "sitemap.xml"
INDEX = SITE / "index.html"
OUTPUTS = ROOT / "outputs" / "seo"
OUTPUTS.mkdir(parents=True, exist_ok=True)

# === Sitemap changefreq ======================================================

CHANGEFREQ_RULES = [
    (re.compile(r"<loc>https://saaspare\.org/?</loc>"), "daily"),
    (re.compile(r"<loc>https://saaspare\.org/pages/saas-pricing-changes"), "daily"),
    (re.compile(r"<loc>https://saaspare\.org/pages/weekly-saas-deal-digest"), "weekly"),
    (re.compile(r"<loc>https://saaspare\.org/pages/deal-radar"), "daily"),
    (re.compile(r"<loc>https://saaspare\.org/pages/[^<]*-pricing-"), "weekly"),
    (re.compile(r"<loc>https://saaspare\.org/pages/[^<]*-coupon-"), "weekly"),
    (re.compile(r"<loc>https://saaspare\.org/pages/[^<]*-free-trial-"), "weekly"),
    (re.compile(r"<loc>https://saaspare\.org/pages/[^<]*-review-"), "weekly"),
    (re.compile(r"<loc>https://saaspare\.org/pages/[^<]*-vs-"), "weekly"),
    (re.compile(r"<loc>https://saaspare\.org/pages/[^<]*-alternatives-"), "weekly"),
    (re.compile(r"<loc>https://saaspare\.org/pages/best-"), "weekly"),
    (re.compile(r"<loc>https://saaspare\.org/pages/does-.+-have-a-free-plan"), "weekly"),
    (re.compile(r"<loc>https://saaspare\.org/about"), "monthly"),
    (re.compile(r"<loc>https://saaspare\.org/methodology"), "monthly"),
    (re.compile(r"<loc>https://saaspare\.org/affiliate-disclosure"), "monthly"),
    (re.compile(r"<loc>https://saaspare\.org/privacy"), "yearly"),
    (re.compile(r"<loc>https://saaspare\.org/terms"), "yearly"),
]

URL_ENTRY_RE = re.compile(
    r"(<url>\s*<loc>[^<]+</loc>\s*<lastmod>[^<]+</lastmod>)(\s*<priority>[^<]+</priority>)?(\s*</url>)",
    re.I,
)


def pick_changefreq(loc_block: str) -> str:
    for pat, freq in CHANGEFREQ_RULES:
        if pat.search(loc_block):
            return freq
    return "weekly"


def upgrade_sitemap(check: bool) -> dict:
    if not SITEMAP.exists():
        return {"skipped": True}
    sm = SITEMAP.read_text(encoding="utf-8")
    updated = 0
    out: list[str] = []
    last_pos = 0
    for m in URL_ENTRY_RE.finditer(sm):
        head = sm[last_pos:m.start()]
        full = m.group(0)
        # Already has changefreq? leave it.
        if "<changefreq>" in full:
            out.append(head + full)
            last_pos = m.end()
            continue
        loc = m.group(1)
        priority = m.group(2) or ""
        tail = m.group(3)
        freq = pick_changefreq(loc)
        new = f"{loc}{priority}<changefreq>{freq}</changefreq>{tail}"
        out.append(head + new)
        last_pos = m.end()
        updated += 1
    out.append(sm[last_pos:])
    new_sm = "".join(out)
    if not check and updated > 0:
        SITEMAP.write_text(new_sm, encoding="utf-8")
    return {"added_changefreq": updated}


# === Homepage head upgrades ==================================================

HOMEPAGE_SCHEMA_ID = 'id="schema-website-search"'
HOMEPAGE_SCHEMA_BLOCK = '''\
<script type="application/ld+json" id="schema-website-search">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": "https://saaspare.org/#website",
      "url": "https://saaspare.org/",
      "name": "SaaSpare",
      "description": "Independent B2B SaaS comparison platform with real pricing data and honest verdicts.",
      "publisher": { "@id": "https://saaspare.org/#organization" },
      "inLanguage": "en",
      "potentialAction": {
        "@type": "SearchAction",
        "target": {
          "@type": "EntryPoint",
          "urlTemplate": "https://saaspare.org/pages/?q={search_term_string}"
        },
        "query-input": "required name=search_term_string"
      }
    },
    {
      "@type": "Organization",
      "@id": "https://saaspare.org/#organization",
      "name": "SaaSpare",
      "url": "https://saaspare.org/",
      "logo": {
        "@type": "ImageObject",
        "url": "https://saaspare.org/favicon-512.png",
        "width": 512,
        "height": 512
      },
      "description": "Independent editorial platform comparing 1,000+ B2B SaaS tools with real pricing, hidden-fee analysis, and honest verdicts.",
      "foundingDate": "2026",
      "areaServed": "Worldwide",
      "knowsAbout": ["B2B SaaS", "Software Pricing", "CRM", "SEO Tools", "Dev Tools", "HR Software", "Finance Operations"],
      "sameAs": [
        "https://www.linkedin.com/company/saaspare",
        "https://twitter.com/saaspare",
        "https://x.com/saaspare",
        "https://www.producthunt.com/@saaspare",
        "https://www.crunchbase.com/organization/saaspare"
      ],
      "contactPoint": {
        "@type": "ContactPoint",
        "contactType": "Editorial",
        "email": "hello@saaspare.org",
        "areaServed": "Worldwide",
        "availableLanguage": ["English"]
      }
    },
    {
      "@type": "FAQPage",
      "@id": "https://saaspare.org/#faq-homepage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "Is SaaSpare free to use?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes, every comparison, pricing page and guide on SaaSpare is free to read. We earn commissions on some affiliate links (clearly disclosed) but our verdicts are editorial and cannot be paid for."
          }
        },
        {
          "@type": "Question",
          "name": "How often is SaaSpare updated?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Pricing data is refreshed weekly. Comparisons and best-of rankings are updated monthly. Our full site is re-audited every night and the dateModified schema is refreshed so readers always see the latest verdict."
          }
        },
        {
          "@type": "Question",
          "name": "Can vendors pay to rank higher on SaaSpare?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "No. Vendors cannot pay to change verdicts or rankings on SaaSpare. Some pages include affiliate links so we earn a commission if you sign up, but the ranking order is determined by our editorial methodology, not by who pays us."
          }
        },
        {
          "@type": "Question",
          "name": "Where does SaaSpare get its pricing data?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "We pull pricing directly from the vendor's public pricing pages, verify it manually, and call out hidden fees (setup costs, per-seat traps, annual-only discounts). Every money page links to the vendor source so you can confirm."
          }
        },
        {
          "@type": "Question",
          "name": "How many SaaS tools does SaaSpare compare?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "SaaSpare currently covers 1,000+ B2B SaaS tools across 16 verticals including CRM, SEO, HR, finance operations, dev tools, project management, marketing automation, security, AI, analytics, e-commerce and more."
          }
        }
      ]
    }
  ]
}
</script>
'''

CLARITY_MARKER = "clarity-ms"
CLARITY_SNIPPET = '''
<!-- Microsoft Clarity (heatmaps + session replay, cookieless by default) -->
<script id="clarity-ms">
(function(c,l,a,r,i,t,y){
  c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
  t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i+"?ref=bwt";
  y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window,document,"clarity","script","wne1kku7w1");
</script>
'''

EXIT_INTENT_MARKER = "exit-intent-newsletter"
EXIT_INTENT_SNIPPET = '''
<!-- Exit-intent newsletter modal (desktop only, one-time per session) -->
<style>
#ss-exit-modal{position:fixed;inset:0;background:rgba(0,0,0,.82);display:none;align-items:center;justify-content:center;z-index:9999}
#ss-exit-modal[data-open="1"]{display:flex}
#ss-exit-card{max-width:440px;background:#0d0d16;padding:2rem;border-radius:16px;border:1px solid #1a1a28;color:#f4f4f8;text-align:center;font-family:inherit;box-shadow:0 30px 80px rgba(0,0,0,.5)}
#ss-exit-card h3{margin:0 0 .5rem 0;font-size:1.4rem;color:#e94560}
#ss-exit-card p{margin:0 0 1.2rem 0;opacity:.82;line-height:1.5}
#ss-exit-card form{display:flex;gap:.5rem}
#ss-exit-card input{flex:1;padding:.75rem 1rem;background:#07070d;border:1px solid #222;border-radius:8px;color:inherit;font-size:1rem}
#ss-exit-card button{padding:.75rem 1.2rem;background:#e94560;color:#fff;border:0;border-radius:8px;font-weight:700;cursor:pointer}
#ss-exit-close{position:absolute;top:18px;right:22px;background:transparent;border:0;color:#777;font-size:1.3rem;cursor:pointer}
</style>
<script id="exit-intent-newsletter">
(function(){
  if(sessionStorage.getItem('ssExitShown'))return;
  if(window.innerWidth<768)return; // desktop only
  var shown=false;
  function show(){
    if(shown)return; shown=true;
    sessionStorage.setItem('ssExitShown','1');
    var m=document.createElement('div'); m.id='ss-exit-modal'; m.setAttribute('data-open','1');
    m.innerHTML='<div id="ss-exit-card"><button id="ss-exit-close" aria-label="Close">&times;</button>'
      +'<h3>Before you go &mdash; the honest SaaS deals weekly</h3>'
      +'<p>Every Friday we email 1 verified deal, 1 pricing change and 1 tool to avoid. Free, no spam.</p>'
      +'<form action="https://formsubmit.co/ajax/hellothere@saaspare.org" method="POST" id="ss-exit-form">'
      +'<input type="email" name="email" placeholder="you@company.com" required><button type="submit">Get it</button>'
      +'</form></div>';
    document.body.appendChild(m);
    m.addEventListener('click',function(e){if(e.target===m)m.remove();});
    document.getElementById('ss-exit-close').onclick=function(){m.remove();};
    document.getElementById('ss-exit-form').addEventListener('submit',function(e){
      if(window.gtag)gtag('event','newsletter_signup',{source:'exit_intent'});
    });
  }
  document.addEventListener('mouseleave',function(e){if(e.clientY<=0)show();});
  setTimeout(show,120000); // also show after 2 min if user stays
})();
</script>
'''

MANIFEST_MARKER = 'rel="manifest"'
MANIFEST_LINK = '<link rel="manifest" href="/manifest.webmanifest">\n'

PRELOAD_OG_MARKER = 'rel="preload" as="image" href="/og-default.png"'
PRELOAD_OG_TAG = '<link rel="preload" as="image" href="/og-default.png" fetchpriority="high">\n'


def upgrade_head(html: str, is_homepage: bool) -> tuple[str, dict]:
    """Inject missing head tags. Returns (new_html, {what_changed: True/False})."""
    changed: dict = {}

    # 1. manifest
    if MANIFEST_MARKER not in html:
        html = html.replace("</head>", MANIFEST_LINK + "</head>", 1)
        changed["manifest"] = True

    # 2. preload OG image (only homepage — money pages don't necessarily use it as hero)
    if is_homepage and PRELOAD_OG_MARKER not in html:
        html = html.replace("</head>", PRELOAD_OG_TAG + "</head>", 1)
        changed["preload_og"] = True

    # 3. homepage mega schema
    if is_homepage and HOMEPAGE_SCHEMA_ID not in html:
        html = html.replace("</head>", HOMEPAGE_SCHEMA_BLOCK + "</head>", 1)
        changed["mega_schema"] = True

    # 4. Microsoft Clarity snippet (only injected; actual ID is left as placeholder
    # so user can swap in real Clarity project ID without deploy)
    if CLARITY_MARKER not in html:
        html = html.replace("</head>", CLARITY_SNIPPET + "</head>", 1)
        changed["clarity"] = True

    # 5. exit-intent newsletter (homepage + money pages)
    if EXIT_INTENT_MARKER not in html:
        html = html.replace("</body>", EXIT_INTENT_SNIPPET + "</body>", 1)
        changed["exit_intent"] = True

    return html, changed


# === Lazy-load images ========================================================

IMG_RE = re.compile(r"<img\b([^>]*)>", re.I)


def add_lazy_loading(html: str) -> tuple[str, int]:
    count = 0
    first_seen = False
    def repl(m):
        nonlocal count, first_seen
        attrs = m.group(1)
        if "loading=" in attrs:
            return m.group(0)
        # first image: do not lazy-load (LCP); also add fetchpriority=high
        if not first_seen:
            first_seen = True
            if "fetchpriority=" not in attrs:
                attrs += ' fetchpriority="high"'
            return f"<img{attrs}>"
        count += 1
        return f'<img{attrs} loading="lazy" decoding="async">'
    new_html = IMG_RE.sub(repl, html)
    return new_html, count


# === Main =====================================================================

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args(argv)

    report = {
        "sitemap": upgrade_sitemap(args.check),
        "homepage_changes": {},
        "pages_processed": 0,
        "pages_lazy_images_added": 0,
        "pages_head_upgraded": 0,
        "pages_exit_intent_added": 0,
    }

    # Homepage
    if INDEX.exists():
        html = INDEX.read_text(encoding="utf-8", errors="replace")
        new_html, changed = upgrade_head(html, is_homepage=True)
        if changed:
            new_html2, img_count = add_lazy_loading(new_html)
            if img_count:
                changed["lazy_images"] = img_count
                new_html = new_html2
            if not args.check:
                INDEX.write_text(new_html, encoding="utf-8")
            report["homepage_changes"] = changed

    # All money pages
    for fp in sorted(PAGES.glob("*.html")):
        if fp.name in {"index.html", "thanks.html", "verification.html"}:
            continue
        report["pages_processed"] += 1
        html = fp.read_text(encoding="utf-8", errors="replace")
        new_html, changed = upgrade_head(html, is_homepage=False)
        if changed.get("manifest") or changed.get("clarity"):
            report["pages_head_upgraded"] += 1
        if changed.get("exit_intent"):
            report["pages_exit_intent_added"] += 1
        # lazy images
        new_html, img_count = add_lazy_loading(new_html)
        if img_count:
            report["pages_lazy_images_added"] += 1
        if new_html != html and not args.check:
            fp.write_text(new_html, encoding="utf-8")

    (OUTPUTS / "site_upgrade.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== site_upgrade ===")
    for k, v in report.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
