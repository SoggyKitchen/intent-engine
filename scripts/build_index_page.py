"""
Rebuilds site/pages/index.html as a polished dark-theme directory page.
Scans all site/pages/*.html, auto-categorises, prettifies titles, and renders
a card-grid layout matching the homepage design.
Run: .venv/Scripts/python scripts/build_index_page.py
"""
import re
from datetime import date
from pathlib import Path

PAGES = Path("site/pages")
DOMAIN = "https://saaspare.org"

SKIP = {"index", "thanks", "verification", "saas-roi-calculator"}

def pretty_title(slug: str) -> str:
    """Convert slug to a clean human-readable title."""
    s = slug
    s = re.sub(r'-2026.*', '', s)
    s = re.sub(r'-2025.*', '', s)
    s = s.replace('-vs-', ' vs ')
    s = s.replace('-io', '.io')
    s = s.replace('-ai', ' AI')
    s = s.replace('-com', '.com')
    words = s.split('-')
    titled = []
    for w in words:
        if w.lower() in ('vs', 'for', 'the', 'in', 'of', 'and', 'to', 'a', 'an', 'is', 'it'):
            titled.append(w.lower())
        else:
            titled.append(w.capitalize())
    title = ' '.join(titled)
    # Fix known brand names
    brands = {
        'Semrush': 'Semrush', 'Ahrefs': 'Ahrefs', 'Hubspot': 'HubSpot',
        'Clickup': 'ClickUp', 'Freshbooks': 'FreshBooks', 'Bigcommerce': 'BigCommerce',
        'Digitalocean': 'DigitalOcean', 'Pandadoc': 'PandaDoc', 'Nordlayer': 'NordLayer',
        'Bamboohr': 'BambooHR', 'Docusign': 'DocuSign', 'Activecampaign': 'ActiveCampaign',
        'Moz': 'Moz', 'Spyfu': 'SpyFu', 'Surfer': 'Surfer SEO', 'Rankmath': 'RankMath',
        'Se': 'SE', 'Saas': 'SaaS', 'Devops': 'DevOps', '1password': '1Password',
        'Jasper': 'Jasper AI', 'Copy': 'Copy.AI', 'Pipedrive': 'Pipedrive',
        'Clearscope': 'Clearscope', 'Mangools': 'Mangools', 'Frase': 'Frase.io',
        'Crm': 'CRM', 'Seo': 'SEO', 'Pm': 'PM',
    }
    for wrong, right in brands.items():
        title = re.sub(r'\b' + wrong + r'\b', right, title, flags=re.IGNORECASE)
    return title.strip()


def categorise(slug: str) -> str:
    if re.search(r'-vs-', slug):
        return 'Comparisons'
    if 'alternatives' in slug:
        return 'Alternatives'
    if 'pricing' in slug:
        return 'Pricing Guides'
    if 'review' in slug:
        return 'Reviews'
    if 'free-trial' in slug:
        return 'Free Trials'
    if 'promo-code' in slug or 'coupon' in slug or 'discount' in slug:
        return 'Promo Codes & Deals'
    if slug.startswith('best-'):
        return 'Best-Of Lists'
    return 'Other'

CAT_ORDER = ['Comparisons', 'Alternatives', 'Pricing Guides', 'Reviews',
             'Free Trials', 'Promo Codes & Deals', 'Best-Of Lists', 'Other']

CAT_ICONS = {
    'Comparisons': '⚡',
    'Alternatives': '🔄',
    'Pricing Guides': '💰',
    'Reviews': '⭐',
    'Free Trials': '🎁',
    'Promo Codes & Deals': '🏷️',
    'Best-Of Lists': '🏆',
    'Other': '📄',
}

CAT_DESC = {
    'Comparisons': 'Side-by-side breakdowns of competing tools',
    'Alternatives': 'Best alternatives to popular SaaS tools',
    'Pricing Guides': 'Exact plans, costs & what you actually pay',
    'Reviews': 'Honest verdicts with pros, cons & scores',
    'Free Trials': 'How to get free access, step by step',
    'Promo Codes & Deals': 'Working discount codes & limited offers',
    'Best-Of Lists': 'Top picks across categories & use cases',
    'Other': 'Additional guides & resources',
}


