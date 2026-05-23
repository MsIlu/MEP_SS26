from datetime import datetime, UTC
from pydantic import BaseModel, ConfigDict, Field

from .base import BaseSchema

def utc_now() -> datetime:
    return datetime.now(UTC)

"""
Data structure for audit information.
Automatically creates timestamps upon creation.

:param created_at   Time of creation
:param updated_at   Time of last access
:param created_by   Component that created the object
:param updated_by   Component that last updated the object
"""
class AuditInfo(BaseSchema):
    created_at: datetime = Field(default_factory=utc_now)

    updated_at: datetime = Field(default_factory=utc_now)

    created_by: str | None = None

    updated_by: str | None = None