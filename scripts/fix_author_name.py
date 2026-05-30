"""
Fix author name: Smith Elly → Kaylan von Papen
Replaces all instances across site pages, schemas, author URLs, and initials.

Run: uv run python scripts/fix_author_name.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

REPLACEMENTS = [
    # Author name
    ("Smith Elly",          "Kaylan von Papen"),
    ("smith-elly",          "kaylan-von-papen"),
    # Initials in the author byline block
    ('"SE"',                '"KvP"'),
    (">SE<",                ">KvP<"),
    # Email (if any)
    ("smithelly30121@gmail.com", "hello@saaspare.org"),
]

updated = 0
total_replacements = 0

# Process all HTML files recursively under site/
for f in sorted(SITE.rglob("*.html")):
    try:
        original = f.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  SKIP (read error): {f.name} — {e}")
        continue

    html = original
    for old, new in REPLACEMENTS:
        html = html.replace(old, new)

    if html != original:
        f.write_text(html, encoding="utf-8")
        changes = sum(original.count(old) for old, _ in REPLACEMENTS)
        total_replacements += changes
        updated += 1

print(f"Files updated: {updated}")
print(f"Total replacements: {total_replacements}")
print()
print("Author is now: Kaylan von Papen")
print("Author slug:   kaylan-von-papen")
print("Initials:      KvP")
