from careena_pipeline.models import CaseObservation, MedicalCase, MessageUpdate


def same_observation_identity(
    left: CaseObservation,
    right: CaseObservation,
) -> bool:
    return (
        left.type == right.type
        and (left.concept or left.label) == (right.concept or right.label)
        and left.source_span == right.source_span
        and left.subject_ref == right.subject_ref
        and left.negated == right.negated
    )


class CaseMergePolicy:
    """
    Transitional matching and target-selection policy for CaseMerger.

    This component intentionally centralizes the still heuristic merge-target
    decisions so the actual merger can move closer to pure delta application.
    """

    def merge_target(
        self,
        *,
        case: MedicalCase,
        update: MessageUpdate,
        observation: CaseObservation,
    ) -> CaseObservation | None:
        by_id = self._existing_by_id(case, observation.id)
        if by_id is not None:
            return by_id

        exact = self._exact_match(case, observation)
        if exact is not None:
            return exact

        same_focus = self._same_focus_target(case, update, observation)
        if same_focus is not None:
            return same_focus

        primary = case.primary_observation()
        if primary is None:
            return None

        resolved_keys = {item.key for item in update.resolved_fields}
        if self._can_merge_into_primary_injury(
            update=update,
            primary=primary,
            incoming=observation,
            resolved_keys=resolved_keys,
        ):
            return primary
        return None

    def latest_focus_candidate(
        self,
        *,
        case: MedicalCase,
        update: MessageUpdate,
    ) -> CaseObservation | None:
        candidates = update.case_payload.all_observations
        for observation in candidates:
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

    @staticmethod
    def _existing_by_id(
        case: MedicalCase,
        observation_id: str | None,
    ) -> CaseObservation | None:
        if not observation_id:
            return None
        for existing in case.observations:
            if existing.id == observation_id:
                return existing
        return None

    def _exact_match(
        self,
        case: MedicalCase,
        observation: CaseObservation,
    ) -> CaseObservation | None:
        for existing in case.observations:
            if same_observation_identity(existing, observation):
                return existing
        return None

    def _same_focus_target(
        self,
        case: MedicalCase,
        update: MessageUpdate,
        observation: CaseObservation,
    ) -> CaseObservation | None:
        intent_signals = update.intent_signals
        if intent_signals.possible_new_topic or intent_signals.message_role == "topic_shift":
            return None

        primary = case.primary_observation()
        if primary is None or primary.type != observation.type:
            return None
        if not self._same_focus(primary, observation):
            return None
        if self._can_merge_same_focus(
            update=update,
            existing=primary,
            incoming=observation,
        ):
            return primary
        return None

    def _can_merge_same_focus(
        self,
        *,
        update: MessageUpdate,
        existing: CaseObservation,
        incoming: CaseObservation,
    ) -> bool:
        if self._has_conflicting_qualifiers(existing, incoming):
            return False
        if update.intent_signals.message_role in {"answer_to_followup", "confirmation", "correction"}:
            return True
        return True

    def _can_merge_into_primary_injury(
        self,
        *,
        update: MessageUpdate,
        primary: CaseObservation,
        incoming: CaseObservation,
        resolved_keys: set[str],
    ) -> bool:
        if update.intent_signals.possible_new_topic:
            return False
        if update.intent_signals.message_role not in {"answer_to_followup", "correction"}:
            return False
        if incoming.type != "injury" or primary.type != "injury":
            return False
        if not any(key.startswith("injury.") for key in resolved_keys):
            return False
        if self._has_conflicting_qualifiers(primary, incoming):
            return False

        incoming_focus = (
            (incoming.concept or incoming.label or "").strip().lower(),
            (incoming.runtime_value("body_site") or "").strip().lower(),
        )
        primary_focus = (
            (primary.concept or primary.label or "").strip().lower(),
            (primary.runtime_value("body_site") or "").strip().lower(),
        )
        if incoming_focus != ("", "") and incoming_focus != primary_focus:
            return False
        return True

    @staticmethod
    def _has_conflicting_qualifiers(
        existing: CaseObservation,
        incoming: CaseObservation,
    ) -> bool:
        if (
            existing.laterality is not None
            and incoming.laterality is not None
            and existing.laterality != incoming.laterality
        ):
            return True
        if (
            existing.subject_ref
            and incoming.subject_ref
            and existing.subject_ref != incoming.subject_ref
        ):
            return True
        if existing.negated != incoming.negated:
            return True

        overlapping_details = set(existing.details).intersection(incoming.details)
        if any(
            existing.details[key] != incoming.details[key]
            for key in overlapping_details
        ):
            return True

        overlapping_measurements = set(existing.measurement).intersection(
            incoming.measurement
        )
        if any(
            existing.measurement[key] != incoming.measurement[key]
            for key in overlapping_measurements
        ):
            return True

        return False
