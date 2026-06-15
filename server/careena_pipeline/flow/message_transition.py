from dataclasses import dataclass

from careena_pipeline.models import DialogueState, MedicalCase, MessageUpdate
from careena_pipeline.observability import log_case_snapshot
from careena_pipeline.state import (
    CaseMerger,
    DialogueStateManager,
    StateProgressionService,
)


@dataclass
class AppliedMessageTransition:
    case: MedicalCase
    dialogue_state: DialogueState


class MessageTransitionService:
    """
    Applies a mergeable `MessageUpdate` to case and dialogue state.

    This keeps the actual state transition path out of `MessageParsingStep`
    so the flow step can stay focused on sequencing.
    """

    def __init__(
        self,
        *,
        case_merger: CaseMerger,
        dialogue_state_manager: DialogueStateManager,
    ):
        self.state_progression = StateProgressionService(
            case_merger=case_merger,
            dialogue_state_manager=dialogue_state_manager,
        )

    def apply(
        self,
        *,
        existing_case: MedicalCase | None,
        dialogue_state: DialogueState,
        message_update: MessageUpdate,
    ) -> AppliedMessageTransition:
        progression = self.state_progression.apply(
            existing_case=existing_case,
            dialogue_state=dialogue_state,
            message_update=message_update,
        )
        log_case_snapshot(progression.case)
        return AppliedMessageTransition(
            case=progression.case,
            dialogue_state=progression.dialogue_state,
        )
