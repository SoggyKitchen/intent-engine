import time
from email.utils import parsedate_to_datetime
from typing import Iterator

import feedparser

from adapters.base import BaseAdapter
from core.logger import log
from core.models import RawSignal

FEEDS = [
    ("https://www.producthunt.com/feed", "producthunt"),
    ("https://techcrunch.com/category/startups/feed/", "techcrunch"),
    ("https://news.ycombinator.com/rss", "hackernews_rss"),
    ("https://venturebeat.com/category/ai/feed/", "venturebeat"),
    ("https://feeds.feedburner.com/ASmartBearBlog", "smartbear"),
    ("https://www.indiehackers.com/feed.rss", "indiehackers"),
]


def _entry_ts(entry) -> int:
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            return int(time.mktime(t))
    return int(time.time())


class RSSAdapter(BaseAdapter):
    name = "rss"

    def fetch(self, since_ts: int) -> Iterator[RawSignal]:
        for feed_url, source_name in FEEDS:
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
                    elif hasattr(entry, "content"):
                        body = entry.content[0].value if entry.content else ""
                    body = body[:2000]
                    url = getattr(entry, "link", feed_url)
                    yield RawSignal(
                        source=source_name,
                        url=url,
                        title=title[:500],
                        body=body,
                        author=getattr(entry, "author", ""),
                        ts=ts,
                    )
            except Exception as e:
                log.warning(f"RSS adapter error on {source_name}: {e}")
                continue
