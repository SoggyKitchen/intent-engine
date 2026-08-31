"""
Generate daily / weekly / monthly HTML email reports for SaaSpare.
Called by GitHub Actions with --mode daily|weekly|monthly
Outputs HTML to stdout, which the action pipes into the email sender.

Usage:
  python scripts/generate_email_report.py --mode daily   > /tmp/report.html
  python scripts/generate_email_report.py --mode weekly  > /tmp/report.html
  python scripts/generate_email_report.py --mode monthly > /tmp/report.html
"""
import sys, json, subprocess, re
from pathlib import Path
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MODE = "daily"
for i, a in enumerate(sys.argv):
    if a == "--mode" and i + 1 < len(sys.argv):
        MODE = sys.argv[i + 1]

TODAY = date.today()

# ── Helpers ───────────────────────────────────────────────────────────────────
def git_log(since_days=1):
    since = (TODAY - timedelta(days=since_days)).isoformat()
    try:
        out = subprocess.check_output(
            ["git", "log", f"--since={since}", "--oneline", "--no-merges",
             "--author-date-order"],
            cwd=ROOT, stderr=subprocess.DEVNULL, text=True
        )
        return [l.strip() for l in out.strip().splitlines() if l.strip()]
    except Exception:
        return []

def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default or {}

def safe_int(v):
    try: return int(v)
    except: return 0

def safe_float(v):
    try: return float(v)
    except: return 0.0

# ── Data sources ──────────────────────────────────────────────────────────────
kpis       = read_json(DATA / "public_kpis.json")
gsc_opps   = read_json(DATA / "gsc_opportunities.json")
ctr_report = read_json(DATA / "ctr_fix_report.json")
memory     = read_json(DATA / "memory.json")
affiliate  = read_json(DATA / "affiliate_data.json")

pages_total = safe_int(kpis.get("page_counts", {}).get("total_buyer_pages", 0))
# Prefer the LIVE GSC report written by seo_agent.py each run
# (seo/reports/gsc-opportunities.json). The legacy data/gsc_opportunities.json
# is a static snapshot that went stale on 2026-06-10 and silently pinned this
# report to 79 clicks / 22,919 impressions for months.
_live_gsc = read_json(ROOT / "seo" / "reports" / "gsc-opportunities.json")
_live_opps = _live_gsc.get("opportunities") or []
if _live_opps:
    _seen = {}
    for _o in _live_opps:
        _pg = _o.get("page")
        # de-dupe: engine emits per-query rows plus a "(page rollup)" row per page
        if _o.get("query") == "(page rollup)":
            _seen[_pg] = _o
        elif _pg not in _seen:
            _seen[_pg] = _o
    gsc_clicks = safe_int(sum(safe_float(o.get("clicks", 0)) for o in _seen.values()))
    gsc_impr   = safe_int(sum(safe_float(o.get("impressions", 0)) for o in _seen.values()))
    gsc_ctr    = round((gsc_clicks / gsc_impr * 100), 2) if gsc_impr else 0.0
    p1_pages   = sum(1 for o in _seen.values() if 4 <= safe_float(o.get("position", 0)) <= 10)
    p2_pages   = sum(1 for o in _seen.values() if 11 <= safe_float(o.get("position", 0)) <= 20)
else:
    gsc_summary = gsc_opps.get("summary", {})
    gsc_clicks  = safe_int(gsc_summary.get("total_clicks", 0))
    gsc_impr    = safe_int(gsc_summary.get("total_impressions", 0))
    gsc_ctr     = safe_float(gsc_summary.get("overall_ctr_pct", 0))
    p1_pages    = safe_int(gsc_summary.get("pages_pos_4_10", 0))
    p2_pages    = safe_int(gsc_summary.get("pages_pos_11_20", 0))

aff_earned  = safe_float(affiliate.get("total_earned_usd", 0))
aff_period  = affiliate.get("period", "last 30 days")
aff_programs = affiliate.get("by_program", {})

# ── Colours ───────────────────────────────────────────────────────────────────
BG       = "#050407"
CARD_BG  = "#0e0c14"
BORDER   = "#1e1a2e"
RED      = "#ff416d"
GREEN    = "#22c55e"
YELLOW   = "#f59e0b"
TEXT     = "rgba(255,248,245,.88)"
MUTED    = "rgba(255,248,245,.5)"

def card(content, extra_style=""):
    return f"""<div style="background:{CARD_BG};border:1px solid {BORDER};border-radius:12px;
padding:20px 24px;margin:0 0 16px 0;{extra_style}">{content}</div>"""

