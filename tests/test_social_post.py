from ops.social_post import (
    _build_social_calendar,
    _normalize_linkedin_person_urn,
    _render_social_pack_markdown,
)


def test_render_social_pack_markdown_includes_carousel_and_shot_list():
    markdown = _render_social_pack_markdown(
        [
            {
                "title": "HubSpot vs Salesforce",
                "url": "https://saaspare.org/pages/hubspot-vs-salesforce",
                "x_post": "x copy",
                "linkedin_post": "linkedin copy",
                "reddit_angle": "angle",
                "reddit_post": "reddit body",
                "instagram_caption": "caption",
                "instagram_carousel": ["slide 1", "slide 2"],
                "tiktok_script": "script",
                "tiktok_shot_list": ["shot 1", "shot 2"],
            }
        ]
    )

    assert "### Instagram Carousel" in markdown
    assert "- slide 1" in markdown
    assert "### TikTok Shot List" in markdown
    assert "- shot 2" in markdown
    assert "### Reddit Post" in markdown


def test_build_social_calendar_rotates_channels():
    calendar = _build_social_calendar(
        [
            {"title": "A", "url": "https://example.com/a"},
            {"title": "B", "url": "https://example.com/b"},
            {"title": "C", "url": "https://example.com/c"},
        ]
    )

    assert calendar[0]["day"] == "Monday"
    assert calendar[0]["channel"] == "X + LinkedIn"
    assert calendar[1]["channel"] == "Reddit"
    assert calendar[2]["channel"] == "Instagram"


def test_normalize_linkedin_person_urn_accepts_id_or_full_urn():
    assert _normalize_linkedin_person_urn("abc123") == "urn:li:person:abc123"
    assert _normalize_linkedin_person_urn("urn:li:person:abc123") == "urn:li:person:abc123"
