# SaaSpare Operational Memory

Long-term log of what works on SaaSpare. Append at the end of every session.
(Cross-project context lives in the global Claude memory; this file is SaaSpare-only.)

## Performance History
- 2026-06-05: Baseline ~350 clicks/day, ~40,000 impressions/day. Domain <12mo old.
- Highest-value opportunity pages (GSC, early June 2026):
  - Ramp pricing: 1,732 impressions @ position 10.0
  - Asana free-plan: 327 impressions @ position 23.4
  - Linear free-plan: 247 impressions @ position 9.0

## SEO Learnings (what moved the needle)
- **"[tool] pricing change [month] 2026" pattern works.** Ramp's tracker page pulled
  279 impressions for "ramp pricing change may 2026" @ pos 4.3, growing MoM. Scaled the
  pattern to Shopify, HubSpot, Notion, ClickUp, Semrush, Monday (commit 6e9b2a030).
- **Title pattern that climbs:** `[Tool] Pricing 2026: Every Change, Real Cost & [Month] Update`.
- **FAQPage schema entries** for `did [tool] change pricing` + `[tool] pricing [month] 2026`
  added on the 6 pricing pages above — watch GSC ~3 weeks for impressions on those queries.
- **Generic FAQ placeholders are dead weight** — Notion & Monday.com shipped "check the
  pricing page / we verify weekly" answers; replaced with real plan/limit data.

## CRO Experiments
- (none formally measured yet — log results here as the pricing-change pages mature)

## Durable-change rule learned the hard way
- Pages are regenerated nightly by `generate_*_v3.py`. HTML-only edits get overwritten.
  Always add a `meta_desc=` (and FAQ/data) override to the generator's PRICING dict.
  Done for shopify/hubspot/clickup/semrush (commit d31e4a62e). Notion/Monday rely on the
  premium-template skip-condition instead.

## BLOCKER: GSC 403 (owner must fix — 2 min) — discovered 2026-06-06
- The daily agent now correctly requests `sc-domain:saaspare.org` (format fixed) but the
  Google account behind the `GSC_OAUTH_REFRESH_TOKEN` GitHub secret is NOT authorized on
  the property. Error: "User does not have sufficient permission for site 'sc-domain:saaspare.org'".
- This is the ONLY thing stopping the revenue engine from producing live dollar rankings.
  Everything else (audit, revenue join, program map, daily commit) works.
- FIX (one of):
  (a) In Search Console → Settings → Users and permissions → add the OAuth account
      (the Google account used to mint the refresh token) as Full/Owner on the
      saaspare.org domain property; OR
  (b) Regenerate GSC_OAUTH_REFRESH_TOKEN using the Google account that already owns the
      GSC property, and update the GitHub secret.
- Once fixed, the next daily run auto-populates revenue-opportunities.md with real $ ranking.

## RESOLVED 2026-06-06: Nightly CI failing 8+ days — root cause was canonical de-prefixing
- Symptom: nightly_site_integrity failed every run; two gates contradicted each other.
- TRUE root cause: `upgrade_old_pages.py:fix_canonical` stripped the numeric prefix
  (`7-best-X` → `best-X`) on every alternatives page, re-pointing 38 real canonicals at
  `best-X` pages that don't exist. Integrity test trusted the canonical and demanded the
  ghost in the sitemap; content_qa rejected the ghost when the sitemap echoed it.
- Contributing: `seo_consolidate.py` did the same 7-best→best consolidation (also disabled).
- FIXES (all on main, nightly now GREEN — run 27050636891):
  1. `upgrade_old_pages.fix_canonical` → self-referential canonical (matches own filename).
  2. `seo_consolidate.py` → disabled 7-best-X alternatives consolidation (was noindexing
     real ranking pages = revenue leak).
  3. `update_sitemap_and_index.py` → builder rejects any URL with no backing file.
  4. `nightly_site_integrity.yml` → rebuild sitemap AFTER all generators, before gates.
