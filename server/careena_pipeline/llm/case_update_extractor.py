import json
from dataclasses import dataclass

from careena_pipeline.llm.context import build_case_update_context
from careena_pipeline.llm.call_control import (
    CASE_UPDATE_CALL,
    CallModelConfig,
)
from careena_pipeline.planning.requirement_state import (
    resolve_active_modules,
    resolve_required_fields,
)
from careena_pipeline.state.module_registry import parse_requirements
from careena_pipeline.core.engine import ExtractionEngine
from careena_pipeline.models import (
    CaseObservation,
    DialogueState,
    IntentGateway,
    MedicalCase,
    MessageUpdate,
    Provenance,
    Subject,
)
from careena_pipeline.models.llm.case_update_result import (
    LLMCaseUpdateObservation,
    LLMCaseUpdateResult,
)
from careena_pipeline.observability import log_json
from careena_pipeline.llm.prompts.case_update import (
    build_case_update_system_prompt,
)


@dataclass(frozen=True)
class _ResolvedIntent:
    category: str
    is_medical: bool
    extraction_required: bool
    message_role: str


class LLMCaseUpdateExtractor:
    """
    Primary Call 2 that produces the CaseUpdate-shaped result.

    This is the preferred active extraction path for Careena. The generic
    ExtractionEngine remains infrastructure; this class defines the concrete
    task and adapts the LLM-facing schema into internal pipeline models.
    """

    def __init__(
        self,
        engine: ExtractionEngine,
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
        pending_slot: str | None = None,
        intent_gateway: IntentGateway | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> MessageUpdate:
        system_prompt = build_case_update_system_prompt(
            pending_slot=pending_slot,
        )
        context = build_case_update_context(
            latest_user_message=text,
            existing_case=existing_case,
            dialogue_state=dialogue_state,
            pending_slot=pending_slot,
            intent_gateway=intent_gateway,
            messages=conversation_messages,
        )
        log_json(
            "CASE UPDATE PROMPT",
            {
                "pending_slot": pending_slot,
            },
        )
        log_json("CASE UPDATE CONTEXT", context)

        llm_result = self.engine.extract(
            text=json.dumps(context.model_dump(), ensure_ascii=False),
            system_prompt=system_prompt,
            output_schema=LLMCaseUpdateResult,
            max_tokens=1800,
            model=(
                self.call_models.model_for(CASE_UPDATE_CALL)
                if self.call_models is not None
                else None
            ),
        )

        active_modules = resolve_active_modules(
            explicit_modules=llm_result.active_modules,
            has_subject_update=llm_result.subject is not None,
            observation_types=[
                item.type
                for item in llm_result.observations_added
            ],
        )

        required_fields = resolve_required_fields(
            explicit_fields=llm_result.required_fields,
            active_modules=active_modules,
        )

        resolved_fields = parse_requirements(llm_result.resolved_fields)
        resolved_intent = _resolve_intent_signals(
            llm_result=llm_result,
            intent_gateway=intent_gateway,
            pending_slot=pending_slot,
            resolved_fields=resolved_fields,
        )

        return MessageUpdate(
            raw_text=text,
            intent_category=resolved_intent.category,
            is_medical=resolved_intent.is_medical,
            extraction_required=resolved_intent.extraction_required,
            intent_confidence=llm_result.intent.confidence,
            subject=self._adapt_subject(llm_result.subject),
            observations_added=[
                self._adapt_observation(item)
                for item in llm_result.observations_added
            ],
            negated_observations_added=[
                self._adapt_observation(item)
                for item in llm_result.negated_observations_added
            ],
            user_requests_recommendation=llm_result.user_requests_recommendation,
            possible_new_topic=llm_result.possible_new_topic,
            message_role=resolved_intent.message_role,
            intent_gateway=intent_gateway,
            llm_intent_category=llm_result.intent.category,
            llm_is_medical=llm_result.intent.is_medical,
            llm_extraction_required=llm_result.intent.extraction_required,
            llm_message_role=llm_result.message_role,
            active_modules=active_modules,
            required_fields=required_fields,
            resolved_fields=resolved_fields,
            recommended_modules=llm_result.recommended_modules,
            notes=llm_result.notes or [],
        )

    @staticmethod
    def _adapt_subject(subject) -> Subject | None:
        if subject is None:
            return None

        return Subject(
            relation=subject.relation,
            description=subject.description,
            age=subject.age,
            sex=subject.sex,
            confidence=subject.confidence,
        )

    @staticmethod
    def _adapt_observation(observation: LLMCaseUpdateObservation) -> CaseObservation:
        return CaseObservation(
            id=observation.id,
            type=observation.type,
            label=observation.label,
            display_label=observation.display_label,
            concept=observation.concept,
            source_span=observation.source_span,
            negated=observation.negated,
            certainty=observation.certainty,
            temporality=observation.temporality,
            severity=observation.severity,
            body_site=observation.body_site,
            laterality=observation.laterality,
            course=observation.course,
            measurement=observation.measurement,
            subject_ref=observation.subject_ref,
            details=observation.details,
            confidence=observation.confidence,
            provenance=[
                Provenance(
                    source="user_message",
                    source_span=observation.source_span,
                    confidence=observation.confidence,
                )
            ],
        )


def _resolve_intent_signals(
    *,
    llm_result: LLMCaseUpdateResult,
    intent_gateway: IntentGateway | None,
    pending_slot: str | None,
    resolved_fields,
) -> _ResolvedIntent:
    has_structured_update = _has_structured_update(
        llm_result=llm_result,
        resolved_fields=resolved_fields,
    )

    category = llm_result.intent.category
    is_medical = llm_result.intent.is_medical or has_structured_update
    extraction_required = (
        llm_result.intent.extraction_required
        or has_structured_update
        or llm_result.user_requests_recommendation
    )
    message_role = llm_result.message_role

    # Let Call 2 carry the final extraction view, but keep Call 1 as a narrow
    # guardrail when the extracted payload clearly resolved an awaited follow-up.
    if (
        intent_gateway is not None
        and pending_slot
        and message_role == "new_information"
        and intent_gateway.message_role == "answer_to_followup"
        and resolved_fields
        and not llm_result.possible_new_topic
    ):
        message_role = "answer_to_followup"

    if (
        intent_gateway is not None
        and intent_gateway.is_medical
        and has_structured_update
        and category in {"smalltalk", "not_medical"}
    ):
        category = intent_gateway.category
        is_medical = True

    return _ResolvedIntent(
        category=category,
        is_medical=is_medical,
        extraction_required=extraction_required,
        message_role=message_role,
    )


def _has_structured_update(
    *,
    llm_result: LLMCaseUpdateResult,
    resolved_fields,
) -> bool:
    return any(
        (
            llm_result.subject is not None,
            bool(llm_result.observations_added),
            bool(llm_result.negated_observations_added),
            bool(resolved_fields),
            bool(llm_result.active_modules),
            bool(llm_result.required_fields),
        )
    )
