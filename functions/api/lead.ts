/**
 * Cloudflare Pages Function — /api/lead
 *
 * Accepts form submissions from every SaaSpare page and forwards them via
 * Resend (https://resend.com — 3,000 emails/month free, no credit card).
 *
 * Required env vars (Cloudflare Pages → Settings → Environment variables):
 *   RESEND_API_KEY   — re_xxxxxxxx from resend.com/api-keys
 *   LEAD_NOTIFY_TO   — inbox that receives every submission
 *
 * Optional:
 *   LEAD_FROM        — sender address (default: hello@saaspare.org)
 *   ALLOWED_ORIGINS  — comma-separated origins (default: saaspare.org)
 */

type Env = {
  RESEND_API_KEY?: string;
  LEAD_NOTIFY_TO?: string;
  LEAD_FROM?: string;
  ALLOWED_ORIGINS?: string;
  SEND_EMAIL?: { send(msg: Record<string, string>): Promise<void> };
};

const MAX_FIELD_LENGTH = 4000;
const DEFAULT_ALLOWED_ORIGINS = ["https://saaspare.org", "https://www.saaspare.org"];
const RESEND_API = "https://api.resend.com/emails";

// ─── Entry points ─────────────────────────────────────────────────────────────

export const onRequestOptions: PagesFunction<Env> = async ({ request, env }) => {
  return new Response(null, { status: 204, headers: corsHeaders(request, env) });
};

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  const headers = corsHeaders(request, env);

  if (!env.RESEND_API_KEY && !env.SEND_EMAIL) {
    return json({ ok: false, error: "email_not_configured" }, 503, headers);
  }
  if (!env.LEAD_NOTIFY_TO) {
    return json({ ok: false, error: "email_not_configured" }, 503, headers);
  }

  const origin = request.headers.get("Origin");
  if (origin && !allowedOrigins(env).includes(origin)) {
    return json({ ok: false, error: "origin_not_allowed" }, 403, headers);
  }

  const data = await parseRequest(request);
  if ((data._gotcha || data.website || "").trim()) {
    return json({ ok: true, ignored: true }, 200, headers);
  }

  const email = clean(data.email || data.from || "");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ ok: false, error: "valid_email_required" }, 400, headers);
  }

  const surface = clean(data.signup_surface || data.form_type || "");
  const page = clean(data.page_slug || data.page_title || data.landing_url || request.headers.get("Referer") || "unknown");
  const subject = buildSubject(data, email, surface);
  const html = buildHtmlEmail(data, email, page, surface);
  const text = buildTextBody(data, email, page);

  try {
    if (env.RESEND_API_KEY) {
      // 1. Owner notification
      await sendViaResend(env.RESEND_API_KEY, {
        from: env.LEAD_FROM || "SaaSpare <hello@saaspare.org>",
        to: env.LEAD_NOTIFY_TO,
        reply_to: email,
        subject,
        html,
        text,
      });
      // 2. User confirmation (fire-and-forget)
      const confSubject = buildUserConfirmSubject(surface);
      const confHtml    = buildUserConfirmHtml(data, email, surface);
      const confText    = buildUserConfirmText(surface);
      sendViaResend(env.RESEND_API_KEY, {
        from: env.LEAD_FROM || "SaaSpare <hello@saaspare.org>",
        to: email,
        reply_to: env.LEAD_NOTIFY_TO || "hello@saaspare.org",
        subject: confSubject,
        html: confHtml,
        text: confText,
      }).catch((e: unknown) => console.error("user confirm error:", e));
    } else if (env.SEND_EMAIL) {
      await env.SEND_EMAIL.send({ from: env.LEAD_FROM || "hello@saaspare.org", to: env.LEAD_NOTIFY_TO, subject, text, html });
    }
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error("lead.ts send error:", msg);
    return json({ ok: true, _warn: "delivery_issue" }, 200, headers);
  }

    // Non-JS fallback: redirect to thanks page instead of showing raw JSON
  const isFormPost = !(request.headers.get("Content-Type") || "").includes("application/json");
  if (isFormPost) {
    return Response.redirect("https://saaspare.org/pages/thanks.html", 303);
  }

  return json({ ok: true }, 200, headers);
};

