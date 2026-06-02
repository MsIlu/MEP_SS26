from careena_pipeline.llm import LLMCaseUpdateExtractor, LLMIntentGatewayExtractor
from careena_pipeline.observability import log_case_snapshot, log_json
from careena_pipeline.planning.requirement_state import (
    PendingFollowupContext,
    build_pending_followup_context,
)
from careena_pipeline.planning import SlotFiller
from careena_pipeline.state import CaseMerger, DialogueStateManager
from careena_pipeline.core.exceptions import (
    EmptyLLMResponseError,
    InvalidJSONError,
    SchemaValidationError,
)
from careena_pipeline.models import DialogueState, IntentGateway, MedicalCase, MessageUpdate
from careena_pipeline.pipeline_rules import user_requests_recommendation
from careena_pipeline.safety import SafetyGate
from careena_pipeline.flow.outcomes import MessageParsingOutcome


class MessageParsingStep:
    """Builds message-driven state updates before the planning stages begin."""

    def __init__(
        self,
        *,
        intent_gateway_extractor: LLMIntentGatewayExtractor | None,
        case_update_extractor: LLMCaseUpdateExtractor,
        safety_gate: SafetyGate,
        case_merger: CaseMerger,
        slot_filler: SlotFiller,
        dialogue_state_manager: DialogueStateManager,
    ):
        self.intent_gateway_extractor = intent_gateway_extractor
        self.case_update_extractor = case_update_extractor
        self.safety_gate = safety_gate
        self.case_merger = case_merger
        self.slot_filler = slot_filler
        self.dialogue_state_manager = dialogue_state_manager

    def parse(
        self,
        *,
        text: str,
        existing_case: MedicalCase | None = None,
        existing_dialogue_state: DialogueState | None = None,
        pending_slot: str | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> MessageParsingOutcome:
        if existing_case is not None:
            existing_case.ensure_primary_problem()

        dialogue_state = self.dialogue_state_manager.ensure_state(
            existing_dialogue_state,
            existing_case,
        )
        pending_followup = build_pending_followup_context(
            dialogue_state.pending_followup or pending_slot
        )
        effective_pending_slot = pending_followup.normalized_slot

        raw_safety = self.safety_gate.evaluate(raw_text=text)
        log_json("SAFETY RAW TEXT", raw_safety)
        if raw_safety.red_flag_detected:
            return MessageParsingOutcome(
                raw_safety=raw_safety,
                dialogue_state=dialogue_state,
                early_response_mode="emergency",
            )

        request_recommendation = user_requests_recommendation(text)
        intent_gateway = self._classify_message(
            text=text,
            existing_case=existing_case,
            dialogue_state=dialogue_state,
            pending_slot=effective_pending_slot,
            conversation_messages=conversation_messages,
        )

        if self._should_attempt_slot_fill(
            existing_case=existing_case,
            pending_followup=pending_followup,
            intent_gateway=intent_gateway,
        ):
            slot_result = self.slot_filler.fill(
                existing_case,
                pending_followup,
                text,
            )
            if slot_result.filled:
                log_json(
                    "SLOT FILL",
                    {
                        "slot": effective_pending_slot,
                        "requirement": (
                            pending_followup.resolved_field.key
                            if pending_followup.resolved_field is not None
                            else None
                        ),
                        "text": text,
                    },
                )
                message_update = _build_slot_fill_update(
                    text=text,
                    pending_followup=pending_followup,
                    request_recommendation=request_recommendation,
                )
                dialogue_state = self.dialogue_state_manager.apply_message_update(
                    dialogue_state,
                    message_update,
                    existing_case,
                )
                return MessageParsingOutcome(
                    raw_safety=raw_safety,
                    dialogue_state=dialogue_state,
                    case=existing_case,
                    message_update=message_update,
                    request_recommendation=request_recommendation,
                )

        if intent_gateway is not None and not intent_gateway.extraction_required:
            return MessageParsingOutcome(
                raw_safety=raw_safety,
                dialogue_state=dialogue_state,
                message_update=_build_intent_gateway_update(
                    text=text,
                    intent_gateway=intent_gateway,
                    request_recommendation=request_recommendation,
                ),
                request_recommendation=request_recommendation,
                early_response_mode=_early_response_mode_for(intent_gateway),
            )

        try:
            message_update = self.case_update_extractor.extract_update(
                text,
                existing_case=existing_case,
                dialogue_state=dialogue_state,
                pending_slot=effective_pending_slot,
                intent_gateway=intent_gateway,
                conversation_messages=conversation_messages,
            )
        except (EmptyLLMResponseError, InvalidJSONError, SchemaValidationError) as exc:
            log_json(
                "CASE UPDATE EXTRACTION FAILED",
                {
                    "error": str(exc),
                    "pending_slot": effective_pending_slot,
                    "has_existing_case": existing_case is not None,
                },
            )
            if self._should_attempt_slot_fill(
                existing_case=existing_case,
                pending_followup=pending_followup,
                intent_gateway=intent_gateway,
            ):
                return MessageParsingOutcome(
                    raw_safety=raw_safety,
                    dialogue_state=dialogue_state,
                    case=existing_case,
                    message_update=_build_pending_followup_update(
                        text=text,
                        pending_followup=pending_followup,
                        request_recommendation=request_recommendation,
                        mark_resolved=False,
                    ),
                    request_recommendation=request_recommendation,
                    force_deterministic_gate=True,
                )

            return MessageParsingOutcome(
                raw_safety=raw_safety,
                dialogue_state=dialogue_state,
                early_response_mode="cannot_assess",
            )

        log_json("CASE UPDATE", message_update)

        if not message_update.is_medical:
            return MessageParsingOutcome(
                raw_safety=raw_safety,
                dialogue_state=dialogue_state,
                message_update=message_update,
                early_response_mode="out_of_scope",
            )

        if not message_update.extraction_required:
            return MessageParsingOutcome(
                raw_safety=raw_safety,
                dialogue_state=dialogue_state,
                message_update=message_update,
                early_response_mode="cannot_assess",
            )

        case = self.case_merger.merge_update(existing_case, message_update)
        dialogue_state = self.dialogue_state_manager.apply_message_update(
            dialogue_state,
            message_update,
            case,
        )
        self.dialogue_state_manager.sync_case(case, dialogue_state)
        log_case_snapshot(case)

        return MessageParsingOutcome(
            raw_safety=raw_safety,
            dialogue_state=dialogue_state,
            case=case,
            message_update=message_update,
            request_recommendation=message_update.user_requests_recommendation,
        )

    def _classify_message(
        self,
        *,
        text: str,
        existing_case: MedicalCase | None,
        dialogue_state: DialogueState,
        pending_slot: str | None,
        conversation_messages: list[dict[str, str]] | None,
    ) -> IntentGateway | None:
        if self.intent_gateway_extractor is None:
            return None

        try:
            return self.intent_gateway_extractor.classify(
                text,
                existing_case=existing_case,
                dialogue_state=dialogue_state,
                pending_slot=pending_slot,
                conversation_messages=conversation_messages,
            )
        except (EmptyLLMResponseError, InvalidJSONError, SchemaValidationError) as exc:
            log_json(
                "INTENT GATEWAY FAILED",
                {
                    "error": str(exc),
                    "pending_slot": pending_slot,
                    "has_existing_case": existing_case is not None,
                },
            )
            return None

    @staticmethod
    def _should_attempt_slot_fill(
        *,
        existing_case: MedicalCase | None,
        pending_followup: PendingFollowupContext,
        intent_gateway: IntentGateway | None,
    ) -> bool:
        if existing_case is None or pending_followup.normalized_slot is None:
            return False
        if intent_gateway is None:
            return True
        return intent_gateway.message_role == "answer_to_followup"


def _build_slot_fill_update(
    *,
    text: str,
    pending_followup: PendingFollowupContext,
    request_recommendation: bool,
) -> MessageUpdate:
    return _build_pending_followup_update(
        text=text,
        pending_followup=pending_followup,
        request_recommendation=request_recommendation,
        mark_resolved=True,
    )


def _build_pending_followup_update(
    *,
    text: str,
    pending_followup: PendingFollowupContext,
    request_recommendation: bool,
    mark_resolved: bool,
) -> MessageUpdate:
    return MessageUpdate(
        raw_text=text,
        is_medical=True,
        extraction_required=True,
        user_requests_recommendation=request_recommendation,
        message_role="answer_to_followup",
        active_modules=pending_followup.active_modules,
        required_fields=pending_followup.required_fields,
        resolved_fields=(
            [pending_followup.resolved_field]
            if mark_resolved and pending_followup.resolved_field is not None
            else []
        ),
        recommended_modules=[
            "recommendation_readiness",
            "routing_recommendation",
        ],
    )


def _build_intent_gateway_update(
    *,
    text: str,
    intent_gateway: IntentGateway,
    request_recommendation: bool,
) -> MessageUpdate:
    return MessageUpdate(
        raw_text=text,
        intent_category=intent_gateway.category,
        is_medical=intent_gateway.is_medical,
        extraction_required=intent_gateway.extraction_required,
        user_requests_recommendation=request_recommendation,
        message_role=intent_gateway.message_role,
        intent_gateway=intent_gateway,
    )


def _early_response_mode_for(intent_gateway: IntentGateway) -> str:
    if intent_gateway.category in {"smalltalk", "not_medical"}:
        return "out_of_scope"
    return "cannot_assess"
