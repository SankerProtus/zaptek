"""/, /health, and the catch-all 500 handler."""

from __future__ import annotations


def test_root_returns_service_metadata(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["service"] == "ZapTek Applications API"
    assert body["docs"] == "/docs"


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["X-Request-ID"]


def test_docs_are_served(client):
    resp = client.get("/docs")
    assert resp.status_code == 200


def test_openapi_schema_is_valid_json(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert schema["info"]["title"] == "ZapTek Applications API"
    assert "/applications" in schema["paths"]


def test_unknown_route_uses_the_same_error_envelope(client):
    """Starlette's own 404 (no matching route) still gets our error shape."""
    resp = client.get("/this-route-does-not-exist")
    assert resp.status_code == 404
    body = resp.json()
    assert body["error"]["code"] == "HTTP_404"
