"""
ONE-TIME SETUP: Generate a GSC OAuth refresh token and push it to GitHub secrets.

Usage:
  1. Download your OAuth 2.0 client JSON from Google Cloud Console (see instructions below)
  2. Place it at the repo root as: client_secret.json
  3. Run:  uv run python scripts/setup_gsc_oauth.py

What this script does:
  - Opens your browser to Google's consent screen
  - You log in with the Google account that OWNS saaspare.org in Search Console
  - Captures the refresh token automatically via a local redirect server
  - Updates GitHub secrets: GSC_OAUTH_CLIENT_ID, GSC_OAUTH_CLIENT_SECRET,
    GSC_OAUTH_REFRESH_TOKEN (and removes the old GSC_SERVICE_ACCOUNT_JSON)
  - Tests the connection with a live GSC query to confirm it works

HOW TO GET client_secret.json (2 minutes):
  1. Go to: https://console.cloud.google.com/apis/credentials
     (create a project if you haven't — call it "saaspare")
  2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
  3. Application type: "Desktop app", name: "saaspare-gsc"
  4. Click Create → then "Download JSON"
  5. Rename the downloaded file to client_secret.json
  6. Move it to this repo's root folder (same folder as CLAUDE.md)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT_SECRET_FILE = ROOT / "client_secret.json"
SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
REDIRECT_PORT = 8765
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"

# Will be set by the callback handler
_auth_code: str | None = None
_server_error: str | None = None


class _OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code, _server_error
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            _auth_code = params["code"][0]
            msg = b"<h2>Authorised! You can close this tab.</h2>"
            self.send_response(200)
        elif "error" in params:
            _server_error = params["error"][0]
            msg = f"<h2>Error: {_server_error}. Close this tab.</h2>".encode()
            self.send_response(400)
        else:
            msg = b"<h2>Unexpected request.</h2>"
            self.send_response(400)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(msg)

    def log_message(self, *args):  # silence access logs
        pass


def _run_server(server: HTTPServer):
    server.handle_request()  # handle exactly one request then stop


def exchange_code(client_id: str, client_secret: str, code: str) -> dict:
    data = urllib.parse.urlencode({
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }).encode()
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def test_gsc(client_id: str, client_secret: str, refresh_token: str) -> bool:
    """Quick test: refresh the access token and hit the GSC API."""
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req) as resp:
        tokens = json.loads(resp.read())
    access_token = tokens["access_token"]

    # List properties to confirm access
    req2 = urllib.request.Request(
        "https://www.googleapis.com/webmasters/v3/sites",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    with urllib.request.urlopen(req2) as resp2:
        sites = json.loads(resp2.read())
    site_urls = [s["siteUrl"] for s in sites.get("siteEntry", [])]
    print(f"  GSC properties found: {site_urls}")
    return any("saaspare" in s.lower() for s in site_urls)


def gh_set_secret(name: str, value: str):
    result = subprocess.run(
        ["gh", "secret", "set", name, "--body", value],
        capture_output=True, text=True, cwd=ROOT,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh secret set {name} failed: {result.stderr}")
    print(f"  ✓ GitHub secret updated: {name}")


def main():
    if not CLIENT_SECRET_FILE.exists():
        print(f"""
ERROR: client_secret.json not found at {CLIENT_SECRET_FILE}

Quick steps to get it:
  1. Open: https://console.cloud.google.com/apis/credentials
  2. Create Credentials → OAuth 2.0 Client IDs → Desktop app → name it 'saaspare-gsc'
  3. Download JSON → rename to client_secret.json
  4. Move to: {ROOT}
  5. Run this script again
""")
        sys.exit(1)

    secrets = json.loads(CLIENT_SECRET_FILE.read_text())
    # Google downloads two possible formats
    info = secrets.get("installed") or secrets.get("web") or {}
    client_id = info.get("client_id") or secrets.get("client_id")
    client_secret = info.get("client_secret") or secrets.get("client_secret")
    if not client_id or not client_secret:
        print("ERROR: Could not find client_id/client_secret in client_secret.json")
        sys.exit(1)

    print("=== SaaSpare GSC OAuth Setup ===\n")
    print("1. Opening Google OAuth consent in your browser...")
    print("   Sign in with the Google account that OWNS saaspare.org in Search Console.\n")

    params = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",  # force refresh_token to be returned
    })
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{params}"

    server = HTTPServer(("localhost", REDIRECT_PORT), _OAuthHandler)
    thread = threading.Thread(target=_run_server, args=(server,), daemon=True)
    thread.start()

    webbrowser.open(auth_url)
    print("   Waiting for you to authorize in the browser...")
    thread.join(timeout=120)

    if _server_error:
        print(f"\nERROR during OAuth: {_server_error}")
        sys.exit(1)
    if not _auth_code:
        print("\nERROR: Timed out waiting for authorization. Try again.")
        sys.exit(1)

    print("\n2. Exchanging authorization code for tokens...")
    tokens = exchange_code(client_id, client_secret, _auth_code)
    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        print("ERROR: No refresh_token in response. Make sure you used 'prompt=consent' (already set).")
        print(f"Full response: {tokens}")
        sys.exit(1)
    print(f"   ✓ Got refresh_token: {refresh_token[:20]}...")

    print("\n3. Testing GSC connection...")
    try:
        found = test_gsc(client_id, client_secret, refresh_token)
        if found:
            print("   ✓ saaspare.org found in GSC properties — connection confirmed!")
        else:
            print("   ⚠ Connected but saaspare.org not listed. Check the account has SC access.")
    except Exception as exc:
        print(f"   ⚠ Test failed: {exc}. The tokens may still work — continuing.")

    print("\n4. Updating GitHub secrets...")
    try:
        gh_set_secret("GSC_OAUTH_CLIENT_ID", client_id)
        gh_set_secret("GSC_OAUTH_CLIENT_SECRET", client_secret)
        gh_set_secret("GSC_OAUTH_REFRESH_TOKEN", refresh_token)
        # Override the site URL to the correct domain-property format
        gh_set_secret("GSC_SITE_URL", "sc-domain:saaspare.org")
        print("\n   ✓ All 4 secrets updated.")
    except Exception as exc:
        print(f"\nERROR updating secrets: {exc}")
        print("\nManually set these in GitHub → Settings → Secrets → Actions:")
        print(f"  GSC_OAUTH_CLIENT_ID     = {client_id}")
        print(f"  GSC_OAUTH_CLIENT_SECRET = {client_secret}")
        print(f"  GSC_OAUTH_REFRESH_TOKEN = {refresh_token}")
        print(f"  GSC_SITE_URL            = sc-domain:saaspare.org")
        sys.exit(1)

    print("""
=== Done! ===

The daily agent will now pull live GSC data every morning.
Trigger a manual run to see the live revenue opportunities right now:

  gh workflow run saaspare_seo_agent.yml

Then pull the results:
  git pull && cat seo/reports/revenue-opportunities.md
""")

    # Clean up: remove client_secret.json (shouldn't be committed)
    print("Removing client_secret.json from disk (keep it safe, don't commit it)...")
    CLIENT_SECRET_FILE.unlink()
    print("Done.")


if __name__ == "__main__":
    main()
