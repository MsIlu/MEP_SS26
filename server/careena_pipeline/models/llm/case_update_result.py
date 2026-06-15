from typing import Literal

from pydantic import Field

from careena_pipeline.state.module_registry import ModuleName
from careena_pipeline.models.common.types import (
    MessageRole,
    ObservationType,
    PlannerModule,
    SubjectRelation,
)
from careena_pipeline.models.domain.observation_data import (
    DiagnosisObservationData,
    InjuryObservationData,
    MeasurementObservationData,
    MedicationObservationData,
    SymptomObservationData,
)
from careena_pipeline.models.system.baseSchema import BaseSchema


class LLMCaseUpdateIntent(BaseSchema):
    category: Literal[
        "symptom_report",
        "emergency",
        "administrative",
        "general_health_question",
        "smalltalk",
        "not_medical",
    ]
    is_medical: bool = False
    extraction_required: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class LLMCaseUpdateSubject(BaseSchema):
    relation: SubjectRelation = "unknown"
    description: str | None = None
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class LLMCaseUpdateObservation(BaseSchema):
    id: str
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
    course: Literal["worsening", "improving", "stable", "sudden", "recurrent", "unknown"] | None = None
    measurement: dict[str, str | bool] = Field(default_factory=dict)
    subject_ref: str | None = None
    details: dict[str, str] = Field(default_factory=dict)
    symptom_data: SymptomObservationData | None = None
    injury_data: InjuryObservationData | None = None
    measurement_data: MeasurementObservationData | None = None
    medication_data: MedicationObservationData | None = None
    diagnosis_data: DiagnosisObservationData | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

class LLMCaseUpdateResult(BaseSchema):
    intent: LLMCaseUpdateIntent
    subject: LLMCaseUpdateSubject | None = None
    observations_added: list[LLMCaseUpdateObservation] = Field(default_factory=list)
    negated_observations_added: list[LLMCaseUpdateObservation] = Field(default_factory=list)
    user_requests_recommendation: bool = False
    possible_new_topic: bool = False
    message_role: MessageRole = "new_information"
    active_modules: list[ModuleName] = Field(default_factory=list)
    required_fields: list[str] = Field(default_factory=list)
    resolved_fields: list[str] = Field(default_factory=list)
    recommended_modules: list[PlannerModule] = Field(default_factory=list)
    notes: list[str] | None = Field(default_factory=list)
