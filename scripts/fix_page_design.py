"""
fix_page_design.py — Upgrade sloppy pages to match the Ahrefs vs Semrush
quality standard (pic 2). Targets pricing, review, VS, and free-plan pages
that were built with old plain-text templates.

Also injects company logos via simpleicons.org CDN.

Logo map: tool slug -> simpleicons name + brand color
"""
import re, json
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
TODAY = date.today().isoformat()
YR = "2026"

# ── Logo map (slug fragment -> simpleicons.org name, brand hex) ──────────────
LOGO_MAP = {
    "hubspot":        ("hubspot",        "ff7a59"),
    "clickup":        ("clickup",        "7b68ee"),
    "monday":         ("monday",         "f6358a"),
    "asana":          ("asana",          "f06a6a"),
    "notion":         ("notion",         "000000"),
    "airtable":       ("airtable",       "18bfff"),
    "trello":         ("trello",         "0052cc"),
    "jira":           ("jira",           "0052cc"),
    "slack":          ("slack",          "4a154b"),
    "zoom":           ("zoom",           "2d8cff"),
    "salesforce":     ("salesforce",     "00a1e0"),
    "pipedrive":      ("pipedrive",      "26292c"),
    "freshbooks":     ("freshbooks",     "0075dd"),
    "quickbooks":     ("intuit",         "2ca01c"),
    "xero":           ("xero",           "13b5ea"),
    "wave":           ("wave",           "1bc0a1"),
    "nordvpn":        ("nordvpn",        "4687ff"),
    "surfshark":      ("surfshark",      "1d2b4f"),
    "expressvpn":     ("expressvpn",     "da3940"),
    "protonvpn":      ("protonvpn",      "6d4aff"),
    "nordpass":       ("nordpass",       "4687ff"),
    "1password":      ("1password",      "1a8cff"),
    "bitwarden":      ("bitwarden",      "175ddc"),
    "dashlane":       ("dashlane",       "007ae1"),
    "lastpass":       ("lastpass",       "d32d27"),
    "semrush":        ("semrush",        "ff642d"),
    "ahrefs":         ("ahrefs",         "ff7733"),
    "shopify":        ("shopify",        "96bf48"),
    "woocommerce":    ("woocommerce",    "96588a"),
    "bigcommerce":    ("bigcommerce",    "34313f"),
    "squarespace":    ("squarespace",    "000000"),
    "wix":            ("wix",            "faad4d"),
    "elementor":      ("elementor",      "92003b"),
    "webflow":        ("webflow",        "4353ff"),
    "wordpress":      ("wordpress",      "21759b"),
    "getresponse":    ("getresponse",    "00afec"),
    "mailchimp":      ("mailchimp",      "ffe01b"),
    "activecampaign": ("activecampaign", "356ae4"),
    "convertkit":     ("convertkit",     "fb6970"),
    "brevo":          ("brevo",          "0092ff"),
    "aweber":         ("aweber",         "77b800"),
    "klaviyo":        ("klaviyo",        "000000"),
    "datadog":        ("datadog",        "632ca6"),
    "mixpanel":       ("mixpanel",       "7856ff"),
    "amplitude":      ("amplitude",      "176ede"),
    "hotjar":         ("hotjar",         "fd3a5c"),
    "intercom":       ("intercom",       "1f8ded"),
    "zendesk":        ("zendesk",        "03363d"),
    "freshdesk":      ("freshworks",     "25c16f"),
    "linear":         ("linear",         "5e6ad2"),
    "github":         ("github",         "181717"),
    "gitlab":         ("gitlab",         "fc6d26"),
    "vercel":         ("vercel",         "000000"),
    "cloudflare":     ("cloudflare",     "f38020"),
    "contabo":        ("contabo",        "1e3a5f"),
    "digitalocean":   ("digitalocean",   "0080ff"),
    "aws":            ("amazonaws",      "ff9900"),
    "google":         ("google",         "4285f4"),
    "microsoft":      ("microsoft",      "737373"),
    "deel":           ("deel",           "635bff"),
    "rippling":       ("rippling",       "f09b35"),
    "gusto":          ("gusto",          "f45d48"),
    "bamboohr":       ("bamboohr",       "73aa24"),
    "fiverr":         ("fiverr",         "1dbf73"),
    "upwork":         ("upwork",         "6fda44"),
    "loom":           ("loom",           "625df5"),
    "miro":           ("miro",           "ffdd33"),
    "figma":          ("figma",          "f24e1e"),
    "canva":          ("canva",          "00c4cc"),
    "typeform":       ("typeform",       "262627"),
    "surveymonkey":   ("surveymonkey",   "00bf6f"),
    "docusign":       ("docusign",       "f5a800"),
    "dropbox":        ("dropbox",        "0061ff"),
    "box":            ("box",            "0061d5"),
    "zapier":         ("zapier",         "ff4a00"),
    "make":           ("make",           "6d00cc"),
    "stripe":         ("stripe",         "635bff"),
    "chargebee":      ("chargebee",      "ff5722"),
    "paddle":         ("paddle",         "c3f53b"),
}

