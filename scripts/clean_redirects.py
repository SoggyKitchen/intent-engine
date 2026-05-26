"""
Clean up _redirects:
1. Remove irrelevant CJ merchants (Bluetti, AOMEI, NCH, etc.)
2. Keep relevant CJ merchants (NordVPN, NordPass, Surfshark, Contabo, ESET, Sucuri)
3. Report what was removed

Run: uv run python scripts/clean_redirects.py
"""
from pathlib import Path

ROOT      = Path(__file__).resolve().parents[1]
REDIRECTS = ROOT / "site" / "_redirects"

# Slugs to remove — irrelevant to B2B SaaS audience, wasting click budget
REMOVE_SLUGS = {
    # Hardware (power stations)
    "bluetti-global",
    "bluetti-global-coupon",
    # Windows desktop software (not SaaS)
    "aomei",
    "aomei-anyviewer",
    "abelssoft-int",
    "nch-software",
    "o-o-software",
    "paragon-software-group",
    # Consumer antivirus (not B2B SaaS)
    "panda-office",
    "pc-protection",
    # Software key reseller (trust risk)
    "mr-key-shop",
    "operating-systems",  # points to mr-key-shop
    # Domain registrars ($1-5 commission, not SaaS audience)
    "netart-australia",
    "netart-australia-coupon",
    "netart-australia-homepage",
    "netart-ca-20",
    "netart-europe-coupon",
    "netart-europe",
    "netart-mt-homepage",
    "netart-us-ca",
    "netart-us-ca-coupon",
    "123-reg",
    "gandi",
    "ssl-certificates",
    # Off-topic ecommerce/hosting
    "evergreen-for-turbify",
    "turbify",
    # Random banner slug
    "268x106-eset-logo",
    # HostPapa (consumer hosting, low commission)
    "hostpapa",
}

def clean():
    content = REDIRECTS.read_text(encoding="utf-8")
    lines   = content.splitlines(keepends=True)

    kept    = []
    removed = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            kept.append(line)
            continue

        # Check if this line's slug is in our remove list
        # Format: /go/slug https://... 302
        parts = stripped.split()
        if parts and parts[0].startswith("/go/"):
            slug = parts[0][4:]  # strip /go/
            if slug in REMOVE_SLUGS:
                removed.append(slug)
                continue  # skip this line

        kept.append(line)

    REDIRECTS.write_text("".join(kept), encoding="utf-8")

    print(f"Removed {len(removed)} irrelevant redirect rules:")
    for slug in sorted(removed):
        print(f"  - /go/{slug}")
    print(f"Remaining lines: {len(kept)}")
    return removed

if __name__ == "__main__":
    removed = clean()
    if not removed:
        print("Nothing to remove (already clean or slugs not found).")
