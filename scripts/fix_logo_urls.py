"""Replace broken SimpleIcons logo URLs with real brand logos.

SimpleIcons removed many SaaS brands (Salesforce, Slack, Microsoft, AWS,
Oracle...) for trademark reasons, so ~200 slugs the generators emit return
404 and pages fall back to letter badges. This sweep rewrites every broken
cdn.simpleicons.org URL to Google's favicon service, which serves the real
brand mark for any live domain. Slugs that aren't real brands (page-title
junk like "crm" or "openclaw-vs-omlx") are left alone — the onerror letter
badge handles those. Runs nightly after generation; safe to re-run.
"""
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"

# broken simpleicons slug -> brand domain (real logo via google favicon svc)
SLUG_DOMAIN = {
    "1password-business": "1password.com",
    "activecampaign": "activecampaign.com",
    "adobe-express": "adobe.com",
    "adobeexpress": "adobe.com",
    "affilae": "affilae.com",
    "agiloft": "agiloft.com",
    "ahrefs": "ahrefs.com",
    "airbase": "airbase.com",
    "amazon": "amazon.com",
    "amazonaws": "aws.amazon.com",
    "aws": "aws.amazon.com",
    "amplitude": "amplitude.com",
    "anthropic-claude": "anthropic.com",
    "anthropicclaude": "anthropic.com",
    "around": "around.co",
    "aweber": "aweber.com",
    "bamboohr": "bamboohr.com",
    "bill": "bill.com",
    "bill-com": "bill.com",
    "billcom": "bill.com",
    "boldcommerce": "boldcommerce.com",
    "canva": "canva.com",
    "capterra": "capterra.com",
    "chargebee": "chargebee.com",
    "cisco-anyconnect": "cisco.com",
    "ciscoanyconnect": "cisco.com",
    "clearscope": "clearscope.io",
    "close": "close.com",
    "cloudflare-access": "cloudflare.com",
    "cloudflareaccess": "cloudflare.com",
    "cohere": "cohere.com",
    "concord": "concordnow.com",
    "conga": "conga.com",
    "contractbook": "contractbook.com",
    "convertkit": "kit.com",
    "copper": "copper.com",
    "copy-ai": "copy.ai",
    "copyai": "copy.ai",
    "crowdstrike": "crowdstrike.com",
    "culture-amp": "cultureamp.com",
    "cultureamp": "cultureamp.com",
    "cyberghost": "cyberghostvpn.com",
    "cyberghostvpn": "cyberghostvpn.com",
    "databox": "databox.com",
    "deel": "deel.com",
    "descript": "descript.com",
    "divvy": "bill.com",
    "docusign": "docusign.com",
    "docusign-clm": "docusign.com",
    "docusignclm": "docusign.com",
    "drip": "drip.com",
    "duo": "duo.com",
    "duo-security": "duo.com",
    "expressvpn-business": "expressvpn.com",
    "expressvpnbusiness": "expressvpn.com",
    "figma-figjam": "figma.com",
    "figmafigjam": "figma.com",
    "firstpromoter": "firstpromoter.com",
    "frase": "frase.io",
    "fraseio": "frase.io",
    "freshbooks": "freshbooks.com",
    "freshdesk": "freshdesk.com",
    "freshsales": "freshworks.com",
    "freshworks": "freshworks.com",
    "fullstory": "fullstory.com",
    "getresponse": "getresponse.com",
    "github-copilot": "github.com",
    "github-issues": "github.com",
    "githubissues": "github.com",
    "google-chat": "google.com",
    "google-drive": "google.com",
    "google-jamboard": "google.com",
    "googlejamboard": "google.com",
    "google-meet": "google.com",
    "google-search-console": "google.com",
    "gorgias": "gorgias.com",
    "heap": "heap.io",
    "help-scout": "helpscout.com",
    "hubspot-service-hub": "hubspot.com",
    "hubspotcrm": "hubspot.com",
    "hubspotservicehub": "hubspot.com",
    "hugging-face": "huggingface.co",
    "icertis": "icertis.com",
    "impact-com": "impact.com",
    "impactcom": "impact.com",
    "insightly": "insightly.com",
    "ironclad": "ironcladapp.com",
    "jasper": "jasper.ai",
    "jasper-ai": "jasper.ai",
    "juro": "juro.com",
    "kajabi": "kajabi.com",
    "keap": "keap.com",
    "keepersecurity": "keepersecurity.com",
    "klaviyo": "klaviyo.com",
    "lattice": "lattice.com",
    "leaddyno": "leaddyno.com",
    "lever": "lever.co",
    "linode": "linode.com",
    "lucidspark": "lucidspark.com",
    "mangools": "mangools.com",
    "marketmuse": "marketmuse.com",
    "marketo": "marketo.com",
    "mercury": "mercury.com",
    "microsoft-designer": "microsoft.com",
    "microsoftdesigner": "microsoft.com",
    "microsoft-teams": "microsoft.com",
    "microsoftteams": "microsoft.com",
    "microsoft-whiteboard": "microsoft.com",
    "microsoftwhiteboard": "microsoft.com",
    "monday": "monday.com",
    "monday-com": "monday.com",
    "mondaydotcom": "monday.com",
    "mondotv": "monday.com",
    "moz": "moz.com",
    "moz-pro": "moz.com",
    "murf-ai": "murf.ai",
    "netsuite": "netsuite.com",
    "new-relic": "newrelic.com",
    "nordlayer": "nordlayer.com",
    "nordpass": "nordpass.com",
    "nutshell": "nutshell.com",
    "onedrive": "microsoft.com",
    "openai": "openai.com",
    "openai-api": "openai.com",
    "openaiapi": "openai.com",
    "oracle": "oracle.com",
    "pandadoc": "pandadoc.com",
    "pardot": "salesforce.com",
    "partnerstack": "partnerstack.com",
    "passwordboss": "passwordboss.com",
    "pendo": "pendo.io",
    "perimeter-81": "perimeter81.com",
    "perimeter81": "perimeter81.com",
    "piktochart": "piktochart.com",
    "pinecone": "pinecone.io",
    "pipedrive": "pipedrive.com",
    "post-affiliate-pro": "postaffiliatepro.com",
    "postaffiliatepro": "postaffiliatepro.com",
    "power-bi": "microsoft.com",
    "powerbi": "microsoft.com",
    "ramp": "ramp.com",
    "rankmath": "rankmath.com",
    "recharge": "rechargepayments.com",
    "recurly": "recurly.com",
    "refersion": "refersion.com",
    "remote-com": "remote.com",
    "remotecom": "remote.com",
    "rewardful": "rewardful.com",
    "rippling": "rippling.com",
    "riverside-fm": "riverside.fm",
    "riversidefm": "riverside.fm",
    "roboform": "roboform.com",
    "salesforce": "salesforce.com",
    "screaming-frog": "screamingfrog.co.uk",
    "se-ranking": "seranking.com",
    "seranking": "seranking.com",
    "segment": "segment.com",
    "sentinelone": "sentinelone.com",
    "slack": "slack.com",
    "smartsheet": "smartsheet.com",
    "spendesk": "spendesk.com",
    "spyfu": "spyfu.com",
    "stickypassword": "stickypassword.com",
    "streamyard": "streamyard.com",
    "sucuri": "sucuri.net",
    "surfer-seo": "surferseo.com",
    "surferseo": "surferseo.com",
    "sync-com": "sync.com",
    "synccom": "sync.com",
    "tableau": "tableau.com",
    "tapfiliate": "tapfiliate.com",
    "teachable": "teachable.com",
    "tenable": "tenable.com",
    "tune": "tune.com",
    "twingate": "twingate.com",
    "ubersuggest": "neilpatel.com",
    "visme": "visme.co",
    "wave": "waveapps.com",
    "weaviate": "weaviate.io",
    "weights-biases": "wandb.ai",
    "weightsbiases": "wandb.ai",
    "whereby": "whereby.com",
    "workable": "workable.com",
    "workday": "workday.com",
    "wrike": "wrike.com",
    "writesonic": "writesonic.com",
    "zscaler": "zscaler.com",
    # page-title junk slugs where the underlying tool is identifiable
    "best-devtools-for-ai-agent-development-in-2025-ollama": "ollama.com",
    "bestdevtoolsforaiagentdevelopmentin2025ollama": "ollama.com",
    "best-open-source-iac-and-cloud-storage-tools-in-2025-opentofu": "opentofu.org",
    "bestopensourceiacandcloudstoragetoolsin2025opentofu": "opentofu.org",
    "terraform-minio-alternatives": "min.io",
    "terraformminioalternatives": "min.io",
}

URL_RE = re.compile(
    r"https://cdn\.simpleicons\.org/([a-z0-9\-\.#%]+)(?:/[0-9a-fA-F]{3,8})?"
)


def favicon(domain: str) -> str:
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=128"


def fix_html(html: str) -> tuple[str, int]:
    n = 0

    def sub(m: re.Match) -> str:
        nonlocal n
        domain = SLUG_DOMAIN.get(m.group(1))
        if not domain:
            return m.group(0)
        n += 1
        return favicon(domain)

    return URL_RE.sub(sub, html), n


def main() -> int:
    files = total = 0
    for p in SITE.rglob("*.html"):
        html = p.read_text(encoding="utf-8", errors="ignore")
        out, n = fix_html(html)
        if n:
            p.write_text(out, encoding="utf-8")
            files += 1
            total += n
    print(f"fix_logo_urls: replaced {total} logo URLs across {files} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
