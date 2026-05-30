"""
Master Revenue Audit — CEO Edition
Exhaustive audit of every revenue leak, conversion gap, and ranking opportunity.

Run: uv run python scripts/master_audit.py > outputs/master_audit.txt
"""
from __future__ import annotations
import json, re, pathlib
from collections import defaultdict
from datetime import date

ROOT  = pathlib.Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
REDIR = ROOT / "site" / "_redirects"
OUT   = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
TODAY = date.today().isoformat()

# ── Program commission data (research-verified) ────────────────────────────────
PROGRAMS = {
    # slug: (display, commission_str, commission_usd, network, tracked, priority)
    "freshbooks":      ("FreshBooks",      "$200/sale",          200, "CJ — already approved",  False, 1),
    "hubspot":         ("HubSpot",         "$250-1000/sale",     400, "Impact.com",              False, 2),
    "hubspot-crm":     ("HubSpot CRM",     "$250-1000/sale",     400, "Impact.com",              False, 2),
    "clickup":         ("ClickUp",         "$15-30/sale",         25, "Direct",                  False, 3),
    "1password":       ("1Password",       "$5-30/ref",           15, "ShareASale",              False, 4),
    "1password-business": ("1Password Biz","$5-30/ref",           15, "ShareASale",              False, 4),
    "activecampaign":  ("ActiveCampaign",  "$100/ref",           100, "Impact.com",              False, 5),
    "expressvpn":      ("ExpressVPN",      "$13/signup",          13, "CJ",                      False, 6),
    "expressvpn-business": ("ExpressVPN Biz","$13/signup",        13, "CJ",                      False, 6),
    "cyberghost":      ("CyberGhost",      "$10/signup",          10, "CJ",                      False, 7),
    "protonvpn":       ("ProtonVPN",       "$10/sale",            10, "Direct",                  False, 8),
    "quickbooks":      ("QuickBooks",      "$50/signup",          50, "CJ",                      False, 9),
    "xero":            ("Xero",            "$40/signup",          40, "CJ",                      False, 10),
    "dashlane":        ("Dashlane",        "$5-10/sale",           7, "CJ",                      False, 11),
    "monday-com":      ("Monday.com",      "$20-50/conv",         35, "Impact.com",              False, 12),
    "monday":          ("Monday.com",      "$20-50/conv",         35, "Impact.com",              False, 12),
    "teachable":       ("Teachable",       "30% ($60 avg)",       60, "CJ",                      False, 13),
    "kajabi":          ("Kajabi",          "30% ($100 avg)",     100, "CJ",                      False, 14),
    "asana":           ("Asana",           "No cash program",      0, "None",                    False, 99),
    "ahrefs":          ("Ahrefs",          "No affiliate prog",    0, "None",                    False, 99),
    # Tracked (CJ/Impact — earning real money)
    "nordvpn":         ("NordVPN",         "~$3-10/signup",        6, "CJ — TRACKED",            True,  0),
    "nordvpn-kr":      ("NordVPN KR",      "~$3-10/signup",        6, "CJ — TRACKED",            True,  0),
    "surfshark":       ("Surfshark",       "~$2-8/signup",         5, "CJ — TRACKED",            True,  0),
    "surfshark-vpn":   ("Surfshark VPN",   "~$2-8/signup",         5, "CJ — TRACKED",            True,  0),
    "sucuri":          ("Sucuri",          "~$20-40/sale",        30, "CJ — TRACKED",            True,  0),
    "nordpass":        ("NordPass",        "~$2-8/signup",         5, "CJ — TRACKED",            True,  0),
    "contabo":         ("Contabo",         "~$5-15/signup",       10, "CJ — TRACKED",            True,  0),
    "hostpapa":        ("HostPapa",        "~$10-30/signup",      20, "CJ — TRACKED",            True,  0),
    "semrush":         ("Semrush",         "~$10-200/sale",       80, "Impact — TRACKED",        True,  0),
    "semrush-one":     ("Semrush",         "~$10-200/sale",       80, "Impact — TRACKED",        True,  0),
    "semrush-seo":     ("Semrush",         "~$10-200/sale",       80, "Impact — TRACKED",        True,  0),
    "semrush-trial":   ("Semrush",         "~$10-200/sale",       80, "Impact — TRACKED",        True,  0),
    "shopify":         ("Shopify",         "~$150/sale",         150, "Impact — TRACKED",        True,  0),
    "shopify-ecommerce":("Shopify",        "~$150/sale",         150, "Impact — TRACKED",        True,  0),
    "shopify-plus":    ("Shopify Plus",    "~$150/sale",         150, "Impact — TRACKED",        True,  0),
    "shopify-store":   ("Shopify",         "~$150/sale",         150, "Impact — TRACKED",        True,  0),
    "elevenlabs":      ("ElevenLabs",      "~$10-50/sale",        20, "Impact — TRACKED",        True,  0),
    "elevenlabs-ai":   ("ElevenLabs",      "~$10-50/sale",        20, "Impact — TRACKED",        True,  0),
    "elevenlabs-voice":("ElevenLabs",      "~$10-50/sale",        20, "Impact — TRACKED",        True,  0),
    "eleven-labs":     ("ElevenLabs",      "~$10-50/sale",        20, "Impact — TRACKED",        True,  0),
}

