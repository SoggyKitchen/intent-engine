# GSC Service Account Setup

Status: service account key is present locally, but Search Console currently returns `403 insufficient permission`.

## Exact Email To Add

`saaspare@saaspare.iam.gserviceaccount.com`

## Required Manual Step

In Google Search Console, open the `sc-domain:saaspare.org` property, then go to:

`Settings` -> `Users and permissions` -> `Add user`

Add `saaspare@saaspare.iam.gserviceaccount.com` with `Full` permission.

## GitHub Secret To Add After That

Add the whole JSON service-account file as a GitHub Actions secret:

`GSC_SERVICE_ACCOUNT_JSON`

Keep `GSC_SITE_URL` set to:

`sc-domain:saaspare.org`

## Why This Matters

Once permission is active, the weekly SEO agent can pull real page/query data and automatically prioritize:

- high-impression pages with weak CTR
- pages ranking positions 8-30
- buyer-intent searches around pricing, alternatives, free trials, coupons and comparisons
- pages losing clicks
- pages getting impressions but no commercial events

