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
     "Every tier shows a number instead of a contact-sales form."),
    ("no_setup_fee", "No mandatory setup fee",
     "No required one-time onboarding or implementation charge."),
    ("single_seat", "Will sell you one seat",
     "No minimum seat count standing between you and the advertised price."),
    ("monthly_billing", "Lets you pay monthly",
     "Paid tiers can be bought month to month, not annual commitment only."),
    ("free_tier", "Has a free tier",
     "A genuinely free plan you can stay on, not just a countdown trial."),
    ("trial_no_card", "Trial without a card",
     "You can try it without handing over card details first."),
    ("fair_annual_gap", "Monthly billing isn't punished",
     "The premium for paying monthly instead of yearly stays under 25%."),
    ("seats_at_list", "Extra seats at list price",
     "Adding a colleague costs the advertised per-seat price, with no surcharge."),
    ("price_is_the_bill", "The price is the whole bill",
     "No usage or transaction charges metered on top of the published plan price."),
    ("no_intro_cliff", "No intro-price cliff",
     "The advertised entry price is the real one, not a promotion that expires."),
]

def load():
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    hidden = json.loads(HIDDEN.read_text(encoding="utf-8"))
    return seed, {
        "fees": {r["vendor"].lower() for r in hidden["onboarding_fees"]},
        "annual_only": {r["vendor"].lower() for r in hidden["annual_only"]},
        "seat_surcharge": {r["vendor"].lower() for r in hidden["extra_seat_costs"]},
        "metered": {r["vendor"].lower() for r in hidden["metered_on_top"]["vendors"]},
        "intro": {r["vendor"].lower() for r in hidden["intro_price_step_up"]["vendors"]},
    }


def score_tool(tool, flags):
    plans = tool["plans"]
    vendor = tool["vendor_name"].lower()
    fee_vendors = flags["fees"]
    annual_only_vendors = flags["annual_only"]
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

    # 3. Seat minimums, judged at the ENTRY point: the cheapest paid plan.
    #    Using max() across all plans was wrong - it scored Calendly and Zapier
    #    as if you cannot buy one seat, when in fact only their Enterprise tier
    #    carries a minimum and anyone can start with a single seat. The question
    #    this criterion asks is "will they sell you one seat", so the answer
    #    lives at the cheapest paid tier, not the most expensive.
    entry = min(paid, key=lambda p: p.get("monthly_usd") or p.get("annual_usd") or 0)         if paid else None
    seat_min = (entry.get("seat_minimum") or 1) if entry else 1
    s["single_seat"] = 2 if seat_min <= 1 else (1 if seat_min <= 3 else 0)

    # 4. Monthly billing. A plan priced annually with no monthly option locks
    #    up a year of cash on day one.
    locked = [p for p in paid if not (p.get("monthly_usd") or 0) > 0]
    if vendor in annual_only_vendors or locked:
        s["monthly_billing"] = 0 if len(locked) >= max(1, len(paid) // 2) else 1
    else:
        s["monthly_billing"] = 2

    # 5. A free tier you can stay on is worth more than a countdown trial.
    has_free = any(p.get("monthly_usd") == 0 for p in plans)
    has_trial = any(p.get("free_trial") for p in plans)
    s["free_tier"] = 2 if has_free else (1 if has_trial else 0)

    # 6. Card-up-front on a "free" trial is the oldest dark pattern there is.
    trials = [p for p in plans if p.get("free_trial")]
    if not trials and not has_free:
        s["trial_no_card"] = 0
    elif any(p.get("cc_required") for p in trials):
        s["trial_no_card"] = 0 if all(p.get("cc_required") for p in trials) else 1
    else:
        s["trial_no_card"] = 2

    # 7. How hard monthly buyers are punished. A discount for committing is
    #    fair; charging 186% more to stay flexible is a penalty, not a discount.
    gaps = []
    for p in paid:
        m, a = p.get("monthly_usd"), p.get("annual_usd")
        if m and a and a > 0:
            gaps.append((m * 12 - a) / a)
    worst = max(gaps) if gaps else 0
    s["fair_annual_gap"] = 2 if worst <= 0.25 else (1 if worst <= 0.60 else 0)

    # 8. Per-seat surcharges on top of the plan price.
    s["seats_at_list"] = 0 if vendor in flags["seat_surcharge"] else 2

    # 9. Metered usage on top of a seat price. A vendor with no seat price at
    #    all (Stripe, Wave) is not penalised - there the percentage IS the
    #    advertised price, so nothing is hidden behind it.
    s["price_is_the_bill"] = 0 if vendor in flags["metered"] else 2

    # 10. Intro-price cliffs. The discount is always disclosed; what buyers
    #     miss is that the bill rises sharply on a known date.
    s["no_intro_cliff"] = 0 if vendor in flags["intro"] else 2

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
        # Headline is a /10 score to one decimal. Twenty points gives 21
        # distinct values; the old half-star scale gave nine and piled 24 of
        # 41 tools onto 4.5, which read as flattery rather than a rating.
        "score10": round(total / (len(CRITERIA) * 2) * 10, 1),
        # Stars stay as the visual, at half-star resolution.
        "stars": round(total / (len(CRITERIA) * 2) * 5 * 2) / 2,
        "worst_annual_gap_pct": round(worst * 100),
    }


def main():
    seed, flags = load()
    scores = [score_tool(t, flags) for t in seed["tools"]]
    scores.sort(key=lambda x: (-x["points"], x["vendor"]))

    payload = {
        "_meta": {
            "generated_from": ["data/pricing_seed.json", "data/hidden_costs.json"],
            "pricing_verified_on": seed["_meta"]["snapshot_date"],
            "facts_verified_on": json.loads(HIDDEN.read_text(encoding="utf-8"))["_meta"]["verified_on"],
            "scale": "10 criteria, 0-2 points each, 20 points total, reported as a score out of 10 to one decimal; stars are the visual at half-star resolution",
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
