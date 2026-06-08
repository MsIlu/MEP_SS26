from careena_pipeline3.domain import CaseMerger, DialogueFocusSync
from careena_pipeline3.models.domain import MedicalCase
from careena_pipeline3.models.turn import ExtractionPayload, TurnContext


"""
Date: 2026-06-08
Last changed: 2026-06-08
Author: workbench@freddy

Short description:
Owns canonical case-state progression inside the turn orchestrator.
It ensures case context exists and applies extraction updates into case truth and focus state.
"""
class CaseStateManager:
    """Owns canonical case-state progression from extracted information."""

    def __init__(
        self,
        *,
        case_merger: CaseMerger | None = None,
        focus_sync: DialogueFocusSync | None = None,
    ):
        self.case_merger = case_merger or CaseMerger()
        self.focus_sync = focus_sync or DialogueFocusSync()

    def ensure_case_context(
        self,
        *,
        context: TurnContext,
    ) -> TurnContext:
        if context.medical_case is None:
            context.medical_case = MedicalCase()

        context.dialogue_state = self.focus_sync.ensure_state_links(
            context.dialogue_state,
            context.medical_case,
        )
        return context

    def apply_extraction(
        self,
        *,
        context: TurnContext,
        extraction_payload: ExtractionPayload,
    ) -> TurnContext:
        context = self.ensure_case_context(context=context)
        if extraction_payload.active_modules:
            context.active_modules = list(extraction_payload.active_modules)
        if extraction_payload.message_delta is not None:
            update_outcome = self.case_merger.merge_delta(
                context.medical_case,
                extraction_payload.message_delta,
            )
            context.medical_case = update_outcome.medical_case
            context.case_update_dialogue_consequences = list(
                update_outcome.dialogue_consequences
            )
            context.trace_notes.extend(update_outcome.trace_notes)
            context.trace_notes.extend(
                [
                    f"case_state_manager:dialogue_consequence:{consequence}"
                    for consequence in update_outcome.dialogue_consequences
                ]
            )

        context.trace_notes.extend(extraction_payload.trace_notes)
        context.dialogue_state = self.focus_sync.sync_state_from_case(
            context.dialogue_state,
            context.medical_case,
        )
        return context
