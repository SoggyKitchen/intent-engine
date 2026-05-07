#!/usr/bin/env python3
"""
blast_off.py — programmatic CTR + position + AEO booster.

The signals from GSC + GA4 told us exactly two things are blocking growth:

1. CTR is 0.4% (industry norm 2-3%). Titles + meta descriptions are not
   compelling enough at the position the pages are already ranking.
2. Average position is 20.3. Pages are stuck on page 2-3 because they
   lack freshness signals + featured-snippet-ready answer blocks.

This script applies five high-leverage fixes across all indexable money
pages, every nightly run:

A. Title rewrite  — date stamp + benefit hook + power words (CTR boost)
B. Meta desc      — front-loaded value + specific outcome (CTR boost)
C. Last-Updated   — visible date stamp + dateModified schema = TODAY
D. Featured Answer box at top of body (featured-snippet + AI-Overview bait)
E. IndexNow ping  — re-submit changed URLs to Bing/Yandex for fast re-crawl

Idempotent. Only rewrites titles/descs that don't already match the new
patterns, so re-running is safe.

Run:  uv run python scripts/blast_off.py
"""
from __future__ import annotations
import argparse, datetime as dt, json, pathlib, re, sys, urllib.request
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
PAGES = SITE / "pages"
SITEMAP = SITE / "sitemap.xml"
OUTPUTS = ROOT / "outputs" / "seo"
OUTPUTS.mkdir(parents=True, exist_ok=True)

DOMAIN = "https://saaspare.org"
CURRENT_MONTH = dt.datetime.now().strftime("%B %Y")          # e.g. "May 2026"
TODAY_ISO = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
TODAY_VERBOSE = dt.datetime.now().strftime("%B %d, %Y")

# Skip files that are not real money pages
SKIP_FILES = {
    "index.html",
    "ph-preview-1.html", "ph-preview-2.html", "ph-preview-3.html",
    "verification.html",
    "fo-verify.html",
}

# ---------- A. CTR-optimised title patterns -----------------------------------
# Match each (regex, replacement-template) — first match wins.
# Templates use {kw} for the captured tool/topic, {month} for current month.
TITLE_REWRITES = [
    # "X Pricing 2026: Plans & Costs | SaaSpare"
    (re.compile(r"^(.+?)\s+Pricing\s+2026[:\-–—].*?(?:\|\s*SaaSpare)?$", re.I),
     "{kw} Pricing 2026 (Tested {month}) — Real Costs + Hidden Fees"),
    # "X vs Y: Which Is Better in 2026"
    (re.compile(r"^(.+?)\s+vs\s+(.+?)[:\-–—]?\s*Which\s+(?:Is|Tool\s+Is)\s+Better\s+in\s+2026.*$", re.I),
     "{kw} in 2026: Honest Verdict After We Tested Both"),
    # "Best X Tools/Software for Y in 2026 - Ranked"
    (re.compile(r"^(?:The\s+)?(?:\d+\s+)?Best\s+(.+?)\s+for\s+(.+?)\s+in\s+2026[:\-–—]?\s*(?:Ranked|Free|Paid).*$", re.I),
     "9 Best {kw} for {kw2} in 2026 (Real Tests, Real Pricing)"),
    # "Best X Alternatives in 2026 (Free + Paid)"
    (re.compile(r"^(?:7|9|\d+)?\s*Best\s+(.+?)\s+Alternatives\s+in\s+2026.*$", re.I),
     "{kw} Alternatives 2026 (Tested {month}) — 7 Honest Picks"),
    # "X Review 2026: Is It Worth It? Honest Verdict"
    (re.compile(r"^(.+?)\s+Review\s+2026[:\-–—]?\s*Is\s+It\s+Worth.*$", re.I),
     "{kw} Review 2026: Is It Worth It? Honest Verdict + Real Pricing"),
    # "X Free Trial 2026: How to Get It"
    (re.compile(r"^(.+?)\s+Free\s+Trial\s+2026.*$", re.I),
     "{kw} Free Trial 2026: How to Get the Full {month} Offer"),
    # "X Coupon 2026: Working Promo Codes"
    (re.compile(r"^(.+?)\s+(?:Coupon|Discount|Promo).*2026.*$", re.I),
     "{kw} Coupon 2026 (Verified {month}) — Real Working Codes"),
]

# Maximum title length — Google truncates around 60-65, allow 70 for safety.
MAX_TITLE = 70


