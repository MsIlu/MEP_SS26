from datetime import datetime
from pydantic import Field

from .base import BaseSchema, utc_now


class SessionReference(BaseSchema):
    session_id: str

    created_at: datetime = Field(default_factory=utc_now)

    last_updated_at: datetime = Field(default_factory=utc_now)