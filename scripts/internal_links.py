#!/usr/bin/env python3
"""
internal_links.py — kill orphan pages by injecting a "Related comparisons"
block onto every money page.

Finding from the May 2026 audit: 850 of 1,034 money pages had zero inbound
internal links. Google ranks orphans poorly — it's the single largest
on-site fix available.

This script injects a block of 4-6 contextually relevant links onto every
money page so no page is an orphan. It is idempotent (replaces any
previous block it wrote) and groups links by:

  - Same tool (e.g. hubspot-pricing ↔ hubspot-review ↔ hubspot-alternatives)
  - Same vertical (CRM, SEO, etc.)
  - Same page kind (vs/best-of/alternatives)
  - "People also compare X vs Y" based on filename tokens

Run:  uv run python scripts/internal_links.py
Safe to re-run nightly.
"""
from __future__ import annotations
import argparse, json, os, pathlib, random, re, sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / "site" / "pages"
OUTPUTS = ROOT / "outputs" / "seo"
OUTPUTS.mkdir(parents=True, exist_ok=True)

BLOCK_START = "<!-- related-links-start (do not edit: managed by internal_links.py) -->"
BLOCK_END = "<!-- related-links-end -->"
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)

# Hashable identifier for any money page: tool token + page kind
KIND_PATTERNS = [
    ("pricing",       re.compile(r"^(.+?)-pricing-2026")),
    ("review",        re.compile(r"^(.+?)-review-2026")),
    ("free_trial",    re.compile(r"^(.+?)-free-trial-2026")),
    ("coupon",        re.compile(r"^(.+?)-coupon-code-2026")),
    ("coupon",        re.compile(r"^(.+?)-coupon-2026")),
    ("alternatives",  re.compile(r"^(?:\d+-)?best-(.+?)-alternatives-in-2026")),
    ("alternatives",  re.compile(r"^(.+?)-alternatives-2026")),
    ("free_plan",     re.compile(r"^does-(.+?)-have-a-free-plan-2026")),
    ("comparison",    re.compile(r"^(.+?)-vs-(.+?)-which-is-better-in-2026")),
    ("bestof",        re.compile(r"^(?:\d+-)?best-(.+?)-(?:software|tools|for-.+?)-in-2026")),
]

VERTICAL_KEYWORDS = {
    "crm":               {"crm", "salesforce", "hubspot", "pipedrive", "zoho", "close", "freshsales", "keap", "copper"},
    "seo":               {"ahrefs", "semrush", "moz", "surfer", "mangools", "frase", "clearscope", "spyfu", "ubersuggest", "se-ranking"},
    "project_mgmt":      {"asana", "clickup", "monday", "notion", "wrike", "smartsheet", "linear", "trello", "basecamp", "todoist"},
    "hr_recruiting":     {"bamboohr", "rippling", "gusto", "deel", "workable", "greenhouse", "lever", "workday", "lattice", "culture-amp"},
    "finance_ops":       {"ramp", "brex", "expensify", "freshbooks", "xero", "chargebee", "stripe", "quickbooks", "wave", "zoho-books", "airbase", "divvy"},
    "dev_tools":         {"github-copilot", "jetbrains", "sentry", "datadog", "snyk", "render", "supabase", "linear", "vercel", "retool", "docker"},
    "security":          {"1password", "bitwarden", "dashlane", "nordpass", "nordlayer", "cloudflare", "okta", "crowdstrike", "qualys", "tenable", "sentinelone", "duo-security", "tresorit"},
    "ai_tools":          {"jasper", "copy-ai", "writesonic", "pinecone", "weaviate", "openai", "anthropic", "cohere", "notion-ai", "grammarly"},
    "marketing_auto":    {"mailchimp", "activecampaign", "convertkit", "klaviyo", "getresponse", "brevo", "lemlist", "marketo", "hubspot-marketing"},
    "analytics":         {"mixpanel", "amplitude", "hotjar", "fullstory", "databox", "heap", "segment"},
    "ecommerce":         {"shopify", "bigcommerce", "gumroad", "woocommerce", "paddle", "recurly", "recharge"},
    "cloud_infra":       {"digitalocean", "vultr", "hetzner", "contabo", "linode", "aws", "heroku", "gcp", "azure"},
    "legal_contract":    {"docusign", "pandadoc", "ironclad", "contractbook", "juro", "concord"},
    "video_conference":  {"zoom", "google-meet", "microsoft-teams", "whereby", "loom"},
}


