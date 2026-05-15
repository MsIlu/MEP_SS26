from datetime import datetime
from pydantic import Field

from .base import BaseSchema, utc_now


class SessionMetadata(BaseSchema):
    created_at: datetime = Field(default_factory=utc_now)

    updated_at: datetime = Field(default_factory=utc_now)

    language: str = "de"

    model_version: str | None = None