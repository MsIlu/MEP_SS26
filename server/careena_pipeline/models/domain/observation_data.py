from typing import Literal

from pydantic import Field

from careena_pipeline.models.common.base import PipelineModel


class SymptomObservationData(PipelineModel):
    duration_or_onset: str | None = None
    body_site: str | None = None
    severity: int | None = Field(default=None, ge=0, le=10)
    course: Literal[
        "worsening",
        "improving",
        "stable",
        "sudden",
        "recurrent",
        "unknown",
    ] | None = None
    quality: str | None = None


class InjuryObservationData(PipelineModel):
    duration_or_onset: str | None = None
    body_site: str | None = None
    severity: int | None = Field(default=None, ge=0, le=10)
    injury_context: str | None = None
    functional_limitation: str | None = None


class MeasurementObservationData(PipelineModel):
    kind: str | None = None
    value: str | None = None
    numeric_value: str | None = None
    unit: str | None = None
    measured_at: str | None = None


class MedicationObservationData(PipelineModel):
    name: str | None = None
    dose: str | None = None
    frequency: str | None = None
    route: str | None = None
    use_context: str | None = None
    is_current: bool | None = None


class DiagnosisObservationData(PipelineModel):
    name: str | None = None
    status: str | None = None
    chronicity: str | None = None
