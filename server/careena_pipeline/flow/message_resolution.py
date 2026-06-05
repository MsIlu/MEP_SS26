from dataclasses import dataclass

from careena_pipeline.core.exceptions import (
    EmptyLLMResponseError,
    InvalidJSONError,
    SchemaValidationError,
)
from careena_pipeline.llm import LLMCaseUpdateExtractor, LLMIntentGatewayExtractor
from careena_pipeline.models import DialogueState, IntentGateway, MedicalCase, MessageUpdate
from careena_pipeline.observability import log_json
from careena_pipeline.pipeline_rules import user_requests_recommendation
from careena_pipeline.planning import SlotFiller
from careena_pipeline.planning.requirement_state import (
    PendingFollowupContext,
)


@dataclass
class MessageResolutionResult:
    message_update: MessageUpdate | None = None
    request_recommendation: bool = False
    force_deterministic_gate: bool = False
    early_response_mode: str | None = None


class MessageResolutionService:
    """
    Resolves one incoming message into a `MessageUpdate`-shaped transition.

    This service keeps the ordered resolution paths out of
    `MessageParsingStep`, so the step can stay closer to pure orchestration.

    Current path order:
    1. Call 1 classification
    2. slot-fill shortcut for follow-up answers
    3. gateway-only early stop when no Call 2 is needed
    4. Call 2 extraction
    5. extraction-failure fallback
    """

    def __init__(
        self,
        *,
        intent_gateway_extractor: LLMIntentGatewayExtractor | None,
        case_update_extractor: LLMCaseUpdateExtractor,
        slot_filler: SlotFiller,
    ):
        self.intent_gateway_extractor = intent_gateway_extractor
        self.case_update_extractor = case_update_extractor
        self.slot_filler = slot_filler

    def resolve(
        self,
        *,
        text: str,
        existing_case: MedicalCase | None,
        dialogue_state: DialogueState,
        pending_followup: PendingFollowupContext,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> MessageResolutionResult:
        effective_pending_slot = pending_followup.normalized_slot
        request_recommendation = user_requests_recommendation(text)
        intent_gateway = self._classify_message(
            text=text,
            existing_case=existing_case,
            dialogue_state=dialogue_state,
            pending_slot=effective_pending_slot,
            conversation_messages=conversation_messages,
        )

        slot_fill_result = self._resolve_slot_fill_shortcut(
            text=text,
            existing_case=existing_case,
            pending_followup=pending_followup,
            intent_gateway=intent_gateway,
            request_recommendation=request_recommendation,
        )
        if slot_fill_result is not None:
            return slot_fill_result

        gateway_stop_result = self._resolve_gateway_only_stop(
            text=text,
            intent_gateway=intent_gateway,
            request_recommendation=request_recommendation,
        )
        if gateway_stop_result is not None:
            return gateway_stop_result

        return self._resolve_case_update_path(
            text=text,
            existing_case=existing_case,
            dialogue_state=dialogue_state,
            pending_followup=pending_followup,
            pending_slot=effective_pending_slot,
            intent_gateway=intent_gateway,
            request_recommendation=request_recommendation,
            conversation_messages=conversation_messages,
        )

    def _resolve_slot_fill_shortcut(
        self,
        *,
        text: str,
        existing_case: MedicalCase | None,
        pending_followup: PendingFollowupContext,
        intent_gateway: IntentGateway | None,
        request_recommendation: bool,
    ) -> MessageResolutionResult | None:
        if not self._should_attempt_slot_fill(
            existing_case=existing_case,
            pending_followup=pending_followup,
            intent_gateway=intent_gateway,
        ):
            return None

        slot_result = self.slot_filler.fill(
            existing_case,
            pending_followup,
            text,
        )
        if not slot_result.filled:
            return None

        log_json(
            "SLOT FILL",
            {
                "slot": pending_followup.normalized_slot,
                "requirement": (
                    pending_followup.resolved_field.key
                    if pending_followup.resolved_field is not None
                    else None
                ),
                "text": text,
            },
        )
        return MessageResolutionResult(
            message_update=build_slot_fill_update(
                text=text,
                pending_followup=pending_followup,
                request_recommendation=request_recommendation,
            ),
            request_recommendation=request_recommendation,
        )

    @staticmethod
    def _resolve_gateway_only_stop(
        *,
        text: str,
        intent_gateway: IntentGateway | None,
        request_recommendation: bool,
    ) -> MessageResolutionResult | None:
        if intent_gateway is None or intent_gateway.extraction_required:
            return None

        return MessageResolutionResult(
            message_update=build_intent_gateway_update(
                text=text,
                intent_gateway=intent_gateway,
                request_recommendation=request_recommendation,
            ),
            request_recommendation=request_recommendation,
            early_response_mode=early_response_mode_for(intent_gateway),
        )

    def _resolve_case_update_path(
        self,
        *,
        text: str,
        existing_case: MedicalCase | None,
        dialogue_state: DialogueState,
        pending_followup: PendingFollowupContext,
        pending_slot: str | None,
        intent_gateway: IntentGateway | None,
        request_recommendation: bool,
        conversation_messages: list[dict[str, str]] | None,
    ) -> MessageResolutionResult:
        try:
            message_update = self.case_update_extractor.extract_update(
                text,
                existing_case=existing_case,
                dialogue_state=dialogue_state,
                pending_slot=pending_slot,
                intent_gateway=intent_gateway,
                conversation_messages=conversation_messages,
            )
        except (EmptyLLMResponseError, InvalidJSONError, SchemaValidationError) as exc:
            return self._resolve_extraction_failure(
                text=text,
                existing_case=existing_case,
                pending_followup=pending_followup,
                pending_slot=pending_slot,
                intent_gateway=intent_gateway,
                request_recommendation=request_recommendation,
                error=exc,
            )

        log_json("CASE UPDATE", message_update)
        return MessageResolutionResult(
            message_update=message_update,
            request_recommendation=message_update.planner_hints.recommendation_requested,
        )

    def _resolve_extraction_failure(
        self,
        *,
        text: str,
        existing_case: MedicalCase | None,
        pending_followup: PendingFollowupContext,
        pending_slot: str | None,
        intent_gateway: IntentGateway | None,
        request_recommendation: bool,
        error: Exception,
    ) -> MessageResolutionResult:
        log_json(
            "CASE UPDATE EXTRACTION FAILED",
            {
                "error": str(error),
                "pending_slot": pending_slot,
                "has_existing_case": existing_case is not None,
            },
        )
        if self._should_attempt_slot_fill(
            existing_case=existing_case,
            pending_followup=pending_followup,
            intent_gateway=intent_gateway,
        ):
            return MessageResolutionResult(
                message_update=build_pending_followup_update(
                    text=text,
                    pending_followup=pending_followup,
                    request_recommendation=request_recommendation,
                    mark_resolved=False,
                ),
                request_recommendation=request_recommendation,
                force_deterministic_gate=True,
            )

        return MessageResolutionResult(
            request_recommendation=request_recommendation,
            early_response_mode="cannot_assess",
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


def build_slot_fill_update(
    *,
    text: str,
    pending_followup: PendingFollowupContext,
    request_recommendation: bool,
) -> MessageUpdate:
    return build_pending_followup_update(
        text=text,
        pending_followup=pending_followup,
        request_recommendation=request_recommendation,
        mark_resolved=True,
    )


def build_pending_followup_update(
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


def build_intent_gateway_update(
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


def early_response_mode_for(intent_gateway: IntentGateway) -> str:
    if intent_gateway.category in {"smalltalk", "not_medical"}:
        return "out_of_scope"
    return "cannot_assess"