// ─── Resend HTTP client ───────────────────────────────────────────────────────

async function sendViaResend(
  apiKey: string,
  payload: { from: string; to: string; reply_to: string; subject: string; html: string; text: string }
): Promise<void> {
  const resp = await fetch(RESEND_API, {
    method: "POST",
    headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!resp.ok) {
    const body = await resp.text().catch(() => "(unreadable)");
    throw new Error(`Resend ${resp.status}: ${body}`);
  }
}

// ─── Subject line ─────────────────────────────────────────────────────────────

function buildSubject(data: Record<string, string>, email: string, surface: string): string {
  const raw = clean(data._subject || data.subject || "");
  if (raw) return raw.slice(0, 160);
  if (surface === "exit_intent")                                    return `[SaaSpare] Exit-intent signup — ${email}`;
  if (surface.includes("newsletter") || surface.includes("digest")) return `[SaaSpare] Newsletter signup — ${email}`;
  if (surface.includes("audit") || surface.includes("intake"))      return `[SaaSpare] Stack Audit intake — ${data.tier || "unknown tier"}`;
  if (surface === "contact" || data.topic)                          return `[SaaSpare] Contact — ${data.topic || "General question"}`;
  return `[SaaSpare] New lead — ${email}`;
}

// ─── Router ───────────────────────────────────────────────────────────────────

function buildHtmlEmail(data: Record<string, string>, email: string, page: string, surface: string): string {
  const isAudit   = surface.includes("audit") || surface.includes("intake") || !!data.tier;
  const isContact = surface === "contact" || !!data.topic;
  if (isAudit)   return auditIntakeEmail(data, email);
  if (isContact) return contactFormEmail(data, email);
  return newsletterSignupEmail(data, email, page, surface);
}

// ─── Design tokens ────────────────────────────────────────────────────────────
// Dark theme: #07070d bg, #e94560 red, #c73652 dark red
// "Glassy" in email = dark card bg + lighter border + subtle inner highlight row

const BG        = "#07070d";   // page background
const CARD      = "#12121f";   // card background
const CARD_EDGE = "#1e1e30";   // card border
const ROW_ALT   = "#0e0e1c";   // alternating data row
const RED       = "#e94560";   // SaaSpare red
const RED_DARK  = "#c73652";   // gradient end
const TEXT      = "#e8e6f0";   // primary text
const MUTED     = "#7b7a96";   // secondary text
const DIM       = "#3a3a55";   // dividers / subtle borders
const GREEN     = "#34d399";   // success / verified
const AMBER     = "#fbbf24";   // warning / next-step

// ─── Shared shell ─────────────────────────────────────────────────────────────

function emailShell(title: string, label: string, badgeHtml: string, body: string, replyEmail = ""): string {
  // Glint: a 1px highlight line across the top of the card simulates glass
  const glint = `<tr><td height="1" style="background:linear-gradient(90deg,transparent 0%,rgba(255,255,255,.12) 40%,rgba(255,255,255,.18) 50%,rgba(255,255,255,.12) 60%,transparent 100%);font-size:0;line-height:0">&nbsp;</td></tr>`;

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark">
<title>${h(title)}</title>
</head>
<body style="margin:0;padding:0;background:${BG};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased">

<!-- outer wrapper -->
<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:${BG};min-height:100vh">
<tr><td align="center" style="padding:40px 16px 48px">
<table width="600" cellpadding="0" cellspacing="0" role="presentation" style="max-width:600px;width:100%">

  <!-- ── HEADER ── -->
  <tr><td style="background:linear-gradient(135deg,${RED} 0%,${RED_DARK} 100%);border-radius:16px 16px 0 0;padding:0;overflow:hidden">
    <!-- glint highlight -->
    <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
      <tr><td height="1" style="background:linear-gradient(90deg,transparent,rgba(255,255,255,.22) 35%,rgba(255,255,255,.32) 50%,rgba(255,255,255,.22) 65%,transparent);font-size:0;line-height:0">&nbsp;</td></tr>
      <tr><td style="padding:28px 32px 26px;text-align:center">
        <!-- logo mark + wordmark -->
        <table cellpadding="0" cellspacing="0" role="presentation" style="margin:0 auto 12px">
          <tr>
            <td style="vertical-align:middle;padding-right:8px">
              <!-- S-mark approximated with two stacked bars -->
              <table cellpadding="0" cellspacing="0" role="presentation">
                <tr><td width="18" height="8" style="background:rgba(255,255,255,.9);border-radius:4px 4px 0 4px;font-size:0">&nbsp;</td></tr>
                <tr><td height="3" style="font-size:0">&nbsp;</td></tr>
                <tr><td width="18" height="8" style="background:rgba(255,255,255,.55);border-radius:0 4px 4px 4px;font-size:0">&nbsp;</td></tr>
              </table>
            </td>
            <td style="vertical-align:middle">
              <span style="font-size:20px;font-weight:800;color:#ffffff;letter-spacing:-.5px;line-height:1">Saa<span style="color:rgba(255,255,255,.55)">Spare</span></span>
            </td>
          </tr>
        </table>
        <!-- event label -->
        <div style="display:inline-block;background:rgba(0,0,0,.25);border:1px solid rgba(255,255,255,.15);border-radius:100px;padding:4px 14px;font-size:11px;font-weight:600;color:rgba(255,255,255,.8);letter-spacing:.06em;text-transform:uppercase">${h(label)}</div>
      </td></tr>
    </table>
  </td></tr>

  <!-- ── CARD ── -->
  <tr><td style="background:${CARD};border:1px solid ${CARD_EDGE};border-top:none;border-radius:0 0 16px 16px;overflow:hidden">
    <!-- card inner glint -->
    <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
      ${glint}
      <tr><td style="padding:28px 32px 0">
        <!-- type badge + heading -->
        ${badgeHtml}
      </td></tr>
      <!-- data rows -->
      <tr><td style="padding:0 32px 24px">
        ${body}
      </td></tr>
      <!-- footer -->
      <tr><td style="padding:20px 32px;border-top:1px solid ${DIM};text-align:center">
        <p style="margin:0;font-size:11px;color:${MUTED}">
          SaaSpare &nbsp;&middot;&nbsp; Unbiased B2B SaaS comparisons &nbsp;&middot;&nbsp; No paid rankings
        </p>
        <p style="margin:6px 0 0;font-size:11px">
          <a href="https://saaspare.org" style="color:${RED};text-decoration:none;font-weight:600">saaspare.org</a>
          ${replyEmail ? `&nbsp;&nbsp;<a href="mailto:${h(replyEmail)}" style="color:${MUTED};text-decoration:none">Reply to ${h(replyEmail)}</a>` : ""}
        </p>
      </td></tr>
    </table>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>`;
}

// ─── Shared components ────────────────────────────────────────────────────────

function sectionHeading(text: string): string {
  return `<p style="margin:24px 0 12px;font-size:17px;font-weight:800;color:${TEXT};letter-spacing:-.3px">${h(text)}</p>`;
}

function dataTable(rows: string): string {
  return `<table width="100%" cellpadding="0" cellspacing="0" role="presentation"
    style="border:1px solid ${DIM};border-radius:10px;overflow:hidden;border-collapse:separate;border-spacing:0;margin-top:4px">
    ${rows}
  </table>`;
}

function dataRow(label: string, value: string, isEven: boolean): string {
  if (!value || value === "(blank)") return "";
  const bg = isEven ? ROW_ALT : CARD;
  return `<tr style="background:${bg}">
    <td style="padding:10px 14px;font-size:12px;font-weight:700;color:${MUTED};white-space:nowrap;vertical-align:top;width:140px;letter-spacing:.02em;text-transform:uppercase;border-bottom:1px solid ${DIM}">${h(label)}</td>
    <td style="padding:10px 14px;font-size:13px;color:${TEXT};word-break:break-word;border-bottom:1px solid ${DIM}">${h(value)}</td>
  </tr>`;
}

function typeBadge(text: string, color: string): string {
  return `<span style="display:inline-block;background:${color}22;border:1px solid ${color}55;color:${color};font-size:10px;font-weight:800;padding:3px 11px;border-radius:100px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px">${h(text)}</span>`;
}

function messageBlock(text: string): string {
  return `<div style="margin-top:16px;background:#0a0a18;border:1px solid ${DIM};border-left:3px solid ${RED};border-radius:8px;padding:16px 18px;font-size:13px;color:${TEXT};line-height:1.7;white-space:pre-wrap">${h(text)}</div>`;
}

function nextStepBanner(html: string): string {
  return `<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="margin-top:20px">
    <tr><td style="background:#1a0d12;border:1px solid #3d1a22;border-left:3px solid ${AMBER};border-radius:8px;padding:14px 16px;font-size:13px;color:${TEXT};line-height:1.6">
      ${html}
    </td></tr>
  </table>`;
}

function replyButton(email: string): string {
  return `<table cellpadding="0" cellspacing="0" role="presentation" style="margin-top:20px">
    <tr><td style="background:linear-gradient(135deg,${RED},${RED_DARK});border-radius:100px;padding:0">
      <a href="mailto:${h(email)}" style="display:inline-block;padding:10px 22px;font-size:13px;font-weight:700;color:#fff;text-decoration:none;letter-spacing:.02em">Reply to ${h(email)} &rarr;</a>
    </td></tr>
  </table>`;
}

// ─── Newsletter / exit-intent email ───────────────────────────────────────────

function newsletterSignupEmail(data: Record<string, string>, email: string, page: string, surface: string): string {
  const isExit   = surface === "exit_intent";
  const label    = isExit ? "Exit-intent signup" : "New subscriber";
  const badgeHtml = typeBadge(isExit ? "Exit-intent popup" : "Inline signup form", RED);
  const now = new Date().toLocaleString("en-AU", { timeZone: "Australia/Sydney", dateStyle: "medium", timeStyle: "short" });

  let i = 0;
  const rows =
    dataRow("Email",    email,                      i++ % 2 === 0) +
    dataRow("Page",     page,                       i++ % 2 === 0) +
    dataRow("Type",     data.page_type || "",       i++ % 2 === 0) +
    dataRow("Vertical", data.vertical  || "",       i++ % 2 === 0) +
    dataRow("UTM src",  data.utm_source || "",      i++ % 2 === 0) +
    dataRow("UTM med",  data.utm_medium || "",      i++ % 2 === 0) +
    dataRow("Campaign", data.utm_campaign || "",    i++ % 2 === 0) +
    dataRow("Referrer", data.signup_referrer || "", i++ % 2 === 0) +
    dataRow("Received", now,                        i++ % 2 === 0);

  const body = sectionHeading("New newsletter subscriber") + dataTable(rows) + replyButton(email);
  return emailShell("New subscriber · SaaSpare", label, badgeHtml, body, email);
}

// ─── Contact form email ───────────────────────────────────────────────────────

function contactFormEmail(data: Record<string, string>, email: string): string {
  const topic   = data.topic || "General question";
  const message = data.message || "";
  const now = new Date().toLocaleString("en-AU", { timeZone: "Australia/Sydney", dateStyle: "medium", timeStyle: "short" });
  const PURPLE  = "#a78bfa";

  let i = 0;
  const rows =
    dataRow("From",     email,  i++ % 2 === 0) +
    dataRow("Topic",    topic,  i++ % 2 === 0) +
    dataRow("Received", now,    i++ % 2 === 0);

  const body =
    sectionHeading("Contact form message") +
    dataTable(rows) +
    (message ? messageBlock(message) : "") +
    replyButton(email);

  return emailShell("Contact form · SaaSpare", "New message", typeBadge(topic, PURPLE), body, email);
}

// ─── Stack Audit intake email ─────────────────────────────────────────────────

function auditIntakeEmail(data: Record<string, string>, email: string): string {
  const tier = data.tier || "unknown";
  const tierLabels: Record<string, string> = {
    brief:     "Stack Brief — A$29",
    audit:     "Stack Audit — A$99",
    concierge: "Stack Concierge — A$299",
  };
  const tierColors: Record<string, string> = { brief: GREEN, audit: RED, concierge: "#a78bfa" };
  const tierLabel  = tierLabels[tier] || tier;
  const color      = tierColors[tier]  || RED;
  const now = new Date().toLocaleString("en-AU", { timeZone: "Australia/Sydney", dateStyle: "medium", timeStyle: "short" });

  let i = 0;
  const rows =
    dataRow("Name",        data.name    || "", i++ % 2 === 0) +
    dataRow("Email",       email,              i++ % 2 === 0) +
    dataRow("Company",     data.company || "", i++ % 2 === 0) +
    dataRow("Country",     data.country || "", i++ % 2 === 0) +
    dataRow("Tier",        tierLabel,          i++ % 2 === 0) +
    dataRow("Stack size",  data.stack_size || "", i++ % 2 === 0) +
    dataRow("Spend / mo",  data.spend   || "", i++ % 2 === 0) +
    dataRow("NDA",         data.nda === "yes" ? "Requested" : "Not requested", i++ % 2 === 0) +
    dataRow("Received",    now,                i++ % 2 === 0);

  const body =
    sectionHeading("Stack Audit intake") +
    dataTable(rows) +
    (data.pain ? messageBlock(data.pain) : "") +
    nextStepBanner(
      `<span style="color:${AMBER};font-weight:700">&#9656; Next step:</span> `+
      `Reply to <a href="mailto:${h(email)}" style="color:${RED};font-weight:700">${h(email)}</a> `+
      `to confirm fit, then send a Stripe payment link for <strong>${h(tierLabel)}</strong>.`
    );

  return emailShell("Stack Audit intake · SaaSpare", `New intake — ${tierLabel}`, typeBadge(tierLabel, color), body, email);
}