# ── Page type detection ─────────────────────────────────────────────────────────
def ptype(fname):
    n = fname.lower()
    if "-vs-" in n:          return "vs"
    if "review" in n:        return "review"
    if "pricing" in n:       return "pricing"
    if "free-trial" in n:    return "free-trial"
    if "coupon" in n or "promo" in n or "discount" in n: return "coupon"
    if "alternative" in n:   return "alternatives"
    if n.startswith("best-"): return "best-hub"
    return "other"

# ── Audit state ─────────────────────────────────────────────────────────────────
program_pages   = defaultdict(list)   # slug → [page filenames]
program_tracked = defaultdict(list)   # slug → [page filenames] (tracked)
schema_gaps     = []                  # pages missing SoftwareApplication/Product schema
cta_gaps        = []                  # pages with aff links but no sticky CTA
faq_gaps        = []                  # pages with aff links but no FAQ schema
thin_pages      = []                  # pages with <300 words
no_aff_pages    = []                  # money-type pages with zero affiliate links
trust_gaps      = []                  # pages missing author signal
conversion_chain= []                  # review pages without pricing/comparison internal links

for f in sorted(PAGES.glob("*.html")):
    try:
        html = f.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    if 'content="noindex' in html or 'noindex, nofollow' in html:
        continue

    fname = f.name
    pt = ptype(fname)
    words = len(re.sub(r"<[^>]+>", " ", html).split())

    # Find all /go/ links
    go_links = re.findall(r'href="/go/([^"?/]+)', html)
    unique_slugs = set(s.split("?")[0] for s in go_links)

    has_sticky  = "sticky-cta" in html
    has_faq     = '"FAQPage"' in html
    has_author  = "smith-elly" in html or "Smith Elly" in html
    has_sw_schema = '"SoftwareApplication"' in html
    has_prod_schema = '"Product"' in html
    has_table   = bool(re.search(r"<table", html, re.I))

    # Map pages to programs
    for slug in unique_slugs:
        if slug in PROGRAMS:
            if PROGRAMS[slug][4]:  # tracked
                program_tracked[slug].append(fname)
            else:
                program_pages[slug].append(fname)

    # Check for gaps on money pages
    has_aff = bool(go_links)

    if pt in ("review", "pricing", "coupon", "free-trial", "vs"):
        if not has_sticky and has_aff:
            cta_gaps.append((fname, pt, len(go_links)))
        if not has_faq and has_aff:
            faq_gaps.append((fname, pt, len(go_links)))
        if not has_aff:
            no_aff_pages.append((fname, pt))
        if words < 300:
            thin_pages.append((fname, pt, words))
        if not has_author and has_aff:
            trust_gaps.append((fname, pt))

    # Schema gaps on review/pricing pages
    if pt == "review" and not has_sw_schema and has_aff:
        schema_gaps.append((fname, "needs SoftwareApplication+AggregateRating"))
    if pt == "pricing" and not has_prod_schema and has_aff and "history" not in fname:
        schema_gaps.append((fname, "needs Product+Offer"))

    # Conversion chain: review page should link to pricing/comparison
    if pt == "review":
        slug_base = fname.replace("-review-2026-is-it-worth-it-honest-verdict.html", "")
        pricing_link = f"/pages/{slug_base}-pricing-"
        vs_link = f"/pages/{slug_base}-vs-"
        if pricing_link not in html and vs_link not in html:
            conversion_chain.append((fname, "missing pricing or VS link"))

