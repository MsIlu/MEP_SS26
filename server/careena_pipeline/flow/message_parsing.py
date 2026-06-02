from careena_pipeline.llm import LLMCaseUpdateExtractor, LLMIntentGatewayExtractor
from careena_pipeline.observability import log_json
from careena_pipeline.planning.requirement_state import (
    build_pending_followup_context,
)
from careena_pipeline.planning import SlotFiller
from careena_pipeline.state import CaseMerger, DialogueStateManager
from careena_pipeline.models import DialogueState, MedicalCase
from careena_pipeline.safety import SafetyGate
from careena_pipeline.flow.outcomes import MessageParsingOutcome
from careena_pipeline.flow.message_parsing_policy import MessageParsingPolicy
from careena_pipeline.flow.message_resolution import MessageResolutionService
from careena_pipeline.flow.message_transition import MessageTransitionService


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
        self.safety_gate = safety_gate
        self.dialogue_state_manager = dialogue_state_manager
        self.parsing_policy = MessageParsingPolicy()
        self.message_resolution = MessageResolutionService(
            intent_gateway_extractor=intent_gateway_extractor,
            case_update_extractor=case_update_extractor,
            slot_filler=slot_filler,
        )
        self.message_transition = MessageTransitionService(
            case_merger=case_merger,
            dialogue_state_manager=dialogue_state_manager,
        )

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
        raw_safety = self.safety_gate.evaluate(raw_text=text)
        log_json("SAFETY RAW TEXT", raw_safety)
        safety_outcome = self.parsing_policy.outcome_from_raw_safety(
            raw_safety=raw_safety,
            dialogue_state=dialogue_state,
        )
        if safety_outcome is not None:
            return safety_outcome

        resolution = self.message_resolution.resolve(
            text=text,
            existing_case=existing_case,
            dialogue_state=dialogue_state,
            pending_followup=pending_followup,
            conversation_messages=conversation_messages,
        )

        policy_outcome = self.parsing_policy.outcome_from_resolution(
            raw_safety=raw_safety,
            dialogue_state=dialogue_state,
            resolution=resolution,
        )
        if policy_outcome is not None:
            return policy_outcome

        message_update = resolution.message_update
        transition = self.message_transition.apply(
            existing_case=existing_case,
            dialogue_state=dialogue_state,
            message_update=message_update,
        )

        return MessageParsingOutcome(
            raw_safety=raw_safety,
            dialogue_state=transition.dialogue_state,
            case=transition.case,
            message_update=message_update,
            request_recommendation=resolution.request_recommendation,
            force_deterministic_gate=resolution.force_deterministic_gate,
        )
