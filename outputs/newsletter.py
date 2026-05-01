"""
Newsletter module — two jobs:
1. Inject email capture form into every SEO page (grows list passively)
2. Generate weekly digest email to send to subscribers (monetized with sponsor slot)

Free stack: Brevo free tier (300 emails/day), or Mailchimp (500 contacts free).
Once list hits 500+ subscribers: charge $200-500/issue for a sponsor slot.
"""
import time
from pathlib import Path
from typing import Optional

from core.db import db
from core.logger import log
from core.secrets import get, DRY_RUN
from llm.router import complete_json

PAGES_DIR = Path("site/pages")
BREVO_API = "https://api.brevo.com/v3"
MAILCHIMP_API = "https://us1.api.mailchimp.com/3.0"

EMAIL_CAPTURE_SNIPPET = """
<div style="background:#1a1a2e;color:#fff;padding:1.5rem 2rem;border-radius:8px;margin:2rem 0;text-align:center;">
  <h3 style="margin:0 0 0.5rem;font-size:1.2rem;">Get weekly B2B software insights</h3>
  <p style="margin:0 0 1rem;color:#aaa;font-size:0.9rem;">Join {subscriber_count}+ founders and engineers. Free, weekly, no spam.</p>
  <form action="{form_action}" method="POST" style="display:flex;gap:0.5rem;justify-content:center;flex-wrap:wrap;">
    <input type="email" name="email" placeholder="your@email.com" required
           style="padding:0.6rem 1rem;border:none;border-radius:4px;font-size:1rem;min-width:220px;">
    <button type="submit"
            style="padding:0.6rem 1.5rem;background:#e94560;color:#fff;border:none;border-radius:4px;font-size:1rem;cursor:pointer;font-weight:600;">
      Subscribe
    </button>
  </form>
</div>
"""


def inject_capture_forms():
    """Add email capture form to all SEO pages that don't have one."""
    form_action = get("EMAIL_FORM_ACTION", "https://app.brevo.com/subscription/subscribe")
    subscriber_count = _get_subscriber_count()
    snippet = EMAIL_CAPTURE_SNIPPET.format(
        form_action=form_action,
        subscriber_count=subscriber_count,
    )
    injected = 0
    for html_file in PAGES_DIR.glob("*.html"):
        content = html_file.read_text(encoding="utf-8")
        if "Subscribe" in content and "email" in content:
            continue
        if "</article>" in content:
            content = content.replace("</article>", snippet + "</article>", 1)
        elif "<footer" in content:
            content = content.replace("<footer", snippet + "<footer", 1)
        else:
            content = content.replace("</body>", snippet + "</body>", 1)
        html_file.write_text(content, encoding="utf-8")
        injected += 1
    log.info(f"Email capture injected into {injected} pages")


def generate_weekly_digest() -> Optional[str]:
    """Generate this week's newsletter digest HTML."""
    since_ts = int(time.time()) - 7 * 86400

    with db() as conn:
        top_signals = conn.execute("""
            SELECT s.vertical, s.intent, s.estimated_deal_usd, r.title, r.url, s.llm_reasoning
            FROM scored_signals s
            JOIN raw_signals r ON r.id = s.raw_id
            WHERE s.ts >= ? AND s.intent >= 70
            ORDER BY s.profit_score DESC
            LIMIT 8
        """, (since_ts,)).fetchall()

        new_pages = conn.execute("""
            SELECT title, published_url, vertical
            FROM outputs
            WHERE type = 'seo_page' AND created_at >= ?
            ORDER BY created_at DESC LIMIT 5
        """, (since_ts,)).fetchall()

    if not top_signals and not new_pages:
        return None

    signals_text = "\n".join(
        f"- [{r['title'][:80]}]({r['url']}) — {r['llm_reasoning'][:100]}"
        for r in top_signals
    )
    pages_text = "\n".join(
        f"- [{p['title']}]({p['published_url'] or '#'})"
        for p in new_pages
    )

    result = complete_json(f"""
Generate a weekly B2B software newsletter digest. Professional, concise, genuinely useful.

Top signals this week:
{signals_text}

New comparison pages:
{pages_text}

Return JSON:
{{
  "subject": "<engaging email subject line>",
  "intro": "<2-3 sentences warm intro>",
  "signal_summaries": ["<1-sentence insight per top signal, 3-5 total>"],
  "cta": "<closing line with link to best new page>",
  "sponsor_slot": "<placeholder: [SPONSOR SLOT — $300 to reach {{}} subscribers]>"
}}
""")
    if not result:
        return None

    subscriber_count = _get_subscriber_count()
    html = _render_digest(result, new_pages, subscriber_count)
    out_path = Path("outputs/generated") / f"newsletter_{time.strftime('%Y-%m-%d')}.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    log.info(f"Newsletter digest generated: {out_path}")
    return str(out_path)


