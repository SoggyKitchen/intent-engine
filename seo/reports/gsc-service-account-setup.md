# GSC Service Account Setup

Status: service account key is present locally, but Search Console currently returns `403 insufficient permission`.

## Exact Email To Add

`saaspare@saaspare.iam.gserviceaccount.com`

## Required Manual Step

In Google Search Console, open the `sc-domain:saaspare.org` property, then go to:

`Settings` -> `Users and permissions` -> `Add user`

Add `saaspare@saaspare.iam.gserviceaccount.com` with `Full` permission.

If Search Console says `email not found`, use the OAuth setup instead. Some
Search Console accounts/properties do not accept service accounts from the
user picker even though the API key file is valid.

## OAuth Fallback

Use OAuth with the same Google account that owns Search Console.

Preferred GitHub secret:

`GSC_AUTHORIZED_USER_JSON`

This should be the full authorized-user JSON for your Google account. The SEO
agent now supports this format directly, including when the JSON is supplied
through `GOOGLE_APPLICATION_CREDENTIALS`.

## GitHub Secret To Add After That

Add the whole JSON service-account file as a GitHub Actions secret:

`GSC_SERVICE_ACCOUNT_JSON`

If using OAuth instead, add the authorized-user JSON as:

`GSC_AUTHORIZED_USER_JSON`

Keep `GSC_SITE_URL` set to:

`sc-domain:saaspare.org`

## Why This Matters

Once permission is active, the weekly SEO agent can pull real page/query data and automatically prioritize:

- high-impression pages with weak CTR
- pages ranking positions 8-30
- buyer-intent searches around pricing, alternatives, free trials, coupons and comparisons
- pages losing clicks
- pages getting impressions but no commercial events

