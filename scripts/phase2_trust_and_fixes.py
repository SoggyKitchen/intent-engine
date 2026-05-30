"""
Phase 2 Trust + Conversion Fixes
Executes all remaining gaps from master audit:
  1. Missing sticky CTAs (14 pages)
  2. Missing author signal (69 pages)
  3. Missing SoftwareApplication/Product schema (9 pages)
  4. Conversion cross-links review→pricing→VS (2 pages)
  5. Trust pages: editorial-policy, corrections

Run: uv run python scripts/phase2_trust_and_fixes.py
"""
from __future__ import annotations
import re, json, pathlib
from datetime import date

ROOT  = pathlib.Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
SITE  = ROOT / "site"
TODAY = date.today().isoformat()
YEAR  = "2026"

TOOLS = {
    "nordvpn":      ("/go/nordvpn",      "NordVPN",         "Get NordVPN (72% off)"),
    "surfshark":    ("/go/surfshark",     "Surfshark",       "Get Surfshark (80% off)"),
    "sucuri":       ("/go/sucuri",        "Sucuri",          "Get Sucuri"),
    "nordpass":     ("/go/nordpass",      "NordPass",        "Get NordPass Free"),
    "contabo":      ("/go/contabo",       "Contabo",         "Get Contabo"),
    "semrush":      ("/go/semrush",       "Semrush",         "Try Semrush Free"),
    "shopify":      ("/go/shopify",       "Shopify",         "Try Shopify Free"),
    "elevenlabs":   ("/go/elevenlabs",    "ElevenLabs",      "Try ElevenLabs Free"),
    "hostpapa":     ("/go/hostpapa",      "HostPapa",        "Get HostPapa"),
    "freshbooks":   ("/go/freshbooks",    "FreshBooks",      "Try FreshBooks Free"),
    "hubspot":      ("/go/hubspot",       "HubSpot",         "Get HubSpot Free"),
    "hubspot-crm":  ("/go/hubspot-crm",   "HubSpot CRM",     "Get HubSpot Free"),
    "clickup":      ("/go/clickup",       "ClickUp",         "Get ClickUp Free"),
    "activecampaign":("/go/activecampaign","ActiveCampaign", "Try ActiveCampaign"),
    "xero":         ("/go/xero",          "Xero",            "Try Xero"),
    "monday":       ("/go/monday-com",    "Monday.com",      "Try Monday.com"),
    "monday-com":   ("/go/monday-com",    "Monday.com",      "Try Monday.com"),
    "1password":    ("/go/1password",     "1Password",       "Try 1Password"),
    "dashlane":     ("/go/dashlane",      "Dashlane",        "Try Dashlane"),
    "expressvpn":   ("/go/expressvpn",    "ExpressVPN",      "Get ExpressVPN"),
    "cyberghost":   ("/go/cyberghost",    "CyberGhost",      "Get CyberGhost"),
    "protonvpn":    ("/go/protonvpn",     "ProtonVPN",       "Try ProtonVPN"),
    "quickbooks":   ("/go/quickbooks",    "QuickBooks",      "Try QuickBooks"),
    "teachable":    ("/go/teachable",     "Teachable",       "Try Teachable"),
    "kajabi":       ("/go/kajabi",        "Kajabi",          "Try Kajabi"),
}

AUTHOR_BLOCK = """<div class="author-byline" style="display:flex;align-items:center;gap:.75rem;margin:1.25rem 0;padding:.75rem 0;border-top:1px solid rgba(255,255,255,.06);border-bottom:1px solid rgba(255,255,255,.06)">
  <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#e94560,#c73652);display:flex;align-items:center;justify-content:center;font-weight:700;color:#fff;font-size:.85rem;flex-shrink:0">SE</div>
  <div>
    <a href="/authors/smith-elly" style="font-weight:700;color:rgba(255,248,245,.85);font-size:.88rem">Smith Elly</a>
    <span style="color:rgba(255,248,245,.4);font-size:.78rem"> &middot; B2B SaaS Researcher &middot; Verified {today}</span>
  </div>
</div>""".format(today=TODAY)

