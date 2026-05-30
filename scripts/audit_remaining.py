"""Find remaining high-priority gaps after CRO fixes."""
import re, pathlib, json
from collections import Counter, defaultdict

ROOT  = pathlib.Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"

TRACKED = {"nordvpn","nordvpn-kr","surfshark","surfshark-vpn","sucuri","sucuri-728x80",
           "nordpass","contabo","hostpapa","semrush","semrush-one","semrush-seo","semrush-trial",
           "shopify","shopify-ecommerce","shopify-plus","shopify-store",
           "elevenlabs","elevenlabs-ai","elevenlabs-voice","eleven-labs"}

def count_tracked(html):
    links = re.findall(r'href="/go/([^"?]+)', html)
    return sum(1 for l in links if l.split("?")[0] in TRACKED)

# Find pages missing sticky CTA but having tracked links
no_sticky_tracked = []
no_sticky_untracked = []
thin_high_intent = []

for f in sorted(PAGES.glob("*.html")):
    html = f.read_text(encoding="utf-8", errors="replace")
    if 'content="noindex' in html: continue
    has_sticky = "sticky-cta" in html
    tracked = count_tracked(html)
    all_aff = len(re.findall(r'href="/go/', html))
    words = len(re.sub(r"<[^>]+>", " ", html).split())
    ptype = "vs" if "-vs-" in f.name else "review" if "review" in f.name else "pricing" if "pricing" in f.name else "coupon" if "coupon" in f.name or "promo" in f.name else "free-trial" if "free-trial" in f.name else "best-hub" if f.name.startswith("best-") else "alternatives" if "alternative" in f.name else "other"

    if not has_sticky and tracked > 0:
        no_sticky_tracked.append((tracked, ptype, f.name[:70]))
    if not has_sticky and all_aff > 0 and tracked == 0:
        no_sticky_untracked.append((all_aff, ptype, f.name[:70]))
    if ptype in ("coupon","free-trial") and words < 200 and all_aff == 0:
        thin_high_intent.append((words, f.name[:70]))

print("=== PAGES WITH TRACKED AFF LINKS BUT NO STICKY CTA ===")
no_sticky_tracked.sort(reverse=True)
for tracked, ptype, name in no_sticky_tracked[:30]:
    print(f"  [{tracked:2d} tracked | {ptype:<12}] {name}")

print(f"\nTotal: {len(no_sticky_tracked)}")

print("\n=== THIN HIGH-INTENT PAGES (coupon/trial, <200 words, 0 aff links) ===")
thin_high_intent.sort()
for words, name in thin_high_intent[:20]:
    print(f"  [{words:3d} words] {name}")

# Best hub pages with tracked affiliate links
print("\n=== BEST-HUB PAGES WITH TRACKED LINKS BUT NO STICKY ===")
for tracked, ptype, name in no_sticky_tracked:
    if ptype == "best-hub":
        print(f"  [{tracked:2d} tracked] {name}")
