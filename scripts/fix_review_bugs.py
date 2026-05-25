"""
Fix the two real bugs found by ultrareview:

1. Stale <meta name="keywords"> — vs-pages had titles rewritten but keywords
   tag still contains the old long-form title. Fix: strip the title fragment
   from keywords, keep only the generic terms.

2. Author URL /authors/smith-elly now has a backing page — no code change
   needed, but verify it exists.

Run: uv run python scripts/fix_review_bugs.py
"""
import re
from pathlib import Path

ROOT  = Path(__file__).resolve().parents[1]
SITE  = ROOT / "site"
PAGES = SITE / "pages"

# ── Fix 1: Stale meta keywords ─────────────────────────────────────────────
# Pattern: <meta name="keywords" content="OLD TITLE, comparison, ..." />
# We want to keep only the generic terms after the first comma-title fragment.
# The stale title fragments are things like:
#   "1Password vs. Bitwarden in 2026: Which Password Manager Is Best?"
#   "HubSpot vs. Salesforce in 2026: Which Software Is Best?"
# Strategy: replace the keyword content with a clean version that strips
# any fragment ending with "?" and keeps only the trailing generic keywords.

KEYWORDS_PAT = re.compile(
    r'(<meta\s+name=["\']keywords["\']\s+content=["\'])([^"\']+)(["\'])',
    re.IGNORECASE
)

GENERIC_FALLBACK = "comparison, SaaS pricing, software comparison, free trial, alternatives, SaaSpare"

def clean_keywords(content: str) -> str:
    """Strip title-like fragments from keywords meta content."""
    parts = [p.strip() for p in content.split(",")]
    # Keep parts that don't look like a title (no colon-question mark pattern)
    clean = [p for p in parts if not ("?" in p or (":" in p and len(p) > 30))]
    # If we stripped everything, use fallback
    if not clean:
        return GENERIC_FALLBACK
    # Always ensure the generic terms are present
    generic = {"comparison", "saas pricing", "software comparison", "free trial", "alternatives", "saaspare"}
    existing_lower = {p.lower() for p in clean}
    for term in ["comparison", "SaaS pricing", "software comparison", "free trial", "alternatives", "SaaSpare"]:
        if term.lower() not in existing_lower:
            clean.append(term)
    return ", ".join(clean)


def fix_stale_keywords():
    fixed = 0
    for p in sorted(PAGES.glob("*.html")):
        try:
            html = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        def replacer(m):
            old_content = m.group(2)
            new_content = clean_keywords(old_content)
            if new_content == old_content:
                return m.group(0)
            return m.group(1) + new_content + m.group(3)

        new_html = KEYWORDS_PAT.sub(replacer, html)
        if new_html != html:
            p.write_text(new_html, encoding="utf-8")
            fixed += 1

    print(f"Keywords cleaned: {fixed} pages")
    return fixed


# ── Fix 2: Verify author page exists ──────────────────────────────────────

def verify_author_page():
    author_page = SITE / "authors" / "smith-elly.html"
    if author_page.exists():
        print(f"Author page OK: {author_page.relative_to(ROOT)}")
        return True
    else:
        print(f"MISSING: {author_page}")
        return False


# ── main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Fix 1: Stale meta keywords ===")
    fix_stale_keywords()

    print("\n=== Fix 2: Author page ===")
    verify_author_page()

    print("\nDone. Run: uv run pytest --tb=short -q")
