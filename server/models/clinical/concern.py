from uuid import uuid4
from pydantic import Field

from .base import BaseSchema, AuditInfo
from .common import Provenance


class Concern(BaseSchema):
    concern_id: str = Field(default_factory=lambda: str(uuid4()))

    description: str

    category: str | None = None

    priority: str | None = None

    provenance: Provenance = Field(default_factory=Provenance)

    audit: AuditInfo = Field(default_factory=AuditInfo)