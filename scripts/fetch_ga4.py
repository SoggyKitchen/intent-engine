"""
Fetch GA4 data for SaaSpare daily CEO review.
Outputs: data/ga4_data.json

Requirements:
    pip install google-analytics-data

Setup:
    1. Go to console.cloud.google.com
    2. Enable "Google Analytics Data API"
    3. Create a Service Account, download JSON key
    4. Share GA4 property with the service account email (Viewer role)
    5. Set env var: GA4_KEY_FILE=/path/to/key.json
    6. Set env var: GA4_PROPERTY_ID=properties/XXXXXXXXX (from GA4 Admin > Property Settings)

Run: uv run python scripts/fetch_ga4.py
"""
import json
import os
from pathlib import Path
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

GA4_KEY_FILE = os.environ.get("GA4_KEY_FILE", "")
GA4_PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID", "")  # e.g. "properties/123456789"

def fetch_ga4(start_date="7daysAgo", end_date="today"):
    if not GA4_KEY_FILE or not GA4_PROPERTY_ID:
        print("GA4_KEY_FILE and GA4_PROPERTY_ID not set. Skipping GA4 fetch.")
        return None

    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            RunReportRequest, DateRange, Dimension, Metric
        )
        from google.oauth2 import service_account

        credentials = service_account.Credentials.from_service_account_file(
            GA4_KEY_FILE,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"]
        )
        client = BetaAnalyticsDataClient(credentials=credentials)

        # Top pages by sessions
        request = RunReportRequest(
            property=GA4_PROPERTY_ID,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="pagePath")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="screenPageViews"),
                Metric(name="bounceRate"),
                Metric(name="averageSessionDuration"),
            ],
            order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}],
            limit=50
        )
        response = client.run_report(request)

        pages = []
        for row in response.rows:
            pages.append({
                "path": row.dimension_values[0].value,
                "sessions": int(row.metric_values[0].value),
                "pageviews": int(row.metric_values[1].value),
                "bounce_rate": round(float(row.metric_values[2].value), 3),
                "avg_session_duration": round(float(row.metric_values[3].value), 1)
            })

        # Total site metrics
        total_request = RunReportRequest(
            property=GA4_PROPERTY_ID,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[],
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers"),
                Metric(name="screenPageViews"),
                Metric(name="newUsers"),
            ]
        )
        total_response = client.run_report(total_request)
        totals = {}
        if total_response.rows:
            row = total_response.rows[0]
            totals = {
                "sessions": int(row.metric_values[0].value),
                "active_users": int(row.metric_values[1].value),
                "pageviews": int(row.metric_values[2].value),
                "new_users": int(row.metric_values[3].value),
            }

        result = {
            "fetched_at": str(date.today()),
            "period": f"{start_date} to {end_date}",
            "totals": totals,
            "top_pages": pages
        }

        outfile = DATA / "ga4_data.json"
        outfile.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"GA4 data written to {outfile}")
        print(f"  Total sessions: {totals.get('sessions', 0)}")
        print(f"  Top page: {pages[0]['path'] if pages else 'none'} ({pages[0]['sessions'] if pages else 0} sessions)")
        return result

    except Exception as e:
        print(f"GA4 fetch failed: {e}")
        return None


if __name__ == "__main__":
    fetch_ga4()
