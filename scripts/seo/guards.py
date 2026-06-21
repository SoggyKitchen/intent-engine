"""
Autonomous-operator safety guards.

The apply-safe engine regenerates metadata from templates. Run unguarded, it
overwrites hand-tuned titles/metas with generic templated ones — a regression.
These guards make autonomous metadata changes *only-improve*:

  * title_quality_score / meta_quality_score — score a string by the SaaSpare
    title/meta formulas (length, year, specificity signals, generic-filler
    penalty). Higher = better.
  * is_generic — detects boilerplate-templated strings ("which software is
    best", bare "| SaaSpare" filler, etc.).
  * should_replace — the gate apply-safe must pass before overwriting: never
    downgrade, never replace a specific string with a generic one, only touch a
    strong existing value if the candidate is clearly better.
  * is_premium_page — a page that is already well-optimized; autonomous runs
    skip its metadata entirely (structural fixes still allowed).

Pure functions, no I/O — unit-tested in tests/test_seo_guards.py.
"""
from __future__ import annotations

import re

# Specificity / buyer-intent signals that make a title earn the click.
_TITLE_SIGNALS = (
    "honest", "verdict", "tested", "real cost", "actually", "every change",
    "explained", "step by step", "verified", "worth it", "free plan",
    "free trial", "% off", "update", "compared", "review", "alternatives",
)

# Generic templated filler — the homogenized output we must never ship over a
# more specific human/curated title. These are the exact stable fragments of the
# bot_patterns.csv templates (after X/Y/[Category] substitution), so any string
# containing one IS machine-generated template output.
_GENERIC_MARKERS = (
    # ── title templates ──
    "alternatives 2026: free & paid options",
    "pricing 2026: plans & costs",
    "free trial 2026: length, limits",
    "free plan 2026: limits & what you get",
    "review 2026: honest pricing & verdict",
    "promo codes & discounts 2026",
    "in 2026: unbiased comparisons",
    # ── meta templates ──
    "and real user verdict. find out which is right for your team",
    "so you can switch with confidence",
    "hidden fees, and true costs for teams",
    "trial length, card requirements",
    "so you know before signing up",
    "real pricing breakdown, honest pros and cons",
    "verified deals, annual plan savings",
    "expert picks to help you decide faster",
    # ── older generic filler ──
    "which software is best",
    "everything you need to know",
    "complete guide",
    "the ultimate guide",
    "all you need to know",
)

# The "X vs. Y: Which [Category] Is Best in 2026?" comparison template — the
# category word varies, so match it as a pattern.
_GENERIC_VS_RE = re.compile(r"\bwhich\b.{0,40}?\bis best\b", re.I)

# How deficient a current value must be before a template candidate may
# overwrite it. At/above this, we keep the human title.
DEFICIENT_TITLE = 34.0
DEFICIENT_META = 34.0

_YEAR_RE = re.compile(r"\b20\d{2}\b")
_NUM_PREFIX_RE = re.compile(r"^\s*\d+\s+best", re.I)

# Thresholds (0–100 scale). A page whose current title scores at/above
# STRONG_TITLE is "good enough"; we only overwrite it for a clearly better one.
STRONG_TITLE = 60.0
STRONG_META = 60.0
IMPROVE_MARGIN = 8.0   # candidate must beat a strong current by this much


def _norm(s: str | None) -> str:
    return " ".join((s or "").replace("\n", " ").split())


def is_generic(text: str | None) -> bool:
    """True if the string reads like boilerplate template output."""
    low = _norm(text).lower()
    if not low:
        return False
    if any(m in low for m in _GENERIC_MARKERS):
        return True
    if _GENERIC_VS_RE.search(low):
        return True
    # Bare "Foo | SaaSpare" with nothing else specific (no year, no signal).
    if low.endswith("| saaspare"):
        core = low.rsplit("|", 1)[0].strip()
        has_signal = any(sig in core for sig in _TITLE_SIGNALS) or bool(_YEAR_RE.search(core))
        if not has_signal and len(core) < 35:
            return True
    return False


