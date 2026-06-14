from __future__ import annotations

from careena_pipeline3.models.common import Call2OperationMode
from careena_pipeline3.models.turn import TurnContext
from careena_pipeline3.models.workflow import IntentGateway


class Call2OperationModeService:
    """Derives a constrained Call-2 operating mode from Call 1 and dialogue state."""

    @staticmethod
    def _requirement_followup_pending(context: TurnContext | None) -> bool:
        if context is None:
            return False
        followup = context.dialogue_state.pending_followup
        return followup is not None and followup.kind == "requirement"

    def resolve(
        self,
        *,
        gateway: IntentGateway,
        context: TurnContext | None = None,
    ) -> Call2OperationMode:
        explicit_mode = gateway.explicit_call2_operation_mode
        if explicit_mode is not None:
            return explicit_mode

        if not gateway.extraction_required or not gateway.is_medical:
            return "no_medical_update_expected"

        pending_followup = self._requirement_followup_pending(context)
        role = gateway.message_role

        if pending_followup:
            if gateway.additional_medical_information:
                return "mixed_update_and_new_info"
            if role in {"answer_to_followup", "confirmation", "correction"}:
                return "followup_slot_update"
            return "mixed_update_and_new_info"

        if role in {"confirmation", "correction"}:
            return "existing_fact_revision"

        if role in {"new_information", "topic_shift"}:
            return "focused_new_fact_extraction"

        return "focused_new_fact_extraction"
