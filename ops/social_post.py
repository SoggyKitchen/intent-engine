"""
Social media auto-poster.
- Twitter/X: publish or queue link-first distribution.
- Reddit: stage helpful, non-spammy replies for high-intent threads.
- Instagram/TikTok: generate post-ready weekly content kits.
"""
import base64
import hashlib
import hmac
import json
import secrets as sec
import smtplib
import time
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

import httpx

from core.db import db
from core.logger import log
from core.secrets import DRY_RUN, get
from llm.router import complete_json

POSTED_FILE = Path("data/social_posted.txt")
SOCIAL_QUEUE_DIR = Path("outputs/generated")
SOCIAL_PACK_DIR = Path("outputs/generated/social")
SOCIAL_RUN_REPORT = SOCIAL_PACK_DIR / "social_run_latest.json"


def _page_url(page: dict, domain: str) -> str:
    return page["published_url"] or f"{domain}/pages/{slugify_title(page['title'])}"


def _social_url(url: str, source: str, campaign: str, content: str = "") -> str:
    parsed = urllib.parse.urlsplit(url)
    params = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    params["utm_source"] = source
    params["utm_medium"] = "social"
    params["utm_campaign"] = campaign
    if content:
        params["utm_content"] = content
    return urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urllib.parse.urlencode(params),
            parsed.fragment,
        )
    )


def _already_posted(url: str) -> bool:
    POSTED_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not POSTED_FILE.exists():
        return False
    uid = hashlib.sha256(url.encode()).hexdigest()[:12]
    return uid in POSTED_FILE.read_text()


def _mark_posted(url: str):
    uid = hashlib.sha256(url.encode()).hexdigest()[:12]
    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(uid + "\n")


