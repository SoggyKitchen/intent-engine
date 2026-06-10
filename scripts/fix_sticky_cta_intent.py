"""
Fix intent-mismatched sticky CTAs (wave19b injected a hardcoded /go/semrush
sticky bar on 185 pages regardless of topic — a Notion page pushing Semrush
converts at ~0% and burns trust).

For every page with the generic "Find the best tool for your needs" sticky:
  - detect the page's actual tool by matching /go/* slugs from _redirects
    against the page filename (longest match wins)
  - tool found + /go/ route exists -> retarget the sticky to that tool:
      "Try <Tool> free" -> /go/<slug>  (rel sponsored, GA4 event keeps firing)
  - no tool route -> point the sticky at the /pages/ comparison hub instead
    (internal link, drop rel=sponsored — it is not an affiliate link)

Idempotent: pages already retargeted are skipped.
Run: uv run python scripts/fix_sticky_cta_intent.py
"""
import re
from pathlib import Path

ROOT  = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"

GENERIC_SPAN = "Find the best tool for your needs"

# Pages genuinely about Semrush keep their Semrush CTA.
def load_go_slugs() -> list[str]:
    slugs = []
    for line in (ROOT / "site" / "_redirects").read_text(encoding="utf-8-sig").splitlines():
        m = re.match(r"^/go/([a-z0-9-]+)\s+\S+", line.strip())
        if m:
            slugs.append(m.group(1))
    # longest first so "1password-business" beats "1password"
    return sorted(set(slugs), key=len, reverse=True)


def tool_for_page(stem: str, go_slugs: list[str]) -> str | None:
    """Longest /go/ slug whose hyphen-bounded form appears in the filename."""
    padded = f"-{stem}-"
    for slug in go_slugs:
        if f"-{slug}-" in padded:
            return slug
        # trial/coupon route variants: match base tool name too
        base = re.sub(r"-(trial|coupon|crm)$", "", slug)
        if base != slug and f"-{base}-" in padded:
            return slug
    return None


def pretty(slug: str) -> str:
    base = re.sub(r"-(trial|coupon|crm)$", "", slug)
    special = {"hubspot": "HubSpot", "clickup": "ClickUp", "activecampaign":
               "ActiveCampaign", "getresponse": "GetResponse", "freshbooks":
               "FreshBooks", "nordvpn": "NordVPN", "nordpass": "NordPass",
               "monday": "Monday.com", "moz-pro": "Moz Pro",
               "1password": "1Password", "copy-ai": "Copy.ai",
               "elevenlabs": "ElevenLabs", "se-ranking": "SE Ranking"}
    return special.get(base, base.replace("-", " ").title())


def retarget(html: str, stem: str, go_slugs: list[str]) -> str | None:
    if GENERIC_SPAN not in html:
        return None
    tool = tool_for_page(stem, go_slugs)
    if tool and tool != "semrush" and "semrush" not in stem:
        name = pretty(tool)
        html = html.replace(
            f'<span style="color:#a0a0b8;font-size:.88rem;">{GENERIC_SPAN}</span>',
            f'<span style="color:#a0a0b8;font-size:.88rem;">Ready to try {name}?</span>')
        html = html.replace('href="/go/semrush" target="_blank" rel="noopener sponsored"',
                            f'href="/go/{tool}" target="_blank" rel="noopener sponsored"')
        html = html.replace("{tool:'semrush',placement:'sticky_cta'",
                            f"{{tool:'{tool}',placement:'sticky_cta'")
        html = html.replace("Compare Top Tools &rarr;", f"Try {name} &rarr;")
        return html
    if not tool and "semrush" not in stem:
        # No affiliate route for this topic — internal hub link, not sponsored
        html = html.replace('href="/go/semrush" target="_blank" rel="noopener sponsored"',
                            'href="/pages/" rel="noopener"')
        html = html.replace("{tool:'semrush',placement:'sticky_cta'",
                            "{tool:'hub',placement:'sticky_cta'")
        return html
    return None  # semrush page — already correct


if __name__ == "__main__":
    go_slugs = load_go_slugs()
    changed = 0
    for fp in sorted(PAGES.glob("*.html")):
        html = fp.read_text(encoding="utf-8", errors="replace")
        new = retarget(html, fp.stem, go_slugs)
        if new and new != html:
            fp.write_text(new, encoding="utf-8")
            changed += 1
    print(f"Sticky CTAs retargeted: {changed}")
