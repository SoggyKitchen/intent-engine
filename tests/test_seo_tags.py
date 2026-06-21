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


def test_free_plan_template_does_not_corrupt_the_word_you():
    # Regression: a naive .replace("Y", category) rewrote the "Y" inside ordinary
    # words, turning "What You Get" -> "What Softwareou Get". Word-boundary
    # substitution must leave "You" intact.
    tags = get_seo_tags("/pages/does-amplitude-have-a-free-plan-2026", category="analytics")
    assert "What You Get" in tags["title"]
    assert "Softwareou" not in tags["title"]
    assert "Softwareou" not in tags["meta_description"]


def test_x_substitution_does_not_corrupt_brands_containing_x():
    # Regression: a naive .replace("X", value) rewrote the "X" inside "Xero".
    tags = get_seo_tags("/pages/xero-pricing-2026", category="accounting")
    assert tags["title"].startswith("Xero Pricing 2026")
    assert "Xeroero" not in tags["title"]