def build():
    cats: dict[str, list[tuple[str, str]]] = {c: [] for c in CAT_ORDER}

    for f in sorted(PAGES.glob("*.html")):
        if f.stem in SKIP:
            continue
        cat = categorise(f.stem)
        title = pretty_title(f.stem)
        url = f"{DOMAIN}/pages/{f.name}"
        cats[cat].append((url, title))

    total = sum(len(v) for v in cats.values())

    sections_html = ""
    for cat in CAT_ORDER:
        items = cats[cat]
        if not items:
            continue
        icon = CAT_ICONS[cat]
        desc = CAT_DESC[cat]
        items_html = "\n".join(
            f'          <a href="{url}" class="page-link">{title}</a>'
            for url, title in items
        )
        sections_html += f"""
  <section class="cat-section">
    <div class="cat-header">
      <div class="cat-icon">{icon}</div>
      <div>
        <h2>{cat} <span class="count">({len(items)})</span></h2>
        <p class="cat-desc">{desc}</p>
      </div>
    </div>
    <div class="page-grid">
{items_html}
    </div>
  </section>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>All SaaS Comparisons & Guides | SaaSpare</title>
<meta name="description" content="Browse {total} B2B SaaS comparison pages, pricing guides, reviews and alternatives — all free.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{DOMAIN}/pages/">
<meta property="og:title" content="All SaaS Comparisons & Guides | SaaSpare">
<meta property="og:description" content="Browse {total} B2B SaaS comparison pages, pricing guides, reviews and alternatives — all free.">
<meta property="og:image" content="{DOMAIN}/og-default.png">
<meta property="og:type" content="website">
<meta property="og:url" content="{DOMAIN}/pages/">
<meta name="google-adsense-account" content="ca-pub-9433840442322701">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="preconnect" href="https://pagead2.googlesyndication.com" crossorigin>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9433840442322701" crossorigin="anonymous"></script>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Plus Jakarta Sans',system-ui,sans-serif;background:#080810;color:rgba(255,255,255,.85);line-height:1.6}}
  /* NAV */
  nav{{position:fixed;top:0;left:0;right:0;z-index:200;padding:.85rem 2rem;display:flex;align-items:center;gap:6px;background:rgba(8,8,16,.92);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border-bottom:1px solid rgba(255,255,255,.06)}}
  .logo{{display:flex;align-items:center;gap:9px;margin-right:auto;text-decoration:none}}
  .logo-mark{{height:26px;width:auto;flex-shrink:0;overflow:visible;animation:markGlow 4s ease-in-out infinite}}
  .mark-top,.mark-bot{{transform-box:fill-box;transform-origin:center;transition:transform .5s cubic-bezier(.34,1.56,.64,1)}}
  .wv{{pointer-events:none;transition:opacity .3s}}
  @keyframes markGlow{{0%,100%{{filter:drop-shadow(0 0 0px rgba(233,69,96,0))}}50%{{filter:drop-shadow(0 3px 18px rgba(233,69,96,.6))}}}}
  .logo:hover .logo-mark{{animation:none}}
  .logo:hover .mark-top{{transform:translateX(26px);filter:drop-shadow(-2px 0 6px rgba(0,0,0,.9)) drop-shadow(0 0 14px rgba(233,69,96,.5))}}
  .logo:hover .mark-bot{{transform:translateX(-26px);filter:drop-shadow(2px 0 6px rgba(0,0,0,.9)) drop-shadow(0 0 14px rgba(233,69,96,.5))}}
  .logo:hover .wv,.logo:hover .wave-top,.logo:hover .wave-bot,.logo:hover .wave-top2,.logo:hover .wave-bot2{{opacity:0}}
  .logo-text{{font-weight:800;font-size:1.05rem;letter-spacing:-.5px;color:#fff}}
  .logo-text em{{color:#e94560;font-style:normal}}
  .nav-link{{color:rgba(255,255,255,.45);font-size:.82rem;padding:.4rem .85rem;border-radius:8px;font-weight:500;transition:color .18s;text-decoration:none}}
  .nav-link:hover{{color:#fff}}
  .nav-cta{{background:linear-gradient(135deg,#e94560,#c73652);color:#fff;padding:.44rem 1.15rem;border-radius:100px;font-weight:700;font-size:.8rem;margin-left:6px;transition:transform .15s,box-shadow .15s;text-decoration:none}}
  .nav-cta:hover{{transform:translateY(-1px);box-shadow:0 6px 20px rgba(233,69,96,.45)}}
  /* HERO — plexus orb with centered search */
  .hero{{position:relative;overflow:hidden;min-height:76vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:7rem 1.5rem 3rem;background:radial-gradient(ellipse 120% 80% at 50% -10%,#1a0d12 0%,#0d0008 45%,#080810 80%);border-bottom:1px solid rgba(255,255,255,.05)}}
  .ai-orb{{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:0}}
  .hero-inner{{position:relative;z-index:2;width:100%;max-width:680px;margin:0 auto;display:flex;flex-direction:column;align-items:center}}
  .hero-badge{{display:inline-flex;align-items:center;gap:.5rem;font-size:.74rem;font-weight:600;letter-spacing:.02em;color:rgba(255,255,255,.62);background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);padding:.34rem .8rem;border-radius:50px;margin-bottom:1.4rem;opacity:0;animation:orbUp .7s .15s cubic-bezier(.22,1,.36,1) forwards}}
  .hero-badge .pulse{{width:6px;height:6px;border-radius:50%;background:#36e6a1;box-shadow:0 0 8px #36e6a1}}
  .hero h1{{font-size:clamp(2rem,5.5vw,3.4rem);font-weight:800;letter-spacing:-.035em;line-height:1.08;color:#fff;margin-bottom:.7rem;text-wrap:balance;opacity:0;animation:orbUp .8s .25s cubic-bezier(.22,1,.36,1) forwards}}
  .hero h1 em{{font-style:normal;color:#e94560}}
  .hero-sub{{color:rgba(255,255,255,.55);font-size:1.06rem;max-width:520px;margin-bottom:2rem;text-wrap:pretty;opacity:0;animation:orbUp .8s .35s cubic-bezier(.22,1,.36,1) forwards}}
  /* SEARCH — glowing, centered in the orb */
  .search-bar{{position:relative;width:100%;max-width:540px;margin:0 auto;opacity:0;animation:orbScale .9s .45s cubic-bezier(.22,1,.36,1) forwards}}
  .search-bar::before{{content:'';position:absolute;inset:-14px;border-radius:24px;background:radial-gradient(ellipse at center,rgba(233,69,96,.24),transparent 70%);filter:blur(16px);z-index:-1;animation:orbGlow 4.5s ease-in-out infinite}}
  .search-bar input{{width:100%;padding:1.05rem 1.2rem 1.05rem 3.2rem;background:rgba(16,12,20,.74);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(233,69,96,.35);border-radius:16px;color:#fff;font-size:1.02rem;font-family:inherit;outline:none;box-shadow:0 18px 50px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.06);transition:border-color .25s,box-shadow .25s}}
  .search-bar input::placeholder{{color:rgba(255,255,255,.42)}}
  .search-bar input:focus{{border-color:rgba(233,69,96,.72);box-shadow:0 22px 60px rgba(233,69,96,.28),inset 0 1px 0 rgba(255,255,255,.08)}}
  .search-bar svg{{position:absolute;left:1.15rem;top:50%;transform:translateY(-50%);color:rgba(233,69,96,.85);width:18px;height:18px}}
  .search-hint{{margin-top:.9rem;font-size:.78rem;color:rgba(255,255,255,.34);opacity:0;animation:orbUp .8s .6s cubic-bezier(.22,1,.36,1) forwards}}
  .stat-pills{{display:flex;gap:.6rem;justify-content:center;flex-wrap:wrap;margin-top:1.6rem;opacity:0;animation:orbUp .8s .7s cubic-bezier(.22,1,.36,1) forwards}}
  .stat-pill{{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:50px;padding:.34rem .85rem;font-size:.8rem;color:rgba(255,255,255,.6);font-weight:500}}
  .stat-pill strong{{color:#fff}}
  @keyframes orbUp{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:translateY(0)}}}}
  @keyframes orbScale{{from{{opacity:0;transform:scale(.94)}}to{{opacity:1;transform:scale(1)}}}}
  @keyframes orbGlow{{0%,100%{{opacity:.6}}50%{{opacity:1}}}}
  @media(prefers-reduced-motion:reduce){{.hero-badge,.hero h1,.hero-sub,.search-bar,.search-hint,.stat-pills{{animation:none!important;opacity:1;transform:none}}.search-bar::before{{animation:none}}}}
  /* CONTAINER */
  .container{{max-width:980px;margin:0 auto;padding:2rem 1rem 4rem}}
  /* CATEGORY SECTIONS */
  .cat-section{{margin:2.5rem 0}}
  .cat-header{{display:flex;align-items:flex-start;gap:.9rem;margin-bottom:1rem}}
  .cat-icon{{font-size:1.4rem;width:2.4rem;height:2.4rem;background:rgba(233,69,96,.1);border:1px solid rgba(233,69,96,.2);border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:.1rem}}
  .cat-header h2{{font-size:1.1rem;color:#fff;font-weight:700;letter-spacing:-.01em}}
  .count{{color:rgba(255,255,255,.35);font-weight:400;font-size:.95rem}}
  .cat-desc{{color:rgba(255,255,255,.4);font-size:.82rem;margin-top:.1rem}}
  /* PAGE GRID */
  .page-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:.5rem}}
  .page-link{{display:block;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:10px;padding:.6rem .9rem;font-size:.85rem;color:rgba(255,255,255,.7);text-decoration:none;font-weight:500;transition:all .18s;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
  .page-link:hover{{background:rgba(233,69,96,.08);border-color:rgba(233,69,96,.25);color:#fff}}
  /* DIVIDER */
  .divider{{border:none;border-top:1px solid rgba(255,255,255,.06);margin:0}}
  /* FOOTER */
  footer{{text-align:center;color:rgba(255,255,255,.25);font-size:.82rem;padding:2rem 1rem;border-top:1px solid rgba(255,255,255,.07)}}
  footer a{{color:rgba(255,255,255,.35);text-decoration:none}}
  footer a:hover{{color:rgba(255,255,255,.7)}}
  /* HIDDEN search */
  .page-link.hidden{{display:none}}
  @media(max-width:768px){{.nav-link,.nav-cta{{display:none}}.hero{{padding:5rem 1.25rem 2rem}}.page-grid{{grid-template-columns:1fr 1fr}}.hero h1{{font-size:1.8rem}}}}
</style>
</head>
<body>
<nav>
  <a href="{DOMAIN}" class="logo">
    <svg class="logo-mark" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs><clipPath id="ct"><path d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></clipPath><clipPath id="cb"><path d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/></clipPath><mask id="sm1"><rect x="-400" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="-400;0;0;180;180" keyTimes="0;0.20;0.61;0.62;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask><mask id="sm2"><rect x="180" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="180;180;-220;-220;180;180" keyTimes="0;0.21;0.41;0.82;0.83;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask><mask id="sm3"><rect x="-400" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="-400;-400;0;0" keyTimes="0;0.42;0.62;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask><mask id="sm4"><rect x="180" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="180;180;-220;-220" keyTimes="0;0.63;0.83;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask></defs><path class="mark-bot" fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/><path class="mark-top" fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/><g class="wave-top" clip-path="url(#ct)" mask="url(#sm1)"><rect width="180" height="180" fill="#e94560"/></g><g class="wave-top2" clip-path="url(#ct)" mask="url(#sm3)"><rect width="180" height="180" fill="#fff"/></g><g class="wave-bot" clip-path="url(#cb)" mask="url(#sm2)"><rect width="180" height="180" fill="#fff"/></g><g class="wave-bot2" clip-path="url(#cb)" mask="url(#sm4)"><rect width="180" height="180" fill="#e94560"/></g></svg>
    <span class="logo-text">Saa<em>Spare</em></span>
  </a>
  <a href="{DOMAIN}/pages/" class="nav-link">Comparisons</a>
  <a href="{DOMAIN}/pages/saas-roi-calculator.html" class="nav-link">ROI Calculator</a>
  <a href="{DOMAIN}/about.html" class="nav-link">About</a>
  <a href="{DOMAIN}/pages/" class="nav-cta">Browse Tools &#8594;</a>
</nav>

<div class="hero">
  <canvas class="ai-orb" id="ai-orb" aria-hidden="true"></canvas>
  <div class="hero-inner">
    <span class="hero-badge"><span class="pulse"></span>{total} buyer pages indexed</span>
    <h1>Find the right <em>SaaS</em>, fast</h1>
    <p class="hero-sub">Search every comparison, pricing guide and review in one place — no paid rankings, no fluff.</p>
    <div class="search-bar">
      <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      <input type="text" id="search" placeholder="Search tools, pricing, comparisons…" autocomplete="off">
    </div>
    <p class="search-hint">Try “HubSpot pricing”, “Ahrefs vs Semrush”, or “best CRM”.</p>
    <div class="stat-pills">
      <span class="stat-pill"><strong>{len(cats['Comparisons'])}</strong> Comparisons</span>
      <span class="stat-pill"><strong>{len(cats['Pricing Guides'])}</strong> Pricing Guides</span>
      <span class="stat-pill"><strong>{len(cats['Reviews'])}</strong> Reviews</span>
      <span class="stat-pill"><strong>{len(cats['Alternatives'])}</strong> Alternatives</span>
      <span class="stat-pill"><strong>{len(cats['Free Trials'])}</strong> Free Trials</span>
    </div>
  </div>
</div>

<div class="container">
{sections_html}
</div>

<footer>
  <p>Last updated: {date.today().strftime("%B %d, %Y").replace(" 0", " ")} &nbsp;·&nbsp;
  <a href="{DOMAIN}/about.html">About</a> &nbsp;·&nbsp;
  <a href="{DOMAIN}/privacy.html">Privacy</a></p>
</footer>

<script>
(function(){{
  var canvas=document.getElementById('ai-orb');
  if(!canvas)return;
  var ctx=canvas.getContext('2d');
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var DPR=Math.min(window.devicePixelRatio||1,2),W,H;
  function resize(){{
    var p=canvas.parentElement;W=p.offsetWidth;H=p.offsetHeight;
    canvas.width=W*DPR;canvas.height=H*DPR;ctx.setTransform(DPR,0,0,DPR,0,0);
  }}
  resize();window.addEventListener('resize',resize,{{passive:true}});
  var N=window.innerWidth<700?130:220,GOLDEN=Math.PI*(3-Math.sqrt(5)),nodes=[];
  for(var i=0;i<N;i++){{
    var y=1-(i/(N-1))*2,rad=Math.sqrt(Math.max(0,1-y*y)),th=i*GOLDEN;
    nodes.push({{x:Math.cos(th)*rad,y:y,z:Math.sin(th)*rad,pulse:Math.random()*6.283}});
  }}
  var LINK=0.55,edges=[];
  for(var a=0;a<N;a++)for(var b=a+1;b<N;b++){{
    var dx=nodes[a].x-nodes[b].x,dy=nodes[a].y-nodes[b].y,dz=nodes[a].z-nodes[b].z;
    var d=Math.sqrt(dx*dx+dy*dy+dz*dz);
    if(d<LINK)edges.push([a,b,1-d/LINK]);
  }}
  var rotY=0,rotX=-0.18,t=0,mx=0,my=0,smx=0,smy=0,start=performance.now(),proj=new Array(N);
  window.addEventListener('mousemove',function(e){{
    var r=canvas.getBoundingClientRect();
    mx=(e.clientX-r.left)/r.width-0.5;my=(e.clientY-r.top)/r.height-0.5;
  }},{{passive:true}});
  function frame(now){{
    smx+=(mx-smx)*0.05;smy+=(my-smy)*0.05;
    var intro=Math.min(1,(now-start)/1300),ease=reduce?1:1-Math.pow(1-intro,3);
    ctx.clearRect(0,0,W,H);
    var cx=W*0.5,cy=H*0.5,R=Math.min(W,H)*(window.innerWidth<700?0.46:0.4)*ease,op=0.55+0.45*ease;
    var ay=rotY+smx*0.5,ax=rotX+smy*0.35;
    var cY=Math.cos(ay),sY=Math.sin(ay),cX=Math.cos(ax),sX=Math.sin(ax);
    for(var i=0;i<N;i++){{
      var n=nodes[i],x1=n.x*cY-n.z*sY,z1=n.x*sY+n.z*cY;
      var y2=n.y*cX-z1*sX,z2=n.y*sX+z1*cX,persp=1/(2.1-z2);
      proj[i]={{sx:cx+x1*R*persp*1.5,sy:cy+y2*R*persp*1.5,z:z2}};
    }}
    ctx.lineWidth=0.8;
    for(var e2=0;e2<edges.length;e2++){{
      var p1=proj[edges[e2][0]],p2=proj[edges[e2][1]],depth=(p1.z+p2.z)*0.5;
      var la=edges[e2][2]*0.6*((depth+1)*0.5)*op;
      if(la<0.02)continue;
      ctx.strokeStyle='rgba(255,90,120,'+la+')';
      ctx.beginPath();ctx.moveTo(p1.sx,p1.sy);ctx.lineTo(p2.sx,p2.sy);ctx.stroke();
    }}
    for(var k=0;k<N;k++){{
      var p=proj[k],dp=(p.z+1)*0.5,pr=0.82+0.18*Math.sin(t*1.5+nodes[k].pulse);
      var rr=(1+dp*2.4)*pr,al=(0.32+dp*0.62)*op;
      ctx.beginPath();ctx.arc(p.sx,p.sy,rr,0,6.283);
      ctx.fillStyle=dp>0.55?'rgba(255,150,170,'+al+')':'rgba(255,255,255,'+al*0.8+')';
      ctx.fill();
    }}
  }}
  var raf=0;
  function loop(){{
    frame(performance.now());
    if(reduce)return;
    rotY+=0.0014;t+=0.016;
    raf=requestAnimationFrame(loop);
  }}
  loop();
  document.addEventListener('visibilitychange',function(){{if(!document.hidden&&!reduce){{cancelAnimationFrame(raf);raf=requestAnimationFrame(loop);}}}},{{passive:true}});
}})();
var inp=document.getElementById('search');
var links=document.querySelectorAll('.page-link');
inp.addEventListener('input',function(){{
  var q=this.value.toLowerCase().trim();
  links.forEach(function(a){{
    a.classList.toggle('hidden', q && !a.textContent.toLowerCase().includes(q));
  }});
  document.querySelectorAll('.cat-section').forEach(function(s){{
    var vis=[...s.querySelectorAll('.page-link')].some(function(a){{return !a.classList.contains('hidden')}});
    s.style.display=(!q||vis)?'':'none';
  }});
}});
</script>
<script src="https://www.anrdoezrs.net/am/101733230/include/allCj/impressions/page/am.js"></script>
</body>
</html>"""
    out = PAGES / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"Built index.html — {total} pages across {sum(1 for c in cats.values() if c)} categories")


if __name__ == "__main__":
    build()
