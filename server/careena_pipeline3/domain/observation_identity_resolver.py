from __future__ import annotations

from careena_pipeline3.domain.case_update import ObservationMatchResult
from careena_pipeline3.models.domain import CaseObservation, MedicalCase
from careena_pipeline3.models.turn.case_update_bridge import CaseUpdateBridge


"""
Date: 2026-06-08
Last changed: 2026-06-08
Author: workbench@freddy

Short description:
Resolves whether an incoming observation refers to existing canonical case truth.
It centralizes match logic for exact identity, candidate matches, and ambiguity.
"""
class ObservationIdentityResolver:
    """Resolves whether an incoming observation refers to existing case truth."""

    def match_observation(
        self,
        *,
        case: MedicalCase,
        delta: CaseUpdateBridge,
        observation: CaseObservation,
    ) -> ObservationMatchResult:
        by_id = self.existing_by_id(case, observation.id)
        if by_id is not None:
            return ObservationMatchResult(
                status="single_match",
                candidates=[by_id],
                notes=["case_update:match_by_id"],
            )

        exact_matches = self.exact_matches(case, observation)
        if len(exact_matches) == 1:
            return ObservationMatchResult(
                status="single_match",
                candidates=exact_matches,
                notes=["case_update:match_exact_identity"],
            )
        if len(exact_matches) > 1:
            return ObservationMatchResult(
                status="ambiguous_match",
                candidates=exact_matches,
                notes=["case_update:ambiguous_exact_identity"],
            )

        candidates = self.match_candidates(case=case, delta=delta, observation=observation)
        if not candidates:
            return ObservationMatchResult(
                status="no_match",
                notes=["case_update:no_match"],
            )
        if len(candidates) == 1:
            return ObservationMatchResult(
                status="single_match",
                candidates=candidates,
                notes=["case_update:single_candidate_match"],
            )
        return ObservationMatchResult(
            status="ambiguous_match",
            candidates=candidates,
            notes=["case_update:ambiguous_candidate_match"],
        )

    def existing_by_id(
        self,
        case: MedicalCase,
        observation_id: str | None,
    ) -> CaseObservation | None:
        if not observation_id:
            return None
        for existing in case.observations:
            if existing.id == observation_id:
                return existing
        return None

    def exact_matches(
        self,
        case: MedicalCase,
        observation: CaseObservation,
    ) -> list[CaseObservation]:
        return [
            existing
            for existing in case.observations
            if same_observation_identity(existing, observation)
        ]

    def match_candidates(
        self,
        *,
        case: MedicalCase,
        delta: CaseUpdateBridge,
        observation: CaseObservation,
    ) -> list[CaseObservation]:
        merge_hints = delta.merge_hints
        candidates: list[CaseObservation] = []
        for existing in case.active_observations(include_rejected=False):
            if existing.type != observation.type:
                continue
            if merge_hints.possible_new_topic or merge_hints.message_role == "topic_shift":
                continue
            if identity_token(existing) != identity_token(observation):
                continue
            if existing.negated != observation.negated:
                continue
            if not compatible_text(existing.subject_ref, observation.subject_ref):
                continue
            if not compatible_text(existing.runtime_value("body_site"), observation.runtime_value("body_site")):
                continue
            if not compatible_text(existing.laterality, observation.laterality):
                continue
            if observation.type == "measurement" and not compatible_text(
                existing.runtime_measurement_value("kind"),
                observation.runtime_measurement_value("kind"),
            ):
                continue
            candidates.append(existing)
        return candidates

    def latest_focus_candidate(
        self,
        *,
        case: MedicalCase,
        delta: CaseUpdateBridge,
    ) -> CaseObservation | None:
        for observation in delta.claims.all_observations:
            for existing in case.observations:
                if existing.id == observation.id:
                    return existing
        return None

    def already_present(
        self,
        *,
        case: MedicalCase,
        observation: CaseObservation,
    ) -> bool:
        return any(
            same_observation_identity(existing, observation)
            for existing in case.observations
        )


def same_observation_identity(
    left: CaseObservation,
    right: CaseObservation,
) -> bool:
    return (
        left.type == right.type
        and identity_token(left) == identity_token(right)
        and left.subject_ref == right.subject_ref
        and left.negated == right.negated
        and normalized_text(left.runtime_value("body_site"))
        == normalized_text(right.runtime_value("body_site"))
        and left.laterality == right.laterality
    )


def identity_token(observation: CaseObservation) -> str:
    return normalized_text(observation.concept or observation.label)


def normalized_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def compatible_text(left: object, right: object) -> bool:
    left_norm = normalized_text(left)
    right_norm = normalized_text(right)
    if not left_norm or left_norm == "unknown":
        return True
    if not right_norm or right_norm == "unknown":
        return True
    return left_norm == right_norm
