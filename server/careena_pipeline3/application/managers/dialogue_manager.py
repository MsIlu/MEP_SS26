from __future__ import annotations

from careena_pipeline3.application.managers.case_state_manager import CaseStateManager
from careena_pipeline3.application.managers.confirmation_manager import ConfirmationManager
from careena_pipeline3.application.managers.entry_manager import EntryManager
from careena_pipeline3.application.managers.extraction_manager import ExtractionManager
from careena_pipeline3.application.managers.response_manager import ResponseManager
from careena_pipeline3.application.managers.safety_manager import SafetyManager
from careena_pipeline3.application.services import (
    DialogueStateService,
    RecommendationStateService,
)
from careena_pipeline3.models.turn import TurnContext, TurnInput, TurnResult


class DialogueManager:
    """
    Primary turn orchestrator for Careena Pipeline 3.

    The manager owns the per-turn execution order and composes specialized
    manager roles. Early migration stages keep the implementation intentionally
    thin while the surrounding manager contracts are established.
    """

    def __init__(
        self,
        *,
        entry_manager: EntryManager | None = None,
        extraction_manager: ExtractionManager | None = None,
        case_state_manager: CaseStateManager | None = None,
        safety_manager: SafetyManager | None = None,
        response_manager: ResponseManager | None = None,
        confirmation_manager: ConfirmationManager | None = None,
        dialogue_state_service: DialogueStateService | None = None,
        recommendation_state_service: RecommendationStateService | None = None,
    ):
        self.entry_manager = entry_manager or EntryManager()
        self.extraction_manager = extraction_manager or ExtractionManager()
        self.case_state_manager = case_state_manager or CaseStateManager()
        self.safety_manager = safety_manager or SafetyManager()
        self.response_manager = response_manager or ResponseManager()
        self.confirmation_manager = confirmation_manager or ConfirmationManager()
        self.dialogue_state_service = dialogue_state_service or DialogueStateService()
        self.recommendation_state_service = (
            recommendation_state_service or RecommendationStateService()
        )

    def run_turn(self, turn_input: TurnInput) -> TurnResult:
        context = TurnContext()
        context.medical_case = turn_input.existing_case
        if turn_input.existing_dialogue_state is not None:
            context.dialogue_state = turn_input.existing_dialogue_state
        raw_safety = self.safety_manager.assess_raw_message(turn_input)
        context.raw_safety = raw_safety
        context.trace_notes.extend(raw_safety.trace_notes)

        context = self.case_state_manager.ensure_case_context(context=context)
        context.pending_followup = context.dialogue_state.pending_followup

        entry_decision = self.entry_manager.evaluate(turn_input, context=context)
        context.active_modules = list(entry_decision.active_modules)
        context.person_reference_present = entry_decision.person_reference_present
        context.multi_person_context = entry_decision.multi_person_context
        context.subject_relation_unclear = entry_decision.subject_relation_unclear
        context.dialogue_state.recommendation_requested = (
            context.dialogue_state.recommendation_requested
            or entry_decision.recommendation_requested
        )
        context.trace_notes.extend(entry_decision.trace_notes)

        extraction_payload = self.extraction_manager.extract(
            turn_input=turn_input,
            entry_decision=entry_decision,
            context=context,
        )
        extraction_safety = self.safety_manager.assess_extraction(extraction_payload)
        context.extraction_safety = extraction_safety
        context.trace_notes.extend(extraction_safety.trace_notes)

        context = self.case_state_manager.apply_extraction(
            context=context,
            extraction_payload=extraction_payload,
        )
        if extraction_payload.message_delta is not None:
            context.dialogue_state.recommendation_requested = (
                context.dialogue_state.recommendation_requested
                or extraction_payload.message_delta.planner_signals.recommendation_requested
            )
            if extraction_payload.message_delta.planner_signals.recommended_modules:
                context.dialogue_state.recommended_modules = list(
                    extraction_payload.message_delta.planner_signals.recommended_modules
                )

        context.dialogue_state = self.dialogue_state_service.sync_after_case_update(
            dialogue_state=context.dialogue_state,
            medical_case=context.medical_case,
            active_modules=context.active_modules,
            dialogue_consequences=context.case_update_dialogue_consequences,
            person_reference_present=context.person_reference_present,
            multi_person_context=context.multi_person_context,
            subject_relation_unclear=context.subject_relation_unclear,
        )
        context.pending_followup = context.dialogue_state.pending_followup
        context.dialogue_state, context.assessment_readiness = (
            self.recommendation_state_service.sync_dialogue_state(
                dialogue_state=context.dialogue_state,
                medical_case=context.medical_case,
                person_reference_present=context.person_reference_present,
                multi_person_context=context.multi_person_context,
                subject_relation_unclear=context.subject_relation_unclear,
            )
        )
        context.pending_followup = context.dialogue_state.pending_followup
        case_safety = self.safety_manager.assess_case(context.medical_case)
        context.case_safety = case_safety
        context.trace_notes.extend(case_safety.trace_notes)

        response_plan = self.response_manager.plan(
            context=context,
            entry_decision=entry_decision,
            raw_safety=raw_safety,
            extraction_safety=extraction_safety,
            case_safety=case_safety,
        )
        context.response_mode = response_plan.response_mode
        context.trace_notes.extend(response_plan.trace_notes)

        if self.confirmation_manager.should_request_confirmation(context):
            context.trace_notes.append("confirmation_path_not_implemented")

        return TurnResult(
            response_mode=response_plan.response_mode,
            context=context,
            response_text=response_plan.response_text,
            recommendation_result=response_plan.recommendation_result,
        )
