"""Shared test fixtures."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("ADMIN_RESET_TOKEN", "test-admin-token")

from app.data import mock_data
from app.main import app


@pytest.fixture()
def client():
    mock_data.reset_data()
    with TestClient(app) as test_client:
        test_client.headers["X-Admin-Token"] = "test-admin-token"
        yield test_client
    mock_data.reset_data()


@pytest.fixture()
def new_application_payload() -> dict:
    """A minimal, valid payload for POST /applications."""
    return {
        "fullName": "Kwabena Owusu",
        "email": "kwabena.owusu@example.com",
        "phone": "+233 24 111 2233",
        "university": "KNUST",
        "course": "Computer Science",
        "level": "4th Year",
        "track": "Backend Engineering",
        "motivation": "I want to deepen my FastAPI and systems design knowledge.",
        "portfolioLink": "https://github.com/kwabena",
        "joinInnovationClub": True,
    }
