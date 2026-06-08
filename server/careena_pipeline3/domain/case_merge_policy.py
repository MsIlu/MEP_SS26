from careena_pipeline3.domain.case_update import ObservationUpdateDecision
from careena_pipeline3.domain.observation_identity_resolver import (
    ObservationIdentityResolver,
    normalized_text,
)
from careena_pipeline3.domain.observation_normalizer import ObservationNormalizer
from careena_pipeline3.models.domain import CaseObservation, MedicalCase
from careena_pipeline3.models.turn.message_delta import MessageDelta


"""
Date: 2026-06-08
Last changed: 2026-06-08
Author: workbench@freddy

Short description:
Decides how an incoming observation should update canonical case truth.
It consumes normalized identity matches and returns explicit update decisions with dialogue consequences.
"""
class CaseMergePolicy:
    """Target selection policy for applying a message delta to a medical case."""

    def __init__(
        self,
        *,
        observation_normalizer: ObservationNormalizer | None = None,
        identity_resolver: ObservationIdentityResolver | None = None,
    ):
        self.observation_normalizer = observation_normalizer or ObservationNormalizer()
        self.identity_resolver = identity_resolver or ObservationIdentityResolver()

    def decide_observation_update(
        self,
        *,
        case: MedicalCase,
        delta: MessageDelta,
        observation: CaseObservation,
    ) -> ObservationUpdateDecision:
        observation = self.observation_normalizer.normalize(observation)
        match = self.match_observation(case=case, delta=delta, observation=observation)
        if match.status == "no_match":
            return ObservationUpdateDecision(
                match_status=match.status,
                change_kind="new_instance",
                action="create_observation",
                notes=[*match.notes, "case_update:create_observation"],
            )

        if match.status == "ambiguous_match":
            return ObservationUpdateDecision(
                match_status=match.status,
                change_kind="new_instance",
                action="defer_update",
                dialogue_consequence="ask_disambiguation_followup",
                notes=[
                    *match.notes,
                    "case_update:defer_ambiguous_match",
                    "dialogue_consequence:ask_disambiguation_followup",
                ],
            )

        target = match.single_candidate
        if target is None:
            return ObservationUpdateDecision(
                match_status="no_match",
                change_kind="new_instance",
                action="create_observation",
                notes=["case_update:fallback_create_observation"],
            )

        if delta.intent_signals.possible_new_topic and target.id != observation.id:
            return ObservationUpdateDecision(
                match_status=match.status,
                change_kind="new_instance",
                action="create_observation",
                notes=[*match.notes, "case_update:create_due_to_topic_shift_signal"],
            )

        if delta.intent_signals.message_role == "correction":
            return ObservationUpdateDecision(
                match_status=match.status,
                change_kind="correction",
                action="correct_observation",
                target=target,
                notes=[*match.notes, "case_update:correct_observation"],
            )

        if self._has_conflicting_qualifiers(existing=target, incoming=observation):
            return ObservationUpdateDecision(
                match_status=match.status,
                change_kind="contradiction",
                action="flag_conflict",
                target=target,
                dialogue_consequence="ask_conflict_followup",
                notes=[
                    *match.notes,
                    "case_update:flag_conflict",
                    "dialogue_consequence:ask_conflict_followup",
                ],
            )

        if self._adds_specificity(existing=target, incoming=observation):
            return ObservationUpdateDecision(
                match_status=match.status,
                change_kind="enrichment",
                action="enrich_observation",
                target=target,
                notes=[*match.notes, "case_update:enrich_observation"],
            )

        return ObservationUpdateDecision(
            match_status=match.status,
            change_kind="confirmation",
            action="confirm_observation",
            target=target,
            notes=[*match.notes, "case_update:confirm_observation"],
        )

    def match_observation(
        self,
        *,
        case: MedicalCase,
        delta: MessageDelta,
        observation: CaseObservation,
    ):
        return self.identity_resolver.match_observation(
            case=case,
            delta=delta,
            observation=observation,
        )

    def latest_focus_candidate(
        self,
        *,
        case: MedicalCase,
        delta: MessageDelta,
    ) -> CaseObservation | None:
        return self.identity_resolver.latest_focus_candidate(case=case, delta=delta)

    def already_present(
        self,
        *,
        case: MedicalCase,
        observation: CaseObservation,
    ) -> bool:
        observation = self.observation_normalizer.normalize(observation)
        return self.identity_resolver.already_present(case=case, observation=observation)

    @staticmethod
    def _same_focus(left: CaseObservation, right: CaseObservation) -> bool:
        left_key = (
            (left.concept or left.label or "").strip().lower(),
            (left.runtime_value("body_site") or "").strip().lower(),
        )
        right_key = (
            (right.concept or right.label or "").strip().lower(),
            (right.runtime_value("body_site") or "").strip().lower(),
        )
        return left_key == right_key

    def _adds_specificity(
        self,
        *,
        existing: CaseObservation,
        incoming: CaseObservation,
    ) -> bool:
        return any(
            (
                _adds_text_specificity(existing.display_label, incoming.display_label),
                _adds_text_specificity(existing.concept, incoming.concept),
                _adds_text_specificity(existing.runtime_value("temporality"), incoming.runtime_value("temporality")),
                _adds_text_specificity(existing.runtime_value("body_site"), incoming.runtime_value("body_site")),
                _adds_value_specificity(existing.runtime_value("severity"), incoming.runtime_value("severity")),
                _adds_value_specificity(existing.laterality, incoming.laterality, ignore_values={"unknown"}),
                _adds_value_specificity(existing.runtime_value("course"), incoming.runtime_value("course"), ignore_values={"unknown"}),
                _adds_mapping_specificity(existing.details, incoming.details),
                _adds_mapping_specificity(existing.measurement, incoming.measurement),
            )
        )

    @staticmethod
    def _has_conflicting_qualifiers(existing: CaseObservation, incoming: CaseObservation) -> bool:
        if _conflicting_text(existing.laterality, incoming.laterality):
            return True
        if _conflicting_text(existing.subject_ref, incoming.subject_ref):
            return True
        if existing.negated != incoming.negated:
            return True

        overlapping_details = set(existing.details).intersection(incoming.details)
        if any(
            _conflicting_text(existing.details[key], incoming.details[key])
            for key in overlapping_details
        ):
            return True

        overlapping_measurements = set(existing.measurement).intersection(incoming.measurement)
        if any(
            _conflicting_text(existing.measurement[key], incoming.measurement[key])
            for key in overlapping_measurements
        ):
            return True

        return False
def _conflicting_text(left: object, right: object) -> bool:
    left_norm = normalized_text(left)
    right_norm = normalized_text(right)
    if not left_norm or left_norm in {"unknown", "unklar"}:
        return False
    if not right_norm or right_norm in {"unknown", "unklar"}:
        return False
    return left_norm != right_norm


def _adds_text_specificity(current: object, incoming: object) -> bool:
    current_norm = normalized_text(current)
    incoming_norm = normalized_text(incoming)
    if not incoming_norm or incoming_norm == "unknown":
        return False
    if not current_norm or current_norm == "unknown":
        return True
    return False


def _adds_value_specificity(current, incoming, *, ignore_values: set | None = None) -> bool:
    if incoming is None:
        return False
    if ignore_values is not None and incoming in ignore_values:
        return False
    if current is None:
        return True
    if ignore_values is not None and current in ignore_values:
        return True
    return False


def _adds_mapping_specificity(current: dict, incoming: dict) -> bool:
    for key, value in incoming.items():
        if value is None:
            continue
        if isinstance(value, str) and value.strip().lower() in {"", "unknown", "unklar"}:
            continue
        if key not in current:
            return True
        if current.get(key) in {None, "", "unknown", "unklar"}:
            return True
    return False
