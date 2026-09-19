"""GET /applications and GET /applications/stats."""

from __future__ import annotations


def test_list_returns_all_seed_records(client):
    resp = client.get("/applications")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 4
    assert len(body["items"]) == 4


def test_list_filters_by_status(client):
    resp = client.get("/applications", params={"status": "accepted"})
    body = resp.json()
    assert body["total"] == 2
    assert all(item["status"] == "accepted" for item in body["items"])


def test_list_filters_by_university_case_insensitive(client):
    resp = client.get("/applications", params={"university": "knust"})
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["university"] == "KNUST"


def test_list_filters_by_track_case_insensitive(client):
    resp = client.get("/applications", params={"track": "embedded"})
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["track"] == "Embedded Systems"


def test_list_search_matches_name_or_email(client):
    resp = client.get("/applications", params={"search": "yaw"})
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["fullName"] == "Yaw Mensah"


def test_list_pagination_limit_and_offset(client):
    first_page = client.get("/applications", params={"limit": 2, "offset": 0}).json()
    second_page = client.get("/applications", params={"limit": 2, "offset": 2}).json()

    assert first_page["total"] == 4
    assert len(first_page["items"]) == 2
    assert len(second_page["items"]) == 2

    first_ids = {item["id"] for item in first_page["items"]}
    second_ids = {item["id"] for item in second_page["items"]}
    assert first_ids.isdisjoint(second_ids)


def test_list_rejects_limit_over_100(client):
    resp = client.get("/applications", params={"limit": 500})
    assert resp.status_code == 422


def test_stats_counts_by_status_and_university(client):
    resp = client.get("/applications/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 4
    assert body["byStatus"]["accepted"] == 2
    assert body["byStatus"]["pending"] == 1
    assert body["byStatus"]["rejected"] == 1
    assert body["innovationClubOptIns"] == 3


def test_stats_route_does_not_collide_with_id_route(client):
    """'stats' must never be parsed as an {application_id} path param."""
    resp = client.get("/applications/stats")
    assert resp.status_code == 200
    assert "error" not in resp.json()
