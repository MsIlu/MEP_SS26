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
from careena_pipeline3.models.turn import (
    ConfirmationDecision,
    EntryDecision,
    ProcessStateUpdate,
    ReadinessStateUpdate,
    ResponsePlan,
    SafetyState,
    TurnContext,
    TurnInput,
    TurnResult,
)


class DialogueManager:
    """
    Primary turn orchestrator for Careena Pipeline 3.

    The manager owns the per-turn execution order and composes specialized
    manager roles. Early migration stages keep the implementation intentionally
    thin while the surrounding manager contracts are established.

    Current boundary-first role:
    - owns turn sequencing and cross-step state progression
    - reads only small upstream signals where practical
    - delegates canonical case mutation to `CaseStateManager`
    - sequences visible safety, response, and confirmation stages
    - does not decide extraction internals or case-merge semantics itself
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

        # Seed the turn with persisted case and dialogue process state.
        context.medical_case = turn_input.existing_case
        if turn_input.existing_dialogue_state is not None:
            context.dialogue_state = turn_input.existing_dialogue_state

        # Run the first safety look on the raw user message.
        raw_safety = self.safety_manager.assess_raw_message(turn_input)
        self._apply_safety_state(
            context=context,
            stage="raw",
            safety_state=raw_safety,
        )

        # Ensure canonical case/process anchors exist before downstream work.
        context = self.case_state_manager.ensure_case_context(context=context)
        context.pending_followup = context.dialogue_state.pending_followup

        # Read small entry signals before deciding whether extraction runs.
        entry_decision = self.entry_manager.evaluate(turn_input, context=context)
        self._apply_entry_contract(context=context, entry_decision=entry_decision)

        # Run extraction and expose only the small orchestration-facing outputs.
        extraction_payload = self.extraction_manager.extract(
            turn_input=turn_input,
            entry_decision=entry_decision,
            context=context,
        )
        extraction_safety = self.safety_manager.assess_extraction(extraction_payload)
        self._apply_safety_state(
            context=context,
            stage="extraction",
            safety_state=extraction_safety,
        )

        # Progress canonical case truth from transitional extraction outputs.
        context = self.case_state_manager.apply_extraction(
            context=context,
            extraction_payload=extraction_payload,
        )

        # Derive process-state consequences from the updated case truth.
        process_state_update = self.dialogue_state_service.sync_after_case_update(
            dialogue_state=context.dialogue_state,
            medical_case=context.medical_case,
            active_modules=context.active_modules,
            dialogue_consequences=context.case_update_dialogue_consequences,
            person_reference_present=context.person_reference_present,
            multi_person_context=context.multi_person_context,
            subject_relation_unclear=context.subject_relation_unclear,
        )
        self._apply_process_state_update(
            context=context,
            process_state_update=process_state_update,
        )

        # Read recommendation/gating readiness from the settled process state.
        readiness_state_update = self.recommendation_state_service.sync_dialogue_state(
            dialogue_state=context.dialogue_state,
            medical_case=context.medical_case,
            person_reference_present=context.person_reference_present,
            multi_person_context=context.multi_person_context,
            subject_relation_unclear=context.subject_relation_unclear,
        )
        self._apply_readiness_state_update(
            context=context,
            readiness_state_update=readiness_state_update,
        )

        # Run the final safety look on the canonical case state.
        case_safety = self.safety_manager.assess_case(context.medical_case)
        self._apply_safety_state(
            context=context,
            stage="case",
            safety_state=case_safety,
        )

        # Choose the response policy and persist the final response contract.
        response_plan = self.response_manager.plan(
            context=context,
            entry_decision=entry_decision,
            raw_safety=raw_safety,
            extraction_safety=extraction_safety,
            case_safety=case_safety,
        )
        self._apply_response_contract(
            context=context,
            response_plan=response_plan,
        )

        # Keep confirmation as a visible late-stage boundary, even as placeholder.
        confirmation_decision = self.confirmation_manager.evaluate(context)
        self._apply_confirmation_contract(
            context=context,
            confirmation_decision=confirmation_decision,
        )

        return TurnResult(
            response_mode=context.response_mode or "continue",
            context=context,
            response_text=context.response_text,
            recommendation_result=context.recommendation_result,
        )

    def _apply_entry_contract(
        self,
        *,
        context: TurnContext,
        entry_decision: EntryDecision,
    ) -> None:
        """Apply small entry-stage steering signals to the turn context."""
        context.active_modules = list(entry_decision.active_modules)
        context.person_reference_present = entry_decision.person_reference_present
        context.multi_person_context = entry_decision.multi_person_context
        context.subject_relation_unclear = entry_decision.subject_relation_unclear
        context.dialogue_state.recommendation_requested = (
            context.dialogue_state.recommendation_requested
            or entry_decision.recommendation_requested
        )
        context.trace_notes.extend(entry_decision.trace_notes)

    def _apply_process_state_update(
        self,
        *,
        context: TurnContext,
        process_state_update: ProcessStateUpdate,
    ) -> None:
        """Apply process-state progression after case truth changed."""
        context.dialogue_state = process_state_update.dialogue_state
        context.pending_followup = process_state_update.pending_followup

    def _apply_readiness_state_update(
        self,
        *,
        context: TurnContext,
        readiness_state_update: ReadinessStateUpdate,
    ) -> None:
        """Apply readiness/gating progression after process state settled."""
        context.dialogue_state = readiness_state_update.dialogue_state
        context.assessment_readiness = readiness_state_update.assessment_readiness
        context.pending_followup = readiness_state_update.pending_followup

    def _apply_safety_state(
        self,
        *,
        context: TurnContext,
        stage: str,
        safety_state: SafetyState,
    ) -> None:
        """Apply one visible safety-stage result to the turn context."""
        if stage == "raw":
            context.raw_safety = safety_state
        elif stage == "extraction":
            context.extraction_safety = safety_state
        elif stage == "case":
            context.case_safety = safety_state
        else:
            raise ValueError(f"unknown safety stage: {stage}")
        context.trace_notes.extend(safety_state.trace_notes)

    def _apply_response_contract(
        self,
        *,
        context: TurnContext,
        response_plan: ResponsePlan,
    ) -> None:
        """Apply the explicit response-policy result to the turn context."""
        context.response_mode = response_plan.response_mode
        context.response_text = response_plan.response_text
        context.recommendation_result = response_plan.recommendation_result
        context.trace_notes.extend(response_plan.trace_notes)

    def _apply_confirmation_contract(
        self,
        *,
        context: TurnContext,
        confirmation_decision: ConfirmationDecision,
    ) -> None:
        """
        Apply the visible confirmation-stage result.

        Confirmation is still placeholder-heavy, so the current contract mainly
        makes that late-stage boundary explicit without pretending it is fully
        implemented.
        """
        context.trace_notes.extend(confirmation_decision.trace_notes)
        if confirmation_decision.should_request_confirmation:
            context.trace_notes.append("confirmation_path_not_implemented")
