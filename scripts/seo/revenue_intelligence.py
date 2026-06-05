"""
SaaSpare Revenue Intelligence — turns SEO data into dollar-ranked priorities.

The SEO engine (seo_agent.py) tells you which pages CAN climb. This layer tells you
which pages are WORTH climbing, by joining three things:

  1. Which affiliate program each page promotes   (from /go/* links + page slug)
  2. What that program pays + whether it's earning (PROGRAM_VALUE table, real data)
  3. GSC impressions / CTR / position               (seo/reports/gsc-opportunities.json)

Outputs:
  - seo/reports/revenue-opportunities.json/.md  — pages ranked by est. monthly $ uplift
  - seo/reports/program-acquisition.md          — UNAPPROVED programs ranked by the
                                                   traffic already landing on their pages
                                                   (i.e. apply to these first)

IMPORTANT — honesty about the model:
  EPC / commission figures are benchmarks from the affiliate networks (see CLAUDE.md),
  not live earnings. Conversion rates and CTR-by-position are MODELLED industry values.
  When the Impact.com API token is supplied (IMPACT_API_TOKEN), real EPC + conversion
  data should replace the modelled values in PROGRAM_VALUE / CONVERSION_RATE.

Run:  uv run python scripts/seo/revenue_intelligence.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOTS = ROOT / "seo" / "snapshots"
REPORTS = ROOT / "seo" / "reports"
REDIRECTS = ROOT / "site" / "_redirects"

# ── CTR by Google position (industry benchmark, modelled) ────────────────────
CTR_BY_POSITION = {
    1: 0.280, 2: 0.150, 3: 0.100, 4: 0.070, 5: 0.050,
    6: 0.040, 7: 0.030, 8: 0.025, 9: 0.020, 10: 0.018,
}

def ctr_for_position(pos: float) -> float:
    if pos <= 0:
        return 0.0
    p = int(round(pos))
    if p in CTR_BY_POSITION:
        return CTR_BY_POSITION[p]
    if p <= 15:
        return 0.015
    if p <= 20:
        return 0.010
    if p <= 30:
        return 0.006
    return 0.003

# ── Modelled conversion rate by page type (buyer intent) ─────────────────────
CONVERSION_RATE = {
    "coupon": 0.030, "pricing": 0.020, "free_trial": 0.022,
    "alternatives": 0.012, "comparison": 0.013, "best_of": 0.011,
    "review": 0.010, "trust": 0.0, "other": 0.005,
}

# ── PROGRAM VALUE TABLE ──────────────────────────────────────────────────────
# value_usd  = representative commission per conversion (USD, midpoint of range)
# status     = EARNING | PENDING | LOCKED | PLACEHOLDER
# Sourced from CLAUDE.md affiliate tables + deep-research benchmarks. Estimated.
PROGRAM_VALUE = {
    # ── Earning now (real network links live) ──
    "nordvpn":        dict(name="NordVPN",        value_usd=60,  status="EARNING", network="Direct/CJ"),
    "surfshark":      dict(name="Surfshark",      value_usd=55,  status="EARNING", network="Direct"),
    "sucuri":         dict(name="Sucuri",         value_usd=70,  status="EARNING", network="Direct"),
    "nordpass":       dict(name="NordPass",       value_usd=40,  status="EARNING", network="Direct"),
    "contabo":        dict(name="Contabo",        value_usd=45,  status="EARNING", network="CJ"),
    "hostpapa":       dict(name="HostPapa",       value_usd=60,  status="EARNING", network="CJ"),
    "semrush":        dict(name="Semrush",        value_usd=200, status="EARNING", network="Impact"),
    "shopify":        dict(name="Shopify",        value_usd=150, status="EARNING", network="Impact"),
    "elevenlabs":     dict(name="ElevenLabs",     value_usd=25,  status="EARNING", network="Direct"),
    # ── CJ active, need deep links ──
    "getresponse":    dict(name="GetResponse",    value_usd=100, status="EARNING", network="CJ"),
    "proton":         dict(name="Proton",         value_usd=60,  status="EARNING", network="CJ"),
    "protonvpn":      dict(name="ProtonVPN",      value_usd=60,  status="EARNING", network="CJ"),
    "elementor":      dict(name="Elementor",      value_usd=40,  status="EARNING", network="CJ"),
    "aweber":         dict(name="AWeber",         value_usd=12,  status="EARNING", network="CJ"),
    "parallels":      dict(name="Parallels",      value_usd=30,  status="EARNING", network="CJ"),
    # ── Pending network approval (pages live, $0 until approved) ──
    "hubspot":        dict(name="HubSpot",        value_usd=400, status="PENDING", network="Impact"),
    "1password":      dict(name="1Password",      value_usd=45,  status="PENDING", network="Impact"),
    "freshbooks":     dict(name="FreshBooks",     value_usd=200, status="PENDING", network="Awin"),
    "xero":           dict(name="Xero",           value_usd=80,  status="PENDING", network="Direct"),
    # ── Locked behind PartnerStack ban (appeal pending) ──
    "clickup":        dict(name="ClickUp",        value_usd=90,  status="LOCKED",  network="PartnerStack"),
    "activecampaign": dict(name="ActiveCampaign", value_usd=85,  status="LOCKED",  network="PartnerStack"),
    "monday":         dict(name="Monday.com",     value_usd=150, status="LOCKED",  network="PartnerStack"),
    "dashlane":       dict(name="Dashlane",       value_usd=38,  status="LOCKED",  network="PartnerStack"),
    # ── Common tools with pages but no program yet (placeholder /go links) ──
    "notion":         dict(name="Notion",         value_usd=15,  status="PLACEHOLDER", network="none"),
    "asana":          dict(name="Asana",          value_usd=15,  status="PLACEHOLDER", network="none"),
    "ahrefs":         dict(name="Ahrefs",         value_usd=100, status="PLACEHOLDER", network="none"),
    "pipedrive":      dict(name="Pipedrive",      value_usd=60,  status="PLACEHOLDER", network="none"),
    "salesforce":     dict(name="Salesforce",     value_usd=120, status="PLACEHOLDER", network="none"),
    "linear":         dict(name="Linear",         value_usd=20,  status="PLACEHOLDER", network="none"),
    "ramp":           dict(name="Ramp",           value_usd=100, status="PLACEHOLDER", network="none"),
    "datadog":        dict(name="Datadog",        value_usd=80,  status="PLACEHOLDER", network="none"),
    "zoom":           dict(name="Zoom",           value_usd=12,  status="PLACEHOLDER", network="none"),
    "slack":          dict(name="Slack",          value_usd=20,  status="PLACEHOLDER", network="none"),
    "canva":          dict(name="Canva",          value_usd=20,  status="PLACEHOLDER", network="none"),
    "mailchimp":      dict(name="Mailchimp",      value_usd=25,  status="PLACEHOLDER", network="none"),
    "deel":           dict(name="Deel",           value_usd=100, status="PLACEHOLDER", network="none"),
    "gusto":          dict(name="Gusto",          value_usd=100, status="PLACEHOLDER", network="none"),
    "rippling":       dict(name="Rippling",       value_usd=120, status="PLACEHOLDER", network="none"),
}

# Slug-prefix aliases → canonical program key
ALIASES = {
    "1password-business": "1password", "1password-trial": "1password",
    "hubspot-crm": "hubspot", "clickup-trial": "clickup",
    "activecampaign-trial": "activecampaign", "freshbooks-trial": "freshbooks",
    "xero-trial": "xero", "dashlane-trial": "dashlane", "monday-com": "monday",
    "eleven-labs": "elevenlabs", "elevenlabs-voice": "elevenlabs", "elevenlabs-ai": "elevenlabs",
    "frase-io": "frase", "copy-ai": "copyai", "proton-vpn": "protonvpn",
}


def load_redirects() -> dict[str, str]:
    """Map /go/<slug> -> destination URL."""
    mapping = {}
    if not REDIRECTS.exists():
        return mapping
    for line in REDIRECTS.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"^(/go/[^\s]+)\s+(\S+)", line.strip())
        if m:
            mapping[m.group(1)] = m.group(2)
    return mapping


# CJ / affiliate-network click-tracker domains = a REAL earning link.
NETWORK_DOMAINS = ("kqzyfj.com", "dpbolvw.net", "anrdoezrs.net", "tkqlhce.com",
                   "jdoqocy.com", "qksrv.net", "click-101733230", "try.elevenlabs.io",
                   "go.nordvpn", "get.surfshark")


def classify_link(dest: str) -> str:
    """REAL (network click tracker) vs PLACEHOLDER (bare brand utm) vs INTERNAL."""
    if not dest:
        return "unknown"
    if dest.startswith("/"):
        return "internal"
    if any(d in dest for d in NETWORK_DOMAINS):
        return "real"
    return "placeholder"


def program_from_slug(slug: str) -> str | None:
    key = slug.replace("/go/", "")
    key = ALIASES.get(key, key)
    if key in PROGRAM_VALUE:
        return key
    # try progressively shorter prefixes (handles -coupon, -business, -2026 etc.)
    parts = key.split("-")
    for i in range(len(parts), 0, -1):
        cand = "-".join(parts[:i])
        cand = ALIASES.get(cand, cand)
        if cand in PROGRAM_VALUE:
            return cand
    return None


def primary_program(page: dict, redirects: dict) -> tuple[str | None, str]:
    """Return (program_key, link_state) for a page's main monetised tool."""
    best = None
    best_state = "unknown"
    # Prefer a /go link whose program matches the page slug subject.
    slug_subject = page.get("path", "").split("/")[-1]
    for link in page.get("affiliate_links", []):
        slug = link.split("?")[0]
        if not slug.startswith("/go/"):
            continue
        prog = program_from_slug(slug)
        if not prog:
            continue
        state = classify_link(redirects.get(slug, ""))
        match_bonus = prog.split("-")[0] in slug_subject
        # pick the program that matches the page subject, else first found
        if best is None or match_bonus:
            best, best_state = prog, state
            if match_bonus:
                break
    return best, best_state


