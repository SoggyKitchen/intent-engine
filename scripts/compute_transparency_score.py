"""
SaaSpare Cost Transparency Score - our own editorial rating, computed, not typed.

Why not user-review stars
-------------------------
The obvious move is to copy the competitor and show star ratings from user
reviews. Two problems, both fatal:

  1. Google's structured-data policy is explicit: "Don't aggregate reviews or
     ratings from other websites", and ratings "must be sourced directly from
     users". Marking up G2 or Capterra numbers as our own aggregateRating
     invites a structured-data manual action. We currently have none, and that
     clean record is worth more than a star widget.
  2. We have no users leaving reviews, so any first-party rating would be
     invented. That is the one thing this project never does.

What Google DOES allow is an editorial review: a rating authored by the
publisher, of the kind Which? or Wirecutter publish. That is legitimate as
schema.org Review with author = our Organization, and it is defensible because
every input is a fact we have already verified and published.

So the score measures the one thing we can actually evidence: how honest a
vendor's pricing page is with the buyer. Five criteria, 0-2 each, 10 points
total, halved to a 0-5 star rating. Every point traces to a field in
data/pricing_seed.json or data/hidden_costs.json.

This is deterministic. Same data in, same score out, every time - so the score
cannot drift on a whim, and a vendor who fixes their pricing page earns a
higher score automatically.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "pricing_seed.json"
HIDDEN = ROOT / "data" / "hidden_costs.json"
OUT = ROOT / "data" / "transparency_scores.json"

CRITERIA = [
    ("published_pricing", "Publishes a real price",
     "Every paid tier shows a number instead of a contact-sales form."),
    ("no_setup_fee", "No mandatory setup fee",
     "No required one-time onboarding or implementation charge."),
    ("single_seat", "Will sell you one seat",
     "No minimum seat count standing between you and the advertised price."),
    ("monthly_billing", "Lets you pay monthly",
     "Paid tiers can be bought month to month, not annual commitment only."),
    ("try_before_buy", "Try before you buy",
     "A free tier, or at minimum a free trial."),
]


def load():
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    hidden = json.loads(HIDDEN.read_text(encoding="utf-8"))
    fees = {r["vendor"].lower() for r in hidden["onboarding_fees"]}
    annual_only = {r["vendor"].lower() for r in hidden["annual_only"]}
    return seed, fees, annual_only


def score_tool(tool, fee_vendors, annual_only_vendors):
    plans = tool["plans"]
    vendor = tool["vendor_name"].lower()
    paid = [p for p in plans
            if (p.get("monthly_usd") or 0) > 0 or (p.get("annual_usd") or 0) > 0]
    quote_only = [p for p in plans
                  if p.get("monthly_usd") is None and p.get("annual_usd") is None]

    s = {}

    # 1. Published pricing. Quote-only tiers are the buyer's problem, so they
    #    cost points in proportion to how much of the range they hide.
    if not quote_only:
        s["published_pricing"] = 2
    elif len(quote_only) < max(1, len(plans) // 2):
        s["published_pricing"] = 1
    else:
        s["published_pricing"] = 0

    # 2. Mandatory one-time fees. Binary: either the buyer is ambushed or not.
    s["no_setup_fee"] = 0 if vendor in fee_vendors else 2

    # 3. Seat minimums.
    seat_min = max((p.get("seat_minimum") or 1) for p in plans)
    s["single_seat"] = 2 if seat_min <= 1 else (1 if seat_min <= 3 else 0)

    # 4. Monthly billing. A plan priced annually with no monthly option locks
    #    up a year of cash on day one.
    locked = [p for p in paid if not (p.get("monthly_usd") or 0) > 0]
    if vendor in annual_only_vendors or locked:
        s["monthly_billing"] = 0 if len(locked) >= max(1, len(paid) // 2) else 1
    else:
        s["monthly_billing"] = 2

    # 5. Free tier beats free trial beats nothing.
    has_free = any(p.get("monthly_usd") == 0 for p in plans)
    has_trial = any(p.get("free_trial") for p in plans)
    s["try_before_buy"] = 2 if has_free else (1 if has_trial else 0)

    total = sum(s.values())
    return {
        "tool": tool["tool"],
        "vendor": tool["vendor_name"],
        "category": tool.get("category"),
        "source_url": tool.get("source_url"),
        "affiliate_slug": tool.get("affiliate_slug"),
        "criteria": s,
        "points": total,
        "max_points": len(CRITERIA) * 2,
        # Half-star resolution, which is as fine as a 10-point scale honestly
        # supports. Reporting 4.37 stars off ten integer points is false
        # precision.
        "stars": round(total / 2 * 2) / 2,
    }


def main():
    seed, fees, annual_only = load()
    scores = [score_tool(t, fees, annual_only) for t in seed["tools"]]
    scores.sort(key=lambda x: (-x["points"], x["vendor"]))

    payload = {
        "_meta": {
            "generated_from": ["data/pricing_seed.json", "data/hidden_costs.json"],
            "pricing_verified_on": seed["_meta"]["snapshot_date"],
            "facts_verified_on": json.loads(HIDDEN.read_text(encoding="utf-8"))["_meta"]["verified_on"],
            "scale": "5 criteria, 0-2 points each, 10 points total, halved to 0-5 stars",
            "authored_by": "SaaSpare editorial",
            "note": ("Editorial score, not user reviews. Measures how transparent a "
                     "vendor's own pricing page is with the buyer. Deterministic: "
                     "recomputed from verified data, never hand-set."),
            "criteria": [{"key": k, "label": lbl, "test": t} for k, lbl, t in CRITERIA],
        },
        "scores": scores,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"{'vendor':16} {'pts':>4} {'stars':>6}   breakdown")
    for s in scores:
        b = " ".join(f"{k.split('_')[0][:5]}={v}" for k, v in s["criteria"].items())
        print(f"{s['vendor']:16} {s['points']:>4} {s['stars']:>6}   {b}")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
