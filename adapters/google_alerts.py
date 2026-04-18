"""
Google Alerts RSS adapter. Each alert you create at google.com/alerts
produces a free RSS feed URL. This adapter polls all of them.

HOW TO SET UP (one-time, 5 min):
1. Go to google.com/alerts
2. Create an alert for each of these queries (one per vertical):
   - "looking for devops tool" site:reddit.com OR site:news.ycombinator.com
   - "alternative to jira" OR "jira replacement"
   - "best crm for startups" recommendation
   - ... etc. (add as many as you want, up to ~1000 free)
3. Set: How often = As-it-happens, Deliver to = RSS Feed
4. Copy the RSS URL (looks like feeds.feedburner.com/... or google.com/alerts/feeds/...)
5. Add to GOOGLE_ALERT_FEEDS in your .env as comma-separated URLs

This is FREE and pulls FRESH signals that are barely 1 hour old.
"""
import os
import time
from typing import Iterator

import feedparser

from adapters.base import BaseAdapter
from core.logger import log
from core.models import RawSignal
from core.secrets import get

SEED_QUERIES = [
    "looking for alternative {vertical} software",
    "best {vertical} tool for startup",
    "recommend {vertical} platform",
    "switching from {vertical} tool",
    "tired of {vertical} software pricing",
]

VERTICALS = [
    "devops", "crm", "analytics", "marketing automation",
    "cloud hosting", "cybersecurity", "hr software", "ecommerce",
    "ai tools", "developer tools",
]


class GoogleAlertsAdapter(BaseAdapter):
    name = "google_alerts"

    def fetch(self, since_ts: int) -> Iterator[RawSignal]:
        env_feeds = get("GOOGLE_ALERT_FEEDS", "")
        feed_urls = [u.strip() for u in env_feeds.split(",") if u.strip()]

        if not feed_urls:
            log.debug("No GOOGLE_ALERT_FEEDS configured — skipping Google Alerts adapter")
            return

        for feed_url in feed_urls:
            try:
                d = feedparser.parse(feed_url)
                for entry in d.entries:
                    ts = _entry_ts(entry)
                    if ts < since_ts:
                        continue
                    title = getattr(entry, "title", "") or ""
                    body = ""
                    if hasattr(entry, "summary"):
                        body = entry.summary or ""
                    body = _strip_html(body)[:2000]
                    url = getattr(entry, "link", feed_url)
                    if not title:
                        continue
                    yield RawSignal(
                        source="google_alerts",
                        url=url,
                        title=title[:500],
                        body=body,
                        author="",
                        ts=ts,
                    )
            except Exception as e:
                log.warning(f"Google Alerts feed error ({feed_url[:60]}...): {e}")
                continue


def _entry_ts(entry) -> int:
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            return int(time.mktime(t))
    return int(time.time())


def _strip_html(text: str) -> str:
    import re
    return re.sub(r"<[^>]+>", " ", text).strip()
