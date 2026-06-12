from __future__ import annotations

from typing import Protocol

from careena_pipeline3.models.common import Call2OperationMode, Call2Task
from careena_pipeline3.models.domain import DialogueState, MedicalCase
from careena_pipeline3.models.extraction import ExtractionResult


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
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> ExtractionResult: ...


class ExtractionResultNormalizer(Protocol):
    def normalize(
        self,
        result: ExtractionResult,
        *,
        text: str,
        existing_case: MedicalCase | None = None,
        dialogue_state: DialogueState | None = None,
        pending_slot: str | None = None,
        profile: str | None = None,
        call2_tasks: list[Call2Task] | None = None,
        operation_mode: Call2OperationMode | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> ExtractionResult: ...


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
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> ExtractionResult:
        return ExtractionResult(
            raw_text=text,
            case_payload={
                "extraction_notes": [
                    "no_op_extraction_service",
                ],
            },
            trace_notes=["extraction_not_configured"],
        )
