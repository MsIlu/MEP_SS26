from dataclasses import dataclass

from careena_pipeline.llm import LLMCaseUpdateExtractor, LLMIntentGatewayExtractor
from careena_pipeline.models import (
    DialogueState,
    IntentGateway,
    MedicalCase,
    MessageUpdate,
    StagedFollowupAnswer,
)
from careena_pipeline.pipeline_rules import user_requests_recommendation
from careena_pipeline.planning import SlotFiller
from careena_pipeline.planning.requirement_state import (
    PendingFollowupContext,
)
from careena_pipeline.flow.message_update_factory import (
    build_intent_gateway_update,
    build_pending_followup_update,
    early_response_mode_for,
)
from careena_pipeline.flow.resolution_support import (
    CaseUpdateResolutionError,
    CaseUpdateResolutionService,
    FollowupShortcutService,
    IntentClassificationService,
    ResolutionFallbackPolicy,
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
        self.intent_classification = IntentClassificationService(
            intent_gateway_extractor=intent_gateway_extractor,
        )
        self.followup_shortcut = FollowupShortcutService(
            slot_filler=slot_filler,
        )
        self.case_update_resolution = CaseUpdateResolutionService(
            case_update_extractor=case_update_extractor,
        )
        self.fallback_policy = ResolutionFallbackPolicy()

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
        intent_gateway = self.intent_classification.classify(
            text=text,
            existing_case=existing_case,
            dialogue_state=dialogue_state,
            pending_slot=effective_pending_slot,
            conversation_messages=conversation_messages,
        )

        staged_followup_answers = self.followup_shortcut.resolve(
            text=text,
            existing_case=existing_case,
            pending_followup=pending_followup,
            intent_gateway=intent_gateway,
        )

        gateway_stop_result = self._resolve_gateway_only_stop(
            text=text,
            intent_gateway=intent_gateway,
            request_recommendation=request_recommendation,
            staged_followup_answers=staged_followup_answers,
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
            staged_followup_answers=staged_followup_answers,
            conversation_messages=conversation_messages,
        )

    @staticmethod
    def _resolve_gateway_only_stop(
        *,
        text: str,
        intent_gateway: IntentGateway | None,
        request_recommendation: bool,
        staged_followup_answers: list[StagedFollowupAnswer] | None,
    ) -> MessageResolutionResult | None:
        if staged_followup_answers:
            return None
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
        staged_followup_answers: list[StagedFollowupAnswer] | None,
        conversation_messages: list[dict[str, str]] | None,
    ) -> MessageResolutionResult:
        try:
            message_update = self.case_update_resolution.extract(
                text=text,
                existing_case=existing_case,
                dialogue_state=dialogue_state,
                pending_slot=pending_slot,
                intent_gateway=intent_gateway,
                staged_followup_answers=staged_followup_answers,
                conversation_messages=conversation_messages,
            )
        except CaseUpdateResolutionError as exc:
            return self.fallback_policy.fallback_for_case_update_error(
                text=text,
                existing_case=existing_case,
                pending_followup=pending_followup,
                pending_slot=pending_slot,
                intent_gateway=intent_gateway,
                request_recommendation=request_recommendation,
                staged_followup_answers=staged_followup_answers,
                shortcut_service=self.followup_shortcut,
                build_pending_followup_update=build_pending_followup_update,
                result_factory=MessageResolutionResult,
                error=exc,
            )

        return MessageResolutionResult(
            message_update=message_update,
            request_recommendation=message_update.planner_hints.recommendation_requested,
        )
