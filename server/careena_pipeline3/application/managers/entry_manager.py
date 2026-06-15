from careena_pipeline3.application.services.call2_operation_mode_service import (
    Call2OperationModeService,
)
from careena_pipeline3.application.services.intent_classification_service import (
    IntentClassificationService,
)
from careena_pipeline3.application.services.requirement_followup_resolution_service import (
    RequirementFollowupResolutionService,
)
from careena_pipeline3.application.services.recommendation_transition_service import (
    RecommendationChoiceResolutionService,
)
from careena_pipeline3.application.services.recommendation_request_service import (
    RecommendationRequestService,
)
from careena_pipeline3.application.services.safety_clarification_resolver import (
    SafetyClarificationResolver,
)
from careena_pipeline3.models.turn import EntryDecision, TurnContext, TurnInput


class EntryManager:
    """
    Role:
    - maps the Call-1 scout result into the smaller turn-entry contract used
      by the orchestrator.

    Input contract:
    - latest turn input plus current turn context
    - grouped Call-1 signals from the intent gateway
    - optional choice-prompt normalization result for an active
      recommendation choice question

    Output contract:
    - small entry-stage steering signals for extraction, person context,
      recommendation-request intent, and choice-prompt observability

    Does not decide:
    - case truth
    - merge semantics
    - recommendation readiness

    Transitional:
    - yes; the manager still carries a small recommendation-choice helper
      contract while the late closing node is being separated from older
      transition terminology.
    """

    def __init__(
        self,
        *,
        call2_operation_mode_service: Call2OperationModeService | None = None,
        intent_classification: IntentClassificationService | None = None,
        recommendation_request_service: RecommendationRequestService | None = None,
        recommendation_choice_resolution_service: (
            RecommendationChoiceResolutionService | None
        ) = None,
        requirement_followup_resolution_service: (
            RequirementFollowupResolutionService | None
        ) = None,
        safety_clarification_resolver: SafetyClarificationResolver | None = None,
    ):
        self.call2_operation_mode_service = (
            call2_operation_mode_service or Call2OperationModeService()
        )
        self.intent_classification = intent_classification or IntentClassificationService(
            intent_gateway_extractor=None,
        )
        self.recommendation_request_service = (
            recommendation_request_service or RecommendationRequestService()
        )
        self.recommendation_choice_resolution_service = (
            recommendation_choice_resolution_service
            or RecommendationChoiceResolutionService()
        )
        self.requirement_followup_resolution_service = (
            requirement_followup_resolution_service
            or RequirementFollowupResolutionService()
        )
        self.safety_clarification_resolver = (
            safety_clarification_resolver or SafetyClarificationResolver()
        )

    def evaluate(
        self,
        turn_input: TurnInput,
        *,
        context: TurnContext | None = None,
    ) -> EntryDecision:
        message = turn_input.message.strip()
        if not message:
            return EntryDecision(
                extraction_required=False,
                recommendation_requested=False,
                response_mode_hint="ask_followup",
                concern_relation="dialogue_only",
                latest_turn_role="unclear",
                trace_notes=["empty_message"],
            )

        pending_safety_clarification = (
            context.dialogue_state.pending_safety_clarification
            if context is not None
            else None
        )
        if pending_safety_clarification is not None:
            safety_resolution = self.safety_clarification_resolver.resolve(
                pending=pending_safety_clarification,
                answer_code=message,
            )
            return EntryDecision(
                extraction_required=False,
                recommendation_requested=False,
                clear_pending_safety_clarification=(
                    safety_resolution.clear_pending_clarification
                ),
                safety_clarification_resolution=safety_resolution,
                concern_relation="dialogue_only",
                latest_turn_role="dialogue_response",
                trace_notes=[
                    "pending_safety_clarification:red_flag_clarification",
                    "safety_clarification_outcome:"
                    f"{safety_resolution.outcome.value}",
                    *safety_resolution.trace_notes,
                ],
            )

        pending_followup = context.dialogue_state.pending_followup if context is not None else None
        if pending_followup is not None and pending_followup.kind == "requirement":
            resolution, field_update = self.requirement_followup_resolution_service.resolve(
                latest_user_message=turn_input.message,
                pending_followup=pending_followup,
                medical_case=(context.medical_case if context is not None else None),
                dialogue_state=(context.dialogue_state if context is not None else None),
                history_messages=turn_input.entry_history_messages,
            )
            if resolution is not None:
                return EntryDecision(
                    extraction_required=False,
                    recommendation_requested=False,
                    clear_pending_followup=(field_update is not None),
                    requirement_followup_resolution=resolution,
                    requirement_field_update=field_update,
                    message_role="answer_to_followup",
                    concern_relation="same_concern",
                    latest_turn_role="medical_clarification",
                    trace_notes=[
                        "pending_requirement_followup",
                        f"requirement_followup_status:{resolution.status}",
                        (
                            "requirement_followup_contains_extra_medical_information"
                            if resolution.contains_extra_medical_information
                            else "requirement_followup_without_extra_medical_information"
                        ),
                        *resolution.trace_notes,
                    ],
                )

        pending_choice_prompt = (
            context.dialogue_state.pending_choice_prompt if context is not None else None
        )
        choice_resolution = self.recommendation_choice_resolution_service.resolve(
            text=message,
            pending_choice_prompt=pending_choice_prompt,
            transition_history_messages=turn_input.transition_history_messages,
        )
        if choice_resolution is not None and choice_resolution.action == "request_recommendation":
            return EntryDecision(
                extraction_required=False,
                recommendation_requested=True,
                clear_pending_choice_prompt=True,
                choice_prompt_action="request_recommendation",
                concern_relation="dialogue_only",
                latest_turn_role="closing_choice",
                trace_notes=[
                    "choice_prompt_resolution_observed",
                    "pending_choice_prompt:recommendation_choice",
                    "choice_prompt:recommendation_choice:request_recommendation",
                    *choice_resolution.trace_notes,
                ],
            )
        if (
            choice_resolution is not None
            and choice_resolution.action == "report_more_information"
            and message == "report_more_information"
        ):
            return EntryDecision(
                extraction_required=False,
                recommendation_requested=False,
                clear_pending_choice_prompt=True,
                choice_prompt_action="report_more_information",
                concern_relation="same_concern",
                latest_turn_role="closing_choice",
                trace_notes=[
                    "choice_prompt_resolution_observed",
                    "pending_choice_prompt:recommendation_choice",
                    "choice_prompt:recommendation_choice:report_more_information",
                    *choice_resolution.trace_notes,
                ],
            )
        choice_prompt_trace_notes: list[str] = []
        if choice_resolution is not None:
            choice_prompt_trace_notes = [
                "choice_prompt_resolution_observed",
                f"choice_prompt:recommendation_choice:{choice_resolution.action}",
                *choice_resolution.trace_notes,
            ]

        gateway = self.intent_classification.classify(
            text=turn_input.message,
            existing_case=(context.medical_case if context is not None else None),
            dialogue_state=(context.dialogue_state if context is not None else None),
            pending_slot=(
                context.dialogue_state.pending_followup.slot
                if (
                    context is not None
                    and context.dialogue_state.pending_followup is not None
                    and context.dialogue_state.pending_followup.kind == "requirement"
                )
                else None
            ),
            entry_history_messages=turn_input.entry_history_messages,
        )
        if gateway is None:
            return EntryDecision(
                extraction_required=True,
                recommendation_requested=False,
                concern_relation="unclear",
                latest_turn_role="unclear",
                trace_notes=["intent_gateway_unavailable"],
            )

        recommendation_requested = self.recommendation_request_service.is_requested(
            turn_input.message,
            gateway=gateway,
        )
        call2_operation_mode = self.call2_operation_mode_service.resolve(
            gateway=gateway,
            context=context,
        )
        response_mode_hint = self._response_mode_hint_for_gateway(
            gateway=gateway,
        )
        if pending_choice_prompt is not None and choice_resolution is None:
            response_mode_hint = None
        concern_relation = self._concern_relation_for_gateway(
            gateway=gateway,
        )
        latest_turn_role = self._latest_turn_role_for_gateway(
            gateway=gateway,
        )
        pending_choice_trace_notes = self._pending_choice_trace_notes(
            pending_choice_prompt=pending_choice_prompt,
            choice_resolution=choice_resolution,
            response_mode_hint=response_mode_hint,
        )

        if not gateway.extraction_required:
            choice_prompt_action = _choice_prompt_action_for_gateway(
                pending_choice_prompt=pending_choice_prompt,
                choice_resolution=choice_resolution,
                gateway=gateway,
                recommendation_requested=recommendation_requested,
            )
            return EntryDecision(
                extraction_required=False,
                recommendation_requested=recommendation_requested,
                response_mode_hint=response_mode_hint,
                clear_pending_choice_prompt=choice_prompt_action is not None,
                choice_prompt_action=choice_prompt_action,
                message_role=gateway.message_role,
                call2_profile=gateway.profile,
                additional_medical_information=gateway.additional_medical_information,
                person_reference_present=gateway.person_reference_present,
                multi_person_context=gateway.multi_person_context,
                subject_relation_unclear=gateway.subject_relation_unclear,
                concern_relation=concern_relation,
                latest_turn_role=latest_turn_role,
                call2_tasks=list(gateway.call2_tasks),
                call2_operation_mode=call2_operation_mode,
                trace_notes=[
                    f"intent_gateway:{gateway.category}",
                    f"message_role:{gateway.message_role}",
                    f"profile:{gateway.profile}",
                    *choice_prompt_trace_notes,
                    *pending_choice_trace_notes,
                    *(
                        [
                            "choice_prompt:"
                            f"recommendation_choice:{choice_prompt_action}"
                        ]
                        if choice_prompt_action is not None and choice_resolution is None
                        else []
                    ),
                    f"next_step:{gateway.next_step or 'none'}",
                    f"recommendation_requested:{recommendation_requested}",
                    f"call2_mode:{call2_operation_mode}",
                    f"call2_tasks:{','.join(gateway.call2_tasks) if gateway.call2_tasks else 'none'}",
                    *gateway.trace_notes,
                ],
            )

        return EntryDecision(
            extraction_required=True,
            recommendation_requested=recommendation_requested,
            clear_pending_choice_prompt=pending_choice_prompt is not None,
            choice_prompt_action=(
                "report_more_information"
                if (
                    choice_resolution is not None
                    and choice_resolution.action == "report_more_information"
                )
                else None
            ),
            message_role=gateway.message_role,
            call2_profile=gateway.profile,
            additional_medical_information=gateway.additional_medical_information,
            person_reference_present=gateway.person_reference_present,
            multi_person_context=gateway.multi_person_context,
            subject_relation_unclear=gateway.subject_relation_unclear,
            concern_relation=concern_relation,
            latest_turn_role=latest_turn_role,
            call2_tasks=list(gateway.call2_tasks),
            call2_operation_mode=call2_operation_mode,
            trace_notes=[
                f"intent_gateway:{gateway.category}",
                f"message_role:{gateway.message_role}",
                f"profile:{gateway.profile}",
                *choice_prompt_trace_notes,
                *pending_choice_trace_notes,
                f"next_step:{gateway.next_step or 'none'}",
                f"recommendation_requested:{recommendation_requested}",
                f"call2_mode:{call2_operation_mode}",
                f"call2_tasks:{','.join(gateway.call2_tasks) if gateway.call2_tasks else 'none'}",
                *gateway.trace_notes,
            ],
        )

    @staticmethod
    def _response_mode_hint_for_gateway(
        *,
        gateway,
    ) -> str | None:
        if gateway.is_medical:
            return None
        return "out_of_scope"

    @staticmethod
    def _pending_choice_trace_notes(
        *,
        pending_choice_prompt,
        choice_resolution,
        response_mode_hint: str | None,
    ) -> list[str]:
        if pending_choice_prompt is None:
            return []
        if pending_choice_prompt.kind != "recommendation_choice":
            return []
        if choice_resolution is not None:
            return [
                "pending_choice_prompt:recommendation_choice",
                f"choice_prompt:recommendation_choice:{choice_resolution.action}",
            ]
        if response_mode_hint is None:
            return [
                "pending_choice_prompt:recommendation_choice",
                "choice_prompt:recommendation_choice:awaiting_resolved_reply",
            ]
        return []

    @staticmethod
    def _concern_relation_for_gateway(
        *,
        gateway,
    ) -> str:
        if not gateway.is_medical:
            return "dialogue_only"
        if gateway.message_role == "topic_shift":
            return "possible_shift"
        return "same_concern"

    @staticmethod
    def _latest_turn_role_for_gateway(
        *,
        gateway,
    ) -> str:
        if gateway.message_role == "answer_to_followup":
            return "medical_clarification"
        if gateway.contains_medical_update:
            return "medical_progress"
        if not gateway.is_medical:
            return "dialogue_response"
        return "unclear"


def _choice_prompt_action_for_gateway(
    *,
    pending_choice_prompt,
    choice_resolution,
    gateway,
    recommendation_requested: bool,
) -> str | None:
    if pending_choice_prompt is None:
        return None
    if pending_choice_prompt.kind != "recommendation_choice":
        return None
    if choice_resolution is not None:
        return choice_resolution.action
    if recommendation_requested:
        return "request_recommendation"
    if gateway.extraction_required:
        return "report_more_information"
    return None
