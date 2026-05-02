"""Build all SaaSpare strategic, trust, utility, and info pages.

Each module under scripts/strategic/ owns a small set of pages and writes
them to the site/ directory.

Run:  uv run python scripts/build_strategic_pages.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from strategic import (  # noqa: E402
    stack_audit, digest, tracker, state_report, glossary, trust, utility, info_pages,
)


BUILDERS = [
    ("SaaS Stack Audit", stack_audit.build),
    ("Stack Audit Checkout", stack_audit.build_checkout),
    ("Weekly Deal Digest", digest.build),
    ("Pricing Changes Tracker", tracker.build),
    ("State of SaaS Pricing 2026", state_report.build),
    ("SaaS Glossary", glossary.build),
    ("Coupon Verification Policy", trust.build_coupon_policy),
    ("How We Rank", trust.build_rank_methodology),
    ("Request a Comparison", utility.build_request),
    ("Report Outdated Pricing", utility.build_report_pricing),
    ("About SaaSpare", info_pages.build_about),
    ("Privacy Policy", info_pages.build_privacy),
]


def main() -> None:
    print(f"Building {len(BUILDERS)} strategic pages...\n")
    for name, fn in BUILDERS:
        try:
            fn()
            print(f"  [OK]   {name}")
        except Exception as exc:  # noqa: BLE001
            print(f"  [FAIL] {name}: {exc}")
            raise
    print("\nAll strategic pages built.")


if __name__ == "__main__":
    main()
