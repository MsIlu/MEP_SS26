from __future__ import annotations

from careena_pipeline3.application.services.extraction_service import (
    ExtractionResultNormalizer,
    ExtractionService,
)
from careena_pipeline3.application.services.extraction_failure_fallback_builder import (
    ExtractionFailureFallbackBuilder,
)
from careena_pipeline3.models.common import Call2OperationMode, Call2Task
from careena_pipeline3.core.exceptions import (
    EmptyLLMResponseError,
    InvalidJSONError,
    LLMRequestError,
    SchemaValidationError,
)
from careena_pipeline3.server_log.logging import log_json
from careena_pipeline3.models.domain import DialogueState, MedicalCase
from careena_pipeline3.models.extraction import Call2ExtractionResult


class ResilientExtractionService:
    """
    Orchestrates the active Call-2 runtime path.

    The service is intentionally smaller than before:
    - primary extraction
    - failure fallback
    - narrow post-processing

    It no longer owns a second broad LLM normalization pass itself.
    """

    def __init__(
        self,
        inner: ExtractionService,
        *,
        result_normalizer: ExtractionResultNormalizer | None = None,
        fallback_builder: ExtractionFailureFallbackBuilder | None = None,
    ):
        self.inner = inner
        self.result_normalizer = result_normalizer
        self.fallback_builder = fallback_builder or ExtractionFailureFallbackBuilder()

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
    ) -> Call2ExtractionResult:
        try:
            result = self.inner.extract(
                text,
                existing_case=existing_case,
                dialogue_state=dialogue_state,
                pending_slot=pending_slot,
                profile=profile,
                call2_tasks=call2_tasks,
                operation_mode=operation_mode,
                conversation_messages=conversation_messages,
            )
        except (
            EmptyLLMResponseError,
            InvalidJSONError,
            SchemaValidationError,
            LLMRequestError,
        ) as exc:
            log_json(
                "CASE EXTRACTION FAILED",
                {
                    "error": str(exc),
                    "pending_slot": pending_slot,
                    "has_existing_case": existing_case is not None,
                },
            )
            return self.fallback_builder.build(
                pending_slot=pending_slot,
            )

        result = self._post_process_result(
            result,
            text=text,
            dialogue_state=dialogue_state,
            existing_case=existing_case,
            pending_slot=pending_slot,
            profile=profile,
            call2_tasks=call2_tasks,
            operation_mode=operation_mode,
            conversation_messages=conversation_messages,
        )
        log_json("CASE EXTRACTION RESULT", result)
        return result

    def _post_process_result(
        self,
        result: Call2ExtractionResult,
        *,
        text: str,
        dialogue_state: DialogueState | None = None,
        existing_case: MedicalCase | None = None,
        pending_slot: str | None = None,
        profile: str | None = None,
        call2_tasks: list[Call2Task] | None = None,
        operation_mode: Call2OperationMode | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> Call2ExtractionResult:
        if self.result_normalizer is None:
            return result
        try:
            return self.result_normalizer.normalize(
                result,
                text=text,
                existing_case=existing_case,
                dialogue_state=dialogue_state,
                pending_slot=pending_slot,
                profile=profile,
                call2_tasks=call2_tasks,
                operation_mode=operation_mode,
                conversation_messages=conversation_messages,
            )
        except (
            EmptyLLMResponseError,
            InvalidJSONError,
            SchemaValidationError,
            LLMRequestError,
        ) as exc:
            log_json(
                "CASE EXTRACTION POSTPROCESS FAILED",
                {
                    "error": str(exc),
                    "operation_mode": operation_mode,
                    "pending_slot": pending_slot,
                },
            )
            return result
