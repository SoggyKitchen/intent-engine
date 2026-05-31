"""
Fetch Google Search Console data for SaaSpare daily SEO review.
Outputs: data/gsc_data.json

Requirements:
    pip install google-api-python-client google-auth

Setup:
    1. Go to console.cloud.google.com
    2. Enable "Google Search Console API"
    3. Create a Service Account, download JSON key (same one as GA4 is fine)
    4. Add service account email to GSC as Owner/Full User
    5. Set env var: GSC_KEY_FILE=/path/to/key.json
    6. Set env var: GSC_SITE_URL=https://saaspare.org/

Run: uv run python scripts/fetch_gsc.py
"""
import json
import os
from pathlib import Path
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

GSC_KEY_FILE = os.environ.get("GSC_KEY_FILE", "")
GSC_SITE_URL = os.environ.get("GSC_SITE_URL", "https://saaspare.org/")


def fetch_gsc(days=28):
    if not GSC_KEY_FILE:
        print("GSC_KEY_FILE not set. Skipping GSC fetch.")
        return None

    try:
        from googleapiclient.discovery import build
        from google.oauth2 import service_account

        credentials = service_account.Credentials.from_service_account_file(
            GSC_KEY_FILE,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
        service = build("searchconsole", "v1", credentials=credentials)

        end = date.today() - timedelta(days=3)  # GSC has 3-day lag
        start = end - timedelta(days=days)

        def query(dimensions, row_limit=50, **kwargs):
            body = {
                "startDate": str(start),
                "endDate": str(end),
                "dimensions": dimensions,
                "rowLimit": row_limit,
                **kwargs
            }
            return service.searchanalytics().query(siteUrl=GSC_SITE_URL, body=body).execute()

        # Top queries by clicks
        queries_resp = query(["query"], row_limit=50)
        top_queries = [
            {
                "query": r["keys"][0],
                "clicks": r["clicks"],
                "impressions": r["impressions"],
                "ctr": round(r["ctr"], 4),
                "position": round(r["position"], 1)
            }
            for r in queries_resp.get("rows", [])
        ]

        # Pages ranking 4-20 (opportunity zone)
        pages_resp = query(["page"], row_limit=100)
        opportunity_pages = []
        for r in pages_resp.get("rows", []):
            pos = r["position"]
            if 4 <= pos <= 20 and r["impressions"] > 50:
                opportunity_pages.append({
                    "page": r["keys"][0],
                    "clicks": r["clicks"],
                    "impressions": r["impressions"],
                    "ctr": round(r["ctr"], 4),
                    "position": round(pos, 1)
                })
        opportunity_pages.sort(key=lambda x: x["impressions"], reverse=True)

        # Pages with impressions but low CTR (< 3%)
        low_ctr_pages = [
            p for p in [
                {
                    "page": r["keys"][0],
                    "clicks": r["clicks"],
                    "impressions": r["impressions"],
                    "ctr": round(r["ctr"], 4),
                    "position": round(r["position"], 1)
                }
                for r in pages_resp.get("rows", [])
            ]
            if p["impressions"] > 100 and p["ctr"] < 0.03
        ]
        low_ctr_pages.sort(key=lambda x: x["impressions"], reverse=True)

        result = {
            "fetched_at": str(date.today()),
            "period": f"{start} to {end} ({days} days)",
            "top_queries": top_queries[:30],
            "opportunity_pages_4_to_20": opportunity_pages[:20],
            "low_ctr_pages": low_ctr_pages[:20],
            "total_queries": len(top_queries),
            "total_opportunity_pages": len(opportunity_pages)
        }

        outfile = DATA / "gsc_data.json"
        outfile.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"GSC data written to {outfile}")
        print(f"  Top query: {top_queries[0]['query'] if top_queries else 'none'} ({top_queries[0]['clicks'] if top_queries else 0} clicks)")
        print(f"  Opportunity pages (pos 4-20): {len(opportunity_pages)}")
        print(f"  Low CTR pages: {len(low_ctr_pages)}")
        return result

    except Exception as e:
        print(f"GSC fetch failed: {e}")
        return None


if __name__ == "__main__":
    fetch_gsc()
