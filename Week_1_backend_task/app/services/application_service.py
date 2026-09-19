"""Business logic for applications."""

from __future__ import annotations

from typing import Any, Optional

from app.core.exceptions import (
    ApplicationNotFound,
    DuplicateEmail,
    InvalidStatusTransition,
)
from app.data import mock_data
from app.models.application import (
    ApplicationCreate,
    ApplicationUpdate,
    Status,
)

ALLOWED_TRANSITIONS: dict[Status, set[Status]] = {
    Status.PENDING: {Status.ACCEPTED, Status.REJECTED},
    Status.ACCEPTED: {Status.REJECTED},
    Status.REJECTED: set(),
}


def list_applications(
    *,
    status: Optional[Status] = None,
    university: Optional[str] = None,
    track: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    """Filtered, paginated read. Returns (page, total_matching)."""
    records = mock_data.all_records()

    if status is not None:
        records = [r for r in records if r["status"] == status.value]

    if university:
        needle = university.strip().lower()
        records = [r for r in records if needle in r["university"].lower()]

    if track:
        needle = track.strip().lower()
        records = [r for r in records if needle in r["track"].lower()]

    if search:
        needle = search.strip().lower()
        records = [
            r
            for r in records
            if needle in r["fullName"].lower() or needle in r["email"].lower()
        ]

    records.sort(key=lambda r: r["submittedAt"], reverse=True)

    total = len(records)
    return records[offset : offset + limit], total


def get_application(application_id: int) -> dict[str, Any]:
    record = mock_data.find_by_id(application_id)
    if record is None:
        raise ApplicationNotFound(
            f"No application exists with id {application_id}.",
            application_id=application_id,
        )
    return record


def create_application(payload: ApplicationCreate) -> dict[str, Any]:
    if mock_data.find_by_email(payload.email) is not None:
        raise DuplicateEmail(
            f"An application from {payload.email} already exists.",
            email=payload.email,
        )

    record = payload.model_dump(mode="json", by_alias=True)

    record["id"] = mock_data.next_id()
    record["status"] = Status.PENDING.value
    record["submittedAt"] = mock_data.now_iso()

    try:
        return mock_data.insert(record)
    except ValueError as exc:
        raise DuplicateEmail(
            f"An application from {payload.email} already exists.",
            email=payload.email,
        ) from exc


def update_application(
    application_id: int, payload: ApplicationUpdate
) -> dict[str, Any]:
    existing = get_application(application_id)

    changes = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)

    new_email = changes.get("email")
    if new_email and new_email.lower() != existing["email"].lower():
        clash = mock_data.find_by_email(new_email)
        if clash is not None:
            raise DuplicateEmail(
                f"Another application already uses {new_email}.", email=new_email
            )

    existing.update(changes)
    try:
        updated = mock_data.replace(application_id, existing)
    except ValueError as exc:
        raise DuplicateEmail(
            f"Another application already uses {new_email}.", email=new_email
        ) from exc
    if updated is None:  # pragma: no cover - guarded by get_application above
        raise ApplicationNotFound(application_id=application_id)
    return updated


def change_status(
    application_id: int, new_status: Status, note: Optional[str] = None
) -> dict[str, Any]:
    existing = get_application(application_id)
    current = Status(existing["status"])

    if new_status == current:
        return existing

    if new_status not in ALLOWED_TRANSITIONS[current]:
        raise InvalidStatusTransition(
            f"Cannot move an application from '{current.value}' "
            f"to '{new_status.value}'.",
            current_status=current.value,
            requested_status=new_status.value,
            allowed=sorted(s.value for s in ALLOWED_TRANSITIONS[current]),
        )

    existing["status"] = new_status.value
    if note:
        existing["statusNote"] = note

    updated = mock_data.replace(application_id, existing)
    return updated  # type: ignore[return-value]


def delete_application(application_id: int) -> None:
    if not mock_data.remove(application_id):
        raise ApplicationNotFound(
            f"No application exists with id {application_id}.",
            application_id=application_id,
        )


def stats() -> dict[str, Any]:
    """Return aggregate application counts."""
    records = mock_data.all_records()
    by_status: dict[str, int] = {s.value: 0 for s in Status}
    by_university: dict[str, int] = {}

    for record in records:
        by_status[record["status"]] = by_status.get(record["status"], 0) + 1
        uni = record["university"]
        by_university[uni] = by_university.get(uni, 0) + 1

    return {
        "total": len(records),
        "byStatus": by_status,
        "byUniversity": by_university,
        "innovationClubOptIns": sum(1 for r in records if r.get("joinInnovationClub")),
    }