// ─── User confirmation emails ──────────────────────────────────────────────────────────────────────────────

function buildUserConfirmSubject(surface: string): string {
  if (surface.includes("audit") || surface.includes("intake")) return "Your SaaSpare Stack Audit request — we have it";
  if (surface === "contact" || surface.includes("contact"))    return "Got your message — SaaSpare";
  return "You’re subscribed to the Weekly SaaS Deal Digest";
}

function buildUserConfirmText(surface: string): string {
  if (surface.includes("audit") || surface.includes("intake")) {
    return [
      "Hi,", "",
      "Your Stack Audit request has been received. We’ll review your details and reply within one business day.", "",
      "Browse our comparisons: https://saaspare.org/pages/", "",
      "— The SaaSpare team", "https://saaspare.org",
    ].join("\n");
  }
  if (surface === "contact" || surface.includes("contact")) {
    return [
      "Hi,", "",
      "Thanks for reaching out — we got your message and will reply within one business day.", "",
      "— The SaaSpare team", "https://saaspare.org",
    ].join("\n");
  }
  return [
    "Hi,", "",
    "You’re now subscribed to the Weekly SaaS Deal Digest — every Friday: verified discounts, expiring free trials,", "",
    "quiet price hikes, and the one swap worth making this week.", "",
    "• Browse 1,000+ comparisons: https://saaspare.org/pages/",
    "• SaaS Pricing Index: https://saaspare.org/pages/saas-pricing-index.html",
    "• Free Trial Database: https://saaspare.org/pages/free-trial-database.html",
    "", "— The SaaSpare team", "https://saaspare.org",
  ].join("\n");
}

