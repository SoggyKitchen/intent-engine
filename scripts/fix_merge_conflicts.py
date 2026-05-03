"""
fix_merge_conflicts.py
Resolve git merge conflict markers in site/pages/*.html by keeping the
"Updated upstream" (HEAD / ours) side and discarding the stashed side.
Idempotent — safe to re-run.
"""
import re
from pathlib import Path

SITE = Path(__file__).parent.parent / "site"
CONFLICT_RE = re.compile(
    r"<<<<<<< Updated upstream\n(.*?)=======\n.*?>>>>>>> Stashed changes\n",
    re.DOTALL,
)

fixed = 0
skipped = 0

for html in sorted(SITE.rglob("*.html")):
    text = html.read_text(encoding="utf-8", errors="replace")
    if "<<<<<<< Updated upstream" not in text:
        continue
    resolved = CONFLICT_RE.sub(r"\1", text)
    # Safety check — no markers left
    if "<<<<<<< " in resolved or "=======" in resolved or ">>>>>>> " in resolved:
        print(f"  WARN: could not fully resolve {html.name} — skipping")
        skipped += 1
        continue
    html.write_text(resolved, encoding="utf-8")
    print(f"  fixed: {html.relative_to(SITE)}")
    fixed += 1

print(f"\nDone. Fixed: {fixed}  Skipped (manual review needed): {skipped}")
