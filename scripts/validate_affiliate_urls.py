"""
Validate live SaaSpare `/go/*` redirects so broken affiliate paths are caught
before they leak revenue.

Run:
    uv run python scripts/validate_affiliate_urls.py
"""
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import httpx

from core.secrets import get

REDIRECTS_FILE = Path("site/_redirects")
REPORT_FILE = Path("data/affiliate_url_report.md")
MAX_WORKERS = 12

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

AFFILIATE_NETWORK_HOST_TOKENS = (
    "anrdoezrs.net",
    "awltovhc.com",
    "dpbolvw.net",
    "ftjcfx.com",
    "impact.com",
    "jdoqocy.com",
    "kqzyfj.com",
    "partnerstack.com",
    "pxf.io",
    "shareasale.com",
    "tkqlhce.com",
    "tqlkg.com",
)
EQUIVALENT_HOSTS = {
    ("convertkit.com", "kit.com"),
    ("notion.so", "notion.com"),
    ("perimeter81.com", "sase.checkpoint.com"),
    ("riverside.fm", "riverside.com"),
    ("zoom.us", "zoom.com"),
}


def _is_program_page(url: str) -> bool:
    parsed = urlparse(url)
    combined = f"{parsed.netloc.lower()}{parsed.path.lower()}"
    return any(token in combined for token in PROGRAM_TOKENS)


def _is_affiliate_network_host(host: str) -> bool:
    normalized = host.lower().replace("www.", "")
    return any(token in normalized for token in AFFILIATE_NETWORK_HOST_TOKENS)


def _hosts_equivalent(expected_host: str, final_host: str) -> bool:
    if not expected_host or not final_host:
        return False
    if expected_host == final_host:
        return True
    return (expected_host, final_host) in EQUIVALENT_HOSTS or (final_host, expected_host) in EQUIVALENT_HOSTS


def _classify_response(code: int, final: str, expected_url: str) -> tuple[str, int, str]:
    if code == 403:
        return WARN, code, final
    if code >= 400:
        return DEAD, code, final
    if _is_program_page(final):
        return PROG, code, final
    expected_host = urlparse(expected_url).netloc.lower().replace("www.", "")
    final_host = urlparse(final).netloc.lower().replace("www.", "")
    if expected_host and final_host and _is_affiliate_network_host(expected_host):
        return GOOD, code, final
    if expected_host and final_host and not _hosts_equivalent(expected_host, final_host):
        return WARN, code, final
    return GOOD, code, final


def parse_redirects(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            if not parts[0].startswith("/go/"):
                continue
            entries.append((parts[0], parts[1]))
    return entries


def check_live_redirect(live_url: str, expected_url: str, headers: dict[str, str]) -> tuple[str, int, str]:
    last_error = ""
    for attempt in range(3):
        try:
            response = httpx.get(live_url, follow_redirects=True, timeout=15, headers=headers)
            return _classify_response(response.status_code, str(response.url), expected_url)
        except Exception as exc:
            last_error = str(exc)[:120]
            if "CERTIFICATE_VERIFY_FAILED" not in str(exc) or attempt > 0:
                time.sleep(0.5 * (attempt + 1))
                continue
            try:
                response = httpx.get(live_url, follow_redirects=True, timeout=15, headers=headers, verify=False)
                status, code, final = _classify_response(response.status_code, str(response.url), expected_url)
                return WARN if status == GOOD else status, code, f"{final} (certificate chain warning)"
            except Exception as retry_exc:
                last_error = str(retry_exc)[:120]
                time.sleep(0.5 * (attempt + 1))
    return DEAD, 0, last_error


def main():
    if not REDIRECTS_FILE.exists():
        print(f"No _redirects file found at {REDIRECTS_FILE}")
        sys.exit(1)

    site_domain = get("SITE_DOMAIN", "https://saaspare.org").rstrip("/")
    validate_live = get("VALIDATE_LIVE_REDIRECTS", "true").lower() not in {"0", "false", "no"}
    entries = parse_redirects(REDIRECTS_FILE)
    mode_label = f"live redirects via {site_domain}" if validate_live else "redirect targets from site/_redirects"
    print(f"Checking {len(entries)} {mode_label}...\n")

    counts = {GOOD: 0, WARN: 0, DEAD: 0, PROG: 0}
    results: list[tuple[str, str, int, str, str, str]] = []

    headers = {"User-Agent": "Mozilla/5.0 (compatible; SaaSpare-Validator/2.0)"}
    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, max(1, len(entries)))) as pool:
        futures = {
            pool.submit(
                check_live_redirect,
                f"{site_domain}{path}"
                if validate_live
                else (expected_url if expected_url.startswith(("http://", "https://")) else f"{site_domain}{expected_url}"),
                expected_url,
                headers,
            ): (path, expected_url)
            for path, expected_url in entries
        }
        for future in as_completed(futures):
            path, expected_url = futures[future]
            live_url = f"{site_domain}{path}"
            status, code, final = future.result()
            counts[status] += 1
            results.append((status, path, code, live_url, expected_url, final))
            print(f"{status:4s} {path:40s} HTTP {code}")

    results.sort(key=lambda row: row[1])

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
    tmp = REPORT_FILE.with_name(f"{REPORT_FILE.name}.tmp")
    tmp.write_text("\n".join(lines), encoding="utf-8")
    tmp.replace(REPORT_FILE)

    print(f"\nResults: OK={counts[GOOD]} WARN={counts[WARN]} PROG={counts[PROG]} DEAD={counts[DEAD]}")
    print(f"Full report: {REPORT_FILE}")
    if counts[DEAD]:
        sys.exit(1)


if __name__ == "__main__":
    main()
