from typing import Literal
from uuid import uuid4

from pydantic import Field, field_validator

from careena_pipeline.models.common.base import PipelineModel
from careena_pipeline.models.common.types import ObservationStatus, ObservationType
from careena_pipeline.models.domain.provenance import Provenance


class CaseObservation(PipelineModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: ObservationType
    label: str
    display_label: str | None = None
    concept: str | None = None
    source_span: str
    negated: bool = False
    certainty: Literal["confirmed", "suspected", "uncertain"] = "confirmed"
    temporality: str | None = None
    severity: int | None = Field(default=None, ge=0, le=10)
    body_site: str | None = None
    laterality: Literal["left", "right", "bilateral", "unknown"] | None = None
    course: Literal[
        "worsening",
        "improving",
        "stable",
        "sudden",
        "recurrent",
        "unknown",
    ] | None = None
    measurement: dict[str, str | int | float | bool] = Field(default_factory=dict)
    subject_ref: str | None = None
    details: dict[str, str] = Field(default_factory=dict)
    status: ObservationStatus = "extracted"
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    provenance: list[Provenance] = Field(default_factory=list)

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, value):
        if value is None or isinstance(value, int):
            return value
        if isinstance(value, float):
            return round(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if not normalized:
                return None
            if normalized.isdigit():
                return int(normalized)
            words = {
                "none": 0,
                "no": 0,
                "keine": 0,
                "mild": 2,
                "leicht": 2,
                "moderate": 5,
                "mittel": 5,
                "maessig": 5,
                "strong": 8,
                "severe": 8,
                "stark": 8,
                "schwer": 8,
                "very strong": 9,
                "sehr stark": 9,
                "unbearable": 10,
                "unertraeglich": 10,
            }
            if normalized in words:
                return words[normalized]
        return value

    @property
    def patient_label(self) -> str:
        return self.display_label or self.label or "Angabe"

    @property
    def searchable_text(self) -> str:
        parts = [
            self.type,
            self.label,
            self.display_label or "",
            self.concept or "",
            self.body_site or "",
            self.source_span,
        ]
        parts.extend(str(value) for value in self.details.values())
        parts.extend(str(value) for value in self.measurement.values())
        return " ".join(part for part in parts if part)
