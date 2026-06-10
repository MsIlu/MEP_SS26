import json

from careena_pipeline3.core.engine import ExtractionEngine
from careena_pipeline3.server_log.logging import log_json
from careena_pipeline3.models.common import Call2OperationMode, Call2Task
from careena_pipeline3.llm.call_control import CASE_UPDATE_CALL, CallModelConfig
from careena_pipeline3.llm.context import build_case_extraction_input
from careena_pipeline3.llm.prompts.case_extraction import (
    build_case_extraction_system_prompt,
)
from careena_pipeline3.models.domain import DialogueState, MedicalCase
from careena_pipeline3.models.extraction import Call2ExtractionResult, ExtractionResult


class LLMCaseExtractionExtractor:
    """
    Primary Call 2 for conservative fact extraction.

    The LLM now emits a smaller Call-2 contract that is adapted back into the
    current transitional `ExtractionResult` for the rest of the pipeline.
    """

    def __init__(
        self,
        engine: ExtractionEngine,
        call_models: CallModelConfig | None = None,
    ):
        self.engine = engine
        self.call_models = call_models

    def extract(
        self,
        text: str,
        *,
        existing_case: MedicalCase | None = None,
        dialogue_state: DialogueState | None = None,
        pending_slot: str | None = None,
        profile: str | None = None,
        call2_tasks: list[Call2Task] | None = None,
        operation_mode: Call2OperationMode | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> ExtractionResult:
        system_prompt = build_case_extraction_system_prompt(
            call2_tasks,
            operation_mode=operation_mode,
        )
        payload = build_case_extraction_input(
            latest_user_message=text,
            existing_case=existing_case,
            dialogue_state=dialogue_state,
            pending_slot=pending_slot,
            profile=profile,
            call2_tasks=call2_tasks,
            operation_mode=operation_mode,
            messages=conversation_messages,
        )
        log_json(
            "CASE EXTRACTION CONTEXT",
            {
                "pending_slot": pending_slot,
                "profile": profile,
                "operation_mode": operation_mode,
                "call2_tasks": list(call2_tasks or []),
                # absichtlich auskommentiert 
                #"system_prompt": system_prompt,
                "payload": payload,
            },
        )
        call2_result = self.engine.extract(
            text=json.dumps(payload, ensure_ascii=False),
            system_prompt=system_prompt,
            output_schema=Call2ExtractionResult,
            max_tokens=900,
            model=(
                self.call_models.model_for(CASE_UPDATE_CALL)
                if self.call_models is not None
                else None
            ),
        )
        return call2_result.to_extraction_result(raw_text=text)