def detect(filename: str) -> dict:
    """Return {tool, tool2, kind, vertical} for a money page filename."""
    base = filename.lower().removesuffix(".html")
    for kind, pat in KIND_PATTERNS:
        m = pat.match(base)
        if not m:
            continue
        tool = m.group(1)
        tool2 = m.group(2) if m.lastindex and m.lastindex >= 2 else None
        vertical = None
        for v, kws in VERTICAL_KEYWORDS.items():
            if any(kw in base for kw in kws):
                vertical = v
                break
        return {"tool": tool, "tool2": tool2, "kind": kind, "vertical": vertical, "base": base}
    return {"tool": None, "tool2": None, "kind": None, "vertical": None, "base": base}


def index_pages() -> tuple[list[dict], dict]:
    """Walk all money pages, return (records, lookup) for fast related-picking."""
    records: list[dict] = []
    lookup: dict = {
        "by_tool": defaultdict(list),
        "by_kind": defaultdict(list),
        "by_vertical": defaultdict(list),
    }
    for fp in sorted(PAGES.glob("*.html")):
        if fp.name in {"index.html", "thanks.html", "verification.html"}:
            continue
        # Skip noindex
        try:
            head = fp.read_text(encoding="utf-8", errors="replace")[:4000].lower()
        except Exception:
            continue
        if "noindex" in head and '<meta name="robots" content="noindex' in head:
            continue
        info = detect(fp.name)
        info["file"] = fp.name
        info["url"] = f"/pages/{fp.stem}"
        info["title"] = _extract_h1(fp) or fp.stem.replace("-", " ").title()
        records.append(info)
        if info["tool"]:
            lookup["by_tool"][info["tool"]].append(info)
            if info["tool2"]:
                lookup["by_tool"][info["tool2"]].append(info)
        if info["kind"]:
            lookup["by_kind"][info["kind"]].append(info)
        if info["vertical"]:
            lookup["by_vertical"][info["vertical"]].append(info)
    return records, lookup


def _extract_h1(fp: pathlib.Path) -> str | None:
    try:
        html = fp.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    m = H1_RE.search(html)
    if not m:
        return None
    # Tags become a space so a <br> inside the h1 can't glue words together
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip()


def pick_related(rec: dict, lookup: dict, records: list[dict], n: int = 5) -> list[dict]:
    """Pick 5 contextually-relevant links for a given page."""
    picks: list[dict] = []
    seen: set[str] = {rec["url"]}

    def add(items: list[dict], cap: int) -> None:
        for it in items:
            if len(picks) >= n:
                return
            if it["url"] in seen:
                continue
            picks.append(it)
            seen.add(it["url"])
            if len([p for p in picks if p.get("_bucket") == cap]) >= 3:
                return

    # 1. Same tool, different kinds (e.g. hubspot-pricing → hubspot-review + hubspot-alternatives)
    if rec["tool"]:
        same_tool = [r for r in lookup["by_tool"].get(rec["tool"], []) if r["kind"] != rec["kind"]]
        random.shuffle(same_tool)
        for s in same_tool[:2]:
            s["_bucket"] = "same_tool"
            add([s], "same_tool")
    # 2. Same vertical, different tools (same buyer intent)
    if rec["vertical"] and len(picks) < n:
        same_vert = [r for r in lookup["by_vertical"].get(rec["vertical"], []) if r["tool"] != rec["tool"]]
        random.shuffle(same_vert)
        for s in same_vert[:3]:
            s["_bucket"] = "same_vertical"
            add([s], "same_vertical")
    # 3. Same kind of page (all comparisons → other comparisons)
    if rec["kind"] and len(picks) < n:
        same_kind = [r for r in lookup["by_kind"].get(rec["kind"], []) if r["tool"] != rec["tool"]]
        random.shuffle(same_kind)
        for s in same_kind[:2]:
            s["_bucket"] = "same_kind"
            add([s], "same_kind")
    # 4. Fallback: random pool
    if len(picks) < n:
        pool = [r for r in records if r["url"] not in seen]
        random.shuffle(pool)
        for s in pool[: n - len(picks)]:
            picks.append(s)
            seen.add(s["url"])
    return picks[:n]