def _allowed_subreddits() -> set[str]:
    raw = get("REDDIT_ALLOWED_SUBREDDITS", "")
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def _normalize_linkedin_person_urn(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if value.startswith("urn:li:person:"):
        return value
    return f"urn:li:person:{value}"


def _write_social_run_report(summary: dict):
    SOCIAL_PACK_DIR.mkdir(parents=True, exist_ok=True)
    SOCIAL_RUN_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def _select_social_pages(limit: int, fresh_window_seconds: int = 86400) -> list[dict]:
    now = int(time.time())
    with db() as conn:
        rows = conn.execute(
            """
            SELECT title, COALESCE(published_url, '') AS published_url, vertical, created_at,
                   COALESCE(views, 0) AS views, COALESCE(revenue, 0) AS revenue
            FROM outputs
            WHERE type = 'seo_page'
              AND published_url IS NOT NULL
              AND published_url != ''
            ORDER BY created_at DESC
        """
        ).fetchall()

    seen: set[str] = set()
    fresh: list[dict] = []
    evergreen: list[dict] = []
    for row in rows:
        page = dict(row)
        url = page["published_url"]
        if url in seen:
            continue
        seen.add(url)
        is_fresh = page["created_at"] >= (now - fresh_window_seconds)
        known_vertical = (page.get("vertical") or "unknown") != "unknown"
        if is_fresh and known_vertical:
            fresh.append(page)
        else:
            evergreen.append(page)

    evergreen.sort(key=lambda item: (item["revenue"], item["views"], item["created_at"]), reverse=True)
    return (fresh + evergreen)[:limit]


def _match_page_for_signal(signal: dict, pages: list[dict], domain: str) -> dict | None:
    signal_text = f"{signal.get('title', '')} {signal.get('body', '')}".lower()
    best_page = None
    best_score = -1
    for page in pages:
        score = 0
        if page.get("vertical") == signal.get("vertical"):
            score += 5
        for token in slugify_title(page["title"]).split("-"):
            if len(token) > 3 and token in signal_text:
                score += 1
        if score > best_score:
            best_score = score
            best_page = page
    return best_page or (pages[0] if pages else None)


def run_twitter():
    api_key = get("TWITTER_API_KEY")
    api_secret = get("TWITTER_API_SECRET")
    access_token = get("TWITTER_ACCESS_TOKEN")
    access_secret = get("TWITTER_ACCESS_TOKEN_SECRET")

    domain = get("SITE_DOMAIN", "https://yourdomain.com")

    pages = _select_social_pages(limit=3, fresh_window_seconds=86400)

    _write_social_queue(pages, domain)

    tweets: list[dict] = []
    for page in pages:
        url = _social_url(
            _page_url(page, domain),
            source="x",
            campaign="social_launch",
            content=slugify_title(page["title"]),
        )
        tweet_text = _generate_tweet(page["title"], page["vertical"], url)
        if tweet_text:
            tweets.append({"text": tweet_text, "url": url, "title": page["title"]})

    _write_tweet_launchpad(tweets)
    send_tweet_email(tweets)

    if not all([api_key, api_secret, access_token, access_secret]):
        log.info("Twitter: launchpad written - open outputs/generated/tweet_launchpad.html to post")
        return

    for item in tweets:
        if _already_posted(item["url"]):
            continue
        if DRY_RUN:
            log.info(f"[DRY RUN] Would tweet: {item['text'][:80]}...")
            continue
        try:
            _post_tweet(item["text"], api_key, api_secret, access_token, access_secret)
            _mark_posted(item["url"])
            log.info(f"Tweeted: {item['text'][:60]}...")
            time.sleep(60)
        except Exception as e:
            log.warning(f"Tweet failed: {e}")

    _write_social_run_report({"twitter_candidates": len(pages)})


def _write_tweet_launchpad(tweets: list[dict]):
    if not tweets:
        return
    SOCIAL_QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d")
    rows = ""
    for item in tweets:
        intent_url = "https://twitter.com/intent/tweet?text=" + urllib.parse.quote(item["text"], safe="")
        rows += f"""
        <div class="card">
          <div class="title">{item['title']}</div>
          <div class="tweet">{item['text']}</div>
          <a class="btn" href="{intent_url}" target="_blank">Open in Twitter ↗</a>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SaaSpare Tweet Launchpad — {stamp}</title>
<style>
body{{font-family:system-ui,sans-serif;background:#0a0a0a;color:#e8e8e8;padding:2rem;max-width:700px;margin:0 auto}}
h1{{color:#1d9bf0;margin-bottom:.25rem}}
.sub{{color:#666;font-size:.85rem;margin-bottom:2rem}}
.card{{background:#111;border:1px solid #222;border-radius:12px;padding:1.25rem;margin-bottom:1rem}}
.title{{font-size:.75rem;color:#555;margin-bottom:.5rem;text-transform:uppercase;letter-spacing:.5px}}
.tweet{{font-size:.95rem;line-height:1.5;margin-bottom:1rem;white-space:pre-wrap}}
.btn{{display:inline-block;background:#1d9bf0;color:#fff;padding:.5rem 1.25rem;border-radius:100px;text-decoration:none;font-weight:600;font-size:.875rem}}
.btn:hover{{background:#1a8cd8}}
</style>
</head>
<body>
<h1>Tweet Launchpad</h1>
<p class="sub">Generated {stamp} — click "Open in Twitter" for each tweet, then hit Post.</p>
{rows}
</body>
</html>"""
    out = SOCIAL_QUEUE_DIR / "tweet_launchpad.html"
    out.write_text(html, encoding="utf-8")
    log.info(f"Tweet launchpad written: {out}")


def build_social_pack(limit: int = 5) -> Optional[str]:
    domain = get("SITE_DOMAIN", "https://yourdomain.com")
    SOCIAL_PACK_DIR.mkdir(parents=True, exist_ok=True)

    pages = _select_social_pages(limit=limit, fresh_window_seconds=7 * 86400)

    if not pages:
        log.info("No SEO pages available for social pack generation")
        return None

    payload: list[dict] = []
    for page in pages:
        url = _page_url(page, domain)
        copy = _generate_social_copy(
            page["title"],
            page["vertical"],
            {
                "x": _social_url(url, "x", "social_pack", slugify_title(page["title"])),
                "linkedin": _social_url(url, "linkedin", "social_pack", slugify_title(page["title"])),
                "reddit": _social_url(url, "reddit", "social_pack", slugify_title(page["title"])),
                "instagram": _social_url(url, "instagram", "social_pack", slugify_title(page["title"])),
                "tiktok": _social_url(url, "tiktok", "social_pack", slugify_title(page["title"])),
            },
        )
        payload.append(
            {
                "title": page["title"],
                "vertical": page["vertical"],
                "url": url,
                **copy,
            }
        )

    stamp = time.strftime("%Y-%m-%d_%H%M%S")
    json_path = SOCIAL_PACK_DIR / f"social_pack_{stamp}.json"
    md_path = SOCIAL_PACK_DIR / f"social_pack_{stamp}.md"
    calendar_path = SOCIAL_PACK_DIR / f"social_calendar_{stamp}.md"
    latest_json = SOCIAL_PACK_DIR / "social_pack_latest.json"
    latest_md = SOCIAL_PACK_DIR / "social_pack_latest.md"
    latest_calendar = SOCIAL_PACK_DIR / "social_calendar_latest.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_render_social_pack_markdown(payload), encoding="utf-8")
    calendar_path.write_text(
        _render_social_calendar_markdown(_build_social_calendar(payload)),
        encoding="utf-8",
    )
    latest_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    latest_md.write_text(_render_social_pack_markdown(payload), encoding="utf-8")
    latest_calendar.write_text(
        _render_social_calendar_markdown(_build_social_calendar(payload)),
        encoding="utf-8",
    )
    log.info(f"Social pack generated: {json_path}")
    return str(json_path)


def _generate_tweet(title: str, vertical: str, url: str) -> Optional[str]:
    result = complete_json(
        f"""
Generate a high-engagement tweet for this B2B software comparison page.
Title: {title}
Vertical: {vertical}
URL: {url}

Rules:
- Open with a punchy hook (question, bold claim, or surprising stat) — NOT "New post:"
- Sound like a practitioner who actually uses these tools
- Max 2 relevant hashtags only (e.g. #SaaS #CRM)
- Under 240 chars so the URL fits

Return JSON: {{"tweet": "<tweet text WITHOUT the URL — URL appended automatically>"}}
""",
        estimated_tokens=350,
        max_output_tokens=220,
    )
    if not result:
        return None
    tweet = result.get("tweet", "").strip()
    if not tweet:
        return None
    full = f"{tweet} {url}"
    return full[:280]


def _post_tweet(text: str, api_key: str, api_secret: str, access_token: str, access_secret: str):
    oauth_timestamp = str(int(time.time()))
    oauth_nonce = sec.token_hex(16)

    oauth_params = {
        "oauth_consumer_key": api_key,
        "oauth_nonce": oauth_nonce,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": oauth_timestamp,
        "oauth_token": access_token,
        "oauth_version": "1.0",
    }

    all_params = {**oauth_params, "status": text}
    sorted_params = dict(sorted(all_params.items()))
    param_str = "&".join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}"
        for k, v in sorted_params.items()
    )
    base_str = "&".join(
        [
            "POST",
            urllib.parse.quote("https://api.twitter.com/1.1/statuses/update.json", safe=""),
            urllib.parse.quote(param_str, safe=""),
        ]
    )
    signing_key = f"{urllib.parse.quote(api_secret, safe='')}&{urllib.parse.quote(access_secret, safe='')}"
    sig = base64.b64encode(
        hmac.new(signing_key.encode(), base_str.encode(), hashlib.sha1).digest()
    ).decode()
    oauth_params["oauth_signature"] = sig

    auth_header = "OAuth " + ", ".join(
        f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
        for k, v in sorted(oauth_params.items())
    )
    resp = httpx.post(
        "https://api.twitter.com/1.1/statuses/update.json",
        data={"status": text},
        headers={"Authorization": auth_header},
        timeout=20,
    )
    resp.raise_for_status()


