from __future__ import annotations

from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


VerificationStatus = Literal["extracted", "confirmed", "corrected", "rejected"]
ObservationType = Literal[
    "symptom",
    "medication",
    "diagnosis",
    "injury",
    "measurement",
    "risk_factor",
    "concern",
    "administrative",
    "observation",
]
IntentCategory = Literal[
    "symptom_report",
    "emergency",
    "administrative",
    "general_health_question",
    "smalltalk",
    "not_medical",
]
ResponseMode = Literal[
    "emergency",
    "safety_clarification",
    "confirm_case",
    "ask_followup",
    "recommend",
    "out_of_scope",
    "cannot_assess",
]
MessageRole = Literal[
    "new_information",
    "answer_to_followup",
    "confirmation",
    "correction",
    "recommendation_request",
    "topic_shift",
    "non_medical",
]
SubjectRelation = Literal["self", "child", "relative", "other_person", "unknown"]
CareLevel = Literal[
    "self_care",
    "pharmacy",
    "general_practice",
    "specialist",
    "116117",
    "emergency_department",
    "112",
    "unknown",
]
Specialty = Literal[
    "unknown",
    "general_practice",
    "orthopedics",
    "dermatology",
    "neurology",
    "ent",
    "emergency_medicine",
]
Urgency = Literal["unknown", "self_observation", "routine", "soon", "today", "emergency"]
UrgencyLevel = Literal["low", "medium", "high", "emergency", "unclear"]


class PipelineModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Provenance(PipelineModel):
    source: Literal["user_message", "user_confirmation", "user_correction"]
    message_id: str | None = None
    source_span: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    note: str | None = None


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
    numeric_value: float | None = None
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


class Subject(PipelineModel):
    relation: SubjectRelation = "unknown"
    description: str | None = None
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    verification_status: VerificationStatus = "confirmed"

    def has_value(self) -> bool:
        return any(
            (
                self.relation != "unknown",
                self.description,
                self.age is not None,
                self.sex,
            )
        )

    def needs_confirmation(self) -> bool:
        return self.has_value() and self.verification_status not in {"confirmed", "corrected"}


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
    symptom_data: SymptomObservationData | None = None
    injury_data: InjuryObservationData | None = None
    measurement_data: MeasurementObservationData | None = None
    medication_data: MedicationObservationData | None = None
    diagnosis_data: DiagnosisObservationData | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    verification_status: VerificationStatus = "extracted"
    provenance: list[Provenance] = Field(default_factory=list)

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
            self.runtime_value("body_site") or "",
            self.runtime_value("temporality") or "",
            self.source_span,
        ]
        parts.extend(str(value) for value in self.details.values())
        parts.extend(str(value) for value in self.measurement.values())
        return " ".join(part for part in parts if part)

    def runtime_value(self, name: str):
        if name == "temporality":
            if self.type == "symptom" and self.symptom_data is not None:
                return self.symptom_data.duration_or_onset or self.temporality
            if self.type == "injury" and self.injury_data is not None:
                return self.injury_data.duration_or_onset or self.temporality
            if self.type == "measurement" and self.measurement_data is not None:
                return self.measurement_data.measured_at or self.temporality
        if name == "body_site":
            if self.type == "symptom" and self.symptom_data is not None:
                return self.symptom_data.body_site or self.body_site
            if self.type == "injury" and self.injury_data is not None:
                return self.injury_data.body_site or self.body_site
        if name == "severity":
            if self.type == "symptom" and self.symptom_data is not None:
                return self.symptom_data.severity
            if self.type == "injury" and self.injury_data is not None:
                return self.injury_data.severity
        if name == "course" and self.type == "symptom" and self.symptom_data is not None:
            return self.symptom_data.course or self.course
        return getattr(self, name, None)

    def runtime_detail_value(self, key: str) -> str | None:
        if key == "context" and self.type == "injury" and self.injury_data is not None:
            return self.injury_data.injury_context or self.details.get("context")
        if (
            key == "functional_limitation"
            and self.type == "injury"
            and self.injury_data is not None
        ):
            return self.injury_data.functional_limitation or self.details.get(key)
        return self.details.get(key)

    def runtime_measurement_value(self, key: str):
        data = self.measurement_data
        if key == "kind":
            return (data.kind if data is not None else None) or self.measurement.get("kind")
        if key == "value":
            return (
                (data.value if data is not None else None)
                or (data.numeric_value if data is not None else None)
                or self.measurement.get("value")
                or self.measurement.get("numeric_value")
            )
        if key == "unit":
            return (data.unit if data is not None else None) or self.measurement.get("unit")
        return self.measurement.get(key)

    def requirement_value(self, field: str):
        if self.type == "symptom":
            return self._symptom_requirement_value(field)
        if self.type == "injury":
            return self._injury_requirement_value(field)
        if self.type == "measurement":
            return self._measurement_requirement_value(field)
        if self.type == "medication":
            return self._medication_requirement_value(field)
        if self.type == "risk_factor" and field == "kind":
            return self.label or self.concept
        if self.type == "concern" and field == "main_concern":
            return self.display_label or self.label
        if self.type == "diagnosis" and field == "name":
            return (
                (self.diagnosis_data.name if self.diagnosis_data is not None else None)
                or self.label
                or self.concept
            )
        return None

    def _symptom_requirement_value(self, field: str):
        if field == "duration_or_onset":
            return self.runtime_value("temporality")
        if field == "body_site":
            return self.runtime_value("body_site")
        if field == "severity":
            return self.runtime_value("severity")
        if field == "course":
            return self.runtime_value("course")
        return None

    def _injury_requirement_value(self, field: str):
        if field == "duration_or_onset":
            return self.runtime_value("temporality")
        if field == "body_site":
            return self.runtime_value("body_site")
        if field == "severity":
            return self.runtime_value("severity")
        if field == "injury_context":
            return self.runtime_detail_value("context")
        if field == "functional_limitation":
            return self.runtime_detail_value("functional_limitation")
        return None

    def _measurement_requirement_value(self, field: str):
        if field == "kind":
            return self.runtime_measurement_value("kind")
        if field == "value":
            return self.runtime_measurement_value("value")
        return None

    def _medication_requirement_value(self, field: str):
        if field == "name":
            return (
                (self.medication_data.name if self.medication_data is not None else None)
                or self.label
                or self.concept
            )
        if field == "use_context":
            return (
                (self.medication_data.use_context if self.medication_data is not None else None)
                or self.details.get("use_context")
            )
        return None


