from __future__ import annotations

from typing import Protocol

from careena_pipeline3.models.common import Call2OperationMode, Call2Task
from careena_pipeline3.models.domain import DialogueState, MedicalCase
from careena_pipeline3.models.extraction import Call2ExtractionResult


class ExtractionService(Protocol):
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
        extraction_history_messages: list[dict[str, str]] | None = None,
    ) -> Call2ExtractionResult: ...


class ExtractionResultNormalizer(Protocol):
    def normalize(
        self,
        result: Call2ExtractionResult,
        *,
        text: str,
        existing_case: MedicalCase | None = None,
        dialogue_state: DialogueState | None = None,
        pending_slot: str | None = None,
        profile: str | None = None,
        call2_tasks: list[Call2Task] | None = None,
        operation_mode: Call2OperationMode | None = None,
        extraction_history_messages: list[dict[str, str]] | None = None,
    ) -> Call2ExtractionResult: ...


class NoOpExtractionService:
    """Fallback extractor that preserves the new contract without inferring facts."""

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
        extraction_history_messages: list[dict[str, str]] | None = None,
    ) -> Call2ExtractionResult:
        return Call2ExtractionResult(
            extraction_notes=[
                "no_op_extraction_service",
            ],
            trace_notes=["extraction_not_configured"],
        )
