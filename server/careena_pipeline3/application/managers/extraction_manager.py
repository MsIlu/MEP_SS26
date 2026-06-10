from careena_pipeline3.application.services import (
    ExtractionResultMapper,
    ExtractionService,
    NoOpExtractionService,
)
from careena_pipeline3.models.turn import (
    EntryDecision,
    ExtractionPayload,
    TurnContext,
    TurnInput,
)


class ExtractionManager:
    """
    Produces transitional extraction outputs for the turn orchestrator.

    The manager may still carry a transitional truth-update bridge, but it
    should expose neighboring orchestration signals directly instead of
    hiding them inside that bridge contract.
    """

    def __init__(
        self,
        *,
        extraction_service: ExtractionService | None = None,
        extraction_result_mapper: ExtractionResultMapper | None = None,
    ):
        self.extraction_service = extraction_service or NoOpExtractionService()
        self.extraction_result_mapper = extraction_result_mapper or ExtractionResultMapper()

    def extract(
        self,
        *,
        turn_input: TurnInput,
        entry_decision: EntryDecision,
        context: TurnContext,
    ) -> ExtractionPayload:
        if not entry_decision.extraction_required:
            return ExtractionPayload(trace_notes=["extraction_skipped"])

        extraction_result = self.extraction_service.extract(
            turn_input.message,
            existing_case=context.medical_case,
            dialogue_state=context.dialogue_state,
            pending_slot=(
                context.pending_followup.slot
                if (
                    context.pending_followup is not None
                    and context.pending_followup.kind == "requirement"
                )
                else None
            ),
            call2_tasks=entry_decision.call2_tasks,
            operation_mode=entry_decision.call2_operation_mode,
            conversation_messages=turn_input.conversation_messages,
        )
        case_update_bridge = self.extraction_result_mapper.to_case_update_bridge(
            extraction_result,
            message_role=entry_decision.message_role,
            possible_new_topic=(entry_decision.message_role == "topic_shift"),
        )
        active_modules = list(entry_decision.active_modules)
        for module in self.extraction_result_mapper.active_modules(extraction_result):
            if module not in active_modules:
                active_modules.append(module)

        return ExtractionPayload(
            active_modules=active_modules,
            trace_notes=["extraction_manager_completed", *extraction_result.trace_notes],
            extraction_result=extraction_result,
            case_update_bridge=case_update_bridge,
        )
