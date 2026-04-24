"""
Replaces the old light-theme <style> block in all site/pages/*.html files
with the new dark glassmorphism theme. Also upgrades nav and adds Google Fonts.
Idempotent — skips already-patched files (marker: <!-- dark-theme-v1 -->).
Run: .venv/Scripts/python scripts/retheme_pages.py
"""
import re
from pathlib import Path

PAGES = Path("site/pages")
MARKER = "<!-- dark-theme-v1 -->"

GOOGLE_FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">'

NEW_CSS = """<style>
  :root{--accent:#e94560;--glass:rgba(255,255,255,.038);--border:rgba(255,255,255,.08);--text:rgba(255,255,255,.85);--muted:rgba(255,255,255,.45);--green:#34d399;--red:#e94560}
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Plus Jakarta Sans',system-ui,sans-serif;background:#080810;color:var(--text);line-height:1.6}
  /* NAV */
  nav{background:rgba(8,8,16,.92);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border-bottom:1px solid rgba(255,255,255,.06);padding:.75rem 1.5rem;display:flex;align-items:center;gap:1.5rem;position:sticky;top:0;z-index:50}
  .logo{display:flex;align-items:center;gap:.6rem;text-decoration:none;margin-right:auto}
  .logo-bars{display:flex;flex-direction:column;gap:3px}
  .logo-bars span{display:block;height:2px;border-radius:2px;background:var(--accent)}
  .logo-bars span:nth-child(1){width:18px}
  .logo-bars span:nth-child(2){width:12px}
  .logo-bars span:nth-child(3){width:15px}
  .logo-text{font-weight:800;font-size:1.15rem;color:#fff;letter-spacing:-.02em}
  .logo-text em{font-style:normal;color:var(--accent)}
  nav a{color:rgba(255,255,255,.55);text-decoration:none;font-size:.875rem;font-weight:500;transition:color .2s}
  nav a:hover{color:#fff}
  /* LAYOUT */
  .container{max-width:920px;margin:0 auto;padding:2rem 1rem}
  /* HERO */
  .page-hero{background:radial-gradient(ellipse 120% 80% at 50% -10%,#1a0d12 0%,#0d0008 45%,#080810 80%);padding:3rem 1.5rem 2rem;text-align:center;border-bottom:1px solid rgba(255,255,255,.05)}
  .breadcrumb{color:rgba(255,255,255,.35);font-size:.8rem;margin-bottom:1rem}
  .breadcrumb a{color:rgba(255,255,255,.5);text-decoration:none}
  .breadcrumb a:hover{color:var(--accent)}
  h1{font-size:clamp(1.5rem,4vw,2.4rem);font-weight:800;letter-spacing:-.03em;line-height:1.15;color:#fff;margin-bottom:.5rem}
  .subtitle{color:rgba(255,255,255,.55);font-size:1.05rem;margin-bottom:1.5rem}
  /* TL;DR */
  .tldr-box{background:rgba(233,69,96,.08);border:1px solid rgba(233,69,96,.2);border-radius:12px;padding:1.25rem 1.5rem;margin:1.5rem 0}
  .tldr-box strong{color:#fff}
  /* TABLE */
  table{width:100%;border-collapse:collapse;margin:2rem 0;border:1px solid rgba(255,255,255,.08);border-radius:12px;overflow:hidden}
  th{background:rgba(233,69,96,.12);color:#fff;padding:.85rem 1rem;text-align:left;font-size:.85rem;letter-spacing:.04em;text-transform:uppercase}
  td{padding:.75rem 1rem;border-bottom:1px solid rgba(255,255,255,.06);color:rgba(255,255,255,.72);font-size:.9rem}
  tr:last-child td{border-bottom:none}
  tr:hover td{background:rgba(255,255,255,.025)}
  .winner-badge{background:rgba(52,211,153,.2);color:#34d399;border:1px solid rgba(52,211,153,.3);padding:2px 8px;border-radius:12px;font-size:.72rem;margin-left:6px;font-weight:600}
  /* CTA SECTION */
  .cta-section{background:rgba(233,69,96,.1);border:1px solid rgba(233,69,96,.2);padding:2rem;border-radius:16px;margin:2rem 0;text-align:center}
  .cta-section h2{margin-bottom:.75rem;color:#fff}
  .cta-btn{display:inline-block;background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.75rem 2rem;border-radius:50px;text-decoration:none;font-weight:700;margin-top:.75rem;font-size:.95rem;transition:opacity .2s;box-shadow:0 4px 20px rgba(233,69,96,.3)}
  .cta-btn:hover{opacity:.88}
  /* SECTIONS */
  .section{margin:2.5rem 0}
  .section h2{font-size:1.25rem;color:#fff;font-weight:700;margin-bottom:1rem;padding-bottom:.5rem;border-bottom:1px solid rgba(255,255,255,.08)}
  /* TOOL CARDS */
  .tool-card{background:rgba(255,255,255,.034);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:1.5rem;margin:1.5rem 0;transition:border-color .2s}
  .tool-card:hover{border-color:rgba(233,69,96,.3)}
  .tool-card h3{color:#fff;font-size:1.1rem;margin-bottom:.5rem}
  /* VERDICT */
  .verdict-box{background:rgba(52,211,153,.07);border:1px solid rgba(52,211,153,.2);border-radius:12px;padding:1rem 1.5rem;color:rgba(255,255,255,.8)}
  /* PROS / CONS */
  .pros-cons{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1rem 0}
  .pros{background:rgba(52,211,153,.07);border:1px solid rgba(52,211,153,.2);padding:1rem;border-radius:10px}
  .cons{background:rgba(233,69,96,.07);border:1px solid rgba(233,69,96,.18);padding:1rem;border-radius:10px}
  .pros h4{color:#34d399;margin-bottom:.5rem}.cons h4{color:#e94560;margin-bottom:.5rem}
  ul{padding-left:1.2rem}li{margin:.4rem 0;color:rgba(255,255,255,.7)}
  /* FAQ ACCORDION */
  .faq-item{margin:.75rem 0;border:1px solid rgba(255,255,255,.07);border-radius:12px;overflow:hidden}
  .faq-item summary{background:rgba(255,255,255,.03);color:rgba(255,255,255,.85);font-size:.95rem;font-weight:600;padding:1rem 1.25rem;cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center}
  .faq-item summary::-webkit-details-marker{display:none}
  .faq-item summary::after{content:'+';color:var(--accent);font-size:1.2rem;font-weight:300}
  .faq-item[open] summary::after{content:'−'}
  .faq-item p,.faq-item div{padding:1rem 1.25rem;color:rgba(255,255,255,.6);font-size:.9rem;line-height:1.7;border-top:1px solid rgba(255,255,255,.05)}
  /* RELATED */
  .related{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:1.5rem;margin:2rem 0}
  .related h3{color:#fff;margin-bottom:.75rem}
  .related a{display:inline-block;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.1);padding:4px 12px;border-radius:14px;font-size:.82rem;text-decoration:none;color:rgba(255,255,255,.7);margin:3px;transition:all .2s}
  .related a:hover{background:var(--accent);color:#fff;border-color:var(--accent)}
  /* TRUST BAR */
  .trust-bar{display:flex;gap:1.5rem;justify-content:center;padding:1rem;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:8px;margin:1.5rem 0;font-size:.82rem;color:rgba(255,255,255,.5);flex-wrap:wrap}
  .trust-bar span::before{content:'✓ ';color:#34d399;font-weight:700}
  /* EMAIL BOX */
  .email-box{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);padding:2rem;border-radius:16px;margin:2.5rem 0;text-align:center}
  .email-box h3{font-size:1.15rem;color:#fff;margin-bottom:.4rem}
  .email-box p{color:rgba(255,255,255,.45);font-size:.88rem;margin-bottom:1.25rem}
  .email-row{display:flex;gap:.5rem;max-width:420px;margin:0 auto;flex-wrap:wrap;justify-content:center}
  .email-row input{flex:1;min-width:200px;padding:.7rem 1rem;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:8px;color:#fff;font-size:.92rem}
  .email-row input::placeholder{color:rgba(255,255,255,.3)}
  .email-row button{background:linear-gradient(135deg,#e94560,#c73652);color:#fff;border:none;padding:.7rem 1.4rem;border-radius:8px;cursor:pointer;font-weight:700;font-size:.92rem}
  .email-row button:hover{opacity:.85}
  .email-msg{font-size:.78rem;color:rgba(255,255,255,.35);margin-top:.5rem}
  /* FOOTER */
  footer{text-align:center;color:rgba(255,255,255,.25);font-size:.82rem;margin-top:3rem;padding-top:2rem;border-top:1px solid rgba(255,255,255,.07)}
  footer a{color:rgba(255,255,255,.35);text-decoration:none}
  footer a:hover{color:rgba(255,255,255,.7)}
  /* AD SLOTS */
  .ad-slot-v2{margin:2rem 0;text-align:center;min-height:90px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.05);border-radius:8px;padding:1rem}
  .ad-label-v2{font-size:.62rem;color:rgba(255,255,255,.2);letter-spacing:.5px;text-transform:uppercase;display:block;margin-bottom:.25rem}
  /* STICKY CTA */
  .sticky-cta-v2{position:fixed;bottom:0;left:0;right:0;background:rgba(8,8,16,.95);backdrop-filter:blur(16px);border-top:1px solid rgba(255,255,255,.08);color:#fff;padding:.75rem 1rem;display:none;align-items:center;justify-content:space-between;gap:1rem;z-index:100}
  .sticky-cta-v2.show{display:flex}
  .sticky-cta-v2 a{background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.5rem 1.2rem;border-radius:50px;text-decoration:none;font-weight:700;font-size:.85rem;white-space:nowrap}
  .sticky-cta-v2 button{background:none;border:none;color:rgba(255,255,255,.4);font-size:1.2rem;cursor:pointer}
  /* EXIT MODAL */
  .exit-modal-v2{position:fixed;inset:0;background:rgba(0,0,0,.7);display:none;align-items:center;justify-content:center;z-index:1000;padding:1rem}
  .exit-modal-v2.show{display:flex}
  .exit-card-v2{background:#0e0e1a;border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:2rem;max-width:440px;width:100%;text-align:center;position:relative}
  .exit-card-v2 h3{color:#fff;font-size:1.2rem;margin-bottom:.5rem}
  .exit-card-v2 p{color:rgba(255,255,255,.5);font-size:.88rem;margin-bottom:1.25rem}
  .exit-close-v2{position:absolute;top:.5rem;right:.75rem;background:none;border:none;font-size:1.5rem;color:rgba(255,255,255,.3);cursor:pointer}
  .exit-card-v2 form{display:flex;gap:.5rem;flex-wrap:wrap}
  .exit-card-v2 input{flex:1;min-width:180px;padding:.65rem .9rem;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:8px;color:#fff;font-size:.9rem}
  .exit-card-v2 input::placeholder{color:rgba(255,255,255,.3)}
  .exit-card-v2 button[type=submit]{background:linear-gradient(135deg,#e94560,#c73652);color:#fff;border:none;padding:.65rem 1.2rem;border-radius:8px;font-weight:700;cursor:pointer}
  @media(max-width:600px){.pros-cons{grid-template-columns:1fr}h1{font-size:1.5rem}nav a.hide-mobile{display:none}.email-row{flex-direction:column}.email-row input,.email-row button{width:100%}}
</style>"""

