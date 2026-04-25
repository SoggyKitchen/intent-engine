from ops import profit_audit


def test_collect_profit_audit_flags_missing_ctas_and_partner_gaps(tmp_path, monkeypatch):
    pages_dir = tmp_path / "pages"
    pages_dir.mkdir()

    (pages_dir / "hubspot-pricing-2026-plans-costs-what-you-actually-pay.html").write_text(
        "<html><title>HubSpot Pricing | SaaSpare</title><a href='/go/hubspot'>Try HubSpot</a></html>",
        encoding="utf-8",
    )
    (pages_dir / "salesforce-pricing-2026-plans-costs-what-you-actually-pay.html").write_text(
        "<html><title>Salesforce Pricing | SaaSpare</title><p>No CTA here yet</p></html>",
        encoding="utf-8",
    )

    def fake_get_go_url(tool_name: str, page_type: str = "comparison"):
        if tool_name == "HubSpot":
            return "/go/hubspot"
        return None

    monkeypatch.setattr(profit_audit, "get_go_url", fake_get_go_url)
    monkeypatch.setattr(profit_audit, "get_all_redirects", lambda: {"hubspot": "https://cj.example/hubspot"})
    monkeypatch.setattr(profit_audit, "get_network_signups", lambda: [])

    report = profit_audit.collect_profit_audit(
        site_dir=pages_dir,
        pricing_targets=[("HubSpot", "marketing_automation"), ("Salesforce", "crm")],
        coupon_targets=[],
        review_targets=[],
        free_plan_targets=[],
    )

    assert report["page_count"] == 2
    assert report["pages_with_cta"] == 1
    assert report["pages_without_go_cta_total"] == 1
    assert report["pages_without_go_cta"][0]["title"] == "Salesforce Pricing"
    assert report["missing_partner_targets_total"] == 1
    assert report["missing_partner_targets"][0]["tool"] == "Salesforce"
    assert report["missing_partner_targets"][0]["page_count"] == 1


def test_collect_profit_audit_handles_empty_site(monkeypatch, tmp_path):
    monkeypatch.setattr(profit_audit, "get_go_url", lambda tool_name, page_type="comparison": None)
    monkeypatch.setattr(profit_audit, "get_all_redirects", lambda: {})
    monkeypatch.setattr(profit_audit, "get_network_signups", lambda: [])

    report = profit_audit.collect_profit_audit(
        site_dir=tmp_path / "missing-pages",
        pricing_targets=[],
        coupon_targets=[],
        review_targets=[],
        free_plan_targets=[],
    )

    assert report["page_count"] == 0
    assert report["cta_coverage_pct"] == 0.0
    assert report["pages_without_go_cta_total"] == 0
    assert report["missing_partner_targets_total"] == 0
