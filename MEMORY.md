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
