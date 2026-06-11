# SaaSpare 90-Day Aggressive Profit Plan

**Date:** 2026-06-11 · **Status:** Approved by Kaylan (brainstorm session)
**Baseline:** ~66 clicks/28d (GSC), most top revenue-weighted pages on
PLACEHOLDER affiliate links, biggest programs pending approval. Dollar values
modelled from network benchmarks until `IMPACT_API_TOKEN` supplies real EPC.

## Goal

Maximise real commission revenue within 90 days. Owner commits several
hours/week of personal actions (applications, link fetches, outreach) and is
open to small spend (< $50 without escalation). Honest modelling only — no
vanity numbers.

## Targets (day 90)

- Traffic: 300–500 clicks/mo (from ~66/28d).
- First commissions: weeks 3–6 (approval-dependent).
- Modelled run-rate: $150–400/mo by day 90.
- Zero top-20 revenue pages pointing at placeholder links by week 2.

## Phase 1 — Money path (weeks 1–2)

Traffic into dead links earns $0 forever; this phase outranks everything.

**Owner actions (the standing list, maintained in Obsidian):**
1. Send the HubSpot affiliate Gmail draft (already drafted; $250–1000/conv).
2. Fetch 6 waiting CJ deep links at app.cj.com → Links: Constant Contact
   (approved), GetResponse, Proton, Elementor, AWeber, Parallels.
3. Apply to FreshBooks on Awin (publisher 2917137 active).
4. Apply to Ramp's affiliate program — the #1 revenue page
   (`ramp-pricing-…`, 709 impr, pos 9.4, ~$71/mo modelled) is a placeholder.
5. 2026-06-18 (not before): re-apply to PartnerStack for Monday.com and Xero.

**Claude/JARVIS actions:**
- Wire every link the owner hands over within the hour (`_redirects`),
  verify all `/go/` routes resolve to tracked network URLs.
- Add earning-program secondary CTAs to placeholder pages so existing traffic
  monetises immediately (e.g. Ramp pricing page also offers an earning
  alternative comparison CTA) — without removing or faking the primary tool
  content.
- Record EPC baseline per page for before/after measurement.

## Phase 2 — Traffic to earners (weeks 3–8)

Weekly sprint, every week:
- **Climb-zone sprint:** top 5 pages by modelled $ uplift at position 8–30 —
  buyer-intent title/meta rewrite, FAQPage schema upgrade, pricing-change
  tracker block, above-fold verdict, hub internal links. Baked into
  generators, never HTML-only.
- **2 content clusters/week** around programs that ALREADY earn: Semrush
  (priority — `semrush-vs-moz` has 1,366 impressions stranded at pos 70;
  needs content + links, not metadata), Shopify, NordVPN, Incogni,
  ActiveCampaign. Each page meets the quality floor: ≥800 words, real data
  point, real FAQs, hub links.
- **Experiment discipline:** hypothesis with a number → ~10 pages → GSC
  measure at 21 days → expand winners, revert >10% losers. Logged in
  MEMORY.md/Obsidian.

## Phase 3 — Scale (weeks 9–13)

- Newsletter activation (the honest-newsletter block is already live sitewide).
- Digital-PR / outreach link building using owner hours — target the Semrush
  and pricing-index clusters first (they're rankings-limited, not
  content-limited).
- New program applications chosen by the acquisition matrix
  (`program-acquisition.md`) as traffic data proves out.
- Owner supplies `IMPACT_API_TOKEN` → revenue_intelligence.py switches from
  modelled to real EPC/conversions; re-rank everything on real dollars.

## Cadence & measurement

- Daily: automated audit + revenue_intelligence (already in CI).
- Weekly (Mon): read `revenue-opportunities.md`, refresh the owner action
  list in Obsidian, pick the sprint's top 5.
- Alert thresholds stand: impressions −20% WoW → investigate first.

## Hard rules (unchanged, non-negotiable)

No fabricated pricing/limits/coupons/ratings; disclosure visible on every
monetised page; durable changes baked into generators; canonical/sitemap
integrity; pytest 57-pass gate before every push; protected paths untouched.
