"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    environment: str
    admin_reset_token: str | None
    allowed_origins: tuple[str, ...]
    allowed_hosts: tuple[str, ...]
    docs_enabled: bool

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            environment=os.getenv("ENVIRONMENT", "development").lower(),
            admin_reset_token=os.getenv("ADMIN_RESET_TOKEN") or None,
            allowed_origins=_csv(os.getenv("CORS_ALLOWED_ORIGINS", "")),
            allowed_hosts=_csv(
                os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver")
            ),
            docs_enabled=os.getenv("API_DOCS_ENABLED", "true").lower() == "true",
        )


settings = Settings.from_environment()