OLD_STYLE_PATTERN = re.compile(
    r'<style>\s*:root\{--primary:#1a1a2e.*?</style>',
    re.DOTALL
)

OLD_NAV_PATTERN = re.compile(
    r'<nav>.*?</nav>',
    re.DOTALL
)

def make_nav(html: str) -> str:
    """Extract existing nav links and rebuild with new dark nav."""
    # Find all nav links except first (logo)
    nav_match = OLD_NAV_PATTERN.search(html)
    if not nav_match:
        return html
    old_nav = nav_match.group(0)
    # Extract hrefs/labels from old nav <a> tags, skip the first logo link
    links = re.findall(r'<a\s+href="([^"]+)"[^>]*>([^<]+)</a>', old_nav)
    # Build secondary nav links (skip logo-like ones)
    secondary = ""
    for href, label in links[1:]:
        if label.strip():
            secondary += f'<a href="{href}">{label.strip()}</a>'
    # Determine logo href (first link)
    logo_href = links[0][0] if links else "/"
    new_nav = f"""<nav>
<a href="{logo_href}" class="logo">
  <div class="logo-bars"><span></span><span></span><span></span></div>
  <div class="logo-text">Saa<em>Spare</em></div>
</a>
{secondary}
</nav>"""
    return html[:nav_match.start()] + new_nav + html[nav_match.end():]


