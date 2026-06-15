from __future__ import annotations

from careena_pipeline3.core.exceptions import (
    EmptyLLMResponseError,
    InvalidJSONError,
    SchemaValidationError,
)
from careena_pipeline3.llm.requirement_followup_resolver import (
    LLMRequirementFollowupResolver,
)
from careena_pipeline3.models.domain import DialogueState, MedicalCase, PendingFollowup
from careena_pipeline3.models.turn import (
    RequirementFieldUpdate,
    RequirementFollowupResolutionResult,
)


class RequirementFollowupResolutionService:
    """Resolves one open requirement follow-up without going through Call 1/2."""

    def __init__(
        self,
        *,
        resolver: LLMRequirementFollowupResolver | None = None,
    ):
        self.resolver = resolver

    def resolve(
        self,
        *,
        latest_user_message: str,
        pending_followup: PendingFollowup,
        medical_case: MedicalCase | None,
        dialogue_state: DialogueState | None,
        history_messages: list[dict[str, str]] | None = None,
    ) -> tuple[RequirementFollowupResolutionResult | None, RequirementFieldUpdate | None]:
        if self.resolver is None:
            return None, None

        try:
            result = self.resolver.resolve(
                latest_user_message=latest_user_message,
                pending_followup=pending_followup,
                last_assistant_question=_last_assistant_question(history_messages),
                current_value=self._current_value(
                    pending_followup=pending_followup,
                    medical_case=medical_case,
                ),
                allowed_answer_shape=_allowed_answer_shape(pending_followup.slot),
            )
        except (EmptyLLMResponseError, InvalidJSONError, SchemaValidationError):
            return None, None

        if result.status != "resolved" or result.normalized_value is None:
            return result, None

        target_kind = (
            "subject"
            if pending_followup.requirement_key.startswith("subject.")
            else "observation"
        )
        return result, RequirementFieldUpdate(
            requirement_key=pending_followup.requirement_key,
            slot=pending_followup.slot,
            target_kind=target_kind,
            target_observation_id=(
                pending_followup.focus_observation_id if target_kind == "observation" else None
            ),
            normalized_value=result.normalized_value,
            source_text=latest_user_message,
        )

    @staticmethod
    def _current_value(
        *,
        pending_followup: PendingFollowup,
        medical_case: MedicalCase | None,
    ) -> str | int | None:
        if medical_case is None:
            return None
        key = pending_followup.requirement_key
        if key == "subject.subject_relation":
            value = medical_case.subject.relation
            return None if value == "unknown" else value
        if key == "subject.age":
            return medical_case.subject.age
        if pending_followup.focus_observation_id is None:
            return None
        for observation in medical_case.active_observations(include_negated=True):
            if observation.id != pending_followup.focus_observation_id:
                continue
            _, field_name = key.split(".", 1)
            return observation.requirement_value(field_name)
        return None


def _last_assistant_question(
    history_messages: list[dict[str, str]] | None,
) -> str | None:
    for message in reversed(history_messages or []):
        role = (message.get("role") or "").strip().lower()
        if role in {"assistant", "careena"}:
            content = (message.get("content") or "").strip()
            if content:
                return content
    return None


def _allowed_answer_shape(slot: str) -> str | None:
    return {
        "duration_or_onset": "short_time_phrase_only",
        "severity": "severity_only",
        "injury_context": "short_cause_phrase_only",
        "functional_limitation": "short_limitation_phrase_only",
        "subject": "single_relation_only",
        "subject_age": "single_integer_age_only",
    }.get(slot)
