"""Remove personal operator details from public SaaSpare HTML surfaces.

The site should present organization-level trust signals publicly. Keep
individual identity out of generated schema and legal/contact copy unless a
human intentionally adds it later.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

REPLACEMENTS = {
    '<meta name="author" content="Kaylan von Papen">': '<meta name="author" content="SaaSpare Editorial Team">',
    '"author":{"@type":"Person","name":"Kaylan von Papen","url":"https://saaspare.org/about"}': '"author":{"@type":"Organization","name":"SaaSpare","url":"https://saaspare.org/about"}',
    "SaaSpare is operated by Kaylan von Papen, ABN 51 824 753 556, registered in Australia.": "SaaSpare is operated by SaaSpare in Australia.",
    "SaaSpare (“we”, “us”, “SaaSpare”) is operated by Kaylan von Papen, ABN 51 824 753 556, registered in Australia.": "SaaSpare (“we”, “us”, “SaaSpare”) is operated by SaaSpare in Australia.",
    "SaaSpare and Kaylan von Papen are not liable": "SaaSpare is not liable",
}


def main() -> None:
    changed: list[str] = []
    for path in [*SITE.glob("*.html"), *SITE.joinpath("pages").glob("*.html")]:
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in REPLACEMENTS.items():
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="")
            changed.append(str(path.relative_to(ROOT)).replace("\\", "/"))
    print(f"privacy_sanitized={len(changed)}")
    for item in changed[:40]:
        print(item)
    if len(changed) > 40:
        print(f"... and {len(changed) - 40} more")


if __name__ == "__main__":
    main()
