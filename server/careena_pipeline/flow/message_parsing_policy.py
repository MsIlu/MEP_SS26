from careena_pipeline.flow.message_resolution import MessageResolutionResult
from careena_pipeline.flow.outcomes import MessageParsingOutcome
from careena_pipeline.models import DialogueState, SafetyResult


class MessageParsingPolicy:
    """
    Maps parsing-stage signals to an early `MessageParsingOutcome` when the
    message should stop before merge and planning.
    """

    def outcome_from_raw_safety(
        self,
        *,
        raw_safety: SafetyResult,
        dialogue_state: DialogueState,
    ) -> MessageParsingOutcome | None:
        if not raw_safety.red_flag_detected:
            return None
        return MessageParsingOutcome(
            raw_safety=raw_safety,
            dialogue_state=dialogue_state,
            early_response_mode="emergency",
        )

    def outcome_from_resolution(
        self,
        *,
        raw_safety: SafetyResult,
        dialogue_state: DialogueState,
        resolution: MessageResolutionResult,
    ) -> MessageParsingOutcome | None:
        message_update = resolution.message_update

        if resolution.early_response_mode is not None:
            return self._build_outcome(
                raw_safety=raw_safety,
                dialogue_state=dialogue_state,
                resolution=resolution,
                message_update=message_update,
                early_response_mode=resolution.early_response_mode,
            )

        if message_update is None:
            return self._build_outcome(
                raw_safety=raw_safety,
                dialogue_state=dialogue_state,
                resolution=resolution,
                early_response_mode="cannot_assess",
            )

        if not message_update.is_medical:
            return self._build_outcome(
                raw_safety=raw_safety,
                dialogue_state=dialogue_state,
                resolution=resolution,
                message_update=message_update,
                early_response_mode="out_of_scope",
            )

        if not message_update.extraction_required:
            return self._build_outcome(
                raw_safety=raw_safety,
                dialogue_state=dialogue_state,
                resolution=resolution,
                message_update=message_update,
                early_response_mode="cannot_assess",
            )

        return None

    @staticmethod
    def _build_outcome(
        *,
        raw_safety: SafetyResult,
        dialogue_state: DialogueState,
        resolution: MessageResolutionResult,
        early_response_mode: str,
        message_update=None,
    ) -> MessageParsingOutcome:
        return MessageParsingOutcome(
            raw_safety=raw_safety,
            dialogue_state=dialogue_state,
            message_update=message_update,
            request_recommendation=resolution.request_recommendation,
            force_deterministic_gate=resolution.force_deterministic_gate,
            early_response_mode=early_response_mode,
        )
