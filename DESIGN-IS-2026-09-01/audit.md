# Design Is — SaaSpare.org audit, 2026-09-01

**Compression note:** the skill specifies five artifacts produced by five evidence
subagents. I ran a single-operator version and consolidated into one file. Scoring
is unchanged (orchestrator-only, per-principle anchors applied verbatim, ties
broken downward). Every score below cites evidence I measured directly today.

## 00 — Scope

- **Audited:** live saaspare.org — homepage, `/pages/` library, and a representative
  money page (`hubspot-pricing-2026-plans-costs-what-you-actually-pay`)
- **Primary user:** a B2B software buyer comparing tools on real cost
- **Primary task:** get an honest pricing/comparison answer without opening ten vendor tabs
- **Constraints:** dark brand system (`saaspare-design`), static site on Cloudflare Pages,
  affiliate disclosure legally required on every monetised page
- **Reference competitor:** saaspare.com (42 tools, 138 verified user reviews)

## 01 — Evidence (measured 2026-09-01)

| Signal | Value | Source |
|---|---|---|
| Mobile Performance | 73/100 | PageSpeed Insights, live URL |
| Mobile LCP | 4.8s (element render delay 2,320ms) | PSI |
| Accessibility | 93/100 | PSI |
| Best Practices / SEO | 100 / 100 | PSI |
| CSS weight (3 render-blocking files) | 72 KB | `du` on `site/assets` |
| JS weight | 64 KB | `du` on `site/assets` |
| Unused JS | 65 KiB | PSI diagnostics |
| Main-thread work | 2.8s | PSI diagnostics |
| Distinct colours declared | 69 | `saaspare-v2.css` token grep |
| Keyframe animations | 9 | `motion.css` |
| `prefers-reduced-motion` handling | 6 occurrences | `site/assets/*.css` |
| Focus states | 13 `:focus` + 2 `:focus-visible` | `site/assets/*.css` |
| Loading state | skeleton, 40 occurrences | `site/assets/*.css` |
| Empty state | 1 occurrence | `site/assets/*.css` |
| Error state | 0 occurrences | `site/assets/*.css` |
| Disabled state | 0 in shared CSS (page-local only) | `site/assets/*.css` |
| Idle-running animation | `orbFloat` 12s infinite, `spMarkGlow` 4s infinite, wave-dots + plexus canvas | `motion.css`, homepage |
| Interrupting chrome on load | sticky affiliate bar, exit-intent newsletter modal, floating Decision Trail | money-page source |
| Orphan-style debt | `fix_light_theme_blocks.py`, `fix_universal_nav.py` legacy-nav path (550 pages) exist as standing repair scripts | `scripts/` |

## 02 — Scorecard

1. **Innovative — 2/3.** ROI Calculator, Shortlist Builder, Deal Radar and Decision Trail
   are real additions over G2/Capterra's form; the underlying comparison-directory pattern
   is still borrowed. Refreshes an existing pattern with a clear improvement.
2. **Useful — 2/3.** Primary task is directly supported, but the library grid is
   `visibility:hidden` until JS `render()` runs, and mobile LCP is 4.8s — the task completes
   with avoidable friction.
3. **Aesthetic — 2/3.** One coherent system (dark ground, single pink accent, Inter, 4px grid).
   Docked one level for orphan styles: standing repair scripts exist precisely because
   light-theme blocks and legacy inline navs keep reappearing.
4. **Understandable — 2/3.** Nav is plain language, but "Deal Radar" and "Decision Trail"
   are house coinages a first-time buyer can't name unaided.
5. **Unobtrusive — 1/3.** Sticky affiliate bar + exit-intent modal + floating Decision Trail
   + always-on ambient animation. Decoration competes with content.
6. **Honest — 2/3.** Affiliate disclosure on every monetised page, "no paid placements"
   is true, `content_qa.py` gates fabrication. Docked one level because fabricated
   "hands-on tested" claims shipped and had to be stripped — the guardrail works, but
   it fired.
7. **Long-lasting — 1/3.** Three dated trend markers: glassmorphism cards, gradient
   clipped text, ambient blurred glow orbs. Reads as 2025-26.
8. **Thorough — 2/3.** Focus, loading (skeleton) and empty all present;
   `prefers-reduced-motion` respected. Error state absent from shared CSS.
9. **Environmentally friendly — 2/3.** 136 KB total assets is lean and motion is gated,
   but four animations run on an idle screen, so it misses the "no idle animation" bar.
10. **As little design as possible — 1/3.** The homepage runs 14+ distinct sections before
    the footer, plus three floating/interrupting elements. Well over five removable items.

**Total: 17/30**

## 03 — Verdict

**REDESIGN** — total is below 20. No principle scored 0, so nothing here is broken;
the design is over-built rather than wrong.

Highest-leverage moves, in order:

1. **#10 / #5 — cut the homepage.** 14+ sections and three floating elements dilute a
   single job: get the buyer to an answer. Target 6 sections, zero interrupting chrome.
2. **#5 — kill the exit-intent modal.** It is the single most intrusive element on a site
   whose whole pitch is "no dark patterns" — it also undercuts principle #6.
3. **#7 — retire the trend markers.** Drop glassmorphism, gradient text and glow orbs;
   keep the dark ground and the single pink accent, which are brand, not fashion.
4. **#2 — server-render the library grid.** `visibility:hidden` until JS is a
   task-blocking dependency on a page whose entire purpose is browsing.
5. **#8 — add the missing error state** to shared CSS so failures aren't browser-default.

## 04 — Handoff

Not emitted. Design is not the binding constraint on this business right now:
the site takes 5 organic clicks per 29 days across 1,591 pages, and 1,171 of those
pages are "Crawled — currently not indexed". A redesign would be polishing a car
with no engine. This audit is on the record so it can be picked up after the
indexing and authority problem moves — see the strategic note in the session summary.
