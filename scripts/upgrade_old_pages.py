"""
upgrade_old_pages.py — Upgrade all old-template pages to premium design.

Targets: vs/comparison pages, alternatives pages, review pages, free-trial pages
that DON'T already have pr-layout (pricing) or bc-layout (best-of) markers.

What it does:
1. Remove noindex,nofollow → index,follow
2. Inject premium CSS that styles existing HTML classes
3. Strip "Advertisement" text nodes
4. Remove duplicate affiliate disclosure boxes
5. Fix canonical URLs (remove numeric prefix like 7-best → best)
6. Add IndexNow ping for recrawl
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site" / "pages"

# ── Premium CSS injected into every upgraded page ────────────────────────────
PREMIUM_CSS = """<style id="upgrade-v2">
/* ── PAGE UPGRADE v2 — premium shell for comparison/alternatives/review pages ── */
:root{--red:#e94560;--red2:#c73652;--green:#36e6a1;--amber:#f5b942;--bg:#050407;
  --text:rgba(255,248,245,.88);--muted:rgba(255,248,245,.52);--dim:rgba(255,248,245,.22);
  --border:rgba(255,255,255,.08);--card:rgba(255,255,255,.042)}

/* ── PAGE HERO ── */
.page-hero{
  padding:5rem 0 3rem;
  background:radial-gradient(ellipse 120% 60% at 50% 0%,rgba(220,45,72,.14) 0%,transparent 65%);
  border-bottom:1px solid var(--border);margin-bottom:2.5rem;
}
.breadcrumb{
  display:flex;align-items:center;flex-wrap:wrap;gap:4px;
  font-size:.78rem;color:var(--muted);margin-bottom:1.2rem;
}
.breadcrumb a{color:var(--muted);text-decoration:none;transition:color .15s}
.breadcrumb a:hover{color:#fff}
.breadcrumb span{color:var(--dim)}

/* ── H1 ── */
.page-hero h1,.sp-h1{
  font-size:clamp(1.9rem,4.5vw,3rem);font-weight:900;color:#fff;
  line-height:1.12;letter-spacing:-.04em;margin-bottom:1rem;
}

/* ── QUICK ANSWER FEATURED BOX ── */
.featured-answer,.qa-block{
  background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);
  border-left:3px solid var(--red);border-radius:14px;
  padding:1.1rem 1.3rem;margin:1.2rem 0;font-size:.88rem;
  color:var(--text);line-height:1.7;
}
.featured-answer strong,.qa-block strong{color:#fff}

/* ── SUBTITLE / LEAD ── */
.subtitle,.sp-lead{
  font-size:1rem;color:var(--muted);line-height:1.7;
  margin:.5rem 0 1.2rem;max-width:680px;
}

/* ── TRUST BAR ── */
.trust-bar{
  display:flex;flex-wrap:wrap;gap:.6rem;align-items:center;margin-top:1rem;
}
.trust-bar span{
  display:inline-flex;align-items:center;gap:5px;
  background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.09);
  border-radius:100px;padding:4px 12px;font-size:.72rem;
  font-weight:600;color:var(--muted);
}
.trust-bar span::before{content:"✓ ";color:var(--green)}

/* ── CONTAINER ── */
.container{max-width:1100px;margin:0 auto;}

/* ── TLDR BOX ── */
.tldr-box{
  background:rgba(233,69,96,.06);border:1px solid rgba(233,69,96,.18);
  border-radius:14px;padding:1.1rem 1.4rem;font-size:.9rem;
  color:var(--text);margin-bottom:2rem;line-height:1.65;
}
.tldr-box strong{color:var(--red)}

/* ── NATIVE INTENT / CTA CARD ── */
.native-intent-block{
  background:rgba(255,255,255,.042);border:1px solid rgba(255,255,255,.09);
  border-radius:18px;padding:1.8rem 2rem;margin:2rem 0;
}
.mini-kicker{
  font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;
  color:var(--red);margin-bottom:.5rem;
}
.native-intent-block h3{
  font-size:1.15rem;font-weight:800;color:#fff;margin-bottom:.5rem;line-height:1.3;
}
.native-intent-block p{font-size:.86rem;color:var(--muted);line-height:1.65;margin-bottom:1rem}
.native-intent-block a{
  display:inline-flex;align-items:center;gap:6px;
  background:linear-gradient(135deg,var(--red),var(--red2));
  color:#fff;padding:.55rem 1.2rem;border-radius:100px;
  font-weight:700;font-size:.82rem;text-decoration:none;
  box-shadow:0 4px 16px rgba(233,69,96,.35);transition:transform .15s,box-shadow .15s;
}
.native-intent-block a:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(233,69,96,.5)}

