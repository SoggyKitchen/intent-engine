# Cloudflare Email Service Setup

This repo now includes:

- `functions/api/lead.ts`: Cloudflare Pages Function for site form submissions.
- `workers/email-service/`: optional standalone Worker if you want a separate email subdomain later.
- `site/assets/saaspare-ui.js`: progressive form enhancement. It tries `/api/lead` first and falls back to the existing FormSubmit action if Cloudflare is not configured yet.

## Cloudflare Pages setup

In Cloudflare Pages for the SaaSpare project, add these environment variables/bindings:

- `SEND_EMAIL`: Email Service send binding.
- `LEAD_NOTIFY_TO`: the inbox that receives leads, for example your Gmail or a hosted `hello@saaspare.org` mailbox.
- `LEAD_FROM`: verified sender address, recommended `hello@saaspare.org`.
- `ALLOWED_ORIGINS`: optional, use `https://saaspare.org,https://www.saaspare.org`.

Deploy after merging the PR. Test with:

```powershell
Invoke-WebRequest -Method Post https://saaspare.org/api/lead -Body @{ email="test@example.com"; _subject="SaaSpare test"; message="hello" }
```

## If using the standalone Worker

Use `workers/email-service/wrangler.jsonc`, then add Worker variables/secrets in Cloudflare:

- `LEAD_NOTIFY_TO`
- `LEAD_FROM`
- `ALLOWED_ORIGINS`

The static site can be pointed at the Worker by setting:

```html
<script>window.SAASPARE_LEAD_ENDPOINT = "https://email.saaspare.org/lead";</script>
```

The Pages Function path is simpler, so use that first.
