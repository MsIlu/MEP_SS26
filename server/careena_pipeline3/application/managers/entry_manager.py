from careena_pipeline3.application.services.call2_operation_mode_service import (
    Call2OperationModeService,
)
from careena_pipeline3.application.services.intent_classification_service import (
    IntentClassificationService,
)
from careena_pipeline3.application.services.recommendation_request_service import (
    RecommendationRequestService,
)
from careena_pipeline3.application.services.recommendation_transition_service import (
    RecommendationTransitionService,
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
    - optional legacy transition-normalization result for an inactive
      recommendation-ready hook

    Output contract:
    - small entry-stage steering signals for extraction, person context,
      recommendation-request intent, and legacy transition observability

    Does not decide:
    - case truth
    - merge semantics
    - recommendation readiness

    Legacy:
    - may still carry recommendation-transition support fields, but these are
      not part of active primary pre-recommend next-step routing.
    """

    def __init__(
        self,
        *,
        call2_operation_mode_service: Call2OperationModeService | None = None,
        intent_classification: IntentClassificationService | None = None,
        recommendation_request_service: RecommendationRequestService | None = None,
        recommendation_transition_service: RecommendationTransitionService | None = None,
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
        self.recommendation_transition_service = (
            recommendation_transition_service or RecommendationTransitionService()
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

        pending_dialogue_transition = (
            context.dialogue_state.pending_dialogue_transition
            if context is not None
            else None
        )
        transition_resolution = self.recommendation_transition_service.resolve(
            text=message,
            pending_transition=pending_dialogue_transition,
            conversation_messages=turn_input.conversation_messages,
        )
        if transition_resolution is not None and transition_resolution.action == "request_recommendation":
            return EntryDecision(
                extraction_required=False,
                recommendation_requested=True,
                clear_pending_dialogue_transition=True,
                dialogue_transition_action="request_recommendation",
                concern_relation="dialogue_only",
                latest_turn_role="closing_choice",
                trace_notes=[
                    "legacy_transition_resolution_observed",
                    "legacy_transition_hook_present:recommendation_ready_check",
                    "dialogue_transition:recommendation_ready_check:request_recommendation",
                    *transition_resolution.trace_notes,
                ],
            )
        if (
            transition_resolution is not None
            and transition_resolution.action == "report_more_information"
            and message == "report_more_information"
        ):
            return EntryDecision(
                extraction_required=False,
                recommendation_requested=False,
                clear_pending_dialogue_transition=True,
                dialogue_transition_action="report_more_information",
                concern_relation="same_concern",
                latest_turn_role="closing_choice",
                trace_notes=[
                    "legacy_transition_resolution_observed",
                    "legacy_transition_hook_present:recommendation_ready_check",
                    "dialogue_transition:recommendation_ready_check:report_more_information",
                    *transition_resolution.trace_notes,
                ],
            )
        legacy_transition_trace_notes: list[str] = []
        if transition_resolution is not None:
            legacy_transition_trace_notes = [
                "legacy_transition_resolution_observed",
                f"dialogue_transition:recommendation_ready_check:{transition_resolution.action}",
                *transition_resolution.trace_notes,
            ]

        gateway = self.intent_classification.classify(
            text=turn_input.message,
            existing_case=(context.medical_case if context is not None else None),
            dialogue_state=(context.dialogue_state if context is not None else None),
            pending_slot=(
                context.pending_followup.slot
                if (
                    context is not None
                    and context.pending_followup is not None
                    and context.pending_followup.kind == "requirement"
                )
                else None
            ),
            conversation_messages=turn_input.conversation_messages,
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
        if pending_dialogue_transition is not None and transition_resolution is None:
            response_mode_hint = None
        concern_relation = self._concern_relation_for_gateway(
            gateway=gateway,
        )
        latest_turn_role = self._latest_turn_role_for_gateway(
            gateway=gateway,
        )
        dialogue_transition_trace_notes = self._dialogue_transition_trace_notes(
            pending_dialogue_transition=pending_dialogue_transition,
            transition_resolution=transition_resolution,
            response_mode_hint=response_mode_hint,
        )

        if not gateway.extraction_required:
            dialogue_transition_action = _dialogue_transition_action_for_gateway(
                pending_dialogue_transition=pending_dialogue_transition,
                transition_resolution=transition_resolution,
                gateway=gateway,
                recommendation_requested=recommendation_requested,
            )
            return EntryDecision(
                extraction_required=False,
                recommendation_requested=recommendation_requested,
                response_mode_hint=response_mode_hint,
                clear_pending_dialogue_transition=dialogue_transition_action is not None,
                dialogue_transition_action=dialogue_transition_action,
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
                    *legacy_transition_trace_notes,
                    *dialogue_transition_trace_notes,
                    *(
                        [
                            "dialogue_transition:"
                            f"recommendation_ready_check:{dialogue_transition_action}"
                        ]
                        if dialogue_transition_action is not None
                        and transition_resolution is None
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
            clear_pending_dialogue_transition=(
                transition_resolution is not None
                and transition_resolution.action == "report_more_information"
            ),
            dialogue_transition_action=(
                "report_more_information"
                if (
                    transition_resolution is not None
                    and transition_resolution.action == "report_more_information"
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
                *legacy_transition_trace_notes,
                *dialogue_transition_trace_notes,
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
    def _dialogue_transition_trace_notes(
        *,
        pending_dialogue_transition,
        transition_resolution,
        response_mode_hint: str | None,
    ) -> list[str]:
        if pending_dialogue_transition is None:
            return []
        if pending_dialogue_transition.kind != "recommendation_ready_check":
            return []
        if transition_resolution is not None:
            return [
                "legacy_transition_hook_present:recommendation_ready_check",
                f"dialogue_transition:recommendation_ready_check:{transition_resolution.action}",
            ]
        if response_mode_hint is None:
            return [
                "legacy_transition_hook_present:recommendation_ready_check",
                "dialogue_transition:recommendation_ready_check:awaiting_resolved_reply",
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


def _dialogue_transition_action_for_gateway(
    *,
    pending_dialogue_transition,
    transition_resolution,
    gateway,
    recommendation_requested: bool,
) -> str | None:
    if pending_dialogue_transition is None:
        return None
    if pending_dialogue_transition.kind != "recommendation_ready_check":
        return None
    if transition_resolution is not None:
        return transition_resolution.action
    if recommendation_requested:
        return "request_recommendation"
    return None
