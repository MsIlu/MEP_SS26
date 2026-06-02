from dataclasses import dataclass

from careena_pipeline.models import DialogueState, MedicalCase, MessageUpdate
from careena_pipeline.observability import log_case_snapshot
from careena_pipeline.state import CaseMerger, DialogueStateManager
from careena_pipeline.state.requirement_case_projector import RequirementCaseProjector


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
        requirement_case_projector: RequirementCaseProjector | None = None,
    ):
        self.case_merger = case_merger
        self.dialogue_state_manager = dialogue_state_manager
        self.requirement_case_projector = (
            requirement_case_projector or RequirementCaseProjector()
        )

    def apply(
        self,
        *,
        existing_case: MedicalCase | None,
        dialogue_state: DialogueState,
        message_update: MessageUpdate,
    ) -> AppliedMessageTransition:
        case = self.case_merger.merge_update(existing_case, message_update)
        self.requirement_case_projector.apply(case, message_update)
        dialogue_state = self.dialogue_state_manager.apply_message_update(
            dialogue_state,
            message_update,
            case,
        )
        self.dialogue_state_manager.sync_case(case, dialogue_state)
        log_case_snapshot(case)
        return AppliedMessageTransition(
            case=case,
            dialogue_state=dialogue_state,
        )
