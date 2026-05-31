"""
Send HTML email via Gmail SMTP.
Reads HTML from stdin (first line = SUBJECT:... header).

Required env vars:
  GMAIL_USER     — your Gmail address (e.g. smithelly30121@gmail.com)
  GMAIL_APP_PASS — Gmail App Password (16-char, no spaces)
  REPORT_TO      — recipient email (default: same as GMAIL_USER)

Usage:
  python scripts/generate_email_report.py --mode daily | python scripts/send_email_report.py
"""
import os, sys, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_USER     = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASS = os.environ.get("GMAIL_APP_PASS", "")
REPORT_TO      = os.environ.get("REPORT_TO", GMAIL_USER)

if not GMAIL_USER or not GMAIL_APP_PASS:
    print("ERROR: GMAIL_USER and GMAIL_APP_PASS env vars required")
    sys.exit(1)

lines = sys.stdin.read().splitlines()

subject = "SaaSpare CEO Brief"
html_lines = []
for i, line in enumerate(lines):
    if line.startswith("SUBJECT:"):
        subject = line[8:].strip()
    else:
        html_lines.append(line)

html_body = "\n".join(html_lines)

msg = MIMEMultipart("alternative")
msg["Subject"] = subject
msg["From"]    = f"SaaSpare CEO Bot <{GMAIL_USER}>"
msg["To"]      = REPORT_TO
msg.attach(MIMEText(html_body, "html", "utf-8"))

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASS)
        server.sendmail(GMAIL_USER, REPORT_TO, msg.as_string())
    print(f"Email sent to {REPORT_TO}: {subject}")
except Exception as e:
    print(f"Email send failed: {e}")
    sys.exit(1)
