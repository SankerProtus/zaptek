"""Application entrypoint.

ZapTek — Backend Engineering With FastAPI (Team 2), Week 1.

Every error leaving this API has the same shape:

    {"error": {"code": "...", "message": "...", "details": {...}}}

including FastAPI's own 422 validation errors, which are reshaped below.
Consistency across error responses is what makes an API feel finished.
"""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppError
from app.core.config import settings
from app.core.security import require_admin_reset_token
from app.data import mock_data
from app.routers import applications

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("zaptek.requests")

app = FastAPI(
    title="ZapTek Applications API",
    version="1.0.0",
    description=(
        "A complete CRUD backend for programme applications, built on an "
        "in-memory mock datastore instead of a database.\n\n"
        "Interactive docs: `/docs` — ReDoc: `/redoc`"
    ),
    contact={"name": "ZapTek — Backend Engineering With FastAPI (Team 2)"},
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Token"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Attach a request id and log request timing."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    started = time.perf_counter()

    response = await call_next(request)

    duration_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    logger.info(
        "%s %s %s -> %s (%.1fms)",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


def error_body(code: str, message: str, details: dict | None = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details or {}}}


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    response = JSONResponse(
        status_code=exc.status_code,
        content=error_body(exc.code, exc.message, exc.details),
    )
    response.headers["X-Request-ID"] = getattr(request.state, "request_id", "")
    return response


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Reshape Pydantic's 422 into our envelope.

    Each field error becomes {"field": "body.phone", "message": "..."} so a
    frontend can highlight the offending input directly.
    """
    fields = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]
    response = JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_body(
            "VALIDATION_ERROR",
            "One or more fields are invalid.",
            {"fields": fields},
        ),
    )
    response.headers["X-Request-ID"] = getattr(request.state, "request_id", "")
    return response


@app.exception_handler(StarletteHTTPException)
async def handle_http_exception(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    response = JSONResponse(
        status_code=exc.status_code,
        content=error_body(f"HTTP_{exc.status_code}", str(exc.detail)),
    )
    response.headers["X-Request-ID"] = getattr(request.state, "request_id", "")
    return response


@app.exception_handler(Exception)
async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled exception for request %s",
        getattr(request.state, "request_id", "unknown"),
    )
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_body("INTERNAL_ERROR", "An unexpected error occurred."),
    )
    response.headers["X-Request-ID"] = getattr(request.state, "request_id", "")
    return response


app.include_router(applications.router)


@app.get("/", tags=["meta"], summary="Service metadata")
def root() -> dict:
    return {
        "service": "ZapTek Applications API",
        "version": "1.0.0",
        "docs": "/docs",
        "storage": "in-memory mock data (resets on restart)",
    }


@app.get("/health", tags=["meta"], summary="Health check")
def health() -> dict:
    return {"status": "ok"}


@app.post("/admin/reset", tags=["meta"], summary="Restore the seed data")
def reset(_: None = Depends(require_admin_reset_token)) -> dict:
    """Handy during a demo: put the dataset back to its known starting state."""
    mock_data.reset_data()
    return {"status": "reset", "records": len(mock_data.all_records())}