def get_logo_url(tool_slug: str) -> str | None:
    """Return a simpleicons CDN URL for a tool, or None if not mapped."""
    slug = tool_slug.lower().replace("-", "").replace("_", "").replace(".", "")
    for key, (icon, color) in LOGO_MAP.items():
        if key.replace("-", "") in slug or slug in key.replace("-", ""):
            return f"https://cdn.simpleicons.org/{icon}/{color}"
    return None

def make_logo_img(tool_name: str, slug: str, size: int = 32) -> str:
    url = get_logo_url(slug)
    if url:
        return f'<img src="{url}" alt="{tool_name} logo" width="{size}" height="{size}" style="border-radius:6px;object-fit:contain;background:#fff;padding:3px;" loading="lazy" onerror="this.style.display=\'none\'">'
    # Fallback: colored initials badge
    initials = "".join(w[0].upper() for w in tool_name.split()[:2])
    return f'<span style="display:inline-flex;align-items:center;justify-content:center;width:{size}px;height:{size}px;border-radius:6px;background:linear-gradient(135deg,#ff416d,#c9294f);color:#fff;font-weight:900;font-size:{int(size*0.38)}px;">{initials}</span>'


# ── Better comparison page CSS injection ─────────────────────────────────────
UPGRADE_CSS = """<style id="sp-page-upgrade">
/* ── Page upgrade: better visual design for all pages ───────────────────── */
.sp-main,.main-content,main{max-width:860px;margin:0 auto;padding:0 1.5rem 4rem}
h1{font-size:clamp(1.8rem,4vw,2.6rem);font-weight:900;letter-spacing:-.03em;
   line-height:1.15;margin:1.5rem 0 1rem;color:rgba(255,248,245,.95)}
h2{font-size:1.35rem;font-weight:800;letter-spacing:-.02em;margin:2rem 0 .75rem;
   color:rgba(255,248,245,.9);border-bottom:1px solid rgba(255,255,255,.06);
   padding-bottom:.5rem}
h3{font-size:1.05rem;font-weight:700;margin:1.5rem 0 .5rem;color:rgba(255,248,245,.85)}
p,li{line-height:1.75;color:rgba(255,248,245,.78);font-size:.96rem}
.meta{display:flex;flex-wrap:wrap;gap:.5rem;margin:.75rem 0 1.5rem;font-size:.8rem;
      color:rgba(255,248,245,.45)}
.meta a{color:rgba(255,248,245,.55);text-decoration:none}
/* Score cards */
.score-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
             gap:14px;margin:1.5rem 0}
.score-card{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
            border-radius:14px;padding:18px;position:relative}
.score-card.winner{border-color:rgba(255,65,109,.4);
                   background:linear-gradient(135deg,rgba(255,65,109,.08),rgba(200,41,80,.05))}
.score-card-badge{position:absolute;top:-10px;right:14px;background:#ff416d;color:#fff;
                  font-size:.68rem;font-weight:800;padding:3px 10px;border-radius:100px;
                  letter-spacing:.04em;text-transform:uppercase}
.score-card-logo{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.score-card-name{font-weight:800;font-size:1rem;color:rgba(255,248,245,.9)}
.score-card-desc{font-size:.8rem;color:rgba(255,248,245,.5);margin-bottom:12px;line-height:1.5}
.score-card-score{font-size:1.8rem;font-weight:900;color:#ff416d;letter-spacing:-.04em}
.score-card-score em{font-style:normal;font-size:.9rem;color:rgba(255,248,245,.4);
                      font-weight:500;margin-left:2px}
/* VS table */
.vs-table-wrap{overflow-x:auto;margin:1.5rem 0;border-radius:12px;
               border:1px solid rgba(255,255,255,.07)}
.vs-table{width:100%;border-collapse:collapse;font-size:.88rem}
.vs-table th{background:rgba(255,255,255,.05);color:rgba(255,248,245,.5);
             font-size:.72rem;text-transform:uppercase;letter-spacing:.07em;
             padding:10px 14px;text-align:left;border-bottom:1px solid rgba(255,255,255,.07)}
.vs-table td{padding:10px 14px;border-bottom:1px solid rgba(255,255,255,.04);
             color:rgba(255,248,245,.78);vertical-align:top}
.vs-table tr:last-child td{border:0}
.vs-table tr:hover td{background:rgba(255,255,255,.02)}
.vs-table td:first-child{color:rgba(255,248,245,.5);font-size:.82rem;font-weight:600}
/* Quick answer box */
.qa{background:rgba(255,65,109,.06);border:1px solid rgba(255,65,109,.2);
    border-radius:12px;padding:1.25rem 1.5rem;margin:1.25rem 0}
.qa h3{margin:0 0 .5rem;font-size:.88rem;text-transform:uppercase;letter-spacing:.08em;
       color:#ff416d;font-weight:800}
.qa p{margin:0;font-size:.92rem;color:rgba(255,248,245,.85)}
/* CTA card */
.cta-card{background:linear-gradient(135deg,rgba(255,65,109,.1),rgba(120,20,40,.07));
          border:1px solid rgba(255,65,109,.3);border-radius:14px;
          padding:1.5rem;margin:1.5rem 0;display:flex;align-items:center;
          gap:1rem;flex-wrap:wrap}
.cta-card strong{font-size:1rem;color:rgba(255,248,245,.95);flex:1;min-width:200px}
.btn-primary{background:linear-gradient(135deg,#ff416d,#c9294f);color:#fff;
             padding:.55rem 1.4rem;border-radius:100px;font-weight:700;
             font-size:.85rem;text-decoration:none;display:inline-block;
             box-shadow:0 4px 16px rgba(255,65,109,.35);
             transition:transform .15s,box-shadow .15s;white-space:nowrap}
.btn-primary:hover{transform:translateY(-1px);box-shadow:0 8px 24px rgba(255,65,109,.5)}
.btn-secondary{background:rgba(255,255,255,.07);color:rgba(255,248,245,.85);
               padding:.55rem 1.4rem;border-radius:100px;font-weight:600;
               font-size:.85rem;text-decoration:none;display:inline-block;
               border:1px solid rgba(255,255,255,.12);
               transition:all .15s;white-space:nowrap}
.btn-secondary:hover{background:rgba(255,255,255,.11);color:#fff}
/* Verdict card */
.verdict-card{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
              border-radius:14px;padding:1.5rem;margin:1rem 0}
.verdict-winner{font-weight:800;font-size:1rem;color:#ff416d;margin-bottom:.5rem}
/* Pricing grid */
.pricing-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
              gap:14px;margin:1.5rem 0}
.price-card{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
            border-radius:14px;padding:1.5rem}
.price-tool{font-size:.82rem;text-transform:uppercase;letter-spacing:.08em;
            color:rgba(255,248,245,.45);font-weight:700;margin-bottom:.5rem}
.price-amount{font-size:2rem;font-weight:900;color:rgba(255,248,245,.95);
              letter-spacing:-.04em;line-height:1}
.price-period{font-size:.78rem;color:rgba(255,248,245,.4);margin-top:.25rem}
/* Rank list */
.rank-list{display:flex;flex-direction:column;gap:12px;margin:1.5rem 0}
.rank-item{display:flex;gap:14px;background:rgba(255,255,255,.04);
           border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:1rem 1.25rem}
.rank-num{width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#ff416d,#c9294f);
          color:#fff;font-weight:900;font-size:.82rem;display:flex;align-items:center;
          justify-content:center;flex-shrink:0;box-shadow:0 4px 12px rgba(255,65,109,.35)}
.rank-name{font-weight:800;font-size:.95rem;color:rgba(255,248,245,.9);margin-bottom:.25rem}
.rank-desc{font-size:.83rem;color:rgba(255,248,245,.55);line-height:1.5}
/* Pros/cons */
.pros-cons{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:1.5rem 0}
.pros,.cons{background:rgba(255,255,255,.04);border-radius:12px;padding:1.25rem;
            border:1px solid rgba(255,255,255,.07)}
.pros{border-top:3px solid #22c55e}.cons{border-top:3px solid #ef4444}
.pros h3,.cons h3{margin:0 0 .75rem;font-size:.88rem;font-weight:800;
                  text-transform:uppercase;letter-spacing:.06em}
.pros h3{color:#22c55e}.cons h3{color:#ef4444}
.pros ul,.cons ul{margin:0;padding-left:1.2rem}
.pros li,.cons li{font-size:.83rem;margin-bottom:.4rem;color:rgba(255,248,245,.75)}
/* Breadcrumbs */
.crumbs{font-size:.78rem;color:rgba(255,248,245,.4);margin-bottom:1rem}
.crumbs a{color:rgba(255,248,245,.4);text-decoration:none}
.crumbs a:hover{color:rgba(255,248,245,.7)}
.crumbs span{margin:0 .4rem}
/* Disclosure */
.disclosure{font-size:.75rem;color:rgba(255,248,245,.35);margin-top:2rem;
            padding-top:1rem;border-top:1px solid rgba(255,255,255,.06)}
@media(max-width:600px){
  .pros-cons{grid-template-columns:1fr}
  .score-cards{grid-template-columns:1fr}
  .pricing-grid{grid-template-columns:1fr}
}
</style>"""


