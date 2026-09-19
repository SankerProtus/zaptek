"""PATCH /applications/{id}/status — the transition table."""

from __future__ import annotations

import pytest


def test_pending_can_move_to_accepted(client):
    resp = client.patch("/applications/3/status", json={"status": "accepted"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"


def test_pending_can_move_to_rejected(client):
    resp = client.patch("/applications/3/status", json={"status": "rejected"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "rejected"


def test_accepted_can_move_to_rejected(client):
    resp = client.patch("/applications/2/status", json={"status": "rejected"})
    assert resp.status_code == 200


def test_rejected_is_terminal(client):
    """id 5 starts rejected in the seed data; no move out is allowed."""
    resp = client.patch("/applications/5/status", json={"status": "accepted"})
    assert resp.status_code == 409
    body = resp.json()
    assert body["error"]["code"] == "INVALID_STATUS_TRANSITION"
    assert body["error"]["details"]["current_status"] == "rejected"


def test_accepted_cannot_move_back_to_pending(client):
    resp = client.patch("/applications/2/status", json={"status": "pending"})
    assert resp.status_code == 409


def test_setting_same_status_is_a_no_op(client):
    """id 2 is already accepted — re-accepting should succeed, not 409."""
    resp = client.patch("/applications/2/status", json={"status": "accepted"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"


def test_status_change_accepts_optional_note(client):
    resp = client.patch(
        "/applications/3/status",
        json={"status": "accepted", "note": "Strong RF background"},
    )
    assert resp.status_code == 200
    assert resp.json()["statusNote"] == "Strong RF background"


def test_status_change_on_missing_application_returns_404(client):
    resp = client.patch("/applications/999/status", json={"status": "accepted"})
    assert resp.status_code == 404


@pytest.mark.parametrize("bad_status", ["approved", "denied", ""])
def test_status_change_rejects_unknown_status_values(client, bad_status):
    resp = client.patch("/applications/3/status", json={"status": bad_status})
    assert resp.status_code == 422
