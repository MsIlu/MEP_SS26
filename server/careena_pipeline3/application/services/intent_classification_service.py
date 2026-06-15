from careena_pipeline3.core.exceptions import (
    EmptyLLMResponseError,
    InvalidJSONError,
    SchemaValidationError,
)
from careena_pipeline3.server_log.logging import log_json
from careena_pipeline3.llm.intent_gateway_extractor import LLMIntentGatewayExtractor
from careena_pipeline3.models.domain import DialogueState, MedicalCase
from careena_pipeline3.models.workflow import IntentGateway


class IntentClassificationService:
    """Wraps Call 1 and degrades cleanly on extraction/validation failures."""

    def __init__(
        self,
        *,
        intent_gateway_extractor: LLMIntentGatewayExtractor | None,
    ):
        self.intent_gateway_extractor = intent_gateway_extractor

    def classify(
        self,
        *,
        text: str,
        existing_case: MedicalCase | None,
        dialogue_state: DialogueState | None,
        pending_slot: str | None,
        entry_history_messages: list[dict[str, str]] | None,
    ) -> IntentGateway | None:
        if self.intent_gateway_extractor is None:
            return None

        try:
            result = self.intent_gateway_extractor.classify(
                text,
                existing_case=existing_case,
                dialogue_state=dialogue_state,
                pending_slot=pending_slot,
                entry_history_messages=entry_history_messages,
            )
            log_json("INTENT GATEWAY RESULT", result)
            return result
        except (EmptyLLMResponseError, InvalidJSONError, SchemaValidationError):
            return None