def stat_row(label, value, color=TEXT, sub=""):
    sub_html = f'<span style="color:{MUTED};font-size:12px;margin-left:8px;">{sub}</span>' if sub else ""
    return f"""<div style="display:flex;justify-content:space-between;align-items:center;
padding:8px 0;border-bottom:1px solid {BORDER};">
  <span style="color:{MUTED};font-size:14px;">{label}</span>
  <span style="color:{color};font-weight:700;font-size:15px;">{value}{sub_html}</span>
</div>"""

def badge(text, color=RED):
    return f'<span style="background:{color}22;color:{color};border:1px solid {color}44;border-radius:6px;padding:2px 8px;font-size:11px;font-weight:700;">{text}</span>'

# ── Mode-specific date range ───────────────────────────────────────────────────
if MODE == "daily":
    since_days = 1
    period_label = f"Yesterday ({(TODAY - timedelta(1)).strftime('%a %d %b')})"
    subject_prefix = f"[Daily] SaaSpare CEO Brief — {TODAY.strftime('%a %d %b %Y')}"
elif MODE == "weekly":
    since_days = 7
    period_label = f"Last 7 days (week ending {TODAY.strftime('%d %b %Y')})"
    subject_prefix = f"[Weekly] SaaSpare Revenue Report — w/e {TODAY.strftime('%d %b %Y')}"
else:  # monthly
    since_days = 30
    period_label = f"Last 30 days"
    subject_prefix = f"[Monthly] SaaSpare Performance — {TODAY.strftime('%B %Y')}"

commits = git_log(since_days)

# Categorise commits
revenue_commits = [c for c in commits if any(x in c.lower() for x in ["wave", "revenue", "affiliate", "ctr", "fix"])]
ci_commits      = [c for c in commits if "nightly" in c.lower() or "chore" in c.lower() or "harvest" in c.lower()]
other_commits   = [c for c in commits if c not in revenue_commits and c not in ci_commits]

# ── Build HTML ────────────────────────────────────────────────────────────────
def fmt_commit(c):
    sha = c[:7]
    msg = c[8:]
    # Colour code by type
    col = MUTED
    if any(x in msg.lower() for x in ["wave", "revenue", "ctr"]): col = GREEN
    elif "fix" in msg.lower(): col = YELLOW
    return f'<div style="padding:4px 0;font-size:13px;"><span style="color:{MUTED};font-family:monospace;">{sha}</span> <span style="color:{col};">{msg[:80]}</span></div>'

commits_html = "".join(fmt_commit(c) for c in commits[:20]) if commits else f'<div style="color:{MUTED};font-size:13px;">No commits in period</div>'

aff_rows = "".join(
    stat_row(prog, f"${data['earned_usd']:.2f}", GREEN, f"{data['sales']} sales")
    for prog, data in sorted(aff_programs.items(), key=lambda x: x[1]["earned_usd"], reverse=True)
) if aff_programs else stat_row("No data", "—", MUTED, "run fetch_affiliate.py with CJ_API_KEY")

# Pending programs
pending = [
    ("HubSpot", "39 pages", "$250-1000/sale"),
    ("ClickUp", "27 pages", "$36-150/sale"),
    ("ActiveCampaign", "20 pages", "$85/sale"),
    ("Monday.com", "20 pages", "$150/sale"),
    ("1Password", "37 pages", "$30-60/sale"),
    ("FreshBooks", "19 pages", "$200/sale"),
    ("Xero", "18 pages", "varies"),
    ("Dashlane", "14 pages", "$25-50/sale"),
]
pending_html = "".join(
    f'<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid {BORDER};font-size:13px;">'
    f'<span style="color:{YELLOW};">⏳ {name}</span>'
    f'<span style="color:{MUTED};">{pages} &bull; {commission}</span></div>'
    for name, pages, commission in pending
)

# Action items
if MODE == "daily":
    actions = [
        ("Check email for ClickUp + ActiveCampaign approvals", "HIGH"),
        ("Log into app.cj.com → Reports → Earnings to see commissions", "HIGH"),
        ("Submit Xero affiliate application if not done", "MED"),
        ("Email support@partnerstack.com to unlock account", "MED"),
    ]
elif MODE == "weekly":
    actions = [
        ("Export fresh GSC CSV → save as data/gsc_export.csv for better CTR targeting", "HIGH"),
        ("Check all pending affiliate approvals — follow up if >7 days no reply", "HIGH"),
        ("Review CJ dashboard for any new commission transactions", "HIGH"),
        ("Check Impact.com activation status (created May 30)", "MED"),
        ("Apply to any new affiliate programs on Semrush topic (Moz, Ahrefs)", "MED"),
    ]