def send_tweet_email(tweets: list[dict]):
    gmail_user = get("GMAIL_USER", "smithelly30121@gmail.com")
    gmail_password = get("GMAIL_APP_PASSWORD")
    if not gmail_password:
        log.info("GMAIL_APP_PASSWORD not set — skipping tweet email")
        return

    stamp = time.strftime("%B %d, %Y · %H:%M UTC")
    day = time.strftime("%A")
    count = len(tweets)
    cards = ""
    for i, item in enumerate(tweets, 1):
        intent_url = "https://twitter.com/intent/tweet?text=" + urllib.parse.quote(item["text"], safe="")
        cards += f"""
  <tr><td style="padding:0 0 12px 0">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;border:1px solid #e8e8e8;border-radius:12px;overflow:hidden">
      <tr><td style="padding:20px 24px 0 24px">
        <span style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.8px">Tweet {i} of {count}</span>
        <p style="margin:8px 0 16px 0;font-size:15px;line-height:1.65;color:#111827">{item['text']}</p>
      </td></tr>
      <tr><td style="padding:0 24px 20px 24px;border-top:1px solid #f3f4f6">
        <table cellpadding="0" cellspacing="0" style="margin-top:16px">
          <tr><td style="background:#000000;border-radius:100px;padding:11px 24px">
            <a href="{intent_url}" style="color:#ffffff;text-decoration:none;font-size:14px;font-weight:700;letter-spacing:0.2px">Post on X &rarr;</a>
          </td></tr>
        </table>
      </td></tr>
    </table>
  </td></tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SaaSpare Tweet Queue</title>
</head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f9fafb;padding:40px 16px">
<tr><td align="center">
<table width="100%" style="max-width:580px" cellpadding="0" cellspacing="0">

  <!-- Header -->
  <tr><td style="padding-bottom:24px">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#000000;border-radius:14px;padding:28px 32px">
      <tr>
        <td>
          <span style="font-size:13px;font-weight:700;color:#9ca3af;letter-spacing:1px;text-transform:uppercase">SaaSpare</span>
          <h1 style="margin:6px 0 4px 0;font-size:22px;font-weight:800;color:#ffffff;letter-spacing:-0.5px">Your {day} Tweet Queue</h1>
          <p style="margin:0;font-size:13px;color:#6b7280">{stamp}</p>
        </td>
        <td align="right" style="vertical-align:top">
          <span style="background:#1d9bf0;color:#fff;font-size:12px;font-weight:700;padding:5px 12px;border-radius:100px">{count} ready</span>
        </td>
      </tr>
    </table>
  </td></tr>

  <!-- Instruction -->
  <tr><td style="padding:0 4px 20px 4px">
    <p style="margin:0;font-size:14px;color:#6b7280;line-height:1.6">
      Tap <strong style="color:#111827">Post on X</strong> for each tweet below. Twitter opens with the text pre-filled — just hit <strong style="color:#111827">Post</strong>. Done in seconds.
    </p>
  </td></tr>

  <!-- Tweet cards -->
  <table width="100%" cellpadding="0" cellspacing="0">
    {cards}
  </table>

  <!-- Footer -->
  <tr><td style="padding-top:28px;text-align:center;border-top:1px solid #e5e7eb">
    <p style="margin:0;font-size:12px;color:#9ca3af">
      SaaSpare &mdash; B2B SaaS Comparisons &mdash;
      <a href="https://saaspare.org" style="color:#9ca3af">saaspare.org</a>
    </p>
    <p style="margin:4px 0 0 0;font-size:11px;color:#d1d5db">This email is sent 4&times; daily by your automated content bot.</p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Your SaaSpare tweet queue is ready — {time.strftime('%a %d %b')}"
    msg["From"] = f"SaaSpare Bot <{gmail_user}>"
    msg["To"] = "smithelly30121@gmail.com"
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(gmail_user, gmail_password)
            smtp.sendmail(gmail_user, "smithelly30121@gmail.com", msg.as_string())
        log.info("Tweet launchpad email sent to smithelly30121@gmail.com")
    except Exception as e:
        log.warning(f"Tweet email failed: {e}")


def send_reddit_email(items: list[dict]):
    """Email a one-tap Reddit launchpad — replies open thread, new posts autofill via submit URL."""
    gmail_user = get("GMAIL_USER", "smithelly30121@gmail.com")
    gmail_password = get("GMAIL_APP_PASSWORD")
    if not gmail_password or not items:
        return

    stamp = time.strftime("%B %d, %Y · %H:%M UTC")
    day = time.strftime("%A")
    count = len(items)
    cards = ""
    for i, it in enumerate(items, 1):
        subreddit = it.get("subreddit", "saas")
        answer = it["answer"].replace("<", "&lt;").replace(">", "&gt;")

        # If it's a new post (has post_title key), use Reddit submit URL for autofill
        if it.get("post_title"):
            post_title = it["post_title"]
            submit_url = (
                "https://www.reddit.com/r/" + subreddit + "/submit?type=text"
                + "&title=" + urllib.parse.quote(post_title, safe="")
                + "&text=" + urllib.parse.quote(it["answer"], safe="")
            )
            label = f"New Post {i} of {count} &middot; r/{subreddit}"
            btn_label = "Post on Reddit &rarr;"
            btn_url = submit_url
            instruction = "Tap button &rarr; Reddit opens with post pre-filled &rarr; hit <strong>Post</strong>. Done."
            title_line = f'<p style="margin:8px 0 6px 0;font-size:13px;color:#6b7280;font-weight:600">Title: {post_title[:90]}</p>'
        else:
            thread_url = it.get("thread_url", "https://reddit.com")
            label = f"Reply {i} of {count} &middot; r/{subreddit}"
            btn_label = "Open Thread to Reply &rarr;"
            btn_url = thread_url
            instruction = "Copy the reply below, tap button &rarr; paste as comment."
            title_line = f'<p style="margin:8px 0 6px 0;font-size:13px;color:#6b7280;font-weight:600">Thread: {it.get("thread_title","")[:90]}</p>'

        cards += f"""
  <tr><td style="padding:0 0 14px 0">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;border:1px solid #e8e8e8;border-radius:12px;overflow:hidden">
      <tr><td style="padding:20px 24px 0 24px">
        <span style="font-size:11px;font-weight:700;color:#ff4500;text-transform:uppercase;letter-spacing:0.8px">{label}</span>
        {title_line}
        <div style="margin:12px 0 16px 0;font-size:14px;line-height:1.65;color:#111827;background:#f9fafb;border-left:3px solid #ff4500;padding:14px 16px;border-radius:6px;white-space:pre-wrap">{answer}</div>
      </td></tr>
      <tr><td style="padding:0 24px 20px 24px;border-top:1px solid #f3f4f6">
        <table cellpadding="0" cellspacing="0" style="margin-top:16px"><tr>
          <td style="background:#ff4500;border-radius:100px;padding:11px 26px">
            <a href="{btn_url}" style="color:#ffffff;text-decoration:none;font-size:14px;font-weight:700">{btn_label}</a>
          </td>
        </tr></table>
        <p style="margin:12px 0 0 0;font-size:11px;color:#9ca3af">{instruction}</p>
      </td></tr>
    </table>
  </td></tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SaaSpare Reddit Queue</title></head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f9fafb;padding:40px 16px"><tr><td align="center">
