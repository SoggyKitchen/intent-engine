"""
Recovery hygiene: eliminate dead internal links (189 pages, 362 dead targets).

Dead internal links to non-existent pages are crawl waste + a low-quality
signal that works against a domain climbing out of an algorithmic
scaled-content-abuse demotion. This does NOT fabricate destinations:

  - If a dead /pages/<slug> target has a clear existing equivalent (stale
    slug, e.g. ...-2026-free-paid-options vs ...-in-2026-free-paid), the
    link is RETARGETED to the real page (link value preserved).
  - Otherwise the <a> is UNWRAPPED to its plain anchor text (dead link
    removed, words kept). No invented URLs.

Decision per dead target is made ONCE, globally, for consistency.
Idempotent — re-running finds no remaining dead targets.
"""
from pathlib import Path
from difflib import get_close_matches
import re
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
REDIRECTS = ROOT / "site" / "_redirects"

INTERNAL_HREF = re.compile(
    r'href="(?:https?://saaspare\.org)?/pages/([a-z0-9\-]+)"'
)

# Format/year/connector tokens that may differ between two slugs WITHOUT
# changing which tool/comparison the page is about. Everything NOT in this
# set is an "entity" token (tool name, comparison subjects) and MUST match
# exactly for a retarget — otherwise we'd link to a different product.
NOISE = {
    "7", "in", "2024", "2025", "2026",
    "free", "paid", "options", "ranked",
    "which", "is", "best", "better",
    "software", "tool", "tools", "seo",
}


def entity_key(slug: str) -> frozenset:
    return frozenset(t for t in slug.split("-") if t not in NOISE)


def load_existing_slugs():
    return {p.stem for p in PAGES.glob("*.html")}


def load_redirect_sources():
    srcs = set()
    if REDIRECTS.exists():
        for line in REDIRECTS.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                src = parts[0]
                if src.startswith("/pages/"):
                    srcs.add(src[len("/pages/"):])
    return srcs


def collect_dead_targets(existing, redirect_srcs):
    """Scan every page; return set of dead /pages/<slug> targets."""
    dead = Counter()
    for p in PAGES.glob("*.html"):
        html = p.read_text(encoding="utf-8", errors="replace")
        for slug in INTERNAL_HREF.findall(html):
            if slug in existing or slug in redirect_srcs:
                continue
            dead[slug] += 1
    return dead


def decide(dead_slugs, existing):
    """target slug -> ('retarget', new_slug) or ('unwrap', None).

    Two retarget rules, both of which preserve the core safety property:
    never map one product (or page type) onto a different one.

    1. Exact entity-key match - the existing page differs only in
       format/year/connector wording.
    2. Unique superset - the dead slug's entity key is a strict subset of
       exactly ONE existing page's key. A truncated link like
       `nordvpn-pricing-2026` is unambiguously the same page as
       `nordvpn-pricing-2026-plans-costs-what-you-actually-pay`; the tool
       AND the page type both still have to match, and if two or more pages
       could absorb the link (e.g. a bare `salesforce`, which fits pricing,
       review and coupon alike) it stays ambiguous and we unwrap instead.
       Without this rule a truncated link to a live money page had its
       equity thrown away rather than redirected to the real page.
    """
    # Index existing pages by entity key.
    by_entity = {}
    for s in existing:
        by_entity.setdefault(entity_key(s), []).append(s)

    plan = {}
    for slug in dead_slugs:
        ek = entity_key(slug)
        cands = [c for c in by_entity.get(ek, []) if c != slug]
        if cands:
            # Tiebreak (rare): closest textual match.
            best = get_close_matches(slug, cands, n=1, cutoff=0.0) or cands
            plan[slug] = ("retarget", best[0])
            continue

        # Rule 2: unique strict superset.
        supersets = [
            c for k, group in by_entity.items()
            if ek < k
            for c in group
            if c != slug
        ]
        if len(supersets) == 1:
            plan[slug] = ("retarget", supersets[0])
        else:
            plan[slug] = ("unwrap", None)
    return plan


def apply_to_page(html, plan):
    changed = False
    for slug, (action, new) in plan.items():
        if f"/pages/{slug}" not in html:
            continue
        if action == "retarget":
            # Swap the dead slug for the real one inside the href only.
            new_html = re.sub(
                r'(href="(?:https?://saaspare\.org)?/pages/)' + re.escape(slug) + r'(")',
                lambda mm: mm.group(1) + new + mm.group(2),
                html,
            )
        else:
            # Unwrap <a ...href=".../pages/slug"...>TEXT</a> -> TEXT
            new_html = re.sub(
                r'<a\b[^>]*href="(?:https?://saaspare\.org)?/pages/'
                + re.escape(slug) + r'"[^>]*>(.*?)</a>',
                lambda mm: mm.group(1),
                html,
                flags=re.DOTALL,
            )
        if new_html != html:
            html = new_html
            changed = True
    return html, changed


def main():
    existing = load_existing_slugs()
    redirect_srcs = load_redirect_sources()
    dead = collect_dead_targets(existing, redirect_srcs)
    if not dead:
        print("No dead internal links found. Nothing to do.")
        return

    plan = decide(set(dead), existing)
    retargets = {s: n for s, (a, n) in plan.items() if a == "retarget"}
    unwraps = [s for s, (a, _) in plan.items() if a == "unwrap"]

    print(f"Dead targets: {len(dead)}  | retarget: {len(retargets)}  unwrap: {len(unwraps)}")
    print("\nSample retargets:")
    for s, n in list(retargets.items())[:12]:
        print(f"  {s}\n    -> {n}")
    print("\nSample unwraps (no equivalent page exists):")
    for s in unwraps[:12]:
        print(f"  {s}")

    pages_changed = 0
    for p in PAGES.glob("*.html"):
        html = p.read_text(encoding="utf-8", errors="replace")
        new_html, changed = apply_to_page(html, plan)
        if changed:
            p.write_text(new_html, encoding="utf-8")
            pages_changed += 1
    print(f"\nPages rewritten: {pages_changed}")


if __name__ == "__main__":
    main()
