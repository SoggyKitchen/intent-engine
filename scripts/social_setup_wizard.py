"""
Social Bot Setup Wizard
Run: uv run python scripts/social_setup_wizard.py
"""
import subprocess
import sys
import time
import webbrowser


def _color(text, code):
    return f"\033[{code}m{text}\033[0m"

def red(t):    return _color(t, "91")
def green(t):  return _color(t, "92")
def yellow(t): return _color(t, "93")
def cyan(t):   return _color(t, "96")
def bold(t):   return _color(t, "1")
def dim(t):    return _color(t, "2")


def hr(char="─", width=60):
    print(dim(char * width))


def header(title, step, total):
    print()
    hr("═")
    print(bold(f"  STEP {step}/{total}  ·  {title}"))
    hr("═")
    print()


def ask(prompt, secret=False, allow_blank=False):
    import getpass
    while True:
        try:
            val = getpass.getpass(f"  {cyan('►')} {prompt}: ") if secret else input(f"  {cyan('►')} {prompt}: ")
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Wizard cancelled. Run again anytime.")
            sys.exit(0)
        val = val.strip()
        if val or allow_blank:
            return val
        print(f"  {red('Cannot be blank. Try again.')}")


def confirm(prompt):
    try:
        ans = input(f"  {cyan('►')} {prompt} {dim('[y/N]')}: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        return False
    return ans in ("y", "yes")


def open_url(url, label):
    print(f"\n  {yellow('Opening:')} {label}")
    print(f"  {dim(url)}")
    try:
        webbrowser.open(url)
    except Exception:
        print(f"  {red('Could not open browser. Open manually:')} {url}")
    time.sleep(1)


def set_secret(name, value):
    if not value:
        return False
    result = subprocess.run(
        ["gh", "secret", "set", name, "--body", value],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"  {green('✓')} {name} saved to GitHub")
        return True
    else:
        print(f"  {red('✗')} Failed to save {name}: {result.stderr.strip()}")
        return False


def check_secret_exists(name):
    result = subprocess.run(
        ["gh", "secret", "list"],
        capture_output=True, text=True
    )
    return name in result.stdout


def get_existing_secrets():
    result = subprocess.run(["gh", "secret", "list"], capture_output=True, text=True)
    return result.stdout


# ─────────────────────────────────────────────────────────────────────────────

def wizard_intro():
    print()
    hr("═")
    print(bold("  SAASPARE SOCIAL BOT SETUP WIZARD"))
    hr("═")
    print("""
  This wizard walks you through connecting:
    1. X / Twitter  — auto-posts comparison pages
    2. Reddit       — auto-answers high-intent threads
    3. LinkedIn     — posts to your professional network

  All credentials go straight to GitHub Secrets — never stored locally.
  Takes about 10 minutes total.
""")
    existing = get_existing_secrets()
    done = []
    if "TWITTER_API_KEY" in existing:
        done.append(green("✓ Twitter already configured"))
    if "REDDIT_CLIENT_ID" in existing:
        done.append(green("✓ Reddit already configured"))
    if "LINKEDIN_ACCESS_TOKEN" in existing:
        done.append(green("✓ LinkedIn already configured"))

    if done:
        print("  " + "  ".join(done))
        print()

    if not confirm("Ready to start?"):
        print("\n  Run again when you're ready.\n")
        sys.exit(0)


# ─────────────────────────────────────────────────────────────────────────────

def setup_twitter():
    header("X / Twitter", 1, 3)

    if check_secret_exists("TWITTER_API_KEY"):
        print(f"  {green('✓ Twitter is already configured.')}")
        if not confirm("Re-enter credentials anyway?"):
            return

    print("""  Twitter (X) needs a Developer App with Read + Write permissions.
  The bot posts 1 tweet per run (max 5/day). Free tier is fine.
""")

    open_url("https://developer.twitter.com/en/portal/dashboard", "Twitter Developer Portal")

    print("""
  Steps:
    1. Sign in → click "Create Project" (or use an existing one)
    2. Create an App inside the project
    3. Go to App Settings → "User authentication settings"
    4. Set "App permissions" to Read and Write
    5. Set "Type of App" to Native App
    6. Callback URL: https://saaspare.org  (anything works)
    7. Go to "Keys and tokens" tab — copy all 4 values below
""")

    api_key    = ask("API Key (Consumer Key)")
    api_secret = ask("API Secret (Consumer Secret)", secret=True)

    print(f"""
  {yellow('Access tokens:')} still on the "Keys and tokens" tab,
  scroll to "Access Token and Secret" → click Generate.
""")

    access_token  = ask("Access Token")
    access_secret = ask("Access Token Secret", secret=True)

    print()
    ok = all([
        set_secret("TWITTER_API_KEY",              api_key),
        set_secret("TWITTER_API_SECRET",           api_secret),
        set_secret("TWITTER_ACCESS_TOKEN",         access_token),
        set_secret("TWITTER_ACCESS_TOKEN_SECRET",  access_secret),
    ])

    if ok:
        print(f"\n  {green('Twitter is ready.')} The bot will post automatically next CI run.")
    else:
        print(f"\n  {red('Some secrets failed — check the errors above and retry.')}")


# ─────────────────────────────────────────────────────────────────────────────

def setup_reddit():
    header("Reddit", 2, 3)

    if check_secret_exists("REDDIT_CLIENT_ID"):
        print(f"  {green('✓ Reddit is already configured.')}")
        if not confirm("Re-enter credentials anyway?"):
            return

    print("""  Reddit needs a "script" type app. The bot reads high-intent threads
  and posts genuinely helpful answers (max 2 per run, allowlisted
  subreddits only). You need a Reddit account — use your main or a
  dedicated one (e.g. u/SaaSpareBot).
""")

    open_url("https://www.reddit.com/prefs/apps", "Reddit App Preferences")

    print("""
  Steps:
    1. Scroll to the bottom → click "create another app..."
    2. Name: SaaSpare Bot
    3. Type: select "script"
    4. Description: SaaSpare affiliate content bot
    5. About URL: https://saaspare.org
    6. Redirect URI: https://saaspare.org
    7. Click "create app"
    8. Copy the Client ID (under the app name, looks like: abc123XYZ)
    9. Copy the Secret (the longer string)
""")

    client_id     = ask("Client ID (under the app name)")
    client_secret = ask("Client Secret", secret=True)

    print(f"""
  {yellow('Account credentials')} — the Reddit username + password the bot logs in as.
  This is the account that will post the comments.
""")

    username  = ask("Reddit Username (no u/ prefix)")
    password  = ask("Reddit Password", secret=True)
    user_agent = f"saaspare-bot/1.0 by u/{username}"

    print()
    ok = all([
        set_secret("REDDIT_CLIENT_ID",     client_id),
        set_secret("REDDIT_CLIENT_SECRET", client_secret),
        set_secret("REDDIT_USERNAME",      username),
        set_secret("REDDIT_PASSWORD",      password),
        set_secret("REDDIT_USER_AGENT",    user_agent),
    ])

    print(f"""
  {yellow('Subreddit allowlist:')} The bot will ONLY post in subreddits you list here.
  This protects your account from bans. Start conservative — you can always add more.

  Safe defaults: entrepreneur, smallbusiness, SaaS, marketing, startups,
                 hubspot, salesforce, projectmanagement, accounting
""")
    custom = ask("Subreddits to allow (comma-separated, no r/ prefix)", allow_blank=True)
    default_subs = "entrepreneur,smallbusiness,SaaS,marketing,startups,hubspot,projectmanagement,accounting"
    allowlist = custom if custom else default_subs
    set_secret("REDDIT_ALLOWED_SUBREDDITS", allowlist)
    print(f"  {dim('Allowlist:')} {allowlist}")

    if ok:
        print(f"\n  {green('Reddit is ready.')} Bot posts up to 2 answers per run in approved subreddits.")
    else:
        print(f"\n  {red('Some secrets failed — check errors above and retry.')}")


# ─────────────────────────────────────────────────────────────────────────────

def setup_linkedin():
    header("LinkedIn", 3, 3)

    if check_secret_exists("LINKEDIN_ACCESS_TOKEN"):
        print(f"  {green('✓ LinkedIn is already configured.')}")
        if not confirm("Re-enter credentials anyway?"):
            return

    print("""  LinkedIn needs an access token from a LinkedIn Developer App.
  The bot posts 1 update per run using the UGC Posts API.
""")

    open_url("https://www.linkedin.com/developers/apps/new", "LinkedIn Developer Apps")

    print("""
  Steps:
    1. Create a new app:
       - App name: SaaSpare
       - LinkedIn Page: your personal profile or company (create one if needed)
       - Privacy policy URL: https://saaspare.org/privacy.html
       - App logo: upload any image (your site logo or a placeholder)
    2. Click "Create app"
    3. Go to the "Products" tab → request access to "Share on LinkedIn"
       (approve instantly for personal use)
    4. Go to "Auth" tab → copy your Client ID and Client Secret
    5. Then we need to generate an access token. Open the URL below in your
       browser (replace CLIENT_ID with yours):
""")

    client_id = ask("LinkedIn Client ID (from Auth tab)")
    client_secret = ask("LinkedIn Client Secret", secret=True)

    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri=https%3A%2F%2Fsaaspare.org"
        f"&scope=openid%20profile%20w_member_social"
    )

    print(f"""
  {yellow('Authorization URL — open this in your browser:')}
  {dim(auth_url)}
""")
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    print("""  After you approve, LinkedIn redirects to saaspare.org with a URL like:
    https://saaspare.org/?code=AQT...&state=...

  Copy the value of "code=" from that URL.
""")

    auth_code = ask("Paste the code= value from the redirect URL")

    print("\n  Exchanging code for access token...")
    token_result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://www.linkedin.com/oauth/v2/accessToken",
        "-d", f"grant_type=authorization_code"
              f"&code={auth_code}"
              f"&redirect_uri=https%3A%2F%2Fsaaspare.org"
              f"&client_id={client_id}"
              f"&client_secret={client_secret}",
        "-H", "Content-Type: application/x-www-form-urlencoded"
    ], capture_output=True, text=True)

    import json
    try:
        token_data = json.loads(token_result.stdout)
        access_token = token_data.get("access_token", "")
        expires_in = token_data.get("expires_in", 0)
        if access_token:
            print(f"  {green('✓ Got access token!')} Expires in {expires_in // 86400} days")
        else:
            print(f"  {red('Token exchange failed:')} {token_result.stdout}")
            print("  You can paste a token manually if you have one from the LinkedIn OAuth playground.")
            access_token = ask("Access Token (paste manually or leave blank to skip)", allow_blank=True)
    except Exception:
        print(f"  {red('Could not parse response:')} {token_result.stdout[:200]}")
        access_token = ask("Access Token (paste manually)", allow_blank=True)

    print(f"""
  {yellow('Person URN:')} your LinkedIn member ID in the format: urn:li:person:XXXXXXXX
  Get it by visiting: https://www.linkedin.com/in/me/  (the ID is in the URL)
  Or from the API: https://api.linkedin.com/v2/me
""")
    open_url("https://api.linkedin.com/v2/me", "LinkedIn /me endpoint (shows your URN)")

    person_urn = ask("Person URN (e.g. urn:li:person:abc123 or just the ID)")

    if person_urn and not person_urn.startswith("urn:"):
        person_urn = f"urn:li:person:{person_urn}"

    print()
    ok = all([
        set_secret("LINKEDIN_ACCESS_TOKEN", access_token) if access_token else True,
        set_secret("LINKEDIN_PERSON_URN", person_urn) if person_urn else True,
    ])

    if access_token and person_urn and ok:
        print(f"\n  {green('LinkedIn is ready.')} Bot will post once per run.")
        print(f"  {yellow('Note:')} LinkedIn access tokens expire in ~60 days. Re-run this wizard to refresh.")
    elif not access_token:
        print(f"\n  {yellow('LinkedIn skipped')} — no access token. Re-run wizard when you have one.")


