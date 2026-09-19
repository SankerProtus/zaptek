"""Pydantic schemas for the applications resource."""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)


class Status(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Level(str, Enum):
    FIRST = "1st Year"
    SECOND = "2nd Year"
    THIRD = "3rd Year"
    FOURTH = "4th Year"


def to_camel(field_name: str) -> str:
    """full_name -> fullName, whatsapp_number -> whatsappNumber."""
    head, *tail = field_name.split("_")
    return head + "".join(word.capitalize() for word in tail)


class CamelModel(BaseModel):
    """Base model: snake_case in Python, camelCase over the wire."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=False,
        str_strip_whitespace=True,
        extra="forbid",
    )


GHANA_PHONE = re.compile(r"^0\d{9}$")


def normalise_ghana_phone(value: str) -> str:
    """Accept +233 24 556 7812, 233245567812 or 0245567812; store 0245567812.

    Normalising on the way in means two records for the same person can never
    hide behind different formatting.
    """
    digits = re.sub(r"[\s\-()]", "", value)

    if digits.startswith("+233"):
        digits = "0" + digits[4:]
    elif digits.startswith("233") and len(digits) == 12:
        digits = "0" + digits[3:]

    if not GHANA_PHONE.match(digits):
        raise ValueError(
            "must be a 10-digit Ghanaian number starting with 0, e.g. 0245567812"
        )
    return digits


def validate_full_name(value: str) -> str:
    if len(value.split()) < 2:
        raise ValueError("please give both a first and a last name")
    return value


class ApplicationBase(CamelModel):
    full_name: str = Field(min_length=2, max_length=100, examples=["Ama Serwaa Owusu"])
    email: EmailStr
    phone: str = Field(examples=["0245567812"])
    whatsapp_number: Optional[str] = Field(default=None, examples=["0245567812"])

    university: str = Field(min_length=2, max_length=120, examples=["KNUST"])
    course: str = Field(min_length=2, max_length=120, examples=["Computer Engineering"])
    level: Level
    track: str = Field(min_length=2, max_length=80, examples=["Backend Engineering"])

    motivation: str = Field(
        min_length=20,
        max_length=500,
        description="Why the applicant wants a place. At least a sentence.",
    )

    portfolio_link: Optional[HttpUrl] = None
    resume_link: Optional[HttpUrl] = None

    join_innovation_club: bool = False

    @field_validator("phone")
    @classmethod
    def _check_phone(cls, value: str) -> str:
        return normalise_ghana_phone(value)

    @field_validator("whatsapp_number")
    @classmethod
    def _check_whatsapp(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return normalise_ghana_phone(value)

    @field_validator("full_name")
    @classmethod
    def _check_full_name(cls, value: str) -> str:
        return validate_full_name(value)


class ApplicationCreate(ApplicationBase):
    """Client-supplied payload. No id, no status, no submittedAt."""

    @model_validator(mode="after")
    def _default_whatsapp_to_phone(self) -> "ApplicationCreate":
        if self.whatsapp_number is None:
            self.whatsapp_number = self.phone
        return self


class ApplicationUpdate(CamelModel):
    """PATCH payload. Everything optional; status has its own endpoint."""

    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    whatsapp_number: Optional[str] = None

    university: Optional[str] = Field(default=None, min_length=2, max_length=120)
    course: Optional[str] = Field(default=None, min_length=2, max_length=120)
    level: Optional[Level] = None
    track: Optional[str] = Field(default=None, min_length=2, max_length=80)

    motivation: Optional[str] = Field(default=None, min_length=20, max_length=500)

    portfolio_link: Optional[HttpUrl] = None
    resume_link: Optional[HttpUrl] = None

    join_innovation_club: Optional[bool] = None

    @field_validator("full_name")
    @classmethod
    def _check_full_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return validate_full_name(value)

    @field_validator("phone", "whatsapp_number")
    @classmethod
    def _check_phones(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return normalise_ghana_phone(value)


class StatusUpdate(CamelModel):
    """Body for PATCH /applications/{id}/status."""

    status: Status
    note: Optional[str] = Field(default=None, max_length=300)


class ApplicationResponse(ApplicationBase):
    """Full record as returned by the API."""

    id: int
    status: Status
    submitted_at: datetime
    status_note: Optional[str] = Field(
        default=None,
        description="Optional note attached the last time status changed.",
    )


class PaginatedApplications(CamelModel):
    total: int = Field(description="Matching records before pagination")
    limit: int
    offset: int
    items: list[ApplicationResponse]
