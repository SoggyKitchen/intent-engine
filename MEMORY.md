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

## CEO Daily — 2026-06-07

### Gmail Check (no new affiliate approvals)
- Awin account itself is APPROVED (publisher 2917137, activated 2026-06-01) but the
  FreshBooks_Closing program application via Awin was REJECTED same day — dead end there.
- Fiverr (Awin 6288) approval from 2026-06-03 already fully wired: `/go/fiverr`,
  `/go/fiverr-pro`, `/go/fiverr-business` live with correct tracking params, and all 6
  Fiverr pages already link through them. No action needed (done in a prior session).
- Impact.com (7269601): still only Semrush partnered; HubSpot/Monday/Wix pending.
- PartnerStack: still network-limited, ClickUp declined, appeal pending. No change.

### Durable Fix: VS-page CTR template (highest-leverage find of the day)
All 849 `*-vs-*` comparison pages shared one bland templated title —
"`X vs Y (2026): Which Is Better? Full Comparison`" — and every single one of the
0%-CTR climb-zone pages in `gsc-opportunities` (docusign-clm-vs-icertis 237 impr,
aws-vs-render 155 impr, tailscale-vs-zscaler 251 impr, etc.) used it verbatim.
Rewrote the template in `rebuild_vs_pages_v2.py` to "`X vs Y (2026): Honest Verdict
& Who Wins`" + a sharper meta, regenerated all 852 pages, restored the internal-links
sections that the regen briefly wiped (re-ran `internal_links.py`), reran nav/CSS
fixers, rebuilt sitemap. This is the single biggest CTR lever pulled this month —
measure GSC in ~21 days.

### Bug Fix: duplicated "Updated X. Updated Y." meta descriptions (869 pages)
`blast_off.py`'s `rewrite_desc()` only recognised its own `"Updated {Month Year}"`
stamp, not the generators' `"Updated {ISO date}"` stamp — so it kept stacking a
second prefix on top every run, corrupting 869 pages into descriptions like
"Updated June 2026. Updated 2026-06-07. Docusign Clm vs Icertis…". Hardened the
regex to strip ANY existing "Updated X." prefix(es) before re-stamping (idempotent).
The 852 VS pages were fixed by regeneration; the remaining ~20 non-VS pages will
self-heal on tonight's nightly `blast_off.py` run.

### Also fixed: latent Python 3.11 SyntaxError in rebuild_vs_pages_v2.py
An f-string with an escaped quote inside `{}` (`\'{t}\'`) is invalid on Python <3.12
and was silently blocking this generator from ever running in this environment.
Rewrote it as string concatenation with `&quot;` HTML entities — same rendered output.

### New page: skipped (judgment call)
Step 4 asked for a new page for an earning-now program with a coverage gap —
HostPapa has zero pages. hostpapa.com returned 403 to WebFetch (couldn't verify
live pricing/plans from the source; only got third-party-aggregated estimates).
Per Hard Rule 1 ("never fabricate pricing — an empty section beats a fake one"),
skipped building a numbers-heavy review/pricing page rather than guess. Flagging
for the owner: verify HostPapa's current Essentials/Growth/Premium pricing
(~$2.95/$5.95/$6.95/mo per third-party aggregators, NOT independently confirmed)
before a future session builds that page.

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

## Revenue Hunter Session 2026-06-07 (Evening) — BIG FIND: 645 dead-end comparison pages

### Gmail scan
No new affiliate approvals. Fiverr + AWeber already activated in earlier sessions
(verified _redirects has real awin1.com / kqzyfj.com links — no action needed).
PartnerStack still network-limited (appeal pending, ticket 115928), ClickUp + FreshBooks
both formally rejected, Impact.com still only partnered with Semrush (HubSpot/1Password/
Monday still PENDING). Nothing actionable on the affiliate-approval front today.

