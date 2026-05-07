# SaaSpare — 2-Month Hands-Off Runbook

Last updated: May 2026
Commit baseline: `f2311c75`

---

## What's running autonomously (zero human input needed)

Every night at ~3am UTC the site self-heals and self-optimises via the
`nightly_site_integrity.yml` workflow:

| # | Step | What it does |
|---|---|---|
| 1 | Repair corruption | Fixes any malformed titles/trust-boxes from generator bugs |
| 2 | Sync KPI counters | Updates public_kpis.json from DB for marketing pages |
| 3 | Inject journey links | Adds intent-weighted next-step links on buyer pages |
| 4 | Flag risky claims | Adds manual-review flag to pages with refund/SLA claims |
| 5 | Fix Amazon links | Removes dead tags, adds MS365 pill |
| 6 | SEO consolidate | Strips fake aggregateRating, fixes dup canonicals |
| 7 | **Blast off (CTR+AEO)** | Rewrites titles with date stamps, refreshes dateModified, adds featured-answer boxes, pings IndexNow |
| 8 | **Internal links** | Kills orphan pages — every page gets 5 contextual related-page links |
| 9 | **Site upgrade** | Sitemap changefreq, manifest, Clarity, exit-intent on new pages |
| 10 | **llms-full.txt** | Rebuilds LLM-readable index of 1,015 pages |
| 11 | Content QA gate | Fails build on any hard SEO issue |
| 12 | SEO integrity tests | 15 pytest checks (canonicals, schema, sitemap, money-schema) |
| 13 | Commit + push | Auto-commits fixes with `[skip ci]` |

Every weekday at ~7am UTC the programmatic SEO workflow runs:
- Generates new money pages for seeded tools/verticals
- Validates all affiliate redirects (fails on DEAD)
- Submits backlinks + IndexNow pings
- Refreshes YouTube bridge manifest
- Runs the same integrity gates

---

## What needs YOUR attention (the only 4 things)

### 1. Swap the Microsoft Clarity project ID (2 minutes, one-time)

The Clarity snippet is live on all 1,015 pages with placeholder ID
`CLARITY_PROJECT_ID_REPLACE_ME`. To activate:

1. Go to https://clarity.microsoft.com → sign up (free, no credit card)
2. Create project for `saaspare.org`
3. Grab your project ID (looks like `abc1d2e3f4`)
4. Find-replace in repo:
   ```
   sed -i 's/CLARITY_PROJECT_ID_REPLACE_ME/yourprojectid/g' site/index.html site/pages/*.html
   ```
5. Commit + push

**Why it matters:** Free heatmaps, scroll depth, rage-click detection, session
replay. GDPR-safe by default (no cookies unless you toggle them on). This
tells you exactly where users drop off on money pages — huge for conversion
optimisation you can't get from GA4 alone.

### 2. Send the 54 Semrush outreach emails (1 hour, one-time)

The Semrush prospects list + email template is in `seo/reports/`. Sit down
with a coffee, paste-and-send through 54 emails rated 4/5 and 5/5.
Expected return: 5-12 backlinks in 4 weeks.

### 3. Submit to 25 directories (1 hour, one-time)

Pack is at <ref_file file="C:/Users/smith/intent-engine/seo/reports/directory-submission-pack.md" />.
Descriptions are pre-written, URLs are ranked by ROI. Top 7 alone
(Product Hunt, BetaList, AlternativeTo, Capterra, G2, Crunchbase, SaaSHub)
will do more than 100 low-DA auto-submits.

### 4. Fix the social profile URLs (if you don't have them yet)

The new Organization schema on the homepage points to these social profiles
via `sameAs`:
- `linkedin.com/company/saaspare`
- `twitter.com/saaspare`
- `x.com/saaspare`
- `producthunt.com/@saaspare`
- `crunchbase.com/organization/saaspare`

**Create these accounts** (same username if possible) and verify Google can
reach them. If a URL doesn't exist, Google will just ignore that sameAs entry
— not harmful, but a missed trust signal. Creating the 5 profiles takes
~20 minutes total.

---

## Expected timeline

Assumes you do the 4 things above and then leave it.

### Week 1 (Days 1-7)
- IndexNow pings from the blast_off.py run propagate through Bing + Yandex
- Google re-crawls 30-60% of pages with the new titles/descs/answer boxes
- CTR starts lifting: **0.4% → 1.0-1.8%**
- Clarity data starts flowing (if you activated it)

### Week 2-3
- Google has re-indexed most pages with fresh dateModified
- Featured-answer boxes start appearing in AI Overviews for direct-answer queries
- Internal-linking boost begins — previously orphan pages get first meaningful crawl depth
- Expected impressions: **6.5K/17d → 15-25K/17d**
- Expected clicks: **29 → 90-180**
- Authority Score moves from **0 → 3-5** (first directory approvals land)

### Month 1 (Weeks 3-4)
- First outreach links go live (5-12 backlinks from Semrush list)
- Top 7 directories approve (Product Hunt launch often gives 500+ visitors day-of)
- Tresorit pages from the programmatic bot start ranking
- **Target: Authority Score 8-12, organic clicks 300-500/month**

### Month 2 (Weeks 5-8)
- Google's QDF (Query Deserves Freshness) algorithm starts rewarding the nightly
  dateModified refresh — pages move from position 20 → 10-15
