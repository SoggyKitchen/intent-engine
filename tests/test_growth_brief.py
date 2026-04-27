import json
import shutil
from pathlib import Path

from ops import growth_brief


def test_generate_growth_brief_writes_owner_tasks(monkeypatch):
    base = Path("test-temp/growth-brief")
    if base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True)

    report = base / "affiliate_url_report.md"
    report.write_text(
        "\n".join(
            [
                "# Affiliate URL Validation",
                "- OK: 12",
                "- WARN: 1",
                "- PROG: 0",
                "- DEAD: 0",
                "## WARN `/go/example`",
            ]
        ),
        encoding="utf-8",
    )
    social = base / "social_pack_latest.json"
    social.write_text(
        json.dumps([{"title": "HubSpot Pricing 2026", "url": "https://saaspare.org/pages/hubspot-pricing"}]),
        encoding="utf-8",
    )
    out_dir = base / "generated"

    monkeypatch.setattr(growth_brief, "AFFILIATE_REPORT", report)
    monkeypatch.setattr(growth_brief, "SOCIAL_PACK", social)
    monkeypatch.setattr(growth_brief, "OUT_DIR", out_dir)
    monkeypatch.setattr(growth_brief, "_recent_pages", lambda: [])
    monkeypatch.setattr(
        growth_brief,
        "collect_profit_audit",
        lambda max_gap_items=8: {
            "page_count": 10,
            "cta_coverage_pct": 100.0,
            "redirect_count": 5,
            "imported_affiliate_count": 2,
            "missing_partner_targets_total": 0,
            "missing_partner_targets": [],
            "network_signups": [{"name": "PartnerStack", "tools": ["ClickUp", "Notion"]}],
        },
    )

    path = growth_brief.generate_growth_brief()

    text = (out_dir / "growth_brief_latest.md").read_text(encoding="utf-8")
    assert path.endswith("growth_brief_latest.md")
    assert "CTA coverage: 100.0%" in text
    assert "PartnerStack" in text
    assert "HubSpot Pricing 2026" in text
    assert "/go/example" in text

    shutil.rmtree(base)
