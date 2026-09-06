"""
Remove fabricated first-hand-testing claims from the site AND the generators.

CLAUDE.md rule 1 forbids fabricated hands-on claims. A 2026-09-06 audit found
them still shipping on 29 indexable pages, with the generators re-emitting them
nightly. The worst offenders invented a sample size or named testing tools we
have never run:

    "<claim> 24 CRM platforms across 47 data points"
    "<claim> send reputation, inbox placement, and spam trigger rates
     using MailTester and GlockApps"
    "Lightway protocol delivers the lowest latency of any VPN <claim>"

We have never run usability, deliverability or latency testing. What we do is
read vendor pricing pages and documentation and compare them. Claiming
otherwise fabricates the first-hand-experience signal Google's guidance rewards
honestly, and is the kind of statement the FTC and ACCC treat as deceptive.

Fixing the HTML alone is not enough - the generators rebuild it - so both are
swept.

Two files are exempt, and must stay exempt:
  - this script, which has to quote the offending phrase in order to replace it
  - scripts/trust_pass.py, where the phrase is a DETECTOR guarding against
    exactly this problem
An earlier version exempted them only during verification, not during the
sweep, so the script rewrote its own replacement table into no-ops.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Assembled from fragments so this file cannot match its own pattern.
WT = "We " + "tested"
wt = "we " + "tested"

EXEMPT = {"strip_fabricated_testing_claims.py", "trust_pass.py"}

# Specific fabrications, longest first. Invented counts and named tools are
# replaced with what we can actually stand behind, not softened in place.
EXACT = [
    # Wholly invented methodologies. These describe physical actions - network
    # connections, stopwatch timings, hardware benchmarks - that we have never
    # performed. There is no honest rewording, so the claim is replaced with
    # what we genuinely do.
    ("We compared each VPN on a UK IP connecting to Netflix US, Netflix UK, BBC iPlayer, "
     "Disney+, Hulu, and HBO Max. We checked: (1) whether the platform unblocked at all, "
     "(2) whether video quality dropped vs unprotected connection, (3) connection "
     "stability over a 2-hour stream. Tests were repeated monthly.",
     "We compare each VPN on what its provider publishes and documents: which streaming "
     "platforms it states it supports, its advertised server counts and locations, its "
     "protocol options, and its real pricing including renewal rates. We do not run "
     "streaming tests, so we do not report unblocking results as our own findings."),
    ("We measured time-to-first-live-product for a non-technical user",
     "We compared documented setup steps and onboarding requirements"),
    ("We measured time-to-first-campaign for a non-technical user",
     "We compared documented setup steps and onboarding requirements"),
    ("We benchmarked CPU performance, I/O speeds, network latency, and true monthly pricing",
     "We compared published CPU and storage specifications, stated network capacity, "
     "and true monthly pricing including renewal rates"),
    ("How We Tested", "How We Compare Tools"),
    (f"{WT} 24 CRM platforms across 47 data points — pricing, features, support, "
     "real buyer feedback, and ROI signal. Here's who actually wins.",
     "We compared 24 CRM platforms on published pricing, plan limits and documented "
     "features. Here's how they stack up."),
    (f"{WT} 24 CRM platforms across 47 data points.",
     "We compared 24 CRM platforms on published pricing and plan limits."),
    (f"{WT} send reputation, inbox placement, and spam trigger rates using "
     "MailTester and GlockApps",
     "We compared documented sending limits, authentication support and "
     "deliverability features"),
    (f"{WT} free tiers for real-world usability — not just lead generation tools",
     "We compared what each free tier actually includes against its paid tiers"),
    (f"{WT} free tiers for real-world usability, not just lead generation tools",
     "We compared what each free tier actually includes against its paid tiers"),
    (f"Lightway protocol delivers the lowest latency of any VPN {wt}",
     "ExpressVPN publishes Lightway as its lowest-latency protocol"),
    (f"{WT} every feature, pricing, and support.",
     "We reviewed published features, pricing and support tiers."),
    (f"{WT} AI voice cloning, TTS quality, and pricing.",
     "We reviewed published voice-cloning limits, output formats and pricing."),
    (f"{WT} pricing, features & support",
     "We compared published pricing, features and support tiers"),
]

PATTERNS = [
    (re.compile(rf"\b{WT} every major ([^.<]{{0,90}}?) for ([^.<]{{0,120}}?)\."),
     r"We compared every major \1 on \2, using published pricing and documentation."),
    (re.compile(rf"\b{WT} every major ([^.<]{{0,90}}?) across ([^.<]{{0,120}}?)\."),
     r"We compared every major \1 across \2, using published pricing and documentation."),
    (re.compile(rf"\b{WT} every major ([^.<]{{0,90}}?)\."), r"We compared every major \1."),
    (re.compile(rf"\b{WT} every ([^.<]{{0,90}}?)\."), r"We compared every \1."),
    (re.compile(rf"\b{WT} the top ([^.<]{{0,120}}?)\."), r"We compared the top \1."),
    (re.compile(rf"\b{WT} (\d+) ([^.<]{{0,120}}?)\."), r"We compared \1 \2."),
    (re.compile(rf"\b{WT} ([^.<]{{0,120}}?)\."), r"We compared \1."),
    (re.compile(rf"\b{wt}\b"), "we compared"),
    (re.compile(rf"\b{WT}\b"), "We compared"),
    (re.compile(r"Independent Review &middot; Tested \{TODAY\}"),
     "Independent Review &middot; Pricing verified {TODAY}"),
    (re.compile(r"Tested by SaaS experts"), "Pricing verified against vendor pages"),
    (re.compile(r"How We Tested", re.IGNORECASE), "How We Compare Tools"),
]


def clean(text):
    for a, b in EXACT:
        text = text.replace(a, b)
    for rx, rep in PATTERNS:
        text = rx.sub(rep, text)
    return text


def sweep(paths, label):
    changed = 0
    for p in paths:
        if p.name in EXEMPT:
            continue
        try:
            original = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        new = clean(original)
        if new != original:
            p.write_text(new, encoding="utf-8")
            changed += 1
    print(f"{label}: {changed} files rewritten")


def main():
    sweep(sorted((ROOT / "site").rglob("*.html")), "site HTML")
    sweep(sorted((ROOT / "scripts").glob("*.py")), "generators")
    tpl = ROOT / "outputs" / "templates"
    sweep(sorted(tpl.glob("*.html")) if tpl.exists() else [], "templates")

    rx = re.compile(rf"{wt}", re.IGNORECASE)
    leftovers = [
        str(p.relative_to(ROOT))
        for p in list((ROOT / "site").rglob("*.html")) + list((ROOT / "scripts").glob("*.py"))
        if p.name not in EXEMPT
        and rx.search(p.read_text(encoding="utf-8", errors="replace"))
    ]
    print(f"VERIFY  remaining fabricated testing claims: {len(leftovers)}")
    for f in leftovers[:10]:
        print("  " + f)
    if leftovers:
        raise SystemExit("strip_fabricated_testing_claims: did not converge")


if __name__ == "__main__":
    main()
