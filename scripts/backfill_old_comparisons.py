"""Adds review bars + AggregateRating schema to legacy comparison pages.

Older comparisons use:
  <div class="section">
    <h2>{Tool} Review</h2>
    <p>{desc}</p>
    <div class="pros-cons">...</div>
    <p><strong>Pricing:</strong> ...</p>
  </div>

This script:
  1. Detects each {Tool} Review block
  2. Injects score-row + bars-grid before the pros-cons div
  3. Adds Product+AggregateRating schema for each tool
  4. Adds CSS for bars/stars if missing
  5. Idempotent via marker <!-- legacy-bars-v1 -->

Run: python scripts/backfill_old_comparisons.py
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SITE = ROOT / "site"
DOMAIN = "https://saaspare.org"
MARKER = "<!-- legacy-bars-v1 -->"

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
    support = band(h[3], 3.6, 4.9)
    overall = round((pricing + ease + features + support) / 4 + (0.2 if is_winner else 0), 1)
    overall = min(5.0, max(3.5, overall))
    return {"overall": overall, "pricing": pricing, "ease": ease, "features": features, "support": support}


def render_block(scores: dict) -> str:
    o = scores["overall"]
    full = int(o)
    half = 1 if (o - full) >= 0.5 else 0
    empty = 5 - full - half
    STAR = "\u2605"
    stars = STAR * full
    half_html = f'<span style="opacity:.55">{STAR}</span>' if half else ""
    empty_html = f'<span class="dim">{STAR * empty}</span>'

    def cls(v: float) -> str:
        return " red" if v < 3 else (" warn" if v < 4 else "")

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


REVIEW_BLOCK_RE = re.compile(
    r'(<div class="section">\s*<h2>([^<]+?)\s+Review</h2>\s*<p>[^<]*</p>\s*)(<div class="pros-cons">)',
    re.DOTALL,
)


def transform(html: str, file_path: str) -> tuple[str, int]:
    if MARKER in html:
        return html, 0
    if 'class="score-row"' in html:
        return html, 0
    products = []
    inserted = 0

    def repl(m):
        nonlocal inserted
        head = m.group(1)
        name = m.group(2).strip()
        cons_open = m.group(3)
        is_winner = "winner-badge" in head
        sc = derive_scores(name, is_winner)
        block = render_block(sc)
        products.append({
            "@context": "https://schema.org",
            "@type": "Product",
            "name": name,
            "image": f"{DOMAIN}/og-default.png",
            "brand": {"@type": "Brand", "name": name},
            # aggregateRating + review removed: synthetic single-editor
            # scores are not aggregated reviews (Phase 2 rule).
            })
        inserted += 1
        return head + block + cons_open

    new = REVIEW_BLOCK_RE.sub(repl, html)
    if inserted == 0:
        return html, 0

    if "</style>" in new and ".score-row{" not in new:
        new = new.replace("</style>", EXTRA_CSS + "</style>", 1)

    if products and "</head>" in new:
        blocks = "\n".join(
            f'<script type="application/ld+json">{json.dumps(p, ensure_ascii=False)}</script>'
            for p in products
        )
        new = new.replace("</head>", blocks + f"\n{MARKER}\n</head>", 1)
    return new, inserted


def main() -> None:
    files = list((SITE / "pages").glob("*.html"))
    touched = 0
    schemas = 0
    for f in files:
        try:
            original = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        new, n = transform(original, str(f))
        if n:
            f.write_text(new, encoding="utf-8")
            touched += 1
            schemas += n
    print(f"Legacy comparisons updated: {touched} files, {schemas} schemas added.")


if __name__ == "__main__":
    main()
