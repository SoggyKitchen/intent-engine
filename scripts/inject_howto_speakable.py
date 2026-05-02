"""Add HowTo schema on shortlist/deal-radar/stack-audit + Speakable schema on top pages.

Idempotent via marker comments.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DOMAIN = "https://saaspare.org"


def howto(url: str, name: str, description: str, steps: list[dict]) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": name,
        "description": description,
        "url": url,
        "totalTime": "PT5M",
        "step": [
            {"@type": "HowToStep", "position": i + 1, "name": s["name"], "text": s["text"]}
            for i, s in enumerate(steps)
        ],
    }
    return f'<script type="application/ld+json">{json.dumps(data, separators=(",", ":"))}</script>'


def speakable(url: str, name: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": name,
        "url": url,
        "speakable": {
            "@type": "SpeakableSpecification",
            "cssSelector": ["h1", ".page-sub", ".page-eyebrow"],
        },
    }
    return f'<script type="application/ld+json">{json.dumps(data, separators=(",", ":"))}</script>'


HOWTO_TARGETS = {
    "shortlist.html": {
        "marker": "<!-- howto-v1 -->",
        "name": "How to build a SaaS shortlist in under 5 minutes",
        "description": "Rank tools by fit, team size and budget before trialling anything.",
        "url": f"{DOMAIN}/shortlist",
        "steps": [
            {"name": "Pick your category", "text": "Choose the software category you need a tool for (CRM, SEO, Dev, HR, etc.)."},
            {"name": "Select team size", "text": "Tell SaaSpare whether you are a solo operator, an SMB (2-50 seats), or a mid-market team (50-500 seats)."},
            {"name": "Set your budget", "text": "Pick a monthly budget band (free, under $50, $50-$200, or $200+)."},
            {"name": "Review the ranked shortlist", "text": "Get 3-5 tools ranked by fit, with an honest verdict, tags and direct trial links."},
            {"name": "Compare or trial", "text": "Open each tool's full comparison page or start the vendor-direct free trial without giving payment details where possible."},
        ],
    },
    "deal-radar.html": {
        "marker": "<!-- howto-v1 -->",
        "name": "How to find the right SaaS free trial or deal",
        "description": "Use Deal Radar to discover the cheapest, safest onramp for any B2B SaaS tool.",
        "url": f"{DOMAIN}/deal-radar",
        "steps": [
            {"name": "Search for a tool or category", "text": "Type the vendor name or category into Deal Radar."},
            {"name": "Check the trial terms", "text": "Review how long the trial is, whether it needs a credit card, and whether it converts to a paid plan automatically."},
            {"name": "Compare to alternatives", "text": "SaaSpare surfaces 2-3 alternatives with better trial terms where applicable."},
            {"name": "Start the trial via a vendor-direct link", "text": "We link straight to the vendor's signup, not a paid review page."},
        ],
    },
    "pages/saas-stack-audit-checkout.html": {
        "marker": "<!-- howto-v1 -->",
        "name": "How the SaaSpare Stack Audit works",
        "description": "A flat-fee audit that finds 3x the audit cost in recoverable annual SaaS savings.",
        "url": f"{DOMAIN}/pages/saas-stack-audit-checkout",
        "steps": [
            {"name": "Choose a tier", "text": "Pick Stack Brief ($29 DIY toolkit), Stack Audit ($99 manual review) or Stack Concierge ($299 done-for-you)."},
            {"name": "Submit your stack", "text": "Paste your current SaaS subscriptions and renewal dates into the intake form. NDA optional."},
            {"name": "Receive your audit report", "text": "We return a 20-page ranked savings report (PDF + CSV) with recommended renegotiations, switches and cancellations."},
            {"name": "Act on the savings", "text": "Follow the renewal scripts and renegotiation templates to unlock savings, with a money-back guarantee if we can't find 3x the audit cost."},
        ],
    },
}

SPEAKABLE_TARGETS = {
    "index.html": "SaaSpare",
    "shortlist.html": "SaaSpare Shortlist Builder",
    "deal-radar.html": "SaaSpare Deal Radar",
    "about.html": "About SaaSpare",
    "pages/saas-stack-audit-checkout.html": "SaaSpare Stack Audit",
    "pages/index.html": "SaaSpare Comparison Library",
}


def inject(path: Path, marker: str, block: str) -> bool:
    html = path.read_text(encoding="utf-8")
    if marker in html:
        return False
    if "</head>" not in html:
        return False
    html = html.replace("</head>", f"{marker}{block}\n</head>", 1)
    path.write_text(html, encoding="utf-8")
    return True


def main():
    n = 0
    for rel, cfg in HOWTO_TARGETS.items():
        p = SITE / rel
        if not p.exists():
            continue
        block = howto(cfg["url"], cfg["name"], cfg["description"], cfg["steps"])
        if inject(p, cfg["marker"], block):
            n += 1
            print(f"howto    {rel}")

    for rel, name in SPEAKABLE_TARGETS.items():
        p = SITE / rel
        if not p.exists():
            continue
        url = f"{DOMAIN}/{rel.replace('index.html', '').replace('.html', '')}".rstrip("/")
        block = speakable(url or f"{DOMAIN}/", name)
        if inject(p, "<!-- speakable-v1 -->", block):
            n += 1
            print(f"speakable {rel}")
    print(f"injected {n} schema blocks")


if __name__ == "__main__":
    main()
