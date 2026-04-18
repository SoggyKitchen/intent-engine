"""
Social media auto-poster.
- Twitter/X: v2 API free tier (1500 tweets/mo). Posts comparison page summaries.
- Reddit: Posts genuine value-add answers in relevant subs when high-intent questions detected.

Both drive FREE traffic to your SEO pages.
"""
import hashlib
import time
from pathlib import Path
from typing import Optional

import httpx

from core.db import db
from core.logger import log
from core.secrets import get, DRY_RUN
from llm.router import complete_json

POSTED_FILE = Path("data/social_posted.txt")


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

    if not all([api_key, api_secret, access_token, access_secret]):
        log.info("Twitter credentials not set — skipping Twitter posting")
        return

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


def _generate_tweet(title: str, vertical: str, url: str) -> Optional[str]:
    result = complete_json(f"""
Generate a concise, engaging tweet for this B2B software comparison page.
Title: {title}
Vertical: {vertical}
URL: {url}

Return JSON: {{"tweet": "<under 240 chars, no hashtag spam, sounds like a real person sharing a useful resource>"}}
""")
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


def _generate_reddit_answer(question: str, context: str,
                              page_title: str, page_url: str) -> Optional[str]:
    result = complete_json(f"""
Write a helpful Reddit reply to this question. Sound genuine, give real value, then naturally mention the resource.

Question: {question}
Context: {context[:300]}
Resource to mention: {page_title} at {page_url}

Return JSON: {{"reply": "<2-4 paragraphs, genuinely helpful, not spammy, mentions the link naturally at end>"}}
""")
    return result.get("reply") if result else None


def _store_pending_reddit_post(signal, answer: str):
    pending_dir = Path("data/pending_reddit")
    pending_dir.mkdir(parents=True, exist_ok=True)
    fname = pending_dir / f"{int(time.time())}_{signal['subreddit']}.txt"
    fname.write_text(
        f"URL: {signal['url']}\nSubreddit: r/{signal['subreddit']}\n\n{answer}",
        encoding="utf-8"
    )
