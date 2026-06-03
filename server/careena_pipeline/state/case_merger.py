from careena_pipeline.models import CaseObservation, MedicalCase, MessageUpdate


def _pick_text(
    *,
    current: str | None,
    incoming: str | None,
    overwrite: bool,
) -> str | None:
    if not incoming:
        return current
    if overwrite or not current:
        return incoming
    return current


def _pick_value(
    *,
    current,
    incoming,
    overwrite: bool,
):
    if incoming is None:
        return current
    if overwrite or current is None:
        return incoming
    return current


class CaseMerger:
    """
    Merges a structured CaseUpdate into an existing MedicalCase.

    This is intentionally conservative: it appends new observations and keeps
    the existing focus unless the case did not have one yet.
    """

    def merge_update(
        self,
        existing_case: MedicalCase | None,
        update: MessageUpdate,
    ) -> MedicalCase:
        if existing_case is None:
            existing_case = MedicalCase()

        case_payload = update.case_payload
        merged_any = False
        if case_payload.subject is not None and case_payload.subject.relation != "unknown":
            if (
                existing_case.subject.relation == "unknown"
                or case_payload.subject.confidence >= existing_case.subject.confidence
            ):
                existing_case.subject = case_payload.subject

        for observation in case_payload.observations_added:
            target = self._merge_target(existing_case, update, observation)
            if target is not None:
                self._merge_observation(
                    target,
                    observation,
                    message_role=update.message_role,
                )
                merged_any = True
                continue
            if self._already_present(existing_case, observation):
                continue
            observation.status = self._status_for_new_observation(
                update.message_role,
                default=observation.status,
            )
            self._append(existing_case, observation)
            merged_any = True

        for observation in case_payload.negated_observations_added:
            target = self._merge_target(existing_case, update, observation)
            if target is not None:
                self._merge_observation(
                    target,
                    observation,
                    message_role=update.message_role,
                )
                merged_any = True
                continue
            if self._already_present(existing_case, observation):
                continue
            observation.status = self._status_for_new_observation(
                update.message_role,
                default=observation.status,
            )
            existing_case.observations.append(observation)
            merged_any = True

        self._apply_message_role(existing_case, update, merged_any=merged_any)

        if update.possible_new_topic:
            primary = self._latest_focus_candidate(existing_case, update)
            if primary is not None:
                existing_case.set_primary_observation(primary)
        elif existing_case.primary_problem_id is None:
            existing_case.ensure_primary_problem()

        return existing_case

    @staticmethod
    def _already_present(case: MedicalCase, observation: CaseObservation) -> bool:
        return any(
            existing.type == observation.type
            and (existing.concept or existing.label) == (observation.concept or observation.label)
            and existing.source_span == observation.source_span
            for existing in case.observations
        )

    @staticmethod
    def _append(case: MedicalCase, observation: CaseObservation) -> None:
        case.observations.append(observation)

    @classmethod
    def _merge_target(
        cls,
        case: MedicalCase,
        update: MessageUpdate,
        observation: CaseObservation,
    ) -> CaseObservation | None:
        by_id = cls._existing_by_id(case, observation.id)
        if by_id is not None:
            return by_id

        exact = cls._exact_match(case, observation)
        if exact is not None:
            return exact

        same_focus = cls._same_focus_target(case, update, observation)
        if same_focus is not None:
            return same_focus

        primary = case.primary_observation()
        if primary is None:
            return None

        resolved_keys = {item.key for item in update.resolved_fields}
        if (
            observation.type == "injury"
            and primary.type == "injury"
            and any(key.startswith("injury.") for key in resolved_keys)
        ):
            return primary
        return None

    @staticmethod
    def _merge_observation(
        target: CaseObservation,
        source: CaseObservation,
        *,
        message_role: str,
    ) -> None:
        overwrite = message_role == "correction"
        target.display_label = _pick_text(
            current=target.display_label,
            incoming=source.display_label,
            overwrite=overwrite,
        )
        target.concept = _pick_text(
            current=target.concept,
            incoming=source.concept,
            overwrite=overwrite,
        )
        temporality = _pick_text(
            current=target.runtime_value("temporality"),
            incoming=source.runtime_value("temporality"),
            overwrite=overwrite,
        )
        if temporality != target.temporality:
            target.set_surface_field("temporality", temporality)

        severity = _pick_value(
            current=target.runtime_value("severity"),
            incoming=source.runtime_value("severity"),
            overwrite=overwrite,
        )
        if severity != target.severity:
            target.set_surface_field("severity", severity)

        body_site = _pick_text(
            current=target.runtime_value("body_site"),
            incoming=source.runtime_value("body_site"),
            overwrite=overwrite,
        )
        if body_site != target.body_site:
            target.set_surface_field("body_site", body_site)

        target.laterality = _pick_value(
            current=target.laterality,
            incoming=source.laterality,
            overwrite=overwrite,
        )
        course = _pick_value(
            current=target.runtime_value("course"),
            incoming=source.runtime_value("course"),
            overwrite=overwrite,
        )
        if course != target.course:
            target.set_surface_field("course", course)

        if source.measurement:
            target.merge_measurement_values(source.measurement, overwrite=overwrite)
        if source.details:
            target.merge_detail_values(source.details, overwrite=overwrite)
        target.subject_ref = _pick_text(
            current=target.subject_ref,
            incoming=source.subject_ref,
            overwrite=overwrite,
        )
        if overwrite and source.source_span:
            target.source_span = source.source_span
        if overwrite:
            target.negated = source.negated
            target.certainty = source.certainty
        if source.provenance:
            target.provenance.extend(source.provenance)
        if source.confidence is not None and (
            target.confidence is None or source.confidence > target.confidence
        ):
            target.confidence = source.confidence
        if message_role == "confirmation":
            target.status = "user_confirmed"
        elif message_role == "correction":
            target.status = "user_corrected"

    @staticmethod
    def _status_for_new_observation(message_role: str, *, default: str) -> str:
        if message_role == "confirmation":
            return "user_confirmed"
        if message_role == "correction":
            return "user_corrected"
        return default

    @staticmethod
    def _apply_message_role(
        case: MedicalCase,
        update: MessageUpdate,
        *,
        merged_any: bool,
    ) -> None:
        primary = case.primary_observation()
        if primary is None:
            return
        if update.message_role == "confirmation" and not merged_any:
            primary.status = "user_confirmed"

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
    def _existing_by_id(case: MedicalCase, observation_id: str | None) -> CaseObservation | None:
        if not observation_id:
            return None
        for existing in case.observations:
            if existing.id == observation_id:
                return existing
        return None

    @classmethod
    def _exact_match(
        cls,
        case: MedicalCase,
        observation: CaseObservation,
    ) -> CaseObservation | None:
        for existing in case.observations:
            if (
                existing.type == observation.type
                and (existing.concept or existing.label) == (observation.concept or observation.label)
                and existing.source_span == observation.source_span
            ):
                return existing
        return None

    @classmethod
    def _same_focus_target(
        cls,
        case: MedicalCase,
        update: MessageUpdate,
        observation: CaseObservation,
    ) -> CaseObservation | None:
        if update.possible_new_topic or update.message_role == "topic_shift":
            return None

        candidates = [
            existing
            for existing in case.observations
            if existing.type == observation.type
        ]
        for existing in candidates:
            if (
                cls._same_focus(existing, observation)
                and cls._can_merge_same_focus(
                    update=update,
                    existing=existing,
                    incoming=observation,
                )
            ):
                return existing
        return None

    @classmethod
    def _can_merge_same_focus(
        cls,
        *,
        update: MessageUpdate,
        existing: CaseObservation,
        incoming: CaseObservation,
    ) -> bool:
        if update.message_role in {"answer_to_followup", "confirmation", "correction"}:
            return True
        if cls._has_conflicting_qualifiers(existing, incoming):
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

    @staticmethod
    def _latest_focus_candidate(
        case: MedicalCase,
        update: MessageUpdate,
    ) -> CaseObservation | None:
        candidates = update.case_payload.all_observations
        for observation in candidates:
            for existing in case.observations:
                if existing.id == observation.id:
                    return existing
        return None
