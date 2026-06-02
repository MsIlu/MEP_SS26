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

        merged_any = False
        if update.subject is not None and update.subject.relation != "unknown":
            if (
                existing_case.subject.relation == "unknown"
                or update.subject.confidence >= existing_case.subject.confidence
            ):
                existing_case.subject = update.subject

        for observation in update.observations_added:
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

        for observation in update.negated_observations_added:
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

        self._apply_requirement_resolution(existing_case, update)
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
        target.temporality = _pick_text(
            current=target.temporality,
            incoming=source.temporality,
            overwrite=overwrite,
        )
        target.severity = _pick_value(
            current=target.severity,
            incoming=source.severity,
            overwrite=overwrite,
        )
        target.body_site = _pick_text(
            current=target.body_site,
            incoming=source.body_site,
            overwrite=overwrite,
        )
        target.laterality = _pick_value(
            current=target.laterality,
            incoming=source.laterality,
            overwrite=overwrite,
        )
        target.course = _pick_value(
            current=target.course,
            incoming=source.course,
            overwrite=overwrite,
        )
        if source.measurement:
            target.measurement = (
                {**target.measurement, **source.measurement}
                if overwrite
                else {**source.measurement, **target.measurement}
            )
        if source.details:
            target.details = (
                {**target.details, **source.details}
                if overwrite
                else {**source.details, **target.details}
            )
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

    @classmethod
    def _apply_requirement_resolution(
        cls,
        case: MedicalCase,
        update: MessageUpdate,
    ) -> None:
        if not update.resolved_fields:
            return

        resolved_keys = {item.key for item in update.resolved_fields}
        sources = update.observations_added + update.negated_observations_added
        overwrite = update.message_role == "correction"
        for module in ("injury", "symptom"):
            if not any(key.startswith(f"{module}.") for key in resolved_keys):
                continue
            for target in cls._requirement_targets(case, module=module):
                cls._project_fields(
                    target=target,
                    sources=sources,
                    resolved_keys=resolved_keys,
                    module=module,
                    overwrite=overwrite,
                    fallback_text=update.raw_text,
                )
                # For now only enrich one intended target per module to avoid
                # spraying a follow-up answer across multiple observations.
                break

    @classmethod
    def _project_fields(
        cls,
        *,
        target: CaseObservation,
        sources: list[CaseObservation],
        resolved_keys: set[str],
        module: str,
        overwrite: bool,
        fallback_text: str | None,
    ) -> None:
        if f"{module}.duration_or_onset" in resolved_keys:
            value = cls._first_value(sources, "temporality")
            if value and (overwrite or not target.temporality):
                target.temporality = value
        if f"{module}.severity" in resolved_keys:
            value = cls._first_value(sources, "severity")
            if value is not None and (overwrite or target.severity is None):
                target.severity = value
        if f"{module}.body_site" in resolved_keys:
            value = cls._first_value(sources, "body_site")
            if value and (overwrite or not target.body_site):
                target.body_site = value
        if f"{module}.course" in resolved_keys:
            value = cls._first_value(sources, "course")
            if value and (overwrite or target.course is None):
                target.course = value
        if module == "injury" and "injury.injury_context" in resolved_keys:
            value = cls._first_detail(sources, "context") or fallback_text
            if value and (overwrite or "context" not in target.details):
                target.details["context"] = value
        if module == "injury" and "injury.functional_limitation" in resolved_keys:
            value = cls._first_detail(sources, "functional_limitation")
            if value and (
                overwrite or "functional_limitation" not in target.details
            ):
                target.details["functional_limitation"] = value

    @staticmethod
    def _requirement_targets(
        case: MedicalCase,
        *,
        module: str,
    ) -> list[CaseObservation]:
        primary = case.primary_observation()
        if primary is not None and primary.type == module:
            return [primary]

        targets = case.observations_of_type(module, include_negated=True)
        if not targets:
            return []

        primary_focus = case.primary_focus_label()
        if primary_focus:
            focused = [
                observation
                for observation in targets
                if observation.patient_label == primary_focus
            ]
            if focused:
                return focused

        return targets

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
    def _first_value(sources: list[CaseObservation], field: str):
        for source in sources:
            value = getattr(source, field)
            if value is not None:
                return value
        return None

    @staticmethod
    def _first_detail(sources: list[CaseObservation], key: str) -> str | None:
        for source in sources:
            value = source.details.get(key)
            if value:
                return value
        return None

    @staticmethod
    def _same_focus(left: CaseObservation, right: CaseObservation) -> bool:
        left_key = ((left.concept or left.label or "").strip().lower(), (left.body_site or "").strip().lower())
        right_key = ((right.concept or right.label or "").strip().lower(), (right.body_site or "").strip().lower())
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
        candidates = update.observations_added + update.negated_observations_added
        for observation in candidates:
            for existing in case.observations:
                if existing.id == observation.id:
                    return existing
        return None
