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


def test_import_affiliate_bundle_drops_consumer_repair_junk_and_prefers_us_buyer_link(tmp_path):
    csv_path = tmp_path / "links.csv"
    csv_path.write_text(
        "\n".join(
            [
                "ADVERTISER,LINK ID,NAME,DESCRIPTION,KEYWORDS,LINK TYPE,THREE MONTH EPC,SEVEN DAY EPC,HTML LINKS,JAVASCRIPT LINKS,CLICK URL,PROMOTION TYPE,COUPON CODE,CATEGORY,RELATIONSHIP STATUS,LANGUAGE",
                '"HostPapa","1","HostPapa Landing Page - Canada","Canada landing page","hosting","Text Link","$25.00 AUD","$10.00 AUD","<a href=""https://www.hostpapa.com/ca/"">Canada</a>","","https://cj.example/hostpapa-ca","N/A","","Web Hosting/Servers","Active","English"',
                '"HostPapa","2","HostPapa US Homepage Landing Page","US homepage","hosting","Text Link","$20.00 AUD","$8.00 AUD","<a href=""https://www.hostpapa.com/"">US</a>","","https://cj.example/hostpapa-us","N/A","","Web Hosting/Servers","Active","English"',
                '"Restoro","3","Repair PC","PC Repair","computer repair","Text Link","$9.00 AUD","$3.00 AUD","<a href=""https://www.restoro.com/"">Restoro</a>","","https://cj.example/restoro","N/A","","Computer SW","Active","English"',
            ]
        ),
        encoding="utf-8",
    )

    links_path = tmp_path / "affiliate_links.json"
    overrides_path = tmp_path / "affiliate_overrides.json"
    summary = import_affiliate_bundle(csv_path, overrides_path=overrides_path, links_path=links_path)

    links_payload = json.loads(links_path.read_text(encoding="utf-8"))
    assert set(links_payload["advertisers"]) == {"hostpapa"}
    assert links_payload["advertisers"]["hostpapa"]["default_click_url"] == "https://cj.example/hostpapa-us"

    overrides_payload = json.loads(overrides_path.read_text(encoding="utf-8"))
    assert [item["name"] for item in overrides_payload] == ["HostPapa"]
    assert summary["overrides_summary"]["links_selected"] == 1


def test_import_affiliate_csv_applies_known_homepage_fallbacks(tmp_path):
    csv_path = tmp_path / "links.csv"
    csv_path.write_text(
        "\n".join(
            [
                "ADVERTISER,LINK ID,NAME,DESCRIPTION,KEYWORDS,LINK TYPE,THREE MONTH EPC,SEVEN DAY EPC,HTML LINKS,JAVASCRIPT LINKS,CLICK URL,PROMOTION TYPE,COUPON CODE,CATEGORY,RELATIONSHIP STATUS,LANGUAGE",
                '"Contabo","1","Dedicated Servers","Advertise for our US Regions","hosting,server","Text Link","$8.75 AUD","$19.08 AUD","","","https://cj.example/contabo","N/A","","Web Hosting/Servers","Active","English"',
            ]
        ),
        encoding="utf-8",
    )

    output_path = tmp_path / "affiliate_links.json"
    result = import_affiliate_csv(csv_path, output_path)

    assert result["advertiser_count"] == 1

    stored = json.loads(output_path.read_text(encoding="utf-8"))
    contabo = stored["advertisers"]["contabo"]
    assert contabo["default_click_url"] == "https://cj.example/contabo"
    assert contabo["homepage_url"] == "https://contabo.com/en/"