<table width="100%" style="max-width:600px" cellpadding="0" cellspacing="0">
  <tr><td style="padding-bottom:24px">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#000000;border-radius:14px;padding:28px 32px"><tr>
      <td>
        <span style="font-size:13px;font-weight:700;color:#9ca3af;letter-spacing:1px;text-transform:uppercase">SaaSpare</span>
        <h1 style="margin:6px 0 4px 0;font-size:22px;font-weight:800;color:#ffffff;letter-spacing:-0.5px">Your {day} Reddit Queue</h1>
        <p style="margin:0;font-size:13px;color:#6b7280">{stamp}</p>
      </td>
      <td align="right" style="vertical-align:top">
        <span style="background:#ff4500;color:#fff;font-size:12px;font-weight:700;padding:5px 12px;border-radius:100px">{count} ready</span>
      </td>
    </tr></table>
  </td></tr>
  <tr><td style="padding:0 4px 20px 4px">
    <p style="margin:0;font-size:14px;color:#6b7280;line-height:1.6">
      Each card has a high-intent Reddit thread + a genuinely helpful reply. <strong style="color:#111827">Copy the grey reply box</strong>, tap <strong style="color:#111827">Open Reddit Thread</strong>, then paste as a comment.
    </p>
  </td></tr>
  <table width="100%" cellpadding="0" cellspacing="0">{cards}</table>
  <tr><td style="padding-top:28px;text-align:center;border-top:1px solid #e5e7eb">
    <p style="margin:0;font-size:12px;color:#9ca3af">SaaSpare &mdash; <a href="https://saaspare.org" style="color:#9ca3af">saaspare.org</a></p>
    <p style="margin:4px 0 0 0;font-size:11px;color:#d1d5db">Sent 4&times; daily. Only post in subreddits where you're an active member to avoid bans.</p>
  </td></tr>
