from careena_pipeline3.application.services.call2_operation_mode_service import (
    Call2OperationModeService,
)
from careena_pipeline3.application.services.intent_classification_service import (
    IntentClassificationService,
)
from careena_pipeline3.application.services.recommendation_request_service import (
    RecommendationRequestService,
)
from careena_pipeline3.models.turn import EntryDecision, TurnContext, TurnInput


class EntryManager:
    """Classifies the incoming turn and decides whether extraction is needed."""

    def __init__(
        self,
        *,
        call2_operation_mode_service: Call2OperationModeService | None = None,
        intent_classification: IntentClassificationService | None = None,
        recommendation_request_service: RecommendationRequestService | None = None,
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
                response_mode_hint="cannot_assess",
                trace_notes=["empty_message"],
            )

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

        if not gateway.extraction_required:
            response_mode_hint = "out_of_scope" if not gateway.is_medical else None
            return EntryDecision(
                extraction_required=False,
                recommendation_requested=recommendation_requested,
                response_mode_hint=response_mode_hint,
                message_role=gateway.message_role,
                person_reference_present=gateway.signals.person_reference_present,
                multi_person_context=gateway.signals.multi_person_context,
                subject_relation_unclear=gateway.signals.subject_relation_unclear,
                call2_tasks=list(gateway.call2_tasks),
                call2_operation_mode=call2_operation_mode,
                trace_notes=[
                    f"intent_gateway:{gateway.category}",
                    f"message_role:{gateway.message_role}",
                    f"recommendation_requested:{recommendation_requested}",
                    f"call2_mode:{call2_operation_mode}",
                    f"call2_tasks:{','.join(gateway.call2_tasks) if gateway.call2_tasks else 'none'}",
                ],
            )

        return EntryDecision(
            extraction_required=True,
            recommendation_requested=recommendation_requested,
            message_role=gateway.message_role,
            person_reference_present=gateway.signals.person_reference_present,
            multi_person_context=gateway.signals.multi_person_context,
            subject_relation_unclear=gateway.signals.subject_relation_unclear,
            call2_tasks=list(gateway.call2_tasks),
            call2_operation_mode=call2_operation_mode,
            trace_notes=[
                f"intent_gateway:{gateway.category}" if gateway is not None else "entry_manager_scaffold",
                f"message_role:{gateway.message_role}",
                f"recommendation_requested:{recommendation_requested}",
                f"call2_mode:{call2_operation_mode}",
                f"call2_tasks:{','.join(gateway.call2_tasks) if gateway.call2_tasks else 'none'}",
            ],
        )