class MedicalCase(PipelineModel):
    case_id: str = Field(default_factory=lambda: str(uuid4()))
    subject: Subject = Field(default_factory=Subject)
    observations: list[CaseObservation] = Field(default_factory=list)
    primary_problem_id: str | None = None

    def active_observations(
        self,
        *,
        source: Literal["working", "confirmed"] = "working",
        include_negated: bool = True,
        include_rejected: bool = False,
    ) -> list[CaseObservation]:
        observations = list(self.observations)
        if source == "confirmed":
            observations = [
                observation
                for observation in observations
                if observation.verification_status in {"confirmed", "corrected"}
            ]
        if not include_rejected:
            observations = [
                observation
                for observation in observations
                if observation.verification_status != "rejected"
            ]
        if not include_negated:
            observations = [observation for observation in observations if not observation.negated]
        return observations

    def observations_of_type(
        self,
        *types: str,
        source: Literal["working", "confirmed"] = "working",
        include_negated: bool = False,
        include_rejected: bool = False,
    ) -> list[CaseObservation]:
        allowed = set(types)
        return [
            observation
            for observation in self.active_observations(
                source=source,
                include_negated=include_negated,
                include_rejected=include_rejected,
            )
            if observation.type in allowed
        ]

    def complaint_observations(
        self,
        *,
        source: Literal["working", "confirmed"] = "working",
    ) -> list[CaseObservation]:
        return self.observations_of_type(
            "symptom",
            "injury",
            "measurement",
            "concern",
            source=source,
        )

    def problem_observations(
        self,
        *,
        source: Literal["working", "confirmed"] = "working",
    ) -> list[CaseObservation]:
        return self.complaint_observations(source=source) + self.observations_of_type(
            "diagnosis",
            source=source,
        )

    def active_problem_ids(self, *, source: Literal["working", "confirmed"] = "working") -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for observation in self.problem_observations(source=source):
            if observation.id in seen:
                continue
            seen.add(observation.id)
            result.append(observation.id)
        return result

    def primary_observation(
        self,
        *,
        source: Literal["working", "confirmed"] = "working",
    ) -> CaseObservation | None:
        if self.primary_problem_id:
            for observation in self.active_observations(source=source):
                if observation.id == self.primary_problem_id:
                    return observation
        candidates = self.problem_observations(source=source)
        return candidates[0] if candidates else None

    def primary_focus_label(self, *, source: Literal["working", "confirmed"] = "working") -> str | None:
        observation = self.primary_observation(source=source)
        return observation.patient_label if observation is not None else None

    def set_primary_observation(self, observation: CaseObservation | None) -> None:
        self.primary_problem_id = observation.id if observation is not None else None

    def ensure_primary_problem(self, *, source: Literal["working", "confirmed"] = "working") -> None:
        primary = self.primary_observation(source=source)
        self.primary_problem_id = primary.id if primary is not None else None

    def unconfirmed_observations(self) -> list[CaseObservation]:
        return [
            observation
            for observation in self.problem_observations(source="working")
            if observation.verification_status == "extracted"
        ]

    def clone_confirmed_case(self) -> MedicalCase:
        subject = (
            self.subject.model_copy(deep=True)
            if self.subject.verification_status in {"confirmed", "corrected"}
            else Subject()
        )
        case = MedicalCase(
            case_id=self.case_id,
            subject=subject,
            observations=[
                observation.model_copy(deep=True)
                for observation in self.active_observations(source="confirmed")
            ],
            primary_problem_id=self.primary_problem_id,
        )
        case.ensure_primary_problem(source="confirmed")
        return case


