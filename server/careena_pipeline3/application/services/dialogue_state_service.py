from careena_pipeline3.domain.requirement_policy import RequirementPolicy
from careena_pipeline3.models.domain import DialogueState, MedicalCase, PendingFollowup
from careena_pipeline3.domain.case_update import DialogueConsequence
from careena_pipeline3.models.turn import ProcessStateSignals, ProcessStateUpdate


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
        previous_pending_followup: PendingFollowup | None = None,
        additional_medical_information: bool = False,
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
        process_state_signals = self._build_process_state_signals(
            dialogue_state=updated_state,
            previous_pending_followup=previous_pending_followup,
            additional_medical_information=additional_medical_information,
        )
        return ProcessStateUpdate(
            dialogue_state=updated_state,
            pending_followup=updated_state.pending_followup,
            process_state_signals=process_state_signals,
        )

    def _build_process_state_signals(
        self,
        *,
        dialogue_state: DialogueState,
        previous_pending_followup: PendingFollowup | None,
        additional_medical_information: bool,
    ) -> ProcessStateSignals:
        signals = ProcessStateSignals()
        if (
            previous_pending_followup is not None
            and previous_pending_followup.kind == "requirement"
        ):
            if (
                previous_pending_followup.requirement_key
                in dialogue_state.resolved_requirements
            ):
                signals.answered_pending_followup = True
                signals.answered_requirement_key = (
                    previous_pending_followup.requirement_key
                )
                signals.answered_slot = previous_pending_followup.slot
                signals.trace_notes.append(
                    "process_state:answered_pending_followup:"
                    f"{previous_pending_followup.requirement_key}"
                )
            if additional_medical_information:
                signals.additional_medical_information_detected = True
                signals.trace_notes.append(
                    "process_state:additional_medical_information_detected"
                )
                if signals.answered_pending_followup:
                    signals.trace_notes.append(
                        "process_state:mixed_followup_and_additional_information"
                    )
        return signals
