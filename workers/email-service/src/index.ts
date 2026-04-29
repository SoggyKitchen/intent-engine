type SendEmailBinding = {
  send(message: { from: string; to: string; subject: string; text: string; html?: string }): Promise<void>;
};

export interface Env {
  SEND_EMAIL: SendEmailBinding;
  LEAD_NOTIFY_TO?: string;
  LEAD_FROM?: string;
  ALLOWED_ORIGINS?: string;
}

const DEFAULT_ALLOWED_ORIGINS = ["https://saaspare.org", "https://www.saaspare.org"];

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const headers = corsHeaders(request, env);
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers });
    if (request.method !== "POST") return json({ ok: false, error: "method_not_allowed" }, 405, headers);
    if (!env.LEAD_NOTIFY_TO) return json({ ok: false, error: "lead_notify_to_missing" }, 503, headers);

    const origin = request.headers.get("Origin");
    if (origin && !allowedOrigins(env).includes(origin)) {
      return json({ ok: false, error: "origin_not_allowed" }, 403, headers);
    }

    const data = await parseRequest(request);
    if ((data._gotcha || data.website || "").trim()) return json({ ok: true, ignored: true }, 200, headers);

    const email = clean(data.email || data.from || "");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return json({ ok: false, error: "valid_email_required" }, 400, headers);
    }

    const subject = clean(data._subject || data.subject || "New SaaSpare lead").slice(0, 160);
    const text = buildTextBody(data, email, request.headers.get("Referer") || "unknown");
    await env.SEND_EMAIL.send({
      from: env.LEAD_FROM || "hello@saaspare.org",
      to: env.LEAD_NOTIFY_TO,
      subject,
      text,
      html: `<pre style="font-family:ui-monospace,Menlo,Consolas,monospace;white-space:pre-wrap">${escapeHtml(text)}</pre>`,
    });

    return json({ ok: true }, 200, headers);
  },
};

function allowedOrigins(env: Env): string[] {
  const configured = (env.ALLOWED_ORIGINS || "")
    .split(",")
    .map((origin) => origin.trim())
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

function json(body: unknown, status: number, headers: HeadersInit): Response {
  return Response.json(body, { status, headers });
}

async function parseRequest(request: Request): Promise<Record<string, string>> {
  const type = request.headers.get("Content-Type") || "";
  if (type.includes("application/json")) {
    const body = (await request.json()) as Record<string, unknown>;
    return Object.fromEntries(Object.entries(body).map(([key, value]) => [key, clean(String(value ?? ""))]));
  }
  const form = await request.formData();
  return Object.fromEntries([...form.entries()].map(([key, value]) => [key, clean(String(value))]));
}

function clean(value: string): string {
  return value.replace(/\r/g, "").replace(/\u0000/g, "").trim().slice(0, 4000);
}

function buildTextBody(data: Record<string, string>, email: string, page: string): string {
  const fields = Object.entries(data)
    .filter(([key]) => !key.startsWith("_captcha") && !key.startsWith("_next") && !key.startsWith("_autoresponse"))
    .map(([key, value]) => `${key}: ${value || "(blank)"}`)
    .join("\n");
  return `New SaaSpare lead\n\nEmail: ${email}\nPage: ${page}\nReceived: ${new Date().toISOString()}\n\n${fields}`;
}

function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char] || char));
}
