"""
jarvis/daily_brief.py
─────────────────────
Reads live SaaSpare data and outputs a Tony-Stark-style CEO briefing.
Run manually:  uv run python jarvis/daily_brief.py
Scheduled:     Windows Task Scheduler (see setup_scheduler.bat)
Speak aloud:   uv run python jarvis/daily_brief.py --speak
"""

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "seo" / "reports"
REDIRECTS = ROOT / "site" / "_redirects"

# ── helpers ──────────────────────────────────────────────────────────────────

def load_revenue_opps():
    f = REPORTS / "revenue-opportunities.md"
    if not f.exists():
        return []
    lines = f.read_text(encoding="utf-8").splitlines()
    opps = []
    for line in lines:
        m = re.match(r"- \*\*(\$[\d/mo]+)\*\* \(score ([\d.]+)\) `([^`]+)` -> (\S+) \[([^\]]+)\].*impr ([\d.]+), pos ([\d.]+)", line)
        if m:
            opps.append({
                "value": m.group(1), "score": float(m.group(2)),
                "page": m.group(3), "tool": m.group(4),
                "status": m.group(5), "impr": float(m.group(6)),
                "pos": float(m.group(7))
            })
    return sorted(opps, key=lambda x: x["score"], reverse=True)

def load_gsc_opps():
    f = REPORTS / "gsc-opportunities.json"
    if not f.exists():
        return []
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def count_redirects():
    if not REDIRECTS.exists():
        return 0, 0, []
    text = REDIRECTS.read_text(encoding="utf-8")
    live_patterns = ["sjv.io", "pxf.io", "dpbolvw.net", "kqzyfj.com",
                     "jdoqocy.com", "anrdoezrs.net", "tkqlhce.com",
                     "awin1.com", "linksynergy.com", "sjv.io",
                     "try.activecampaign.com", "elevenlabs"]
    recent_wins = []
    live = 0
    bare = 0
    for line in text.splitlines():
        if not line.startswith("/go/"):
            continue
        if any(p in line for p in live_patterns):
            live += 1
            # flag recently activated (look for 2026-06-09 in comment above)
        else:
            bare += 1
    return live, bare, recent_wins

def check_traffic_alarm():
    """Proactive watchdog: compare today's total tracked impressions against
    the last run's snapshot. A >20% drop is spoken FIRST in the brief —
    the June 2026 indexing cliff sat unnoticed for 9 days; never again."""
    opps = load_revenue_opps()
    total = sum(o["impr"] for o in opps)
    snap_file = Path(__file__).parent / ".gsc_snapshot.json"
    alert = None
    try:
        prev = json.loads(snap_file.read_text(encoding="utf-8"))
        prev_total = float(prev.get("total_impressions", 0))
        if prev_total > 100 and total < prev_total * 0.8:
            pct = (1 - total / prev_total) * 100
            alert = (f"ALERT, sir: tracked impressions dropped {pct:.0f} percent "
                     f"since the last brief — {prev_total:.0f} down to {total:.0f}. "
                     "Recommend checking Search Console indexing immediately.")
    except Exception:
        pass
    if total > 0:
        try:
            snap_file.write_text(json.dumps(
                {"total_impressions": total, "date": date.today().isoformat()}),
                encoding="utf-8")
        except Exception:
            pass
    return alert

def get_recent_git_log():
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True, text=True, cwd=ROOT
        )
        return result.stdout.strip().splitlines()
    except Exception:
        return []

# ── brief builder ─────────────────────────────────────────────────────────────

def build_brief():
    today = date.today().strftime("%A, %d %B %Y")
    opps = load_revenue_opps()
    gsc = load_gsc_opps()
    live_links, bare_links, _ = count_redirects()
    recent = get_recent_git_log()

    lines = []
    lines.append(f"Good morning, sir. SaaSpare status briefing for {today}.\n")

    alarm = check_traffic_alarm()
    if alarm:
        lines.insert(0, alarm + "\n")

    # Revenue headline
    if opps:
        top = opps[0]
        lines.append(
            f"TOP REVENUE OPPORTUNITY: {top['page'].split('/')[-1]} — "
            f"modelled at {top['value']} per month. "
            f"Currently ranking position {top['pos']:.1f} with {top['impr']:.0f} impressions. "
            f"Affiliate status: {top['status']}."
        )
        pending = [o for o in opps if "PENDING" in o["status"] or "PLACEHOLDER" in o["status"]]
        total_locked = sum(
            float(o["value"].replace("$","").replace("/mo","") or 0)
            for o in pending
            if re.match(r"\$[\d]+/mo", o["value"])
        )
        if pending:
            lines.append(
                f"\nThere are {len(pending)} high-value pages with placeholder affiliate links — "
                f"estimated {total_locked:.0f} dollars per month still uncaptured. "
                f"HubSpot and FreshBooks approvals will unlock the majority of this."
            )
    else:
        lines.append("Revenue report not available. Run the GSC agent to refresh.")

    # Link status
    lines.append(
        f"\nAFFILIATE LINK HEALTH: {live_links} tracked links live. "
        f"{bare_links} bare placeholder links still earning zero. "
        f"Priority wires pending: HubSpot (187 pages), FreshBooks (73 pages), Perimeter 81."
    )

    # GSC top movers
    if gsc:
        top_gsc = gsc[:3]
        lines.append(f"\nTOP GSC OPPORTUNITIES (highest score):")
        for g in top_gsc:
            url = g.get("url","").replace("https://saaspare.org","")
            score = g.get("score", 0)
            impr = g.get("impressions", 0)
            pos = g.get("position", 0)
            lines.append(f"  · {url} — score {score:.0f}, {impr:.0f} impressions, position {pos:.1f}")

    # Recent commits
    if recent:
        lines.append(f"\nRECENT DEPLOYMENTS:")
        for log in recent[:3]:
            lines.append(f"  · {log}")

    # Pending approvals reminder
    lines.append(
        "\nPENDING ACTIONS:"
        "\n  · HubSpot affiliate email sent — await approval (2-3 business days)"
        "\n  · FreshBooks — apply at ui.awin.com (publisher 2917137)"
        "\n  · Perimeter 81 — application message sent"
        "\n  · PartnerStack re-apply: not before June 18"
        "\n  · ActiveCampaign: LIVE as of today ✓"
        "\n  · Incogni CJ: LIVE as of today ✓"
    )

    lines.append(
        "\nAll systems nominal, sir. Shall I proceed with today's optimisation queue?"
    )

    return "\n".join(lines)

# ── speak (optional) ──────────────────────────────────────────────────────────

def speak(text):
    """Use Windows SAPI TTS — no install required."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 165)
        # Try to find a good voice
        for v in engine.getProperty("voices"):
            if "david" in v.name.lower() or "mark" in v.name.lower():
                engine.setProperty("voice", v.id)
                break
        engine.say(text)
        engine.runAndWait()
    except ImportError:
        # Fallback: Windows built-in via PowerShell
        safe = text.replace("'", "").replace('"', "")[:2000]
        subprocess.run(
            ["powershell", "-Command",
             f"Add-Type -AssemblyName System.Speech; "
             f"$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
             f"$s.Rate = 2; $s.Speak('{safe}')"],
            check=False
        )

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    brief = build_brief()

    # Always write to file for the nightly automation to pick up
    out_file = REPORTS / "daily-brief.md"
    out_file.write_text(f"# SaaSpare Daily Brief\n\n{brief}\n", encoding="utf-8")

    print(brief)

    if "--speak" in sys.argv:
        speak(brief)

if __name__ == "__main__":
    main()
