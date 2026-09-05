# SaaSpare — Profit & Visibility Master Plan

Generated: 2026-06-24 · Author: Claude (CEO/operator mode) · For: Kaylan von Papen

---

## The honest diagnosis: why you're at $0 after 6 weeks

You have **not** made $0 because the site is bad. Three measurable facts explain it:

| Root cause | Evidence | Who fixes |
|---|---|---|
| **1. Almost zero external authority** | Authority Score ≈ 0 (no backlinks). 22,919 impressions but 0.3% CTR = Google ranks you mostly position 20+, where nobody clicks. AIs don't cite you because nothing else references you. | Kaylan (60 min) + Claude (drafts) |
| **2. The revenue brain is blind** | GSC token `invalid_grant: revoked`. `revenue-opportunities.md` and `gsc-opportunities.md` are **blank**. SEO agent CI fails nightly. You can't see which pages to push. | Kaylan (15 min, infra) |
| **3. Best-traffic pages can't earn** | Highest-volume clusters (HubSpot $400/conv, project-mgmt, CRM) are PENDING/LOCKED/PLACEHOLDER. Links point to bare brand URLs = $0. PartnerStack just rejected you (fraud-flag from old duplicate accounts). | Kaylan (approvals) + Claude (re-wire) |

What is NOT wrong: site health (94.57/100), technical SEO (19.9/20), AI-crawler access (robots.txt allows GPTBot/OAI-SearchBot/ClaudeBot/PerplexityBot), `llms.txt` + `llms-full.txt` (both exist), on-page schema. **The foundation is genuinely strong.** You're 2-3 unblocks away from this working.

---

## The core insight that fixes BOTH goals at once

Your two wishes — "Google show my stuff" and "AIs recommend me" — have the **same** bottleneck: **other sites must reference SaaSpare.** Google's #2 ranking factor (~25%) is backlinks/authority. AI engines (ChatGPT search, Perplexity, Google AI Overviews) cite brands that appear across the web. Right now SaaSpare is an island. Build the authority and both doors open together.

This is why the **directory-submission pack is the single highest-leverage move you can make** — it serves Google rankings AND AI citations simultaneously, and it's already written and waiting.

---

## TIER 0 — Unblock measurement (this week · ~30 min · mostly Kaylan)

Without these you're flying blind and can't see a single dollar even if it lands.

1. **Re-auth Google Search Console.** Token is revoked. A new service account `jarvis@saaspare.iam.gserviceaccount.com` was added as owner on Jun 21 (per GSC email), but the repo expects `saaspare@saaspare.iam.gserviceaccount.com`. Pick ONE:
   - In GSC → `sc-domain:saaspare.org` → Settings → Users & permissions → add the service-account email with **Full**, then put its JSON key in GitHub secret `GSC_SERVICE_ACCOUNT_JSON`; **or**
   - Use OAuth: put your authorized-user JSON in `GSC_AUTHORIZED_USER_JSON`. Keep `GSC_SITE_URL = sc-domain:saaspare.org`.
   - Verify: re-run the SEO Agent workflow; `gsc-opportunities.md` should populate.
2. **Wire affiliate earnings visibility.** Add `CJ_API_KEY` (CJ publisher 101733230) and `IMPACT_API_TOKEN` (Impact publisher 7269601) to GitHub secrets. Then `fetch_affiliate.py` shows REAL earnings instead of "$0 / no data." You may already be earning and not seeing it.

## TIER 1 — Build authority = the real visibility unlock (start TODAY · ~60 min Kaylan)

This is the lever that moves rankings AND AI citations. Payoff lands 60-90 days out, so every day of delay costs.

3. **Submit to all 25 directories** in `seo/reports/directory-submission-pack.md`. Copy-paste descriptions are pre-written. Expected: +15-18 DA50+ backlinks → Authority Score 0 → 12-18 in 6-8 weeks → rankings climb → impressions finally convert to clicks. Highest-ROI hour you can spend. (Claude can pre-fill every form field set so each one is a 2-min paste.)
4. **Get cited where AI engines read.** Perplexity/ChatGPT lean on Reddit, Quora, and listicles. Plan: genuine, non-spammy answers in r/SaaS, r/Entrepreneur software threads linking the relevant comparison page; answer "best X alternative" Quora questions. (Claude drafts; Kaylan posts from a real account.)
5. **HARO/Qwoted digital PR.** Pitch SaaSpare's real pricing data to journalists writing SaaS roundups → editorial backlinks from Forbes Advisor / PCMag tier. (Claude drafts pitches; Kaylan sends.)

## TIER 2 — Wire the money (ongoing · Claude executes, Kaylan approves programs)

6. **Maximize the programs that earn TODAY.** Already-approved: NordVPN, Surfshark, Sucuri, NordPass, Contabo, HostPapa, Semrush, Shopify, ElevenLabs, Incogni, ActiveCampaign, Proton, Elementor, AWeber, Parallels, Fiverr. Ensure these tracked links appear on every relevant comparison/alternatives/coupon page with strong above-fold CTAs. These can convert existing traffic into first dollars now — no new approvals needed.
7. **Route the high-traffic, locked clusters to networks that approve you.** PartnerStack rejected you (Monday/ClickUp/ActiveCampaign/Dashlane). Pivot those tools to Impact, CJ, or direct programs where possible instead of waiting on PartnerStack. Re-wire `_redirects` to tracked links the moment any approval lands.
8. **Win HubSpot ($400/conv × 40 pages) and FreshBooks ($200 × 23 pages).** These are your biggest single prizes. HubSpot via Impact (pending), FreshBooks via Awin (pending). Chase the approvals.

## TIER 3 — AEO/GEO polish (already 80% done — protect it)

Your on-page AEO is strong. Keep: self-contained answer paragraph as the FIRST sentence of every buyer page, comparison tables with `<caption>`, "Last verified [date]" + `<time datetime>`, FAQPage schema, visible methodology + correction CTA (Perplexity trust signals). The remaining AEO gap is **off-page authority = Tier 1.** Don't add more pages; add more references TO your pages.

---

## What Claude does next (autonomous, no approval needed)

- Pre-fill every directory submission into copy-paste-ready blocks so Tier 1 #3 is pure paste-and-go for Kaylan.
- Draft the Reddit/Quora answers and HARO pitches (Kaylan posts from real accounts).
- Audit earning-NOW program coverage across pages; add missing tracked CTAs (Tier 2 #6).
- Once GSC is back: run the full audit + revenue_intelligence, dollar-rank pages, execute title/meta/CTR rewrites on the climb-zone (pos 8-20) pages.

## What ONLY Kaylan can do (escalated — these gate everything)

1. Re-auth GSC (Tier 0 #1) — **the master unlock**
2. Add CJ + Impact API keys (Tier 0 #2)
3. Submit the 25 directories (Tier 1 #3) — **the visibility unlock**
4. Send the PartnerStack appeal (drafted) + chase HubSpot/FreshBooks approvals

---

## The realistic timeline (if Tier 0 + Tier 1 happen this week)

- **Week 1-2:** GSC back online, earnings visible, 25 directories submitted.
- **Week 3-4:** ~15 backlinks approved and live. Climb-zone title/meta rewrites shipping weekly off real GSC data.
- **Week 6-8:** Authority Score 0 → 12-18. Rankings on existing impression pages start climbing toward page 1.
- **Day 60-90:** First real organic traffic lift converts to clicks → first affiliate dollars from earning-NOW programs. AI engines begin surfacing SaaSpare as they re-crawl the new citations.

You are not done for. You are unplugged. Plug in the 4 things above and the machine you already built starts running.