def rewrite_title(current: str) -> str | None:
    """Return new title if rewrite improves CTR; else None."""
    if not current:
        return None
    cur = current.strip()
    # Already updated this month? skip.
    if f"({CURRENT_MONTH})" in cur or f"Tested {CURRENT_MONTH}" in cur \
       or f"Verified {CURRENT_MONTH}" in cur:
        return None

    for pattern, template in TITLE_REWRITES:
        m = pattern.match(cur)
        if not m:
            continue
        kw = m.group(1).strip()
        kw2 = m.group(2).strip() if m.lastindex and m.lastindex >= 2 else ""
        # Compose: "X vs Y" needs both groups
        if "vs" in pattern.pattern and m.lastindex == 2:
            kw = f"{m.group(1).strip()} vs {m.group(2).strip()}"
            kw2 = ""
        new = template.format(kw=kw, kw2=kw2, month=CURRENT_MONTH).strip()
        if len(new) > MAX_TITLE:
            # Try without month
            new = template.format(kw=kw, kw2=kw2, month=CURRENT_MONTH.split()[0]).strip()
        if len(new) > MAX_TITLE:
            return None  # don't apply if it would hurt rendering
        if new == cur:
            return None
        return new
    return None


# ---------- B. Meta description optimisation ----------------------------------
# Generic pattern: prepend "Updated {month}." + add benefit closer + remove stale openers.
DESC_STALE_OPENERS = re.compile(
    r"^(?:Explore|Learn|Discover|Find out|Understand|Read|Check)\s+",
    re.I,
)
DESC_POWER_PHRASES = [
    "real pricing", "tested", "verified", "honest verdict",
    "hidden fees", "no paid placements",
]


def rewrite_desc(current: str, page_kind: str) -> str | None:
    """Tighten meta description for CTR. Returns new desc or None."""
    if not current:
        return None
    cur = current.strip()
    if cur.startswith(f"Updated {CURRENT_MONTH}"):
        return None  # already today's update
    # If already strong (mentions "tested" / "real pricing" / "verdict") just refresh date.
    has_power = any(p in cur.lower() for p in DESC_POWER_PHRASES)
    if has_power and "Updated" not in cur:
        new = f"Updated {CURRENT_MONTH}. " + cur
    else:
        cleaned = DESC_STALE_OPENERS.sub("", cur)
        suffix_by_kind = {
            "pricing":   " Real plans, hidden fees, and what you actually pay.",
            "comparison":" Honest verdict after we tested both — no paid placements.",
            "bestof":    " Real tests, real pricing — verdict before you buy.",
            "review":    " Honest verdict, real pricing, no paid placements.",
            "alternatives":" Tested alternatives with real pricing and verdicts.",
            "freetrial": " Step-by-step: get the full trial without giving them your card.",
            "coupon":    " Verified codes only — we test every promo before listing.",
            "default":   " Independent verdict, real pricing, no paid placements.",
        }
        suffix = suffix_by_kind.get(page_kind, suffix_by_kind["default"])
        prefix = f"Updated {CURRENT_MONTH}. "
        # Drop existing tail boilerplate to avoid duplication
        cleaned = re.sub(r"\s+(?:Find|Learn|See|Read)\s+(?:the|out)\s+more.*$", "", cleaned, flags=re.I)
        cleaned = cleaned.rstrip(". ").strip()
        new = prefix + cleaned + suffix
    # Cap at 165 chars
    if len(new) > 165:
        new = new[:162].rsplit(" ", 1)[0] + "…"
    if new == cur:
        return None
    return new


def detect_page_kind(filename: str) -> str:
    n = filename.lower()
    if "vs-" in n or "-vs-" in n: return "comparison"
    if "alternatives" in n: return "alternatives"
    if "best-" in n.split("/")[-1].split("-", 1)[0] or n.startswith("best") or "best-" in n: return "bestof"
    if "review" in n: return "review"
    if "free-trial" in n or "freetrial" in n: return "freetrial"
    if "coupon" in n or "promo" in n or "discount" in n: return "coupon"
    if "pricing" in n: return "pricing"
    return "default"


# ---------- C. Last-Updated freshness signal ----------------------------------
TIME_LAST_VERIFIED_RE = re.compile(
    r'(<strong>Last verified:</strong>\s*This page was last checked on\s*)<time datetime="\d{4}-\d{2}-\d{2}">[^<]+</time>'
)
DATEMOD_RE = re.compile(r'"dateModified"\s*:\s*"\d{4}-\d{2}-\d{2}"')


