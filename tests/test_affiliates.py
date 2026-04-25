import json

from publisher.affiliate_importer import import_cj_csv
from publisher.affiliate_registry import get_all_redirects, get_go_url


def test_go_redirects_use_affiliate_urls():
    redirects = get_all_redirects()
    assert redirects["semrush"] == "https://www.semrush.com/partner/"
    assert get_go_url("Semrush") == "/go/semrush"


def test_import_cj_csv_selects_best_active_link(tmp_path):
    csv_path = tmp_path / "links.csv"
    overrides_path = tmp_path / "affiliate_overrides.json"
    csv_path.write_text(
        '"ADVERTISER","NAME","DESCRIPTION","KEYWORDS","LINK TYPE","THREE MONTH EPC","SEVEN DAY EPC","HTML LINKS","CLICK URL","PROMOTION TYPE","COUPON CODE","PROMOTIONAL END DATE","CATEGORY","RELATIONSHIP STATUS"\n'
        '"AOMEI","AnyViewer Homepage","Remote desktop","AnyViewer,AOMEI","Text Link","$8.00 AUD","$12.00 AUD","<a href=""https://www.aomeitech.com/anyviewer/"" target=""_top"">https://www.aomeitech.com/anyviewer/</a>","https://www.jdoqocy.com/click-1","N/A","","","Computer SW","Active"\n'
        '"AOMEI","AnyViewer Banner","Remote desktop","AnyViewer,AOMEI","Banner","$1.00 AUD","$1.00 AUD","<a href=""https://www.aomeitech.com/anyviewer/"" target=""_top"">banner</a>","https://www.jdoqocy.com/click-2","N/A","","","Computer SW","Active"\n',
        encoding="utf-8",
    )

    summary = import_cj_csv(csv_path, overrides_path=overrides_path)
    payload = json.loads(overrides_path.read_text(encoding="utf-8"))
    anyviewer = next(item for item in payload if item["name"] == "AnyViewer")

    assert summary["links_selected"] >= 1
    assert anyviewer["affiliate_url"] == "https://www.jdoqocy.com/click-1"
    assert anyviewer["vertical"] == "devtools"
    assert anyviewer["homepage"] == "https://www.aomeitech.com/anyviewer/"
