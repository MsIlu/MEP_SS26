from careena4.models.domain import Observation, Provenance, Subject
from careena4.models.turn import CaseWritePlan, CaseWriteStep, ExtractionClaims, ObservationClaim


class _CaseWritePlanner:
    def build_write_plan(
        self,
        *,
        existing_observations: list[Observation],
        claims: ExtractionClaims,
        topic_id: str | None,
    ) -> CaseWritePlan:
        plan = CaseWritePlan(topic_id_update=topic_id)
        subject_update = self._subject_update(claims)
        if subject_update is not None:
            plan.subject_update = subject_update
        for index, claim in enumerate(claims.observations):
            mapped_observation = self._to_observation(claim)
            target = self._find_match(existing_observations=existing_observations, claim=claim)
            if target is None:
                plan.steps.append(CaseWriteStep(action="create", claim_index=index, observation=mapped_observation))
                continue
            if claim.negated:
                plan.steps.append(
                    CaseWriteStep(
                        action="negate",
                        claim_index=index,
                        observation=mapped_observation,
                        target_observation_id=target.observation_id,
                    )
                )
                continue
            if self._has_new_information(target=target, claim=claim):
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
    def _subject_update(claims: ExtractionClaims) -> Subject | None:
        relation = claims.subject_claims.get("relation")
        if relation not in {"self", "child", "other", "unclear"}:
            return None
        return Subject(relation=relation)

    @staticmethod
    def _to_observation(claim: ObservationClaim) -> Observation:
        topic_relation = "central" if claim.type in {"symptom", "injury", "measurement"} else "related"
        return Observation(
            type=claim.type,
            label=claim.label,
            normalized_concept=claim.normalized_concept,
            subject_ref=claim.subject_ref or "unclear",
            negated=claim.negated,
            topic_relation=topic_relation,
            attributes=dict(claim.attributes),
            provenance=[Provenance(source="user_message", source_span=claim.source_span)],
        )

    @staticmethod
    def _find_match(*, existing_observations: list[Observation], claim: ObservationClaim) -> Observation | None:
        identity = (
            claim.type,
            claim.normalized_concept or claim.label.casefold(),
            claim.subject_ref or "unclear",
        )
        for observation in existing_observations:
            if observation.identity_key() == identity:
                return observation
        return None

    @staticmethod
    def _has_new_information(*, target: Observation, claim: ObservationClaim) -> bool:
        if claim.negated and not target.negated:
            return True
        for key, value in claim.attributes.items():
            if value is None:
                continue
            if target.attributes.get(key) != value:
                return True
        return False
