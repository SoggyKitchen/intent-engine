"""
Normalise the inconsistent per-page "how we evaluated" paragraphs that the
AI generator shipped (e.g. "we tested for 10 hours", "over 40+ hours",
"consulted with 12 IT leaders", "surveyed 120+ teams", "1,200+ data
points"). Those claims are not uniformly verifiable and they are flagged
as an E-E-A-T risk in the external audit.

Strategy: where we detect one of these machine-generated methodology
paragraphs, replace it with a single, honest, consistent paragraph
that maps to the canonical /methodology page and does not claim
unverifiable testing hours or consultant counts.

Idempotent: running again on an already-normalised page is a no-op.
"""
from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = ROOT / "outputs" / "seo" / "methodology-normalisation.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

CANONICAL_METHODOLOGY_PARAGRAPH = (
    "SaaSpare evaluated both tools using a consistent four-part process: "
    "we read the vendors&#x27; public pricing pages and plan documentation, "
    "checked free-trial and refund terms on the vendor&#x27;s own site, "
    "reviewed third-party user reviews on G2, Capterra and TrustRadius for "
    "recurring themes, and tested any publicly available trial where access "
    "did not require a sales call. We do not claim hands-on usage of every "
    "paid tier \u2014 where a plan is only available via sales call we mark "
    "the fact explicitly. See our <a href=\"/methodology\">full "
    "methodology</a> for the rubric we use across every comparison."
)

# Heuristic: find an <p> tag that starts a methodology paragraph. We match
# the most common opening phrases used by the generator, then look inside
# the same <p> for one of the unverifiable claim markers.
METHODOLOGY_P_RE = re.compile(
    r"<p([^>]*)>\s*"  # 1 = attrs
    r"(?:We evaluated|We tested|SaaSpare evaluated|SaaSpare tested|"
    r"We compared|SaaSpare compared)\s+"
    r"[^<]{0,600}?"  # body up to marker (same <p>, no nested tags)
    r"(?:\d+\+?\s+hours|\d{2,4}\+?\s+data points|consulted with \d+|"
    r"surveyed \d+|for \d+ hours|tested both tools|tested both platforms)"
    r"[^<]{0,1200}?"
    r"</p>",
    re.IGNORECASE,
)


def process_file(path: Path) -> dict | None:
    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        original = path.read_text(encoding="utf-8", errors="replace")

    if "saaspare-normalised-methodology" in original:
        return None  # already processed

    m = METHODOLOGY_P_RE.search(original)
    if not m:
        return None

    replacement = (
        f"<p{m.group(1)} data-saaspare-normalised-methodology=\"v1\">"
        f"{CANONICAL_METHODOLOGY_PARAGRAPH}"
        f"</p>"
    )
    new_html = METHODOLOGY_P_RE.sub(replacement, original, count=1)
    if new_html == original:
        return None
    path.write_text(new_html, encoding="utf-8", newline="")
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "matched_snippet": m.group(0)[:200],
    }


def main() -> None:
    changed: list[dict] = []
    pages = list((SITE / "pages").glob("*.html"))
    for page in pages:
        result = process_file(page)
        if result is not None:
            changed.append(result)
    report = {
        "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "pages_scanned": len(pages),
        "pages_changed": len(changed),
        "changes": changed,
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"scanned={len(pages)} normalised={len(changed)} "
        f"report={OUT.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