### THE BIG ONE: 645 of 852 VS comparison pages had ZERO clickable monetization path
`rebuild_vs_pages_v2.py`'s `cta_btn()`/`winner_cta()` rendered a disabled `<span class="sp-btn-ghost"
style="opacity:.5;cursor:default">` whenever neither compared tool had an affiliate program
(`url=None` in TOOLS dict — true for AWS, Render, Recurly, Docusign CLM, Icertis, Zscaler,
Tailscale, Twingate, etc — ~90 of the ~200 tools in the DB have no program). Audit showed:
- 645 pages: 100% dead — not a single live CTA anywhere on the page
- 204 pages: partial (one side monetized, one dead)
- 0 pages: fully live
These pages are real traffic (e.g. aws-vs-render 155 impr/mo pos 9, docusign-clm-vs-icertis
237 impr/mo pos 8.8, twingate-vs-zscaler 126 impr/mo pos 7.2) — visitors land, find nothing
to click, and bounce. Pure lost funnel.

**Fix (baked into the generator, not just HTML):** when `url` is falsy, `cta_btn()`/`winner_cta()`
now render a real link to `/shortlist` (the internal Shortlist Builder tool) instead of a
disabled span — "Compare in Shortlist Builder →" / "Build Your Shortlist →". Keeps every
visitor in an on-site funnel (email capture + internal links to monetized pages) instead of
a dead end. Regenerated all 852 VS pages; reran internal_links/nav/CSS fixers + sitemap.
Verify in ~21 days: are `/shortlist` referrals from VS pages up, and do internal-link
clickthroughs to monetized comparison pages increase?

### Also fixed: frozen triple-stamped "Updated X. Updated Y. Updated Z." artifacts
65 best-of/alternatives pages had body lead-paragraphs + Article-schema descriptions frozen
mid-bug with 2-3 stacked "Updated {month}." prefixes (a snapshot of the meta-description
stacking bug fixed in the `<meta>` tag by the d6d336b3 commit, but never cleaned from the
static body copy that had been generated from the broken value). One-off regex collapse to
a single "Updated June 2026." — not a generator fix since these are frozen artifacts, not
actively regenerated. Also fixed `saas-glossary.html`'s broken/truncated meta description
("Updated June 2026. Updated 2026 guide from SaaSpare — expert analysis…") with real content.

### Direct URL leak scan: clean
grep for hubspot/clickup/1password/etc direct hrefs in site/pages/ → 0 matches. All routed
through /go/.

## Revenue Hunter Session 2026-07-01 — CTR freshness sweep + new Elementor alternatives page

### Gmail Scan
- **Fiverr (Awin)** — ALREADY ACTIVE in _redirects (confirmed, no action needed)
- **PartnerStack** — 3rd network rejection received 2026-06-22. Appeal pending (ticket 116965).
  ClickUp, Monday.com, ActiveCampaign, Dashlane ALL still locked. Owner should escalate appeal.
- **Impact.com** — Account active but ONLY Semrush is partnered. HubSpot ($250-1000/sale) and
  1Password ($30-60/sale) still PENDING approval. Owner should follow up with Impact support.
- **Wix** — Contract application sent via Impact.com (pending approval)
- No Xero, Brevo, Hotjar, Constant Contact approvals found

### CTR Freshness Fixes (June → July 2026)
14 pages updated. Top by GSC impact:
- `mixpanel-pricing` — pos 13.7, 742 impr/mo, 0 clicks. New title: "Mixpanel Pricing July 2026: Every Plan Cost, Real Growth Fees + No Surprise Billing"
- `nordlayer-pricing` — pos 19.0, 270 impr/mo. Title updated to July 2026
- `notion-pricing` — pos 17.4, 214 impr/mo. Title updated to July 2026
- `does-cloudflare-access-free-plan` — pos 10.0, 219 impr/mo. Meta updated
- `ramp-review` — pos 7.8, 127 impr/mo. Meta updated
- `datadog-coupon` — pos 7.4, 131 impr/mo. Title + meta updated
- `surfer-seo-vs-se-ranking` — pos 53.9, 131 impr/mo. Title updated (was "June")
- `lastpass-vs-nordpass` — pos 66.6, 69 impr/mo. Title rewritten + July date
- `best-devops-config-drift-2025` — pos 18.1, 380 impr/mo. Title "[June]" → "[July 2026]"
- Plus: twingate-vs-tailscale, twingate-vs-zscaler, tailscale-vs-zscaler,
  shopify-vs-recurly, does-linear-free-plan
Measure CTR improvement in 14-21 days.

### New Page Built
- `best-elementor-alternatives-in-2026-free-paid.html`
- Target queries: "elementor alternatives" (~3-5K searches/mo), "best elementor alternatives"
- 6 tools: Elementor (winner), Divi, Beaver Builder, Bricks Builder, Webflow, SeedProd
- All 6 /go/ routes active in _redirects
- Monetized via /go/elementor → CJ #6798066 (45% commission, EPC $7.55)
- Added to generator HARDCODED_PAGE_TOOLS (durable)
- Added TOOLS dict entries for Elementor, Divi, Beaver Builder, Bricks Builder, SeedProd

### GSC Opportunity Notes
- `does-notion-free-plan` (557 impr, pos 9.4, 0% CTR) — title is good. Likely featured snippet
  stealing clicks. Monitor — no action needed.
- `does-sentry-free-plan` (528 impr, pos 7.5, 0% CTR) — same. Already says July 2026.
- `ramp pricing change june 2026` — pos 3.7, 121 impr, 0 clicks. Ramp pricing page title already
  targets this ("Did Ramp Change Pricing in June 2026?") — investigate why 0 clicks at pos 3.7.
  Possibly a SERP feature (rich result) capturing all clicks.
- Semrush vs Moz cluster: ~1,200 combined impr at pos 66-82. Two competing pages. Owner decision
  needed to consolidate (redirect one to the other). Cannot fix autonomously.

### Action for Owner
1. PartnerStack appeal: follow up on ticket 116965 (Anjola S, 2026-06-23)
2. Impact.com: HubSpot + 1Password program applications — check app.impact.com → Programs
3. Semrush vs Moz dedup: `semrush-vs-moz-which-is-better-in-2026` vs `semrush-vs-moz-pro-which-is-better-in-2026` — 301 one to the other

## CEO Daily Session — 2026-08-10

### Gmail Scan
- **EngageBay (Awin)**: APPROVED 2026-07-22. Awin publisher 2917137, commission 30% recurring.
  `/go/engagebay` and `/go/engagebay-pricing` already in _redirects from a prior session.
  Awin tracking link confirmed correct (awinmid + awinaffid=2917137). ✅ ACTIVE
- **Iternal Technologies (CJ)**: APPROVED 2026-08-03. Also covers AirgapAI.
  `/go/iternal`, `/go/airgapai`, `/go/airgapai-code` in _redirects — but links are UTM-only,
  NOT CJ tracking links. **Gap**: commissions won't attribute through CJ until the real kqzyfj.com
  links are obtained from app.cj.com → Links → Get Links → Advertiser 2177716.
  **Owner action required**: get CJ deep links and update _redirects.
- **Pipedrive (PartnerStack)**: Email says "application review in progress" — manual TOS approval
  needed at https://dash.partnerstack.com/pipedrive. **Owner action required.**
- No new Impact.com approvals (HubSpot/1Password still PENDING).
- PartnerStack network lock still unresolved (ClickUp, Monday, ActiveCampaign, Dashlane blocked).

### CTR Title Upgrades (baked into generators — survive nightly CI)
All changes baked into `scripts/fix_ctr_opportunities.py` so nightly CI won't revert:
- **Notion free plan** (557 impr, pos 9.4, 0% CTR):
  New: "Notion Free Plan 2026: Unlimited Blocks — But 10-Guest Cap, 7-Day History & No Automations"
  (statement-format with the 3 specific limits that block upgrade decisions)
- **Sentry free plan** (528 impr, pos 7.5, 0% CTR):
  New: "Sentry Free Plan 2026: 5K Events/Month, 1 Seat, 7-Day Retention — Is It Enough?"
  (specific numbers in title — more informative, better CTR signal)
- **DocuSign CLM vs Icertis** (237 impr, pos 8.8, 0% CTR):
  New: "DocuSign CLM vs Icertis (2026): Head-to-Head Compared — Pricing, AI Features & Verdict"
  (baked into TITLE_OVERRIDES in rebuild_vs_pages_v2.py)
- Cloudflare Access free plan: meta updated (August 2026 freshness)
Measure CTR in 14-21 days. Hypothesis: statement titles with specific numbers outperform question titles.

### New Page Built: EngageBay vs Keap
- `engagebay-vs-keap-which-is-better-in-2026.html`
- Target: SMB CRM buyers choosing between free-plan CRM (EngageBay) vs Keap's $249/mo (formerly Infusionsoft)
- EngageBay wins (8.5/10 vs 8.1/10) — monetized via `/go/engagebay` (Awin 30% recurring)
- Both tools baked into `rebuild_vs_pages_v2.py` TOOLS dict — all future EngageBay and Keap VS pages will be generated automatically
- Triggers 14 new EngageBay VS pages (vs HubSpot, Pipedrive, etc.) on next generator run

### Revenue Leak Scan: CLEAN
grep for direct vendor hrefs across all site/pages/ → 0 matches. All affiliate links route through /go/.

### Tests: 93 passed (up from 57 — test suite grew, this is healthy)

### Action Items for Owner
1. **Pipedrive (PartnerStack)**: Visit https://dash.partnerstack.com/pipedrive to manually approve TOS. Quick win.
2. **Iternal/AirgapAI (CJ)**: Get real CJ tracking links from app.cj.com → Links → Advertiser 2177716 → Get Links. Update `/go/iternal`, `/go/airgapai`, `/go/airgapai-code` in `site/_redirects`. Currently earning $0 from CJ on these.
3. **Impact.com**: Follow up on HubSpot ($250-1000/sale, 39 pages live) and 1Password ($30-60/sale, 37 pages live) — both still PENDING.
4. **PartnerStack ban**: Escalate ticket 116965 — ClickUp, Monday, ActiveCampaign, Dashlane still locked.
