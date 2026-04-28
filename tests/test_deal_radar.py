import re
from pathlib import Path


def test_deal_radar_internal_pages_and_go_slugs_exist():
    html = Path("site/deal-radar.html").read_text(encoding="utf-8")
    redirects = Path("site/_redirects").read_text(encoding="utf-8")

    page_paths = re.findall(r'page:"([^"]+)"', html)
    slugs = re.findall(r'slug:"([^"]+)"', html)

    assert page_paths
    assert slugs

    for page_path in page_paths:
        assert (Path("site") / page_path.lstrip("/")).exists(), page_path

    for slug in slugs:
        assert re.search(rf"^/go/{re.escape(slug)}\s", redirects, re.MULTILINE), slug
