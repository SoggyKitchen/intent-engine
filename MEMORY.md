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

## Known issues / pending (owner actions)
- PartnerStack ban appeal pending (ClickUp, ActiveCampaign, Monday, Dashlane locked).
- Impact.com applications pending: HubSpot (39 pages), 1Password (37 pages).
- FreshBooks Awin closed — needs replacement program.
- Newsletter form has no backend (Beehiiv pending).
- Ahrefs/Semrush MCPs gated behind API-plan upgrades — GSC engine is sufficient meanwhile.

## Tasks Completed (archive)
- 2026-06-05: Scaled pricing-change pattern to 6 tools + baked generator overrides.
- 2026-06-05: Wrote CLAUDE.md operating manual + this MEMORY.md.
