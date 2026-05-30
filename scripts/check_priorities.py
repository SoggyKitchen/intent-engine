"""Quick check of high-priority pages."""
import pathlib, re

PAGES = pathlib.Path(__file__).resolve().parents[1] / "site" / "pages"

targets = [
    "contabo-coupon-2026-discount-codes-promo.html",
    "nordvpn-review-2026-is-it-worth-it-honest-verdict.html",
    "sucuri-review-2026-is-it-worth-it-honest-verdict.html",
    "surfshark-review-2026-is-it-worth-it-honest-verdict.html",
]

for fname in targets:
    f = PAGES / fname
    html = f.read_text(encoding="utf-8", errors="replace")
    aff = len(re.findall(r'href="/go/', html))
    has_sticky = "sticky-cta" in html
    has_faq = "FAQPage" in html
    print(f"{fname[:60]}")
    print(f"  aff={aff} sticky={has_sticky} faq={has_faq} lines={len(html.splitlines())}")

print()
print("=== COUPON/FREE-TRIAL PAGES FOR CJ-TRACKED PROGRAMS ===")
tracked_slugs = ["nordvpn","surfshark","sucuri","nordpass","contabo","hostpapa","semrush","shopify","elevenlabs"]
for slug in tracked_slugs:
    for pattern in [f"{slug}-coupon*", f"{slug}-free-trial*", f"{slug}-promo*"]:
        for m in sorted(PAGES.glob(pattern)):
            html = m.read_text(encoding="utf-8", errors="replace")
            aff = len(re.findall(r'href="/go/', html))
            has_sticky = "sticky-cta" in html
            print(f"  [{aff:2d} aff sticky={int(has_sticky)}] {m.name[:65]}")
