from careena_pipeline.models import CaseObservation, MedicalCase, MessageUpdate


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

        if update.subject is not None and update.subject.relation != "unknown":
            if (
                existing_case.subject.relation == "unknown"
                or update.subject.confidence >= existing_case.subject.confidence
            ):
                existing_case.subject = update.subject

        for observation in update.observations_added:
            target = self._merge_target(existing_case, update, observation)
            if target is not None:
                self._merge_observation(target, observation)
                continue
            if self._already_present(existing_case, observation):
                continue
            self._append(existing_case, observation)

        for observation in update.negated_observations_added:
            target = self._merge_target(existing_case, update, observation)
            if target is not None:
                self._merge_observation(target, observation)
                continue
            if self._already_present(existing_case, observation):
                continue
            existing_case.observations.append(observation)

        self._apply_requirement_resolution(existing_case, update)

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

        same_focus = cls._same_focus_target(case, observation)
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
    def _merge_observation(target: CaseObservation, source: CaseObservation) -> None:
        if not target.display_label and source.display_label:
            target.display_label = source.display_label
        if not target.concept and source.concept:
            target.concept = source.concept
        if not target.temporality and source.temporality:
            target.temporality = source.temporality
        if target.severity is None and source.severity is not None:
            target.severity = source.severity
        if not target.body_site and source.body_site:
            target.body_site = source.body_site
        if target.laterality is None and source.laterality is not None:
            target.laterality = source.laterality
        if target.course is None and source.course is not None:
            target.course = source.course
        if source.measurement:
            target.measurement = {**target.measurement, **source.measurement}
        if source.details:
            target.details = {**target.details, **source.details}
        if source.subject_ref and not target.subject_ref:
            target.subject_ref = source.subject_ref
        if source.provenance:
            target.provenance.extend(source.provenance)
        if source.confidence is not None and (
            target.confidence is None or source.confidence > target.confidence
        ):
            target.confidence = source.confidence

    @classmethod
    def _apply_requirement_resolution(
        cls,
        case: MedicalCase,
        update: MessageUpdate,
    ) -> None:
        if not update.resolved_fields:
            return

        primary = case.primary_observation()
        if primary is None:
            return

        resolved_keys = {item.key for item in update.resolved_fields}
        sources = update.observations_added + update.negated_observations_added
        if any(key.startswith("injury.") for key in resolved_keys) and primary.type == "injury":
            cls._project_fields(
                target=primary,
                sources=sources,
                resolved_keys=resolved_keys,
                module="injury",
            )
        if any(key.startswith("symptom.") for key in resolved_keys) and primary.type == "symptom":
            cls._project_fields(
                target=primary,
                sources=sources,
                resolved_keys=resolved_keys,
                module="symptom",
            )

    @classmethod
    def _project_fields(
        cls,
        *,
        target: CaseObservation,
        sources: list[CaseObservation],
        resolved_keys: set[str],
        module: str,
    ) -> None:
        if f"{module}.duration_or_onset" in resolved_keys:
            value = cls._first_value(sources, "temporality")
            if value and not target.temporality:
                target.temporality = value
        if f"{module}.severity" in resolved_keys:
            value = cls._first_value(sources, "severity")
            if value is not None and target.severity is None:
                target.severity = value
        if f"{module}.body_site" in resolved_keys:
            value = cls._first_value(sources, "body_site")
            if value and not target.body_site:
                target.body_site = value
        if f"{module}.course" in resolved_keys:
            value = cls._first_value(sources, "course")
            if value and target.course is None:
                target.course = value
        if module == "injury" and "injury.injury_context" in resolved_keys:
            value = cls._first_detail(sources, "context")
            if value and "context" not in target.details:
                target.details["context"] = value
        if module == "injury" and "injury.functional_limitation" in resolved_keys:
            value = cls._first_detail(sources, "functional_limitation")
            if value and "functional_limitation" not in target.details:
                target.details["functional_limitation"] = value

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
        observation: CaseObservation,
    ) -> CaseObservation | None:
        candidates = [
            existing
            for existing in case.observations
            if existing.type == observation.type
        ]
        for existing in candidates:
            if cls._same_focus(existing, observation):
                return existing
        return None

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
