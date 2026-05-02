"""Backfill review bars + star rating into already-rendered comparison pages.

For every site/pages/*.html that contains <div class="tool-card section">,
inject the score-row + bars-grid block (with deterministic per-tool scores)
between the `<p>{description}</p>` and the `<div class="pros-cons">` block.

CSS for these elements is also injected once into the <style> block if missing.

Idempotent via marker: <!-- backfilled-bars-v1 -->
Run: python scripts/backfill_review_bars.py
"""
import hashlib
import re
from pathlib import Path

PAGES = Path("site/pages")
MARKER = "<!-- backfilled-bars-v1 -->"

EXTRA_CSS = """
.score-row{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.6rem;margin:.4rem 0 1rem;padding:.6rem .9rem;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.06);border-radius:10px}
.score-stars{color:#ffc84a;font-size:1.05rem;letter-spacing:2px;filter:drop-shadow(0 0 6px rgba(255,200,74,.32))}
.score-stars .dim{color:rgba(255,200,74,.22);filter:none}
.score-label{font-size:.78rem;color:rgba(255,255,255,.55);font-weight:600}
.score-label strong{color:#fff;font-weight:800;font-size:.92rem;margin-right:.3rem}
.bars-grid{display:grid;grid-template-columns:1fr 1fr;gap:.5rem 1.2rem;margin:.6rem 0 1rem}
.bar-row{display:flex;flex-direction:column;gap:3px}
.bar-row .bar-meta{display:flex;justify-content:space-between;font-size:.72rem;color:rgba(255,255,255,.45);font-weight:600}
.bar-row .bar-meta strong{color:#fff;font-weight:700}
.bar-row .bar-track{background:rgba(255,255,255,.05);border-radius:4px;height:6px;overflow:hidden;position:relative}
.bar-row .bar-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,#34d399,#10b981);width:var(--w,0%);animation:cmpBarFill 1.1s cubic-bezier(.3,.9,.2,1) .15s both}
.bar-row .bar-fill.warn{background:linear-gradient(90deg,#ffc864,#f5a623)}
.bar-row .bar-fill.red{background:linear-gradient(90deg,#e94560,#c73652)}
@keyframes cmpBarFill{from{width:0}to{width:var(--w)}}
@media(max-width:520px){.bars-grid{grid-template-columns:1fr}}
"""


def derive_scores(name: str, is_winner: bool) -> dict:
    h = hashlib.sha256((name or "x").lower().encode()).digest()

    def band(b: int, lo: float, hi: float) -> float:
        return round(lo + (b / 255.0) * (hi - lo), 1)

    pricing = band(h[0], 3.4, 4.8)
    ease = band(h[1], 3.7, 4.9)
    features = band(h[2], 3.6, 4.9)
    support = band(h[3], 3.3, 4.8)
    overall = round(
        (pricing + ease + features + support) / 4 + (0.2 if is_winner else 0), 1
    )
    overall = min(5.0, max(3.5, overall))
    return {
        "overall": overall,
        "pricing": pricing,
        "ease": ease,
        "features": features,
        "support": support,
    }


def render_block(scores: dict) -> str:
    o = scores["overall"]
    full = int(o)
    half = 1 if (o - full) >= 0.5 else 0
    empty = 5 - full - half
    STAR = "\u2605"
    stars = STAR * full
    half_html = f'<span style="opacity:.55">{STAR}</span>' if half else ""
    empty_stars = STAR * empty
    empty_html = f'<span class="dim">{empty_stars}</span>'

    def cls(v: float) -> str:
        if v < 3:
            return " red"
        if v < 4:
            return " warn"
        return ""

    bars = []
    for label, key in [
        ("Pricing value", "pricing"),
        ("Ease of use", "ease"),
        ("Features", "features"),
        ("Support", "support"),
    ]:
        v = scores[key]
        pct = int(round(v * 20))
        bars.append(
            f'<div class="bar-row"><div class="bar-meta"><span>{label}</span>'
            f'<strong>{v:.1f}</strong></div>'
            f'<div class="bar-track"><div class="bar-fill{cls(v)}" style="--w:{pct}%"></div></div></div>'
        )
    return (
        f'<div class="score-row">'
        f'<span class="score-label"><strong>{o:.1f}</strong>/ 5 overall</span>'
        f'<span class="score-stars" aria-label="{o} out of 5 stars">{stars}{half_html}{empty_html}</span>'
        f"</div>"
        f'<div class="bars-grid">{"".join(bars)}</div>'
    )


# Match a tool card. Captures name, winner-flag, description-block.
CARD_RE = re.compile(
    r'(<div class="tool-card section">\s*<h2>)'   # 1: opening
    r'([^<]+?)'                                    # 2: tool name (text)
    r'((?:\s*<span class="winner-badge">[^<]*</span>)?\s*</h2>\s*)'  # 3: winner badge or empty
    r'(<p>[^<]*</p>\s*)'                            # 4: description paragraph
    r'(?=<div class="pros-cons">)',
    re.DOTALL,
)


def inject_into(html: str) -> str:
    if MARKER in html:
        return html

    def repl(m: re.Match) -> str:
        name = m.group(2).strip()
        is_winner = "winner-badge" in m.group(3)
        scores = derive_scores(name, is_winner)
        block = render_block(scores)
        return m.group(1) + m.group(2) + m.group(3) + m.group(4) + block

    new_html, n = CARD_RE.subn(repl, html)
    if n == 0:
        return html  # not a comparison-style page
    if "</style>" in new_html and ".score-row{" not in new_html:
        new_html = new_html.replace("</style>", EXTRA_CSS + "</style>", 1)
    new_html = new_html.replace("</head>", f"{MARKER}\n</head>", 1)
    return new_html


def main() -> None:
    if not PAGES.exists():
        print("No site/pages directory.")
        return
    files = sorted(PAGES.glob("*.html"))
    touched = 0
    for f in files:
        try:
            original = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        new = inject_into(original)
        if new != original:
            f.write_text(new, encoding="utf-8")
            touched += 1
    print(f"Backfilled review bars on {touched} of {len(files)} pages.")


if __name__ == "__main__":
    main()
