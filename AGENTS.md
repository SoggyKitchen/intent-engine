# SaaSpare / intent-engine — agent notes

## Commands

| Intent | Command |
| --- | --- |
| Run the full test suite | `uv run pytest -q` |
| Run SEO integrity CI gates only | `uv run pytest tests/test_normalise.py tests/test_seo_integrity.py -v` |
| Repair any title / trust-box corruption | `uv run python scripts/fix_corrupted_titles.py` |
| Sync public KPI counters across marketing pages | `uv run python scripts/sync_public_kpis.py` |
| Normalise per-page methodology paragraphs | `uv run python scripts/normalise_methodology_copy.py` |
| Inject intent-weighted journey links on buyer pages | `uv run python scripts/inject_journey_links.py` (use `--check` to dry-run) |
| Flag risky factual claims + update verification state | `uv run python scripts/flag_risky_claims.py` |
| Run the affiliate-network trust pass (Impact / PartnerStack readiness) | `uv run python scripts/trust_pass.py` (use `--check` to dry-run) |
| Unify nav logo across all buyer pages | `uv run python scripts/nav_unify.py` (use `--check` to dry-run) |
| Fix Amazon Associates links (remove non-earning AWS tags, add MS365 pill) | `uv run python scripts/fix_amazon_links.py` (use `--check` to dry-run) |
| SEO consolidation: strip fake aggregateRating, fix duplicate canonicals, noindex previews | `uv run python scripts/seo_consolidate.py` (use `--check` to dry-run) |
| Comprehensive content QA gate (CI; reports to outputs/seo/content_qa.json) | `uv run python scripts/content_qa.py` |
| Run the existing weekly SEO agent (uses OpenAI/GSC) | `npm run seo:agent` |

## Source-of-truth files

- `data/public_kpis.json` — canonical page counts and display strings.
  Regenerate via `scripts/sync_public_kpis.py`.
- `publisher/normalise.py` — canonical title/brand normalisation +
  corruption detectors. Import from any publisher or test module; do
  NOT duplicate the regex rules elsewhere.
- `scripts/seo/seo_agent.py::inject_buyer_trust_block` — canonical
  Source Verification Box. Mirrored by
  `scripts/fix_corrupted_titles.py::new_trustbox_sentence` for legacy
  HTML repair.

## Reports

Nightly audit writes to `outputs/seo/`:

- `corruption-report.json` — any title/trust-box artefacts repaired.
- `methodology-normalisation.json` — per-page methodology rewrites.
- `journey-links.json` — intent-weighted next-step links injected.
- `manual_review_queue.json` — pages flagged with risky factual claims.

## CI gates (must pass before publish)

- `tests/test_normalise.py` — no corrupted titles; no stale trust-box
  "Last verified: &lt;title&gt; is checked during scheduled SEO..."
  sentence remaining on site.
- `tests/test_seo_integrity.py` — every indexable page has a canonical
  link, is in the sitemap, has valid JSON-LD, and money pages have an
  accepted schema type (Article, BreadcrumbList, Product, FAQPage,
  Service, AggregateRating, WebPage, Review, HowTo, ItemList,
  CollectionPage).

## Verification-state vocabulary

`data-verification-state` attribute values used in
`<section data-seo-trustbox>`:

- `needs_manual_review` (default after publish)
- `verified_from_vendor` (editor has confirmed pricing/trial terms against
  the vendor&#x27;s public page and added a source URL)
- `custom_quote_unverified` (vendor uses sales-only quotes; we do not
  claim pricing)
- `risky_claim_needs_vendor_source` (auto-set by flag_risky_claims.py
  when a page makes unverifiable refund/SLA/money-back claims)

## Monetisation pages that already exist

- `/pages/saas-spend-audit.html` — productised audit landing page
  (Stack Brief A$29 / Stack Audit A$99 / Stack Concierge A$299).
- `/pages/saas-stack-audit-checkout.html` — formsubmit intake form.
- `/pages/saas-pricing-index.html` — SaaS Pricing Index data asset.
- `/pages/saas-pricing-changes.html` — pricing-change tracker.
- `/pages/free-trial-database.html` — free-trial database.
- `/pages/weekly-saas-deal-digest.html` — newsletter landing.

Do not create new revenue landing pages without first checking these
because the paths are already indexed.

## DO / DO NOT

- DO run `scripts/fix_corrupted_titles.py` and
  `scripts/sync_public_kpis.py` after any batch content update.
- DO assert `publisher.normalise.assert_no_corruption(title)` when
  generating new page titles programmatically.
- DO NOT re-introduce the "Last verified: {audit.title}" pattern in
  `inject_buyer_trust_block` — it caused ~900 pages of leaked titles.
- DO NOT silently rewrite pricing / refund / SLA claims. Mark the page
  via `scripts/flag_risky_claims.py` and let the editor verify from
  the vendor&#x27;s public page.
- DO NOT touch `_redirects` affiliate rules without re-running
  `scripts/validate_affiliate_urls.py` first.