def needs_upgrade(html: str) -> bool:
    """Check if page has old/plain design that needs upgrading."""
    # Pages that already have the upgrade CSS are fine
    if 'id="sp-page-upgrade"' in html:
        return False
    # Pages with no styling at all (just raw text) need it
    if 'saaspare-v2.css' not in html and 'sp-shared.css' not in html:
        return True
    # Pages with saaspare-v2.css but very minimal content structure
    return False


def inject_upgrade_css(html: str) -> str:
    """Inject upgrade CSS before </head>."""
    if 'id="sp-page-upgrade"' in html:
        return html
    return html.replace("</head>", UPGRADE_CSS + "\n</head>", 1)


def inject_logos_in_vs_table(html: str, slug: str) -> str:
    """Attempt to add logos to VS table headers based on slug."""
    # Extract tool names from slug (e.g. "hubspot-vs-salesforce" -> hubspot, salesforce)
    if "-vs-" not in slug:
        return html

    parts = slug.split("-vs-")[0:2]
    if len(parts) < 2:
        return html

    tool_a = parts[0].split("-")[0]  # First word of first tool
    tool_b_raw = parts[1]
    # Remove common suffixes
    for suffix in ["-which-is-better-in-2026", "-2026", "-which-is-better"]:
        tool_b_raw = tool_b_raw.replace(suffix, "")
    tool_b = tool_b_raw.split("-")[0]

    logo_a = get_logo_url(tool_a)
    logo_b = get_logo_url(tool_b)

    if logo_a:
        logo_a_html = f'<img src="{logo_a}" width="18" height="18" style="vertical-align:middle;margin-right:5px;border-radius:4px;background:#fff;padding:1px;" loading="lazy" onerror="this.style.display=\'none\'">'
        # Add logo to first vs table header if not already there
        html = re.sub(
            r'(<th[^>]*>)(' + re.escape(parts[0].replace("-", " ").title()) + r')',
            r'\1' + logo_a_html + r'\2',
            html, count=1, flags=re.IGNORECASE
        )

    return html


def main():
    pages = list((SITE / "pages").glob("*.html"))
    pages += [SITE / "index.html", SITE / "about.html", SITE / "contact.html"]

    upgraded = 0
    logo_injected = 0

    print(f"Page design upgrade — scanning {len(pages)} pages...")

    for path in pages:
        try:
            html = path.read_text(encoding="utf-8", errors="replace")
            orig = html
            changed = False

            # 1. Inject upgrade CSS if page looks plain/old
            if needs_upgrade(html):
                html = inject_upgrade_css(html)
                changed = True

            # 2. Inject logos in VS tables
            slug = path.stem
            if "-vs-" in slug:
                new_html = inject_logos_in_vs_table(html, slug)
                if new_html != html:
                    html = new_html
                    logo_injected += 1
                    changed = True

            if changed and html != orig:
                path.write_text(html, encoding="utf-8")
                upgraded += 1

        except Exception as e:
            pass

    print(f"Done: {upgraded} pages upgraded, {logo_injected} VS pages got logos")
    print()
    print("Note: The Ahrefs vs Semrush style (pic 2) is the engine's own template.")
    print("Pages we build in waves now use the upgrade CSS above.")
    print("Run this again after any wave to keep pages consistent.")


if __name__ == "__main__":
    main()
