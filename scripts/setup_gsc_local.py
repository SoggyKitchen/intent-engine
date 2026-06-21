"""
GSC Local OAuth Setup — run once to wire GSC credentials into .env

Usage:
    uv run python scripts/setup_gsc_local.py

You will need:
  - OAuth 2.0 Client ID and Secret from Google Cloud Console
    (console.cloud.google.com → APIs & Services → Credentials → your OAuth 2.0 Client)
  - The OAuth app must have "https://www.googleapis.com/auth/webmasters.readonly" scope
  - Redirect URI "http://localhost:8765" must be listed in the OAuth client's Authorized redirect URIs

What it does:
  1. Prompts for client_id and client_secret
  2. Opens your browser to Google's OAuth consent screen
  3. Starts a local HTTP server to capture the auth code
  4. Exchanges the code for tokens
  5. Writes GSC_OAUTH_CLIENT_ID, GSC_OAUTH_CLIENT_SECRET, GSC_OAUTH_REFRESH_TOKEN,
     and GSC_SITE_URL into your .env file
"""

import http.server
import json
import os
import threading
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

REDIRECT_URI = "http://localhost:8765"
SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
ENV_FILE = Path(__file__).parent.parent / ".env"

_auth_code: str | None = None
_server_done = threading.Event()


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            _auth_code = params["code"][0]
            body = b"<h2>Auth complete. You can close this tab.</h2>"
        else:
            error = params.get("error", ["unknown"])[0]
            body = f"<h2>Error: {error}</h2>".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body)
        _server_done.set()

    def log_message(self, *args):
        pass


def _run_server():
    server = http.server.HTTPServer(("localhost", 8765), _CallbackHandler)
    server.handle_request()


def _build_auth_url(client_id: str) -> str:
    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
    }
    return AUTH_URL + "?" + urllib.parse.urlencode(params)


def _exchange_code(client_id: str, client_secret: str, code: str) -> dict:
    data = urllib.parse.urlencode({
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _update_env(key: str, value: str):
    """Upsert a key=value line in .env without touching other lines."""
    text = ENV_FILE.read_text(encoding="utf-8") if ENV_FILE.exists() else ""
    lines = text.splitlines(keepends=True)
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}=") or line.startswith(f"{key} ="):
            lines[i] = f"{key}={value}\n"
            found = True
            break
    if not found:
        if lines and not lines[-1].endswith("\n"):
            lines.append("\n")
        lines.append(f"{key}={value}\n")
    ENV_FILE.write_text("".join(lines), encoding="utf-8")


def main():
    print("\n=== SaaSpare GSC Local OAuth Setup ===\n")
    print("Step 1 — Get your OAuth 2.0 credentials from Google Cloud Console:")
    print("  console.cloud.google.com → APIs & Services → Credentials")
    print("  Find (or create) an OAuth 2.0 Client ID of type 'Desktop app' or 'Web application'.")
    print(f"  Add '{REDIRECT_URI}' as an Authorised redirect URI if it's a Web app client.\n")

    client_id = input("Paste your Client ID: ").strip()
    client_secret = input("Paste your Client Secret: ").strip()

    if not client_id or not client_secret:
        print("Aborted — both values are required.")
        return

    print("\nStep 2 — Starting local callback server on port 8765...")
    t = threading.Thread(target=_run_server, daemon=True)
    t.start()

    auth_url = _build_auth_url(client_id)
    print(f"Step 3 — Opening browser for Google consent. Log in with smithelly30121@gmail.com.\n")
    webbrowser.open(auth_url)

    print("Waiting for OAuth callback...")
    _server_done.wait(timeout=120)

    if not _auth_code:
        print("Timed out or error — no auth code received.")
        return

    print("Step 4 — Exchanging code for tokens...")
    try:
        tokens = _exchange_code(client_id, client_secret, _auth_code)
    except Exception as exc:
        print(f"Token exchange failed: {exc}")
        return

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        print("No refresh_token in response. Make sure 'access_type=offline' and 'prompt=consent'.")
        print(f"Full response: {tokens}")
        return

    print("Step 5 — Writing credentials to .env ...")
    _update_env("GSC_OAUTH_CLIENT_ID", client_id)
    _update_env("GSC_OAUTH_CLIENT_SECRET", client_secret)
    _update_env("GSC_OAUTH_REFRESH_TOKEN", refresh_token)
    _update_env("GSC_SITE_URL", "sc-domain:saaspare.org")

    print("\n✓ Done. Credentials written to .env:")
    print(f"  GSC_OAUTH_CLIENT_ID  = {client_id[:20]}...")
    print(f"  GSC_OAUTH_SECRET     = {client_secret[:6]}...")
    print(f"  GSC_OAUTH_REFRESH    = {refresh_token[:20]}...")
    print(f"  GSC_SITE_URL         = sc-domain:saaspare.org")
    print("\nTest it with: uv run python scripts/seo/seo_agent.py --mode audit")


if __name__ == "__main__":
    main()
