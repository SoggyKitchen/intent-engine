import time
from typing import Iterator

from adapters.base import BaseAdapter
from core.http import get
from core.logger import log
from core.models import RawSignal

HN_ALGOLIA = "https://hn.algolia.com/api/v1/search"

QUERIES = [
    "looking for",
    "recommend",
    "alternative to",
    "switching from",
    "best tool for",
    "anyone use",
    "what do you use for",
    "tired of",
    "need a solution",
    "advice on",
]

TAGS = ["ask_hn", "story", "comment"]


class HNAdapter(BaseAdapter):
    name = "hackernews"

    def fetch(self, since_ts: int) -> Iterator[RawSignal]:
        seen = set()
        for query in QUERIES:
            try:
                resp = get(HN_ALGOLIA, params={
                    "query": query,
                    "tags": "ask_hn,story",
                    "numericFilters": f"created_at_i>{since_ts}",
                    "hitsPerPage": 50,
                }, skip_robots=True)
                for hit in resp.json().get("hits", []):
                    url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit['objectID']}"
                    sig_id = hit["objectID"]
                    if sig_id in seen:
                        continue
                    seen.add(sig_id)
                    title = hit.get("title") or hit.get("story_title", "")
                    body = hit.get("story_text") or hit.get("comment_text") or ""
                    if not title and not body:
                        continue
                    yield RawSignal(
                        source="hackernews",
                        url=url,
                        title=title[:500],
                        body=body[:2000],
                        author=hit.get("author", ""),
                        ts=hit.get("created_at_i", int(time.time())),
                    )
            except Exception as e:
                log.warning(f"HN adapter error for query '{query}': {e}")
                continue
