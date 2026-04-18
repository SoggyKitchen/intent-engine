import time
import urllib.robotparser
from collections import defaultdict
from threading import Lock
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from core.logger import log

_rate_locks: dict[str, tuple[float, Lock]] = defaultdict(lambda: (0.0, Lock()))
_robot_cache: dict[str, urllib.robotparser.RobotFileParser] = {}

UA = "IntentEngine/1.0 (+https://github.com/you/intent-engine; contact: your@email.com)"

MIN_DELAY = {
    "reddit.com": 2.0,
    "api.reddit.com": 2.0,
    "hn.algolia.com": 0.5,
    "api.github.com": 1.0,
    "api.stackexchange.com": 1.0,
    "default": 1.0,
}


def _host(url: str) -> str:
    from urllib.parse import urlparse
    return urlparse(url).netloc.lstrip("www.")


def _wait_for_rate(host: str):
    delay = MIN_DELAY.get(host, MIN_DELAY["default"])
    last, lock = _rate_locks[host]
    with lock:
        elapsed = time.time() - last
        if elapsed < delay:
            time.sleep(delay - elapsed)
        _rate_locks[host] = (time.time(), lock)


def _robots_allow(url: str) -> bool:
    host = _host(url)
    from urllib.parse import urlparse
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    if robots_url not in _robot_cache:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        try:
            rp.read()
        except Exception:
            return True
        _robot_cache[robots_url] = rp
    return _robot_cache[robots_url].can_fetch(UA, url)


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=2, min=2, max=60),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    reraise=True,
)
def get(url: str, params: Optional[dict] = None, headers: Optional[dict] = None,
        timeout: float = 20.0, skip_robots: bool = False) -> httpx.Response:
    host = _host(url)
    if not skip_robots and not _robots_allow(url):
        log.warning(f"robots.txt disallows {url} — skipping")
        raise PermissionError(f"robots.txt blocks {url}")
    _wait_for_rate(host)
    h = {"User-Agent": UA, **(headers or {})}
    resp = httpx.get(url, params=params, headers=h, timeout=timeout, follow_redirects=True)
    if resp.status_code == 429:
        retry_after = int(resp.headers.get("Retry-After", 60))
        log.warning(f"Rate limited by {host}, sleeping {retry_after}s")
        time.sleep(retry_after)
        raise httpx.HTTPStatusError("429", request=resp.request, response=resp)
    resp.raise_for_status()
    return resp
