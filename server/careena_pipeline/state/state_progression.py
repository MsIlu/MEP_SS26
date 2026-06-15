from dataclasses import dataclass

from careena_pipeline.models import DialogueState, MedicalCase, MessageUpdate
from careena_pipeline.state.case_merger import CaseMerger
from careena_pipeline.state.dialogue_state_manager import DialogueStateManager


@dataclass
class StateProgressionResult:
    case: MedicalCase
    dialogue_state: DialogueState


class StateProgressionService:
    """
    Owns the canonical per-turn state progression after resolution.

    The progression contract is:
    1. merge the message delta into case truth
    2. advance dialogue state from the merged case
    3. resync requirement progress from the anchored case state
    """

    def __init__(
        self,
        *,
        case_merger: CaseMerger,
        dialogue_state_manager: DialogueStateManager,
    ):
        self.case_merger = case_merger
        self.dialogue_state_manager = dialogue_state_manager

    def apply(
        self,
        *,
        existing_case: MedicalCase | None,
        dialogue_state: DialogueState,
        message_update: MessageUpdate,
    ) -> StateProgressionResult:
        case = self.case_merger.merge_update(existing_case, message_update)
        dialogue_state = self.dialogue_state_manager.apply_message_update(
            dialogue_state,
            message_update,
            case,
        )
        dialogue_state = self.dialogue_state_manager.sync_requirement_progress(
            dialogue_state,
            case=case,
            message_update=message_update,
        )
        self.dialogue_state_manager.sync_case(case, dialogue_state)
        return StateProgressionResult(
            case=case,
            dialogue_state=dialogue_state,
        )
