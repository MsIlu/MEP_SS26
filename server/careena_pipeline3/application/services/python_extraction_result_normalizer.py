from __future__ import annotations

from careena_pipeline3.models.common import Call2OperationMode, Call2Task
from careena_pipeline3.models.domain import CaseObservation, DialogueState, MedicalCase
from careena_pipeline3.models.extraction import (
    Call2CaseExtensionStatus,
    Call2ExtractionResult,
    ExtractedObservation,
    ExtractedSubject,
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
    ) -> Call2ExtractionResult:
        del dialogue_state, profile, extraction_history_messages

        normalized = result.model_copy(deep=True)
        self._normalize_subject_contract(normalized, call2_tasks=call2_tasks)
        self._prune_observations_by_tasks(normalized, call2_tasks=call2_tasks)
        self._apply_operation_mode_contract(
            normalized,
            text=text,
            existing_case=existing_case,
            pending_slot=pending_slot,
            operation_mode=operation_mode,
        )
        self._normalize_case_topic_contract(normalized)
        normalized.case_extension_status = self._normalized_case_extension_status(
            normalized,
            operation_mode=operation_mode,
        )
        normalized.trace_notes.append(
            "python_normalized:case_extension_status:"
            f"{normalized.case_extension_status}"
        )
        return normalized

    def _normalize_subject_contract(
        self,
        result: Call2ExtractionResult,
        *,
        call2_tasks: list[Call2Task] | None,
    ) -> None:
        tasks = set(call2_tasks or [])
        if "resolve_subject_context" in tasks:
            return
        if self._is_empty_subject(result.subject_update):
            result.subject_update = None
        result.open_questions = [
            question
            for question in result.open_questions
            if question not in {"subject", "subject_age"}
        ]

    @staticmethod
    def _normalize_case_topic_contract(result: Call2ExtractionResult) -> None:
        if result.case_frame_label is None:
            return
        normalized = result.case_frame_label.strip()
        if not normalized or not result.all_observations():
            result.case_frame_label = None
            return
        result.case_frame_label = normalized

    def _prune_observations_by_tasks(
        self,
        result: Call2ExtractionResult,
        *,
        call2_tasks: list[Call2Task] | None,
    ) -> None:
        tasks = set(call2_tasks or [])
        allowed_types = set()
        for task in tasks:
            allowed_types.update(OBSERVATION_TYPE_BY_TASK.get(task, set()))
        if not allowed_types:
            result.focus_update = None
            result.new_items = []
            return
        if (
            result.focus_update is not None
            and result.focus_update.observation_type not in allowed_types
        ):
            result.focus_update = None
        result.new_items = [
            observation
            for observation in result.new_items
            if observation.observation_type in allowed_types
        ]

    def _apply_operation_mode_contract(
        self,
        result: Call2ExtractionResult,
        *,
        text: str,
        existing_case: MedicalCase | None,
        pending_slot: str | None,
        operation_mode: Call2OperationMode | None,
    ) -> None:
        if operation_mode == "no_medical_update_expected":
            result.subject_update = None
            result.case_frame_label = None
            result.focus_update = None
            result.new_items = []
            result.open_questions = []
            result.extraction_notes.append(
                "python_normalized_no_medical_update_expected"
            )
            result.trace_notes.append("python_normalized:no_medical_update_expected")
            return

        if operation_mode == "followup_slot_update":
            # Legacy requirement followup path; active requirement followups
            # no longer repair Call-2 output via pending-slot normalization.
            result.trace_notes.append("legacy_followup_slot_update_inactive")
            return

        if operation_mode == "mixed_update_and_new_info":
            # Legacy requirement followup path; active requirement followups
            # no longer repair Call-2 output via pending-slot normalization.
            result.trace_notes.append("legacy_mixed_update_and_new_info_inactive")
            return

        if operation_mode == "existing_fact_revision":
            if result.focus_update is None and result.new_items:
                result.focus_update = result.new_items[0]
                result.new_items = result.new_items[1:]
            if result.new_items:
                result.new_items = []
                result.extraction_notes.append(
                    "python_normalized_existing_fact_revision"
                )
                result.trace_notes.append("python_normalized:existing_fact_revision")

    def _normalized_case_extension_status(
        self,
        result: Call2ExtractionResult,
        *,
        operation_mode: Call2OperationMode | None,
    ) -> Call2CaseExtensionStatus:
        if not result.all_observations():
            if self._has_write_relevant_subject(result.subject_update):
                if operation_mode == "existing_fact_revision":
                    return "updates_existing_information"
                return "adds_new_information"
            return "no_relevant_change"

        focus_update_present = result.focus_update is not None
        new_item_present = bool(result.new_items)

        if focus_update_present and new_item_present:
            return "mixed_update_and_new"
        if new_item_present:
            return "adds_new_information"
        if focus_update_present:
            return "updates_existing_information"

        if operation_mode == "existing_fact_revision":
            return "updates_existing_information"
        return "no_relevant_change"

    def _normalize_followup_slot_update(
        self,
        result: Call2ExtractionResult,
        *,
        text: str,
        existing_case: MedicalCase | None,
        pending_slot: str | None,
    ) -> None:
        # Legacy requirement followup path; kept temporarily as reference while
        # the general Call-2 followup modes are being retired.
        if pending_slot is None or existing_case is None:
            return

        focus = existing_case.primary_observation()
        if focus is None:
            return

        update_observation = self._followup_focus_update_observation(
            result=result,
            raw_text=text,
            focus=focus,
            pending_slot=pending_slot,
        )
        if update_observation is None:
            return

        result.focus_update = update_observation
        result.new_items = []
        result.extraction_notes.append(
            f"python_normalized_followup_slot_update:{pending_slot}"
        )
        result.trace_notes.append(
            f"python_normalized_followup_slot_update:{focus.type}:{pending_slot}"
        )

    def _normalize_mixed_update_and_new_info(
        self,
        result: Call2ExtractionResult,
        *,
        text: str,
        existing_case: MedicalCase | None,
        pending_slot: str | None,
    ) -> None:
        # Legacy requirement followup path; kept temporarily as reference while
        # the general Call-2 followup modes are being retired.
        if pending_slot is None or existing_case is None:
            return

        focus = existing_case.primary_observation()
        if focus is None:
            return

        focus_source = result.focus_update
        if focus_source is None:
            return

        update_observation = self._followup_focus_update_observation(
            result=result,
            raw_text=text,
            focus=focus,
            pending_slot=pending_slot,
            source=focus_source,
        )
        if update_observation is None:
            return

        result.focus_update = update_observation
        result.new_items = [
            observation
            for observation in result.new_items
            if observation is not focus_source
        ]
        result.extraction_notes.append(
            f"python_normalized_mixed_update_and_new_info:{pending_slot}"
        )
        result.trace_notes.append(
            f"python_normalized_mixed_update_and_new_info:{focus.type}:{pending_slot}"
        )

    def _followup_focus_update_observation(
        self,
        *,
        result: Call2ExtractionResult,
        raw_text: str,
        focus: CaseObservation,
        pending_slot: str,
        source: ExtractedObservation | None = None,
    ) -> ExtractedObservation | None:
        if source is None and result.focus_update is None and not result.new_items:
            return None

        source = source or result.focus_update or result.new_items[0]
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

    @classmethod
    def _has_write_relevant_subject(cls, subject: ExtractedSubject | None) -> bool:
        if subject is None:
            return False
        return not cls._is_empty_subject(subject)


def _followup_attributes_from_slot(
    *,
    pending_slot: str,
    source: ExtractedObservation,
    raw_text: str,
) -> dict[str, object] | None:
    # Legacy requirement followup helper; active requirement followups now
    # resolve through their dedicated resolver instead of Call-2 repair.
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
