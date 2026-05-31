"""
Fix Nav & Footer: Replace placeholder sp-nav/sp-footer on ALL inner pages
with the real SaaSpare branded nav (animated SVG logo) and full footer.

Run: uv run python scripts/fix_nav_footer.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

# ── PROPER NAV (matches homepage exactly) ─────────────────────────────────────
LOGO_SVG = '<svg style="height:26px;width:auto;flex-shrink:0;overflow:visible" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs><clipPath id="ct"><path d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></clipPath><clipPath id="cb"><path d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/></clipPath></defs><path fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/><path fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></svg>'

PROPER_NAV = f"""<nav id="sp-nav" style="position:fixed;top:0;left:0;right:0;z-index:200;padding:.9rem 2rem;display:flex;align-items:center;gap:6px;background:transparent;border-bottom:none;transition:all .3s ease;">
    <a href="/" style="display:flex;align-items:center;gap:9px;margin-right:auto;text-decoration:none;">
      {LOGO_SVG}
      <span style="font-weight:800;font-size:1.05rem;letter-spacing:-.4px;color:#fff">Saa<em style="color:#e94560;font-style:normal">Spare</em></span>
    </a>
    <a href="/pages/" style="color:rgba(255,248,245,.42);font-size:.8rem;padding:.38rem .82rem;border-radius:8px;font-weight:500;text-decoration:none;white-space:nowrap;">Comparisons</a>
    <a href="/deal-radar" style="color:rgba(255,248,245,.42);font-size:.8rem;padding:.38rem .82rem;border-radius:8px;font-weight:500;text-decoration:none;white-space:nowrap;">Deal Radar</a>
    <a href="/about" style="color:rgba(255,248,245,.42);font-size:.8rem;padding:.38rem .82rem;border-radius:8px;font-weight:500;text-decoration:none;white-space:nowrap;">About</a>
    <a href="/shortlist" style="background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.44rem 1.15rem;border-radius:100px;font-weight:700;font-size:.78rem;box-shadow:0 4px 16px rgba(233,69,96,.4);margin-left:6px;text-decoration:none;white-space:nowrap;">Shortlist Builder &#8594;</a>
  </nav>
  <script>
    (function(){{
      var n=document.getElementById('sp-nav');
      if(!n) return;
      window.addEventListener('scroll',function(){{
        if(window.scrollY>40){{
          n.style.background='rgba(7,7,13,.85)';
          n.style.borderBottom='1px solid rgba(255,255,255,.07)';
          n.style.backdropFilter='blur(20px)';
        }} else {{
          n.style.background='transparent';
          n.style.borderBottom='none';
          n.style.backdropFilter='none';
        }}
      }},{{passive:true}});
    }})();
  </script>"""

FOOTER_SVG = '<svg style="height:22px;width:auto;flex-shrink:0" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg"><path fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/><path fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></svg>'

PROPER_FOOTER = f"""<footer style="border-top:1px solid rgba(255,255,255,.07);position:relative;z-index:1;margin-top:4rem;">
    <div style="max-width:1300px;margin:0 auto;padding:3rem clamp(1.5rem,4vw,3rem) 2rem;display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:3rem;">
      <div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:.65rem;">
          {FOOTER_SVG}
          <span style="font-weight:800;font-size:.92rem;color:#fff">Saa<em style="color:#e94560;font-style:normal">Spare</em></span>
        </div>
        <p style="font-size:.8rem;color:rgba(255,255,255,.24);line-height:1.75;max-width:220px;">Unbiased B2B SaaS comparisons for founders, CTOs and operators making smart software decisions.</p>
      </div>
      <div>
        <h4 style="font-size:.62rem;font-weight:700;color:rgba(255,255,255,.22);letter-spacing:.9px;text-transform:uppercase;margin-bottom:.9rem;">Compare</h4>
        <a href="/pages/" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">All Comparisons</a>
        <a href="/pages/?q=crm" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">CRM Tools</a>
        <a href="/pages/?q=seo" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">SEO Software</a>
        <a href="/pages/?q=vpn" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">VPN</a>
        <a href="/pages/?q=accounting" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">Accounting</a>
      </div>
      <div>
        <h4 style="font-size:.62rem;font-weight:700;color:rgba(255,255,255,.22);letter-spacing:.9px;text-transform:uppercase;margin-bottom:.9rem;">Resources</h4>
        <a href="/pages/saas-pricing-changes" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">Price Changes Tracker</a>
        <a href="/pages/best-vpn-for-streaming-2026" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">Best VPN for Streaming</a>
        <a href="/pages/best-password-manager-2026" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">Best Password Manager</a>
        <a href="/deal-radar" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">Deal Radar</a>
        <a href="/shortlist" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">Shortlist Builder</a>
        <a href="/blog/" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">Blog</a>
      </div>
      <div>
        <h4 style="font-size:.62rem;font-weight:700;color:rgba(255,255,255,.22);letter-spacing:.9px;text-transform:uppercase;margin-bottom:.9rem;">Company</h4>
        <a href="/about" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">About</a>
        <a href="/authors/kaylan-von-papen" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">Kaylan von Papen</a>
        <a href="/editorial-policy" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">Editorial Policy</a>
        <a href="/affiliate-disclosure" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">Affiliate Disclosure</a>
        <a href="/privacy" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">Privacy</a>
        <a href="/contact" style="display:block;font-size:.8rem;color:rgba(255,255,255,.32);margin-bottom:.5rem;">Contact</a>
      </div>
    </div>
    <div style="max-width:1300px;margin:0 auto;padding:1.25rem clamp(1.5rem,4vw,3rem);border-top:1px solid rgba(255,255,255,.04);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.5rem;font-size:.72rem;color:rgba(255,255,255,.18);">
      <span>&copy; 2026 SaaSpare &middot; <a href="/affiliate-disclosure" style="color:rgba(255,255,255,.24);">Affiliate Disclosure</a></span>
      <span>This site contains affiliate links. We may earn a commission at no extra cost to you.</span>
    </div>
  </footer>"""


def fix_nav_footer(fp: Path) -> bool:
    content = fp.read_text(encoding='utf-8', errors='replace')
    original = content

    # Replace sp-nav (our placeholder nav from design system)
    # Pattern: <nav class="sp-nav"...>...</nav> (possibly with id)
    content = re.sub(
        r'<nav\s+class="sp-nav"[^>]*>.*?</nav>',
        PROPER_NAV,
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Also replace nav with id="sp-nav" that we might have already set
    content = re.sub(
        r'<nav\s+id="sp-nav"[^>]*>.*?</nav>(?:\s*<script>.*?</script>)?',
        PROPER_NAV,
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Replace sp-footer
    content = re.sub(
        r'<footer\s+class="sp-footer"[^>]*>.*?</footer>',
        PROPER_FOOTER,
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Replace generic plain footer from our wave19 wrapper
    content = re.sub(
        r'<footer style="[^"]*border-top[^"]*"[^>]*>.*?</footer>',
        PROPER_FOOTER,
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE
    )

    if content != original:
        fp.write_text(content, encoding='utf-8')
        return True
    return False


def main():
    fixed = 0
    skipped = 0

    targets = (
        list((SITE / "pages").glob("*.html")) +
        list((SITE / "blog").glob("*.html")) +
        list((SITE / "authors").glob("*.html"))
    )

    total = len(targets)
    print(f"Processing {total} pages…")

    for fp in sorted(targets):
        if "v3-preview" in fp.name:
            skipped += 1
            continue
        try:
            if fix_nav_footer(fp):
                fixed += 1
        except Exception as e:
            print(f"  ERROR {fp.name}: {e}")

    print(f"\nDone.")
    print(f"  Nav/footer fixed: {fixed}")
    print(f"  Skipped:          {skipped}")
    print(f"  Unchanged:        {total - fixed - skipped}")


if __name__ == '__main__':
    main()
