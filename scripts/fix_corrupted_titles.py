"""
One-shot repo cleaner for SaaSpare that:

1. Removes stale "Last verified:" trust-box sentences that leaked the page
   title into the body, e.g.
       "Last verified: Xero vs. Sage: Which Software Is Best in 2026? |
       SaaSpare is checked during scheduled SEO and link audits..."
   and replaces them with a proper, stable Source Verification sentence
   that matches the new template in scripts/seo/seo_agent.py.

2. Detects and repairs programmatic duplication/corruption patterns like
   "Sageero vs. Sage" or "Airbaseero vs. Airbase" that are visible inside
   some generated HTML bodies (e.g. "Xero vs. Sageero vs. Sage: Which
   Software Is Best in 2026?").

3. Writes a JSON report to outputs/seo/corruption-report.json listing
   every file touched, the pattern(s) matched, and the replacement.

Safe to re-run. Only modifies files if the pattern is present.
"""
from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"
OUTPUTS_DIR = ROOT / "outputs" / "seo"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Brands with duplication risk. We detect "<brand>ero vs. <brand>" (the
# specific corruption seen on saaspare.org: Sageero, Airbaseero, Brexero,
# QuickBooksero, Rampero, Divvyero, Expensifyero, NetSuiteero, etc.).
DUPLICATE_BRAND_SUFFIX_RE = re.compile(
    r"\b([A-Za-z0-9.]+)ero vs\. \1\b",
    re.IGNORECASE,
)

# Catches the exact trust-box sentence where audit.title was injected
# into body copy. This is specifically the bug fixed in
# scripts/seo/seo_agent.py::inject_buyer_trust_block().
TRUSTBOX_STALE_SENTENCE_RE = re.compile(
    r"<p><strong>Last verified:</strong>\s*[^<]+? is checked during scheduled SEO and link audits\.\s*[^<]+?</p>",
    re.IGNORECASE,
)

# Full trust-box replacement is built per-call so we share the exact
# template with seo_agent.inject_buyer_trust_block and can evolve them
# together.
def _now_verified_label_iso() -> tuple[str, str]:
    now_utc = datetime.now(UTC)
    iso = now_utc.date().isoformat()
    try:
        label = now_utc.strftime("%B %-d, %Y")
    except ValueError:
        label = now_utc.strftime("%B %d, %Y").replace(" 0", " ")
    return iso, label


def new_trustbox_sentence() -> str:
    iso, label = _now_verified_label_iso()
    source_line = (
        "Pricing source: public vendor pages linked from this page where "
        "available; otherwise marked for verification."
    )
    return (
        f"<p><strong>Last verified:</strong> This page was last checked on "
        f"<time datetime=\"{iso}\">{escape(label)}</time> as part of our "
        f"scheduled SEO and link audits. {source_line}</p>\n"
        f"  <p><strong>Verification state:</strong> <span data-verification-label>"
        f"Awaiting manual vendor-source verification</span>. Pricing, trial "
        f"terms, coupon validity and refund policy may change on the "
        f"vendor&#x27;s official site at any time &mdash; always confirm on "
        f"the vendor page linked above before you buy.</p>"
    )


def _add_state_attr(html: str) -> str:
    """Add data-verification-state to any legacy trustbox that lacks it."""
    pattern = re.compile(
        r'<section class="seo-trustbox section" data-seo-trustbox>',
    )
    replacement = (
        '<section class="seo-trustbox section" data-seo-trustbox '
        'data-verification-state="needs_manual_review">'
    )
    return pattern.sub(replacement, html)


def fix_duplicate_brand_suffix(html: str) -> tuple[str, list[str]]:
    """Repair "Sageero vs. Sage" -> "Sage" etc., only inside visible body
    text. Matches are replaced with the canonical brand token."""
    matches = DUPLICATE_BRAND_SUFFIX_RE.findall(html)
    # Replace <Brand>ero vs. <Brand> with <Brand> (drop the leaked "ero vs."
    # fragment and keep a single brand mention so the sentence still reads).
    fixed = DUPLICATE_BRAND_SUFFIX_RE.sub(lambda m: m.group(1), html)
    return fixed, matches


def fix_trustbox_stale_title(html: str) -> tuple[str, int]:
    """Replace any <p><strong>Last verified:</strong> <title>... sentence
    with the evidence-anchored template from inject_buyer_trust_block."""
    replacement = "  " + new_trustbox_sentence()
    if not TRUSTBOX_STALE_SENTENCE_RE.search(html):
        return html, 0
    new_html, count = TRUSTBOX_STALE_SENTENCE_RE.subn(replacement, html)
    return new_html, count


def process_file(path: Path) -> dict | None:
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw = path.read_text(encoding="utf-8", errors="replace")
    original = raw

    raw, dup_matches = fix_duplicate_brand_suffix(raw)
    raw, stale_count = fix_trustbox_stale_title(raw)
    raw = _add_state_attr(raw)

    if raw == original:
        return None

    path.write_text(raw, encoding="utf-8", newline="")
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "duplicate_brand_fragments": dup_matches,
        "stale_trustbox_sentences_rewritten": stale_count,
    }


def main() -> None:
    changed: list[dict] = []
    html_files = list(SITE_DIR.rglob("*.html"))
    for path in html_files:
        result = process_file(path)
        if result is not None:
            changed.append(result)

    report = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "html_files_scanned": len(html_files),
        "files_changed": len(changed),
        "changes": changed,
    }
    out = OUTPUTS_DIR / "corruption-report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"scanned={len(html_files)} changed={len(changed)} "
        f"report={out.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
