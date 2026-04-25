from scripts import youtube_bridge


def test_build_page_index_uses_clean_titles_and_strong_keys(monkeypatch):
    monkeypatch.setattr(
        youtube_bridge,
        "_load_pages",
        lambda: [
            {
                "title": "Ahrefs Pricing 2026: Plans, Costs & What You Actually Pay | SaaSpare",
                "url": "https://saaspare.org/pages/ahrefs-pricing-2026",
                "slug": "ahrefs-pricing-2026",
                "vertical": "seo_tools",
                "page_type": "pricing",
                "keywords": ["ahrefs", "seo_tools"],
            }
        ],
    )

    manifest = youtube_bridge.build_page_index()

    assert manifest["total"] == 1
    assert manifest["pages"]["ahrefs-pricing-2026-plans-costs-what-you-actually-pay"] == "https://saaspare.org/pages/ahrefs-pricing-2026"
    assert manifest["pages"]["ahrefs"] == "https://saaspare.org/pages/ahrefs-pricing-2026"
    assert "2026" not in manifest["pages"]


def test_clean_title_strips_brand_suffix():
    assert youtube_bridge.clean_title("Ahrefs Review | SaaSpare") == "Ahrefs Review"