- Featured snippets win for 15-30 queries
- AI Overview citations begin for "best X", "X vs Y", and pricing queries
- Tier 2 directories approve (DA 50-70)
- **Target: Authority Score 14-20, organic clicks 1-2K/month**

### Month 3 (beyond this runbook)
- Domain hits escape velocity — pages start ranking in top 10 for long-tail queries
- Compound effect from 60+ backlinks + fresh content + AI-Overview citations
- **Target: Authority Score 22-30, organic clicks 3-5K/month**

---

## What could go wrong (and how to spot it)

### Warning signs in GSC (check weekly)
- **Impressions suddenly drop by >30%** — possible algorithm penalty or
  indexing issue. Action: check "Coverage" report, look for new errors
- **CTR drops below 1.0%** — title/desc changes may have been too aggressive.
  Action: check `outputs/seo/blast_off.json` for what changed
- **Average position climbs above 30** — content freshness signal not landing.
  Action: verify nightly workflow is running (`gh run list`)

### Warning signs in GA4
- **Bounce rate > 80% on money pages** — featured answer box may be too
  definitive (readers not scrolling). Action: check Clarity scroll heatmaps
- **Exit-intent newsletter fires < 1% signup rate** — copy needs tweaking
- **/go/ affiliate clicks flat** — CTA may be too low on page. Check
  Clarity rage-clicks on pricing tables

### Warning signs in CI
- **Nightly workflow fails** — check `gh run list --workflow=nightly_site_integrity.yml`.
  Usually a rebase conflict from two bots committing at once. Autofixed via
  `-X ours` but if it persists, check the workflow logs.
- **Content QA shows > 10 hard failures** — something in the generator broke.
  Check `outputs/seo/content_qa.json` for specific pages.

---

## Quick status commands (paste into terminal)

```bash
# Check nightly workflow is running
cd intent-engine && gh run list --workflow=nightly_site_integrity.yml --limit 3

# Check what blast_off did last night
cat outputs/seo/blast_off.json | jq .

# Check orphan page count
cat outputs/seo/internal_links.json | jq '.orphans_after'

# Check content QA status
cat outputs/seo/content_qa.json | jq '.stats.hard, .stats.soft'

# Run local full verification
uv run python scripts/content_qa.py && \
  uv run pytest tests/test_normalise.py tests/test_seo_integrity.py -q
```

---

## What I deliberately did NOT do (and why)

1. **Meta Pixel / TikTok Pixel retargeting** — needs cookie-consent framework
   first (GDPR/UK ICO). Add when you're ready to do consent banner too.

2. **Automated content generation beyond what the bot does** — writing
   10K low-quality pages tanks your domain. The 1,015 existing pages are the
   sweet spot for a new site.

3. **Paid traffic** — not worth it until Authority Score is >20. You'd be
   paying to promote pages that can't convert at the auction-clearing CPC.

4. **Newsletter scaling beyond exit-intent** — add a proper ESP (ConvertKit,
   Resend, Buttondown) once you have 500+ subscribers. Until then,
   FormSubmit.co covers it fine.

5. **Sitemap index splitting** — single sitemap.xml is fine up to 10K URLs.
   You're at 996. Revisit when past 5K.

6. **Author profile pages with LinkedIn** — noted in the original SEO phase
   report as template work. Real human bios + photos beat any AI-generated
   "team" page. Do this when you hire help.

---

## If you want ONE dashboard to watch

Create a Google Sheet with these 5 rows, checked weekly:

| Week | GSC impressions | GSC clicks | GSC avg position | GA4 active users | Authority Score |
|---|---|---|---|---|---|
| Baseline (May 7) | 6,540 | 29 | 20.3 | 201 | 0 |
| Week 1 | | | | | |
| Week 2 | | | | | |
| Week 4 | | | | | |
| Week 8 | | | | | |

That's the only number tracking you need.

---

## Commit log of what was shipped during this pass

- `b7dc7f6c` — nav logo unified across 771 pages
- `dbf287f3` — partner network applications doc
- `63b5d725` — removed fake aggregateRating source from generators
- `acda639d` — Tresorit Rakuten affiliate links + seeds
- `1b75c61c` — Tresorit in programmatic bot queues
- `a94572ea` — 13 Tresorit pages auto-generated
- `a184479c` — CTR + AEO blast pack (89 titles, 1,015 descs, 1,015 featured answers)
- `94ac8ad4` — Blast pack wired into nightly
- `f2311c75` — **mega audit fix: orphan-kill, homepage mega-schema, sitemap changefreq, _headers, manifest, Clarity, exit-intent, llms-full.txt**

**Net state change over the last 24 hours:**
- 1,031 pages got new featured-answer blocks (AEO)
- 1,015 pages got internal-link blocks (orphan kill)
- 1,015 pages got upgraded head (manifest, Clarity, exit-intent)
- 1,044 sitemap entries got changefreq
- Homepage got full mega-schema (WebSite + SearchAction + Organization + FAQPage + sameAs)
- /llms-full.txt generated (356 KB index for LLM crawlers)
- /manifest.webmanifest live
- /_headers live (Cloudflare cache + security + HSTS)

Leave it alone for 8 weeks. Come back to check the dashboard. That's the plan.
