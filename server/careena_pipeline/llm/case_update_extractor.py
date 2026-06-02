import json

from careena_pipeline.llm.context import build_case_update_context
from careena_pipeline.state.module_registry import (
    infer_active_modules,
    normalize_modules,
    parse_requirements,
    required_fields_for_modules,
)
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


class LLMCaseUpdateExtractor:
    """
    LLM module that directly produces a CaseUpdate-shaped result.

    This is the preferred active extraction path for Careena. The generic
    ExtractionEngine remains infrastructure; this class defines the concrete
    task and adapts the LLM-facing schema into internal pipeline models.
    """

    def __init__(self, engine: ExtractionEngine):
        self.engine = engine

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
        )

        active_modules = normalize_modules(llm_result.active_modules)
        if not active_modules:
            active_modules = infer_active_modules(
                has_subject_update=llm_result.subject is not None,
                observation_types=[
                    item.type
                    for item in llm_result.observations_added
                ],
            )

        required_fields = parse_requirements(llm_result.required_fields)
        if not required_fields:
            required_fields = required_fields_for_modules(active_modules)

        resolved_fields = parse_requirements(llm_result.resolved_fields)

        return MessageUpdate(
            raw_text=text,
            intent_category=(
                intent_gateway.category
                if intent_gateway is not None
                else llm_result.intent.category
            ),
            is_medical=(
                intent_gateway.is_medical
                if intent_gateway is not None
                else llm_result.intent.is_medical
            ),
            extraction_required=(
                intent_gateway.extraction_required
                if intent_gateway is not None
                else llm_result.intent.extraction_required
            ),
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
            message_role=(
                intent_gateway.message_role
                if intent_gateway is not None
                else llm_result.message_role
            ),
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
            confidence=observation.confidence,
            provenance=[
                Provenance(
                    source="user_message",
                    source_span=observation.source_span,
                    confidence=observation.confidence,
                )
            ],
        )
