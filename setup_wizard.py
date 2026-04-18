"""
Intent Engine — Interactive Setup Wizard
Run: uv run --with httpx python setup_wizard.py

Opens each signup URL in your browser automatically, waits for you to get the key,
tests it works, then writes your .env file. Total time: ~15 minutes.
"""
import os
import sys
import time
import webbrowser
from pathlib import Path


def banner(text: str):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def step(n: int, total: int, text: str):
    print(f"\n[{n}/{total}] {text}")
    print("-" * 50)


def ask(prompt: str, default: str = "") -> str:
    if default:
        val = input(f"  {prompt} [{default}]: ").strip()
        return val if val else default
    return input(f"  {prompt}: ").strip()


def open_url(url: str):
    print(f"\n  -> Opening: {url}")
    webbrowser.open(url)
    time.sleep(1)


def _http():
    try:
        import httpx
        return httpx
    except ImportError:
        import urllib.request, urllib.error
        return None


def test_groq(key: str) -> bool:
    try:
        import httpx
        resp = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "user", "content": "Say OK"}],
                  "max_tokens": 5},
            timeout=20,
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


def test_gemini(key: str) -> bool:
    try:
        import httpx
        resp = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}",
            json={"contents": [{"parts": [{"text": "Say OK"}]}]},
            timeout=20,
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


def test_reddit(client_id: str, client_secret: str) -> bool:
    try:
        import httpx, base64
        creds = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        resp = httpx.post(
            "https://www.reddit.com/api/v1/access_token",
            headers={"Authorization": f"Basic {creds}",
                     "User-Agent": "IntentEngineSetup/1.0"},
            data={"grant_type": "client_credentials"},
            timeout=15,
        )
        return resp.status_code == 200 and "access_token" in resp.json()
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


def test_github(token: str) -> bool:
    try:
        import httpx
        resp = httpx.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {token}", "User-Agent": "IntentEngine"},
            timeout=10,
        )
        if resp.status_code == 200:
            username = resp.json().get("login", "unknown")
            print(f"  Logged in as GitHub user: {username}")
            return True
        return False
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


