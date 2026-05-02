"""Inject /assets/saaspare-events.js into every HTML page (idempotent via marker)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
MARKER = "<!-- ga-events-v1 -->"
TAG = f'{MARKER}<script defer src="/assets/saaspare-events.js"></script>'

changed = 0
for p in SITE.rglob("*.html"):
    try:
        html = p.read_text(encoding="utf-8")
    except Exception:
        continue
    if MARKER in html:
        continue
    if "</head>" not in html:
        continue
    html = html.replace("</head>", TAG + "\n</head>", 1)
    p.write_text(html, encoding="utf-8")
    changed += 1
print(f"Injected GA events script into {changed} pages.")
