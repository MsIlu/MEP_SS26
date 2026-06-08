import json

from careena_pipeline3.core.engine import ExtractionEngine
from careena_pipeline3.server_log.logging import log_json
from careena_pipeline3.llm.call_control import CASE_NORMALIZATION_CALL, CallModelConfig
from careena_pipeline3.llm.context import build_extraction_normalization_input
from careena_pipeline3.llm.prompts.extraction_normalization import (
    EXTRACTION_NORMALIZATION_PROMPT,
)
from careena_pipeline3.models.common import Call2OperationMode, Call2Task
from careena_pipeline3.models.domain import DialogueState, MedicalCase
from careena_pipeline3.models.extraction import ExtractionResult


class LLMExtractionResultNormalizer:
    """Post-processes Call-2 output into the currently allowed turn contract."""

    def __init__(
        self,
        engine: ExtractionEngine,
        call_models: CallModelConfig | None = None,
    ):
        self.engine = engine
        self.call_models = call_models

    def normalize(
        self,
        result: ExtractionResult,
        *,
        text: str,
        existing_case: MedicalCase | None = None,
        dialogue_state: DialogueState | None = None,
        pending_slot: str | None = None,
        call2_tasks: list[Call2Task] | None = None,
        operation_mode: Call2OperationMode | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> ExtractionResult:
        payload = build_extraction_normalization_input(
            latest_user_message=text,
            extraction_result=result,
            existing_case=existing_case,
            dialogue_state=dialogue_state,
            pending_slot=pending_slot,
            call2_tasks=call2_tasks,
            operation_mode=operation_mode,
            messages=conversation_messages,
        )
        log_json(
            "CASE EXTRACTION NORMALIZATION CONTEXT",
            {
                "operation_mode": operation_mode,
                "pending_slot": pending_slot,
                "payload": payload,
            },
        )
        return self.engine.extract(
            text=json.dumps(payload, ensure_ascii=False),
            system_prompt=EXTRACTION_NORMALIZATION_PROMPT,
            output_schema=ExtractionResult,
            max_tokens=900,
            model=(
                self.call_models.model_for(CASE_NORMALIZATION_CALL)
                if self.call_models is not None
                else None
            ),
        )