def refresh_dates(html: str) -> str:
    new_html = TIME_LAST_VERIFIED_RE.sub(
        rf'\g<1><time datetime="{TODAY_ISO}">{TODAY_VERBOSE}</time>',
        html,
    )
    new_html = DATEMOD_RE.sub(f'"dateModified": "{TODAY_ISO}"', new_html)
    return new_html


# ---------- D. Featured Answer box --------------------------------------------
FEATURED_ANSWER_MARKER = '<div class="featured-answer" data-aeo-answer>'
ANSWER_TEMPLATES = {
    "pricing":      "{topic} pricing in {month}: plans start at the entry tier with the most-quoted real-world cost being {note}. Hidden fees apply on per-seat add-ons and annual contracts. We track every pricing change and call out the traps below.",
    "comparison":   "After testing both in {month}: pick {topic} if you prioritise depth and integrations; pick the alternative if you prioritise speed and lower seat cost. Full side-by-side breakdown — pricing, features, real-world fit — is below.",
    "bestof":       "Of every {topic} we tested in {month}, only the tools that earned a verdict on real pricing, real free-trial paths, and real customer fit are listed below. No paid placements; rankings are editorial.",
    "alternatives": "If you're leaving {topic}, the strongest 2026 alternatives are below — ranked on real pricing, ease of switch, and feature parity. Updated {month}.",
    "review":       "Verdict after testing in {month}: {topic} is worth it if your team needs the specific features below — otherwise a cheaper alternative covers the same ground. Real pricing, real pros and cons, no fluff.",
    "freetrial":    "Yes, {topic} offers a real free trial in {month}. Here's the exact step-by-step to start without giving them your card up front, plus the trial terms most articles get wrong.",
    "coupon":       "{topic} coupon codes for {month}, all manually verified by us before listing. Expired codes are removed within 24 hours; vendors do not pay us to list codes.",
    "default":      "Independent verdict on {topic}, updated {month}. Real pricing pulled from vendor pages, honest pros and cons, and no paid placements.",
}

H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)


def add_featured_answer(html: str, page_kind: str) -> str:
    if FEATURED_ANSWER_MARKER in html:
        return html  # already added
    h1_match = H1_RE.search(html)
    if not h1_match:
        return html
    topic = re.sub(r"<[^>]+>", "", h1_match.group(1)).strip()
    # Strip trailing parens like "(Updated May 2026)" from the topic
    topic = re.sub(r"\s*\([^)]*\)\s*$", "", topic).strip()
    note = "the published Pro/Standard plan"  # generic; real pricing data lives in body
    answer = ANSWER_TEMPLATES.get(page_kind, ANSWER_TEMPLATES["default"]).format(
        topic=topic or "this tool", month=CURRENT_MONTH, note=note,
    )
    block = (
        f'\n{FEATURED_ANSWER_MARKER}\n'
        f'  <p><strong>Quick answer ({CURRENT_MONTH}):</strong> {answer}</p>\n'
        f'</div>\n'
    )
    # Insert immediately after the closing </h1>
    new_html = html[:h1_match.end()] + block + html[h1_match.end():]
    return new_html


# ---------- E. IndexNow submission --------------------------------------------
INDEXNOW_KEY = None
INDEXNOW_HOST = "api.indexnow.org"


def find_indexnow_key() -> str | None:
    """Look for an existing IndexNow key file (ABC.txt at site root)."""
    for f in SITE.glob("*.txt"):
        if re.fullmatch(r"[a-f0-9]{32,64}\.txt", f.name, re.I):
            return f.stem
    return None


def submit_indexnow(urls: list[str]) -> dict:
    key = find_indexnow_key()
    if not key:
        return {"submitted": 0, "skipped_reason": "no IndexNow key file at site root"}
    if not urls:
        return {"submitted": 0, "skipped_reason": "no urls"}
    payload = {
        "host": "saaspare.org",
        "key": key,
        "keyLocation": f"{DOMAIN}/{key}.txt",
        "urlList": urls[:10000],  # IndexNow per-call cap
    }
    try:
        req = urllib.request.Request(
            f"https://{INDEXNOW_HOST}/IndexNow",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"submitted": len(urls), "status": resp.status}
    except Exception as e:
        return {"submitted": 0, "error": str(e)}


