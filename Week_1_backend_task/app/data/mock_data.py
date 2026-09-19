"""Thread-safe in-memory datastore for local development and tests."""

from __future__ import annotations

import copy
import threading
from datetime import datetime, timezone
from itertools import count
from typing import Any, Iterator, Optional

SEED_APPLICATIONS: list[dict[str, Any]] = [
    {
        "id": 2,
        "fullName": "Ama Serwaa Owusu",
        "email": "amaserwaa@gmail.com",
        "phone": "0245567812",
        "whatsappNumber": "0245567812",
        "university": "University of Ghana",
        "course": "Computer Engineering",
        "level": "2nd Year",
        "track": "Embedded Systems",
        "motivation": (
            "I want to gain hands-on experience in embedded systems "
            "and IoT development."
        ),
        "portfolioLink": "https://github.com/amase",
        "resumeLink": "https://linkedin.com/in/amase",
        "joinInnovationClub": True,
        "status": "accepted",
        "submittedAt": "2026-05-04T10:12:45Z",
    },
    {
        "id": 3,
        "fullName": "Yaw Mensah",
        "email": "yawmensah@gmail.com",
        "phone": "0558876123",
        "whatsappNumber": "0558876123",
        "university": "KNUST",
        "course": "Electrical Engineering",
        "level": "4th Year",
        "track": "Radar & RF Systems",
        "motivation": (
            "To improve my knowledge in RF systems, radar engineering, "
            "and wireless communications."
        ),
        "portfolioLink": "https://github.com/yawmensah",
        "resumeLink": "https://linkedin.com/in/yawmensah",
        "joinInnovationClub": True,
        "status": "pending",
        "submittedAt": "2026-05-05T08:45:30Z",
    },
    {
        "id": 4,
        "fullName": "Priscilla Adjei",
        "email": "priscilla.adjei@gmail.com",
        "phone": "0203344556",
        "whatsappNumber": "0203344556",
        "university": "Ashesi University",
        "course": "Software Engineering",
        "level": "3rd Year",
        "track": "Backend Engineering",
        "motivation": (
            "I want to strengthen my backend engineering skills using FastAPI "
            "and modern software architecture."
        ),
        "portfolioLink": "https://github.com/priscillaadjei",
        "resumeLink": "https://linkedin.com/in/priscillaadjei",
        "joinInnovationClub": True,
        "status": "accepted",
        "submittedAt": "2026-05-06T14:18:22Z",
    },
    {
        "id": 5,
        "fullName": "Daniel Kofi Asante",
        "email": "danielasante@gmail.com",
        "phone": "0277788990",
        "whatsappNumber": "0277788990",
        "university": "UENR",
        "course": "Biomedical Engineering",
        "level": "2nd Year",
        "track": "Biomedical Systems",
        "motivation": (
            "To explore biomedical monitoring systems and healthcare "
            "technology innovations."
        ),
        "portfolioLink": "https://github.com/danielasante",
        "resumeLink": "https://linkedin.com/in/danielasante",
        "joinInnovationClub": False,
        "status": "rejected",
        "submittedAt": "2026-05-07T11:05:10Z",
    },
]


_applications: list[dict[str, Any]] = []
_id_counter: Iterator[int] = count(1)
_lock = threading.RLock()


def reset_data() -> None:
    """Restore seed records and reset the id counter."""
    global _applications, _id_counter
    with _lock:
        _applications = copy.deepcopy(SEED_APPLICATIONS)
        highest = max((record["id"] for record in _applications), default=0)
        _id_counter = count(highest + 1)


def next_id() -> int:
    with _lock:
        return next(_id_counter)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def all_records() -> list[dict[str, Any]]:
    """A safe copy of every record."""
    with _lock:
        return copy.deepcopy(_applications)


def find_by_id(application_id: int) -> Optional[dict[str, Any]]:
    with _lock:
        for record in _applications:
            if record["id"] == application_id:
                return copy.deepcopy(record)
    return None


def find_by_email(email: str) -> Optional[dict[str, Any]]:
    target = email.strip().lower()
    with _lock:
        for record in _applications:
            if record["email"].lower() == target:
                return copy.deepcopy(record)
    return None


def insert(record: dict[str, Any]) -> dict[str, Any]:
    with _lock:
        if find_by_email(record["email"]) is not None:
            raise ValueError("duplicate email")
        _applications.append(copy.deepcopy(record))
        return copy.deepcopy(record)


def replace(application_id: int, record: dict[str, Any]) -> Optional[dict[str, Any]]:
    with _lock:
        for index, existing in enumerate(_applications):
            if existing["id"] == application_id:
                duplicate = next(
                    (
                        item
                        for item in _applications
                        if item["id"] != application_id
                        and item["email"].lower() == record["email"].lower()
                    ),
                    None,
                )
                if duplicate is not None:
                    raise ValueError("duplicate email")
                _applications[index] = copy.deepcopy(record)
                return copy.deepcopy(record)
    return None


def remove(application_id: int) -> bool:
    with _lock:
        for index, existing in enumerate(_applications):
            if existing["id"] == application_id:
                del _applications[index]
                return True
    return False


reset_data()
