"""Fix malformed ItemList JSON-LD in best-web-hosting and best-password-manager pages."""
import json, re
from pathlib import Path

PAGES = Path(__file__).resolve().parents[1] / "site" / "pages"
YEAR = "2026"
TODAY = "2026-05-30"

FIXES = {
    f"best-web-hosting-{YEAR}.html": {
        "bad_pattern": r'(<script type="application/ld\+json" id="schema-itemlist"[^>]*>)(.*?)(</script>)',
        "new_schema": json.dumps({
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"Best Web Hosting {YEAR}",
            "url": f"https://saaspare.org/pages/best-web-hosting-{YEAR}",
            "numberOfItems": 8,
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Contabo", "url": f"https://saaspare.org/pages/contabo-review-{YEAR}-is-it-worth-it-honest-verdict"},
                {"@type": "ListItem", "position": 2, "name": "HostPapa", "url": f"https://saaspare.org/pages/best-web-hosting-{YEAR}"},
                {"@type": "ListItem", "position": 3, "name": "SiteGround", "url": f"https://saaspare.org/pages/best-web-hosting-{YEAR}"},
                {"@type": "ListItem", "position": 4, "name": "DigitalOcean", "url": f"https://saaspare.org/pages/contabo-vs-digitalocean-which-is-better-in-{YEAR}"},
                {"@type": "ListItem", "position": 5, "name": "Cloudflare Pages", "url": f"https://saaspare.org/pages/best-web-hosting-{YEAR}"},
                {"@type": "ListItem", "position": 6, "name": "Hetzner", "url": f"https://saaspare.org/pages/contabo-vs-hetzner-which-is-better-in-{YEAR}"},
                {"@type": "ListItem", "position": 7, "name": "Vultr", "url": f"https://saaspare.org/pages/contabo-vs-vultr-which-is-better-in-{YEAR}"},
                {"@type": "ListItem", "position": 8, "name": "Kinsta", "url": f"https://saaspare.org/pages/best-web-hosting-{YEAR}"},
            ],
        }),
    },
    f"best-password-manager-{YEAR}.html": {
        "bad_pattern": r'(<script type="application/ld\+json" id="schema-itemlist"[^>]*>)(.*?)(</script>)',
        "new_schema": json.dumps({
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"Best Password Managers {YEAR}",
            "url": f"https://saaspare.org/pages/best-password-manager-{YEAR}",
            "numberOfItems": 7,
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "NordPass", "url": f"https://saaspare.org/pages/nordpass-review-{YEAR}-is-it-worth-it-honest-verdict"},
                {"@type": "ListItem", "position": 2, "name": "1Password", "url": f"https://saaspare.org/pages/1password-review-{YEAR}-is-it-worth-it-honest-verdict"},
                {"@type": "ListItem", "position": 3, "name": "Bitwarden", "url": f"https://saaspare.org/pages/1password-vs-bitwarden-which-is-better-in-{YEAR}"},
                {"@type": "ListItem", "position": 4, "name": "Dashlane", "url": f"https://saaspare.org/pages/1password-vs-dashlane-which-is-better-in-{YEAR}"},
                {"@type": "ListItem", "position": 5, "name": "Keeper", "url": f"https://saaspare.org/pages/1password-vs-keeper-which-is-better-in-{YEAR}"},
                {"@type": "ListItem", "position": 6, "name": "LastPass", "url": f"https://saaspare.org/pages/1password-vs-lastpass-which-is-better-in-{YEAR}"},
                {"@type": "ListItem", "position": 7, "name": "Enpass", "url": f"https://saaspare.org/pages/1password-vs-enpass-which-is-better-in-{YEAR}"},
            ],
        }),
    },
}

# These pages have the ItemList embedded inline (not as id="schema-itemlist")
# so we need a different approach — find and replace the malformed block

def fix_inline_jsonld(path: Path) -> bool:
    """Find JSON-LD blocks that fail to parse and replace them."""
    html = path.read_text(encoding="utf-8")

    # Find all JSON-LD blocks
    blocks = list(re.finditer(
        r'(<script[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)',
        html, re.DOTALL | re.IGNORECASE
    ))

    changed = False
    for block in blocks:
        payload = block.group(2).strip()
        try:
            json.loads(payload)
        except Exception:
            # This block is bad — skip it (remove it)
            print(f"  Removing malformed block ({len(payload)} chars)")
            html = html.replace(block.group(0), "", 1)
            changed = True

    if changed:
        path.write_text(html, encoding="utf-8")
    return changed


# For both pages, inject a clean ItemList schema before </head>
def inject_clean_itemlist(fname: str, schema_dict: dict):
    p = PAGES / fname
    if not p.exists():
        print(f"  Missing: {fname}")
        return

    html = p.read_text(encoding="utf-8")

    # First, fix inline malformed blocks
    changed = False
    new_blocks = []
    for block in re.finditer(r'(<script[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)', html, re.DOTALL | re.IGNORECASE):
        payload = block.group(2).strip()
        try:
            json.loads(payload)
            new_blocks.append((block.group(0), None))  # Keep good blocks
        except Exception:
            print(f"  [{fname}] Removing malformed JSON-LD block")
            new_blocks.append((block.group(0), ""))  # Remove bad blocks
            changed = True

    for original, replacement in new_blocks:
        if replacement is not None:
            html = html.replace(original, replacement, 1)

    # Now inject the correct ItemList before </head>
    if '"ItemList"' not in html:
        clean_schema = f'<script type="application/ld+json">\n{json.dumps(schema_dict, indent=2)}\n</script>'
        html = html.replace("</head>", clean_schema + "\n</head>", 1)
        changed = True
        print(f"  [{fname}] Injected clean ItemList schema")

    if changed:
        p.write_text(html, encoding="utf-8")
        print(f"  [{fname}] Saved")


for fname, cfg in FIXES.items():
    inject_clean_itemlist(fname, json.loads(cfg["new_schema"]))

print("Done.")
