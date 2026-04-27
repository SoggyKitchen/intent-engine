"""
Drop any affiliate network CSV into data/affiliate-imports/ and push.
This script detects the network format, normalises to CJ-style columns,
runs the importer, then moves the file to data/affiliate-imports/processed/.

Supported networks (auto-detected by header row):
  - CJ Affiliate   : ADVERTISER, CATEGORY, LINK
  - ShareASale     : Merchant, Category, Affiliate Link
  - Impact Radius  : Brand/Advertiser, Category, Tracking Link / Deep Link URL
  - Awin           : Advertiser Name, Category, Deep Link
  - Generic        : any CSV with a URL-like column — best-effort import

Run:
  uv run python scripts/process_affiliate_drop.py [--dry-run]
"""
import argparse
import csv
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DROPS = ROOT / "data" / "affiliate-imports"
PROCESSED = DROPS / "processed"

sys.path.insert(0, str(ROOT))
from publisher.affiliate_importer import import_affiliate_bundle
from publisher.affiliate_registry import IMPORTED_AFFILIATE_PATH, OVERRIDES_PATH


_NETWORK_SIGNATURES = {
    "cj": {"ADVERTISER", "CATEGORY", "LINK"},
    "shareasale": {"Merchant", "Category", "Affiliate Link"},
    "impact": {"Brand", "Tracking Link"},
    "impact_alt": {"Advertiser", "Deep Link URL"},
    "awin": {"Advertiser Name", "Deep Link"},
}


def detect_network(headers: list[str]) -> str:
    hset = set(headers)
    for network, required in _NETWORK_SIGNATURES.items():
        if required.issubset(hset):
            return network.split("_")[0]
    return "generic"


def normalise_row(row: dict, network: str) -> dict | None:
    """Return a CJ-normalised dict or None to skip."""
    def g(*keys):
        for k in keys:
            v = (row.get(k) or "").strip()
            if v:
                return v
        return ""

    if network == "cj":
        return row

    if network == "shareasale":
        return {
            "ADVERTISER": g("Merchant"),
            "CATEGORY": g("Category"),
            "LINK": g("Affiliate Link"),
            "NAME": g("Link Name", "Link Description", "Merchant"),
            "DESCRIPTION": g("Description", "Merchant"),
            "7-Day EPC": g("EPC (7 Day)", "7 Day EPC"),
        }

    if network == "impact":
        return {
            "ADVERTISER": g("Brand", "Advertiser"),
            "CATEGORY": g("Category", "Vertical"),
            "LINK": g("Tracking Link", "Deep Link URL"),
            "NAME": g("Ad Name", "Campaign Name", "Brand"),
            "DESCRIPTION": g("Description", "Brand"),
            "7-Day EPC": "0",
        }

    if network == "awin":
        return {
            "ADVERTISER": g("Advertiser Name"),
            "CATEGORY": g("Category"),
            "LINK": g("Deep Link"),
            "NAME": g("Link Name", "Advertiser Name"),
            "DESCRIPTION": g("Description", "Advertiser Name"),
            "7-Day EPC": "0",
        }

    url_col = next(
        (k for k in row if re.search(r"link|url|href|tracking|affiliate", k, re.I)), None
    )
    name_col = next(
        (k for k in row if re.search(r"advertiser|merchant|brand|company|name", k, re.I)), None
    )
    cat_col = next(
        (k for k in row if re.search(r"categ|vertical|niche|industry", k, re.I)), None
    )
    if not url_col or not name_col:
        return None
    return {
        "ADVERTISER": (row.get(name_col) or "").strip(),
        "CATEGORY": (row.get(cat_col) or "software").strip() if cat_col else "computer software",
        "LINK": (row.get(url_col) or "").strip(),
        "NAME": (row.get(name_col) or "").strip(),
        "DESCRIPTION": "",
        "7-Day EPC": "0",
    }


def convert_to_cj(src: Path, tmp: Path, network: str) -> int:
    """Write a CJ-normalised copy of src to tmp. Returns row count."""
    with src.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = [normalise_row(r, network) for r in reader]
    rows = [r for r in rows if r and r.get("LINK")]
    if not rows:
        return 0
    fieldnames = ["ADVERTISER", "CATEGORY", "LINK", "NAME", "DESCRIPTION", "7-Day EPC"]
    with tmp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def process_file(path: Path, dry_run: bool) -> dict:
    with path.open(newline="", encoding="utf-8-sig") as f:
        headers = next(csv.reader(f), [])
    network = detect_network(headers)
    print(f"  → detected network: {network}")

    if network == "cj":
        src = path
    else:
        src = path.with_suffix(".cj_normalised.csv")
        count = convert_to_cj(path, src, network)
        print(f"  → normalised {count} rows to CJ format")
        if count == 0:
            print("  ✗ no usable rows — skipping")
            return {"status": "empty"}

    if dry_run:
        print("  [dry-run] would import", src)
        return {"status": "dry-run"}

    result = import_affiliate_bundle(str(src), overrides_path=OVERRIDES_PATH, links_path=str(IMPORTED_AFFILIATE_PATH))
    if network != "cj" and src.exists():
        src.unlink()

    PROCESSED.mkdir(parents=True, exist_ok=True)
    dest = PROCESSED / path.name
    if dest.exists():
        dest = PROCESSED / (path.stem + "_2" + path.suffix)
    shutil.move(str(path), str(dest))
    print(f"  ✓ moved to processed/")
    return {"status": "ok", "result": result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    csvs = sorted(DROPS.glob("*.csv")) + sorted(DROPS.glob("*.CSV"))
    if not csvs:
        print("No CSVs found in data/affiliate-imports/ — nothing to do.")
        return

    total_advertisers = 0
    for csv_path in csvs:
        print(f"\nProcessing: {csv_path.name}")
        res = process_file(csv_path, args.dry_run)
        if res.get("status") == "ok":
            a = res["result"].get("links_summary", {}).get("advertiser_count", 0)
            total_advertisers += a
            print(f"  → {a} advertisers imported")

    print(f"\nDone. Total new advertisers across all files: {total_advertisers}")
    if total_advertisers and not args.dry_run:
        print("Run 'uv run engine publish' to inject links into pages.")


if __name__ == "__main__":
    main()
