# Commission Factory SEO Checklist Applied To SaaSpare

Generated: 2026-05-12

Source: https://help.commissionfactory.com/how-to-increase-website-traffic-and-improve-seo

## Current Repo Status

- SEO helper audit: 96.24/100, Elite SEO/revenue engine.
- Content QA: 1,208 pages scanned, 1,158 indexable pages, 1,019 money pages, 0 hard failures, 0 soft issues.
- Sitemap: 1,200 URLs with `lastmod`.
- Affiliate redirects validated: 165 live redirects, 0 dead links.

## Checklist Mapping

| Commission Factory recommendation | SaaSpare implementation | Status |
| --- | --- | --- |
| Focus on a specific niche and keywords | SaaSpare is focused on SaaS pricing, comparisons, reviews, free trials, coupons, and alternatives. | Complete |
| Differentiate from other affiliate sites | Hidden Fee Detector, pricing-change tracker, free-trial database, SaaS Pricing Index, source verification boxes, no-paid-rankings positioning. | Complete |
| Write unique content and publish consistently | Programmatic buyer pages, data assets, blog/research pages, pricing-history rendering, nightly SEO automation. | Complete |
| Update existing content | `blast_off.py`, pricing tracker, dateModified refreshes, content QA, SEO helper reports. | Complete |
| Fill thin-content gaps | `detect-thin-pages`, `content_qa.py`, trust boxes, related links, source/correction CTAs. | Complete with ongoing review queue |
| Title tags and meta descriptions | Central SEO helper, OTTO importer, GSC quick-win reports, CTR rewrite scripts. | Complete |
| Affiliate links are nofollow/sponsored | Buyer templates use `rel="sponsored noopener"` or `rel="sponsored nofollow noopener"` for `/go/` CTAs; content QA checks this. | Complete |
| Flat/organized URL structure | Public routes use shallow `/pages/`, `/blog/`, `/research/`, `/go/` structure with crawlable links. | Complete |
| XML sitemap | `site/sitemap.xml` includes canonical indexable URLs with lastmod. | Complete |
| Canonical tags | SEO integrity tests require canonical links on indexable pages. | Complete |
| Improve page speed | Cloudflare cache rules, static assets, lazy loading, no empty ad slots, UX/performance reports. | Active |

## Current Watch Items

- The remaining bottleneck is not basic technical SEO; it is authority, verified source depth, and moving GSC pages from average positions 11-30 into top 10.
- Keep affiliate links out of paid-search trademark bidding unless each program explicitly allows it.
- Continue weekly GSC-driven title/meta tests for high-impression, low-CTR pages.
- Keep verifying exact pricing/trial claims against vendor pages before marking pages as vendor-verified.

## Next 7 Actions

1. Add GSC credentials to CI so the SEO helper can prioritize real queries weekly.
2. Verify the top 25 pricing pages against vendor source pages.
3. Build backlinks to SaaS Pricing Index, Hidden Fee Detector, and pricing-change tracker.
4. Apply to high-fit SaaS affiliate programs before broad retail programs.
5. Keep Cloudflare cache rules active and bypass `/go/*`.
6. Re-run `uv run python scripts/content_qa.py` after each major page batch.
7. Re-run `npm run seo:agent -- --mode=audit` weekly and inspect `seo/reports/top-100-fixes.md`.
