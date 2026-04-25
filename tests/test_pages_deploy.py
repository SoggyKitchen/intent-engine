from publisher.pages_deploy import _detect_page_type, _page_label


def test_page_label_preserves_brands():
    assert _page_label("hubspot-pricing-2026-plans-costs-what-you-actually-pay") == "HubSpot Pricing"
    assert _page_label("ahrefs-vs-se-ranking-which-is-better-in-2026") == "Ahrefs vs SE Ranking Which Is Better In"


def test_detect_page_type_covers_core_templates():
    assert _detect_page_type("ahrefs-vs-semrush-which-is-better-in-2026") == "comparison"
    assert _detect_page_type("hubspot-pricing-2026-plans-costs-what-you-actually-pay") == "pricing"
    assert _detect_page_type("best-semrush-alternatives-in-2026-free-paid") == "alternatives"
