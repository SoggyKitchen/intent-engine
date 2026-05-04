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
      // 2. User confirmation — awaited with own try/catch so errors never break owner notify
      try {
        const confSubject = buildUserConfirmSubject(surface);
        const confHtml    = buildUserConfirmHtml(data, email, surface);
        const confText    = buildUserConfirmText(surface);
        await sendViaResend(env.RESEND_API_KEY, {
          from: env.LEAD_FROM || "SaaSpare <hello@saaspare.org>",
          to: email,
          reply_to: env.LEAD_NOTIFY_TO || "hello@saaspare.org",
          subject: confSubject,
          html: confHtml,
          text: confText,
        });
      } catch (ce: unknown) {
        console.error("user confirm error:", ce instanceof Error ? ce.message : String(ce));
      }
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
        <!-- logo -->
        <table cellpadding="0" cellspacing="0" role="presentation" style="margin:0 auto 12px">
          <tr>
            <td style="vertical-align:middle;padding-right:10px">
              <img src="data:image/png;base64,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" alt="SaaSpare" width="40" height="40"
                style="display:block;border-radius:10px;border:0;width:40px;height:40px">
            </td>
            <td style="vertical-align:middle">
              <span style="font-size:20px;font-weight:800;color:#ffffff;letter-spacing:-.5px;line-height:1">Saa<span style="color:rgba(255,255,255,.65)">Spare</span></span>
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
      `Not you? <a href="mailto:hello@saaspare.org" style="color:${MUTED}">Unsubscribe</a>.` +
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
