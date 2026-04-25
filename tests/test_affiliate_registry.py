import json

from publisher import affiliate_registry as registry


def test_static_redirects_use_affiliate_urls():
    redirects = registry.get_all_redirects()
    assert redirects["ahrefs"] == "https://ahrefs.com/affiliates"
    assert redirects["1password"] == "https://1password.com/partners/"


def test_imported_affiliates_override_and_add_coupon_redirects(tmp_path, monkeypatch):
    imported_path = tmp_path / "affiliate_links.json"
    imported_path.write_text(
        json.dumps(
            {
                "advertisers": {
                    "hubspot": {
                        "name": "HubSpot",
                        "default_click_url": "https://cj.example/hubspot",
                        "coupon_click_url": "https://cj.example/hubspot-coupon",
                        "homepage_url": "https://www.hubspot.com",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(registry, "IMPORTED_AFFILIATE_PATH", imported_path)
    registry.clear_imported_affiliate_cache()

    assert registry.get_affiliate_url_for_tool("HubSpot") == "https://cj.example/hubspot"
    assert registry.get_go_url("HubSpot") == "/go/hubspot"
    assert registry.get_go_url("HubSpot", page_type="coupon") == "/go/hubspot-coupon"

    redirects = registry.get_all_redirects()
    assert redirects["hubspot"] == "https://cj.example/hubspot"
    assert redirects["hubspot-coupon"] == "https://cj.example/hubspot-coupon"