class DialogueState(PipelineModel):
    conversation_id: str = Field(default_factory=lambda: str(uuid4()))
    pending_requirement: str | None = None
    awaiting_confirmation: bool = False
    pending_confirmation_observation_ids: list[str] = Field(default_factory=list)
    pending_confirmation_subject: bool = False
    focus_observation_id: str | None = None
    last_assistant_question: str | None = None
    recommendation_requested: bool = False


class ConversationTurn(PipelineModel):
    role: Literal["user", "assistant", "system"]
    content: str


class CaseSummaryObservation(PipelineModel):
    id: str
    type: ObservationType
    display_label: str
    concept: str | None = None
    body_site: str | None = None
    temporality: str | None = None
    severity: int | None = None
    details: dict[str, str] = Field(default_factory=dict)
    verification_status: VerificationStatus


class CaseSummary(PipelineModel):
    subject_relation: SubjectRelation = "unknown"
    subject_age: int | None = None
    primary_focus: str | None = None
    primary_problem_id: str | None = None
    active_problem_ids: list[str] = Field(default_factory=list)
    observations: list[CaseSummaryObservation] = Field(default_factory=list)


class DialogueSummary(PipelineModel):
    pending_requirement: str | None = None
    awaiting_confirmation: bool = False
    pending_confirmation_observation_ids: list[str] = Field(default_factory=list)
    pending_confirmation_subject: bool = False
    focus_observation_id: str | None = None
    focus_label: str | None = None
    recommendation_requested: bool = False


class ExtractionContext(PipelineModel):
    latest_user_message: str
    pending_requirement: str | None = None
    last_assistant_question: str | None = None
    recent_turns: list[ConversationTurn] = Field(default_factory=list)
    case_summary: CaseSummary | None = None
    dialogue_summary: DialogueSummary | None = None


class MessageUpdate(PipelineModel):
    raw_text: str
    intent_category: IntentCategory = "symptom_report"
    is_medical: bool = False
    message_role: MessageRole = "new_information"
    user_requests_recommendation: bool = False
    possible_new_topic: bool = False
    subject: Subject | None = None
    observations: list[CaseObservation] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class AssessmentReadiness(PipelineModel):
    ready: bool = False
    missing_requirements: list[str] = Field(default_factory=list)
    unconfirmed_observation_ids: list[str] = Field(default_factory=list)
    subject_needs_confirmation: bool = False
    reason_tags: list[str] = Field(default_factory=list)


class Recommendation(PipelineModel):
    care_level: CareLevel = "unknown"
    urgency_level: UrgencyLevel = "unclear"
    specialty: Specialty = "unknown"
    urgency: Urgency = "unknown"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning_tags: list[str] = Field(default_factory=list)
    explanation: str = ""
    reasons: list[str] = Field(default_factory=list)


class SafetyResult(PipelineModel):
    red_flag_detected: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    matched_flags: list[str] = Field(default_factory=list)
    checked_sources: list[str] = Field(default_factory=list)
    action: str = "continue"
    severity: str | None = None
    rule_id: str | None = None
    rule_name: str | None = None
    category: str | None = None
    message_key: str | None = None
    matched_keywords: list[str] = Field(default_factory=list)


class PipelineResult(PipelineModel):
    raw_text: str
    safety: SafetyResult
    medical_context: MedicalContextStatus | None = None
    red_flag_status: RedFlagStatus | None = None
    case: MedicalCase | None = None
    dialogue_state: DialogueState | None = None
    message_update: MessageUpdate | None = None
    readiness: AssessmentReadiness | None = None
    recommendation: Recommendation | None = None
    response_mode: ResponseMode
    followup_question: str | None = None


class ConfirmationUpdate(PipelineModel):
    confirmed_observation_ids: list[str] = Field(default_factory=list)
    rejected_observation_ids: list[str] = Field(default_factory=list)
    corrected_observations: list[CaseObservation] = Field(default_factory=list)
    added_observations: list[CaseObservation] = Field(default_factory=list)
    confirm_subject: bool = False
    corrected_subject: Subject | None = None

# --- Context and safety status models ---------------------------------------
# These models keep raw text checks, structured checks and final decisions
# separated. This avoids turning an early keyword hit directly into a final
# emergency decision.

class MedicalContextStatus(PipelineModel):
    """Represents whether the current user message is medically relevant."""

    raw_status: str = "unclear"
    structured_status: str = "not_checked"
    final_status: str = "unclear"
    confidence: float = 0.0
    reason_tags: list[str] = Field(default_factory=list)


class RedFlagStatus(PipelineModel):
    """Represents the combined red flag result from raw and structured checks."""

    raw_red_flag: bool = False
    structured_red_flag: bool | None = None
    final_status: str = "none"
    red_flag: bool = False
    requires_safety_question: bool = False
    safety_question: str | None = None
    reason_tags: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)