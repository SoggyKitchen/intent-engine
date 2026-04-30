"""Patches existing generated pages in site/pages/ with AdSense, exit-intent modal,
sticky CTA, and table affiliate buttons. One-shot — safe to run multiple times
(idempotent via marker comments)."""
from pathlib import Path
import re

PAGES = Path("site/pages")
MARKER = "<!-- saaspare-v2-patched -->"

ADSENSE_HEAD = """<meta name="google-adsense-account" content="ca-pub-9433840442322701">
<link rel="preconnect" href="https://pagead2.googlesyndication.com" crossorigin>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9433840442322701" crossorigin="anonymous"></script>
"""

AD_SLOT_CSS = """  .ad-slot-v2{margin:2rem 0;text-align:center;min-height:90px;background:#fafbfc;border-radius:6px;padding:1rem}
  .ad-label-v2{font-size:.65rem;color:#bbb;letter-spacing:.5px;text-transform:uppercase;display:block;margin-bottom:.25rem}
  .sticky-cta-v2{position:fixed;bottom:0;left:0;right:0;background:#1a1a2e;color:#fff;padding:.75rem 1rem;display:none;align-items:center;justify-content:space-between;gap:1rem;box-shadow:0 -4px 18px rgba(0,0,0,.15);z-index:100}
  .sticky-cta-v2.show{display:flex}
  .sticky-cta-v2 a{background:#e94560;color:#fff;padding:.5rem 1.1rem;border-radius:5px;text-decoration:none;font-weight:700;font-size:.85rem;white-space:nowrap}
  .sticky-cta-v2 button{background:none;border:none;color:rgba(255,255,255,.5);font-size:1.1rem;cursor:pointer}
  .exit-modal-v2{position:fixed;inset:0;background:rgba(0,0,0,.6);display:none;align-items:center;justify-content:center;z-index:1000;padding:1rem}
  .exit-modal-v2.show{display:flex}
  .exit-card-v2{background:#fff;border-radius:12px;padding:2rem;max-width:440px;text-align:center;position:relative}
  .exit-card-v2 h3{color:#1a1a2e;font-size:1.3rem;margin-bottom:.5rem}
  .exit-card-v2 p{color:#666;font-size:.92rem;margin-bottom:1.25rem}
  .exit-close-v2{position:absolute;top:.5rem;right:.75rem;background:none;border:none;font-size:1.5rem;color:#aaa;cursor:pointer}
  .exit-card-v2 form{display:flex;gap:.5rem;flex-wrap:wrap}
  .exit-card-v2 input{flex:1;min-width:180px;padding:.65rem .9rem;border:1px solid #ddd;border-radius:5px}
  .exit-card-v2 button[type=submit]{background:#e94560;color:#fff;border:none;padding:.65rem 1.2rem;border-radius:5px;font-weight:700;cursor:pointer}
"""

AD_SLOT_HTML = """<div class="ad-slot-v2">
<span class="ad-label-v2">Advertisement</span>
<ins class="adsbygoogle" style="display:block;width:100%" data-ad-client="ca-pub-9433840442322701" data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
</div>"""

EXIT_MODAL = """<div class="sticky-cta-v2" id="sticky-cta-v2">
<span style="font-size:.85rem;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">Start your free trial today — no credit card required.</span>
<a href="https://saaspare.org/pages/">See Top Picks →</a>
<button onclick="document.getElementById('sticky-cta-v2').classList.remove('show');sessionStorage.setItem('scHidV2','1')">×</button>
</div>
<div class="exit-modal-v2" id="exit-modal-v2">
<div class="exit-card-v2">
<button class="exit-close-v2" onclick="closeExitV2()">×</button>
<h3>Before you go — grab the weekly deal digest</h3>
<p>Free trials, exclusive discounts &amp; new tool reviews. One short email every Friday.</p>
<form action="https://formsubmit.co/hello@saaspare.org" method="POST" id="exit-form-v2">
<input type="email" name="email" placeholder="your@email.com" required>
<input type="hidden" name="_subject" value="New SaaSpare subscriber (exit-intent)">
<input type="hidden" name="_captcha" value="false">
<input type="hidden" name="_next" value="https://saaspare.org/pages/thanks.html">
<button type="submit">Get the List →</button>
</form>
<p style="color:#aaa;font-size:.75rem;margin-top:.75rem">Join 500+ founders already subscribed</p>
</div>
</div>
<script>
(adsbygoogle=window.adsbygoogle||[]).push({});(adsbygoogle=window.adsbygoogle||[]).push({});
var scV2=document.getElementById('sticky-cta-v2');
if(scV2&&!sessionStorage.getItem('scHidV2')){window.addEventListener('scroll',function(){if(window.scrollY>600)scV2.classList.add('show');},{passive:true});}
var emV2=document.getElementById('exit-modal-v2'),shownV2=false;
function closeExitV2(){emV2.classList.remove('show');localStorage.setItem('exHidV2',Date.now());}
function maybeExitV2(){if(shownV2||localStorage.getItem('exHidV2'))return;shownV2=true;emV2.classList.add('show');}
document.addEventListener('mouseout',function(e){if(e.clientY<=0&&!e.relatedTarget)maybeExitV2();});
setTimeout(function(){if(!shownV2&&!localStorage.getItem('exHidV2'))maybeExitV2();},45000);
document.getElementById('exit-form-v2')&&document.getElementById('exit-form-v2').addEventListener('submit',function(){setTimeout(closeExitV2,200);});
emV2&&emV2.addEventListener('click',function(e){if(e.target===emV2)closeExitV2();});
</script>
"""


def patch(html: str) -> str | None:
    if MARKER in html:
        return None
    if "</head>" not in html or "</body>" not in html:
        return None
    html = html.replace("</head>", f"{ADSENSE_HEAD}{MARKER}\n</head>", 1)
    html = re.sub(r"(</style>)", AD_SLOT_CSS + r"\1", html, count=1)
    html = re.sub(
        r'(<div class="tldr-box">.*?</div>)',
        lambda m: m.group(1) + "\n" + AD_SLOT_HTML,
        html, count=1, flags=re.DOTALL,
    )
    html = re.sub(
        r'(<h2[^>]*>\s*Frequently Asked Questions)',
        AD_SLOT_HTML + r"\n\1",
        html, count=1,
    )
    html = html.replace("</body>", f"{EXIT_MODAL}\n</body>", 1)
    return html


def main() -> None:
    patched = skipped = 0
    for f in sorted(PAGES.glob("*.html")):
        src = f.read_text(encoding="utf-8", errors="ignore")
        out = patch(src)
        if out is None:
            skipped += 1
            continue
        f.write_text(out, encoding="utf-8")
        patched += 1
    print(f"Patched: {patched} | Skipped (already patched or invalid): {skipped}")


if __name__ == "__main__":
    main()
