"""GET /applications/{id}."""

from __future__ import annotations


def test_get_existing_application(client):
    resp = client.get("/applications/2")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == 2
    assert body["fullName"] == "Ama Serwaa Owusu"


def test_get_missing_application_returns_404_envelope(client):
    resp = client.get("/applications/999")
    assert resp.status_code == 404
    body = resp.json()
    assert body["error"]["code"] == "APPLICATION_NOT_FOUND"
    assert body["error"]["details"]["application_id"] == 999


def test_get_rejects_non_positive_id(client):
    resp = client.get("/applications/0")
    assert resp.status_code == 422
