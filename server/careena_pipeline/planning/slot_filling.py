import re
from typing import TYPE_CHECKING

from careena_pipeline.planning.subject_detection import SubjectDetector
from careena_pipeline.models import MedicalCase
from careena_pipeline.pipeline_rules import (
    looks_like_question,
    normalize_text,
)

if TYPE_CHECKING:
    from careena_pipeline.planning.requirement_state import PendingFollowupContext


class SlotFillResult:
    def __init__(self, filled: bool, slot: str | None = None):
        self.filled = filled
        self.slot = slot


class SlotFiller:
    """
    Handles short follow-up answers when Careena already knows what it asked.

    This keeps answers like "seit vorhin" or "8 von 10" out of the full
    understanding LLM path.
    """

    def __init__(self, subject_detector: SubjectDetector | None = None):
        self.subject_detector = subject_detector or SubjectDetector()

    def fill(
        self,
        case: MedicalCase,
        pending_followup: "PendingFollowupContext",
        text: str,
    ) -> SlotFillResult:
        case.ensure_primary_problem()
        pending_slot = pending_followup.normalized_slot
        if pending_slot is None:
            return SlotFillResult(False)

        normalized = text.strip()
        if not normalized:
            return SlotFillResult(False, pending_slot)
        if looks_like_question(normalized):
            return SlotFillResult(False, pending_slot)

        if pending_slot == "subject":
            subject = self.subject_detector.detect(normalized)
            if subject.relation == "unknown":
                return SlotFillResult(False, pending_slot)
            subject.confirmed = True
            age = self._extract_age(normalized)
            if age is not None:
                subject.age = age
            case.subject = subject
            return SlotFillResult(True, pending_slot)

        if pending_slot == "subject_age":
            age = self._extract_age(normalized)
            if age is None:
                return SlotFillResult(False, pending_slot)
            case.subject.age = age
            return SlotFillResult(True, pending_slot)

        if pending_slot == "duration_or_onset":
            if not _looks_like_temporality(normalized):
                return SlotFillResult(False, pending_slot)
            self._apply_temporality(
                case,
                normalized,
                module=(
                    pending_followup.resolved_field.module
                    if pending_followup.resolved_field is not None
                    else None
                ),
            )
            return SlotFillResult(True, pending_slot)

        if pending_slot == "injury_context":
            if not _contains_context_marker(normalized):
                return SlotFillResult(False, pending_slot)
            self._apply_detail(case, "context", normalized)
            return SlotFillResult(True, pending_slot)

        if pending_slot == "functional_limitation":
            if not _looks_like_functional_limitation(normalized):
                return SlotFillResult(False, pending_slot)
            self._apply_detail(case, "functional_limitation", normalized)
            return SlotFillResult(True, pending_slot)

        if pending_slot == "severity":
            severity = self._extract_severity(normalized)
            if severity is None:
                return SlotFillResult(False, pending_slot)
            self._apply_severity(case, severity)
            return SlotFillResult(True, pending_slot)

        return SlotFillResult(False, pending_slot)

    @staticmethod
    def _apply_temporality(
        case: MedicalCase,
        value: str,
        *,
        module: str | None,
    ) -> None:
        for observation in _target_observations(case, module=module):
            if _can_replace_temporality(observation.temporality, value):
                observation.set_surface_field("temporality", value)

    @staticmethod
    def _apply_detail(case: MedicalCase, key: str, value: str) -> None:
        observations = _focused_observations(case)
        if key == "context":
            observations = _focused_injuries(case) or case.observations_of_type("injury")
        elif key == "functional_limitation":
            observations = (
                _focused_injuries(case)
                or _focused_observations(case)
                or case.observations_of_type("injury")
                or case.observations_of_type("symptom")
            )

        for observation in observations:
            if observation.type in {"injury", "symptom"} and key not in observation.details:
                observation.set_detail_value(key, value)

    @staticmethod
    def _extract_severity(text: str) -> int | None:
        match = re.search(r"\b(10|[0-9])\b", text)
        if match:
            return int(match.group(1))

        lowered = normalize_text(text)
        for word, value in {
            "leicht": 2,
            "mittel": 5,
            "maessig": 5,
            "stark": 8,
            "schwer": 8,
            "sehr stark": 9,
            "unertraeglich": 10,
        }.items():
            if word in lowered:
                return value
        return None

    @staticmethod
    def _extract_age(text: str) -> int | None:
        match = re.search(r"\b(1[01][0-9]|120|[1-9][0-9]?)\b", text)
        if not match:
            return None
        return int(match.group(1))

    @staticmethod
    def _apply_severity(case: MedicalCase, value: int) -> None:
        for observation in _focused_observations(case):
            if observation.severity is None:
                observation.set_surface_field("severity", value)


