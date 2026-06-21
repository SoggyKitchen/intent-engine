"""Tests for the autonomous-operator circuit breaker."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "seo"))

import operator_circuit_breaker as cb  # noqa: E402


SAMPLE_DIFF = """\
diff --git a/site/pages/foo.html b/site/pages/foo.html
--- a/site/pages/foo.html
+++ b/site/pages/foo.html
-<title>Old Title 2026: Honest Verdict</title>
+<title>New Title 2026: Honest Verdict After Testing</title>
-<meta name="description" content="old desc">
+<meta name="description" content="new desc">
-<link rel="canonical" href="https://saaspare.org/pages/foo">
+<link rel="canonical" href="https://saaspare.org/pages/foo-fixed">
"""


def test_counts_title_and_meta_changes():
    titles, metas = cb.count_metadata_changes(SAMPLE_DIFF)
    assert titles == 1
    assert metas == 1


def test_canonical_change_not_counted():
    # Structural fixes must not trip the breaker.
    diff = (
        "-<link rel=\"canonical\" href=\"https://saaspare.org/a\">\n"
        "+<link rel=\"canonical\" href=\"https://saaspare.org/b\">\n"
    )
    titles, metas = cb.count_metadata_changes(diff)
    assert titles == 0
    assert metas == 0


def test_empty_diff_is_zero():
    assert cb.count_metadata_changes("") == (0, 0)


def test_indented_title_counted():
    diff = "-  <title>Indented Old</title>\n+  <title>Indented New 2026: Real Cost</title>\n"
    titles, _ = cb.count_metadata_changes(diff)
    assert titles == 1
