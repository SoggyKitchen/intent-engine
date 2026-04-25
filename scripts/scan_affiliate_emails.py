"""
Scans Gmail for affiliate-related emails and extracts:
  - Approval emails (subject contains "welcome to", "approved", "accepted")
  - Tracking links / affiliate URLs
  - Program names

Outputs:
  - data/affiliate_inbox.json — structured list of opportunities
  - data/affiliate_inbox.md   — human-readable summary

Authentication:
  Uses GMAIL_REFRESH_TOKEN, GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET env vars.
  See docs/gmail_setup.md for one-time setup.

Run: .venv/Scripts/python scripts/scan_affiliate_emails.py
Cron: Add to .github/workflows/programmatic.yml as a daily step.
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    print("Install: pip install google-api-python-client google-auth")
    sys.exit(1)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

KEYWORDS = [
    "welcome to", "approved", "accepted", "affiliate program",
    "partner program", "publisher", "tracking link", "commission",
    "your application", "you're in", "you have been approved",
]

REJECT_KEYWORDS = ["rejected", "declined", "not approved", "unable to approve"]

PROGRAMS_OF_INTEREST = [
    "semrush", "ahrefs", "notion", "monday", "clickup", "asana", "canva",
    "shopify", "wordpress", "wpengine", "kinsta", "cloudways", "bluehost",
    "hubspot", "pipedrive", "freshbooks", "xero", "quickbooks", "linear",
    "airtable", "webflow", "framer", "loom", "calendly", "zoom",
    "1password", "lastpass", "nordvpn", "expressvpn", "protonvpn",
    "datadog", "mixpanel", "amplitude", "intercom", "zendesk",
    "convertkit", "mailchimp", "activecampaign", "getresponse",
]


def load_creds():
    refresh = os.environ.get("GMAIL_REFRESH_TOKEN")
    client_id = os.environ.get("GMAIL_CLIENT_ID")
    client_secret = os.environ.get("GMAIL_CLIENT_SECRET")
    if not all([refresh, client_id, client_secret]):
        print("Missing GMAIL_* env vars — see docs/gmail_setup.md")
        sys.exit(1)
    return Credentials(
        None,
        refresh_token=refresh,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )


def extract_links(body: str) -> list[str]:
    urls = re.findall(r'https?://[^\s<>"\']+', body)
    affiliate_patterns = ["click", "track", "ref", "aff", "partner", "/r/", "go.", "?id=", "tracking"]
    return [u for u in urls if any(p in u.lower() for p in affiliate_patterns)][:5]


def extract_program_name(subject: str, body: str) -> str | None:
    text = (subject + " " + body[:500]).lower()
    for prog in PROGRAMS_OF_INTEREST:
        if prog in text:
            return prog
    m = re.search(r'welcome to (?:the )?([^\.!\n]+?)(?:\s+affiliate|\s+partner|!|\.)', subject, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None


def scan():
    creds = load_creds()
    service = build("gmail", "v1", credentials=creds)

    cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y/%m/%d")
    query = f'after:{cutoff} (affiliate OR "partner program" OR "welcome to" OR commission)'

    results = service.users().messages().list(userId="me", q=query, maxResults=100).execute()
    messages = results.get("messages", [])

    opportunities = []
    rejections = []

    for msg in messages:
        full = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        headers = {h["name"]: h["value"] for h in full["payload"].get("headers", [])}
        subject = headers.get("Subject", "")
        sender = headers.get("From", "")
        date = headers.get("Date", "")

        body = ""
        parts = full["payload"].get("parts", [full["payload"]])
        for p in parts:
            if p.get("mimeType", "").startswith("text/"):
                import base64
                data = p.get("body", {}).get("data", "")
                if data:
                    try:
                        body += base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="ignore")
                    except Exception:
                        pass

        subj_lower = subject.lower()
        body_snippet = body[:1000].lower()

        is_rejection = any(k in subj_lower or k in body_snippet for k in REJECT_KEYWORDS)
        is_opportunity = any(k in subj_lower for k in KEYWORDS)

        program = extract_program_name(subject, body)
        links = extract_links(body)

        record = {
            "id": msg["id"],
            "subject": subject,
            "from": sender,
            "date": date,
            "program": program,
            "links": links,
        }

        if is_rejection:
            rejections.append(record)
        elif is_opportunity:
            opportunities.append(record)

    out = {
        "scanned_at": datetime.now().isoformat(),
        "approved_count": len(opportunities),
        "rejected_count": len(rejections),
        "opportunities": opportunities,
        "rejections": rejections,
    }

    (DATA_DIR / "affiliate_inbox.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    md = [f"# Affiliate Inbox Scan ({out['scanned_at']})\n"]
    md.append(f"**Approved/Opportunities:** {len(opportunities)} | **Rejected:** {len(rejections)}\n")
    md.append("## Approved Programs / Opportunities\n")
    for o in opportunities:
        md.append(f"- **{o['program'] or 'Unknown'}** — {o['subject']}")
        md.append(f"  - From: {o['from']}")
        if o['links']:
            md.append(f"  - Links: {', '.join(o['links'][:2])}")
        md.append("")
    md.append("\n## Rejections (need follow-up)\n")
    for r in rejections:
        md.append(f"- **{r['program'] or 'Unknown'}** — {r['subject']}")
        md.append(f"  - From: {r['from']}")
    (DATA_DIR / "affiliate_inbox.md").write_text("\n".join(md), encoding="utf-8")

    print(f"Scanned. {len(opportunities)} opportunities, {len(rejections)} rejections")
    print(f"Output: data/affiliate_inbox.json + .md")


if __name__ == "__main__":
    scan()
