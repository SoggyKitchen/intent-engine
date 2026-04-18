import time
from typing import Iterator

import httpx

from adapters.base import BaseAdapter
from core.logger import log
from core.models import RawSignal

SUBREDDITS = [
    "entrepreneur", "startups", "SaaS", "webdev", "devops", "aws",
    "CloudComputing", "marketing", "smallbusiness", "SideProject",
    "indiehackers", "MachineLearning", "artificial", "datascience",
    "cybersecurity", "netsec", "devtools", "programming",
]

HEADERS = {"User-Agent": "IntentEngine/1.0 (signal harvester; contact: bot@intentengine.local)"}


class RedditAdapter(BaseAdapter):
    name = "reddit"

    def fetch(self, since_ts: int) -> Iterator[RawSignal]:
        with httpx.Client(headers=HEADERS, timeout=20, follow_redirects=True) as client:
            for sub_name in SUBREDDITS:
                try:
                    resp = client.get(f"https://www.reddit.com/r/{sub_name}/new.json?limit=75")
                    if resp.status_code != 200:
                        log.warning(f"Reddit r/{sub_name} returned {resp.status_code}")
                        time.sleep(2)
                        continue
                    posts = resp.json().get("data", {}).get("children", [])
                    for child in posts:
                        p = child.get("data", {})
                        if p.get("created_utc", 0) < since_ts:
                            continue
                        if p.get("score", 0) < 3:
                            continue
                        title = (p.get("title") or "")[:500]
                        body = (p.get("selftext") or "")[:2000]
                        permalink = p.get("permalink", "")
                        yield RawSignal(
                            source="reddit",
                            url=f"https://reddit.com{permalink}",
                            title=title,
                            body=body,
                            author=p.get("author", ""),
                            subreddit=sub_name,
                            score=p.get("score", 0),
                            ts=int(p.get("created_utc", 0)),
                        )
                        if p.get("num_comments", 0) > 10:
                            time.sleep(1)
                            comments_resp = client.get(
                                f"https://www.reddit.com{permalink}.json?limit=5"
                            )
                            if comments_resp.status_code == 200:
                                try:
                                    listing = comments_resp.json()
                                    comments = listing[1]["data"]["children"] if len(listing) > 1 else []
                                    for cc in comments[:5]:
                                        c = cc.get("data", {})
                                        cbody = (c.get("body") or "")
                                        if len(cbody) < 80:
                                            continue
                                        yield RawSignal(
                                            source="reddit_comment",
                                            url=f"https://reddit.com{permalink}",
                                            title=title[:200],
                                            body=cbody[:2000],
                                            author=c.get("author", ""),
                                            subreddit=sub_name,
                                            score=c.get("score", 0),
                                            ts=int(c.get("created_utc", 0)),
                                        )
                                except Exception:
                                    pass
                    time.sleep(1)
                except Exception as e:
                    log.warning(f"Reddit unexpected error on r/{sub_name}: {e}")
                    continue
