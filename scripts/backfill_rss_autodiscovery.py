"""Add <link rel="alternate" type="application/rss+xml"> autodiscovery to all pages."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
MARKER = "<!-- rss-autodiscovery -->"
TAG = f'{MARKER}<link rel="alternate" type="application/rss+xml" title="SaaSpare" href="/feed.xml">'

n = 0
for p in SITE.rglob("*.html"):
    try:
        html = p.read_text(encoding="utf-8")
    except Exception:
        continue
    if MARKER in html or "</head>" not in html:
        continue
    html = html.replace("</head>", TAG + "\n</head>", 1)
    p.write_text(html, encoding="utf-8")
    n += 1
print(f"added RSS autodiscovery to {n} pages")
