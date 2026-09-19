"""PATCH /applications/{id} — partial updates."""

from __future__ import annotations


def test_update_changes_only_supplied_fields(client):
    resp = client.patch("/applications/3", json={"track": "RF & Antenna Systems"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["track"] == "RF & Antenna Systems"
    assert body["fullName"] == "Yaw Mensah"


def test_update_missing_application_returns_404(client):
    resp = client.patch("/applications/999", json={"track": "Anything"})
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "APPLICATION_NOT_FOUND"


def test_update_to_duplicate_email_is_rejected(client):
    resp = client.patch("/applications/3", json={"email": "amaserwaa@gmail.com"})
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "DUPLICATE_EMAIL"


def test_update_keeping_own_email_is_allowed(client):
    resp = client.patch("/applications/3", json={"email": "yawmensah@gmail.com"})
    assert resp.status_code == 200


def test_update_normalises_phone(client):
    resp = client.patch("/applications/3", json={"phone": "+233 55 887 6123"})
    assert resp.status_code == 200
    assert resp.json()["phone"] == "0558876123"


def test_update_rejects_invalid_value(client):
    resp = client.patch("/applications/3", json={"level": "10th Year"})
    assert resp.status_code == 422


def test_update_cannot_set_status_directly(client):
    """status has its own endpoint; ApplicationUpdate has no status field."""
    resp = client.patch("/applications/2", json={"status": "rejected"})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