def upgrade_breadcrumb(html: str) -> str:
    """Wrap breadcrumb + h1 + subtitle in page-hero div if not already."""
    if 'class="page-hero"' in html:
        return html
    # Find breadcrumb div and wrap it with page-hero through subtitle
    pattern = re.compile(
        r'(<div class="container">)\s*(<p class="breadcrumb">.*?</p>)\s*(<h1>.*?</h1>)\s*(<p class="subtitle">.*?</p>)',
        re.DOTALL
    )
    def wrap(m):
        return f'<div class="page-hero"><div class="container">\n{m.group(2)}\n{m.group(3)}\n{m.group(4)}\n</div></div>\n<div class="container">'
    result = pattern.sub(wrap, html, count=1)
    return result


def patch(html: str) -> str | None:
    if MARKER in html:
        return None
    # Replace old style block
    if not OLD_STYLE_PATTERN.search(html):
        return None  # not an old-style page

    # Add Google Fonts before <style>
    html = html.replace('<style>', GOOGLE_FONTS + '\n' + NEW_CSS + '\n<!--', 1)
    # Remove everything up to and including old </style>
    # Actually, replace the old <style>...</style> block entirely
    html = OLD_STYLE_PATTERN.sub('', html)
    # Remove the placeholder we added (the <!--)
    html = html.replace(GOOGLE_FONTS + '\n' + NEW_CSS + '\n<!--', GOOGLE_FONTS + '\n' + NEW_CSS, 1)

    # Now add font + new CSS properly
    # The above logic is messy; let's do it cleanly:
    # Reset and do it right
    return None  # placeholder


