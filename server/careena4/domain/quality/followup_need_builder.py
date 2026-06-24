from __future__ import annotations

from careena4.domain.case import CaseManager
from careena4.domain.requirements import RequirementPolicy
from careena4.models.domain import CaseTopic, FollowupNeed, MedicalCase, Observation


class FollowupNeedBuilder:
    def __init__(
        self,
        *,
        case_manager: CaseManager | None = None,
        requirement_policy: RequirementPolicy | None = None,
    ) -> None:
        self.case_manager = case_manager or CaseManager()
        self.requirement_policy = requirement_policy or RequirementPolicy()

    def build(
        self,
        *,
        case_topic: CaseTopic | None,
        medical_case: MedicalCase,
    ) -> list[FollowupNeed]:
        needs: list[FollowupNeed] = []
        active_observations = self.case_manager.active_observations(medical_case=medical_case)
        topic_label = self.case_manager.topic_label(case_topic=case_topic)
        if self.case_manager.has_observations(medical_case=medical_case):
            for rule in self.requirement_policy.case_rules():
                if self.requirement_policy.is_case_rule_satisfied(medical_case=medical_case, rule=rule):
                    continue
                needs.append(
                    FollowupNeed(
                        reason=rule.reason,
                        priority=rule.priority,
                        blocking=rule.blocking,
                    )
                )

        for observation in active_observations:
            needs.extend(
                self._observation_needs(
                    observation=observation,
                    case_focus_label=topic_label or observation.label,
                )
            )
        return needs

    def _observation_needs(
        self,
        *,
        observation: Observation,
        case_focus_label: str,
    ) -> list[FollowupNeed]:
        needs: list[FollowupNeed] = []
        for rule in self.requirement_policy.observation_rules(observation=observation):
            if self.requirement_policy.is_observation_rule_satisfied(observation=observation, rule=rule):
                continue
            needs.append(
                FollowupNeed(
                    observation_id=observation.observation_id,
                    reason=rule.reason,
                    target_extension_kind=rule.target_extension_kind,
                    case_focus_label=case_focus_label,
                    related_observation_ids=[observation.observation_id],
                    priority=rule.priority,
                    blocking=rule.blocking,
                )
            )
        return needs