function buildUserConfirmHtml(data: Record<string, string>, email: string, surface: string): string {
  const isAudit   = surface.includes("audit") || surface.includes("intake") || !!data.tier;
  const isContact = surface === "contact" || surface.includes("contact");
  if (isAudit)   return userAuditConfirmEmail(data, email);
  if (isContact) return userContactConfirmEmail(email);
  return userNewsletterConfirmEmail(email);
}

function userNewsletterConfirmEmail(email: string): string {
  const cards =
    featureCard("&#128202;", "1,000+ Comparisons", "Every major SaaS tool head-to-head", "https://saaspare.org/pages/") +
    featureCard("&#128178;", "Pricing Index", "Real pricing across 16 verticals", "https://saaspare.org/pages/saas-pricing-index.html") +
    featureCard("&#9989;", "Free Trials", "No-card trials worth grabbing now", "https://saaspare.org/pages/free-trial-database.html");

  const body =
    sectionHeading("The Weekly SaaS Deal Digest") +
    `<p style="margin:0 0 20px;font-size:15px;color:${TEXT};line-height:1.7">` +
      "Every Friday: verified discounts, expiring free trials, quiet price hikes, " +
      "and the one tool swap worth making this week. No fluff, no paid placements." +
    `</p>` +
    `<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="margin-bottom:24px"><tr>` +
      `<td width="33%" style="padding-right:8px;vertical-align:top">${featureCard("&#128202;", "1,000+ Comparisons", "Every major SaaS tool head-to-head", "https://saaspare.org/pages/")}</td>` +
      `<td width="33%" style="padding-right:8px;vertical-align:top">${featureCard("&#128178;", "Pricing Index", "Real pricing across 16 verticals", "https://saaspare.org/pages/saas-pricing-index.html")}</td>` +
      `<td width="34%" style="vertical-align:top">${featureCard("&#9989;", "Free Trials", "No-card trials worth grabbing now", "https://saaspare.org/pages/free-trial-database.html")}</td>` +
    `</tr></table>` +
    ctaButton("Browse all comparisons &rarr;", "https://saaspare.org/pages/") +
    `<p style="margin:20px 0 0;font-size:12px;color:${MUTED};text-align:center">` +
      `You subscribed as ${h(email)}. ` +
      `Not you? <a href="mailto:hello@saaspare.org?subject=Unsubscribe" style="color:${MUTED}">Unsubscribe</a>.` +
    `</p>`;

  return emailShell("You’re subscribed · SaaSpare", "Newsletter confirmed",
    typeBadge("Weekly SaaS Deal Digest", GREEN), body);
}

