"""HTTP security dependencies."""

from __future__ import annotations

import secrets

from fastapi import Header

from app.core.config import settings
from app.core.exceptions import AdminResetNotConfigured, InvalidAdminToken


def require_admin_reset_token(
    token: str | None = Header(default=None, alias="X-Admin-Token"),
) -> None:
    if settings.admin_reset_token is None:
        raise AdminResetNotConfigured()
    if token is None or not secrets.compare_digest(token, settings.admin_reset_token):
        raise InvalidAdminToken()