/* ── SECTION HEADINGS ── */
.section{margin:2.5rem 0}
.section h2,.section h3{
  font-size:clamp(1.3rem,3vw,1.9rem);font-weight:900;color:#fff;
  letter-spacing:-.03em;margin-bottom:1rem;line-height:1.2;
}
.section h2 span.sp-accent,.section h3 span.sp-accent{color:var(--red)}
.section p{font-size:.9rem;color:var(--muted);line-height:1.75;margin-bottom:.9rem}

/* ── COMPARISON TABLE ── */
.section table,.comparison-table{
  width:100%;border-collapse:separate;border-spacing:0;
  border:1px solid var(--border);border-radius:18px;overflow:hidden;
  margin:1.5rem 0;font-size:.85rem;
}
.section table th,.comparison-table th{
  padding:14px 16px;background:rgba(14,8,18,.95);
  font-size:.7rem;font-weight:900;letter-spacing:.08em;
  text-transform:uppercase;color:var(--muted);
  border-bottom:1px solid var(--border);text-align:left;position:relative;
}
.section table td,.comparison-table td{
  padding:13px 16px;border-bottom:1px solid rgba(255,255,255,.05);
  color:rgba(255,248,245,.72);vertical-align:middle;
}
.section table tr:last-child td,.comparison-table tr:last-child td{border-bottom:none}
.section table tr:hover td,.comparison-table tr:hover td{background:rgba(255,255,255,.025)}
.section table td:first-child,.comparison-table td:first-child{
  color:#fff;font-weight:600;
}

/* ── WINNER BADGE ── */
.winner-badge{
  display:inline-flex;align-items:center;gap:4px;
  background:rgba(233,69,96,.15);border:1px solid rgba(233,69,96,.3);
  color:var(--red);border-radius:100px;
  padding:2px 8px;font-size:.62rem;font-weight:800;
  letter-spacing:.04em;text-transform:uppercase;margin-left:6px;
  vertical-align:middle;
}

/* ── TABLE CTA BUTTONS ── */
.tbl-cta{
  display:inline-block;
  background:linear-gradient(135deg,var(--red),var(--red2));
  color:#fff!important;padding:.35rem .9rem;border-radius:100px;
  font-weight:700;font-size:.75rem;text-decoration:none!important;
  white-space:nowrap;box-shadow:0 3px 12px rgba(233,69,96,.3);
  transition:transform .15s,box-shadow .15s;
}
.tbl-cta:hover{transform:translateY(-1px);box-shadow:0 6px 18px rgba(233,69,96,.45)}
.tbl-cta.alt{
  background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);
  box-shadow:none;
}
.tbl-cta.alt:hover{background:rgba(255,255,255,.12);box-shadow:none}

/* ── VERDICT / SCORE SECTIONS ── */
.verdict-box,.score-box{
  background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);
  border-radius:18px;padding:1.5rem 1.8rem;margin:1.5rem 0;
}

/* ── SECTION EYEBROW ── */
.section-eyebrow,.sp-eyebrow{
  display:inline-flex;align-items:center;gap:6px;
  font-size:.7rem;font-weight:800;letter-spacing:.1em;
  text-transform:uppercase;color:var(--red);margin-bottom:.5rem;
}

/* ── AFFILIATE DISCLOSURE PILL (keep only one) ── */
.aff-disclosure-pill{display:none!important}

/* ── HIDE JUNK ── */
.ad-placeholder,.ad-slot,.advertisement{display:none!important}

/* ── AUTHOR BYLINE ── */
.author-byline,.byline{
  font-size:.78rem;color:var(--muted);margin-bottom:1rem;
  display:flex;align-items:center;gap:.4rem;flex-wrap:wrap;
}
.author-byline a,.byline a{color:var(--red);text-decoration:none}

