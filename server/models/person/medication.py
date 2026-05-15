from uuid import uuid4
from pydantic import Field

from .base import BaseSchema, AuditInfo


class Medication(BaseSchema):
    medication_id: str = Field(default_factory=lambda: str(uuid4()))

    name: str

    dosage: str | None = None

    frequency: str | None = None

    audit: AuditInfo = Field(default_factory=AuditInfo)