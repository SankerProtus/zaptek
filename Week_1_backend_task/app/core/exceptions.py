"""Domain exceptions.

The service layer raises these. It does not raise HTTPException, because the
service layer should not know it is being called over HTTP — that is what makes
it reusable from a CLI, a background job or a test.

main.py translates each one into a response.
"""

from __future__ import annotations

from typing import Any


class AppError(Exception):
    """Base class for everything this API raises deliberately."""

    code = "INTERNAL_ERROR"
    status_code = 500
    message = "Something went wrong."

    def __init__(self, message: str | None = None, **details: Any) -> None:
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class ApplicationNotFound(AppError):
    code = "APPLICATION_NOT_FOUND"
    status_code = 404
    message = "No application exists with that id."


class DuplicateEmail(AppError):
    code = "DUPLICATE_EMAIL"
    status_code = 409
    message = "An application with this email already exists."


class InvalidStatusTransition(AppError):
    code = "INVALID_STATUS_TRANSITION"
    status_code = 409
    message = "That status change is not allowed."


class AdminResetNotConfigured(AppError):
    code = "ADMIN_RESET_NOT_CONFIGURED"
    status_code = 503
    message = "The admin reset endpoint is not configured."


class InvalidAdminToken(AppError):
    code = "INVALID_ADMIN_TOKEN"
    status_code = 401
    message = "A valid admin token is required."
