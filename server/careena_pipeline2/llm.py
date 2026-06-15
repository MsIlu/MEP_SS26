from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Mapping

from pydantic import Field

from careena_pipeline2.core.engine import ExtractionEngine
from careena_pipeline2.models import (
    CaseObservation,
    CaseSummary,
    CaseSummaryObservation,
    ConversationTurn,
    DiagnosisObservationData,
    DialogueState,
    DialogueSummary,
    ExtractionContext,
    InjuryObservationData,
    IntentCategory,
    MeasurementObservationData,
    MedicalCase,
    MedicationObservationData,
    MessageRole,
    MessageUpdate,
    ObservationType,
    PipelineModel,
    Provenance,
    Subject,
    SubjectRelation,
    SymptomObservationData,
)
from careena_pipeline2.text import user_requests_recommendation


EXTRACTION_CALL = "extraction"

CALL_MODEL_ENV_VARS = {
    EXTRACTION_CALL: "CAREENA2_EXTRACTION_MODEL",
}

MAX_RECENT_TURNS = 4


@dataclass(frozen=True)
class CallModelConfig:
    default_model: str
    overrides: Mapping[str, str] = field(default_factory=dict)

    def model_for(self, call_name: str) -> str:
        return self.overrides.get(call_name, self.default_model)


def build_call_model_config(
    *,
    default_model: str,
    overrides: Mapping[str, str] | None = None,
) -> CallModelConfig:
    merged_overrides = {
        call_name: model
        for call_name, model in {
            **_env_overrides(),
            **dict(overrides or {}),
        }.items()
        if model
    }
    return CallModelConfig(default_model=default_model, overrides=merged_overrides)


def _env_overrides() -> dict[str, str]:
    return {
        call_name: os.getenv(env_var, "").strip()
        for call_name, env_var in CALL_MODEL_ENV_VARS.items()
    }


class LLMExtractedSubject(PipelineModel):
    relation: SubjectRelation = "unknown"
    description: str | None = None
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class LLMExtractedObservation(PipelineModel):
    id: str | None = None
    type: ObservationType
    label: str
    display_label: str | None = None
    concept: str | None = None
    source_span: str
    negated: bool = False
    certainty: str = "confirmed"
    temporality: str | None = None
    severity: int | None = Field(default=None, ge=0, le=10)
    body_site: str | None = None
    laterality: str | None = None
    course: str | None = None
    measurement: dict[str, str | int | float | bool] = Field(default_factory=dict)
    subject_ref: str | None = None
    details: dict[str, str] = Field(default_factory=dict)
    symptom_data: SymptomObservationData | None = None
    injury_data: InjuryObservationData | None = None
    measurement_data: MeasurementObservationData | None = None
    medication_data: MedicationObservationData | None = None
    diagnosis_data: DiagnosisObservationData | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class LLMExtractedMessage(PipelineModel):
    intent_category: IntentCategory = "symptom_report"
    is_medical: bool = False
    message_role: MessageRole = "new_information"
    user_requests_recommendation: bool = False
    possible_new_topic: bool = False
    subject: LLMExtractedSubject | None = None
    observations: list[LLMExtractedObservation] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


