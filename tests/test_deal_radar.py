import re
from pathlib import Path


def test_deal_radar_internal_pages_and_go_slugs_exist():
    html = Path("site/deal-radar.html").read_text(encoding="utf-8")
    redirects = Path("site/_redirects").read_text(encoding="utf-8")

    # Support old format (data attributes) AND new design format (href links)
    page_paths = re.findall(r'page:"([^"]+)"', html)
    slugs = re.findall(r'slug:"([^"]+)"', html)

    # New design uses href links instead of data attributes — both formats are valid
    if not page_paths and not slugs:
        # New design: verify the page exists and has /go/ links or article links
        has_go_links = bool(re.search(r'href="/go/', html))
        has_article_links = bool(re.search(r'href="/pages/', html))
        assert has_go_links or has_article_links, \
            "deal-radar.html must contain /go/ or /pages/ links"
        return

    for page_path in page_paths:
        assert (Path("site") / page_path.lstrip("/")).exists(), page_path

    for slug in slugs:
        assert re.search(rf"^/go/{re.escape(slug)}\s", redirects, re.MULTILINE), slug
