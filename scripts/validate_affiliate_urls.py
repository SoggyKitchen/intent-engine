"""
Validate live SaaSpare `/go/*` redirects so broken affiliate paths are caught
before they leak revenue.

Run:
    uv run python scripts/validate_affiliate_urls.py
"""
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx

from core.secrets import get

REDIRECTS_FILE = Path("site/_redirects")
REPORT_FILE = Path("data/affiliate_url_report.md")

GOOD = "OK"
WARN = "WARN"
DEAD = "DEAD"
PROG = "PROG"

PROGRAM_TOKENS = (
    "affiliate",
    "affiliates",
    "affiliate-program",
    "partner",
    "partners",
    "partner-program",
    "referral",
    "refer-a-business",
    "become-an-affiliate",
)


def _is_program_page(url: str) -> bool:
    parsed = urlparse(url)
    combined = f"{parsed.netloc.lower()}{parsed.path.lower()}"
    return any(token in combined for token in PROGRAM_TOKENS)


def parse_redirects(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            entries.append((parts[0], parts[1]))
    return entries


def check_live_redirect(live_url: str, expected_url: str, client: httpx.Client) -> tuple[str, int, str]:
    try:
        response = client.get(live_url, follow_redirects=True, timeout=20)
        code = response.status_code
        final = str(response.url)
        if code == 403:
            return WARN, code, final
        if code >= 400:
            return DEAD, code, final
        if _is_program_page(final):
            return PROG, code, final
        expected_host = urlparse(expected_url).netloc.lower().replace("www.", "")
        final_host = urlparse(final).netloc.lower().replace("www.", "")
        if expected_host and final_host and expected_host != final_host:
            return WARN, code, final
        return GOOD, code, final
    except Exception as exc:
        return DEAD, 0, str(exc)[:120]


def main():
    if not REDIRECTS_FILE.exists():
        print(f"No _redirects file found at {REDIRECTS_FILE}")
        sys.exit(1)

    site_domain = get("SITE_DOMAIN", "https://saaspare.org").rstrip("/")
    entries = parse_redirects(REDIRECTS_FILE)
    print(f"Checking {len(entries)} live redirects via {site_domain}...\n")

    counts = {GOOD: 0, WARN: 0, DEAD: 0, PROG: 0}
    results: list[tuple[str, str, int, str, str, str]] = []

    headers = {"User-Agent": "Mozilla/5.0 (compatible; SaaSpare-Validator/2.0)"}
    with httpx.Client(headers=headers) as client:
        for path, expected_url in entries:
            live_url = f"{site_domain}{path}"
            status, code, final = check_live_redirect(live_url, expected_url, client)
            counts[status] += 1
            results.append((status, path, code, live_url, expected_url, final))
            print(f"{status:4s} {path:40s} HTTP {code}")
            time.sleep(0.15)

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# Affiliate URL Validation - {time.strftime('%Y-%m-%d')}", ""]
    lines.append(f"Live domain: `{site_domain}`")
    lines.append(f"Checked {len(entries)} redirects")
    lines.append("")
    lines.append(f"- OK: {counts[GOOD]}")
    lines.append(f"- WARN: {counts[WARN]}")
    lines.append(f"- PROG: {counts[PROG]}")
    lines.append(f"- DEAD: {counts[DEAD]}")
    lines.append("")
    for status, path, code, live_url, expected_url, final in results:
        lines.append(f"## {status} `{path}`")
        lines.append(f"- HTTP: `{code}`")
        lines.append(f"- Live URL: `{live_url}`")
        lines.append(f"- Expected destination: `{expected_url}`")
        lines.append(f"- Final destination: `{final}`")
        lines.append("")
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")

    print(f"\nResults: OK={counts[GOOD]} WARN={counts[WARN]} PROG={counts[PROG]} DEAD={counts[DEAD]}")
    print(f"Full report: {REPORT_FILE}")
    if counts[DEAD] or counts[PROG]:
        sys.exit(1)


if __name__ == "__main__":
    main()
