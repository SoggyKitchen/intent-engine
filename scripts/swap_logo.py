import re, pathlib, sys

ROOT = pathlib.Path(__file__).parent.parent

# ── NEW logo SVG mark (two-part S) ──────────────────────────────────────────
MARK_SVG = (
    '<svg class="logo-mark" viewBox="0 0 36 44" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<path class="mark-top" d="M4,0 H22 Q26,0 26,4 V12 L12,21 H4 Q0,21 0,17 V4 Q0,0 4,0 Z" fill="#fff"/>'
    '<path class="mark-bot" d="M14,23 H30 Q34,23 34,27 V40 Q34,44 30,44 H12 Q8,44 8,40 V31 L14,23 Z" fill="#e94560"/>'
    '</svg>'
)
LOGO_TEXT = '<span class="logo-text">Saa<em>Spare</em></span>'

# ── NEW CSS block ────────────────────────────────────────────────────────────
NEW_CSS = (
    ".logo-mark{height:22px;width:auto;flex-shrink:0;overflow:visible}"
    ".mark-top,.mark-bot{transition:transform .35s cubic-bezier(.34,1.4,.64,1)}"
    "@keyframes markDrift{0%,100%{transform:translate(0,0)}40%{transform:translate(-.8px,-.8px)}70%{transform:translate(.35px,.35px)}}"
    "@keyframes markDriftBot{0%,100%{transform:translate(0,0)}40%{transform:translate(.8px,.8px)}70%{transform:translate(-.35px,-.35px)}}"
    ".mark-top{animation:markDrift 5s ease-in-out infinite}"
    ".mark-bot{animation:markDriftBot 5s ease-in-out infinite}"
    ".logo:hover .mark-top{animation:none;transform:translate(-2.5px,-2.5px)}"
    ".logo:hover .mark-bot{animation:none;transform:translate(2.5px,2.5px)}"
    ".logo:hover .logo-mark{filter:drop-shadow(0 0 12px rgba(233,69,96,.6))}"
)

# ── Patterns to remove from CSS ──────────────────────────────────────────────
CSS_PATTERNS = [
    r"@keyframes barIdle\{[^}]+\}",
    r"\.logo-bars\{[^}]+\}",
    r"\.logo-bars span\{[^}]+\}",
    r"\.logo-bars span:nth-child\(1\)\{[^}]+\}",
    r"\.logo-bars span:nth-child\(2\)\{[^}]+\}",
    r"\.logo-bars span:nth-child\(3\)\{[^}]+\}",
    r"\.logo:hover \.logo-bars span\{[^}]+\}",
    r"\.logo:hover \.logo-bars span:nth-child\(1\)\{[^}]+\}",
    r"\.logo:hover \.logo-bars span:nth-child\(2\)\{[^}]+\}",
    r"\.logo:hover \.logo-bars span:nth-child\(3\)\{[^}]+\}",
]

# ── HTML: logo-bars div block ────────────────────────────────────────────────
BARS_HTML_RE = re.compile(
    r'<div class="logo-bars">\s*<span></span>\s*<span></span>\s*<span></span>\s*</div>',
    re.DOTALL
)
# logo-text div → span
LOGOTEXT_DIV_RE = re.compile(
    r'<div class="logo-text">(Saa<em>Spare</em>|Saa<em>S</em>pare|SaaSpare)</div>'
)


def process_file(path: pathlib.Path) -> bool:
    original = path.read_text(encoding="utf-8")
    text = original

    # 1. Remove old CSS rules
    for pat in CSS_PATTERNS:
        text = re.sub(pat, "", text)

    # 2. Inject new CSS right before </style> (first occurrence only)
    if ".logo-mark" not in text:
        text = text.replace("</style>", NEW_CSS + "\n</style>", 1)

    # 3. Replace logo-bars HTML with SVG mark
    text = BARS_HTML_RE.sub(MARK_SVG, text)

    # 4. Replace logo-text div with span
    text = LOGOTEXT_DIV_RE.sub(LOGO_TEXT, text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"  ✓ {path.relative_to(ROOT)}")
        return True
    else:
        print(f"  – {path.relative_to(ROOT)}  (no change)")
        return False


targets = [
    ROOT / "site/index.html",
    ROOT / "site/about.html",
    ROOT / "site/contact.html",
    ROOT / "site/privacy.html",
    ROOT / "site/media-kit.html",
    ROOT / "site/pages/index.html",
    ROOT / "site/pages/saas-roi-calculator.html",
    ROOT / "outputs/templates/comparison_page.html.j2",
]

print("Swapping logo across all pages...")
changed = sum(process_file(p) for p in targets)
print(f"\nDone — {changed}/{len(targets)} files updated.")
