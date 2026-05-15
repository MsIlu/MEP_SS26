from uuid import uuid4
from pydantic import Field

from .base import BaseSchema, AuditInfo
from .common import Coding, Provenance
from .temporal import TemporalState
from .assertion import AssertionState


class SymptomAttributes(BaseSchema):
    severity: int | None = Field(default=None, ge=0, le=10)

    location: str | None = None

    radiation: str | None = None

    frequency: str | None = None


class Symptom(BaseSchema):
    symptom_id: str = Field(default_factory=lambda: str(uuid4()))

    raw_text: str

    normalized_name: str

    coding: Coding | None = None

    attributes: SymptomAttributes = Field(default_factory=SymptomAttributes)

    temporal: TemporalState = Field(default_factory=TemporalState)

    assertion: AssertionState = Field(default_factory=AssertionState)

    status: str = "active"

    provenance: Provenance = Field(default_factory=Provenance)

    audit: AuditInfo = Field(default_factory=AuditInfo)