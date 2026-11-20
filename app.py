"""Minimal stdlib HTTP service exposing the native GET /welcome route.

This is a standalone runnable script kept outside the ``src/octop_harness``
distribution package: the library itself gains no HTTP server. It uses only
the Python standard library (``http.server``), so it adds no runtime deps.
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

_WELCOME_BODY = json.dumps({"message": "welcome"}).encode("utf-8")


class WelcomeHandler(BaseHTTPRequestHandler):
    """Serve GET /welcome as JSON; return 404 for every other path."""

    def do_GET(self) -> None:
        if self.path == "/welcome":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(_WELCOME_BODY)))
            self.end_headers()
            self.wfile.write(_WELCOME_BODY)
        else:
            self.send_error(404)

    def log_message(self, format: str, *args: object) -> None:
        """Silence default stderr request logging (keeps test output clean)."""
        return


def create_server(host: str = "127.0.0.1", port: int = 0) -> ThreadingHTTPServer:
    """Build a server; port=0 lets the OS pick a free port (used by tests)."""
    return ThreadingHTTPServer((host, port), WelcomeHandler)


def main(argv: list[str] | None = None) -> None:
    """Start the service. An optional first CLI arg overrides the port.

    ``python3 app.py {port}`` lets a caller (e.g. the platform runtime) bind a
    specific ephemeral port; otherwise WELCOME_PORT / 8000 is used.
    """
    args = sys.argv[1:] if argv is None else argv
    host = os.environ.get("WELCOME_HOST", "127.0.0.1")
    port = int(args[0]) if args else int(os.environ.get("WELCOME_PORT", "8000"))
    server = create_server(host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
