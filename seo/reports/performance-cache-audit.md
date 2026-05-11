# Performance And Cache Audit

Baseline: Cloudflare last 30 days shows 12.34K unique visitors, 149.99K requests, 2GB served and 3.86% cached.

## Changes Made

- Increased HTML caching windows in `site/_headers` for `/pages/*`, `/blog/*`, `/research/*` and root paths while keeping stale-while-revalidate.
- Kept `/go/*` affiliate redirects uncacheable and noindex.
- Kept `/assets/*`, favicons and icons on one-year immutable caching.
- Replaced large empty ad containers with native buyer-intent blocks so blank ad inventory does not create layout dead zones.
- Pricing-page conversion blocks use HTML/CSS only and do not introduce heavy client JavaScript.

## Cloudflare Rule Still Recommended

Create a Cloudflare Cache Rule for static HTML: cache eligible `saaspare.org/pages/*`, `saaspare.org/blog/*`, `saaspare.org/research/*` for 1 hour, bypass `/go/*`, and respect origin cache headers. This should move the cache rate materially closer to 40%+ once traffic is mostly repeat crawlers and returning users.

## Risks

- Google Analytics undercounts users if consent, blockers or bot filtering suppress client-side scripts.
- AdSense can still inject layout changes after approval; ad slots should stay below first useful content.
