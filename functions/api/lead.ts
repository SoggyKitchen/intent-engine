/**
 * Cloudflare Pages Function — /api/lead
 *
 * Accepts form submissions from every SaaSpare page and forwards them via
 * Resend (https://resend.com — 3,000 emails/month free, no credit card).
 *
 * Required env vars (set in Cloudflare Pages → Settings → Environment variables):
 *   RESEND_API_KEY   — re_xxxxxxxx from resend.com/api-keys
 *   LEAD_NOTIFY_TO   — inbox that receives every submission, e.g. hello@saaspare.org
 *
 * Optional env vars:
 *   LEAD_FROM        — verified sender address (default: onboarding@resend.dev works
 *                      without domain verification; use hello@saaspare.org once your
 *                      domain is verified in Resend dashboard)
 *   ALLOWED_ORIGINS  — comma-separated list (default: saaspare.org + www.)
 */

type Env = {
  RESEND_API_KEY?: string;
  LEAD_NOTIFY_TO?: string;
  LEAD_FROM?: string;
  ALLOWED_ORIGINS?: string;
  // Legacy Cloudflare Email binding — kept for backward compat, ignored if RESEND_API_KEY set
  SEND_EMAIL?: { send(msg: Record<string, string>): Promise<void> };
};

const MAX_FIELD_LENGTH = 4000;
const DEFAULT_ALLOWED_ORIGINS = ["https://saaspare.org", "https://www.saaspare.org"];
const RESEND_API = "https://api.resend.com/emails";

// ─── Entry points ────────────────────────────────────────────────────────────

export const onRequestOptions: PagesFunction<Env> = async ({ request, env }) => {
  return new Response(null, { status: 204, headers: corsHeaders(request, env) });
};

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  const headers = corsHeaders(request, env);

  // Must have at least one delivery method configured
  if (!env.RESEND_API_KEY && !env.SEND_EMAIL) {
    return json({ ok: false, error: "email_not_configured" }, 503, headers);
  }
  if (!env.LEAD_NOTIFY_TO) {
    return json({ ok: false, error: "email_not_configured" }, 503, headers);
  }

  // CORS guard
  const origin = request.headers.get("Origin");
  if (origin && !allowedOrigins(env).includes(origin)) {
    return json({ ok: false, error: "origin_not_allowed" }, 403, headers);
  }

  // Parse body
  const data = await parseRequest(request);

  // Honeypot
  if ((data._gotcha || data.website || "").trim()) {
    return json({ ok: true, ignored: true }, 200, headers);
  }

  // Validate email
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
      await sendViaResend(env.RESEND_API_KEY, {
        from: env.LEAD_FROM || "SaaSpare <onboarding@resend.dev>",
        to: env.LEAD_NOTIFY_TO,
        reply_to: email,
        subject,
        html,
        text,
      });
    } else if (env.SEND_EMAIL) {
      // Fallback: legacy Cloudflare Email binding
      await env.SEND_EMAIL.send({
        from: env.LEAD_FROM || "hello@saaspare.org",
        to: env.LEAD_NOTIFY_TO,
        subject,
        text,
        html,
      });
    }
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error("lead.ts send error:", msg);
    // Still return ok=true to the user — don't expose internal errors
    // Log is visible in Cloudflare Pages Functions logs
    return json({ ok: true, _warn: "delivery_issue" }, 200, headers);
  }

  return json({ ok: true }, 200, headers);
};

// ─── Resend HTTP client ──────────────────────────────────────────────────────

async function sendViaResend(
  apiKey: string,
  payload: { from: string; to: string; reply_to: string; subject: string; html: string; text: string }
): Promise<void> {
  const resp = await fetch(RESEND_API, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!resp.ok) {
    const body = await resp.text().catch(() => "(unreadable)");
    throw new Error(`Resend ${resp.status}: ${body}`);
  }
}

// ─── Email builders ──────────────────────────────────────────────────────────

