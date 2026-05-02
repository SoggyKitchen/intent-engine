"""Fix UTF-8 mojibake (cp1252 misread) across source + site files.

Idempotent: only replaces known bad sequences with correct unicode chars.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REPLACEMENTS = [
    ("\u00e2\u20ac\u201d", "\u2014"),
    ("\u00e2\u20ac\u201c", "\u2013"),
    ("\u00e2\u20ac\u2122", "\u2019"),
    ("\u00e2\u20ac\u02dc", "\u2018"),
    ("\u00e2\u20ac\u0153", "\u201c"),
    ("\u00e2\u20ac\u009d", "\u201d"),
    ("\u00e2\u20ac\u00a6", "\u2026"),
    ("\u00e2\u20ac\u00a2", "\u2022"),
    ("\u00c2\u00b7", "\u00b7"),
    ("\u00c2\u00ad", "\u00ad"),
    ("\u00c2\u00a0", "\u00a0"),
    ("\u00c2\u00ae", "\u00ae"),
    ("\u00c2\u00a9", "\u00a9"),
    ("\u00c2\u00b0", "\u00b0"),
    ("\u00c2\u00bd", "\u00bd"),
    ("\u00c3\u00a9", "\u00e9"),
    ("\u00c3\u00a8", "\u00e8"),
    ("\u00c3\u00aa", "\u00ea"),
    ("\u00c3\u00a0", "\u00e0"),
    ("\u00c3\u00a7", "\u00e7"),
    ("\u00c3\u00b6", "\u00f6"),
    ("\u00c3\u00bc", "\u00fc"),
    ("\u00c3\u00b1", "\u00f1"),
    ("\u00c3\u00b8", "\u00f8"),
    ("\u00c3\u00b3", "\u00f3"),
    ("\u00c3\u2014", "\u00d7"),
    ("\u00c3\u00b7", "\u00f7"),
    ("\u00e2\u2020\u2019", "\u2192"),
    ("\u00e2\u2020\u0090", "\u2190"),
    ("\u00e2\u2020\u2018", "\u2191"),
    ("\u00e2\u2020\u201c", "\u2193"),
    ("\u00e2\u2020\u2014", "\u2197"),
    ("\u00e2\u2020\u2122", "\u2199"),
    ("\u00e2\u02dc\u2026", "\u2605"),
    ("\u00e2\u02dc\u2020", "\u2606"),
    ("\u00e2\u0153\u201c", "\u2713"),
    ("\u00e2\u0153\u2014", "\u2717"),
    ("\u00e2\u20ac\u00b9", "\u2039"),
    ("\u00e2\u20ac\u00ba", "\u203a"),
    ("\u00e2\u20ac\u02dc", "\u2018"),
]

TARGET_DIRS = [
    (ROOT / "scripts", ("*.py",)),
    (ROOT / "outputs", ("*.py", "*.j2", "*.html")),
    (ROOT / "site", ("*.html", "*.txt", "*.xml", "*.json")),
]


def fix_text(text: str) -> tuple[str, int]:
    n = 0
    for bad, good in REPLACEMENTS:
        if bad in text:
            n += text.count(bad)
            text = text.replace(bad, good)
    return text, n


def main() -> None:
    total_files = 0
    total_replacements = 0
    for base, patterns in TARGET_DIRS:
        if not base.exists():
            continue
        for pat in patterns:
            for path in base.rglob(pat):
                if path.is_file() and "node_modules" not in path.parts and ".git" not in path.parts:
                    try:
                        original = path.read_text(encoding="utf-8")
                    except (UnicodeDecodeError, PermissionError):
                        continue
                    fixed, n = fix_text(original)
                    if n:
                        path.write_text(fixed, encoding="utf-8")
                        total_files += 1
                        total_replacements += n
                        print(f"{n:4d}  {path.relative_to(ROOT)}")
    print(f"\nFixed {total_replacements} mojibake instances across {total_files} files.")


if __name__ == "__main__":
    main()
