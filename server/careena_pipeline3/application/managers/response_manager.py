from careena_pipeline3.application.services import (
    RecommendationResultBuilder,
    ResponseTextBuilder,
)
from careena_pipeline3.models.turn import EntryDecision, ResponsePlan, SafetyState, TurnContext


class ResponseManager:
    """Chooses the response path and delegates wording to a dedicated builder."""

    def __init__(
        self,
        *,
        response_text_builder: ResponseTextBuilder | None = None,
        recommendation_result_builder: RecommendationResultBuilder | None = None,
    ):
        self.response_text_builder = response_text_builder or ResponseTextBuilder()
        self.recommendation_result_builder = (
            recommendation_result_builder or RecommendationResultBuilder()
        )

    def plan(
        self,
        *,
        context: TurnContext,
        entry_decision: EntryDecision,
        raw_safety: SafetyState,
        extraction_safety: SafetyState,
        case_safety: SafetyState,
    ) -> ResponsePlan:
        response_mode, trace_notes = self._select_response_path(
            context=context,
            entry_decision=entry_decision,
            raw_safety=raw_safety,
            extraction_safety=extraction_safety,
            case_safety=case_safety,
        )
        recommendation_result = self._build_recommendation_result(
            response_mode=response_mode,
            context=context,
        )
        response_text = self.response_text_builder.build(
            response_mode=response_mode,
            context=context,
            entry_decision=entry_decision,
            recommendation_result=recommendation_result,
        )
        return ResponsePlan(
            response_mode=response_mode,
            response_text=response_text,
            recommendation_result=recommendation_result,
            trace_notes=trace_notes,
        )

    def _build_recommendation_result(
        self,
        *,
        response_mode: str,
        context: TurnContext,
    ):
        if response_mode != "recommend":
            return None
        return self.recommendation_result_builder.build(context=context)

    def _select_response_path(
        self,
        *,
        context: TurnContext,
        entry_decision: EntryDecision,
        raw_safety: SafetyState,
        extraction_safety: SafetyState,
        case_safety: SafetyState,
    ) -> tuple[str, list[str]]:
        if (
            raw_safety.red_flag_detected
            or extraction_safety.red_flag_detected
            or case_safety.red_flag_detected
        ):
            return "emergency", ["response_manager_emergency"]

        if entry_decision.response_mode_hint is not None:
            return entry_decision.response_mode_hint, ["response_manager_entry_hint"]

        readiness = context.assessment_readiness

        if context.dialogue_state.pending_followup is not None:
            trace_head = (
                "response_manager_recommendation_followup_required"
                if context.dialogue_state.recommendation_requested
                else "response_manager_followup_required"
            )
            return "ask_followup", [
                trace_head,
                *[f"readiness:{tag}" for tag in readiness.reason_tags],
            ]

        if not readiness.has_medical_problem:
            trace_head = (
                "response_manager_recommendation_missing_problem"
                if context.dialogue_state.recommendation_requested
                else "response_manager_no_medical_problem"
            )
            return "cannot_assess", [
                trace_head,
                *[f"readiness:{tag}" for tag in readiness.reason_tags],
            ]

        if (
            context.dialogue_state.recommendation_requested
            and context.dialogue_state.recommendation_ready
        ):
            return "recommend", [
                "response_manager_recommendation_ready",
                *[f"readiness:{tag}" for tag in readiness.reason_tags],
            ]

        if context.dialogue_state.recommendation_ready:
            return "guide_next_step", [
                "response_manager_transition_ready",
                *[f"readiness:{tag}" for tag in readiness.reason_tags],
            ]

        return "continue", [
            "response_manager_continue_path",
            *[f"readiness:{tag}" for tag in readiness.reason_tags],
        ]