</table>
</td></tr></table>
</body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Your SaaSpare Reddit replies are ready — {time.strftime('%a %d %b')}"
    msg["From"] = f"SaaSpare Bot <{gmail_user}>"
    msg["To"] = "smithelly30121@gmail.com"
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(gmail_user, gmail_password)
            smtp.sendmail(gmail_user, "smithelly30121@gmail.com", msg.as_string())
        log.info(f"Reddit launchpad email sent ({count} items)")
    except Exception as e:
        log.warning(f"Reddit email failed: {e}")


def run_reddit_answers():
    """Post genuine, value-adding answers to high-intent Reddit threads via PRAW."""
    client_id = get("REDDIT_CLIENT_ID")
    client_secret = get("REDDIT_CLIENT_SECRET")
    reddit_username = get("REDDIT_USERNAME")
    reddit_password = get("REDDIT_PASSWORD")
    user_agent = get("REDDIT_USER_AGENT", "saaspare-bot/1.0")

    domain = get("SITE_DOMAIN", "https://yourdomain.com")

    reddit = None
    if all([client_id, client_secret, reddit_username, reddit_password]):
        try:
            import praw
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                username=reddit_username,
                password=reddit_password,
                user_agent=user_agent,
            )
        except Exception as e:
            log.warning(f"PRAW init failed: {e}")

    with db() as conn:
        signals = conn.execute(
            """
            SELECT r.url, r.title, r.body, r.subreddit, s.vertical, s.intent
            FROM scored_signals s
            JOIN raw_signals r ON r.id = s.raw_id
            WHERE r.source IN ('reddit', 'reddit_comment')
              AND s.intent >= 70
              AND s.ts >= ?
            ORDER BY s.profit_score DESC
            LIMIT 3
        """,
            (int(time.time()) - 3600 * 12,),
        ).fetchall()

    site_pages = _select_social_pages(limit=50, fresh_window_seconds=30 * 86400)
    allowed_subreddits = _allowed_subreddits()

    posted_count = 0
    email_items: list[dict] = []
    for signal in signals:
        if posted_count >= 2:
            break
        if _already_posted(signal["url"]):
            continue
        page = _match_page_for_signal(dict(signal), site_pages, domain)
        if not page:
            continue
        answer = _generate_reddit_answer(
            signal["title"],
            signal["body"],
            page["title"],
            _social_url(
                _page_url(page, domain),
                source="reddit",
                campaign="social_reply",
                content=slugify_title(page["title"]),
            ),
        )
        if not answer:
            continue

        email_items.append({
            "subreddit": signal["subreddit"] or "saas",
            "thread_url": signal["url"],
            "thread_title": signal["title"] or "Reddit thread",
            "answer": answer,
        })

        subreddit = (signal["subreddit"] or "").lower()
        autopost_allowed = bool(allowed_subreddits) and subreddit in allowed_subreddits
        if DRY_RUN or not reddit or not autopost_allowed:
            reason = "dry-run" if DRY_RUN else "no-creds" if not reddit else "subreddit-not-allowlisted"
            log.info(f"Reddit staged for r/{signal['subreddit']} ({reason})")
            _store_pending_reddit_post(signal, answer, reason=reason)
            continue

        _store_pending_reddit_post(signal, answer)

        try:
            submission = reddit.submission(url=signal["url"])
            submission.reply(answer)
            _mark_posted(signal["url"])
            posted_count += 1
            log.info(f"Posted Reddit reply to r/{signal['subreddit']}")
            time.sleep(120)
        except Exception as e:
            log.warning(f"Reddit post failed for r/{signal['subreddit']}: {e}")

    # Generate new-post items alongside replies (autofill via Reddit submit URL)
    post_items: list[dict] = []
    post_pages = _select_social_pages(limit=3, fresh_window_seconds=7 * 86400)
    for page in post_pages:
        vertical = page.get("vertical", "saas")
        subreddit_map = {
            "crm": "CRM", "marketing": "marketing", "hr": "humanresources",
            "finance": "financialindependence", "devtools": "devops",
            "project_management": "projectmanagement", "analytics": "analytics",
        }
        sub = subreddit_map.get(vertical, "SaaS")
        page_url = page.get("published_url") or domain
        post_title, post_body = _generate_reddit_new_post(page["title"], vertical, page_url)
        if post_title and post_body:
            post_items.append({
                "subreddit": sub,
                "post_title": post_title,
                "answer": post_body,
            })

    all_items = (email_items + post_items)[:3]

    if all_items:
        send_reddit_email(all_items)

    _write_social_run_report(
        {
            "reddit_candidates": len(signals),
            "reddit_posted": posted_count,
            "reddit_allowlist_size": len(allowed_subreddits),
            "reddit_emailed": len(all_items),
        }
    )


