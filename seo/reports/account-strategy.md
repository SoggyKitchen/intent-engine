# SaaSpare Account Strategy

## Decision
SaaSpare should not require accounts for comparisons, pricing pages, Deal Radar, ROI Calculator, Shortlist Builder, or affiliate outbound clicks.

The best current model is account-lite:

- Keep every SEO and buyer-intent page public and crawlable.
- Let visitors save shortlist preferences locally in the browser without sign-up.
- Offer email capture only after the user has received value.
- Add real accounts later only for features that justify friction: renewal reminders, team workspaces, saved vendor notes, price-watch alerts, or procurement exports.

## Why
Mandatory login would add friction before affiliate clicks and can reduce crawlable value if used as a gate. SaaSpare’s current revenue model depends on public search visibility and fast buyer action, so the account layer should increase retention without blocking discovery.

## Product Rules
- No login wall on indexable content.
- No login requirement before `/go/` affiliate redirects.
- No account prompt before the first useful comparison, verdict, pricing table, or shortlist result.
- Use local storage for lightweight saved state.
- Use email capture for weekly deal digest and shortlist reminders.
- Only add database-backed accounts when there is a real recurring user job to save.

## Future Pro Ideas
- Renewal calendar with price-change alerts.
- Team shortlist workspace.
- Procurement export to CSV/PDF.
- Vendor comparison notes.
- Stack spend tracker.
- Slack/email alerts for pricing changes.

## Implementation Status
- Shortlist Builder now supports browser-saved shortlists without login.
- Shortlist email form now includes the selected category and ranked tool snapshot.
- Privacy policy now discloses local browser storage for saved shortlists.
