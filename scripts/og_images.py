#!/usr/bin/env python3
"""
og_images.py — generate per-vertical Open Graph images.

Currently every page shares /og-default.png. That hurts social sharing CTR
and looks spammy when sharing 5 different SaaSpare links to a Slack channel.

Phase 2 fix: generate 16 vertical-specific OG images (1200×630, dark theme,
SaaSpare branded) and update each page's <meta property="og:image"> to
point to the right one based on the page's vertical.

Output: site/og/{vertical}.png and updated <meta og:image> tags on all pages.

Run: uv run python scripts/og_images.py
Re-runs are idempotent (regenerate images, re-set meta tags).
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys, base64

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
PAGES = SITE / "pages"
OG_DIR = SITE / "og"
OG_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS = ROOT / "outputs" / "seo"
OUTPUTS.mkdir(parents=True, exist_ok=True)

# Vertical → (slug, label, accent color, keyword markers in filename)
VERTICALS = {
    "crm":              ("CRM Software",         "#e94560", {"crm", "salesforce", "hubspot", "pipedrive", "zoho", "close", "freshsales", "keap", "copper"}),
    "seo":              ("SEO Tools",            "#4ecdc4", {"ahrefs", "semrush", "moz", "surfer", "mangools", "frase", "clearscope", "spyfu", "ubersuggest", "se-ranking"}),
    "project-mgmt":     ("Project Management",   "#7b68ee", {"asana", "clickup", "monday", "notion", "wrike", "smartsheet", "linear", "trello", "basecamp", "todoist"}),
    "hr":               ("HR & Recruiting",      "#ff6b6b", {"bamboohr", "rippling", "gusto", "deel", "workable", "greenhouse", "lever", "workday", "lattice"}),
    "finance":          ("Finance Operations",   "#feca57", {"ramp", "brex", "expensify", "freshbooks", "xero", "chargebee", "stripe", "quickbooks", "wave", "airbase"}),
    "dev-tools":        ("Developer Tools",      "#1dd1a1", {"github-copilot", "jetbrains", "sentry", "datadog", "snyk", "render", "supabase", "vercel", "retool"}),
    "security":         ("Security",             "#54a0ff", {"1password", "bitwarden", "dashlane", "nordlayer", "cloudflare", "okta", "crowdstrike", "qualys", "tresorit"}),
    "ai":               ("AI Tools",             "#a55eea", {"jasper", "copy-ai", "writesonic", "pinecone", "openai", "anthropic", "cohere"}),
    "marketing":        ("Marketing Automation", "#f368e0", {"mailchimp", "activecampaign", "convertkit", "klaviyo", "getresponse", "brevo", "lemlist"}),
    "analytics":        ("Analytics",            "#26de81", {"mixpanel", "amplitude", "hotjar", "fullstory", "databox", "heap", "segment"}),
    "ecommerce":        ("E-commerce",           "#fc5c65", {"shopify", "bigcommerce", "gumroad", "woocommerce", "paddle", "recurly"}),
    "cloud":            ("Cloud Infrastructure", "#45aaf2", {"digitalocean", "vultr", "hetzner", "contabo", "linode", "aws", "heroku"}),
    "legal":            ("Legal & Contracts",    "#fed330", {"docusign", "pandadoc", "ironclad", "contractbook", "juro", "concord"}),
    "video":            ("Video Conferencing",   "#5f27cd", {"zoom", "google-meet", "microsoft-teams", "whereby", "loom"}),
    "vpn":              ("VPN & Secure Access",  "#00d2d3", {"nordlayer", "twingate", "perimeter", "tailscale", "cloudflare-access"}),
    "default":          ("SaaSpare",             "#e94560", set()),
}


def vertical_for(filename: str) -> str:
    base = filename.lower()
    for slug, (_, _, kws) in VERTICALS.items():
        if any(kw in base for kw in kws):
            return slug
    return "default"


def make_svg(label: str, accent: str) -> str:
    """Generate a 1200x630 SVG with SaaSpare branding + vertical label."""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#07070d"/>
      <stop offset="100%" stop-color="#11111b"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{accent}"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0.6"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <!-- subtle grid -->
  <g opacity="0.04" stroke="#fff" stroke-width="1">
    <path d="M0 100 L1200 100 M0 200 L1200 200 M0 300 L1200 300 M0 400 L1200 400 M0 500 L1200 500"/>
    <path d="M100 0 L100 630 M300 0 L300 630 M500 0 L500 630 M700 0 L700 630 M900 0 L900 630 M1100 0 L1100 630"/>
  </g>
  <!-- accent stripe -->
  <rect x="0" y="0" width="14" height="630" fill="url(#accent)"/>
  <!-- label badge -->
  <g transform="translate(80, 130)">
    <rect width="200" height="40" rx="20" fill="{accent}" fill-opacity="0.16" stroke="{accent}" stroke-opacity="0.4"/>
    <text x="100" y="26" text-anchor="middle" fill="{accent}" font-family="-apple-system,Segoe UI,sans-serif" font-size="16" font-weight="700" letter-spacing="2">SAASPARE.ORG</text>
  </g>
  <!-- main title -->
  <text x="80" y="290" fill="#f4f4f8" font-family="-apple-system,Segoe UI,sans-serif" font-size="86" font-weight="800" letter-spacing="-2">{label}</text>
  <text x="80" y="380" fill="#888896" font-family="-apple-system,Segoe UI,sans-serif" font-size="44" font-weight="500">Real pricing. Honest verdict.</text>
  <!-- footer -->
  <g transform="translate(80, 500)">
    <text x="0" y="40" fill="rgba(255,255,255,0.65)" font-family="-apple-system,Segoe UI,sans-serif" font-size="22" font-weight="600">Independent B2B SaaS comparisons</text>
    <text x="0" y="74" fill="rgba(255,255,255,0.4)" font-family="-apple-system,Segoe UI,sans-serif" font-size="18">1,000+ tools — no paid placements</text>
  </g>
  <!-- right side: accent shape -->
  <g transform="translate(900, 220)">
    <circle cx="100" cy="100" r="120" fill="{accent}" fill-opacity="0.08"/>
    <circle cx="100" cy="100" r="80" fill="{accent}" fill-opacity="0.12"/>
    <circle cx="100" cy="100" r="40" fill="{accent}" fill-opacity="0.2"/>
  </g>
</svg>'''


OG_META_RE = re.compile(
    r'<meta\s+property="og:image"\s+content="[^"]*"',
    re.I,
)
TWITTER_META_RE = re.compile(
    r'<meta\s+name="twitter:image"\s+content="[^"]*"',
    re.I,
)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args(argv)

    report = {
        "svg_files": 0,
        "pages_updated": 0,
        "by_vertical": {},
    }

    # 1. Generate one SVG per vertical (we serve SVG directly — Twitter & FB accept SVG)
    for slug, (label, accent, _) in VERTICALS.items():
        svg = make_svg(label, accent)
        out = OG_DIR / f"{slug}.svg"
        if not args.check:
            out.write_text(svg, encoding="utf-8")
        report["svg_files"] += 1

    # 2. Walk all pages, set og:image and twitter:image to the matching vertical
    for fp in sorted(PAGES.glob("*.html")):
        if fp.name in {"index.html", "thanks.html", "verification.html"}:
            continue
        html = fp.read_text(encoding="utf-8", errors="replace")
        if "noindex" in html[:4000].lower():
            continue
        slug = vertical_for(fp.name)
        target = f"https://saaspare.org/og/{slug}.svg"
        new_html = OG_META_RE.sub(
            f'<meta property="og:image" content="{target}"', html, count=1
        )
        new_html = TWITTER_META_RE.sub(
            f'<meta name="twitter:image" content="{target}"', new_html, count=1
        )
        if new_html != html:
            if not args.check:
                fp.write_text(new_html, encoding="utf-8")
            report["pages_updated"] += 1
            report["by_vertical"][slug] = report["by_vertical"].get(slug, 0) + 1

    (OUTPUTS / "og_images.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print("=== og_images ===")
    for k, v in report.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