- LESSON: the `7-best-X` alternatives pages are the REAL, self-canonical, indexed revenue
  pages (Ramp/Notion/etc. have GSC impressions). Any script that tries to collapse them to
  a `best-X` twin is both an SEO/revenue mistake and a CI break. Do not re-introduce.

## Known issues / pending (owner actions)
- PartnerStack ban appeal pending (ClickUp, ActiveCampaign, Monday, Dashlane locked).
- Impact.com applications pending: HubSpot (39 pages), 1Password (37 pages).
- FreshBooks Awin closed — needs replacement program.
- Newsletter form has no backend (Beehiiv pending).
- Ahrefs/Semrush MCPs gated behind API-plan upgrades — GSC engine is sufficient meanwhile.

## Revenue Intelligence (the dollars-not-rankings layer)
- `revenue_intelligence.py` joins GSC × program-promoted-per-page × commission value →
  `revenue-opportunities.md` (pages ranked by $ uplift) + `program-acquisition.md`
  (which programs to apply to, ranked by traffic already on their pages).
- Latent map at build time (traffic-blind, no GSC locally): HubSpot 32 pages @ $400/conv
  PENDING · FreshBooks 18 @ $200 PENDING · Ahrefs 26 @ $100 PLACEHOLDER (no program!) ·
  Salesforce 13 @ $120 PLACEHOLDER · Rippling 15 @ $120 · Deel 17 @ $100.
- **Biggest untapped levers:** (1) get HubSpot Impact approval — 32 pages, highest $/conv.
  (2) Ahrefs has 26 pages and NO affiliate program yet — apply to Ahrefs affiliate program.
  (3) PartnerStack appeal unlocks ClickUp(18)+ActiveCampaign(18)+Monday(14)+Dashlane(9).
- Dollar values are MODELLED benchmarks; connect IMPACT_API_TOKEN for real EPC/conversions.

## Affiliate Status (last verified 2026-06-05)
- **Fiverr via Awin**: APPROVED 2026-06-03. Tracking link `/go/fiverr` already in _redirects (awinmid=6288, awinaffid=2917137). ✅
- **AWeber via CJ**: APPROVED 2026-05-13. `/go/aweber` with CJ link already in _redirects. ✅
- **FreshBooks Awin**: REJECTED 2026-06-01 (program FreshBooks_Closing was already closing). Needs replacement — apply to FreshBooks direct or ShareASale.
- **PartnerStack**: NETWORK-LOCKED 2026-06-04. Appeal filed 2026-06-05 (Ticket 115928). ClickUp, ActiveCampaign, Monday, Dashlane all blocked until resolved.
- **Impact.com (ID 7269601)**: Only Semrush active. Wix application PENDING. HubSpot PENDING.
- **HubSpot direct**: DECLINED via affiliates@hubspot.com (May 2026) — insufficient site traffic at time of application. Re-apply in 60 days when GSC clicks improve.
- **Unidata via CJ**: Approved (May 2026) — niche, low EPC, deprioritize.

## CTR Experiments (2026-06-05 baseline)
- 4 pages updated with revised titles/metas:
  - Ramp pricing: new title targets "pricing changes" query directly (was 0.59% CTR, 1687 impr @ pos 10)
  - Mixpanel pricing: "June 2026" specificity added (was 0% CTR, 742 impr @ pos 13.7)
  - Notion free plan: meta rewritten to drive through-clicks past featured snippet (0% CTR, 557 impr @ pos 9.4)
  - Sentry free plan: reframed around "when you'll outgrow it" (0% CTR, 528 impr @ pos 7.5)
- Check GSC ~21 days for CTR movement. Target: Ramp > 2%, Mixpanel > 1%.

## New Pages (2026-06-05)
- Built: `parallels-desktop-pricing-2026-plans-costs-what-you-actually-pay.html`
  CJ Advertiser 2005415, EPC $31.65 (highest of all CJ programs), `/go/parallels` already live.
  No competing pages existed. Covers Standard ($99.99/yr), Pro ($119.99/yr), Business ($149.99/user/yr).
  Key angle: subscription-only trap + Windows license sold separately.