# ─────────────────────────────────────────────────────────────────────────────

def wizard_done():
    print()
    hr("═")
    print(bold("  ALL DONE"))
    hr("═")

    existing = get_existing_secrets()
    status = {
        "Twitter": "TWITTER_API_KEY" in existing,
        "Reddit":  "REDDIT_CLIENT_ID" in existing,
        "LinkedIn": "LINKEDIN_ACCESS_TOKEN" in existing,
    }

    print()
    for platform, ready in status.items():
        icon = green("✓") if ready else yellow("○")
        state = "Active" if ready else "Not configured"
        print(f"  {icon}  {platform:<12} {state}")

    all_ready = all(status.values())
    print()

    if all_ready:
        print(f"  {green('All 3 platforms active!')} The bot runs automatically 4× per day via GitHub Actions.")
        print(f"  Next run: check https://github.com/SoggyKitchen/intent-engine/actions")
    else:
        missing = [p for p, r in status.items() if not r]
        print(f"  {yellow('Still to configure:')} {', '.join(missing)}")
        print(f"  Re-run this wizard anytime: {cyan('uv run python scripts/social_setup_wizard.py')}")

    print(f"""
  {bold('How the bot works:')}
    • Runs at 6:30am, 12:30pm, 6:30pm, 11:30pm UTC
    • Twitter: 1 tweet per run (latest comparison page)
    • Reddit: up to 2 answers per run (high-intent threads only)
    • LinkedIn: 1 post per run

  {bold('Check social queue:')}
    outputs/generated/social_queue_*.md  (what it's queuing)
    outputs/generated/social/            (calendar + platform breakdowns)
""")
    hr("═")
    print()


