from publisher.seo_tags import get_seo_tags


def test_exact_searchatlas_export_wins():
    tags = get_seo_tags("/pages/ahrefs-vs-semrush-which-is-better-in-2026")
    assert tags["title"] == "Ahrefs vs. Semrush: Which SEO Tool Is Right for You? | SaaSpare"
    assert "Compare Ahrefs vs. Semrush in 2026" in tags["meta_description"]


def test_pattern_generates_comparison_tags_from_slug():
    tags = get_seo_tags(
        "/pages/monday-com-vs-asana-which-is-better-in-2026",
        category="project_management",
    )
    assert tags["title"] == "Monday.com vs. Asana: Which Project Management Is Best in 2026? | SaaSpare"
    assert "Compare Monday.com vs. Asana in 2026" in tags["meta_description"]


def test_pattern_generates_pricing_tags_without_title_duplication():
    tags = get_seo_tags("/pages/ahrefs-pricing-2026-plans-costs-what-you-actually-pay")
    assert tags["title"].startswith("Ahrefs Pricing 2026")
    assert "Ahrefs Pricing 2026 Pricing" not in tags["title"]