function buildSubject(data: Record<string, string>, email: string, surface: string): string {
  const raw = clean(data._subject || data.subject || "");
  if (raw) return raw.slice(0, 160);

  if (surface === "exit_intent") return `[SaaSpare] Exit-intent signup — ${email}`;
  if (surface.includes("newsletter") || surface.includes("digest")) return `[SaaSpare] Newsletter signup — ${email}`;
  if (surface.includes("audit") || surface.includes("intake")) return `[SaaSpare] Stack Audit intake — ${data.tier || "unknown tier"}`;
  if (surface === "contact") return `[SaaSpare] Contact form — ${data.topic || "General question"}`;
  return `[SaaSpare] New lead — ${email}`;
}

/** Full branded HTML email — different layout per surface type */
function buildHtmlEmail(
  data: Record<string, string>,
  email: string,
  page: string,
  surface: string
): string {
  const isAudit = surface.includes("audit") || surface.includes("intake") || !!data.tier;
  const isContact = surface === "contact" || !!data.topic;

  if (isAudit) return auditIntakeEmail(data, email);
  if (isContact) return contactFormEmail(data, email);
  return newsletterSignupEmail(data, email, page, surface);
}

// Shared layout wrapper
function emailShell(title: string, accentColor: string, body: string): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${h(title)}</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f8;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f8;padding:32px 16px">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">

  <!-- Header -->
  <tr><td style="background:${accentColor};border-radius:12px 12px 0 0;padding:28px 32px;text-align:center">
    <span style="font-size:22px;font-weight:800;color:#fff;letter-spacing:-.5px">Saa<span style="color:rgba(255,255,255,.65)">Spare</span></span>
    <span style="display:block;font-size:12px;color:rgba(255,255,255,.65);margin-top:4px;font-weight:500">${h(title)}</span>
  </td></tr>

  <!-- Body -->
  <tr><td style="background:#fff;padding:32px;border-radius:0 0 12px 12px;box-shadow:0 4px 24px rgba(0,0,0,.08)">
    ${body}
    <!-- Footer -->
    <p style="margin:28px 0 0;padding-top:20px;border-top:1px solid #eee;font-size:11px;color:#9ca3af;text-align:center">
      SaaSpare &middot; Unbiased B2B SaaS comparisons &middot; No paid rankings<br>
      <a href="https://saaspare.org" style="color:#9ca3af">saaspare.org</a>
    </p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>`;
}

function row(label: string, value: string): string {
  if (!value || value === "(blank)") return "";
  return `<tr>
    <td style="padding:8px 12px;font-size:13px;font-weight:600;color:#374151;white-space:nowrap;vertical-align:top;width:160px">${h(label)}</td>
    <td style="padding:8px 12px;font-size:13px;color:#4b5563;word-break:break-word">${h(value)}</td>
  </tr>`;
}

function table(rows: string): string {
  return `<table width="100%" cellpadding="0" cellspacing="0"
    style="border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;margin:16px 0;border-collapse:collapse">
    <tbody>${rows}</tbody>
  </table>`;
}

function badge(text: string, color: string): string {
  return `<span style="display:inline-block;background:${color};color:#fff;font-size:11px;font-weight:700;padding:3px 10px;border-radius:100px;letter-spacing:.04em;text-transform:uppercase">${h(text)}</span>`;
}

// ── Newsletter / exit-intent signup email ────────────────────────────────────
function newsletterSignupEmail(
  data: Record<string, string>,
  email: string,
  page: string,
  surface: string
): string {
  const surfaceLabel = surface === "exit_intent" ? "Exit-intent popup" : "Inline signup form";
  const pageType = data.page_type || "";
  const vertical = data.vertical || "";

  const body = `
    <p style="margin:0 0 16px;font-size:16px;font-weight:700;color:#111827">New newsletter subscriber</p>
    ${badge(surfaceLabel, "#e94560")}
    ${table(
      row("Email", email) +
      row("Page", page) +
      row("Page type", pageType) +
      row("Vertical", vertical) +
      row("UTM source", data.utm_source || "") +
      row("UTM medium", data.utm_medium || "") +
      row("UTM campaign", data.utm_campaign || "") +
      row("Landing URL", data.landing_url || "") +
      row("Referrer", data.signup_referrer || "") +
      row("Received", new Date().toLocaleString("en-AU", { timeZone: "Australia/Sydney", dateStyle: "medium", timeStyle: "short" }))
    )}
    <p style="margin:16px 0 0;font-size:13px;color:#6b7280">
      <a href="mailto:${h(email)}" style="color:#e94560;font-weight:600">Reply directly to ${h(email)}</a>
    </p>`;

  return emailShell("New subscriber", "#e94560", body);
}

// ── Contact form email ────────────────────────────────────────────────────────
function contactFormEmail(data: Record<string, string>, email: string): string {
  const topic = data.topic || "General question";
  const message = data.message || "";

  const body = `
    <p style="margin:0 0 16px;font-size:16px;font-weight:700;color:#111827">New contact form message</p>
    ${badge(topic, "#7c3aed")}
    ${table(
      row("From", email) +
      row("Topic", topic) +
      row("Received", new Date().toLocaleString("en-AU", { timeZone: "Australia/Sydney", dateStyle: "medium", timeStyle: "short" }))
    )}
    ${message ? `
    <p style="margin:16px 0 6px;font-size:13px;font-weight:600;color:#374151">Message</p>
    <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:16px;font-size:14px;color:#374151;line-height:1.6;white-space:pre-wrap">${h(message)}</div>
    ` : ""}
    <p style="margin:16px 0 0;font-size:13px;color:#6b7280">
      <a href="mailto:${h(email)}" style="color:#7c3aed;font-weight:600">Reply to ${h(email)}</a>
    </p>`;

  return emailShell("Contact form", "#7c3aed", body);
}

// ── Stack Audit intake email ─────────────────────────────────────────────────
function auditIntakeEmail(data: Record<string, string>, email: string): string {
  const tier = data.tier || "unknown";
  const tierLabels: Record<string, string> = {
    brief: "Stack Brief — A$29",
    audit: "Stack Audit — A$99",
    concierge: "Stack Concierge — A$299",
  };
  const tierLabel = tierLabels[tier] || tier;
  const tierColors: Record<string, string> = { brief: "#059669", audit: "#e94560", concierge: "#7c3aed" };
  const accentColor = tierColors[tier] || "#e94560";

  const body = `
    <p style="margin:0 0 16px;font-size:16px;font-weight:700;color:#111827">New Stack Audit intake</p>
    ${badge(tierLabel, accentColor)}
    ${table(
      row("Name", data.name || "") +
      row("Email", email) +
      row("Company", data.company || "") +
      row("Country", data.country || "") +
      row("Tier", tierLabel) +
      row("Stack size", data.stack_size || "") +
      row("Monthly spend", data.spend || "") +
      row("NDA requested", data.nda === "yes" ? "Yes" : "No") +
      row("Received", new Date().toLocaleString("en-AU", { timeZone: "Australia/Sydney", dateStyle: "medium", timeStyle: "short" }))
    )}
    ${data.pain ? `
    <p style="margin:16px 0 6px;font-size:13px;font-weight:600;color:#374151">Pain point</p>
    <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:16px;font-size:14px;color:#374151;line-height:1.6;white-space:pre-wrap">${h(data.pain)}</div>
    ` : ""}
    <p style="margin:20px 0 0;padding:16px;background:#fef3c7;border:1px solid #fcd34d;border-radius:8px;font-size:13px;color:#92400e">
      <strong>Next step:</strong> Confirm fit by replying to
      <a href="mailto:${h(email)}" style="color:#92400e;font-weight:600">${h(email)}</a>,
      then send a Stripe payment link for <strong>${h(tierLabel)}</strong>.
    </p>`;

  return emailShell("Stack Audit intake", accentColor, body);
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function h(value: string): string {
  return value.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[c] ?? c));
}

function json(body: unknown, status: number, headers: HeadersInit): Response {
  return Response.json(body, { status, headers });
}

function allowedOrigins(env: Env): string[] {
  const configured = (env.ALLOWED_ORIGINS || "")
    .split(",")
    .map((o) => o.trim())
    .filter(Boolean);
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
