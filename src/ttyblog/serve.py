"""tiny http.server wrapper for preview."""
from __future__ import annotations

import functools
import http.server
import socketserver
from pathlib import Path


def serve(directory: Path, port: int = 8000) -> None:
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(directory)
    )
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"serving {directory} at http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nbye")
