"""Import affiliate tracking links from a CSV export into registry overrides.

Usage:
    .venv\\Scripts\\python scripts\\import_affiliate_links.py C:\\path\\to\\links.csv
"""

import sys

from publisher.affiliate_importer import import_affiliate_bundle


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_affiliate_links.py <links.csv> [output.json]")
        return 1
    csv_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    summary = import_affiliate_bundle(csv_path, links_path=output_path or "data/affiliate_links.json")
    print(
        f"Imported {summary['links_summary']['advertiser_count']} advertisers into "
        f"{summary['links_path']} and rebuilt {summary['overrides_summary']['links_selected']} curated overrides"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
