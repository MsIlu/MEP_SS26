from careena4.models.domain import MedicalCase, Person, Topic, TopicEntry
from careena4.models.turn import CaseWritePlan, ExtractedTopicEntryInput, ObservationPatch


class _CaseWriter:
    def write_plan(self, *, medical_case: MedicalCase, plan: CaseWritePlan) -> tuple[MedicalCase, list[str]]:
        trace_notes = list(plan.trace_notes)
        if plan.person_update is not None and plan.person_update.relation != "unclear":
            medical_case.person = plan.person_update
            trace_notes.append(f"case_write:person:{plan.person_update.relation}")
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
        if person_update is None:
            return medical_case
        medical_case.person.relation = person_update.relation
        medical_case.person.relation_source = person_update.relation_source
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

    @staticmethod
    def write_topic_entries(
        *,
        medical_case: MedicalCase,
        entries: list[ExtractedTopicEntryInput],
    ) -> MedicalCase:
        if not entries:
            return medical_case
        if medical_case.topic is None:
            medical_case.topic = Topic(label="")
        for entry in entries:
            medical_case.topic.entries.append(
                TopicEntry(
                    topic_part=entry.topic_part,
                    source=entry.source.model_copy(deep=True),
                )
            )
        return medical_case

    @staticmethod
    def write_topic_label(
        *,
        medical_case: MedicalCase,
        label: str,
    ) -> MedicalCase:
        if medical_case.topic is None:
            medical_case.topic = Topic(label=label)
            return medical_case
        medical_case.topic.label = label
        return medical_case

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
