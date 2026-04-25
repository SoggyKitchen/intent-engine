"""
Social media auto-poster.
- Twitter/X: v2 API free tier (1500 tweets/mo). Posts comparison page summaries.
- Reddit: Posts genuine value-add answers in relevant subs when high-intent questions detected.

Both drive FREE traffic to your SEO pages.
"""
import hashlib
import json
import time
from pathlib import Path
from typing import Optional

import httpx

from core.db import db
from core.logger import log
from core.secrets import get, DRY_RUN
from llm.router import complete_json

POSTED_FILE = Path("data/social_posted.txt")
SOCIAL_QUEUE_DIR = Path("outputs/generated")
SOCIAL_PACK_DIR = Path("outputs/generated/social")


def _already_posted(url: str) -> bool:
    POSTED_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not POSTED_FILE.exists():
        return False
    uid = hashlib.sha256(url.encode()).hexdigest()[:12]
    return uid in POSTED_FILE.read_text()


def _mark_posted(url: str):
    uid = hashlib.sha256(url.encode()).hexdigest()[:12]
    with open(POSTED_FILE, "a") as f:
        f.write(uid + "\n")


def run_twitter():
    bearer = get("TWITTER_BEARER_TOKEN")
    api_key = get("TWITTER_API_KEY")
    api_secret = get("TWITTER_API_SECRET")
    access_token = get("TWITTER_ACCESS_TOKEN")
    access_secret = get("TWITTER_ACCESS_TOKEN_SECRET")

    domain = get("SITE_DOMAIN", "https://yourdomain.com")

    with db() as conn:
        pages = conn.execute("""
            SELECT title, published_url, vertical, created_at
            FROM outputs
            WHERE type = 'seo_page'
              AND published_url IS NOT NULL
              AND created_at >= ?
            ORDER BY created_at DESC
            LIMIT 5
        """, (int(time.time()) - 86400,)).fetchall()

    _write_social_queue(pages, domain)

    if not all([api_key, api_secret, access_token, access_secret]):
        log.info("Twitter credentials not set — generated social queue only")
        return

    for page in pages:
        url = page["published_url"] or f"{domain}/{page['title']}"
        if _already_posted(url):
            continue

        tweet_text = _generate_tweet(page["title"], page["vertical"], url)
        if not tweet_text:
            continue

        if DRY_RUN:
            log.info(f"[DRY RUN] Would tweet: {tweet_text[:80]}...")
            _mark_posted(url)
            continue

        try:
            _post_tweet(tweet_text, api_key, api_secret, access_token, access_secret)
            _mark_posted(url)
            log.info(f"Tweeted: {tweet_text[:60]}...")
            time.sleep(60)
        except Exception as e:
            log.warning(f"Tweet failed: {e}")


