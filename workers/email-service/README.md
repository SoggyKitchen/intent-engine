# SaaSpare Cloudflare Email Service

This is the standalone Worker version of the same lead-capture handler used by the Pages Function at `functions/api/lead.ts`.

Use the Pages Function first if `saaspare.org` is deployed on Cloudflare Pages. Use this standalone Worker only if you prefer a separate route such as `https://email.saaspare.org/lead`.

## Required Cloudflare bindings

- `SEND_EMAIL`: Cloudflare Email Service / Email Routing send binding.
- `LEAD_NOTIFY_TO`: destination inbox for form submissions.
- `LEAD_FROM`: verified sender such as `hello@saaspare.org`.
- `ALLOWED_ORIGINS`: optional comma-separated origins. Defaults to `https://saaspare.org,https://www.saaspare.org`.

Never commit inbox credentials or API keys.
