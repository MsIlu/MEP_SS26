from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from careena4.models.common import CaseExtensionKind, FollowupPriority, FollowupReason
from careena4.models.domain import MedicalCase, Observation


ObservationRequirementField = Literal["person_ref", "onset", "severity", "description"]


@dataclass(frozen=True)
class CaseRequirementRule:
    reason: FollowupReason
    priority: FollowupPriority = "high"
    blocking: bool = True


@dataclass(frozen=True)
class ObservationRequirementRule:
    field_name: ObservationRequirementField
    reason: FollowupReason
    target_extension_kind: CaseExtensionKind | None = None
    priority: FollowupPriority = "high"
    blocking: bool = True


class RequirementPolicy:
    _CASE_RULES = (
        CaseRequirementRule(reason="subject_unclear"),
    )

    _SYMPTOM_RULES = (
        ObservationRequirementRule(field_name="person_ref", reason="person_ref_missing"),
        ObservationRequirementRule(
            field_name="onset",
            reason="duration_missing",
            target_extension_kind="duration_or_onset",
        ),
        ObservationRequirementRule(field_name="severity", reason="severity_missing"),
        ObservationRequirementRule(
            field_name="description",
            reason="description_missing",
            target_extension_kind="description",
        ),
    )

    def case_rules(self) -> tuple[CaseRequirementRule, ...]:
        return self._CASE_RULES

    def observation_rules(self, *, observation: Observation) -> tuple[ObservationRequirementRule, ...]:
        if observation.type != "symptom":
            return ()
        return self._SYMPTOM_RULES

    @staticmethod
    def is_case_rule_satisfied(*, medical_case: MedicalCase, rule: CaseRequirementRule) -> bool:
        if rule.reason == "subject_unclear":
            return medical_case.person.relation != "unclear"
        return True

    @staticmethod
    def is_observation_rule_satisfied(*, observation: Observation, rule: ObservationRequirementRule) -> bool:
        value = getattr(observation, rule.field_name)
        return value not in (None, "", [], "unclear")
