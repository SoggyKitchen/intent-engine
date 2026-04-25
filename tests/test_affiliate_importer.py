import json

from publisher.affiliate_importer import import_affiliate_bundle, import_affiliate_csv


def test_import_affiliate_csv_prefers_homepage_and_coupon_links(tmp_path):
    csv_path = tmp_path / "links.csv"
    csv_path.write_text(
        "\n".join(
            [
                "ADVERTISER,LINK ID,NAME,DESCRIPTION,KEYWORDS,LINK TYPE,THREE MONTH EPC,SEVEN DAY EPC,HTML LINKS,JAVASCRIPT LINKS,CLICK URL,PROMOTION TYPE,COUPON CODE,CATEGORY,RELATIONSHIP STATUS,LANGUAGE",
                '"AOMEI","1","Home page","Official homepage","backup","Text Link","$8.75 AUD","$19.08 AUD","<a href=""https://tracking.example/home"">AOMEI Homepage</a>","","https://cj.example/home","N/A","","Computer SW","Active","English"',
                '"AOMEI","2","Holiday banner","Seasonal banner","backup","Banner","$1.00 AUD","$2.00 AUD","<a href=""https://tracking.example/banner"">Banner</a>","","https://cj.example/banner","N/A","","Computer SW","Active","English"',
                '"AOMEI","3","Coupon offer","Coupon landing page","backup","Text Link","$0.00 AUD","$1.00 AUD","<a href=""https://tracking.example/coupon"">Coupon</a>","","https://cj.example/coupon","Coupon","SAVE30","Computer SW","Active","English"',
            ]
        ),
        encoding="utf-8",
    )

    output_path = tmp_path / "affiliate_links.json"
    report_path = tmp_path / "affiliate_links_report.md"
    result = import_affiliate_csv(csv_path, output_path, report_path)

    assert result["offer_count"] == 3

    stored = json.loads(output_path.read_text(encoding="utf-8"))
    aomei = stored["advertisers"]["aomei"]
    assert aomei["default_click_url"] == "https://cj.example/home"
    assert aomei["coupon_click_url"] == "https://cj.example/coupon"
    assert aomei["coupon_code"] == "SAVE30"
    assert report_path.exists()


def test_import_affiliate_bundle_filters_irrelevant_rows_and_normalizes_advertisers(tmp_path):
    csv_path = tmp_path / "links.csv"
    csv_path.write_text(
        "\n".join(
            [
                "ADVERTISER,LINK ID,NAME,DESCRIPTION,KEYWORDS,LINK TYPE,THREE MONTH EPC,SEVEN DAY EPC,HTML LINKS,JAVASCRIPT LINKS,CLICK URL,PROMOTION TYPE,COUPON CODE,CATEGORY,RELATIONSHIP STATUS,LANGUAGE",
                '"GetResponse Inc.","1","GetResponse 10% Off Pricing","Email marketing automation","newsletter,automation","Text Link","$8.75 AUD","$19.08 AUD","<a href=""https://www.getresponse.com/"" target=""_top"">https://www.getresponse.com/</a>","","https://cj.example/getresponse","N/A","","Email Marketing","Active","English"',
                '"Forces War Records","2","Military Ancestors","Discover your military ancestors","ancestry,records","Text Link","$8.75 AUD","$19.08 AUD","<a href=""https://forces-war-records.co.uk/"" target=""_top"">https://forces-war-records.co.uk/</a>","","https://cj.example/forces","N/A","","Self Help","Active","English"',
            ]
        ),
        encoding="utf-8",
    )

    links_path = tmp_path / "affiliate_links.json"
    overrides_path = tmp_path / "affiliate_overrides.json"
    summary = import_affiliate_bundle(csv_path, overrides_path=overrides_path, links_path=links_path)

    links_payload = json.loads(links_path.read_text(encoding="utf-8"))
    assert "getresponse" in links_payload["advertisers"]
    assert "forces-war-records" not in links_payload["advertisers"]

    overrides_payload = json.loads(overrides_path.read_text(encoding="utf-8"))
    assert [item["name"] for item in overrides_payload] == ["GetResponse"]
    assert summary["links_summary"]["advertiser_count"] == 1
    assert summary["overrides_summary"]["links_selected"] == 1
