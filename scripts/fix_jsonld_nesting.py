"""
Fix nested/malformed JSON-LD blocks caused by double-wrapping.
Finds <script type="application/ld+json"> blocks containing nested script tags
and flattens them. Also removes empty JSON-LD script blocks.

Run: uv run python scripts/fix_jsonld_nesting.py
"""
import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

fixed = 0
all_html = (
    list((SITE / "pages").glob("*.html")) +
    list((SITE / "blog").glob("*.html")) +
    list((SITE / "authors").glob("*.html")) +
    [SITE / "index.html"]
)

def clean_jsonld(html):
    """Remove nested script tags inside JSON-LD blocks and fix double-wrapping."""
    changed = False

    # Remove empty JSON-LD script blocks
    new_html = re.sub(
        r'<script\s+type="application/ld\+json"\s*>\s*</script>',
        '',
        html
    )
    if new_html != html:
        changed = True
        html = new_html

    # Find JSON-LD blocks that contain nested <script> tags and unwrap the inner scripts
    # Pattern: <script type="application/ld+json">...<script type="application/ld+json">JSON</script>...</script>
    def fix_nested(m):
        outer_content = m.group(1)
        # If there are nested script tags inside, extract their content
        if '<script' in outer_content:
            # Remove the nested script tags but keep their content as separate blocks
            inner_scripts = re.findall(
                r'<script\s+type="application/ld\+json"\s*>(.*?)</script>',
                outer_content, re.DOTALL
            )
            # What's left after removing inner scripts
            remainder = re.sub(
                r'<script\s+type="application/ld\+json"\s*>.*?</script>',
                '',
                outer_content, flags=re.DOTALL
            ).strip()

            result_blocks = []
            # Add remainder if it's valid JSON
            if remainder.strip().startswith('{') or remainder.strip().startswith('['):
                try:
                    json.loads(remainder.strip())
                    result_blocks.append(f'<script type="application/ld+json">{remainder.strip()}</script>')
                except:
                    pass
            # Add inner scripts as separate blocks
            for inner in inner_scripts:
                inner = inner.strip()
                if inner:
                    try:
                        json.loads(inner)
                        result_blocks.append(f'<script type="application/ld+json">{inner}</script>')
                    except:
                        pass
            return '\n  '.join(result_blocks) if result_blocks else ''
        return m.group(0)

    new_html = re.sub(
        r'<script\s+type="application/ld\+json"\s*>(.*?)</script>',
        fix_nested,
        html, flags=re.DOTALL
    )
    if new_html != html:
        changed = True
        html = new_html

    return html, changed


for fp in sorted(all_html):
    try:
        content = fp.read_text(encoding='utf-8', errors='replace')
        cleaned, changed = clean_jsonld(content)
        if changed:
            fp.write_text(cleaned, encoding='utf-8')
            fixed += 1
    except Exception as e:
        print(f"  ERROR {fp.name}: {e}")

print(f"Fixed nested/malformed JSON-LD on {fixed} pages")
