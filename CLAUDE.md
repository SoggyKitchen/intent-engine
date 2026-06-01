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

## Design Rules (Critical — violations break the site)
1. `<body style="background:#050407;color:rgba(255,248,245,.88)">` — NO `class="sp-bg"` on body (causes scroll/click freeze)
2. JSON-LD must be in `<script type="application/ld+json">` tags — bare JSON renders as visible text
3. Nav must use the real SVG logo (red/white S mark), not `class="sp-nav"` placeholder
4. Always run `uv run pytest -q` before pushing — must show 57 passed
5. CSS: `/assets/saaspare-v2.css` + `/assets/motion.css` + `/assets/motion.js`
6. Author on all pages: Kaylan von Papen — `/authors/kaylan-von-papen`

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
