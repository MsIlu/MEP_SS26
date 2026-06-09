from careena_pipeline3.domain.requirement_policy import RequirementPolicy
from careena_pipeline3.models.domain import DialogueState, MedicalCase
from careena_pipeline3.domain.case_update import DialogueConsequence
from careena_pipeline3.models.turn import ProcessStateUpdate


class DialogueStateService:
    """Synchronizes dialogue state from canonical case truth and active modules."""

    def __init__(self, *, requirement_policy: RequirementPolicy | None = None):
        self.requirement_policy = requirement_policy or RequirementPolicy()

    def sync_after_case_update(
        self,
        *,
        dialogue_state: DialogueState,
        medical_case: MedicalCase | None,
        active_modules: list[str],
        dialogue_consequences: list[DialogueConsequence] | None = None,
        person_reference_present: bool = False,
        multi_person_context: bool = False,
        subject_relation_unclear: bool = False,
    ) -> ProcessStateUpdate:
        synced_state = self.requirement_policy.sync_dialogue_state(
            dialogue_state=dialogue_state,
            medical_case=medical_case,
            active_modules=active_modules,
            person_reference_present=person_reference_present,
            multi_person_context=multi_person_context,
            subject_relation_unclear=subject_relation_unclear,
        )
        updated_state = self.requirement_policy.apply_dialogue_consequences(
            dialogue_state=synced_state,
            medical_case=medical_case,
            dialogue_consequences=dialogue_consequences or [],
        )
        return ProcessStateUpdate(
            dialogue_state=updated_state,
            pending_followup=updated_state.pending_followup,
        )
