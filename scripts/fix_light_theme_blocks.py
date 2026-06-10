"""Convert light-theme inline blocks to dark-theme equivalents site-wide.

Several legacy generators (build_categories, build_round2_pages, fix_ctr_opportunities,
fix_internal_linking, ...) inject asides/alerts with light backgrounds (#fff7ed,
#f1f5f9, #fef2f2, ...) that render as broken white pillars on the dark site theme.
This post-processor rewrites those inline styles to translucent dark equivalents
and lightens the dark text colors used inside them.

Run after any bulk generation; wired into nightly site integrity.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# Light background -> translucent dark equivalent (keeps the accent hue)
BG_MAP = {
    "background:#fff7ed": "background:rgba(234,88,12,.12)",   # orange-50
    "background:#fef3c7": "background:rgba(245,158,11,.12)",  # amber-100
    "background:#fffbeb": "background:rgba(245,158,11,.10)",  # amber-50
    "background:#fefce8": "background:rgba(250,204,21,.10)",  # yellow-50
    "background:#fef2f2": "background:rgba(220,38,38,.12)",   # red-50
    "background:#f0fdf4": "background:rgba(34,197,94,.10)",   # green-50
    "background:#eff6ff": "background:rgba(59,130,246,.10)",  # blue-50
    "background:#f1f5f9": "background:rgba(255,255,255,.06)", # slate-100
    "background:#f8fafc": "background:rgba(255,255,255,.05)", # slate-50
    "background:#f9fafb": "background:rgba(255,255,255,.05)", # gray-50
}

# Dark accent text colors (designed for light backgrounds) -> light equivalents
COLOR_MAP = {
    "color:#9a3412": "color:#fdba74",  # orange-800 -> orange-300
    "color:#7c2d12": "color:#fdba74",  # orange-900
    "color:#991b1b": "color:#fca5a5",  # red-800 -> red-300
    "color:#7f1d1d": "color:#fca5a5",  # red-900
    "color:#92400e": "color:#fcd34d",  # amber-800 -> amber-300
    "color:#14532d": "color:#86efac",  # green-900 -> green-300
    "color:#166534": "color:#86efac",  # green-800
    "color:#1e3a8a": "color:#93c5fd",  # blue-900 -> blue-300
    "color:#1e40af": "color:#93c5fd",  # blue-800
}

SKIP_PREFIXES = ("v3-preview",)  # standalone light-theme previews


def fix_file(p: Path) -> bool:
    html = p.read_text(encoding="utf-8")
    if "background:#050407" not in html:
        return False  # not a dark-theme page
    out = html
    for old, new in {**BG_MAP, **COLOR_MAP}.items():
        out = out.replace(old, new)
    if out != html:
        p.write_text(out, encoding="utf-8")
        return True
    return False


def main():
    fixed = 0
    for p in SITE.rglob("*.html"):
        if p.name.startswith(SKIP_PREFIXES):
            continue
        if fix_file(p):
            fixed += 1
    print(f"fix_light_theme_blocks: {fixed} pages converted to dark-theme blocks")


if __name__ == "__main__":
    main()
