import time
from typing import Iterator

from adapters.base import BaseAdapter
from core.http import get
from core.logger import log
from core.models import RawSignal
from core.secrets import get as get_secret

GH_API = "https://api.github.com/search/issues"

QUERIES = [
    "looking for alternative",
    "recommendation for",
    "best tool for",
    "what do you use",
    "switching from",
    "feature request comparison",
]


class GithubAdapter(BaseAdapter):
    name = "github"

    def fetch(self, since_ts: int) -> Iterator[RawSignal]:
        token = get_secret("GITHUB_TOKEN")
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        from datetime import datetime, timezone
        since_dt = datetime.fromtimestamp(since_ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        seen = set()
        for query in QUERIES:
            try:
                resp = get(GH_API, params={
                    "q": f"{query} is:issue created:>{since_dt}",
                    "sort": "reactions",
                    "order": "desc",
                    "per_page": 30,
                }, headers=headers, skip_robots=True)
                for item in resp.json().get("items", []):
                    if item["id"] in seen:
                        continue
                    seen.add(item["id"])
                    body = (item.get("body") or "")[:2000]
                    if len(body) < 50:
                        continue
                    ts = int(time.mktime(
                        time.strptime(item["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                    ))
                    yield RawSignal(
                        source="github",
                        url=item["html_url"],
                        title=item["title"][:500],
                        body=body,
                        author=item.get("user", {}).get("login", ""),
                        score=item.get("reactions", {}).get("total_count", 0),
                        ts=ts,
                    )
            except Exception as e:
                log.warning(f"GitHub adapter error for '{query}': {e}")
                continue