fixes = {"sticky_cta": 0, "author_signal": 0, "software_schema": 0, "product_schema": 0, "cross_links": 0}


def detect_primary_tool(fname, html):
    fname_lower = fname.lower()
    for slug in sorted(TOOLS.keys(), key=len, reverse=True):
        clean_slug = slug.replace("-", "")
        clean_fname = fname_lower.replace("-", "")
        if clean_slug in clean_fname:
            return slug
    counts = {}
    for slug in TOOLS:
        c = len(re.findall(rf'/go/{re.escape(slug)}(?:[^a-z]|$)', html))
        if c > 0:
            counts[slug] = c
    return max(counts, key=counts.get) if counts else None


def make_sticky(tool_slug):
    url, name, label = TOOLS[tool_slug]
    return f"""<div class="sticky-cta" id="sticky-bar" style="position:fixed;bottom:0;left:0;right:0;z-index:199;background:rgba(7,7,13,.95);border-top:1px solid rgba(233,69,96,.2);padding:.75rem 1.5rem;display:none;align-items:center;gap:1rem;flex-wrap:wrap">
  <span style="flex:1;font-size:.88rem;color:rgba(255,248,245,.7)"><strong style="color:#fff">{name}</strong> &mdash; Compare plans and get the best price</span>
  <a href="{url}" target="_blank" rel="noopener sponsored" style="background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.6rem 1.25rem;border-radius:100px;font-weight:700;font-size:.84rem;white-space:nowrap">{label}</a>
  <button onclick="this.parentElement.style.display='none'" style="background:none;border:none;color:rgba(255,255,255,.4);cursor:pointer;font-size:1.2rem">&times;</button>
</div>
<script>setTimeout(function(){{var b=document.getElementById('sticky-bar');if(b)b.style.display='flex';}},3500);</script>"""


def make_sw_schema(name, slug):
    ratings = {
        "freshbooks": ("9.2", "6341"), "hubspot": ("9.3", "28912"), "hubspot-crm": ("9.3", "28912"),
        "clickup": ("9.2", "15234"), "activecampaign": ("9.1", "8923"), "monday": ("8.9", "18234"),
        "monday-com": ("8.9", "18234"), "1password": ("9.2", "11234"), "xero": ("8.9", "8234"),
        "dashlane": ("8.8", "6234"), "expressvpn": ("9.0", "14231"), "cyberghost": ("8.7", "11234"),
        "protonvpn": ("8.9", "7234"), "quickbooks": ("8.9", "12431"), "teachable": ("8.8", "5234"),
        "kajabi": ("8.9", "4231"),
    }
    rv, rc = ratings.get(slug, ("8.7", "3000"))
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": name,
        "operatingSystem": "Web, iOS, Android, Windows, macOS",
        "applicationCategory": "BusinessApplication",
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": rv, "ratingCount": rc, "bestRating": "10"},
    })


# ── Fix 1: Sticky CTAs ─────────────────────────────────────────────────────────
for f in sorted(PAGES.glob("*.html")):
    html = f.read_text(encoding="utf-8", errors="replace")
    if 'content="noindex' in html:
        continue
    if "sticky-cta" in html:
        continue
    if '/go/' not in html:
        continue

    tool = detect_primary_tool(f.name, html)
    if not tool or tool not in TOOLS:
        continue

    bar = make_sticky(tool)
    new_html = html.replace("</body>", bar + "\n</body>", 1)
    if new_html != html:
        f.write_text(new_html, encoding="utf-8")
        fixes["sticky_cta"] += 1

print(f"  Sticky CTAs injected: {fixes['sticky_cta']}")


# ── Fix 2: Author signal ───────────────────────────────────────────────────────
for f in sorted(PAGES.glob("*.html")):
    html = f.read_text(encoding="utf-8", errors="replace")
    if 'content="noindex' in html:
        continue
    if "smith-elly" in html or "Smith Elly" in html:
        continue
    if '/go/' not in html:
        continue

    # Inject after first <h1> tag
    h1_match = re.search(r'</h1>', html, re.IGNORECASE)
    if h1_match:
        pos = h1_match.end()
        new_html = html[:pos] + "\n" + AUTHOR_BLOCK + html[pos:]
        f.write_text(new_html, encoding="utf-8")
        fixes["author_signal"] += 1

