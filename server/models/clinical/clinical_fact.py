from uuid import uuid4
from pydantic import Field

from .base import BaseSchema, AuditInfo
from .common import Provenance


class ClinicalFact(BaseSchema):
    fact_id: str = Field(default_factory=lambda: str(uuid4()))

    fact_type: str

    value: str

    normalized_value: str | None = None

    provenance: Provenance = Field(default_factory=Provenance)

    audit: AuditInfo = Field(default_factory=AuditInfo)