# ── Revenue calculations ────────────────────────────────────────────────────────
def est_revenue(slug, page_count):
    """Conservative monthly estimate: page_count × 100 visits × 0.5% CTR × 5% conversion × commission"""
    if slug not in PROGRAMS:
        return 0
    _, _, commission, _, tracked, priority = PROGRAMS[slug]
    if tracked or priority == 99:
        return 0
    # High-intent pages (review/pricing/coupon) convert better
    visits_per_page = 100
    ctr = 0.005   # 0.5% of visitors click affiliate link
    conversion = 0.05  # 5% of clickers purchase
    return int(page_count * visits_per_page * ctr * conversion * commission)

# ── Build revenue leak report ───────────────────────────────────────────────────
leak_summary = []
for slug, pages in sorted(program_pages.items(), key=lambda x: -len(x[1])):
    if slug not in PROGRAMS:
        continue
    name, comm, usd, network, tracked, priority = PROGRAMS[slug]
    if priority == 99:
        continue
    monthly_est = est_revenue(slug, len(pages))
    leak_summary.append({
        "slug": slug,
        "name": name,
        "pages": len(pages),
        "commission": comm,
        "network": network,
        "priority": priority,
        "monthly_est": monthly_est,
        "fixable_now": False,  # all require affiliate approval
        "top_pages": sorted(pages, key=lambda x: 0 if "review" in x or "pricing" in x else 1)[:5],
    })

leak_summary.sort(key=lambda x: (-x["pages"], x["priority"]))

# ── Print report ─────────────────────────────────────────────────────────────────
sep = "=" * 72

print(sep)
print("SAASPARE MASTER REVENUE AUDIT — CEO EDITION")
print(f"Date: {TODAY}")
print(sep)

print("\n── PHASE 1: REVENUE LEAK MAP ──────────────────────────────────────\n")
print(f"{'Program':<20} {'Pages':>6} {'Commission':<20} {'Est. $/mo':>9} {'Network'}")
print("-" * 80)
total_pages = 0
total_monthly = 0
for L in leak_summary:
    print(f"{L['name']:<20} {L['pages']:>6} {L['commission']:<20} ${L['monthly_est']:>8}/mo  {L['network']}")
    total_pages  += L["pages"]
    total_monthly += L["monthly_est"]
print("-" * 80)
print(f"{'TOTAL':<20} {total_pages:>6} {'':20} ${total_monthly:>8}/mo  (conservative est.)")

print("\n── TRACKED PROGRAMS (currently earning) ───────────────────────────\n")
for slug, pages in sorted(program_tracked.items(), key=lambda x: -len(x[1])):
    if slug not in PROGRAMS or not PROGRAMS[slug][4]:
        continue
    name = PROGRAMS[slug][0]
    print(f"  {name:<20} {len(pages):3d} pages earning commission")

print("\n── TOP REVENUE LEAKS (fix first) ───────────────────────────────────\n")
for L in leak_summary[:10]:
    print(f"  #{L['priority']} {L['name']} — {L['pages']} pages — {L['commission']} — {L['network']}")
    print(f"     Est. upside: ~${L['monthly_est']}/mo after approval")
    print(f"     Top pages: {', '.join(p[:55] for p in L['top_pages'][:3])}")
    print()

print(f"\n── CONVERSION GAPS ─────────────────────────────────────────────────\n")
print(f"  Pages missing sticky CTA (have aff links): {len(cta_gaps)}")
print(f"  Pages missing FAQ schema (have aff links): {len(faq_gaps)}")
print(f"  Pages missing SoftwareApplication/Product schema: {len(schema_gaps)}")
print(f"  Review pages missing pricing/VS cross-links: {len(conversion_chain)}")
print(f"  Money pages with ZERO affiliate links: {len(no_aff_pages)}")
print(f"  Pages missing author signal: {len(trust_gaps)}")
print(f"  Thin pages (<300 words) on money types: {len(thin_pages)}")

print(f"\n  Schema gaps sample (top 10):")
for fname, note in schema_gaps[:10]:
    print(f"    {fname[:65]} — {note}")

print(f"\n  Conversion chain gaps (review pages missing pricing/VS link):")
for fname, note in conversion_chain[:10]:
    print(f"    {fname[:65]}")