def main() -> int:
    pages_path = SNAPSHOTS / "pages.json"
    if not pages_path.exists():
        print("revenue_intelligence: seo/snapshots/pages.json not found. Run seo_agent.py --mode audit first.")
        return 1
    pages = json.loads(pages_path.read_text(encoding="utf-8"))
    redirects = load_redirects()

    # GSC metrics keyed by page URL (page-rollup rows only).
    gsc_metrics: dict[str, dict] = {}
    gsc_path = REPORTS / "gsc-opportunities.json"
    gsc_live = False
    if gsc_path.exists():
        gsc = json.loads(gsc_path.read_text(encoding="utf-8"))
        gsc_live = not gsc.get("skipped", True)
        for opp in gsc.get("opportunities", []):
            if not opp.get("query"):  # page rollup row
                gsc_metrics[opp["page"].rstrip("/")] = opp

    opportunities = []
    program_traffic: dict[str, dict] = {}

    for page in pages:
        prog_key, link_state = primary_program(page, redirects)
        if not prog_key:
            continue
        prog = PROGRAM_VALUE[prog_key]
        url = page.get("url", "").rstrip("/")
        m = gsc_metrics.get(url, {})
        impressions = float(m.get("impressions", 0))
        position = float(m.get("position", 0))
        clicks = float(m.get("clicks", 0))
        conv_rate = CONVERSION_RATE.get(page.get("page_type", "other"), 0.005)

        # Revenue-uplift model: climb to target position 4 (top of page).
        uplift_rev = 0.0
        extra_clicks = 0.0
        if impressions >= 20 and 5 <= position <= 30:
            target = 4
            cur_ctr = ctr_for_position(position)
            tgt_ctr = ctr_for_position(target)
            # GSC impressions are for the period (~28d); treat as monthly-ish.
            extra_clicks = max(0.0, impressions * (tgt_ctr - cur_ctr))
            extra_conv = extra_clicks * conv_rate
            # Only EARNING programs realise revenue today; others are potential.
            realised = prog["value_usd"] if prog["status"] == "EARNING" else 0.0
            uplift_rev = extra_conv * (realised or prog["value_usd"])

        # Priority score blends realised potential and traffic size.
        status_weight = {"EARNING": 1.0, "PENDING": 0.6, "LOCKED": 0.5, "PLACEHOLDER": 0.4}.get(prog["status"], 0.3)
        score = round(uplift_rev * status_weight + min(impressions, 3000) / 100, 2)

        if uplift_rev > 0 or impressions >= 50:
            opportunities.append({
                "score": score,
                "page": page["path"],
                "program": prog["name"],
                "status": prog["status"],
                "linkState": link_state,
                "valuePerConvUsd": prog["value_usd"],
                "impressions": round(impressions),
                "position": round(position, 1),
                "clicks": round(clicks),
                "estExtraClicksMo": round(extra_clicks, 1),
                "estMonthlyUpliftUsd": round(uplift_rev, 2),
                "pageType": page.get("page_type"),
            })

        # Aggregate traffic by program for the acquisition priority list.
        pt = program_traffic.setdefault(prog_key, {
            "program": prog["name"], "status": prog["status"],
            "network": prog["network"], "valuePerConvUsd": prog["value_usd"],
            "pages": 0, "impressions": 0.0,
        })
        pt["pages"] += 1
        pt["impressions"] += impressions

    opportunities.sort(key=lambda o: o["score"], reverse=True)

    # Programs to ACQUIRE: not earning, ranked by traffic already on their pages.
    acquire = sorted(
        (v for v in program_traffic.values() if v["status"] != "EARNING"),
        key=lambda v: v["impressions"], reverse=True,
    )

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "revenue-opportunities.json").write_text(
        json.dumps({"gscLive": gsc_live, "opportunities": opportunities[:300]}, indent=2),
        encoding="utf-8",
    )
    _write_md(opportunities, acquire, gsc_live)
    earning_uplift = sum(o["estMonthlyUpliftUsd"] for o in opportunities if o["status"] == "EARNING")
    print(f"revenue_intelligence: {len(opportunities)} monetised pages, "
          f"{len(acquire)} programs to acquire, GSC={'live' if gsc_live else 'offline'}, "
          f"est. earning uplift ${earning_uplift:,.0f}/mo")
    return 0


