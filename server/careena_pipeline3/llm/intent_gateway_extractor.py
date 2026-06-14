import json

from careena_pipeline3.core.engine import ExtractionEngine
from careena_pipeline3.llm.call_control import CallModelConfig, INTENT_GATEWAY_CALL
from careena_pipeline3.llm.context import build_intent_gateway_context
from careena_pipeline3.llm.prompts.intent_gateway import INTENT_GATEWAY_SYSTEM_PROMPT
from careena_pipeline3.models.domain import DialogueState, MedicalCase
from careena_pipeline3.models.workflow import IntentGateway


class LLMIntentGatewayExtractor:
    """Primary Call 1 for message-level intake."""

    def __init__(
        self,
        engine: ExtractionEngine,
        call_models: CallModelConfig | None = None,
    ):
        self.engine = engine
        self.call_models = call_models

    def classify(
        self,
        text: str,
        *,
        existing_case: MedicalCase | None = None,
        dialogue_state: DialogueState | None = None,
        pending_slot: str | None = None,
        entry_history_messages: list[dict[str, str]] | None = None,
    ) -> IntentGateway:
        context = build_intent_gateway_context(
            latest_user_message=text,
            existing_case=existing_case,
            dialogue_state=dialogue_state,
            pending_slot=pending_slot,
            history_messages=entry_history_messages,
        )
        return self.engine.extract(
            text=json.dumps(context.model_dump(), ensure_ascii=False),
            system_prompt=INTENT_GATEWAY_SYSTEM_PROMPT,
            output_schema=IntentGateway,
            max_tokens=500,
            model=(
                self.call_models.model_for(INTENT_GATEWAY_CALL)
                if self.call_models is not None
                else None
            ),
        )
