"""POST /applications — creation, validation, and duplicate handling."""

from __future__ import annotations


def test_create_application_succeeds(client, new_application_payload):
    resp = client.post("/applications", json=new_application_payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["fullName"] == "Kwabena Owusu"
    assert body["status"] == "pending"
    assert "submittedAt" in body


def test_create_rejects_client_supplied_id_and_status(client, new_application_payload):
    """Server-controlled fields cannot be smuggled into a create payload."""
    payload = dict(new_application_payload, id=999, status="accepted")
    resp = client.post("/applications", json=payload)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_normalises_phone_number(client, new_application_payload):
    resp = client.post("/applications", json=new_application_payload)
    body = resp.json()
    assert body["phone"] == "0241112233"


def test_create_defaults_whatsapp_to_phone_when_omitted(
    client, new_application_payload
):
    assert "whatsappNumber" not in new_application_payload
    resp = client.post("/applications", json=new_application_payload)
    body = resp.json()
    assert body["whatsappNumber"] == body["phone"]


def test_create_duplicate_email_returns_409(client, new_application_payload):
    client.post("/applications", json=new_application_payload)
    resp = client.post("/applications", json=new_application_payload)
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "DUPLICATE_EMAIL"


def test_create_duplicate_email_is_case_insensitive(client, new_application_payload):
    client.post("/applications", json=new_application_payload)
    payload = dict(
        new_application_payload, email=new_application_payload["email"].upper()
    )
    resp = client.post("/applications", json=payload)
    assert resp.status_code == 409


def test_create_rejects_invalid_phone(client, new_application_payload):
    payload = dict(new_application_payload, phone="12345")
    resp = client.post("/applications", json=payload)
    assert resp.status_code == 422
    fields = resp.json()["error"]["details"]["fields"]
    assert any("phone" in f["field"] for f in fields)


def test_create_rejects_short_motivation(client, new_application_payload):
    payload = dict(new_application_payload, motivation="Too short")
    resp = client.post("/applications", json=payload)
    assert resp.status_code == 422


def test_create_rejects_single_word_name(client, new_application_payload):
    payload = dict(new_application_payload, fullName="Kwabena")
    resp = client.post("/applications", json=payload)
    assert resp.status_code == 422


def test_create_rejects_unknown_level(client, new_application_payload):
    payload = dict(new_application_payload, level="5th Year")
    resp = client.post("/applications", json=payload)
    assert resp.status_code == 422


def test_error_envelope_shape_is_consistent_for_validation_errors(
    client, new_application_payload
):
    payload = dict(new_application_payload, email="not-an-email")
    resp = client.post("/applications", json=payload)
    body = resp.json()
    assert set(body["error"].keys()) == {"code", "message", "details"}
    assert body["error"]["code"] == "VALIDATION_ERROR"
