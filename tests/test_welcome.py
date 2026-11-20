"""Contract tests for the native GET /welcome HTTP route (stdlib only)."""

from __future__ import annotations

import http.client
import json
import threading
from collections.abc import Iterator

import pytest
from app import create_server


@pytest.fixture
def server_address() -> Iterator[tuple[str, int]]:
    """Start the welcome server on an ephemeral loopback port for one test."""
    server = create_server("127.0.0.1", 0)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield host, port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _get(address: tuple[str, int], path: str) -> tuple[int, str, bytes]:
    """Issue one real loopback GET and return (status, content_type, body)."""
    host, port = address
    conn = http.client.HTTPConnection(host, port, timeout=5)
    try:
        conn.request("GET", path)
        response = conn.getresponse()
        return response.status, response.getheader("Content-Type", ""), response.read()
    finally:
        conn.close()


def test_welcome_returns_200(server_address: tuple[str, int]) -> None:
    status, _, _ = _get(server_address, "/welcome")
    assert status == 200


def test_welcome_returns_expected_json(server_address: tuple[str, int]) -> None:
    _, _, body = _get(server_address, "/welcome")
    assert json.loads(body) == {"message": "welcome"}


def test_welcome_content_type_is_json(server_address: tuple[str, int]) -> None:
    _, content_type, _ = _get(server_address, "/welcome")
    assert content_type.startswith("application/json")


def test_other_path_returns_404(server_address: tuple[str, int]) -> None:
    status, _, _ = _get(server_address, "/other")
    assert status == 404
