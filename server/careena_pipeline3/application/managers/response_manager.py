from careena_pipeline3.application.services import (
    RecommendationResultBuilder,
    ResponseGenerationService,
)
from careena_pipeline3.models.domain import PendingDialogueTransition
from careena_pipeline3.models.turn import (
    EntryDecision,
    ResponsePlan,
    ResponseState,
    ResponseStrategy,
    SafetyState,
    TurnContext,
)


class ResponseManager:
    """
    Role:
    - owns late-turn response policy on top of an explicit small reaction
      state, then delegates wording to a dedicated builder.

    Input contract:
    - reads settled case/readiness/dialogue state plus small entry and safety
      signals.

    Output contract:
    - returns a `ResponsePlan` with explicit late-turn reaction state,
      visible response path, optional transition state, and optional
      recommendation payload.

    Does not decide:
    - medical case truth
    - extraction behavior
    - final recommendation content architecture

    Transitional:
    - yes; V4 keeps `response_mode` visible but recommendation/transition
      internals now survive only as legacy observability and future hooks.
    """

    def __init__(
        self,
        *,
        response_generation_service: ResponseGenerationService | None = None,
        recommendation_result_builder: RecommendationResultBuilder | None = None,
    ):
        self.response_generation_service = (
            response_generation_service or ResponseGenerationService()
        )
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
        latest_user_message: str = "",
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> ResponsePlan:
        response_state = self._build_response_state(
            context=context,
            entry_decision=entry_decision,
            raw_safety=raw_safety,
            extraction_safety=extraction_safety,
            case_safety=case_safety,
        )
        response_mode, trace_notes = self._select_response_path(
            context=context,
            response_state=response_state,
        )
        response_state.selected_response_mode = response_mode
        response_strategy = self._build_response_strategy(
            context=context,
            response_mode=response_mode,
            response_state=response_state,
        )
        pending_dialogue_transition = self._pending_dialogue_transition_for_response(
            response_mode=response_mode,
        )
        recommendation_result = self._build_recommendation_result(
            response_mode=response_mode,
            context=context,
        )
        response_text = self.response_generation_service.build(
            response_mode=response_mode,
            response_strategy=response_strategy,
            context=context,
            entry_decision=entry_decision,
            latest_user_message=latest_user_message,
            conversation_messages=conversation_messages,
            recommendation_result=recommendation_result,
        )
        return ResponsePlan(
            response_mode=response_mode,
            response_state=response_state,
            response_strategy=response_strategy,
            response_text=response_text,
            recommendation_result=recommendation_result,
            pending_dialogue_transition=pending_dialogue_transition,
            trace_notes=[
                *trace_notes,
                f"response_strategy:{response_strategy.kind}",
            ],
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

    @staticmethod
    def _pending_dialogue_transition_for_response(
        *,
        response_mode: str,
    ) -> PendingDialogueTransition | None:
        # Legacy recommendation transition hook; inactive for primary
        # pre-recommend routing in the minimal next-step model.
        return None

    def _build_response_state(
        self,
        *,
        context: TurnContext,
        entry_decision: EntryDecision,
        raw_safety: SafetyState,
        extraction_safety: SafetyState,
        case_safety: SafetyState,
    ) -> ResponseState:
        safety_override = None
        if (
            raw_safety.red_flag_detected
            or extraction_safety.red_flag_detected
            or case_safety.red_flag_detected
        ):
            safety_override = "emergency"

        readiness = context.assessment_readiness
        allowed_next_step = context.active_allowed_next_step
        transition_state = "inactive"
        if allowed_next_step == "stay_on_closing_check":
            transition_state = "awaiting_reply"
        elif allowed_next_step == "allow_recommendation":
            transition_state = "commit_recommendation"
        elif allowed_next_step == "return_to_medical":
            transition_state = "return_to_medical"

        medical_state = "sufficient_information"
        if context.dialogue_state.pending_followup is not None:
            medical_state = "followup_required"
        elif not readiness.has_medical_problem:
            medical_state = "no_medical_problem"

        recommendation_state = "not_requested"
        if allowed_next_step == "allow_recommendation":
            recommendation_state = "ready_for_recommendation"
        elif allowed_next_step == "stay_on_closing_check":
            recommendation_state = "ready_for_transition"
        elif context.dialogue_state.recommendation_requested:
            recommendation_state = "requested_not_ready"

        return ResponseState(
            safety_override=safety_override,
            entry_response_hint=entry_decision.response_mode_hint,
            medical_state=medical_state,
            transition_state=transition_state,
            recommendation_state=recommendation_state,
        )

    @staticmethod
    def _build_response_strategy(
        *,
        context: TurnContext,
        response_mode: str,
        response_state: ResponseState,
    ) -> ResponseStrategy:
        if response_mode == "emergency":
            return ResponseStrategy(kind="static_emergency")
        if response_mode == "out_of_scope":
            return ResponseStrategy(kind="static_out_of_scope")
        if response_mode == "ask_safety_question":
            # Formal safety hook only; real safety-question policy is added later.
            return ResponseStrategy(kind="static_safety_followup")
        if response_mode == "ask_followup":
            return ResponseStrategy(kind="static_followup")
        if response_mode == "guide_next_step":
            return ResponseStrategy(kind="static_recommendation_transition")
        if response_mode == "recommend":
            return ResponseStrategy(kind="static_recommendation_placeholder")
        if response_mode == "continue":
            if response_state.transition_state == "return_to_medical":
                return ResponseStrategy(kind="static_return_to_medical")
            return ResponseStrategy(kind="llm_bounded_response")
        return ResponseStrategy(kind="static_out_of_scope")

    def _select_response_path(
        self,
        *,
        context: TurnContext,
        response_state: ResponseState,
    ) -> tuple[str, list[str]]:
        readiness = context.assessment_readiness
        gate_decision = context.gate_decision
        allowed_next_step = context.active_allowed_next_step
        gate_reason_tags = gate_decision.reason_tags if gate_decision is not None else []
        if response_state.safety_override is not None:
            return response_state.safety_override, ["response_manager_emergency"]

        if response_state.entry_response_hint is not None:
            return response_state.entry_response_hint, ["response_manager_entry_hint"]

        if allowed_next_step == "safety_question":
            return "ask_safety_question", [
                "response_manager_safety_question_hook",
                f"response_state:transition:{response_state.transition_state}",
                f"response_state:recommendation:{response_state.recommendation_state}",
                *gate_reason_tags,
                *[f"readiness:{tag}" for tag in readiness.reason_tags],
            ]

        if allowed_next_step == "ask_clarifying_question":
            return "ask_followup", [
                "response_manager_concern_clarification",
                f"response_state:transition:{response_state.transition_state}",
                f"response_state:recommendation:{response_state.recommendation_state}",
                *gate_reason_tags,
                *[f"readiness:{tag}" for tag in readiness.reason_tags],
            ]

        if allowed_next_step == "stay_on_closing_check":
            return "guide_next_step", [
                "response_manager_closing_check",
                f"response_state:transition:{response_state.transition_state}",
                f"response_state:recommendation:{response_state.recommendation_state}",
                *gate_reason_tags,
                *[f"readiness:{tag}" for tag in readiness.reason_tags],
            ]

        if allowed_next_step == "allow_recommendation":
            return "recommend", [
                "response_manager_recommendation_allowed",
                f"response_state:transition:{response_state.transition_state}",
                f"response_state:recommendation:{response_state.recommendation_state}",
                *gate_reason_tags,
                *[f"readiness:{tag}" for tag in readiness.reason_tags],
            ]

        if allowed_next_step == "return_to_medical":
            return "continue", [
                "response_manager_return_to_medical",
                f"response_state:transition:{response_state.transition_state}",
                f"response_state:recommendation:{response_state.recommendation_state}",
                *gate_reason_tags,
                *[f"readiness:{tag}" for tag in readiness.reason_tags],
            ]

        if allowed_next_step == "out_of_scope":
            return "out_of_scope", [
                "response_manager_out_of_scope",
                f"response_state:transition:{response_state.transition_state}",
                f"response_state:recommendation:{response_state.recommendation_state}",
                *gate_reason_tags,
                *[f"readiness:{tag}" for tag in readiness.reason_tags],
            ]

        return "continue", [
            "response_manager_continue_path",
            "response_state:medical:sufficient_information",
            f"response_state:transition:{response_state.transition_state}",
            f"response_state:recommendation:{response_state.recommendation_state}",
            *[f"readiness:{tag}" for tag in readiness.reason_tags],
        ]
