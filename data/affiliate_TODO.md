# Affiliate Network Signup Checklist

You were rejected from direct affiliate programs (Ahrefs, HubSpot, etc.) because of low traffic.
The fix: join **networks** instead. One signup = access to hundreds of programs, no individual approval needed.

---

## Step 1 — Join These 3 Networks

### 1. Impact.com Marketplace
- **Signup URL:** https://impact.com/affiliates/
- **Why:** Single account gives access to HubSpot, Brevo, Shopify, Semrush, DocuSign, NordLayer,
  Monday.com, ExpressVPN, Vultr, BigCommerce, Malwarebytes, Keeper, NordPass and 2000+ more.
- **Approval:** Approves new/low-traffic publishers. Use saaspare.org as your website.
- **Tracked link format after joining:**
  `https://impact.sjv.io/[PROGRAM_ID]?irgwc=1`
  (Each brand in the marketplace gives you a unique program ID when you join their sub-program.)

### 2. PartnerStack Marketplace
- **Signup URL:** https://app.partnerstack.com/
- **Why:** Most SaaS tools use PartnerStack. Access to JetBrains, Retool, Datadog, Sentry,
  Amplitude, Mixpanel, Databox, Hotjar, FullStory, ActiveCampaign, Klaviyo, ConvertKit, Lemlist,
  Render, Supabase, 1Password, Snyk, CrowdStrike, BambooHR, Rippling, Workable, Deel,
  Chargebee, PandaDoc, Ironclad, Contractbook, Xero, Jasper AI, Copy.ai, Writesonic, Pinecone,
  Asana, ClickUp, Notion, Wrike, Smartsheet, Pipedrive, Close, Freshsales, Copper, Keap,
  LastPass, Dashlane, Whereby, Riverside.fm, Loom, Zoom, Perimeter 81, Twingate,
  Surfer SEO, SE Ranking, Frase.io and hundreds more.
- **Approval:** Easy — no traffic minimum for most programs.
- **Tracked link format after joining:**
  `https://partnerstack.com/[PROGRAM_SLUG]?via=[YOUR_REF_CODE]`
  (Your ref code is assigned per-program when you join each sub-program inside the marketplace.)

### 3. ShareASale
- **Signup URL:** https://www.shareasale.com/
- **Why:** Established network with easy approval. Access to FreshBooks, Moz Pro, SpyFu, Rankmath Pro.
- **Approval:** Fill in the form — approvals are fast, low-traffic sites accepted.
- **Tracked link format after joining:**
  `https://shareasale.com/r.cfm?b=[BANNER_ID]&u=[USER_ID]&m=[MERCHANT_ID]`
  (All IDs provided in your ShareASale dashboard per merchant.)

---

## Step 2 — After Joining Each Network

1. Search for each tool by name inside the marketplace.
2. Click "Apply" or "Join Program" for each tool you have a page about.
3. Once approved (usually instant or within 24h), grab your tracked deep link.
4. Update `publisher/affiliate_registry.py` — replace the `affiliate_url` for each tool with
   your tracked network link. The `network` field already tells you which network each tool uses.

---

## Step 3 — Tools by Network

### Impact.com tools (join at https://impact.com/affiliates/)
- HubSpot — marketing automation
- Brevo — marketing automation
- DigitalOcean — cloud infra
- Vultr — cloud infra
- NordLayer — cybersecurity / vpn_business
- Shopify — ecommerce
- BigCommerce — ecommerce
- DocuSign — legal/compliance
- Semrush — SEO tools
- Monday.com — project management
- Malwarebytes — cybersecurity
- Keeper — password managers
- NordPass — password managers
- ExpressVPN Business — vpn_business

### PartnerStack tools (join at https://app.partnerstack.com/)
- JetBrains, Retool, Datadog, Sentry — devtools
- Amplitude, Mixpanel, Databox, Hotjar, FullStory — analytics
- ActiveCampaign, Klaviyo, ConvertKit, Lemlist — marketing automation
- Render, Supabase — cloud infra
- 1Password Business, Snyk, CrowdStrike — cybersecurity
- BambooHR, Rippling, Workable, Deel — HR
- Chargebee — ecommerce
- PandaDoc, Ironclad, Contractbook — legal
- Xero — finance
- Jasper AI, Copy.ai, Writesonic, Pinecone — AI/ML
- Asana, ClickUp, Notion, Wrike, Smartsheet — project management
- Pipedrive, Close, Freshsales, Copper, Keap — CRM
- LastPass, Dashlane — password managers
- Whereby, Riverside.fm, Loom, Zoom — video conferencing
- Perimeter 81, Twingate — VPN
- Surfer SEO, SE Ranking, Frase.io — SEO tools

### ShareASale tools (join at https://www.shareasale.com/)
- FreshBooks — finance ops
- Moz Pro — SEO tools
- SpyFu — SEO tools
- Rankmath Pro — SEO tools

### Direct programs (apply individually when you have traffic)
- GitHub Copilot, Linear — devtools
- Mailchimp — marketing automation
- Hetzner — cloud infra
- Zoho CRM — CRM
- Gusto — HR
- Gumroad — ecommerce
- Brex, Ramp, Expensify — finance
- Ahrefs, Mangools, Clearscope, Screaming Frog — SEO tools

---

## Notes

- **Amazon Associates** (https://affiliate-program.amazon.com/) — also worth joining.
  Approves anyone. Use for Microsoft 365, Adobe Creative Cloud, antivirus software sold via Amazon.
  Link format: `https://www.amazon.com/dp/[ASIN]?tag=[YOUR_TAG]`
- Replace `AMAZON_ASSOCIATE_TAG` in your `.env` / secrets with your real tag after signup.
