from pathlib import Path
from typing import Iterable

from publisher.affiliate_importer import import_affiliate_bundle
from publisher.affiliate_registry import IMPORTED_AFFILIATE_PATH, OVERRIDES_PATH


def main(argv: Iterable[str] | None = None):
    import argparse

    parser = argparse.ArgumentParser(description="Import CJ affiliate links into overrides and redirect data")
    parser.add_argument("csv_path", help="Path to a CJ export like links.csv")
    parser.add_argument("--output", default=str(IMPORTED_AFFILIATE_PATH), help="Output affiliate-links JSON path")
    args = parser.parse_args(list(argv) if argv is not None else None)

    result = import_affiliate_bundle(args.csv_path, overrides_path=OVERRIDES_PATH, links_path=args.output)
    print(
        f"Imported {result['links_summary']['advertiser_count']} advertisers into "
        f"{result['links_path']} and {result['overrides_summary']['links_selected']} "
        f"curated overrides into {result['overrides_path']}"
    )


if __name__ == "__main__":
    main()
