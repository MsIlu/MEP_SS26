from uuid import uuid4
from datetime import datetime

from pydantic import Field

from .base import BaseSchema, utc_now


class SafetyEvent(BaseSchema):
    event_id: str = Field(default_factory=lambda: str(uuid4()))

    event_type: str

    description: str

    timestamp: datetime = Field(default_factory=utc_now)