def _render_digest(data: dict, pages: list, subscriber_count: int) -> str:
    domain = get("SITE_DOMAIN", "https://yourdomain.com")
    items = "".join(f"<li>{s}</li>" for s in data.get("signal_summaries", []))
    page_links = "".join(
        f'<li><a href="{p["published_url"] or domain}" style="color:#e94560;">{p["title"]}</a></li>'
        for p in pages
    )
    sponsor = data.get("sponsor_slot", "").replace(
        "{}", str(subscriber_count)
    )
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>{data.get('subject', 'Weekly B2B Digest')}</title></head>
<body style="font-family:-apple-system,sans-serif;max-width:600px;margin:0 auto;padding:2rem;color:#333;">
  <h1 style="color:#1a1a2e;font-size:1.4rem;">B2B Software Intent Digest</h1>
  <p style="color:#666;font-size:0.9rem;">{time.strftime('%B %d, %Y')} — {subscriber_count} subscribers</p>
  <p>{data.get('intro', '')}</p>
  <div style="background:#fff3cd;padding:1rem;border-radius:6px;margin:1rem 0;font-size:0.85rem;color:#856404;">
    <strong>Sponsor slot:</strong> {sponsor}
  </div>
  <h2 style="font-size:1.1rem;color:#1a1a2e;">This Week's Buyer Intent Signals</h2>
  <ul>{items}</ul>
  <h2 style="font-size:1.1rem;color:#1a1a2e;">New Comparison Pages</h2>
  <ul>{page_links}</ul>
  <p style="margin-top:2rem;font-size:0.95rem;">{data.get('cta', '')}</p>
  <hr style="margin:2rem 0;border:none;border-top:1px solid #eee;">
  <p style="color:#999;font-size:0.8rem;">You're receiving this because you subscribed at {domain}.
  <a href="{{{{unsubscribe}}}}" style="color:#999;">Unsubscribe</a></p>
</body></html>"""


def _get_subscriber_count() -> int:
    brevo_key = get("BREVO_API_KEY")
    if not brevo_key:
        return 0
    try:
        import httpx
        resp = httpx.get(f"{BREVO_API}/contacts/lists",
                         headers={"api-key": brevo_key}, timeout=10)
        if resp.status_code == 200:
            lists = resp.json().get("lists", [])
            return sum(l.get("totalActiveContacts", 0) for l in lists)
    except Exception:
        pass
    return 0


def send_digest(digest_path: str):
    """Send digest via Brevo API to all subscribers."""
    if DRY_RUN:
        log.info(f"[DRY RUN] Would send newsletter: {digest_path}")
        return
    brevo_key = get("BREVO_API_KEY")
    if not brevo_key:
        log.warning("BREVO_API_KEY not set — skipping send")
        return
    html = Path(digest_path).read_text(encoding="utf-8")
    import httpx
    resp = httpx.post(f"{BREVO_API}/emailCampaigns", headers={
        "api-key": brevo_key, "content-type": "application/json"
    }, json={
        "name": f"Digest {time.strftime('%Y-%m-%d')}",
        "subject": f"B2B Buyer Signals — {time.strftime('%b %d')}",
        "sender": {"name": "B2B Signals", "email": get("SENDER_EMAIL", "digest@yourdomain.com")},
        "type": "classic",
        "htmlContent": html,
        "recipients": {"lists": [int(get("BREVO_LIST_ID", "1"))]},
    }, timeout=30)
    if resp.status_code == 201:
        campaign_id = resp.json()["id"]
        httpx.post(f"{BREVO_API}/emailCampaigns/{campaign_id}/sendNow",
                   headers={"api-key": brevo_key}, timeout=20)
        log.info(f"Newsletter sent (campaign {campaign_id})")
    else:
        log.error(f"Newsletter send failed: {resp.text}")
