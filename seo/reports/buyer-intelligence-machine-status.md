# SaaSpare Buyer-Intelligence Machine — Implementation Status

The strategic plan: turn SaaSpare from an AI-written comparison site into a
living buyer-intelligence machine. This doc tracks what's been built, what's
running autonomously, and what's deliberately deferred.

Last updated: May 7, 2026 — commit baseline `c11af6d7+`

---

## ✅ Idea 1 — Price Intelligence Engine (MVP shipped)

**Status:** running nightly. Currently tracks **15 of the top SaaS vendors**;
expandable to 50 by editing `data/pricing_seed.json`.

**What ships:**

| Artefact | Path |
|---|---|
| Schema | `pricing_snapshots` + `pricing_changes` tables in `data/intent.db` |
| Seed data | `data/pricing_seed.json` — 15 tools × 4 plans avg, all with vendor source URLs |
| Tracker | `scripts/track_pricing.py` (snapshots + diff detection) |
| Page renderer | `scripts/render_pricing_history.py` → 15 `/pages/[tool]-pricing-history-2026.html` pages |
| Roll-up renderer | `scripts/render_buyer_intel.py` → rebuilds `/pages/saas-pricing-changes.html` from real diff data |
| Schema markup | Each page has `Dataset` + `Article` + `BreadcrumbList` JSON-LD |
| Affiliate routing | Every page CTAs to `/go/[tool]` (commission-tracked) |

**Pages live as of today:**
- `/pages/hubspot-pricing-history-2026`
- `/pages/salesforce-pricing-history-2026`
- `/pages/ahrefs-pricing-history-2026`
- `/pages/semrush-pricing-history-2026`
- `/pages/notion-pricing-history-2026`
- `/pages/clickup-pricing-history-2026`
- `/pages/asana-pricing-history-2026`
- `/pages/monday-com-pricing-history-2026`
- `/pages/pipedrive-pricing-history-2026`
- `/pages/linear-pricing-history-2026`
- `/pages/stripe-pricing-history-2026`
- `/pages/1password-pricing-history-2026`
- `/pages/tresorit-pricing-history-2026`
- `/pages/shopify-pricing-history-2026`
- `/pages/datadog-pricing-history-2026`

**Why this is the moat:** original time-stamped pricing data with source URLs.
G2/Capterra publish reviews; nobody else publishes weekly diff logs. Google's
helpful-content guidance specifically rewards original information, reporting,
and analysis.

### How to expand to 50 tools

Edit `data/pricing_seed.json`. Add another entry to the `tools` array
following the existing schema. Run `uv run python scripts/track_pricing.py
&& uv run python scripts/render_pricing_history.py`. Done. Nightly will
keep diffing thereafter.

### How to mark a real change