## Tasks Completed (archive)
- 2026-06-05: Scaled pricing-change pattern to 6 tools + baked generator overrides.
- 2026-06-05: Wrote CLAUDE.md operating manual + this MEMORY.md.
- 2026-06-06: Built revenue_intelligence.py (revenue layer) + wired into daily CI agent.
  Drafted PartnerStack ban appeal (Nina R ticket #115498 = evidence the dup account was
  caused by their email-bounce blocklist, not fraud).
- 2026-06-05: CEO Daily — CTR rewrites on 4 climb-zone pages, new Parallels pricing page.

## Revenue Hunter Session 2026-06-05 (Evening)

### Gmail Affiliate Status Update
- **Fiverr (Awin ID 6288)**: Approved 2026-06-03. `/go/fiverr` tracking links already correct in _redirects (awinmid=6288, awinaffid=2917137). No action needed.
- **AWeber (CJ 5111249)**: Approved 2026-05-13. `/go/aweber` with real CJ link (kqzyfj.com) already in _redirects. No action needed.
- **FreshBooks Awin**: REJECTED — program was "FreshBooks_Closing 06.01.2026". Dead end. Explore FreshBooks via ShareASale instead.
- **Impact.com**: Login alerts show active access. Support ticket #831603 confirmed only Semrush is partnered on account 7269601. HubSpot + 1Password still PENDING approval.
- **PartnerStack LOCKED**: Network profile limitation since 2026-06-04 due to "association with potentially fraudulent accounts". Appeal filed 2026-06-05 to networkquality@partnerstack.com (Ticket 115928). ClickUp DECLINED by ClickUp specifically. ActiveCampaign is sending onboarding emails (portal access exists) but the account lock may prevent tracking. Check PartnerStack portal directly.
- **HubSpot direct affiliate**: Rejected May 2026 via affiliates@hubspot.com — insufficient traffic. Re-apply at ~10K monthly clicks.
- **Wix via Impact**: Application sent 2026-06-01 to Wix (5514169). Still pending.

### CTR Fixes Applied (Revenue Hunter 2026-06-05 evening)
Targeted 1,800+ impressions/month that were generating near-zero clicks:
- `ramp-pricing-history-2026`: "April, May & June Updates" → pos 3.7, 121 impr, 0 clicks for "ramp pricing change june 2026"
- `does-notion-have-free-plan`: "[Yes] — 4 Limits, Restrictions & Workarounds (June)" → 557 impr, 0 clicks
- `does-sentry-have-free-plan`: "[Yes] — 5K Event Cap & All Free Tier Limits Explained" → 528 impr, 0 clicks
- `does-bitwarden-have-free-plan`: "Limitations 2026" pattern → pos 4-7
- `mixpanel-pricing`: "Pricing Changes 2026" → 742 impr @ pos 13.7, 0 clicks
- `nordlayer-pricing`: "Price 2026" → 97 impr @ pos 11.2, 0 clicks
Measure GSC CTR in 14-21 days. Target: Ramp history >1%, Notion/Sentry >0.5%.

### New Page Built
- `aweber-pricing-2026-plans-costs-what-you-actually-pay.html` (AWeber CJ active, $10-$300/conversion)
  - Plans: Free (500 subs), Lite $12.50/mo, Plus $20/mo, Unlimited $899/mo (all annual base rates)
  - Subscriber-count scaling clearly disclosed in hidden costs section
  - Baked into `generate_pricing_pages_v3.py` PRICING dict — durable across nightly runs
  - CTA: `/go/aweber`

### Duplicate Intent Alert (Not Fixed — Monitor)
- Two competing pages for "semrush vs moz": `semrush-vs-moz-which-is-better-in-2026.html` AND `semrush-vs-moz-pro-which-is-better-in-2026.html`
- Both ranking pos 66-68 with ~550 combined impressions/month and 0 clicks
- Fix: consolidate to one page + 301 redirect. Discuss with owner before doing — destructive action.
