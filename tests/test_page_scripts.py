import re
import shutil
import subprocess
from pathlib import Path

from outputs.seo_page import _JINJA_ENV


def _assert_javascript_syntax(source: str, tmp_path: Path):
    node = shutil.which("node")
    if not node:
        assert "function trackEvent(name, params){" in source
        return
    script_path = tmp_path / "snippet.js"
    script_path.write_text(source, encoding="utf-8")
    result = subprocess.run([node, "--check", str(script_path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_comparison_template_inline_script_is_syntax_valid(tmp_path):
    template = _JINJA_ENV.get_template("comparison_page.html.j2")
    html = template.render(
        title="HubSpot vs Salesforce",
        meta_description="desc",
        canonical_url="https://saaspare.org/pages/hubspot-vs-salesforce",
        site_domain="https://saaspare.org",
        schema_json="",
        ga_id="",
        subtitle="subtitle",
        updated_date="April 27, 2026",
        tldr="summary",
        tools=[
            {
                "name": "HubSpot",
                "winner": True,
                "description": "desc",
                "pros": ["pro"],
                "cons": ["con"],
                "pricing": "$50",
                "affiliate_url": "/go/hubspot",
            }
        ],
        comparison_features=[{"name": "Pricing", "values": ["$50"]}],
        cta_url="/go/hubspot",
        cta_text="Try the top pick",
        cta_button="Start Free Trial",
        cta_tool_name="HubSpot",
        faqs=[{"question": "q", "answer": "a"}],
        deep_sections=[],
        newsletter_form_action="https://example.com/form",
        page_slug="hubspot-vs-salesforce",
        page_type="comparison",
        vertical="crm",
        related_pages=[],
    )
    scripts = re.findall(r"<script>(.*?)</script>", html, re.DOTALL)
    inline_script = scripts[-1]

    assert "utm_source:params.get('utm_source')||''" in inline_script
    _assert_javascript_syntax(inline_script, tmp_path)


def test_roi_calculator_scripts_are_syntax_valid(tmp_path):
    html = Path("site/pages/saas-roi-calculator.html").read_text(encoding="utf-8")
    scripts = re.findall(r"<script>(.*?)</script>", html, re.DOTALL)
    inline_source = "\n".join(scripts)

    assert '/go/hubspot' in html
    _assert_javascript_syntax(inline_source, tmp_path)