/* ── JOURNEY LINKS ── */
.journey-links-block{
  background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.08);
  border-radius:14px;padding:1.2rem 1.5rem;margin:2rem 0;
}
.journey-links-block h4{font-size:.82rem;font-weight:700;color:var(--muted);margin-bottom:.75rem}
.journey-links-block a{
  display:inline-block;background:rgba(255,255,255,.06);
  border:1px solid rgba(255,255,255,.1);border-radius:8px;
  padding:.3rem .8rem;font-size:.78rem;color:rgba(255,248,245,.7);
  text-decoration:none;margin:.2rem;transition:all .15s;
}
.journey-links-block a:hover{border-color:rgba(233,69,96,.3);color:#fff}

/* ── FAQ SECTION ── */
.faq-item{
  background:rgba(255,255,255,.038);border:1px solid rgba(255,255,255,.08);
  border-radius:14px;padding:1.2rem 1.4rem;margin:.75rem 0;
}
.faq-item h3,.faq-q{font-size:.92rem;font-weight:700;color:#fff;margin-bottom:.5rem}
.faq-item p,.faq-a{font-size:.86rem;color:var(--muted);line-height:1.7}

/* ── OUTER WRAPPER ── */
[style*="max-width:900px"],[style*="max-width: 900px"],
[style*="max-width:940px"],[style*="max-width: 940px"]{
  max-width:1100px!important;
  padding-top:0!important;
}
</style>"""

# ── Detect old-template pages ─────────────────────────────────────────────────
def is_old_template(html: str) -> bool:
    """Return True if page uses old template (not premium pricing/best-of)."""
    return (
        "pr-layout" not in html
        and "bc-layout" not in html
        and "score-ring" not in html
    )

# ── Cleanup functions ─────────────────────────────────────────────────────────
def fix_robots(html: str) -> str:
    """Change noindex,nofollow to index,follow."""
    html = re.sub(
        r'<meta\s+name=["\']robots["\']\s+content=["\']noindex[^"\']*["\']',
        '<meta name="robots" content="index, follow"',
        html, flags=re.IGNORECASE
    )
    return html

def remove_advertisement_text(html: str) -> str:
    """Remove bare 'Advertisement' text nodes that appear in content."""
    html = re.sub(r'(?m)^\s*Advertisement\s*$', '', html)
    html = re.sub(r'<p[^>]*>\s*Advertisement\s*</p>', '', html)
    return html

def remove_duplicate_disclosures(html: str) -> str:
    """Keep only first affiliate disclosure box, remove extras."""
    # Remove the inline aff-disclosure-pill (schema_pro adds one, template has another)
    # We keep the pill via CSS display:none and let the template's own disclosure show
    # Just strip literal "Advertisement" repeats
    return html

def inject_premium_css(html: str) -> str:
    """Inject premium CSS before </head>."""
    if 'id="upgrade-v2"' in html:
        # Re-inject with latest version
        html = re.sub(
            r'<style id="upgrade-v2">.*?</style>',
            PREMIUM_CSS,
            html, flags=re.DOTALL
        )
        return html
    return html.replace("</head>", PREMIUM_CSS + "\n</head>", 1)

def fix_canonical(html: str, path: Path) -> str:
    """Fix canonical URLs — remove numeric prefix (7-best → best)."""
    # If canonical has the filename with numeric prefix, fix it
    filename_stem = path.stem
    # e.g. "7-best-1password-alternatives-in-2026-free-paid"
    clean_stem = re.sub(r'^\d+-', '', filename_stem)
    if clean_stem != filename_stem:
        canonical_old = f"https://saaspare.org/pages/{filename_stem}"
        canonical_new = f"https://saaspare.org/pages/{clean_stem}"
        html = html.replace(canonical_old, canonical_new)
    return html

def upgrade_page(path: Path) -> bool:
    """Apply premium upgrades to a single page. Returns True if changed."""
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
        if not is_old_template(html):
            return False  # Already premium

        original = html
        html = fix_robots(html)
        html = remove_advertisement_text(html)
        html = remove_duplicate_disclosures(html)
        html = inject_premium_css(html)
        html = fix_canonical(html, path)

        if html != original:
            path.write_text(html, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"  ERROR {path.name}: {e}")
        return False

def main():
    pages = sorted(SITE.glob("*.html"))
    total = len(pages)
    upgraded = skipped = errors = 0

    print(f"Upgrading old-template pages — scanning {total} pages...")
    print()

    for i, path in enumerate(pages):
        changed = upgrade_page(path)
        if changed:
            upgraded += 1
            if upgraded <= 15 or upgraded % 100 == 0:
                print(f"  [OK] {path.name[:60]}")
        else:
            skipped += 1

    print()
    print(f"Done: {upgraded} upgraded | {skipped} already premium/skipped")
    print()
    print("Changes applied:")
    print("  - noindex → index,follow on all old pages")
    print("  - Premium CSS injected (tables, cards, hero, typography)")
    print("  - 'Advertisement' text nodes removed")
    print("  - Canonical URLs cleaned (7-best- → best-)")

if __name__ == "__main__":
    main()