function userContactConfirmEmail(email: string): string {
  const PURPLE = "#a78bfa";
  const body =
    sectionHeading("We got your message") +
    `<p style="margin:0 0 20px;font-size:15px;color:${TEXT};line-height:1.7">` +
      `Thanks for reaching out. We’ll get back to you within one business day at ` +
      `<strong style="color:${TEXT}">${h(email)}</strong>.` +
    `</p>` +
    `<p style="margin:0 0 24px;font-size:14px;color:${MUTED};line-height:1.6">` +
      "Our comparisons and pricing guides are free to browse — no sign-in required." +
    `</p>` +
    ctaButton("Browse comparisons &rarr;", "https://saaspare.org/pages/");
  return emailShell("Got your message · SaaSpare", "Message received",
    typeBadge("Contact", PURPLE), body);
}

function userAuditConfirmEmail(data: Record<string, string>, email: string): string {
  const tier = data.tier || "audit";
  const tierLabels: Record<string, string> = {
    brief:     "Stack Brief — A$29",
    audit:     "Stack Audit — A$99",
    concierge: "Stack Concierge — A$299",
  };
  const tierColors: Record<string, string> = { brief: GREEN, audit: RED, concierge: "#a78bfa" };
  const tierLabel = tierLabels[tier] || tier;
  const color     = tierColors[tier] || RED;
  const name      = (data.name || "").split(" ")[0] || "there";

  const body =
    sectionHeading("Your request is in") +
    `<p style="margin:0 0 16px;font-size:15px;color:${TEXT};line-height:1.7">` +
      `Hi ${h(name)}, your <strong style="color:${TEXT}">${h(tierLabel)}</strong> intake is received. ` +
      "We’ll review your stack and reply within one business day to confirm fit and next steps." +
    `</p>` +
    nextStepBanner(
      `<span style="color:${AMBER};font-weight:700">&#9656; What happens next:</span> ` +
      `We’ll email <strong>${h(email)}</strong> to confirm the engagement and walk you through getting started.`
    ) +
    `<p style="margin:20px 0 8px;font-size:13px;color:${MUTED}">In the meantime:</p>` +
    ctaButton("Browse all comparisons &rarr;", "https://saaspare.org/pages/");

  return emailShell(`Audit request received · SaaSpare`, `Intake — ${tierLabel}`,
    typeBadge(tierLabel, color), body);
}