def _generate_reddit_new_post(page_title: str, vertical: str, url: str):
    """Generate a genuine Reddit new-post (title + body) with a soft mention of SaaSpare."""
    prompt = (
        f"Write a Reddit post for the r/SaaS or r/{vertical} community.\n"
        f"Topic: someone asking for advice or sharing a finding about '{page_title}'.\n"
        f"Rules: genuine, helpful, conversational — NOT promotional. 1 sentence max mentioning "
        f"you compared tools at {url}. Post title max 12 words. Body 3-5 sentences.\n"
        f"Return JSON: {{\"title\": \"...\", \"body\": \"...\"}}"
    )
    result = complete_json(prompt)
    if result and "title" in result and "body" in result:
        return result["title"], result["body"]
    return None, None


def _generate_social_copy(title: str, vertical: str, urls: dict[str, str]) -> dict:
    canonical_url = urls["x"]
    result = complete_json(
        f"""
Create concise social copy variations for this B2B SaaS page.
Title: {title}
Vertical: {vertical}
Canonical URL: {canonical_url}

Return JSON:
{{
  "x_post": "<single X post under 260 chars including the URL>",
  "linkedin_post": "<2 short paragraphs for LinkedIn including the URL. No fabricated first-person claims or fake usage/testing>",
  "reddit_angle": "<one-sentence hook for a relevant Reddit comment or post>",
  "reddit_post": "<short Reddit post or comment body that is helpful first, includes the URL naturally, and does not claim personal use unless stated>",
  "instagram_caption": "<short caption with CTA and 3-5 relevant hashtags>",
  "instagram_carousel": ["<slide 1 hook>", "<slide 2 takeaway>", "<slide 3 takeaway>", "<slide 4 CTA>"],
  "tiktok_script": "<20-30 second spoken script with a hook and CTA>",
  "tiktok_shot_list": ["<shot 1 visual>", "<shot 2 visual>", "<shot 3 visual>"]
}}
"""
    )
    if result:
        return {
            "x_post": _ensure_url(result.get("x_post", ""), urls["x"]),
            "linkedin_post": _ensure_url(result.get("linkedin_post", ""), urls["linkedin"]),
            "reddit_angle": result.get("reddit_angle", "") or f"Useful breakdown for anyone comparing {title}: {urls['reddit']}",
            "reddit_post": _ensure_url(result.get("reddit_post", ""), urls["reddit"])
            if result.get("reddit_post")
            else _fallback_reddit_post(title, vertical, urls["reddit"]),
            "instagram_caption": _ensure_url(result.get("instagram_caption", ""), urls["instagram"]),
            "instagram_carousel": _ensure_list(
                result.get("instagram_carousel"),
                _fallback_instagram_carousel(title, urls["instagram"]),
            ),
            "tiktok_script": result.get("tiktok_script", "") or _fallback_tiktok_script(title, urls["tiktok"]),
            "tiktok_shot_list": _ensure_list(
                result.get("tiktok_shot_list"),
                _fallback_tiktok_shot_list(title),
            ),
        }
    return {
        "x_post": f"{title} is live. Quick breakdown, real pricing, and the best fit by use case: {urls['x']}",
        "linkedin_post": (
            f"{title} is now live on SaaSpare.\n\n"
            f"If you're comparing options in {vertical.replace('_', ' ')}, this gives you the pricing, "
            f"tradeoffs, and best-fit summary without the fluff.\n\n{urls['linkedin']}"
        ),
        "reddit_angle": f"If anyone here is evaluating {title}, this breakdown covers pricing and tradeoffs in one place: {urls['reddit']}",
        "reddit_post": _fallback_reddit_post(title, vertical, urls["reddit"]),
        "instagram_caption": f"New SaaS breakdown: {title}. Pricing, pros, cons, and the best fit in one place. {urls['instagram']} #saas #software #b2b #startups",
        "instagram_carousel": _fallback_instagram_carousel(title, urls["instagram"]),
        "tiktok_script": _fallback_tiktok_script(title, urls["tiktok"]),
        "tiktok_shot_list": _fallback_tiktok_shot_list(title),
    }


