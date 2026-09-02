"""
validate_pricing_data.py — integrity gate for data/pricing_seed.json.

Why this exists: on 2026-09-02 an audit found ahrefs/Enterprise stored as
monthly_usd=14990 when its own note read "$14,990 billed annually only".
Anything computing a real monthly cost from that would have published
"$74,950/month" (14990 x the 5-seat minimum). Published pricing is the one
asset where being wrong is worse than being silent, so bad rows must fail
the build rather than reach a page.

HARD failures (exit 1):
  - annual_usd < monthly_usd            (impossible)
  - monthly_usd equals annual_usd on an annual-only plan (the annual
    figure copied into the monthly field - the ahrefs/Enterprise signature)
  - negative or absurd values

SOFT warnings (exit 0, reported):
  - annual/monthly ratio outside 8-13x. Legitimate annual discounts land
    around 8-10x, so this flags oddities without blocking - ClickUp at 7.6x
    is a real discount, not an error.

Run:  uv run python scripts/validate_pricing_data.py
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "pricing_seed.json"
ANNUAL_ONLY = re.compile(r"annual(ly)?[^.]{0,30}only|billed annually only", re.I)
MAX_SANE_MONTHLY = 10_000


def main() -> int:
    data = json.loads(SEED.read_text(encoding="utf-8"))
    hard: list[str] = []
    soft: list[str] = []

    for tool in data["tools"]:
        for plan in tool["plans"]:
            tag = f"{tool['tool']}/{plan['plan']}"
            m, a = plan.get("monthly_usd"), plan.get("annual_usd")
            notes = plan.get("notes") or ""

            for label, val in (("monthly_usd", m), ("annual_usd", a)):
                if val is not None and val < 0:
                    hard.append(f"{tag}: negative {label} ({val})")
            if m is not None and m > MAX_SANE_MONTHLY:
                hard.append(f"{tag}: monthly_usd {m} exceeds sane ceiling "
                            f"{MAX_SANE_MONTHLY} - is this an annual figure?")
            if m and a and a < m:
                hard.append(f"{tag}: annual_usd {a} < monthly_usd {m}")
            # An "annual only" note describes billing cadence, not a bad
            # number: Salesforce Pro Suite is legitimately $110/mo effective,
            # $1,200/yr, just not purchasable month-to-month. The real error
            # signature is an annual figure duplicated into monthly_usd, which
            # makes the two fields equal (ahrefs/Enterprise: both 14990).
            if m and a and m == a and ANNUAL_ONLY.search(notes):
                hard.append(f"{tag}: monthly_usd == annual_usd ({m}) with an "
                            f"annual-only note - the annual figure has been "
                            f"copied into monthly_usd; set monthly_usd to null")
            if m and a and m > 0:
                ratio = a / m
                if not (8 <= ratio <= 13):
                    soft.append(f"{tag}: annual/monthly ratio {ratio:.1f}x "
                                f"(m={m} a={a})")

            seats = plan.get("seat_minimum")
            if seats is not None and (seats < 1 or seats > 100):
                hard.append(f"{tag}: implausible seat_minimum {seats}")

    plans = sum(len(t["plans"]) for t in data["tools"])
    print(f"=== validate_pricing_data === {len(data['tools'])} tools, {plans} plans")
    for w in soft:
        print(f"  WARN  {w}")
    for e in hard:
        print(f"  FAIL  {e}")
    print(f"  hard failures: {len(hard)} | warnings: {len(soft)}")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