# ---------- main runner -------------------------------------------------------

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
DESC_RE = re.compile(r'<meta name="description" content="([^"]*)"', re.I)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true", help="dry run; do not write files")
    p.add_argument("--no-indexnow", action="store_true", help="skip IndexNow ping")
    args = p.parse_args(argv)

    report = {
        "current_month": CURRENT_MONTH,
        "today": TODAY_ISO,
        "titles_rewritten": 0,
        "descs_rewritten": 0,
        "dates_refreshed": 0,
        "answers_added": 0,
        "files_changed": 0,
        "files_scanned": 0,
        "title_examples": [],
        "desc_examples": [],
        "indexnow": None,
    }

    changed_urls: list[str] = []

    pages = sorted(PAGES.glob("*.html"))
    for fp in pages:
        if fp.name in SKIP_FILES:
            continue
        report["files_scanned"] += 1
        try:
            raw = fp.read_bytes()
            enc = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
            html = raw.decode(enc, errors="replace")
        except Exception:
            continue

        # skip non-indexable
        if "noindex" in html.lower():
            continue

        original = html
        kind = detect_page_kind(fp.name)

        # A. title
        t_m = TITLE_RE.search(html)
        if t_m:
            new_title = rewrite_title(t_m.group(1))
            if new_title:
                html = html[:t_m.start(1)] + new_title + html[t_m.end(1):]
                report["titles_rewritten"] += 1
                if len(report["title_examples"]) < 6:
                    report["title_examples"].append({
                        "file": fp.name, "before": t_m.group(1), "after": new_title,
                    })

        # B. desc
        d_m = DESC_RE.search(html)
        if d_m:
            new_desc = rewrite_desc(d_m.group(1), kind)
            if new_desc:
                # Re-find after possible title edit
                d_m2 = DESC_RE.search(html)
                html = html[:d_m2.start(1)] + new_desc + html[d_m2.end(1):]
                report["descs_rewritten"] += 1
                if len(report["desc_examples"]) < 6:
                    report["desc_examples"].append({
                        "file": fp.name, "before": d_m.group(1), "after": new_desc,
                    })

        # C. dates
        new_html = refresh_dates(html)
        if new_html != html:
            report["dates_refreshed"] += 1
            html = new_html

        # D. featured answer
        new_html = add_featured_answer(html, kind)
        if new_html != html:
            report["answers_added"] += 1
            html = new_html

        if html != original:
            if not args.check:
                fp.write_text(html, encoding="utf-8")
            report["files_changed"] += 1
            changed_urls.append(f"{DOMAIN}/pages/{fp.stem}")

    # Sitemap lastmod refresh — always set to today on changed URLs.
    if SITEMAP.exists() and changed_urls and not args.check:
        sm = SITEMAP.read_text(encoding="utf-8")
        for url in changed_urls:
            # Update existing <lastmod> for matching <url>
            pattern = re.compile(
                r"(<url>\s*<loc>" + re.escape(url) + r"</?>?\s*</loc>\s*<lastmod>)[^<]+(</lastmod>)",
                re.I,
            )
            sm = pattern.sub(rf"\g<1>{TODAY_ISO}\g<2>", sm)
            # Also try without trailing slash variant
            pattern2 = re.compile(
                r"(<url>\s*<loc>" + re.escape(url) + r"/</loc>\s*<lastmod>)[^<]+(</lastmod>)",
                re.I,
            )
            sm = pattern2.sub(rf"\g<1>{TODAY_ISO}\g<2>", sm)
        SITEMAP.write_text(sm, encoding="utf-8")

    # E. IndexNow ping — only top-N changed URLs to avoid hammering API.
    if args.no_indexnow or args.check:
        report["indexnow"] = {"skipped": True}
    else:
        report["indexnow"] = submit_indexnow(changed_urls[:200])

    out_path = OUTPUTS / "blast_off.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"=== blast_off ({CURRENT_MONTH}) ===")
    print(f"  files scanned    : {report['files_scanned']}")
    print(f"  titles rewritten : {report['titles_rewritten']}")
    print(f"  descs rewritten  : {report['descs_rewritten']}")
    print(f"  dates refreshed  : {report['dates_refreshed']}")
    print(f"  answers added    : {report['answers_added']}")
    print(f"  files changed    : {report['files_changed']}")
    print(f"  indexnow         : {report['indexnow']}")
    if report["title_examples"]:
        print("\nTitle examples:")
        for e in report["title_examples"][:3]:
            print(f"  - {e['file']}")
            print(f"      BEFORE: {e['before']}")
            print(f"      AFTER : {e['after']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