def build_social_pack(limit: int = 5) -> Optional[str]:
    domain = get("SITE_DOMAIN", "https://yourdomain.com")
    SOCIAL_PACK_DIR.mkdir(parents=True, exist_ok=True)

    with db() as conn:
        pages = conn.execute("""
            SELECT title, COALESCE(published_url, '') AS published_url, vertical, created_at
            FROM outputs
            WHERE type = 'seo_page'
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

    if not pages:
        log.info("No SEO pages available for social pack generation")
        return None

    payload: list[dict] = []
    for page in pages:
        url = page["published_url"] or f"{domain}/pages/{slugify_title(page['title'])}.html"
        copy = _generate_social_copy(page["title"], page["vertical"], url)
        payload.append({
            "title": page["title"],
            "vertical": page["vertical"],
            "url": url,
            **copy,
        })

    stamp = time.strftime("%Y-%m-%d")
    json_path = SOCIAL_PACK_DIR / f"social_pack_{stamp}.json"
    md_path = SOCIAL_PACK_DIR / f"social_pack_{stamp}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_render_social_pack_markdown(payload), encoding="utf-8")
    log.info(f"Social pack generated: {json_path}")
    return str(json_path)


def _generate_tweet(title: str, vertical: str, url: str) -> Optional[str]:
    result = complete_json(f"""
Generate a concise, engaging tweet for this B2B software comparison page.
Title: {title}
Vertical: {vertical}
URL: {url}

Return JSON: {{"tweet": "<under 240 chars, no hashtag spam, sounds like a real person sharing a useful resource>"}}
""", estimated_tokens=350, max_output_tokens=220)
    if not result:
        return None
    tweet = result.get("tweet", "")
    if not tweet:
        return None
    if url not in tweet:
        tweet = f"{tweet} {url}"
    return tweet[:280]


def _post_tweet(text: str, api_key: str, api_secret: str,
                access_token: str, access_secret: str):
    import hmac
    import hashlib
    import base64
    import urllib.parse
    import secrets as sec

    oauth_timestamp = str(int(time.time()))
    oauth_nonce = sec.token_hex(16)

    params = {
        "oauth_consumer_key": api_key,
        "oauth_nonce": oauth_nonce,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": oauth_timestamp,
        "oauth_token": access_token,
        "oauth_version": "1.0",
    }

    base_params = dict(sorted(params.items()))
    param_str = "&".join(f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}"
                         for k, v in base_params.items())
    base_str = "&".join([
        "POST",
        urllib.parse.quote("https://api.twitter.com/2/tweets", safe=""),
        urllib.parse.quote(param_str, safe=""),
    ])
    signing_key = f"{urllib.parse.quote(api_secret, safe='')}&{urllib.parse.quote(access_secret, safe='')}"
    sig = base64.b64encode(
        hmac.new(signing_key.encode(), base_str.encode(), hashlib.sha1).digest()
    ).decode()
    params["oauth_signature"] = sig

    auth_header = "OAuth " + ", ".join(
        f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
        for k, v in sorted(params.items())
    )
    resp = httpx.post(
        "https://api.twitter.com/2/tweets",
        json={"text": text},
        headers={"Authorization": auth_header, "Content-Type": "application/json"},
        timeout=20,
    )
    resp.raise_for_status()


def run_reddit_answers():
    """Post genuine, value-adding answers to high-intent Reddit threads."""
    reddit_key = get("REDDIT_CLIENT_ID")
    if not reddit_key:
        return

    domain = get("SITE_DOMAIN", "https://yourdomain.com")

    with db() as conn:
        signals = conn.execute("""
            SELECT r.url, r.title, r.body, r.subreddit, s.vertical, s.intent
            FROM scored_signals s
            JOIN raw_signals r ON r.id = s.raw_id
            WHERE r.source IN ('reddit', 'reddit_comment')
              AND s.intent >= 70
              AND s.ts >= ?
            ORDER BY s.profit_score DESC
            LIMIT 10
        """, (int(time.time()) - 3600 * 12,)).fetchall()

        site_pages = conn.execute("""
            SELECT title, published_url, vertical
            FROM outputs
            WHERE type = 'seo_page'
        """).fetchall()

    page_index = {p["vertical"]: p for p in site_pages}

    for signal in signals:
        if _already_posted(signal["url"]):
            continue
        vertical = signal["vertical"]
        if vertical not in page_index:
            continue

        page = page_index[vertical]
        answer = _generate_reddit_answer(
            signal["title"], signal["body"],
            page["title"], page["published_url"] or domain
        )
        if not answer:
            continue

        if DRY_RUN:
            log.info(f"[DRY RUN] Reddit answer for r/{signal['subreddit']}: {answer[:80]}...")
            _mark_posted(signal["url"])
            continue

        log.info(f"Reddit answer ready for r/{signal['subreddit']} — post manually or via PRAW")
        _store_pending_reddit_post(signal, answer)
        _mark_posted(signal["url"])


def _generate_social_copy(title: str, vertical: str, url: str) -> dict:
    result = complete_json(f"""
Create concise social copy variations for this B2B SaaS page.
Title: {title}
Vertical: {vertical}
URL: {url}

Return JSON:
{{
  "x_post": "<single X post under 260 chars including the URL>",
  "linkedin_post": "<2 short paragraphs for LinkedIn including the URL>",
  "reddit_angle": "<one-sentence hook for a relevant Reddit comment or post>",
  "instagram_caption": "<short caption with CTA and 3-5 relevant hashtags>",
  "tiktok_script": "<20-30 second spoken script with a hook and CTA>"
}}
""")
    if result:
        return {
            "x_post": _ensure_url(result.get("x_post", ""), url),
            "linkedin_post": _ensure_url(result.get("linkedin_post", ""), url),
            "reddit_angle": result.get("reddit_angle", "") or f"Useful breakdown for anyone comparing {title}: {url}",
            "instagram_caption": _ensure_url(result.get("instagram_caption", ""), url),
            "tiktok_script": result.get("tiktok_script", "") or _fallback_tiktok_script(title, url),
        }
    return {
        "x_post": f"{title} is live. Quick breakdown, real pricing, and the best fit by use case: {url}",
        "linkedin_post": f"{title} is now live on SaaSpare.\n\nIf you're comparing options in {vertical.replace('_', ' ')}, this gives you the pricing, tradeoffs, and best-fit summary without the fluff.\n\n{url}",
        "reddit_angle": f"If anyone here is evaluating {title}, this breakdown covers pricing and tradeoffs in one place: {url}",
        "instagram_caption": f"New SaaS breakdown: {title}. Pricing, pros, cons, and the best fit in one place. {url} #saas #software #b2b #startups",
        "tiktok_script": _fallback_tiktok_script(title, url),
    }


def _fallback_tiktok_script(title: str, url: str) -> str:
    return (
        f"Hook: If you're comparing tools right now, don't buy before reading this.\n"
        f"Body: We just published {title} with pricing, pros, cons, and who each option is actually for.\n"
        f"CTA: Check the full breakdown at {url}"
    )


def _ensure_url(text: str, url: str) -> str:
    text = (text or "").strip()
    if not text:
        return url
    return text if url in text else f"{text} {url}"


def _render_social_pack_markdown(payload: list[dict]) -> str:
    lines = ["# Weekly Social Pack", ""]
    for item in payload:
        lines.extend([
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
            "### Instagram",
            item["instagram_caption"],
            "",
            "### TikTok Script",
            item["tiktok_script"],
            "",
        ])
    return "\n".join(lines)


def slugify_title(title: str) -> str:
    from slugify import slugify
    return slugify(title)


def _generate_reddit_answer(question: str, context: str,
                              page_title: str, page_url: str) -> Optional[str]:
    result = complete_json(f"""
Write a helpful Reddit reply to this question. Sound genuine, give real value, then naturally mention the resource.

Question: {question}
Context: {context[:300]}
Resource to mention: {page_title} at {page_url}

Return JSON: {{"reply": "<2-4 paragraphs, genuinely helpful, not spammy, mentions the link naturally at end>"}}
""", estimated_tokens=900, max_output_tokens=700)
    return result.get("reply") if result else None


def _store_pending_reddit_post(signal, answer: str):
    pending_dir = Path("data/pending_reddit")
    pending_dir.mkdir(parents=True, exist_ok=True)
    fname = pending_dir / f"{int(time.time())}_{signal['subreddit']}.txt"
    fname.write_text(
        f"URL: {signal['url']}\nSubreddit: r/{signal['subreddit']}\n\n{answer}",
        encoding="utf-8"
    )


def _write_social_queue(pages, domain: str):
    if not pages:
        return

    SOCIAL_QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SOCIAL_QUEUE_DIR / f"social_queue_{time.strftime('%Y-%m-%d')}.md"
    lines = ["# Weekly Social Queue", ""]
    for page in pages:
        url = page["published_url"] or domain
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
                "",
            ]
        )
    out_path.write_text("\n".join(lines), encoding="utf-8")
    log.info(f"Social queue written: {out_path}")
