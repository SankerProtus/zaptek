"""DELETE endpoint and datastore regression tests."""

from __future__ import annotations

from app.data import mock_data


def test_delete_existing_application_returns_204(client):
    resp = client.delete("/applications/4")
    assert resp.status_code == 204
    assert resp.content == b""


def test_deleted_application_is_gone(client):
    client.delete("/applications/4")
    resp = client.get("/applications/4")
    assert resp.status_code == 404


def test_delete_missing_application_returns_404(client):
    resp = client.delete("/applications/999")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "APPLICATION_NOT_FOUND"


def test_delete_is_not_idempotent_on_the_second_call(client):
    first = client.delete("/applications/4")
    second = client.delete("/applications/4")
    assert first.status_code == 204
    assert second.status_code == 404


def test_new_id_never_collides_with_existing_ids(client, new_application_payload):
    """Seed data starts at id 2 with no id 1 — len()+1 would collide here."""
    existing_ids = {item["id"] for item in client.get("/applications").json()["items"]}
    created = client.post("/applications", json=new_application_payload).json()
    assert created["id"] not in existing_ids


def test_reads_return_copies_not_live_references(client):
    """Mutating a returned record must never affect the underlying store."""
    record = client.get("/applications/2").json()
    record["fullName"] = "Tampered Name"

    fresh = client.get("/applications/2").json()
    assert fresh["fullName"] == "Ama Serwaa Owusu"


def test_admin_reset_restores_seed_data(client):
    client.delete("/applications/2")
    assert client.get("/applications/2").status_code == 404

    resp = client.post("/admin/reset")
    assert resp.status_code == 200
    assert resp.json()["records"] == 4
    assert client.get("/applications/2").status_code == 200


def test_admin_reset_rejects_an_invalid_token(client):
    resp = client.post("/admin/reset", headers={"X-Admin-Token": "wrong"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "INVALID_ADMIN_TOKEN"
