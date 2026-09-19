"""HTTP layer for /applications.

Every handler here does three things and no more: read the request, call the
service, shape the response.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Path, Query, Response, status as http_status

from app.models.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
    PaginatedApplications,
    Status,
    StatusUpdate,
)
from app.services import application_service as service

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get(
    "",
    response_model=PaginatedApplications,
    summary="List applications",
)
def list_applications(
    status: Optional[Status] = Query(default=None, description="Filter by status"),
    university: Optional[str] = Query(
        default=None, max_length=120, description="Partial match"
    ),
    track: Optional[str] = Query(
        default=None, max_length=80, description="Partial match"
    ),
    search: Optional[str] = Query(
        default=None, max_length=120, description="Name or email"
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedApplications:
    items, total = service.list_applications(
        status=status,
        university=university,
        track=track,
        search=search,
        limit=limit,
        offset=offset,
    )
    return PaginatedApplications(
        total=total,
        limit=limit,
        offset=offset,
        items=[ApplicationResponse.model_validate(item) for item in items],
    )


@router.get(
    "/stats",
    summary="Aggregate counts",
    description="Declared before /{application_id} so 'stats' is not read as an id.",
)
def get_stats() -> dict:
    return service.stats()


@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
    summary="Get a single application",
    responses={404: {"description": "Application not found"}},
)
def get_application(
    application_id: int = Path(ge=1, description="Application id"),
) -> ApplicationResponse:
    return ApplicationResponse.model_validate(service.get_application(application_id))


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Submit a new application",
    responses={409: {"description": "Email already used"}},
)
def create_application(payload: ApplicationCreate) -> ApplicationResponse:
    return ApplicationResponse.model_validate(service.create_application(payload))


@router.patch(
    "/{application_id}",
    response_model=ApplicationResponse,
    summary="Partially update an application",
    responses={404: {"description": "Application not found"}},
)
def update_application(
    payload: ApplicationUpdate,
    application_id: int = Path(ge=1),
) -> ApplicationResponse:
    return ApplicationResponse.model_validate(
        service.update_application(application_id, payload)
    )


@router.patch(
    "/{application_id}/status",
    response_model=ApplicationResponse,
    summary="Accept or reject an application",
    description=(
        "Separate from the general update because approving someone is a "
        "different operation from fixing a typo, with different rules and, "
        "later, different permissions."
    ),
)
def change_status(
    payload: StatusUpdate,
    application_id: int = Path(ge=1),
) -> ApplicationResponse:
    return ApplicationResponse.model_validate(
        service.change_status(application_id, payload.status, payload.note)
    )


@router.delete(
    "/{application_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    summary="Withdraw an application",
)
def delete_application(application_id: int = Path(ge=1)) -> Response:
    service.delete_application(application_id)
    return Response(status_code=http_status.HTTP_204_NO_CONTENT)
