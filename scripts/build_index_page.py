"""Rebuilds site/pages/index.html.

Delegates to the canonical rich generator (publisher.pages_deploy._rebuild_pages_index)
so CI and manual runs always produce the same premium library page (plexus-sphere hero,
logo comparison rows, buyer-intent sidebar) instead of a divergent simple grid.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from publisher.pages_deploy import _rebuild_pages_index


def build():
    _rebuild_pages_index(Path("site"))


if __name__ == "__main__":
    build()
