import json

from careena_pipeline.core.engine import ExtractionEngine
from careena_pipeline.llm.call_control import (
    CallModelConfig,
    INTENT_GATEWAY_CALL,
)
from careena_pipeline.llm.context import build_case_update_context
from careena_pipeline.llm.prompts.intent_gateway import INTENT_GATEWAY_SYSTEM_PROMPT
from careena_pipeline.models import DialogueState, IntentGateway, MedicalCase
from careena_pipeline.observability import log_json


class LLMIntentGatewayExtractor:
    """
    Primary Call 1 for message-level intake.

    It classifies the latest message just enough to decide whether a deeper
    extraction call is needed and keeps that decision separate from the actual
    case-update extraction.
    """

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
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> IntentGateway:
        context = build_case_update_context(
            latest_user_message=text,
            existing_case=existing_case,
            dialogue_state=dialogue_state,
            pending_slot=pending_slot,
            messages=conversation_messages,
        )
        log_json(
            "INTENT GATEWAY CONTEXT",
            {
                "pending_slot": pending_slot,
                "has_existing_case": existing_case is not None,
                "dialogue_state_present": dialogue_state is not None,
            },
        )

        result = self.engine.extract(
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
        log_json("INTENT GATEWAY", result)
        return result
