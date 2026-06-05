# SaaSpare — Project Context & Operating Instructions

## The Business
SaaSpare.org is an independent B2B SaaS comparison and affiliate site.
- **Owner:** Kaylan von Papen
- **Repo:** SoggyKitchen/intent-engine
- **Deploy:** Cloudflare Pages (auto-deploys on push to main)
- **GA4:** G-RLYVYV8WQJ | **CJ Publisher ID:** 101733230 | **Impact Publisher ID:** 7269601 | **Awin:** PENDING (applied 2026-06-01)
- **ABN:** 20 602 197 525

## KPI Priority
Revenue → Traffic → Rankings → Conversion → Trust → Technical → Polish

## The SEO Engine (your daily spine — USE IT, don't rebuild it)
`scripts/seo/seo_agent.py` is a ~1,500-line autonomous engine. Run with `uv`:
```bash
uv run python scripts/seo/seo_agent.py --mode audit       # read-only: crawl + live GSC + 25 reports
uv run python scripts/seo/seo_agent.py --mode apply-safe  # also applies guardrailed metadata/schema fixes
```
Read these reports before deciding anything (in `seo/reports/`):
- `gsc-opportunities.json/.md` — **LIVE Search Console data**, ranked by buyer-intent
  opportunity score (impressions, low CTR, position 8–30, buyer keywords). Your daily to-do list.
- `revenue-priorities.md` — pages ranked by monetisation potential.
- `site-health.md` — health score + fastest path to next tier.
- `top-100-fixes.md`, `thin-pages.md`, `conversion-issues.md`, `link-cleanup.md`,
  `schema-validation.md`, `orphan-pages.json`, `duplicate-intent.md`.

GSC is already authed via GitHub secrets. **siteUrl is `sc-domain:saaspare.org`** —
never `https://www.saaspare.org` (that returns 403). `apply-safe` refuses to touch
coupons, ratings, pricing numbers, review claims, noindex, or `STRATEGIC_PROTECTED_PATHS`.

## Daily Loop (what to actually do each session)
1. Run `--mode audit`. Read `gsc-opportunities.json`.
2. Take the top 3–5 buyer pages with `impressions > 100` and `position` 8–30 (the climb zone).
3. Per page: stronger buyer-intent title (+ year + specificity), meta with the answer +
   CTA, upgrade FAQPage schema, add pricing-change tracker block (pricing pages),
   strengthen above-fold verdict, add internal links from category hubs.
4. **Bake durable parts into the generator** (see Hard Rules), verify, commit.
5. Append learnings to `MEMORY.md`.

## Hard Rules (violating these is failure even if metrics improve)
1. **Never fabricate** pricing, plan limits, coupon codes, ratings, or "we tested" claims.
   Unverified → label it or omit it. An empty section beats a fake one.
2. **Affiliate disclosure stays visible** on every monetised page. Never strip it.
3. **Bake durable changes into the generator, not just HTML.** `generate_*_v3.py`
   regenerates pages nightly; an HTML-only edit can be overwritten. Add titles/metas/FAQs/
   data to the generator's data dict (e.g. `meta_desc=` overrides) AND confirm the
   skip-condition protects already-premium pages. Proven on Ramp/Shopify/HubSpot/Notion/
   ClickUp/Semrush/Monday pricing pages.
4. **Never break canonical URLs or the sitemap.** Canonical must match the real filename
   incl. any `7-` prefix. `content_qa.py` fails the nightly build (exit 1) on HARD issues.
5. **Off-limits:** `STRATEGIC_PROTECTED_PATHS`, `.github/workflows/*` (change only with
   reason + test), this file, `MEMORY.md`, `seo/config.json`, secrets. Never `rm -rf`,
   force-push, or `--no-verify`.

## Proven Plays (ranked by ROI — do these first)
1. **Title/meta CTR rewrites on climb-zone pages.** Pattern: `[Tool] Pricing 2026: Every
   Change, Real Cost & [Month] Update`. Highest ROI, lowest risk.
2. **Pricing-change tracker + FAQ schema** for `did [tool] change pricing` / `[tool]
   pricing [month] 2026`. Proven on Ramp (279 impr @ pos 4.3) → now 6 more tools.
3. **Replace placeholder/generic FAQ answers with real data** (some pages still ship
   "check the pricing page" boilerplate — dead weight).
4. **Fix thin pages + broken internal links** (protect existing rankings).
5. **CTA/disclosure coverage** on monetised pages missing them.
6. **Internal links from category hubs** to push pos-8–20 pages into the top 10.

