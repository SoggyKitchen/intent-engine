import csv
import shutil
from pathlib import Path

from scripts.process_affiliate_drop import convert_to_cj


def test_affiliate_drop_normalises_generic_network_to_importer_schema():
    base = Path("test-temp/affiliate-drop")
    if base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True)

    src = base / "awin.csv"
    with src.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Advertiser Name", "Category", "Deep Link", "Link ID"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "Advertiser Name": "Example SaaS",
                "Category": "CRM",
                "Deep Link": "https://example.com/trial",
                "Link ID": "12345",
            }
        )

    out = base / "normalised.csv"
    count = convert_to_cj(src, out, "awin")

    rows = list(csv.DictReader(out.open("r", encoding="utf-8")))
    assert count == 1
    assert rows[0]["CLICK URL"] == "https://example.com/trial"
    assert rows[0]["RELATIONSHIP STATUS"] == "Active"
    assert rows[0]["LINK TYPE"] == "Text Link"

    shutil.rmtree(base)