def title_quality_score(title: str | None) -> float:
    """Score a title 0–100 by the SaaSpare title formula."""
    t = _norm(title)
    if not t:
        return 0.0
    score = 0.0
    length = len(t)

    # Length: ideal 35–60 chars. Penalize too-short and too-long.
    if 35 <= length <= 60:
        score += 30
    elif 28 <= length < 35:
        score += 22
    elif 60 < length <= 70:
        score += 18
    elif length > 70:
        score += 6
    else:  # < 28
        score += 10

    # Year present (freshness signal).
    if _YEAR_RE.search(t):
        score += 18

    # Buyer-intent / specificity signals (cap the bonus).
    low = t.lower()
    sig_hits = sum(1 for sig in _TITLE_SIGNALS if sig in low)
    score += min(sig_hits, 3) * 10

    # "N best ..." listicle prefix is a strong CTR pattern.
    if _NUM_PREFIX_RE.search(t):
        score += 8

    # Penalties.
    if is_generic(t):
        score -= 30
    # Bare boilerplate suffix with no substance.
    if low.endswith("| saaspare") and not _YEAR_RE.search(low) and sig_hits == 0:
        score -= 8

    return max(0.0, min(100.0, score))


def meta_quality_score(meta: str | None) -> float:
    """Score a meta description 0–100 (length sweet spot + answer-first + year)."""
    m = _norm(meta)
    if not m:
        return 0.0
    score = 0.0
    length = len(m)

    # Ideal 120–158 chars.
    if 120 <= length <= 158:
        score += 40
    elif 100 <= length < 120:
        score += 30
    elif 158 < length <= 165:
        score += 22
    elif 70 <= length < 100:
        score += 18
    elif length > 165:
        score += 6
    else:
        score += 8

    low = m.lower()
    if _YEAR_RE.search(m):
        score += 15
    sig_hits = sum(1 for sig in _TITLE_SIGNALS if sig in low)
    score += min(sig_hits, 3) * 8
    # Answer-first openers.
    if low.startswith(("yes", "no", "$")) or re.match(r"^\$?\d", m):
        score += 8
    if is_generic(m):
        score -= 20

    return max(0.0, min(100.0, score))


def should_replace(current: str | None, candidate: str | None, kind: str = "title") -> bool:
    """
    The only-improve gate. Return True only if overwriting `current` with
    `candidate` is a genuine improvement.

    Rules (in order):
      1. No candidate → never replace.
      2. No current → always set it.
      3. Never replace a specific value with a generic templated one.
      4. If current is already strong → require candidate to beat it by a margin.
      5. Otherwise → replace only if candidate scores strictly higher.
    """
    cand = _norm(candidate)
    cur = _norm(current)
    if not cand:
        return False
    if not cur:
        return True
    # Identical (ignoring whitespace) → no-op.
    if cand == cur:
        return False

    scorer = title_quality_score if kind == "title" else meta_quality_score
    deficient = DEFICIENT_TITLE if kind == "title" else DEFICIENT_META

    # Rule 3: a generic template candidate may ONLY fill an empty value
    # (handled above). It must never overwrite an existing title/meta — not a
    # specific one, and not even another generic one (that's churn, and on
    # utility/preview pages it produces nonsense like
    # "Page not found" → "404 Review 2026: Honest Pricing & Verdict").
    if is_generic(cand):
        return False

    cur_score = scorer(cur)
    cand_score = scorer(cand)

    # Rule 4: the current value is a real, non-deficient human/curated string.
    # Be conservative — require a large, unambiguous win to overwrite it.
    if cur_score >= deficient and not is_generic(cur):
        return cand_score >= cur_score + IMPROVE_MARGIN

    # Rule 5: current is deficient (too short, no signals, or itself generic)
    # and the candidate is non-generic — adopt it if it scores strictly higher.
    return cand_score > cur_score


def is_premium_page(
    title: str | None,
    meta: str | None,
    word_count: int = 0,
    has_faq_schema: bool = False,
) -> bool:
    """
    A page already optimized to a high standard. Autonomous metadata rewrites
    skip these entirely so hand-tuned money pages are never homogenized.
    Structural fixes (broken links, alt text, org schema) still apply.
    """
    if title_quality_score(title) < STRONG_TITLE:
        return False
    if meta_quality_score(meta) < STRONG_META:
        return False
    if word_count and word_count < 600:
        return False
    return True