# ─────────────────────────────────────────────────────────────────────────────

def main():
    wizard_intro()

    existing = get_existing_secrets()

    platforms = []
    if "TWITTER_API_KEY" not in existing:
        platforms.append(("Twitter/X", setup_twitter))
    else:
        platforms.append(("Twitter/X (already set — skip?)", setup_twitter))

    if "REDDIT_CLIENT_ID" not in existing:
        platforms.append(("Reddit", setup_reddit))
    else:
        platforms.append(("Reddit (already set — skip?)", setup_reddit))

    if "LINKEDIN_ACCESS_TOKEN" not in existing:
        platforms.append(("LinkedIn", setup_linkedin))
    else:
        platforms.append(("LinkedIn (already set — skip?)", setup_linkedin))

    print("\n  Which platforms do you want to set up?")
    for i, (name, _) in enumerate(platforms, 1):
        already = green("✓ ") if "already set" in name else "  "
        clean_name = name.split(" (")[0]
        print(f"  {already}{i}. {clean_name}")

    print(f"  {dim('Press Enter to do all, or type numbers e.g. 1 3')}")
    try:
        choice = input(f"  {cyan('►')} Your choice: ").strip()
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)

    if choice == "":
        selected = list(range(len(platforms)))
    else:
        try:
            selected = [int(x.strip()) - 1 for x in choice.replace(",", " ").split() if x.strip().isdigit()]
        except Exception:
            selected = list(range(len(platforms)))

    for idx in selected:
        if 0 <= idx < len(platforms):
            _, fn = platforms[idx]
            fn()

    wizard_done()


if __name__ == "__main__":
    main()