MESSAGE_EXTRACTION_PROMPT = """
You are the message-extraction layer for Careena, a German
patient-routing assistant.

Your task:
Convert the latest user message into a structured update for one ongoing
medical case.

The model input is structured JSON with these fields:
- latest_user_message: the only source for newly extracted facts
- pending_requirement: what the application is waiting for, if anything
- last_assistant_question: the previous assistant question, if available
- recent_turns: short recent chat context
- case_summary: compact current case state
- dialogue_summary: confirmation and focus state

You do NOT diagnose.
You do NOT recommend care.
You do NOT decide urgency.
You only describe what the latest user message adds, confirms, corrects,
negates, or requests.

Use context only to interpret short answers correctly.
Extract only information that is explicitly stated, confirmed, corrected,
or negated in latest_user_message.
Do not copy facts from case_summary into observations unless the latest
user message confirms or updates them.
Do not invent missing details.
Return ONLY valid JSON matching the schema.

Output schema:
{
  "intent_category": "symptom_report | emergency | administrative | general_health_question | smalltalk | not_medical",
  "is_medical": true,
  "message_role": "new_information | answer_to_followup | confirmation | correction | recommendation_request | topic_shift | non_medical",
  "user_requests_recommendation": false,
  "possible_new_topic": false,
  "subject": {
    "relation": "self | child | relative | other_person | unknown",
    "description": "string or null",
    "age": null,
    "sex": "string or null",
    "confidence": 0.0
  },
  "observations": [
    {
      "id": "existing observation id when this message updates an existing fact, otherwise a new stable id or null",
      "type": "symptom | medication | diagnosis | injury | measurement | risk_factor | concern | administrative | observation",
      "label": "short stable internal label",
      "display_label": "short German user-facing label or null",
      "concept": "short snake_case concept key or null",
      "source_span": "exact span from latest_user_message",
      "negated": false,
      "certainty": "confirmed | suspected | uncertain",
      "temporality": "string or null",
      "severity": null,
      "body_site": "string or null",
      "laterality": "left | right | bilateral | unknown | null",
      "course": "worsening | improving | stable | sudden | recurrent | unknown | null",
      "measurement": {},
      "subject_ref": "self | child | relative | other_person | unknown | null",
      "details": {},
      "symptom_data": {
        "duration_or_onset": "string or null",
        "body_site": "string or null",
        "severity": null,
        "course": "worsening | improving | stable | sudden | recurrent | unknown | null",
        "quality": "string or null"
      },
      "injury_data": {
        "duration_or_onset": "string or null",
        "body_site": "string or null",
        "severity": null,
        "injury_context": "string or null",
        "functional_limitation": "string or null"
      },
      "measurement_data": {
        "kind": "string or null",
        "value": "string or null",
        "numeric_value": null,
        "unit": "string or null",
        "measured_at": "string or null"
      },
      "medication_data": {
        "name": "string or null",
        "dose": "string or null",
        "frequency": "string or null",
        "route": "string or null",
        "use_context": "string or null",
        "is_current": null
      },
      "diagnosis_data": {
        "name": "string or null",
        "status": "string or null",
        "chronicity": "string or null"
      },
      "confidence": 0.0
    }
  ],
  "notes": []
}

Important rules:
- observations contains both positive and explicitly negated facts. Use negated=true
  for denied symptoms or findings.
- If the latest message updates the current focus or answers a follow-up about an
  existing symptom, injury, or measurement, reuse the existing observation id
  from case_summary when the target is clear.
- If the message only confirms previously summarized information and adds no new
  fact, message_role should be confirmation and observations may be empty.
- If the message corrects a previous summary, message_role should be correction.
- recommendation_request is for messages whose main purpose is asking what to do
  or where to go.
- non_medical and not_medical are for content with no human-medical case value.
- Animal or veterinary content is always not_medical.
- Keep source_span exact and only from latest_user_message.
- Write display_label in German.
- Do not create duplicate observations when the user is clearly refining an
  already known complaint.
"""


