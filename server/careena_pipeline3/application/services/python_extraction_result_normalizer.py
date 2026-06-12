from __future__ import annotations

from careena_pipeline3.models.common import Call2OperationMode, Call2Task
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

OBSERVATION_TYPE_BY_TASK: dict[Call2Task, set[str]] = {
    "extract_symptoms": {"symptom"},
    "extract_injuries": {"injury"},
    "extract_measurements": {"measurement"},
    "extract_medications": {"medication"},
}


class PythonExtractionResultNormalizer:
    """
    Small Python-side post-processor for the current Call-2 contract.

    This intentionally replaces the previous broad second LLM pass in the
    active runtime path. Its job is to enforce a few narrow contract rules,
    not to perform a second extraction.
    """

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
    ) -> ExtractionResult:
        del text, dialogue_state, profile, conversation_messages

        normalized = result.model_copy(deep=True)
        self._normalize_subject_contract(normalized, call2_tasks=call2_tasks)
        self._prune_observations_by_tasks(normalized, call2_tasks=call2_tasks)
        self._apply_operation_mode_contract(
            normalized,
            existing_case=existing_case,
            pending_slot=pending_slot,
            operation_mode=operation_mode,
        )
        return normalized

    def _normalize_subject_contract(
        self,
        result: ExtractionResult,
        *,
        call2_tasks: list[Call2Task] | None,
    ) -> None:
        tasks = set(call2_tasks or [])
        if "resolve_subject_context" in tasks:
            return
        if self._is_empty_subject(result.case_payload.subject):
            result.case_payload.subject = None
        result.case_payload.unresolved_questions = [
            question
            for question in result.case_payload.unresolved_questions
            if question not in {"subject", "subject_age"}
        ]

    def _prune_observations_by_tasks(
        self,
        result: ExtractionResult,
        *,
        call2_tasks: list[Call2Task] | None,
    ) -> None:
        tasks = set(call2_tasks or [])
        allowed_types = set()
        for task in tasks:
            allowed_types.update(OBSERVATION_TYPE_BY_TASK.get(task, set()))
        if not allowed_types:
            result.case_payload.observations = []
            return
        result.case_payload.observations = [
            observation
            for observation in result.case_payload.observations
            if observation.observation_type in allowed_types
        ]

    def _apply_operation_mode_contract(
        self,
        result: ExtractionResult,
        *,
        existing_case: MedicalCase | None,
        pending_slot: str | None,
        operation_mode: Call2OperationMode | None,
    ) -> None:
        if operation_mode == "no_medical_update_expected":
            result.case_payload.subject = None
            result.case_payload.observations = []
            result.case_payload.unresolved_questions = []
            result.case_payload.extraction_notes.append(
                "python_normalized_no_medical_update_expected"
            )
            result.trace_notes.append("python_normalized:no_medical_update_expected")
            return

        if operation_mode == "followup_slot_update":
            self._normalize_followup_slot_update(
                result,
                existing_case=existing_case,
                pending_slot=pending_slot,
            )
            return

        if operation_mode == "mixed_update_and_new_info":
            self._normalize_mixed_update_and_new_info(
                result,
                existing_case=existing_case,
                pending_slot=pending_slot,
            )
            return

        if operation_mode == "existing_fact_revision":
            if len(result.case_payload.observations) > 1:
                result.case_payload.observations = result.case_payload.observations[:1]
                result.case_payload.extraction_notes.append(
                    "python_normalized_existing_fact_revision"
                )
                result.trace_notes.append("python_normalized:existing_fact_revision")

    def _normalize_followup_slot_update(
        self,
        result: ExtractionResult,
        *,
        existing_case: MedicalCase | None,
        pending_slot: str | None,
    ) -> None:
        if pending_slot is None or existing_case is None:
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
            f"python_normalized_followup_slot_update:{pending_slot}"
        )
        result.trace_notes.append(
            f"python_normalized_followup_slot_update:{focus.type}:{pending_slot}"
        )

    def _normalize_mixed_update_and_new_info(
        self,
        result: ExtractionResult,
        *,
        existing_case: MedicalCase | None,
        pending_slot: str | None,
    ) -> None:
        if pending_slot is None or existing_case is None:
            return

        focus = existing_case.primary_observation()
        if focus is None:
            return

        focus_source = self._observation_with_contract_role(
            result.case_payload.observations,
            role="focus_update",
        )
        if focus_source is None:
            return

        update_observation = self._followup_focus_update_observation(
            result=result,
            focus=focus,
            pending_slot=pending_slot,
            source=focus_source,
        )
        if update_observation is None:
            return

        result.case_payload.observations = [
            update_observation,
            *[
                observation
                for observation in result.case_payload.observations
                if observation is not focus_source
            ],
        ]
        result.case_payload.extraction_notes.append(
            f"python_normalized_mixed_update_and_new_info:{pending_slot}"
        )
        result.trace_notes.append(
            f"python_normalized_mixed_update_and_new_info:{focus.type}:{pending_slot}"
        )

    def _followup_focus_update_observation(
        self,
        *,
        result: ExtractionResult,
        focus: CaseObservation,
        pending_slot: str,
        source: ExtractedObservation | None = None,
    ) -> ExtractedObservation | None:
        if source is None and not result.case_payload.observations:
            return None

        source = source or result.case_payload.observations[0]
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
    def _observation_with_contract_role(
        observations: list[ExtractedObservation],
        *,
        role: str,
    ) -> ExtractedObservation | None:
        for observation in observations:
            for signal in observation.signals:
                if signal.code == "call2_contract_role" and signal.value == role:
                    return observation
        return None

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
    source_value = source.attributes.get(attribute_name)
    if isinstance(source_value, str) and source_value.strip():
        return {attribute_name: source_value.strip()}
    if source_value is not None:
        return {attribute_name: source_value}
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
