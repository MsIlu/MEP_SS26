from careena4.models.domain import Observation, Person
from careena4.models.turn import CaseWritePlan, CaseWriteStep


class _CaseWritePlanner:
    def build_write_plan(
        self,
        *,
        existing_observations: list[Observation],
        observations: list[Observation],
        person_update: Person | None = None,
    ) -> CaseWritePlan:
        plan = CaseWritePlan(person_update=person_update)
        for index, mapped_observation in enumerate(observations):
            target = self._find_match(
                existing_observations=existing_observations,
                candidate=mapped_observation,
            )
            if target is None:
                plan.steps.append(CaseWriteStep(action="create", claim_index=index, observation=mapped_observation))
                continue
            if mapped_observation.status == "negated":
                plan.steps.append(
                    CaseWriteStep(
                        action="negate",
                        claim_index=index,
                        observation=mapped_observation,
                        target_observation_id=target.observation_id,
                    )
                )
                continue
            if self._has_new_information(target=target, candidate=mapped_observation):
                plan.steps.append(
                    CaseWriteStep(
                        action="enrich",
                        claim_index=index,
                        observation=mapped_observation,
                        target_observation_id=target.observation_id,
                    )
                )
            else:
                plan.steps.append(
                    CaseWriteStep(
                        action="ignore",
                        claim_index=index,
                        observation=mapped_observation,
                        target_observation_id=target.observation_id,
                    )
                )
        return plan

    @staticmethod
    def _find_match(*, existing_observations: list[Observation], candidate: Observation) -> Observation | None:
        for observation in existing_observations:
            if observation.matches_identity(other=candidate):
                return observation
        return None

    @staticmethod
    def _has_new_information(*, target: Observation, candidate: Observation) -> bool:
        if candidate.status == "negated" and not target.is_negated():
            return True
        if candidate.person_ref != "unclear" and candidate.person_ref != target.person_ref:
            return True
        return not target.has_same_medical_content(other=candidate)
