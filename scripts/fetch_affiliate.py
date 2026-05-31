"""
Fetch affiliate network performance data for SaaSpare Revenue Hunter.
Outputs: data/affiliate_data.json

Covers: CJ Affiliate (REST API)

Setup CJ:
    1. Log into app.cj.com
    2. Go to Account > API Keys
    3. Generate a Personal Access Token
    4. Set env var: CJ_API_KEY=your_token_here
    5. Set env var: CJ_CID=101733230 (your publisher CID)

Run: uv run python scripts/fetch_affiliate.py
"""
import json
import os
import urllib.request
from pathlib import Path
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

CJ_API_KEY = os.environ.get("CJ_API_KEY", "")
CJ_CID = os.environ.get("CJ_CID", "101733230")


def fetch_cj(days=7):
    if not CJ_API_KEY:
        print("CJ_API_KEY not set. Skipping CJ fetch.")
        return None

    try:
        end = date.today()
        start = end - timedelta(days=days)

        # CJ Commission Detail report
        url = (
            f"https://commission-detail.api.cj.com/v3/commissions"
            f"?cid={CJ_CID}"
            f"&start-date={start}"
            f"&end-date={end}"
            f"&page-number=1"
            f"&records-per-page=100"
        )

        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {CJ_API_KEY}")
        req.add_header("Accept", "application/json")

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        commissions = data.get("commissions", {}).get("commission", [])
        if isinstance(commissions, dict):
            commissions = [commissions]

        # Summarise by advertiser
        by_program = {}
        total_earned = 0.0
        for c in commissions:
            prog = c.get("advertiser-name", "Unknown")
            amount = float(c.get("pub-commission-amount-usd", 0))
            total_earned += amount
            if prog not in by_program:
                by_program[prog] = {"sales": 0, "earned_usd": 0.0, "clicks": 0}
            by_program[prog]["sales"] += 1
            by_program[prog]["earned_usd"] += amount

        result = {
            "fetched_at": str(date.today()),
            "period": f"{start} to {end} ({days} days)",
            "network": "CJ_Affiliate",
            "publisher_id": CJ_CID,
            "total_commissions": len(commissions),
            "total_earned_usd": round(total_earned, 2),
            "by_program": by_program,
            "raw_count": len(commissions)
        }

        outfile = DATA / "affiliate_data.json"
        outfile.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"CJ data written to {outfile}")
        print(f"  Total earned ({days}d): ${total_earned:.2f}")
        print(f"  Programs: {list(by_program.keys())}")
        return result

    except Exception as e:
        print(f"CJ fetch failed: {e}")
        return None


if __name__ == "__main__":
    fetch_cj(days=30)
