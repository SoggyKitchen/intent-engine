"""
Wave 18: Revenue Infrastructure Completion
- Inject sticky CTAs to all money pages missing them (coupon/pricing/review/deal)
- Add GA4 affiliate_click events to all /go/ links missing tracking
- Skip policy/preview/utility pages
- Update sitemap to include all indexable pages

Run: uv run python scripts/wave18_revenue_completion.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PAGES = SITE / "pages"

# Pages to skip (not money pages)
SKIP_PATTERNS = [
    "v3-preview", "coupon-verification-policy", "report-outdated-pricing",
    "saas-pricing-changes", "weekly-saas-deal-digest", "best-saas-deals-this-week",
    "editorial-policy", "corrections", "privacy", "contact", "about",
    "affiliate-disclosure", "404", "roi-calculator", "shortlist",
    "deal-radar", "homepage", "newsletter", "library",
]

# Tool→affiliate link mapping for sticky CTAs
TOOL_CTA = {
    "ahrefs":        ("/go/ahrefs",          "Try Ahrefs Free",        "ahrefs"),
    "amplitude":     ("/go/amplitude",        "Start Free on Amplitude","amplitude"),
    "asana":         ("/go/asana",            "Try Asana Free",         "asana"),
    "bigcommerce":   ("/go/bigcommerce",      "Try BigCommerce Free",   "bigcommerce"),
    "canva":         ("/go/canva",            "Try Canva Free",         "canva"),
    "clearscope":    ("/go/clearscope",       "Try Clearscope",         "clearscope"),
    "copy-ai":       ("/go/copyai",           "Try Copy.ai Free",       "copy-ai"),
    "datadog":       ("/go/datadog",          "Try Datadog Free",       "datadog"),
    "digitalocean":  ("/go/digitalocean",     "Try DigitalOcean",       "digitalocean"),
    "freshbooks":    ("/go/freshbooks-trial", "Try FreshBooks Free",    "freshbooks"),
    "getresponse":   ("/go/getresponse-email","Try GetResponse Free",   "getresponse"),
    "gusto":         ("/go/gusto",            "Try Gusto Free",         "gusto"),
    "hetzner":       ("/go/hetzner",          "Try Hetzner Cloud",      "hetzner"),
    "linear":        ("/go/linear",           "Try Linear Free",        "linear"),
    "miro":          ("/go/miro",             "Try Miro Free",          "miro"),
    "mixpanel":      ("/go/mixpanel",         "Try Mixpanel Free",      "mixpanel"),
    "moz-pro":       ("/go/moz",              "Try Moz Pro Free",       "moz"),
    "notion":        ("/go/notion",           "Try Notion Free",        "notion"),
    "pandadoc":      ("/go/pandadoc",         "Try PandaDoc Free",      "pandadoc"),
    "pipedrive":     ("/go/pipedrive",        "Try Pipedrive Free",     "pipedrive"),
    "ramp":          ("/go/ramp",             "Try Ramp Free",          "ramp"),
    "salesforce":    ("/go/salesforce",       "Try Salesforce Free",    "salesforce"),
    "se-ranking":    ("/go/seranking",        "Try SE Ranking Free",    "se-ranking"),
    "slack":         ("/go/slack",            "Try Slack Free",         "slack"),
    "stripe":        ("/go/stripe",           "Try Stripe Free",        "stripe"),
    "supabase":      ("/go/supabase",         "Try Supabase Free",      "supabase"),
    "tresorit":      ("/go/tresorit",         "Try Tresorit Free",      "tresorit"),
    "vultr":         ("/go/vultr",            "Try Vultr Cloud",        "vultr"),
    "workable":      ("/go/workable",         "Try Workable Free",      "workable"),
    "zendesk":       ("/go/zendesk",          "Try Zendesk Free",       "zendesk"),
    # Already tracked programs
    "nordvpn":       ("/go/nordvpn",          "Get NordVPN Deal",       "nordvpn"),
    "surfshark":     ("/go/surfshark",        "Get Surfshark Deal",     "surfshark"),
    "nordpass":      ("/go/nordpass",         "Try NordPass Free",      "nordpass"),
    "sucuri":        ("/go/sucuri",           "Protect with Sucuri",    "sucuri"),
    "semrush":       ("/go/semrush",          "Try Semrush Free",       "semrush"),
    "shopify":       ("/go/shopify",          "Start Shopify Trial",    "shopify"),
    "elevenlabs":    ("/go/elevenlabs",       "Try ElevenLabs Free",    "elevenlabs"),
    "contabo":       ("/go/contabo",          "Get Contabo VPS",        "contabo"),
    "hostpapa":      ("/go/hostpapa",         "Try HostPapa Hosting",   "hostpapa"),
    "expressvpn":    ("/go/expressvpn",       "Get ExpressVPN Deal",    "expressvpn"),
    "hubspot":       ("/go/hubspot-crm",      "Try HubSpot Free",       "hubspot"),
    "clickup":       ("/go/clickup-trial",    "Try ClickUp Free",       "clickup"),
    "1password":     ("/go/1password-trial",  "Try 1Password Free",     "1password"),
    "activecampaign":("/go/activecampaign-trial","Try ActiveCampaign",  "activecampaign"),
    "monday":        ("/go/monday",           "Try Monday.com Free",    "monday"),
    "xero":          ("/go/xero-trial",       "Try Xero Free",          "xero"),
    "dashlane":      ("/go/dashlane-trial",   "Try Dashlane Free",      "dashlane"),
    "kajabi":        ("/go/kajabi",           "Start Kajabi Trial",     "kajabi"),
    "teachable":     ("/go/teachable",        "Try Teachable Free",     "teachable"),
    "quickbooks":    ("/go/quickbooks",       "Try QuickBooks Free",    "quickbooks"),
    "bitdefender":   ("/go/bitdefender",      "Try Bitdefender Free",   "bitdefender"),
    "malwarebytes":  ("/go/malwarebytes",     "Try Malwarebytes Free",  "malwarebytes"),
}

def make_sticky_cta(href, label, tool_key):
    """Generate sticky bottom CTA HTML."""
    return f"""
  <!-- Sticky Bottom CTA -->
  <div id="sticky-cta" style="position:fixed;bottom:0;left:0;right:0;z-index:999;background:rgba(5,4,7,0.97);backdrop-filter:blur(12px);border-top:1px solid rgba(255,65,109,0.25);padding:14px 20px;display:flex;align-items:center;justify-content:center;gap:16px;transform:translateY(100%);transition:transform 0.4s ease;" aria-label="Sticky offer bar">
    <span style="color:#a0a0b8;font-size:0.88rem;">Ready to try it?</span>
    <a href="{href}" target="_blank" rel="noopener sponsored"
       onclick="if(window.gtag){{gtag('event','affiliate_click',{{tool:'{tool_key}',placement:'sticky_cta',page:window.location.pathname}});}}"
       style="display:inline-flex;align-items:center;gap:8px;padding:10px 22px;background:linear-gradient(135deg,#ff416d,#ff6b35);color:#fff;font-weight:700;font-size:0.92rem;border-radius:9999px;text-decoration:none;box-shadow:0 4px 20px rgba(255,65,109,0.35);">
      {label} →
    </a>
    <button onclick="document.getElementById('sticky-cta').style.display='none'" style="background:none;border:none;color:#666;cursor:pointer;font-size:1.2rem;padding:4px 8px;" aria-label="Close">&times;</button>
  </div>
  <script>
    (function(){{
      var bar = document.getElementById('sticky-cta');
      if(!bar) return;
      var shown = false;
      window.addEventListener('scroll', function(){{
        if(!shown && window.scrollY > 300){{
          bar.style.transform = 'translateY(0)';
          shown = true;
        }}
      }}, {{passive:true}});
    }})();
  </script>"""


def make_ga4_snippet(tool_key):
    """Generate GA4 affiliate_click event for /go/ links that are missing tracking."""
    return f"""
  <script>
    document.addEventListener('DOMContentLoaded', function() {{
      document.querySelectorAll('a[href^="/go/"]').forEach(function(link) {{
        if (!link.hasAttribute('data-tracked')) {{
          link.setAttribute('data-tracked', '1');
          link.addEventListener('click', function() {{
            if (window.gtag) {{
              gtag('event', 'affiliate_click', {{
                tool: '{tool_key}',
                placement: 'body_link',
                destination: link.href,
                page: window.location.pathname
              }});
            }}
          }});
        }}
      }});
    }});
  </script>"""


def get_tool_key(filename):
    """Extract tool key from filename."""
    name = filename.replace(".html", "")
    # Remove suffixes
    for suffix in ["-pricing-history-2026", "-coupon-2026-discount-codes-promo",
                   "-coupon-code-promo-codes-2026-verified-discounts",
                   "-review-2026", "-pricing-2026", "-pricing",
                   "-promo-codes-2026-verified-deals"]:
        name = name.replace(suffix, "")
    return name


def should_skip(filename):
    for pat in SKIP_PATTERNS:
        if pat in filename:
            return True
    return False


def inject_cta(filepath, href, label, tool_key):
    """Inject sticky CTA before </body> if not present."""
    content = filepath.read_text(encoding="utf-8", errors="replace")
    if "sticky-cta" in content or "sticky_cta" in content:
        return False
    cta = make_sticky_cta(href, label, tool_key)
    new_content = content.replace("</body>", cta + "\n</body>", 1)
    if new_content != content:
        filepath.write_text(new_content, encoding="utf-8")
        return True
    return False


def inject_ga4(filepath, tool_key):
    """Inject GA4 auto-tracker before </body> if not present."""
    content = filepath.read_text(encoding="utf-8", errors="replace")
    if "affiliate_click" in content:
        return False
    snippet = make_ga4_snippet(tool_key)
    new_content = content.replace("</body>", snippet + "\n</body>", 1)
    if new_content != content:
        filepath.write_text(new_content, encoding="utf-8")
        return True
    return False


def main():
    cta_injected = 0
    ga4_injected = 0
    skipped = 0

    money_pages = list(PAGES.glob("*.html"))
    money_pages = [p for p in money_pages if
                   any(kw in p.name for kw in ["review", "pricing", "coupon", "promo", "discount", "deal", "hub"])]

    print(f"Auditing {len(money_pages)} money pages…")

    for fp in sorted(money_pages):
        fname = fp.name

        if should_skip(fname):
            skipped += 1
            continue

        tool_key = get_tool_key(fname)

        # Find matching CTA config
        cta_config = None
        for key, cfg in TOOL_CTA.items():
            if tool_key == key or tool_key.startswith(key):
                cta_config = cfg
                break

        if not cta_config:
            # Generic fallback - use best match
            cta_config = ("/go/saaspare", "Compare Top Tools", tool_key)

        href, label, tk = cta_config

        # Inject sticky CTA if missing
        content = fp.read_text(encoding="utf-8", errors="replace")
        if "sticky-cta" not in content and "sticky_cta" not in content:
            cta_html = make_sticky_cta(href, label, tk)
            new = content.replace("</body>", cta_html + "\n</body>", 1)
            if new != content:
                fp.write_text(new, encoding="utf-8")
                cta_injected += 1
                content = new  # use updated content for next check

        # Inject GA4 if missing
        if "affiliate_click" not in content:
            snippet = make_ga4_snippet(tk)
            new = content.replace("</body>", snippet + "\n</body>", 1)
            if new != content:
                fp.write_text(new, encoding="utf-8")
                ga4_injected += 1

    print(f"Sticky CTAs injected:     {cta_injected}")
    print(f"GA4 events injected:      {ga4_injected}")
    print(f"Skipped (policy/preview): {skipped}")


if __name__ == "__main__":
    main()
