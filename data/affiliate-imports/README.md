# Affiliate link CSV drops

Drop partner-network exports in this folder, commit them, and push.

The `Affiliate Import` GitHub Action normalizes common CJ, Awin, Impact, PartnerStack, ShareASale, and generic CSV columns into the canonical importer schema. The safest columns are:

- `ADVERTISER`
- `CLICK URL`
- `RELATIONSHIP STATUS` with `Active`
- `LINK TYPE` with `Text Link`, `Free Trial`, `Coupon`, or `Pricing`
- `SEVEN DAY EPC`
- `THREE MONTH EPC`

If a network uses different names, keep the real advertiser name and the real destination URL in obvious columns. The normalizer ignores ID/status/name-only columns when guessing URLs so it does not accidentally import tracking IDs as links.
