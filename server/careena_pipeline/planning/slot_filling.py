import re
from typing import TYPE_CHECKING

from careena_pipeline.models import MedicalCase, StagedFollowupAnswer
from careena_pipeline.pipeline_rules import looks_like_question

if TYPE_CHECKING:
    from careena_pipeline.planning.requirement_state import PendingFollowupContext


class SlotFillResult:
    def __init__(
        self,
        filled: bool,
        slot: str | None = None,
        *,
        staged_answers: list[StagedFollowupAnswer] | None = None,
    ):
        self.filled = filled
        self.slot = slot
        self.staged_answers = list(staged_answers or [])


class SlotFiller:
    """
    Minimal slot filling for a very small set of deterministic follow-ups.

    Slot filling is intentionally not a general extraction path.
    It should only answer narrowly defined standard follow-ups without using
    the LLM. Everything else must fall back to the normal extraction path.

    Current active scope:
    - `severity`
    - `duration_or_onset`
    """

    FIELD_SPECS = {
        "duration_or_onset": {
            "extractor": "_extract_duration_or_onset",
        },
        "severity": {
            "extractor": "_extract_severity",
        },
    }

    def fill(
        self,
        case: MedicalCase,
        pending_followup: "PendingFollowupContext",
        text: str,
    ) -> SlotFillResult:
        case.ensure_primary_problem()
        pending_slot = pending_followup.normalized_slot
        spec = self.FIELD_SPECS.get(pending_slot)
        if spec is None:
            return SlotFillResult(False, pending_slot)

        raw_text = text.strip()
        if not raw_text or looks_like_question(raw_text):
            return SlotFillResult(False, pending_slot)

        extractor = getattr(self, spec["extractor"])
        value = extractor(raw_text)
        if value is None:
            return SlotFillResult(False, pending_slot)

        staged_answers = _build_staged_answers(
            pending_followup=pending_followup,
            slot=pending_slot,
            value=value,
            case=case,
        )
        if not staged_answers:
            return SlotFillResult(False, pending_slot)
        return SlotFillResult(True, pending_slot, staged_answers=staged_answers)

    @staticmethod
    def _extract_duration_or_onset(text: str) -> str | None:
        return text or None

    @staticmethod
    def _extract_severity(text: str) -> int | None:
        match = re.search(r"\b(10|[0-9])\b", text)
        if match:
            return int(match.group(1))
        return None

def _build_staged_answers(
    *,
    pending_followup: "PendingFollowupContext",
    slot: str | None,
    value,
    case: MedicalCase,
) -> list[StagedFollowupAnswer]:
    requirement = pending_followup.resolved_field
    if requirement is None:
        return []

    raw_text = str(value).strip()
    if not raw_text:
        return []

    focus_id = case.primary_problem_id
    return [
        StagedFollowupAnswer(
            requirement_key=requirement.key,
            raw_text=raw_text,
            slot=slot,
            focus_observation_id=focus_id,
        )
    ]