## Experiments (operate like a CEO, not a content mill)
Hypothesis with a number → deploy to ~10 pages → baseline in MEMORY.md → measure GSC at
~21 days → expand if it beats control, **revert if it underperforms by >10%**. Pages with
<~100 clicks/variant are inconclusive.

## Escalate to owner ONLY when
Money > $50 · affiliate-program application/approval · legal/compliance/trust wording ·
destructive infra (DNS, Cloudflare, deleting pages) · genuinely expensive ambiguity.
Otherwise: act, verify, commit, log. No permission needed for routine optimisation.

## Design Rules (Critical — violations break the site)
1. `<body style="background:#050407;color:rgba(255,248,245,.88)">` — NO `class="sp-bg"` on body
2. JSON-LD must be in `<script type="application/ld+json">` tags — bare JSON renders as visible text
3. Nav: use `<nav id="sp-nav">` with the animated SVG logo from fix_universal_nav.py — NEVER use `class="sp-nav"` or `class="sp-topnav"`
4. Always run `uv run pytest -q` before pushing — must show 57 passed
5. CSS on every page (ALL THREE required):
   - `/assets/saaspare-v2.css`
   - `/assets/saaspare-ui.css`  ← REQUIRED — without this cards/pricing/scores show as plain text
   - `/assets/motion.css`
6. Author on all pages: Kaylan von Papen — `/authors/kaylan-von-papen`
7. After building pages, run: `uv run python scripts/fix_universal_nav.py` + `uv run python scripts/fix_inject_ui_css.py`

## Affiliate Programs

### Earning commissions now
NordVPN `/go/nordvpn` | Surfshark `/go/surfshark` | Sucuri `/go/sucuri` |
NordPass `/go/nordpass` | Contabo `/go/contabo` | HostPapa `/go/hostpapa` |
Semrush `/go/semrush` | Shopify `/go/shopify` | ElevenLabs `/go/elevenlabs`

### CJ active — need deep links (get from app.cj.com → Links → Get Links)
| Program | CJ Advertiser ID | Commission | EPC | Status |
|---------|-----------------|------------|-----|--------|
| GetResponse | 3142111 | $100/lead | $31.63 | NEED CJ LINK |
| Proton/ProtonVPN | 5227916 | 30-100% | $29.91 | NEED CJ LINK |
| Elementor | 6798066 | 45% | $7.55 | NEED CJ LINK |
| AWeber | 5111249 | $10-15/sale | - | NEED CJ LINK |
| Parallels | 2005415 | 10% | $31.65 | NEED CJ LINK |

### Pending network approval (pages live, $0 earned)
| Program | Route | Pages | Commission | Network |
|---------|-------|-------|-----------|---------|
| HubSpot | /go/hubspot-crm | 39 | $250-1000/sale | Impact.com PENDING |
| 1Password | /go/1password-trial | 37 | $30-60/sale | Impact.com PENDING |
| ClickUp | /go/clickup-trial | 27 | $36-150/sale | PartnerStack LOCKED |
| ActiveCampaign | /go/activecampaign-trial | 20 | $85/sale | PartnerStack LOCKED |
| Monday.com | /go/monday | 20 | $150/sale | PartnerStack LOCKED |
| FreshBooks | /go/freshbooks-trial | 19 | $200/sale | Awin PENDING (applied 2026-06-01) |
| Xero | /go/xero-trial | 18 | varies | Direct (applied 2026-06-01) |
| Dashlane | /go/dashlane-trial | 14 | $25-50/sale | PartnerStack LOCKED |

## Commit Message Prefixes
`ceo-daily:` | `revenue-hunter:` | `sunday-maximizer:` | `wave-N:` | `fix:` | `feat:`

## Key Scripts
```bash
uv run pytest -q                              # tests (must show 57 passed)
uv run python scripts/update_sitemap_and_index.py   # rebuild sitemap + IndexNow
uv run python scripts/fix_body_and_jsonld.py        # fix body.sp-bg + bare JSON-LD
uv run python scripts/fix_jsonld_v2.py              # wrap remaining bare JSON-LD
```

## Memory
Read `data/memory.json` at session start for context on past actions.
Check `git log --oneline -10` to see what changed recently.

## Autonomous Routines (Claude Code)
- Daily CEO Review: 7am Brisbane (trig_01FCDNuqeXEivnZ1LJvTyugK)
- Revenue Hunter: 7:30am Brisbane (trig_01U3FBGZ1hcxNegCd5wiFZhU)
- Sunday Profit Maximizer: 9am Brisbane Sundays (trig_01Ag9J9J4uq5pgLqKqfYTyPL)
All routines require GitHub connected at claude.ai to access the repo.
