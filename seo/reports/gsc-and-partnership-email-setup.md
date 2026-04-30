# GSC and Partnership Email Setup

## Recommended domain emails

Create these aliases first:

- `partnerships@saaspare.org` for affiliate networks, partner managers, media-kit CTA, PartnerStack, Impact, Awin, CJ, ShareASale, and direct programs.
- `hello@saaspare.org` for general contact forms, correction reports, and comparison suggestions.
- `privacy@saaspare.org` for privacy requests already listed in the privacy page.

Fast free setup: Cloudflare Email Routing can forward these aliases to your real Gmail inbox. That gives networks a domain email without paying for Google Workspace.

Paid inbox setup: Google Workspace gives you an actual mailbox and is stronger for deliverability, but it is not required just to reapply to networks.

## Cloudflare Email Routing steps

1. Open Cloudflare dashboard.
2. Select `saaspare.org`.
3. Go to `Email` then `Email Routing`.
4. Enable Email Routing if it is not enabled.
5. Add destination address: your real Gmail inbox.
6. Verify the destination from the email Cloudflare sends you.
7. Add custom addresses:
   - `partnerships@saaspare.org` forwards to your Gmail.
   - `hello@saaspare.org` forwards to your Gmail.
   - `privacy@saaspare.org` forwards to your Gmail.
8. Let Cloudflare add the required MX/TXT DNS records if prompted.
9. Send a test email to each address.

## GSC automation status

Search Console rejected the service account email. The repo now supports an OAuth fallback, which uses your real Google account instead of a service account.

Required GitHub secrets for OAuth mode:

- `GSC_SITE_URL` = `sc-domain:saaspare.org`
- `GSC_OAUTH_CLIENT_ID`
- `GSC_OAUTH_CLIENT_SECRET`
- `GSC_OAUTH_REFRESH_TOKEN`

Once those are present, the weekly SaaSpare SEO Agent can pull clicks, impressions, CTR, average position, pages, and queries from Search Console.