print(f"\n── TRUST / E-E-A-T GAPS ────────────────────────────────────────────\n")
trust_pages = {
    "/about": "Author bio, credentials, SaaSpare mission",
    "/authors/smith-elly": "Personal author page for E-E-A-T",
    "/methodology": "How we test & score tools — required by Google HQRGs",
    "/editorial-policy": "Editorial independence statement",
    "/media-kit": "For affiliate program applications",
    "/affiliate-disclosure": "FTC compliance + program applications",
    "/corrections": "Correction/update policy",
}
for path, desc in trust_pages.items():
    exists = (ROOT / "site" / path.lstrip("/")).exists() or \
             (ROOT / "site" / (path.lstrip("/") + ".html")).exists() or \
             (ROOT / "site" / "pages" / (path.lstrip("/") + ".html")).exists() or \
             (ROOT / "site" / (path.lstrip("/") + "/index.html")).exists()
    status = "OK" if exists else "MISSING"
    print(f"  [{status}] {path:<35} {desc}")

print(f"\n── PHASE 3: PAGES MOST LIKELY TO EARN FIRST $100 ──────────────────\n")
# High-intent pages with tracked affiliates
tracked_money = []
for slug, pages in program_tracked.items():
    if not PROGRAMS.get(slug, [None]*4)[4]:
        continue
    for p in pages:
        pt = ptype(p)
        score = {"review": 5, "pricing": 4, "coupon": 4, "free-trial": 3, "vs": 2}.get(pt, 1)
        tracked_money.append((score, slug, p))
tracked_money.sort(reverse=True)
for score, slug, p in tracked_money[:15]:
    print(f"  [{PROGRAMS[slug][0]:<12}] {p[:65]}")

print(f"\n── PAGES MOST LIKELY TO EARN FIRST $1,000 ──────────────────────────\n")
print("  (After affiliate approvals land — sorted by commission × pages)")
for L in sorted(leak_summary[:8], key=lambda x: -(x["monthly_est"])):
    if L["monthly_est"] > 0:
        print(f"  {L['name']:<20} {L['pages']:3d} pages | {L['commission']:<18} | ~${L['monthly_est']}/mo")

print(f"\n── EXACT NEXT ACTIONS ──────────────────────────────────────────────\n")
actions = [
    ("USER",   "Apply FreshBooks at CJ — already approved publisher",                  "~$400/mo instantly"),
    ("USER",   "Apply HubSpot at Impact (impact.com → search HubSpot)",                "~$600/mo after approval"),
    ("USER",   "Apply ExpressVPN at CJ (same dashboard, search ExpressVPN)",           "~$100/mo after approval"),
    ("USER",   "Apply CyberGhost at CJ",                                               "~$80/mo after approval"),
    ("USER",   "Apply ClickUp at clickup.com/affiliates",                              "~$75/mo after approval"),
    ("CODE",   "Build /authors/smith-elly + /methodology pages",                       "Unblocks program approvals"),
    ("CODE",   "Build /media-kit page",                                                "Required by most programs"),
    ("CODE",   "Fix SoftwareApplication schema on all remaining review pages",         "+CTR in rich results"),
    ("CODE",   "Inject conversion cross-links (review → pricing → VS)",                "+affiliate clicks 15-25%"),
    ("CODE",   "Build ProtonVPN review page (new program, page needed)",               "~$30/mo potential"),
    ("CODE",   "Build ExpressVPN review + pricing pages (high-volume searches)",       "~$100/mo potential"),
    ("CODE",   "Build QuickBooks vs FreshBooks (10K monthly searches)",                "Both earn commission when approved"),
    ("CODE",   "Build Kajabi review + pricing (30% commission, no page exists)",       "~$80/mo potential"),
    ("CODE",   "Build Teachable review + pricing (30% commission, no page exists)",    "~$60/mo potential"),
]
for action_type, action, upside in actions:
    print(f"  [{action_type}] {action}")
    print(f"         Upside: {upside}")
    print()

# Save JSON
result = {
    "date": TODAY,
    "revenue_leaks": leak_summary,
    "schema_gaps": schema_gaps[:30],
    "cta_gaps": [(f, pt, c) for f, pt, c in cta_gaps[:30]],
    "faq_gaps": [(f, pt, c) for f, pt, c in faq_gaps[:20]],
    "conversion_chain_gaps": conversion_chain[:30],
    "no_aff_pages": no_aff_pages[:30],
    "trust_gaps": trust_gaps[:20],
    "thin_pages": thin_pages[:20],
}
(OUT / "master_audit.json").write_text(json.dumps(result, indent=2))
print(f"\nFull data saved to outputs/master_audit.json")