def _fallback_tiktok_script(title: str, url: str) -> str:
    return (
        "Hook: If you're comparing tools right now, don't buy before reading this.\n"
        f"Body: We just published {title} with pricing, pros, cons, and who each option is actually for.\n"
        f"CTA: Check the full breakdown at {url}"
    )


def _fallback_tiktok_shot_list(title: str) -> list[str]:
    return [
        f"Hook frame: big on-screen text with '{title}'",
        "Screen capture: pricing table or top comparison bullets",
        "Voiceover: who each tool is actually for",
        "CTA frame: point viewers to the full breakdown",
    ]


def _fallback_instagram_carousel(title: str, url: str) -> list[str]:
    return [
        f"{title}: the fast buyer summary",
        "What you pay: the real pricing tiers and where costs jump",
        "Best fit: who should buy, and who should skip it",
        f"Read the full breakdown at {url}",
    ]


def _fallback_reddit_post(title: str, vertical: str, url: str) -> str:
    return (
        f"If you're comparing options in {vertical.replace('_', ' ')}, the main thing I would watch "
        "is where pricing and onboarding complexity start to climb. "
        f"I pulled the tradeoffs together here so you can skim it faster: {url}"
    )


def _ensure_list(value, fallback: list[str], limit: int = 5) -> list[str]:
    if isinstance(value, list):
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        if cleaned:
            return cleaned[:limit]
    return fallback[:limit]


def _ensure_url(text: str, url: str) -> str:
    text = (text or "").strip()
    if not text:
        return url
    return text if url in text else f"{text} {url}"


def _build_social_calendar(payload: list[dict]) -> list[dict]:
    slots = [
        ("Monday", "X + LinkedIn", "Publish the strongest link-first launch post"),
        ("Tuesday", "Reddit", "Use the long-form Reddit version only where the thread intent fits"),
        ("Wednesday", "Instagram", "Turn the page into a 4-slide carousel"),
        ("Thursday", "TikTok", "Record the short script with 3-4 fast cuts"),
        ("Friday", "X repost", "Repackage the strongest point as a fresh hook"),
    ]
    calendar: list[dict] = []
    for idx, item in enumerate(payload):
        day, channel, instruction = slots[idx % len(slots)]
        calendar.append(
            {
                "day": day,
                "channel": channel,
                "title": item["title"],
                "url": item["url"],
                "instruction": instruction,
            }
        )
    return calendar


def _render_social_pack_markdown(payload: list[dict]) -> str:
    lines = ["# Weekly Social Pack", ""]
    for item in payload:
        lines.extend(
            [
                f"## {item['title']}",
                f"URL: {item['url']}",
                "",
                "### X",
                item["x_post"],
                "",
                "### LinkedIn",
                item["linkedin_post"],
                "",
                "### Reddit Angle",
                item["reddit_angle"],
                "",
                "### Reddit Post",
                item.get("reddit_post", ""),
                "",
                "### Instagram",
                item["instagram_caption"],
                "",
                "### Instagram Carousel",
                *[f"- {slide}" for slide in item.get("instagram_carousel", [])],
                "",
                "### TikTok Script",
                item["tiktok_script"],
                "",
                "### TikTok Shot List",
                *[f"- {shot}" for shot in item.get("tiktok_shot_list", [])],
                "",
            ]
        )
    return "\n".join(lines)


def _render_social_calendar_markdown(calendar: list[dict]) -> str:
    lines = ["# Weekly Social Calendar", ""]
    for item in calendar:
        lines.extend(
            [
                f"## {item['day']} - {item['channel']}",
                f"Page: {item['title']}",
                f"URL: {item['url']}",
                item["instruction"],
                "",
            ]
        )
    return "\n".join(lines)


def slugify_title(title: str) -> str:
    from slugify import slugify

    return slugify(title)


