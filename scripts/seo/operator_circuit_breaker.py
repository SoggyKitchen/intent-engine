"""
Autonomous-operator circuit breaker.

Before the cloud operator pushes apply-safe changes to the live site, this
counts how many <title> and <meta name="description"> values changed in the
working tree. The only-improve guards (guards.py) should keep this near zero.
A spike means a guard regression (like the one that homogenized 1458 pages) —
so we ABORT the push instead of shipping a mass downgrade.

Exit 0  → safe to push (title/meta changes within budget)
Exit 1  → abort: too many metadata changes, human review required

Usage:
    python scripts/seo/operator_circuit_breaker.py [--max-meta-changes N]
"""
from __future__ import annotations

import argparse
import subprocess
import sys

DEFAULT_MAX = 60  # titles + metas combined; structural fixes are not counted


def _git_diff_site() -> str:
    out = subprocess.run(
        ["git", "diff", "--unified=0", "--", "site/**/*.html", "site/*.html"],
        capture_output=True, text=True, encoding="utf-8", errors="ignore",
    )
    return out.stdout or ""


def count_metadata_changes(diff_text: str) -> tuple[int, int]:
    """Return (title_changes, meta_changes) — removed-line counts."""
    titles = 0
    metas = 0
    for line in diff_text.splitlines():
        if line.startswith("-<title") or line.startswith("-  <title"):
            titles += 1
        elif line.startswith('-<meta name="description"') or line.startswith('-  <meta name="description"'):
            metas += 1
    return titles, metas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-meta-changes", type=int, default=DEFAULT_MAX)
    args = ap.parse_args()

    titles, metas = count_metadata_changes(_git_diff_site())
    total = titles + metas
    print(f"[circuit-breaker] title changes={titles} meta changes={metas} total={total} budget={args.max_meta_changes}")

    if total > args.max_meta_changes:
        print(
            f"[circuit-breaker] ABORT — {total} metadata changes exceeds budget "
            f"{args.max_meta_changes}. This indicates a guard regression. "
            "Refusing to push a mass metadata change to the live site. "
            "Human review required."
        )
        return 1

    print("[circuit-breaker] OK — metadata changes within budget, safe to push.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