def _write_md(opps: list[dict], acquire: list[dict], gsc_live: bool) -> None:
    note = ("Live GSC data." if gsc_live else
            "GSC offline (no creds / pull failed) — revenue model needs live "
            "gsc-opportunities.json. Traffic-blind run: program map only, no $ ranking.")
    disclaimer = ("Dollar values are MODELLED from network benchmarks (see CLAUDE.md), "
                  "not live earnings. Connect IMPACT_API_TOKEN for real EPC + conversions.")

    # File 1 — revenue-opportunities.md (pages ranked by $ uplift)
    rev = [
        "# Revenue Opportunities", "", f"Status: {note}", "", disclaimer, "",
        "## Top revenue-weighted pages", "",
    ]
    if opps:
        for o in opps[:50]:
            rev.append(
                f"- **${o['estMonthlyUpliftUsd']:,.0f}/mo** (score {o['score']}) "
                f"`{o['page']}` -> {o['program']} [{o['status']}/{o['linkState']}] "
                f"· impr {o['impressions']}, pos {o['position']}, "
                f"+{o['estExtraClicksMo']} clicks/mo @ ${o['valuePerConvUsd']}/conv"
            )
    else:
        rev.append("_No traffic-scored opportunities (GSC offline). See program-acquisition.md._")
    (REPORTS / "revenue-opportunities.md").write_text("\n".join(rev) + "\n", encoding="utf-8")

    # File 2 — program-acquisition.md (programs to apply to, ranked by page traffic)
    acq = [
        "# Program Acquisition Priority", "", f"Status: {note}", "",
        "Unapproved / locked / placeholder programs ranked by traffic already on their "
        "pages. Apply to / unlock these first — the pages already rank, they just don't earn.",
        "", f"({disclaimer})", "",
    ]
    sort_key = "impressions" if gsc_live else "pages"
    for v in sorted(acquire, key=lambda x: x[sort_key], reverse=True)[:25]:
        acq.append(
            f"- **{v['program']}** [{v['status']}, {v['network']}] — "
            f"{v['pages']} pages, {round(v['impressions']):,} impressions, "
            f"${v['valuePerConvUsd']}/conv"
        )
    (REPORTS / "program-acquisition.md").write_text("\n".join(acq) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
