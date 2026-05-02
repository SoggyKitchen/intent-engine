"""Shared helpers used across all strategic page builders."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _page_shell import page_shell, hero_h1_with_glint, breadcrumb_html  # noqa

ROOT = Path(__file__).resolve().parent.parent.parent
PAGES = ROOT / "site" / "pages"
SITE = ROOT / "site"
PAGES.mkdir(parents=True, exist_ok=True)

CRUMB_HOME = ("/", "Home")


def star_row(score: float, label: str = "") -> str:
    full = int(score)
    half = 1 if (score - full) >= 0.5 else 0
    empty = 5 - full - half
    lit = "★" * full + ("⯪" if half else "")
    dim = "★" * empty
    label_html = f"<span>{label}</span>" if label else ""
    return (
        f'<div class="rate-row">'
        f'<span class="stars">{lit}</span>'
        f'<span class="stars dim">{dim}</span>'
        f'<span><strong>{score:.1f}</strong> / 5</span>'
        f'{label_html}</div>'
    )


def bar(label: str, score: float, color: str = "green") -> str:
    pct = min(100, max(0, int(score * 20)))
    cls = "" if color == "green" else color
    return (
        f'<div class="bar-line">'
        f'<div class="bar-label"><span>{label}</span><strong>{score:.1f}</strong></div>'
        f'<div class="bar-track"><div class="bar-fill {cls}" style="--w:{pct}%"></div></div>'
        f'</div>'
    )


def write_page(slug: str, html: str, target_dir: Path = PAGES, filename: str = None) -> None:
    name = filename or f"{slug}.html"
    (target_dir / name).write_text(html, encoding="utf-8")
