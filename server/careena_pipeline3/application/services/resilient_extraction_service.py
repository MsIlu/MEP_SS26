from __future__ import annotations

from careena_pipeline3.application.services.extraction_service import (
    ExtractionResultNormalizer,
    ExtractionService,
)
from careena_pipeline3.models.common import Call2OperationMode, Call2Task
from careena_pipeline3.core.exceptions import (
    EmptyLLMResponseError,
    InvalidJSONError,
    LLMRequestError,
    SchemaValidationError,
)
from careena_pipeline3.server_log.logging import log_json
from careena_pipeline3.models.domain import CaseObservation, DialogueState, MedicalCase
from careena_pipeline3.models.extraction import (
    ExtractedObservation,
    ExtractedSubject,
    ExtractionResult,
)

FOLLOWUP_SLOT_ATTRIBUTE_MAP: dict[str, str] = {
    "duration_or_onset": "temporality",
    "body_site": "body_site",
    "injury_context": "injury_context",
    "functional_limitation": "functional_limitation",
}


class ResilientExtractionService:
    """Wraps extraction with error handling and a contract-stable fallback."""

    def __init__(
        self,
        inner: ExtractionService,
        *,
        result_normalizer: ExtractionResultNormalizer | None = None,
    ):
        self.inner = inner
        self.result_normalizer = result_normalizer

    def extract(
        self,
        text: str,
        *,
        existing_case: MedicalCase | None = None,
        dialogue_state: DialogueState | None = None,
        pending_slot: str | None = None,
        call2_tasks: list[Call2Task] | None = None,
        operation_mode: Call2OperationMode | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> ExtractionResult:
        try:
            result = self.inner.extract(
                text,
                existing_case=existing_case,
                dialogue_state=dialogue_state,
                pending_slot=pending_slot,
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
            return ExtractionResult(
                raw_text=text,
                case_payload={
                    "unresolved_questions": [pending_slot] if pending_slot else [],
                    "extraction_notes": ["case_extraction_failed"],
                },
                trace_notes=["case_extraction_failed"],
            )

        result = self._normalize_result(
            result,
            dialogue_state=dialogue_state,
            existing_case=existing_case,
            pending_slot=pending_slot,
            call2_tasks=call2_tasks,
            operation_mode=operation_mode,
            conversation_messages=conversation_messages,
        )
        log_json("CASE EXTRACTION RESULT", result)
        return result

    def _normalize_result(
        self,
        result: ExtractionResult,
        *,
        dialogue_state: DialogueState | None = None,
        existing_case: MedicalCase | None = None,
        pending_slot: str | None = None,
        call2_tasks: list[Call2Task] | None = None,
        operation_mode: Call2OperationMode | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
    ) -> ExtractionResult:
        tasks = list(call2_tasks or [])
        if "resolve_subject_context" not in tasks:
            if self._is_empty_subject(result.case_payload.subject):
                result.case_payload.subject = None
            result.case_payload.unresolved_questions = [
                question
                for question in result.case_payload.unresolved_questions
                if question not in {"subject", "subject_age"}
            ]
        result, normalized_by_llm = self._normalize_with_llm(
            result,
            text=result.raw_text,
            existing_case=existing_case,
            dialogue_state=dialogue_state,
            pending_slot=pending_slot,
            call2_tasks=call2_tasks,
            operation_mode=operation_mode,
            conversation_messages=conversation_messages,
        )
        if not normalized_by_llm:
            self._normalize_followup_slot_update(
                result,
                existing_case=existing_case,
                pending_slot=pending_slot,
                operation_mode=operation_mode,
            )
        return result

    def _normalize_with_llm(
        self,
        result: ExtractionResult,
        *,
        text: str,
        existing_case: MedicalCase | None,
        dialogue_state: DialogueState | None,
        pending_slot: str | None,
        call2_tasks: list[Call2Task] | None,
        operation_mode: Call2OperationMode | None,
        conversation_messages: list[dict[str, str]] | None,
    ) -> tuple[ExtractionResult, bool]:
        if self.result_normalizer is None:
            return result, False
        try:
            normalized = self.result_normalizer.normalize(
                result,
                text=text,
                existing_case=existing_case,
                dialogue_state=dialogue_state,
                pending_slot=pending_slot,
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
                "CASE EXTRACTION NORMALIZATION FAILED",
                {
                    "error": str(exc),
                    "operation_mode": operation_mode,
                    "pending_slot": pending_slot,
                },
            )
            return result, False
        log_json("CASE EXTRACTION NORMALIZED RESULT", normalized)
        return normalized, True

    def _normalize_followup_slot_update(
        self,
        result: ExtractionResult,
        *,
        existing_case: MedicalCase | None,
        pending_slot: str | None,
        operation_mode: Call2OperationMode | None,
    ) -> None:
        if operation_mode != "followup_slot_update" or pending_slot is None:
            return
        if existing_case is None:
            return

        focus = existing_case.primary_observation()
        if focus is None:
            return

        update_observation = self._followup_focus_update_observation(
            result=result,
            focus=focus,
            pending_slot=pending_slot,
        )
        if update_observation is None:
            return

        result.case_payload.observations = [update_observation]
        result.case_payload.extraction_notes.append(
            f"normalized_followup_slot_update:{pending_slot}"
        )
        result.trace_notes.append(
            f"normalized_followup_slot_update:{focus.type}:{pending_slot}"
        )

    def _followup_focus_update_observation(
        self,
        *,
        result: ExtractionResult,
        focus: CaseObservation,
        pending_slot: str,
    ) -> ExtractedObservation | None:
        if not result.case_payload.observations:
            return None

        source = result.case_payload.observations[0]
        raw_text = result.raw_text.strip()
        if not raw_text:
            return None

        attributes = _followup_attributes_from_slot(
            pending_slot=pending_slot,
            source=source,
            raw_text=raw_text,
        )
        if attributes is None:
            return None

        return ExtractedObservation(
            raw_label=focus.patient_label,
            observation_type=focus.type,
            normalized_concept=focus.concept,
            negated=False,
            certainty="confirmed",
            subject_ref=focus.subject_ref or source.subject_ref,
            source_span=raw_text,
            confidence=source.confidence,
            attributes=attributes,
            signals=list(source.signals),
        )

    @staticmethod
    def _is_empty_subject(subject: ExtractedSubject | None) -> bool:
        if subject is None:
            return False
        return (
            (subject.relation is None or subject.relation == "unknown")
            and subject.age is None
            and subject.sex is None
            and not subject.signals
        )


def _followup_attributes_from_slot(
    *,
    pending_slot: str,
    source: ExtractedObservation,
    raw_text: str,
) -> dict[str, object] | None:
    if pending_slot == "severity":
        severity_value = _severity_from_source(source, fallback=raw_text)
        if severity_value is None:
            return None
        return {"severity": severity_value}

    attribute_name = FOLLOWUP_SLOT_ATTRIBUTE_MAP.get(pending_slot)
    if attribute_name is None:
        return None
    return {attribute_name: raw_text}


def _severity_from_source(
    source: ExtractedObservation,
    *,
    fallback: str,
) -> int | str | None:
    value = source.attributes.get("severity")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip():
        normalized = value.strip()
        if normalized.isdigit():
            return int(normalized)
        return normalized
    normalized_fallback = fallback.strip()
    if normalized_fallback.isdigit():
        return int(normalized_fallback)
    return normalized_fallback or None