def _focused_observations(case: MedicalCase):
    focus = case.primary_focus_label()
    focus_id = case.primary_problem_id
    candidates = case.observations_of_type(
        "symptom",
        "injury",
        "measurement",
        "concern",
        include_negated=True,
    )

    if focus_id:
        focused = [observation for observation in candidates if observation.id == focus_id]
        if focused:
            return focused

    if focus:
        focused = [
            observation
            for observation in candidates
            if _matches_focus(observation, focus)
        ]
        if focused:
            return focused

    return candidates


def _focused_injuries(case: MedicalCase):
    focus = case.primary_focus_label()
    focus_id = case.primary_problem_id
    injuries = case.observations_of_type("injury", include_negated=True)
    if not focus:
        return injuries

    if focus_id:
        focused = [observation for observation in injuries if observation.id == focus_id]
        if focused:
            return focused

    return [
        observation
        for observation in injuries
        if _matches_focus(observation, focus)
    ]


def _target_observations(case: MedicalCase, *, module: str | None):
    if module == "injury":
        return _focused_injuries(case) or case.observations_of_type(
            "injury",
            include_negated=True,
        )
    if module == "symptom":
        symptoms = case.observations_of_type("symptom", include_negated=True)
        focus = case.primary_focus_label()
        focus_id = case.primary_problem_id
        if focus_id:
            focused = [
                observation
                for observation in symptoms
                if observation.id == focus_id
            ]
            if focused:
                return focused
        if focus:
            focused = [
                observation
                for observation in symptoms
                if _matches_focus(observation, focus)
            ]
            if focused:
                return focused
        return symptoms
    return _focused_observations(case)


def _matches_focus(observation, focus: str) -> bool:
    normalized_focus = normalize_text(focus)
    return normalized_focus in {
        normalize_text(observation.label),
        normalize_text(observation.patient_label),
        normalize_text(observation.concept or ""),
    }


def _contains_context_marker(text: str) -> bool:
    normalized = normalize_text(text)
    return any(
        marker in normalized
        for marker in (
            "sturz",
            "unfall",
            "gesturzt",
            "gestuerzt",
            "gefallen",
            "angestossen",
            "gestossen",
            "fahrrad",
            "treppe",
            "sport",
            "schlag",
            "aufprall",
        )
    )


def _looks_like_temporality(text: str) -> bool:
    normalized = normalize_text(text)
    return any(
        marker in normalized
        for marker in (
            "seit",
            "heute",
            "gestern",
            "vorhin",
            "eben",
            "stunde",
            "stunden",
            "tag",
            "tage",
            "woche",
            "wochen",
            "minute",
            "minuten",
        )
    ) or bool(re.search(r"\b\d+\s*(stunde|stunden|tag|tage|woche|wochen|minute|minuten)\b", normalized))


def _looks_like_functional_limitation(text: str) -> bool:
    normalized = normalize_text(text)
    return any(
        marker in normalized
        for marker in (
            "auftreten",
            "stehen",
            "gehen",
            "laufen",
            "belasten",
            "kaum",
            "nicht",
            "normal",
        )
    ) or len(normalized.split()) >= 2


def _can_replace_temporality(current: str | None, incoming: str) -> bool:
    if not incoming:
        return False
    if current is None:
        return True

    normalized_current = normalize_text(current)
    normalized_incoming = normalize_text(incoming)
    if normalized_current == normalized_incoming:
        return False

    # Replace vague extraction placeholders with concrete user-provided timing.
    if normalized_current in {"just now", "eben", "gerade", "aktuell", "now"}:
        return True

    return False