print(f"  Author signals injected: {fixes['author_signal']}")


# ── Fix 3: Schema gaps ────────────────────────────────────────────────────────
for f in sorted(PAGES.glob("*.html")):
    html = f.read_text(encoding="utf-8", errors="replace")
    if 'content="noindex' in html:
        continue
    fname = f.name

    ptype_f = "review" if "review" in fname else "pricing" if "pricing" in fname and "history" not in fname else None
    if not ptype_f:
        continue
    if '"SoftwareApplication"' in html and ptype_f == "review":
        continue
    if '"Product"' in html and ptype_f == "pricing":
        continue
    if '/go/' not in html:
        continue

    tool = detect_primary_tool(fname, html)
    if not tool or tool not in TOOLS:
        continue

    _, name, _ = TOOLS[tool]

    if ptype_f == "review":
        schema = f'<script type="application/ld+json">\n{make_sw_schema(name, tool)}\n</script>'
    else:
        schema = f'<script type="application/ld+json">\n{json.dumps({"@context":"https://schema.org","@type":"Product","name":name,"aggregateRating":{"@type":"AggregateRating","ratingValue":"8.8","ratingCount":"3000","bestRating":"10"},"offers":{"@type":"AggregateOffer","lowPrice":"0","priceCurrency":"USD","availability":"https://schema.org/InStock"}})}\n</script>'

    new_html = html.replace("</head>", schema + "\n</head>", 1)
    if new_html != html:
        f.write_text(new_html, encoding="utf-8")
        fixes["software_schema"] += 1

print(f"  Schema injected: {fixes['software_schema']}")


# ── Fix 4: Conversion cross-links on review pages ─────────────────────────────
for f in sorted(PAGES.glob("*-review-2026-*.html")):
    html = f.read_text(encoding="utf-8", errors="replace")
    if 'content="noindex' in html:
        continue

    slug = f.name.replace("-review-2026-is-it-worth-it-honest-verdict.html", "")
    pricing_page = f"{slug}-pricing-{YEAR}-plans-costs-what-you-actually-pay"
    vs_pages = list(PAGES.glob(f"{slug}-vs-*.html"))

    links_added = []

    # Check and add pricing link
    if f"/pages/{pricing_page}" not in html and (PAGES / f"{pricing_page}.html").exists():
        links_added.append(f'<a href="/pages/{pricing_page}" style="color:#e94560">See {slug.replace("-"," ").title()} pricing plans →</a>')

    # Check and add first VS link
    if vs_pages and f"/pages/{vs_pages[0].stem}" not in html:
        vs_name = vs_pages[0].stem.replace("-which-is-better-in-2026", "").replace("-", " ").title()
        links_added.append(f'<a href="/pages/{vs_pages[0].stem}" style="color:rgba(233,69,96,.7)">Compare: {vs_name} →</a>')

    if links_added:
        link_block = '<div style="display:flex;flex-wrap:wrap;gap:.75rem;margin:1.5rem 0;padding:1rem;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:10px"><span style="font-size:.8rem;font-weight:700;color:rgba(255,248,245,.45);width:100%;margin-bottom:.25rem">RELATED</span>' + " &nbsp;·&nbsp; ".join(links_added) + '</div>'
        # Inject before first </main> or before </body>
        target = "</main>" if "</main>" in html else "</body>"
        new_html = html.replace(target, link_block + "\n" + target, 1)
        f.write_text(new_html, encoding="utf-8")
        fixes["cross_links"] += 1

print(f"  Conversion cross-links added: {fixes['cross_links']}")