class MessageExtractor:
    def __init__(
        self,
        engine: ExtractionEngine,
        *,
        call_models: CallModelConfig | None = None,
    ):
        self.engine = engine
        self.call_models = call_models

    def extract_update(
        self,
        text: str,
        *,
        existing_case: MedicalCase | None = None,
        dialogue_state: DialogueState | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> MessageUpdate:
        context = build_extraction_context(
            latest_user_message=text,
            existing_case=existing_case,
            dialogue_state=dialogue_state,
            messages=conversation_messages,
        )
        result = self.engine.extract(
            text=json.dumps(context.model_dump(), ensure_ascii=False),
            system_prompt=MESSAGE_EXTRACTION_PROMPT.strip() + "\n",
            output_schema=LLMExtractedMessage,
            max_tokens=1800,
            model=(
                self.call_models.model_for(EXTRACTION_CALL)
                if self.call_models is not None
                else None
            ),
        )
        return MessageUpdate(
            raw_text=text,
            intent_category=result.intent_category,
            is_medical=result.is_medical,
            message_role=result.message_role,
            user_requests_recommendation=(
                result.user_requests_recommendation or user_requests_recommendation(text)
            ),
            possible_new_topic=result.possible_new_topic,
            subject=self._adapt_subject(result.subject, message_role=result.message_role),
            observations=[
                self._adapt_observation(item, message_role=result.message_role)
                for item in result.observations
            ],
            notes=list(result.notes),
        )

    @staticmethod
    def _adapt_subject(subject: LLMExtractedSubject | None, *, message_role: MessageRole) -> Subject | None:
        if subject is None:
            return None
        adapted = Subject(
            relation=subject.relation,
            description=subject.description,
            age=subject.age,
            sex=subject.sex,
            confidence=subject.confidence,
        )
        if adapted.has_value():
            adapted.verification_status = _verification_status_for_role(message_role)
        return adapted

    @staticmethod
    def _adapt_observation(
        observation: LLMExtractedObservation,
        *,
        message_role: MessageRole,
    ) -> CaseObservation:
        payload = {
            "type": observation.type,
            "label": observation.label,
            "display_label": observation.display_label,
            "concept": observation.concept,
            "source_span": observation.source_span,
            "negated": observation.negated,
            "certainty": observation.certainty,
            "temporality": observation.temporality,
            "severity": observation.severity,
            "body_site": observation.body_site,
            "laterality": observation.laterality,
            "course": observation.course,
            "measurement": dict(observation.measurement),
            "subject_ref": observation.subject_ref,
            "details": dict(observation.details),
            "symptom_data": observation.symptom_data,
            "injury_data": observation.injury_data,
            "measurement_data": observation.measurement_data,
            "medication_data": observation.medication_data,
            "diagnosis_data": observation.diagnosis_data,
            "confidence": observation.confidence,
            "verification_status": _verification_status_for_role(message_role),
            "provenance": [
                Provenance(
                    source=(
                        "user_correction"
                        if message_role == "correction"
                        else "user_message"
                    ),
                    source_span=observation.source_span,
                    confidence=observation.confidence,
                )
            ],
        }
        if observation.id:
            payload["id"] = observation.id
        return CaseObservation(**payload)


def build_extraction_context(
    *,
    latest_user_message: str,
    existing_case: MedicalCase | None = None,
    dialogue_state: DialogueState | None = None,
    messages: list[dict[str, str]] | None = None,
) -> ExtractionContext:
    recent_turns = _recent_turns(messages, latest_user_message=latest_user_message)
    last_assistant_question = _last_assistant_question(recent_turns)
    return ExtractionContext(
        latest_user_message=latest_user_message,
        pending_requirement=(
            dialogue_state.pending_requirement if dialogue_state is not None else None
        ),
        last_assistant_question=last_assistant_question,
        recent_turns=recent_turns,
        case_summary=_summarize_case(existing_case),
        dialogue_summary=_summarize_dialogue(dialogue_state, existing_case),
    )


def _recent_turns(
    messages: list[dict[str, str]] | None,
    *,
    latest_user_message: str,
) -> list[ConversationTurn]:
    if not messages:
        return []
    normalized_messages = [
        turn for turn in (_normalize_turn(message) for message in messages) if turn is not None
    ]
    if (
        normalized_messages
        and normalized_messages[-1].role == "user"
        and normalized_messages[-1].content.strip() == latest_user_message.strip()
    ):
        normalized_messages = normalized_messages[:-1]
    return normalized_messages[-MAX_RECENT_TURNS:]


def _normalize_turn(message: dict[str, str] | None) -> ConversationTurn | None:
    if not message:
        return None
    role = (message.get("role") or "").strip().lower()
    content = (message.get("content") or "").strip()
    if not role or not content:
        return None
    role_aliases = {
        "patient": "user",
        "careena": "assistant",
    }
    normalized_role = role_aliases.get(role, role)
    if normalized_role not in {"user", "assistant", "system"}:
        return None
    return ConversationTurn(role=normalized_role, content=content)


def _last_assistant_question(recent_turns: list[ConversationTurn]) -> str | None:
    for turn in reversed(recent_turns):
        if turn.role == "assistant":
            return turn.content
    return None


def _summarize_case(existing_case: MedicalCase | None) -> CaseSummary | None:
    if existing_case is None:
        return None
    existing_case.ensure_primary_problem()
    observations = [
        CaseSummaryObservation(
            id=observation.id,
            type=observation.type,
            display_label=observation.patient_label,
            concept=observation.concept,
            body_site=observation.runtime_value("body_site"),
            temporality=observation.runtime_value("temporality"),
            severity=observation.runtime_value("severity"),
            details=observation.details,
            verification_status=observation.verification_status,
        )
        for observation in existing_case.active_observations(include_rejected=False)
    ]
    return CaseSummary(
        subject_relation=existing_case.subject.relation,
        subject_age=existing_case.subject.age,
        primary_focus=existing_case.primary_focus_label(),
        primary_problem_id=existing_case.primary_problem_id,
        active_problem_ids=existing_case.active_problem_ids(),
        observations=observations[:6],
    )


def _summarize_dialogue(
    dialogue_state: DialogueState | None,
    existing_case: MedicalCase | None,
) -> DialogueSummary | None:
    if dialogue_state is None and existing_case is None:
        return None
    return DialogueSummary(
        pending_requirement=(
            dialogue_state.pending_requirement if dialogue_state is not None else None
        ),
        awaiting_confirmation=(
            dialogue_state.awaiting_confirmation if dialogue_state is not None else False
        ),
        pending_confirmation_observation_ids=(
            list(dialogue_state.pending_confirmation_observation_ids)
            if dialogue_state is not None
            else []
        ),
        pending_confirmation_subject=(
            dialogue_state.pending_confirmation_subject if dialogue_state is not None else False
        ),
        focus_observation_id=(
            dialogue_state.focus_observation_id if dialogue_state is not None else None
        ),
        focus_label=(
            existing_case.primary_focus_label() if existing_case is not None else None
        ),
        recommendation_requested=(
            dialogue_state.recommendation_requested if dialogue_state is not None else False
        ),
    )


def _verification_status_for_role(message_role: MessageRole) -> str:
    if message_role == "confirmation":
        return "confirmed"
    if message_role == "correction":
        return "corrected"
    return "extracted"