function featureCard(icon: string, title: string, desc: string, url: string): string {
  return `<a href="${h(url)}" style="display:block;text-decoration:none;background:${CARD_EDGE};border:1px solid ${DIM};border-radius:10px;padding:14px 12px;text-align:center">` +
    `<div style="font-size:22px;margin-bottom:6px">${icon}</div>` +
    `<div style="font-size:12px;font-weight:800;color:${TEXT};margin-bottom:3px">${h(title)}</div>` +
    `<div style="font-size:11px;color:${MUTED};line-height:1.4">${h(desc)}</div>` +
  `</a>`;
}

function ctaButton(label: string, url: string): string {
  return `<table cellpadding="0" cellspacing="0" role="presentation" style="margin:0 auto">` +
    `<tr><td style="background:linear-gradient(135deg,${RED},${RED_DARK});border-radius:100px;padding:0">` +
    `<a href="${h(url)}" style="display:inline-block;padding:13px 28px;font-size:14px;font-weight:700;color:#fff;text-decoration:none;letter-spacing:.02em">${label}</a>` +
    `</td></tr></table>`;
}
// ─── Utilities ────────────────────────────────────────────────────────────────

function h(value: string): string {
  return value.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[c] ?? c));
}

function json(body: unknown, status: number, headers: HeadersInit): Response {
  return Response.json(body, { status, headers });
}