def render_block(rec: dict, picks: list[dict]) -> str:
    """Render the HTML block injected into the page."""
    items = []
    for p in picks:
        label = p["title"][:80].strip()
        items.append(f'    <li><a href="{p["url"]}">{label}</a></li>')
    lis = "\n".join(items)
    heading = "Related comparisons you should also see"
    if rec["kind"] == "pricing":
        heading = "More on pricing, trials and alternatives"
    elif rec["kind"] == "comparison":
        heading = "More head-to-head comparisons"
    elif rec["kind"] == "alternatives":
        heading = "More alternative lists and verdicts"
    elif rec["kind"] == "review":
        heading = "More reviews and pricing deep-dives"
    elif rec["kind"] == "bestof":
        heading = "More best-of guides and shortlists"
    return (
        f'\n{BLOCK_START}\n'
        f'<aside class="related-links" aria-label="Related comparisons" '
        f'style="max-width:920px;margin:3rem auto;padding:1.5rem;'
        f'background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);'
        f'border-radius:14px">\n'
        f'  <h2 style="font-size:1.1rem;margin:0 0 1rem 0;color:#e94560">'
        f'{heading}</h2>\n'
        f'  <ul style="list-style:none;padding:0;margin:0;display:grid;'
        f'grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:.7rem">\n'
        f'{lis}\n'
        f'  </ul>\n'
        f'</aside>\n'
        f'{BLOCK_END}\n'
    )


REMOVE_BLOCK_RE = re.compile(
    re.escape(BLOCK_START) + r".*?" + re.escape(BLOCK_END) + r"\s*",
    re.DOTALL,
)


def inject(fp: pathlib.Path, block: str) -> bool:
    html = fp.read_text(encoding="utf-8", errors="replace")
    # remove old block if present
    html2 = REMOVE_BLOCK_RE.sub("", html)
    # find </main> or <footer> to insert above
    anchor = re.search(r"</main>", html2, re.I)
    if not anchor:
        anchor = re.search(r"<footer", html2, re.I)
    if not anchor:
        return False
    new = html2[: anchor.start()] + block + html2[anchor.start():]
    if new == html:
        return False
    fp.write_text(new, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true", help="dry run")
    p.add_argument("--seed", type=int, default=None, help="random seed for reproducible picks")
    args = p.parse_args(argv)

    if args.seed is not None:
        random.seed(args.seed)

    records, lookup = index_pages()
    report = {
        "total_pages": len(records),
        "updated": 0,
        "skipped": 0,
        "orphans_before": 0,
        "orphans_after": 0,
        "samples": [],
    }

    # Count orphans before
    before_links: dict = defaultdict(int)
    for fp in PAGES.glob("*.html"):
        try:
            html = fp.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in re.finditer(r'href="/pages/([^"?#]+?)(?:\.html)?["?#]', html):
            before_links[m.group(1) + ".html"] += 1
    report["orphans_before"] = sum(1 for r in records if before_links.get(r["file"], 0) == 0)

    for rec in records:
        fp = PAGES / rec["file"]
        picks = pick_related(rec, lookup, records, n=5)
        block = render_block(rec, picks)
        if args.check:
            continue
        ok = inject(fp, block)
        if ok:
            report["updated"] += 1
            if len(report["samples"]) < 3:
                report["samples"].append({
                    "file": rec["file"],
                    "picks": [p["url"] for p in picks],
                })
        else:
            report["skipped"] += 1

    # Count orphans after
    after_links: dict = defaultdict(int)
    for fp in PAGES.glob("*.html"):
        try:
            html = fp.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in re.finditer(r'href="/pages/([^"?#]+?)(?:\.html)?["?#]', html):
            after_links[m.group(1) + ".html"] += 1
    report["orphans_after"] = sum(1 for r in records if after_links.get(r["file"], 0) == 0)

    (OUTPUTS / "internal_links.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(f"=== internal_links ===")
    print(f"  total pages     : {report['total_pages']}")
    print(f"  orphans before  : {report['orphans_before']}")
    print(f"  orphans after   : {report['orphans_after']}")
    print(f"  pages updated   : {report['updated']}")
    print(f"  pages skipped   : {report['skipped']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