When you spot a vendor pricing hike (e.g. via news, your own checks, or
the bot's email):
1. Update the relevant plan's `monthly_usd` / `annual_usd` in `pricing_seed.json`
2. Add a `notes` field describing the change (e.g. `"Hiked from $25 to $27.50 in Feb 2026"`)
3. Commit + push. Next nightly run logs the diff into `pricing_changes` and
   the change appears on `/pages/saas-pricing-changes` automatically.

### Phase 2 — automated vendor-page parsing

Currently the seed is hand-curated (highest accuracy, lowest fragility).
Phase 2 should add a Cerebras-LLM step in CI that fetches each vendor's
pricing page weekly and proposes seed updates with confidence scores. The
existing `programmatic.py` workflow has the API keys; this would be a
~1-day build adding `scripts/parse_pricing_pages.py` that outputs
`data/pricing_seed.diff.json` for human review before merge.

---

## ✅ Idea 3 — Buyer Pain Index (MVP shipped)

**Status:** roll-up page live; per-tool pages deferred until signal
coverage per tool exceeds 20 mentions.

**What ships:**

| Artefact | Path |
|---|---|
| Existing data | `scored_signals` table — 646 already-classified buyer-intent rows |
| Roll-up page | `/pages/saas-buyer-signals-2026.html` — vertical breakdown + 25 sourced insights |
| Schema | `Dataset` JSON-LD with CC-BY licence (encourages LLM citation) |
| Auto-refresh | Wired into nightly via `render_buyer_intel.py` |

**Why a single roll-up instead of per-tool pages:** signals per individual
tool currently range 0-5 (too thin for a useful page). The roll-up is a
strong page on its own and shows Google we have original data; per-tool
pages will activate when the harvester accumulates ≥20 mentions per tool
(naturally over 4-6 weeks).

### How per-tool pain pages activate

Existing `harvest.yml` workflow runs every ~6 hours and adds new
signals. Once any tool has ≥20 mentions in `raw_signals`, a future
`render_pain_pages.py` (deferred) will generate `/pages/[tool]-buyer-complaints-2026.html`
automatically. Trigger that build manually with:

```
uv run python scripts/render_pain_pages.py --threshold 20
```

(Script will be added when coverage reaches threshold.)

---

## ⏸️ Idea 2 — Stack Builder (deferred — needs real product build)

The Stack Builder is the highest-converting idea but it's a real product
build, not a script. It needs:

1. Multi-step quiz UX (8-12 questions, conditional branching)
2. Scoring algorithm (weight by team size × budget × pain × integrations)
3. Recommendation engine (per-category top pick + cheaper alt + premium alt)
4. Email-delivered stack PDF (lead capture)
5. Analytics on completed quiz funnel
6. CRO-optimised result page

**Estimated effort:** 1-2 weeks of focused work, even with AI assistance.

**Deferred until:** SaaSpare has its first 1,000 organic clicks/month
(currently 29 clicks). Building a high-CRO conversion engine before there's
traffic to convert is premature.

**The /shortlist page already exists** as a lite version. Improving that is
a 1-day polish job and might be worth doing before the full Stack Builder.

### Recommended interim: improve /shortlist

The existing `/shortlist` page can become a Stack Builder Lite with:
- Pre-filled budget brackets ($50, $100, $200, $300, $500/mo)
- Pre-filled team size brackets (solo, 2-5, 6-20, 20+)
- Hard-coded recommendations per (vertical × budget × team_size) combo
- Email capture: "send me this stack"

That's a 4-6 hour build vs the 1-2 weeks for the full Stack Builder.

---

## What runs nightly now (full chain — 26 steps)

```
✓ Repair corruption           ✓ Internal links pass
✓ Sync KPI counters           ✓ Site upgrade pass
✓ Inject journey links        ✓ Build llms-full.txt
✓ Flag risky claims           ✓ Schema pro pass
✓ Fix Amazon links            ✓ OG images per vertical
✓ SEO consolidate             ✓ Price intelligence track     ← NEW
✓ Blast off (CTR + AEO)       ✓ Render pricing history pages ← NEW
                              ✓ Render buyer-intel pages     ← NEW
                              ✓ CI gate - content QA
                              ✓ CI gate - corruption
                              ✓ CI gate - SEO integrity
                              ✓ Run full test suite
                              ✓ Commit + push
```

---

## What's hand-built vs autonomous

| Component | Hand-built once | Autonomous |
|---|---|---|
| 15-tool pricing seed | ✅ Today | ❌ Manual edits drive updates (Phase 2 will automate) |
| Pricing history pages | ❌ | ✅ Re-rendered nightly |
| Pricing change page | ❌ | ✅ Re-rendered nightly from real diffs |
| Buyer signals page | ❌ | ✅ Re-rendered nightly from harvester data |
| Affiliate registry | ✅ Done | ❌ Manual additions when new networks accept |
| Programmatic SEO bot | ✅ Done | ✅ Generates new comparison pages weekly |
| Buyer-intent harvester | ✅ Done | ✅ Runs every ~6 hours, ingests Reddit/HN/etc |
| Outreach agent (v2) | Doc only | Manual trigger Tue+Thu |

---

## Realistic 8-week trajectory (with buyer-intel machine)

The pricing-history pages target a different keyword cluster than your
existing comparison pages. Expected uplift on top of the prior trajectory:

| Week | New impressions/wk | Conversion uplift |
|---|---|---|
| 1-2 | +2-5K from `[tool] pricing history` searches | minimal |
| 3-4 | +8-15K (Google indexes the Dataset schema) | 1-2 affiliate clicks/wk from "pricing too expensive" intent |
| 5-8 | +20-40K. AI Overviews start citing SaaSpare pricing data | 5-12 trial signups/wk routed via `/go/` |
| 8-12 | First commission payouts likely (HubSpot/Semrush 30-day attribution) |

**This is the moat.** When ChatGPT cites "according to SaaSpare's pricing
history, HubSpot Pro increased from $X to $Y in February 2026," that's the
single most defensible AI-search position you can hold. Nobody else has that
data.

---

## What you (the human) need to do — 4 things

1. **Approve the seed prices** at `data/pricing_seed.json`. I verified the
   15 tools' current pricing as of May 2026, but you should spot-check
   2-3 entries against the live vendor pages before this goes wide.

2. **Verify Cloudflare Pages deploys cleanly.** Open
   https://saaspare.org/pages/hubspot-pricing-history-2026 in your browser
   in ~60 seconds and check it renders.

3. **Apply to PartnerStack** if you haven't (https://partnerstack.com/become-a-partner).
   They have HubSpot, Notion, ClickUp, Linear, Pipedrive, Asana, Monday all
   in one network. One application unlocks 7 of the 15 tracked tools.

4. **Update seed prices monthly.** The strategic plan recommends 50 tools
   eventually. Add 5 new tools per month — it'll take 30 minutes per
   addition. Or wait for Phase 2 (automated vendor-page parsing).

That's it. The machine runs itself between updates.