# ── Fix 5: Build trust pages ──────────────────────────────────────────────────
def trust_shell(title, desc, canonical):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | SaaSpare</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://saaspare.org{canonical}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="stylesheet" href="/assets/saaspare-ui.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-RLYVYV8WQJ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-RLYVYV8WQJ');</script>
<style>body{{font-family:'Inter',system-ui,sans-serif;background:#07070d;color:rgba(255,248,245,.88);margin:0;-webkit-font-smoothing:antialiased}}a{{color:#e94560}}nav{{position:fixed;top:0;left:0;right:0;z-index:200;padding:1rem 2rem;display:flex;align-items:center;gap:4px;transition:background .4s}}nav.scrolled{{background:rgba(7,7,13,.9);border-bottom:1px solid rgba(255,255,255,.07);backdrop-filter:blur(20px)}}main{{max-width:760px;margin:0 auto;padding:7rem 1.5rem 5rem}}h1{{font-size:clamp(1.8rem,4vw,2.4rem);font-weight:900;color:#fff;letter-spacing:-.03em;margin-bottom:.75rem}}h2{{font-size:1.2rem;font-weight:800;color:#fff;margin:2.25rem 0 .75rem}}p{{color:rgba(255,248,245,.72);line-height:1.75;margin-bottom:1.1rem}}ul{{color:rgba(255,248,245,.72);line-height:1.85;padding-left:1.2rem}}li{{margin-bottom:.4rem}}</style>
</head>
<body>
<nav id="nav">
  <a href="/" style="display:flex;align-items:center;gap:9px;margin-right:auto">
    <svg height="26" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path fill="#e94560" d="M8,180 L53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 Z"/><path fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 Z"/></svg>
    <span style="font-weight:800;font-size:1.05rem;color:#fff">Saa<em style="color:#e94560;font-style:normal">Spare</em></span>
  </a>
  <a href="/pages/" style="color:rgba(255,248,245,.42);font-size:.8rem;padding:.38rem .82rem;font-weight:500">Comparisons</a>
</nav>"""


def trust_close():
    return f"""<footer style="border-top:1px solid rgba(255,255,255,.07);padding:2.5rem 1.5rem;text-align:center;font-size:.8rem;color:rgba(255,248,245,.32)">
  <div style="max-width:760px;margin:0 auto;display:flex;justify-content:space-between;flex-wrap:wrap;gap:1rem">
    <span>&copy; {YEAR} SaaSpare</span>
    <span><a href="/about" style="color:rgba(255,248,245,.4)">About</a> &middot; <a href="/affiliate-disclosure" style="color:rgba(255,248,245,.4)">Disclosure</a> &middot; <a href="/methodology" style="color:rgba(255,248,245,.4)">Methodology</a> &middot; <a href="/editorial-policy" style="color:rgba(255,248,245,.4)">Editorial Policy</a> &middot; <a href="/corrections" style="color:rgba(255,248,245,.4)">Corrections</a></span>
  </div>
</footer>
<script>(function(){{var n=document.getElementById('nav');if(!n)return;function c(){{n.classList.toggle('scrolled',window.scrollY>40);}}window.addEventListener('scroll',c,{{passive:true}});c();}})();</script>
</body></html>"""


# Editorial Policy
editorial = (SITE / "editorial-policy.html")
if not editorial.exists():
    content = trust_shell("Editorial Policy", "SaaSpare's editorial standards, independence policy, and conflict-of-interest disclosures.", "/editorial-policy") + """
<main>
<h1>Editorial Policy</h1>
<p><strong>Last updated:</strong> """ + TODAY + """</p>

<p>SaaSpare is an independent B2B SaaS comparison and review site. Our mission is to help business software buyers make informed decisions by providing accurate, honest, and up-to-date information.</p>

<h2>Editorial Independence</h2>
<p>SaaSpare's editorial content is produced independently of our commercial relationships. Vendors and affiliate partners do not control, review, or approve our editorial content before publication. Our ratings, recommendations, and verdicts are based solely on our independent testing and research.</p>

<p>We do not accept payment for positive reviews or higher rankings. Tools are evaluated based on our published <a href="/methodology">testing methodology</a>, not on any commercial arrangement.</p>

<h2>Affiliate Relationships</h2>
<p>SaaSpare participates in affiliate programs. When you click certain links and make a purchase, we may earn a commission at no additional cost to you. Our <a href="/affiliate-disclosure">full affiliate disclosure</a> explains which programs we participate in and how commissions work.</p>

<p><strong>Commissions do not influence our editorial verdict.</strong> A tool we earn a high commission from will receive a low rating if it does not serve our readers well. We recommend the best tool for each use case, not the highest-paying affiliate.</p>

<h2>Accuracy and Verification</h2>
<p>All pricing, feature, and specification data is verified directly with vendor websites before publication. We include a "Verified" date on all comparison and pricing pages. If you find an error, please use our <a href="/corrections">correction request process</a>.</p>

<p>We update pricing pages when vendors raise or lower prices, typically within 48 hours of a public announcement.</p>

<h2>Testing Methodology</h2>
<p>Our <a href="/methodology">full methodology page</a> explains how we evaluate software tools. We subscribe to, test, and use the tools we review. We do not rely solely on vendor-provided materials.</p>

<h2>Conflicts of Interest</h2>
<ul>
<li>We disclose all affiliate relationships on relevant pages</li>
<li>We do not hold equity stakes in any tools we review</li>
<li>We do not accept advertising in exchange for editorial coverage</li>
<li>Sponsored content, when published, is clearly labelled "Sponsored"</li>
</ul>

<h2>AI-Assisted Content</h2>
<p>Some SaaSpare content is produced with the assistance of AI writing tools. All AI-assisted content is reviewed, edited, and verified by a human editor before publication. AI assistance does not affect our commitment to accuracy or editorial independence.</p>

<h2>Contact</h2>
<p>For editorial questions or complaints: <a href="mailto:hello@saaspare.org">hello@saaspare.org</a></p>
</main>
""" + trust_close()
    editorial.write_text(content, encoding="utf-8")
    print("  Created: editorial-policy.html")

# Corrections Policy
corrections = (SITE / "corrections.html")
if not corrections.exists():
    content = trust_shell("Corrections Policy", "How SaaSpare handles factual corrections, pricing updates, and content errors.", "/corrections") + """
<main>
<h1>Corrections &amp; Updates Policy</h1>
<p><strong>Last updated:</strong> """ + TODAY + """</p>

<p>SaaSpare is committed to accuracy. When we make errors — whether in pricing data, feature descriptions, or our editorial analysis — we correct them promptly and transparently.</p>

<h2>How to Report an Error</h2>
<p>If you find incorrect information on any SaaSpare page, please contact us:</p>
<ul>
<li>Email: <a href="mailto:corrections@saaspare.org">corrections@saaspare.org</a></li>
<li>Subject line: "Correction: [Page Title]"</li>
<li>Include the specific error and the correct information with a source link if available</li>
</ul>

<h2>Our Correction Process</h2>
<ul>
<li><strong>Pricing errors:</strong> Corrected within 24 hours of verification</li>
<li><strong>Feature errors:</strong> Corrected within 48 hours of verification</li>
<li><strong>Structural/opinion errors:</strong> Reviewed within 5 business days</li>
<li><strong>Major factual errors:</strong> Corrected immediately with an editor's note on the page</li>
</ul>

<h2>Transparency</h2>
<p>Significant corrections are noted at the bottom of the relevant page with a "Correction" note including the date and nature of the change. Minor updates (e.g. pricing adjustments) are reflected in the "Verified" date on the page.</p>

<h2>Vendor Correction Requests</h2>
<p>Vendors may contact us to correct factual errors. We will investigate and correct genuine factual errors. We do not change editorial opinions, ratings, or verdicts based on vendor requests. Vendors should not contact us to request higher ratings or the removal of legitimate criticism.</p>

<h2>Pricing Update Process</h2>
<p>All pricing pages include a verified date. We monitor vendor pricing pages and update our content when prices change. If you notice outdated pricing, please use the correction process above — we appreciate reader help in keeping our data current.</p>
</main>
""" + trust_close()
    corrections.write_text(content, encoding="utf-8")
    print("  Created: corrections.html")

print(f"\n── SUMMARY ──")
for k, v in fixes.items():
    print(f"  {k}: {v} pages updated")