else:  # monthly
    actions = [
        ("Export monthly GSC CSV to track CTR improvement", "HIGH"),
        ("Review all affiliate earnings — calculate monthly revenue total", "HIGH"),
        ("Identify top 10 pages by traffic — ensure affiliate links working", "HIGH"),
        ("Plan next content wave — check gsc_opportunities.json for gaps", "MED"),
        ("Update Impact.com profile with new stats (1,385+ pages)", "MED"),
        ("Invoice or record ABN income for tax records", "LOW"),
    ]

action_col = {
    "HIGH": RED, "MED": YELLOW, "LOW": GREEN
}
actions_html = "".join(
    f'<div style="display:flex;gap:10px;padding:6px 0;border-bottom:1px solid {BORDER};font-size:13px;align-items:flex-start;">'
    f'<span style="background:{action_col[pri]}22;color:{action_col[pri]};border-radius:4px;padding:1px 6px;font-size:11px;font-weight:700;white-space:nowrap;">{pri}</span>'
    f'<span style="color:{TEXT};">{task}</span></div>'
    for task, pri in actions
)

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{subject_prefix}</title>
</head>
<body style="margin:0;padding:0;background:{BG};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:{TEXT};">

<div style="max-width:640px;margin:0 auto;padding:24px 16px;">

  <!-- Header -->
  <div style="text-align:center;padding:24px 0 16px;">
    <div style="font-size:28px;font-weight:900;letter-spacing:-1px;">
      <span style="color:{RED};">S</span><span style="color:{TEXT};">aaSpare</span>
    </div>
    <div style="color:{MUTED};font-size:13px;margin-top:4px;">CEO Brief &bull; {period_label}</div>
  </div>

  <!-- KPI strip -->
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:0 0 20px;">
    {"".join(f'''<div style="background:{CARD_BG};border:1px solid {BORDER};border-radius:10px;padding:14px;text-align:center;">
      <div style="font-size:20px;font-weight:800;color:{c};">{v}</div>
      <div style="font-size:11px;color:{MUTED};margin-top:2px;">{l}</div>
    </div>''' for l, v, c in [
        ("Pages Live", f"{pages_total:,}", RED),
        ("GSC Clicks", str(gsc_clicks), GREEN),
        ("Impressions", f"{gsc_impr:,}", YELLOW),
        ("CTR", f"{gsc_ctr:.1f}%", TEXT),
    ])}
  </div>

  <!-- Affiliate earnings -->
  {card(f'''<div style="font-size:13px;font-weight:700;color:{MUTED};letter-spacing:.05em;text-transform:uppercase;margin-bottom:12px;">
    Affiliate Earnings &bull; {aff_period}
  </div>
  {stat_row("Total Earned", f"${aff_earned:.2f}", GREEN)}
  {aff_rows}
  <div style="margin-top:12px;padding-top:12px;border-top:1px solid {BORDER};">
    <div style="font-size:12px;color:{MUTED};">Pending (not yet approved)</div>
    {pending_html}
  </div>''')}

  <!-- SEO snapshot -->
  {card(f'''<div style="font-size:13px;font-weight:700;color:{MUTED};letter-spacing:.05em;text-transform:uppercase;margin-bottom:12px;">
    Search Rankings Snapshot
  </div>
  {stat_row("Pages on page 1 (pos 4-10)", str(p1_pages), YELLOW, "CTR optimise")}
  {stat_row("Pages on page 2 (pos 11-20)", str(p2_pages), MUTED, "push to page 1")}
  {stat_row("CTR fixes applied this run", str(ctr_report.get("updated", 0)), GREEN)}
  {stat_row("Top opportunity", "ramp-pricing-2026 (1,687 impr)", TEXT)}''')}

  <!-- Commits -->
  {card(f'''<div style="font-size:13px;font-weight:700;color:{MUTED};letter-spacing:.05em;text-transform:uppercase;margin-bottom:12px;">
    Commits ({len(commits)} in period)
  </div>
  {commits_html}''')}

  <!-- Action items -->
  {card(f'''<div style="font-size:13px;font-weight:700;color:{RED};letter-spacing:.05em;text-transform:uppercase;margin-bottom:12px;">
    Your Action Items
  </div>
  {actions_html}''')}

  <!-- Footer -->
  <div style="text-align:center;padding:20px 0;font-size:12px;color:{MUTED};">
    SaaSpare.org &bull; ABN 20 602 197 525 &bull; Auto-generated by CEO routine<br>
    <a href="https://saaspare.org" style="color:{RED};text-decoration:none;">saaspare.org</a> &bull;
    <a href="https://github.com/SoggyKitchen/intent-engine" style="color:{MUTED};text-decoration:none;">GitHub</a>
  </div>

</div>
</body>
</html>"""

# Print subject on first line so the action can parse it, then HTML
print(f"SUBJECT:{subject_prefix}")
print(html)
