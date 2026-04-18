# Intent Engine — Setup Guide

## What you need (one-time, ~2 hours)

### Step 1 — Buy a domain ($9, debit card works)
Go to **porkbun.com**, search for a `.com` like `buysignals.com` or `intentleads.com`.
Checkout with your debit card. No age check at registrars in AU.

### Step 2 — Cloudflare (free, no card needed)
1. Sign up at **cloudflare.com** (free plan, no card)
2. Add your domain → follow DNS instructions from Porkbun
3. Enable **Cloudflare Pages** (will host your SEO comparison site)
4. Enable **Cloudflare Email Routing** → forward `admin@yourdomain.com` to your ProtonMail

### Step 3 — GitHub repo (free)
1. Create a **private GitHub repo** called `intent-engine`
2. Push this code:
   ```
   cd intent-engine
   git init
   git add .
   git commit -m "init"
   git remote add origin https://github.com/YOU/intent-engine.git
   git push -u origin main
   ```
3. Create a **second public GitHub repo** called `intent-site` — this is your SEO site

### Step 4 — Get free LLM API keys (20 min)
All free, all instant, none require age verification:
- **Groq** → console.groq.com → Create API key → copy `gsk_...`
- **Google AI Studio** → aistudio.google.com → Get API key → copy `AIza...`
- **Cerebras** → inference.cerebras.ai → Sign up → API key
- **OpenRouter** → openrouter.ai → Sign up → Keys → copy `sk-or-...`

### Step 5 — Reddit API key (free, instant)
1. reddit.com → Settings → Safety & Privacy → **Manage third-party app access**
   OR go to **reddit.com/prefs/apps**
2. Click "create another app" → select **script**
3. Name: `IntentEngine`, redirect: `http://localhost`
4. Copy the client ID (under the app name) and secret

### Step 6 — GitHub token (for data fetching)
1. github.com → Settings → Developer settings → Personal access tokens → Fine-grained
2. New token → name `intent-data` → expiry 1 year → **read-only public repo access**
3. Copy `ghp_...`

### Step 7 — Add GitHub Actions secrets
In your `intent-engine` repo → Settings → Secrets and variables → Actions → New secret:

```
GROQ_API_KEY          = gsk_...
GEMINI_API_KEY        = AIza...
CEREBRAS_API_KEY      = csk_...
OPENROUTER_API_KEY    = sk-or-...
REDDIT_CLIENT_ID      = (from step 5)
REDDIT_CLIENT_SECRET  = (from step 5)
REDDIT_USER_AGENT     = IntentEngine/1.0 (contact: youremail@proton.me)
GH_DATA_TOKEN         = ghp_...
GH_PAT                = (a PAT with repo write access — so Actions can commit the DB)
MONETIZATION_MODE     = affiliate_only
DRY_RUN               = false
AMAZON_ASSOCIATE_TAG  = yourtag-22
SITE_DOMAIN           = https://yourdomain.com
CF_PAGES_REPO         = https://github.com/YOU/intent-site.git
HEALTHCHECKS_URL      = https://hc-ping.com  (optional, from healthchecks.io)
```

### Step 8 — Amazon Associates (for affiliate revenue)
1. Go to **affiliate-program.amazon.com.au**
2. Sign up with your name and email
3. Website URL: your domain
4. At signup they ask for your website — put your Cloudflare Pages URL
5. You need to make **3 qualifying sales within 180 days** to keep the account
   (The system will drive traffic — this is achievable)
6. Get your Associate Tag (e.g. `yourname-22`) → add to secrets above

### Step 9 — Connect Cloudflare Pages to intent-site repo
1. Cloudflare dashboard → Pages → Create project
2. Connect to GitHub → select `intent-site` repo
3. Build command: (leave blank, it's static HTML)
4. Output directory: `/` (root)
5. Deploy → you'll get a `*.pages.dev` URL

### Step 10 — Run it!
```bash
# Local test first:
cp .env.example .env
# Fill in your keys in .env
uv sync
uv run engine init
uv run engine harvest
uv run engine score
uv run engine publish
uv run engine stats
```

Then push to GitHub — the Actions cron takes over automatically.

---

## Monetization Modes

Set `MONETIZATION_MODE` in GitHub secrets to:

| Mode | What it does | Revenue potential |
|---|---|---|
| `affiliate_only` | Only publishes SEO comparison pages with Amazon/affiliate links. No Gumroad. | $50–$500/mo after 3–6 months of SEO |
| `full` | Publishes lead packs to Gumroad + SEO pages + affiliate. Requires Gumroad KYC. | $500–$5000/mo |
| `shadow` | Generates everything but doesn't publish. Dry run mode. | $0 (save outputs for later) |

**Start with `affiliate_only`** — the SEO pages go live immediately, Amazon Associates works, and you build up traffic. When ready to unlock full revenue (Gumroad + all affiliates), switch to `full`.

---

## Revenue Timeline Estimates

| Month | What's happening | Est. monthly revenue |
|---|---|---|
| 1 | System running, SEO pages indexed, Amazon traffic trickling in | $0–$30 |
| 2 | 30–60 SEO pages live, Google starting to rank them | $20–$100 |
| 3 | First pages ranking page 1 for long-tail queries | $80–$300 |
| 4 | Strong verticals identified by bandit, lead packs ready | $200–$600 |
| 5 | Compounding: 100+ pages, repeat buyers, SEO snowball | $400–$1500 |
| 6 | Full stack running, bandit optimized | $600–$3000 |

These are **conservative estimates** for `affiliate_only` mode. `full` mode (with lead pack sales) adds 3–5× on top once Gumroad is live.

---

## How the money flows (affiliate_only mode)

1. System generates comparison pages like *"Best DevOps Tools 2025"*
2. Pages go live on your domain via Cloudflare Pages
3. Google indexes them (IndexNow accelerates this)
4. Someone searches "best CI/CD tool", finds your page
5. They click your Amazon or PartnerStack affiliate link
6. They buy → you earn 4–15% commission
7. Commission accumulates in your affiliate account
8. You cash out whenever you choose (at any time, once thresholds met)

**Amazon AU pays out when balance reaches $10 AUD** — direct to your bank.

---

## Files the system generates

```
outputs/generated/
  leadpack_devtools_2025-01-15_a3b4.csv    ← weekly lead pack (CSV)
  leadpack_devtools_2025-01-15_a3b4.md     ← summary brief

site/pages/
  best-ci-cd-tools-2025.html              ← SEO comparison page
  top-devops-monitoring-tools.html        ← another SEO page
  ...
```

All committed to your repo automatically by GitHub Actions.
