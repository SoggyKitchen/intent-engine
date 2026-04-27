import re
from pathlib import Path


def test_shortlist_internal_pages_and_go_slugs_exist():
    shortlist = Path("site/shortlist.html").read_text(encoding="utf-8")
    redirects = Path("site/_redirects").read_text(encoding="utf-8")

    page_paths = re.findall(r'page:"([^"]+)"', shortlist)
    slugs = re.findall(r'slug:"([^"]+)"', shortlist)

    assert page_paths
    assert slugs

    for page_path in page_paths:
        local_path = Path("site") / page_path.lstrip("/")
        assert local_path.exists(), f"shortlist page link is missing: {page_path}"

    for slug in slugs:
        assert re.search(rf"^/go/{re.escape(slug)}\s", redirects, re.MULTILINE), f"shortlist redirect is missing: /go/{slug}"
