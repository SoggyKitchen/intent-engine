from pathlib import Path

from publisher.affiliate_importer import import_affiliate_bundle
from publisher.affiliate_registry import IMPORTED_AFFILIATE_PATH


def import_csv(csv_path: str, output_path: str | None = None) -> tuple[int, str]:
    destination = Path(output_path) if output_path else IMPORTED_AFFILIATE_PATH
    summary = import_affiliate_bundle(csv_path, links_path=destination)
    count = summary["links_summary"]["advertiser_count"]
    return count, str(destination)