def main():
    banner("Intent Engine Setup Wizard")
    print("""
  This wizard will:
  1. Open each signup page in your browser
  2. Wait for you to get the key/credential
  3. Test it works
  4. Write your .env file

  You only type personal info (email/password) on the websites.
  You paste API keys here after getting them.
    """)

    input("  Press ENTER to start...")

    env = {}
    TOTAL = 5

    # ── Step 1: Groq ──────────────────────────────────────────────────────────
    step(1, TOTAL, "Groq API Key (primary LLM — free, instant)")
    print("""
  Instructions:
  1. Click "Sign Up" or "Sign In with Google" on the page that opens
  2. Once logged in, click "API Keys" in the left sidebar
  3. Click "Create API Key", name it "intent-engine"
  4. Copy the key (starts with gsk_...)
    """)
    open_url("https://console.groq.com/keys")
    while True:
        key = ask("Paste your Groq API key (gsk_...)")
        if not key.startswith("gsk_"):
            print("  That doesn't look right — Groq keys start with gsk_")
            continue
        print("  Testing key...")
        if test_groq(key):
            print("  Key works!")
            env["GROQ_API_KEY"] = key
            break
        else:
            retry = ask("Test failed. Try again? (y/n)", "y")
            if retry.lower() != "y":
                env["GROQ_API_KEY"] = key
                break

    # ── Step 2: GitHub PAT ────────────────────────────────────────────────────
    step(2, TOTAL, "GitHub Personal Access Token (for repo + Actions)")
    print("""
  Instructions:
  1. On the page that opens, click "Generate new token" > "Generate new token (classic)"
  2. Note: "intent-engine-pat"
  3. Expiration: 1 year
  4. Scopes: check ONLY "repo" (full control of private repos)
  5. Scroll down, click "Generate token"
  6. Copy it NOW — GitHub only shows it once (starts with ghp_)
    """)
    open_url("https://github.com/settings/tokens/new")
    while True:
        token = ask("Paste your GitHub token (ghp_...)")
        if not token.startswith("ghp_") and not token.startswith("github_pat_"):
            print("  That doesn't look right — GitHub tokens start with ghp_ or github_pat_")
            continue
        print("  Testing token...")
        if test_github(token):
            print("  Token works!")
            env["GH_PAT"] = token
            env["GH_DATA_TOKEN"] = token
            break
        else:
            retry = ask("Test failed. Try again? (y/n)", "y")
            if retry.lower() != "y":
                env["GH_PAT"] = token
                env["GH_DATA_TOKEN"] = token
                break

    # ── Step 3: Amazon Associates ─────────────────────────────────────────────
    step(3, TOTAL, "Amazon Associates AU (affiliate links — accumulates until you cash out)")
    print("""
  Instructions:
  1. Sign in or create an Amazon AU account on the page that opens
  2. Fill in your account info (name, address)
  3. For "website": enter your future domain (e.g. https://yourdomain.com)
        If you don't have one yet, use https://github.com/your-username for now
  4. Choose your niche: "Computer & Electronics" or "Software"
  5. Complete signup — you'll get an Associate Tag like "yourname-22"

  NOTE: Amazon needs 3 qualifying sales in 180 days to keep the account active.
  The system will drive traffic to meet this automatically.
    """)
    open_url("https://affiliate-program.amazon.com.au")
    tag = ask("Paste your Amazon Associate Tag (e.g. yourname-22)", "yourtag-22")
    env["AMAZON_ASSOCIATE_TAG"] = tag

    # ── Step 4: Domain (optional for now) ─────────────────────────────────────
    step(4, TOTAL, "Domain name (optional — skip if you haven't bought one yet)")
    print("""
  A domain is needed for the SEO site. You can skip this now and add it later.
  Recommended: porkbun.com — $9/year, debit card accepted, no age check.
    """)
    buy = ask("Have you bought a domain? (y/n)", "n")
    if buy.lower() == "y":
        open_url("https://dash.cloudflare.com/")
        domain = ask("Enter your domain (e.g. buysignals.com)")
        env["SITE_DOMAIN"] = f"https://{domain}"
    else:
        print("  Skipping — set SITE_DOMAIN in .env later")
        env["SITE_DOMAIN"] = "https://yourdomain.com"

    # ── Step 5: GitHub Repo ───────────────────────────────────────────────────
    step(5, TOTAL, "Create GitHub repo and push the code")
    print("""
  Instructions:
  1. On the page that opens, click "New repository"
  2. Name: intent-engine
  3. Visibility: PRIVATE (important — keeps your keys safe)
  4. Do NOT initialize with README
  5. Click "Create repository"
  6. Copy the repo URL (e.g. https://github.com/yourname/intent-engine.git)
    """)
    open_url("https://github.com/new")
    repo_url = ask("Paste your new repo URL (https://github.com/YOU/intent-engine.git)")
    env["CF_PAGES_REPO"] = repo_url.replace("intent-engine", "intent-site")

    # ── Write .env ────────────────────────────────────────────────────────────
    banner("Writing .env file")
    env_path = Path(__file__).parent / ".env"
    env_content = "\n".join(f"{k}={v}" for k, v in env.items())
    env_content += "\n"
    env_content += "GEMINI_API_KEY=\n"
    env_content += "MONETIZATION_MODE=affiliate_only\n"
    env_content += "DRY_RUN=false\n"
    env_content += "LOG_LEVEL=INFO\n"
    env_content += "DB_PATH=data/intent.db\n"
    env_path.write_text(env_content)
    print(f"\n  .env written to: {env_path}")

    # ── Push to GitHub ────────────────────────────────────────────────────────
    banner("Pushing code to GitHub")
    print("""
  Run these commands in your terminal (Git Bash or Command Prompt):
    """)
    git_remote = repo_url if repo_url != "https://github.com/YOU/intent-engine.git" else "<your-repo-url>"
    print(f"""  cd C:\\Users\\smith\\intent-engine
  git init
  git add .
  git commit -m "init: intent engine"
  git branch -M main
  git remote add origin {git_remote}
  git push -u origin main""")

    print("""
  After pushing, add these GitHub Actions secrets:
  Go to: your repo -> Settings -> Secrets -> Actions -> New repository secret
    """)
    secrets_needed = {k: v for k, v in env.items()
                      if k not in ("SITE_DOMAIN", "CF_PAGES_REPO", "MONETIZATION_MODE",
                                   "DRY_RUN", "LOG_LEVEL", "DB_PATH")}
    for k, v in secrets_needed.items():
        masked = v[:6] + "..." if len(v) > 8 else "***"
        print(f"    {k:<35} = {masked}")
    print(f"    {'MONETIZATION_MODE':<35} = affiliate_only")
    print(f"    {'DRY_RUN':<35} = false")
    print(f"    {'SITE_DOMAIN':<35} = {env.get('SITE_DOMAIN','https://yourdomain.com')}")

    # ── Test local pipeline ───────────────────────────────────────────────────
    banner("Test your local pipeline now?")
    run_test = ask("Run a quick local harvest test? (y/n)", "y")
    if run_test.lower() == "y":
        print("\n  Running: engine init + harvest (HN only, no Reddit to keep it fast)...")
        os.system("uv run engine init")
        os.environ.update(env)
        os.system("uv run engine harvest")
        os.system("uv run engine stats")

    banner("Setup complete!")
    print("""
  What happens next (fully automatic once you push to GitHub):

    Every 6 hours:   harvest.yml fires -> collects signals from Reddit, HN, GitHub
    Every morning:   score_publish.yml -> scores signals with Groq, generates SEO pages,
                                          deploys to Cloudflare Pages, pings IndexNow
    Every Monday:    weekly_packs.yml  -> generates B2B lead pack CSVs

  Your affiliate links are live in every comparison page from day 1.
  Amazon commissions accumulate in your Associates account.
  Cash out whenever you want (no minimum for AU bank transfer after $10 AUD).

  To check progress anytime:
    uv run engine stats

  Good luck!
    """)


if __name__ == "__main__":
    main()
