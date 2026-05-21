"""Tiny preview server that mimics Cloudflare Pages' auto .html resolution.

Run from project root:
    uv run python scripts/preview_server.py

Then open http://127.0.0.1:8000/pages/v3-preview-index
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1] / "site"
PORT = 8000


class PrettyURLHandler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def translate_path(self, path: str) -> str:
        # Strip query string for filesystem lookup.
        bare = path.split("?", 1)[0].split("#", 1)[0]
        fs = super().translate_path(bare)
        # If the requested file does not exist, try `.html`.
        if not os.path.exists(fs) and not bare.endswith("/"):
            html = fs + ".html"
            if os.path.exists(html):
                return html
        # If a directory was requested, fall back to its index.html as usual.
        return fs


if __name__ == "__main__":
    print(f"Serving {ROOT} on http://127.0.0.1:{PORT}")
    print(f"Open: http://127.0.0.1:{PORT}/pages/v3-preview-index")
    with ThreadingHTTPServer(("127.0.0.1", PORT), PrettyURLHandler) as srv:
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            pass