def _generate_reddit_answer(question: str, context: str, page_title: str, page_url: str) -> Optional[str]:
    result = complete_json(
        f"""
Write a helpful Reddit reply to this question. Sound genuine, give real value, then naturally mention the resource.

Question: {question}
Context: {context[:300]}
Resource to mention: {page_title} at {page_url}

Return JSON: {{"reply": "<2-4 paragraphs, genuinely helpful, not spammy, mentions the link naturally at end>"}}
""",
        estimated_tokens=900,
        max_output_tokens=700,
    )
    return result.get("reply") if result else None


def _store_pending_reddit_post(signal, answer: str, reason: str = ""):
    pending_dir = Path("data/pending_reddit")
    pending_dir.mkdir(parents=True, exist_ok=True)
    fname = pending_dir / f"{int(time.time())}_{signal['subreddit']}.txt"
    fname.write_text(
        f"URL: {signal['url']}\nSubreddit: r/{signal['subreddit']}\nReason: {reason or 'pending'}\n\n{answer}",
        encoding="utf-8",
    )


def _write_social_queue(pages, domain: str):
    if not pages:
        return

    SOCIAL_QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SOCIAL_QUEUE_DIR / f"social_queue_{time.strftime('%Y-%m-%d')}.md"
    lines = ["# Weekly Social Queue", ""]
    for page in pages:
        url = _social_url(
            _page_url(page, domain),
            source="x",
            campaign="social_queue",
            content=slugify_title(page["title"]),
        )
        title = page["title"]
        vertical = page["vertical"] or "saas"
        lines.extend(
            [
                f"## {title}",
                f"URL: {url}",
                f"Vertical: {vertical}",
                "",
                "X",
                f"- New on SaaSpare: {title}. Quick breakdown, pricing context, and the best-fit recommendation in one place. {url}",
                "",
                "LinkedIn",
                f"- We just published {title} on SaaSpare.\n- Includes the buyer context, pricing angle, and who each tool is best for.\n- Useful if you're shortlisting vendors this week.\n- {url}",
                "",
                "Reddit angle",
                f"- Use this when someone asks for a {vertical} recommendation.\n- Lead with practical tradeoffs, then drop the link only if it fits the thread.\n- Reference: {url}",
                "",
                "Short-form hook",
                f"- Hook: '{title} in 30 seconds: who should actually buy it?'",
                f"- CTA: 'Read the full breakdown at {url}'",
                "- Repurpose: turn the key takeaway into a 4-slide Instagram carousel",
                "",
            ]
        )
    out_path.write_text("\n".join(lines), encoding="utf-8")
    log.info(f"Social queue written: {out_path}")


def run_linkedin():
    """Post to LinkedIn via API. Requires LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN."""
    access_token = get("LINKEDIN_ACCESS_TOKEN")
    person_urn = _normalize_linkedin_person_urn(get("LINKEDIN_PERSON_URN"))

    if not access_token or not person_urn:
        log.info("LinkedIn credentials not set — skipping auto-post")
        return

    domain = get("SITE_DOMAIN", "https://yourdomain.com")

    pages = _select_social_pages(limit=3, fresh_window_seconds=86400)

    posted = 0
    for page in pages:
        url = _social_url(
            _page_url(page, domain),
            source="linkedin",
            campaign="social_launch",
            content=slugify_title(page["title"]),
        )
        if _already_posted(f"li:{url}"):
            continue

        post_text = _generate_linkedin_post(page["title"], page["vertical"], url)
        if not post_text:
            continue

        if DRY_RUN:
            log.info(f"[DRY RUN] LinkedIn: {post_text[:80]}...")
            continue

        try:
            _post_linkedin(post_text, access_token, person_urn)
            _mark_posted(f"li:{url}")
            posted += 1
            log.info(f"LinkedIn posted: {page['title'][:60]}")
            time.sleep(30)
        except Exception as e:
            log.warning(f"LinkedIn post failed: {e}")

    log.info(f"LinkedIn: {posted} posts published")
    _write_social_run_report({"linkedin_candidates": len(pages), "linkedin_posted": posted})


def _generate_linkedin_post(title: str, vertical: str, url: str) -> Optional[str]:
    result = complete_json(
        f"""
Write a LinkedIn post for a B2B SaaS comparison page. Sound like a knowledgeable analyst, not a marketer.
Lead with a sharp insight or counterintuitive point about this software category, then share the resource.

Title: {title}
Vertical: {vertical}
URL: {url}

Return JSON: {{
  "post": "<3-5 short paragraphs. Hook first. No generic openers like 'Excited to share'. No fabricated first-person usage claims. End with URL naturally.>"
}}
""",
        estimated_tokens=500,
        max_output_tokens=400,
    )
    if not result:
        return None
    post = result.get("post", "").strip()
    if not post:
        return None
    if url not in post:
        post = f"{post}\n\n{url}"
    return post[:2900]


def _post_linkedin(text: str, access_token: str, person_urn: str):
    payload = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    resp = httpx.post(
        "https://api.linkedin.com/v2/ugcPosts",
        json=payload,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        timeout=20,
    )
    resp.raise_for_status()
