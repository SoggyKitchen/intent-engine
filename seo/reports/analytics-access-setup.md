# SaaSpare Analytics Access Setup

The SEO agent can now use Google Search Console data directly when a service account is added.

## What to create

1. Open Google Cloud Console and create a project named `saaspare-seo-agent`.
2. Enable the **Google Search Console API**.
3. Create a **Service Account**.
4. Create a JSON key for that service account.
5. Open Google Search Console for `saaspare.org`.
6. Go to **Settings > Users and permissions > Add user**.
7. Add the service account email as **Full** user. Owner is not required for query data.

## GitHub secrets to add

Set one of these:

```powershell
gh secret set GSC_SERVICE_ACCOUNT_JSON --repo SoggyKitchen/intent-engine --body "PASTE_THE_FULL_JSON_KEY_HERE"
```

or base64 encode the JSON first and set the base64 string:

```powershell
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes((Get-Content C:\path\to\key.json -Raw))) | gh secret set GSC_SERVICE_ACCOUNT_JSON --repo SoggyKitchen/intent-engine --body-file -
```

Also confirm:

```powershell
gh secret set GSC_SITE_URL --repo SoggyKitchen/intent-engine --body "https://saaspare.org"
```

## What the bot does with it

- Pulls the last 28 days of Search Console query/page data.
- Finds high-impression low-CTR pages.
- Finds buyer-intent queries around pricing, trial, coupon, alternative, vs, review, cost and discount.
- Finds pages ranking positions 8-30 that are close enough to push upward with internal links and better snippets.
- Writes the opportunity list to `seo/reports/gsc-opportunities.md` and `seo/reports/gsc-opportunities.json`.

The bot does not need Google Analytics credentials yet. GSC is the better first signal because it shows what Google is already testing in search.
