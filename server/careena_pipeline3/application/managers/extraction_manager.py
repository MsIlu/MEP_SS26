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
    """Produces extraction payloads when the entry decision requires it."""

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
        message_delta = self.extraction_result_mapper.to_message_delta(
            extraction_result,
            message_role=entry_decision.message_role,
            possible_new_topic=(entry_decision.message_role == "topic_shift"),
        )
        active_modules = list(entry_decision.active_modules)
        for module in message_delta.requirement_signals.active_modules:
            if module not in active_modules:
                active_modules.append(module)

        return ExtractionPayload(
            active_modules=active_modules,
            trace_notes=["extraction_manager_completed", *extraction_result.trace_notes],
            extraction_result=extraction_result,
            message_delta=message_delta,
        )
