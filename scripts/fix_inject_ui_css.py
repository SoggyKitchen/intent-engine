"""Inject saaspare-ui.css into all pages that are missing it."""
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"
UI_TAG = '<link rel="stylesheet" href="/assets/saaspare-ui.css">'

all_pages = list((SITE / "pages").glob("*.html"))
for subdir in ["blog", "authors"]:
    all_pages.extend((SITE / subdir).glob("*.html"))
for name in ["index.html", "about.html", "contact.html", "deal-radar.html",
             "shortlist.html", "newsletter.html", "404.html", "media-kit.html"]:
    p = SITE / name
    if p.exists():
        all_pages.append(p)

fixed = 0
for path in all_pages:
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
        if "saaspare-ui.css" in html:
            continue
        v2_tag = '<link rel="stylesheet" href="/assets/saaspare-v2.css">'
        shared_tag = '<link rel="stylesheet" href="/assets/sp-shared.css">'
        if v2_tag in html:
            html = html.replace(v2_tag, v2_tag + "\n  " + UI_TAG, 1)
        elif shared_tag in html:
            html = html.replace(shared_tag, shared_tag + "\n  " + UI_TAG, 1)
        else:
            html = html.replace("</head>", "  " + UI_TAG + "\n</head>", 1)
        path.write_text(html, encoding="utf-8")
        fixed += 1
    except Exception as e:
        print(f"  ERR {path.name}: {e}")

print(f"Fixed: {fixed} pages now link saaspare-ui.css")
