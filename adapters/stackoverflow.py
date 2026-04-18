import time
from typing import Iterator

from adapters.base import BaseAdapter
from core.http import get
from core.logger import log
from core.models import RawSignal
from core.secrets import get as get_secret

SO_API = "https://api.stackexchange.com/2.3/questions"

TAGS = [
    "software-recommendations",
    "tools",
    "devops-tools",
    "machine-learning-tools",
    "cloud",
]


class StackOverflowAdapter(BaseAdapter):
    name = "stackoverflow"

    def fetch(self, since_ts: int) -> Iterator[RawSignal]:
        key = get_secret("STACKEXCHANGE_KEY")
        for tag in TAGS:
            try:
                params = {
                    "site": "stackoverflow",
                    "tagged": tag,
                    "fromdate": since_ts,
                    "sort": "votes",
                    "order": "desc",
                    "pagesize": 50,
                    "filter": "withbody",
                }
                if key:
                    params["key"] = key
                resp = get(SO_API, params=params, skip_robots=True)
                data = resp.json()
                for item in data.get("items", []):
                    if item.get("score", 0) < 2:
                        continue
                    body = item.get("body", "")[:2000]
                    yield RawSignal(
                        source="stackoverflow",
                        url=item["link"],
                        title=item["title"][:500],
                        body=body,
                        author=item.get("owner", {}).get("display_name", ""),
                        score=item.get("score", 0),
                        ts=item["creation_date"],
                    )
                if data.get("backoff"):
                    time.sleep(data["backoff"])
            except Exception as e:
                log.warning(f"StackOverflow adapter error on tag '{tag}': {e}")
                continue
