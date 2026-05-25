"""Inspect broken JSON-LD blocks."""
from pathlib import Path
import re, json

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

pat = re.compile(
    r'type="application/ld\+json"[^>]*>([\s\S]*?)</script>',
    re.IGNORECASE
)

bad = []
for p in sorted(SITE.glob("**/*.html")):
    try:
        raw = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    for i, m in enumerate(pat.finditer(raw)):
        pl = m.group(1).strip()
        if not pl:
            continue
        try:
            json.loads(pl)
        except json.JSONDecodeError as e:
            bad.append((p, i, pl, e))

print(f"Total bad blocks: {len(bad)}\n")
# Show first 3 in detail
for p, idx, pl, e in bad[:5]:
    print(f"FILE: {p.name}, block {idx}")
    print(f"  Error: {e}")
    lines = pl.splitlines()
    for li, line in enumerate(lines[max(0, e.lineno-3):e.lineno+2], start=max(1, e.lineno-2)):
        marker = " >>>" if li == e.lineno else "    "
        print(f"  {marker} L{li}: {line}")
    print()

# Just list all files
print("All affected files:")
seen = set()
for p, _, _, _ in bad:
    if p not in seen:
        print(f"  {p.relative_to(ROOT)}")
        seen.add(p)