function allowedOrigins(env: Env): string[] {
  const configured = (env.ALLOWED_ORIGINS || "").split(",").map((o) => o.trim()).filter(Boolean);
  return configured.length ? configured : DEFAULT_ALLOWED_ORIGINS;
}

function corsHeaders(request: Request, env: Env): HeadersInit {
  const origin = request.headers.get("Origin") || "";
  const allowOrigin = allowedOrigins(env).includes(origin) ? origin : DEFAULT_ALLOWED_ORIGINS[0];
  return {
    "Access-Control-Allow-Origin": allowOrigin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}

async function parseRequest(request: Request): Promise<Record<string, string>> {
  const type = request.headers.get("Content-Type") || "";
  if (type.includes("application/json")) {
    const body = (await request.json()) as Record<string, unknown>;
    return Object.fromEntries(Object.entries(body).map(([k, v]) => [k, clean(String(v ?? ""))]));
  }
  const form = await request.formData();
  return Object.fromEntries([...form.entries()].map(([k, v]) => [k, clean(String(v))]));
}

function clean(value: string): string {
  return value.replace(/\r/g, "").replace(/\u0000/g, "").trim().slice(0, MAX_FIELD_LENGTH);
}

function buildTextBody(data: Record<string, string>, email: string, page: string): string {
  const skipKeys = new Set(["_captcha", "_next", "_autoresponse", "_template", "website", "_gotcha"]);
  const fields = Object.entries(data)
    .filter(([k]) => !skipKeys.has(k) && !k.startsWith("utm_"))
    .map(([k, v]) => `${k}: ${v || "(blank)"}`)
    .join("\n");
  return `New SaaSpare lead\n\nEmail: ${email}\nPage: ${page}\nReceived: ${new Date().toISOString()}\n\n${fields}`;
}
