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
            if self._already_present(existing_case, observation):
                continue
            self._append(existing_case, observation)

        for observation in update.negated_observations_added:
            if self._already_present(existing_case, observation):
                continue
            existing_case.observations.append(observation)

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
