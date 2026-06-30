from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from careena4.models.common import FollowupPriority, FollowupReason
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
    priority: FollowupPriority = "high"
    blocking: bool = True


class RequirementPolicy:
    _CASE_RULES = (
        CaseRequirementRule(reason="person_missing"),
        CaseRequirementRule(reason="age_missing"),
        CaseRequirementRule(reason="sex_missing"),
    )

    _SYMPTOM_RULES = (
        ObservationRequirementRule(field_name="person_ref", reason="person_ref_missing"),
        ObservationRequirementRule(field_name="onset", reason="duration_missing"),
        ObservationRequirementRule(field_name="severity", reason="severity_missing"),
        ObservationRequirementRule(field_name="description", reason="description_missing"),
    )

    def case_rules(self) -> tuple[CaseRequirementRule, ...]:
        return self._CASE_RULES

    def observation_rules(self, *, observation: Observation) -> tuple[ObservationRequirementRule, ...]:
        if observation.type != "symptom":
            return ()
        return self._SYMPTOM_RULES

    @staticmethod
    def is_case_rule_satisfied(*, medical_case: MedicalCase, rule: CaseRequirementRule) -> bool:
        if rule.reason == "person_missing":
            return medical_case.person.relation != "unclear"
        if rule.reason == "age_missing":
            return medical_case.person.relation == "unclear" or medical_case.person.age is not None
        if rule.reason == "sex_missing":
            return medical_case.person.relation == "unclear" or medical_case.person.sex not in (None, "")
        return True

    @staticmethod
    def is_observation_rule_satisfied(*, observation: Observation, rule: ObservationRequirementRule) -> bool:
        value = getattr(observation, rule.field_name)
        return value not in (None, "", [], "unclear")
