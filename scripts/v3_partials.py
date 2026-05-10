"""HTML partials for the v3 design system.

Imported by scripts/build_v3_previews.py and (later) scripts/redesign_v3.py.
Keeps nav / footer / head boilerplate in one place.
"""

LOGO_SVG = """<svg class="v3-logo-mark" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs><clipPath id="ct"><path d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></clipPath><clipPath id="cb"><path d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/></clipPath><mask id="sm1"><rect x="-400" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="-400;0;0;180;180" keyTimes="0;0.20;0.61;0.62;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask><mask id="sm2"><rect x="180" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="180;180;-220;-220;180;180" keyTimes="0;0.21;0.41;0.82;0.83;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask><mask id="sm3"><rect x="-400" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="-400;-400;0;0" keyTimes="0;0.42;0.62;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask><mask id="sm4"><rect x="180" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="180;180;-220;-220" keyTimes="0;0.63;0.83;1" dur="12s" repeatCount="indefinite" calcMode="linear"/></rect></mask></defs><path class="mark-bot" fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/><path class="mark-top" fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/><g class="wave-top" clip-path="url(#ct)" mask="url(#sm1)"><rect width="180" height="180" fill="#e94560"/></g><g class="wave-top2" clip-path="url(#ct)" mask="url(#sm3)"><rect width="180" height="180" fill="#fff"/></g><g class="wave-bot" clip-path="url(#cb)" mask="url(#sm2)"><rect width="180" height="180" fill="#fff"/></g><g class="wave-bot2" clip-path="url(#cb)" mask="url(#sm4)"><rect width="180" height="180" fill="#e94560"/></g></svg>"""


def nav_html(active: str = "") -> str:
    """active: 'comparisons'|'roi'|'shortlist'|'deals'|'about'|'' """

    def cls(name: str) -> str:
        return ' class="nav-link active"' if active == name else ' class="nav-link"'

    return f"""<nav id="nav" class="v3-nav">
  <a href="/" class="v3-logo">
    {LOGO_SVG}
    <span class="v3-logo-text">Saa<em>Spare</em></span>
  </a>
  <a href="/pages/"{cls('comparisons')}>Comparisons</a>
  <a href="/pages/saas-roi-calculator"{cls('roi')}>ROI Calculator</a>
  <a href="/shortlist"{cls('shortlist')}>Shortlist Builder</a>
  <a href="/deal-radar"{cls('deals')}>Deal Radar</a>
  <a href="/about"{cls('about')}>About</a>
  <a href="/shortlist" class="nav-cta">Build Shortlist &#8594;</a>
</nav>"""


FOOTER = """<footer class="v3-footer">
  <div class="v3-container">
    <div class="v3-footer-grid">
      <div>
        <a href="/" class="v3-logo" style="margin-bottom:1rem">
          <svg class="v3-logo-mark" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="height:24px"><path fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/><path fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></svg>
          <span class="v3-logo-text">Saa<em>Spare</em></span>
        </a>
        <p style="font-size:.85rem;color:rgba(255,255,255,.42);max-width:300px;line-height:1.6;margin:0">
          Independent SaaS comparisons. Real pricing. Hidden fees exposed. Built for buyers, not vendors.
        </p>
      </div>
      <div>
        <h5>Product</h5>
        <ul>
          <li><a href="/pages/">Comparisons</a></li>
          <li><a href="/pages/saas-roi-calculator">ROI Calculator</a></li>
          <li><a href="/shortlist">Shortlist Builder</a></li>
          <li><a href="/deal-radar">Deal Radar</a></li>
        </ul>
      </div>
      <div>
        <h5>Categories</h5>
        <ul>
          <li><a href="/pages/best-crm-software-for-b2b-saas-in-2026-ranked">CRM</a></li>
          <li><a href="/pages/best-marketing-automation-software-for-small-business-in-2026-ranked">Marketing</a></li>
          <li><a href="/pages/best-password-managers-software-for-business-in-2026-ranked">Security</a></li>
          <li><a href="/pages/best-project-management-software-for-startups-in-2026-ranked">Project Mgmt</a></li>
          <li><a href="/pages/best-finance-ops-software-for-b2b-saas-in-2026-ranked">Finance</a></li>
        </ul>
      </div>
      <div>
        <h5>Company</h5>
        <ul>
          <li><a href="/about">About</a></li>
          <li><a href="/methodology">Methodology</a></li>
          <li><a href="/contact">Contact</a></li>
          <li><a href="/media-kit">Media Kit</a></li>
        </ul>
      </div>
      <div>
        <h5>Legal</h5>
        <ul>
          <li><a href="/affiliate-disclosure">Affiliate Disclosure</a></li>
          <li><a href="/privacy">Privacy</a></li>
          <li><a href="/terms">Terms</a></li>
        </ul>
      </div>
    </div>
    <div class="v3-footer-bottom">
      <span>&copy; 2026 SaaSpare. Independent. No vendor money buys placement.</span>
      <span>Made for SaaS buyers. Updated daily.</span>
    </div>
  </div>
</footer>"""


def head_html(title: str, description: str, canonical: str, *, extra_meta: str = "") -> str:
    """Returns full <head> block for a v3 preview page."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | SaaSpare</title>
<meta name="description" content="{description}">
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{canonical}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="/favicon-192.png">
<meta name="theme-color" content="#07070d">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="https://saaspare.org/og-default.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;850;900&family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/saaspare-v3.css">
{extra_meta}
</head>
<body class="v3">
"""