def patch_clean(html: str) -> str | None:
    """Clean replacement logic."""
    if MARKER in html:
        return None
    if not OLD_STYLE_PATTERN.search(html):
        return None

    # 1. Replace old <style> block with new dark CSS
    html = OLD_STYLE_PATTERN.sub(NEW_CSS, html, count=1)

    # 2. Inject Google Fonts before the new <style>
    html = html.replace('<style>', GOOGLE_FONTS + '\n<style>', 1)

    # 3. Add marker after </head> open tag area
    html = html.replace('<style>', f'{MARKER}\n<style>', 1)

    # 4. Upgrade nav
    html = make_nav(html)

    # 5. Wrap breadcrumb in page-hero
    html = upgrade_breadcrumb(html)

    # 6. Convert old static FAQ items to details/summary accordion
    # Old pattern: <div class="faq-item"><h3>Q</h3><p>A</p></div>
    html = re.sub(
        r'<div class="faq-item">\s*<h3>([^<]+)</h3>\s*<p>(.*?)</p>\s*</div>',
        lambda m: f'<details class="faq-item"><summary>{m.group(1).strip()}</summary><p>{m.group(2).strip()}</p></details>',
        html,
        flags=re.DOTALL
    )

    return html


def main():
    patched = skipped = errors = 0
    for f in sorted(PAGES.glob("*.html")):
        try:
            src = f.read_text(encoding="utf-8", errors="ignore")
            out = patch_clean(src)
            if out is None:
                skipped += 1
                continue
            f.write_text(out, encoding="utf-8")
            patched += 1
            print(f"  Patched: {f.name}")
        except Exception as e:
            print(f"  ERROR {f.name}: {e}")
            errors += 1
    print(f"\nDone — Patched: {patched} | Skipped: {skipped} | Errors: {errors}")


if __name__ == "__main__":
    main()
