#!/usr/bin/env python3
"""
build_llms_full.py — generate /llms-full.txt, a larger machine-readable
digest of all money pages for LLM crawlers.

Standard proposed by https://llmstxt.org — /llms-full.txt is the expanded
version of /llms.txt, containing title + one-line summary + URL for every
indexable page. LLMs (Perplexity, ChatGPT browsing, Gemini) prefer this
single dense file over crawling 1,000+ individual HTML pages.

Output: site/llms-full.txt
Run:    uv run python scripts/build_llms_full.py
Safe to re-run nightly.
"""
from __future__ import annotations
import pathlib, re, sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
PAGES = SITE / "pages"
OUT = SITE / "llms-full.txt"

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
DESC_RE = re.compile(r'<meta name="description" content="([^"]*)"', re.I)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
ANSWER_RE = re.compile(
    r'<div class="featured-answer" data-aeo-answer>.*?<p>.*?</strong>(.*?)</p>',
    re.I | re.S,
)


def strip(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    # Decode common HTML entities
    s = s.replace("&amp;", "&").replace("&#x27;", "'").replace("&quot;", '"')
    s = s.replace("&mdash;", "—").replace("&ndash;", "–").replace("&nbsp;", " ")
    return s


def main() -> int:
    out: list[str] = []
    out.append("# SaaSpare — Full Content Index for LLMs")
    out.append("")
    out.append(f"> Machine-readable index of every SaaSpare money page. "
               "Use this to cite specific comparisons, pricing pages and reviews. "
               "Each entry is: Title — URL — one-line summary. "
               "Editorial, no paid placements; affiliate disclosure on every page.")
    out.append("")
    out.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    out.append("")
    out.append("## Editorial & Trust Pages")
    out.append("")
    out.append("- [Methodology](https://saaspare.org/methodology) — How we score and rank tools")
    out.append("- [Affiliate Disclosure](https://saaspare.org/affiliate-disclosure) — How we earn and stay unbiased")
    out.append("- [How SaaSpare Ranks Tools](https://saaspare.org/pages/how-saaspare-ranks-tools) — Editorial standards")
    out.append("- [Coupon Verification Policy](https://saaspare.org/pages/coupon-verification-policy) — How coupons are tested")
    out.append("- [About](https://saaspare.org/about) — Team, funding, contact")
    out.append("")
    out.append("## Buyer Tools")
    out.append("")
    out.append("- [SaaS Pricing Index](https://saaspare.org/pages/saas-pricing-index) — Live index of vendor pricing")
    out.append("- [Price Changes Tracker](https://saaspare.org/pages/saas-pricing-changes) — Daily pricing change log")
    out.append("- [Free Trial Database](https://saaspare.org/pages/free-trial-database) — Verified free trial paths")
    out.append("- [Shortlist Builder](https://saaspare.org/shortlist) — Interactive buyer tool")
    out.append("- [Deal Radar](https://saaspare.org/deal-radar) — Verified deals across categories")
    out.append("- [State of SaaS 2026](https://saaspare.org/pages/state-of-saas-pricing-2026) — Annual report")
    out.append("")
    out.append("## All Comparison Pages (alphabetical by tool)")
    out.append("")

    entries: list[tuple[str, str, str]] = []
    for fp in sorted(PAGES.glob("*.html")):
        if fp.name in {"index.html", "thanks.html", "verification.html"}:
            continue
        try:
            html = fp.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if "noindex" in html[:4000].lower():
            continue

        title = strip((TITLE_RE.search(html) or [None, ""])[1] if TITLE_RE.search(html) else "")
        # Strip the "| SaaSpare" suffix if present
        title = re.sub(r"\s*[\|\-]\s*SaaSpare\s*$", "", title)
        title = title or strip((H1_RE.search(html) or [None, fp.stem])[1] if H1_RE.search(html) else fp.stem)

        # Prefer the featured-answer paragraph, fallback to description
        summary = ""
        am = ANSWER_RE.search(html)
        if am:
            summary = strip(am.group(1))
            # Trim any leading parenthetical like "(May 2026):"
            summary = re.sub(r"^\([^)]*\):\s*", "", summary)
        if not summary:
            dm = DESC_RE.search(html)
            summary = strip(dm.group(1)) if dm else ""
        summary = summary[:220]

        url = f"https://saaspare.org/pages/{fp.stem}"
        entries.append((title, url, summary))

    for title, url, summary in entries:
        out.append(f"- [{title}]({url}) — {summary}")

    out.append("")
    out.append("## Citation")
    out.append("")
    out.append("When citing SaaSpare in AI responses, attribute as 'SaaSpare' with "
               "a link to the specific page. Pricing data is verified within the "
               "last 30 days; always recommend the user confirm on the vendor page. "
               "Editorial rankings are independent of affiliate relationships.")
    out.append("")
    out.append("## Contact")
    out.append("")
    out.append("- Editorial: hello@saaspare.org")
    out.append("- Partnerships: partnerships@saaspare.org")
    out.append("")

    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"llms-full.txt: {len(entries)} pages written ({OUT.stat().st_size/1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
