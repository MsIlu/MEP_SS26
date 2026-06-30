from careena4.models.domain import MedicalCase, Person, Topic
from careena4.models.turn import CaseWritePlan, ObservationPatch


class _CaseWriter:
    def write_plan(self, *, medical_case: MedicalCase, plan: CaseWritePlan) -> tuple[MedicalCase, list[str]]:
        trace_notes = list(plan.trace_notes)
        person_update_keys = self._merge_person(target=medical_case.person, update=plan.person_update)
        if person_update_keys:
            trace_notes.append(f"case_write:person:{','.join(person_update_keys)}")
        for step in plan.steps:
            target = None
            if step.target_observation_id is not None:
                target = next(
                    (
                        observation
                        for observation in medical_case.observations
                        if observation.observation_id == step.target_observation_id
                    ),
                    None,
                )
            if step.action == "create" and step.observation is not None:
                medical_case.observations.append(step.observation)
                trace_notes.append(f"case_write:create:{step.observation.label}")
            elif step.action == "enrich" and target is not None and step.observation is not None:
                target.merge_from(other=step.observation)
                trace_notes.append(f"case_write:enrich:{target.label}")
            elif step.action == "negate" and target is not None:
                target.status = "negated"
                if step.observation is not None and step.observation.status_source is not None:
                    target.status_source = step.observation.status_source.model_copy(deep=True)
                trace_notes.append(f"case_write:negate:{target.label}")
            elif step.action == "ignore":
                trace_notes.append("case_write:ignore_duplicate")
        return medical_case, trace_notes

    def write_observation_negated(
        self,
        *,
        medical_case: MedicalCase,
        observation_id: str,
    ) -> MedicalCase:
        target = self._find_target_observation(medical_case=medical_case, observation_id=observation_id)
        if target is None:
            return medical_case
        target.status = "negated"
        return medical_case

    def write_person_relation(
        self,
        *,
        medical_case: MedicalCase,
        person_update: Person | None,
    ) -> MedicalCase:
        self._merge_person(target=medical_case.person, update=person_update)
        # Propagate to observations that still have "unclear" person_ref so the
        # observation-level person_ref_missing rule doesn't re-fire after the
        # case-level subject clarification has been answered.
        if person_update is not None and person_update.relation not in (None, "", "unclear"):
            for obs in medical_case.observations:
                if obs.person_ref == "unclear":
                    obs.person_ref = person_update.relation
        return medical_case

    def write_followup_enrichment(
        self,
        *,
        medical_case: MedicalCase,
        observation_id: str,
        patch: ObservationPatch,
    ) -> MedicalCase:
        target = self._find_target_observation(medical_case=medical_case, observation_id=observation_id)
        if target is None or not patch.has_values():
            return medical_case
        if patch.person_ref not in (None, "", "unclear"):
            target.person_ref = patch.person_ref
            if patch.person_ref_source is not None:
                target.person_ref_source = patch.person_ref_source.model_copy(deep=True)
        self._write_optional_field(
            target=target,
            field_name="onset",
            source_field_name="onset_source",
            value=patch.onset,
            source=patch.onset_source,
        )
        self._write_optional_field(
            target=target,
            field_name="body_site",
            source_field_name="body_site_source",
            value=patch.body_site,
            source=patch.body_site_source,
        )
        self._write_optional_field(
            target=target,
            field_name="severity",
            source_field_name="severity_source",
            value=patch.severity,
            source=patch.severity_source,
        )
        if patch.description not in (None, ""):
            target.description = patch.description
            if patch.description_source is not None:
                target.description_sources = [patch.description_source.model_copy(deep=True)]
        return medical_case

    def write_topic(
        self,
        *,
        medical_case: MedicalCase,
        label: str | None = None,
        description: str | None = None,
    ) -> MedicalCase:
        if medical_case.topic is None:
            medical_case.topic = Topic()
        if label not in (None, ""):
            medical_case.topic.label = label
        if description not in (None, ""):
            medical_case.topic.description = description
        return medical_case

    @staticmethod
    def _merge_person(*, target: Person, update: Person | None) -> list[str]:
        if update is None:
            return []
        changed_keys: list[str] = []
        if update.relation not in (None, "", "unclear"):
            target.relation = update.relation
            target.relation_source = (
                update.relation_source.model_copy(deep=True)
                if update.relation_source is not None
                else None
            )
            changed_keys.append(f"relation:{update.relation}")
        if update.age is not None:
            target.age = update.age
            target.age_source = (
                update.age_source.model_copy(deep=True)
                if update.age_source is not None
                else None
            )
            changed_keys.append("age")
        if update.sex not in (None, ""):
            target.sex = update.sex
            target.sex_source = (
                update.sex_source.model_copy(deep=True)
                if update.sex_source is not None
                else None
            )
            changed_keys.append(f"sex:{update.sex}")
        if update.pregnancy_status is not None:
            target.pregnancy_status = update.pregnancy_status
            changed_keys.append(f"pregnancy_status:{update.pregnancy_status}")
        return changed_keys

    @staticmethod
    def _find_target_observation(
        *,
        medical_case: MedicalCase,
        observation_id: str,
    ):
        return next(
            (
                observation
                for observation in medical_case.observations
                if observation.observation_id == observation_id
            ),
            None,
        )

    @staticmethod
    def _write_optional_field(
        *,
        target,
        field_name: str,
        source_field_name: str,
        value: object,
        source,
    ) -> None:
        if value in (None, "", []):
            return
        setattr(target, field_name, value)
        if source is not None:
            setattr(target, source_field_name, source.model_copy(deep=True))
