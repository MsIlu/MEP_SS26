from careena4.domain.case._case_reader import _CaseReader
from careena4.domain.case._case_write_planner import _CaseWritePlanner
from careena4.domain.case._case_writer import _CaseWriter
from careena4.models.domain import CaseExtension, CaseTopic, MedicalCase, Observation, Person, Source, Topic
from careena4.models.turn import (
    CaseWritePlan,
    ExtractedCaseInput,
    ExtractedObservationInput,
    ObservationPatch,
    PersonUpdate,
)


class CaseManager:
    """
    Access boundary for all productive case reads and writes.

    Any productive access to MedicalCase or CaseTopic must run through
    CaseManager and its internal reader/writer layers. Callers outside
    this boundary should not read or mutate case state directly.
    """

    def __init__(
        self,
        *,
        case_reader: _CaseReader | None = None,
        case_write_planner: _CaseWritePlanner | None = None,
        case_writer: _CaseWriter | None = None,
    ) -> None:
        self.case_reader = case_reader or _CaseReader()
        self.case_write_planner = case_write_planner or _CaseWritePlanner()
        self.case_writer = case_writer or _CaseWriter()

    def apply_claims(
        self,
        *,
        medical_case: MedicalCase,
        claims: ExtractedCaseInput,
        case_topic: CaseTopic | None,
    ) -> tuple[MedicalCase, list[str]]:
        existing_observations = self.case_reader.read_observations(medical_case=medical_case)
        plan = self.case_write_planner.build_write_plan(
            existing_observations=existing_observations,
            observations=[self._observation_from_input(observation_input=observation) for observation in claims.observations],
            person_update=self._person_from_case_input(case_input=claims),
        )
        medical_case, trace_notes = self.apply_write_plan(medical_case=medical_case, plan=plan)
        if medical_case.topic is None and claims.topic_signal:
            medical_case.topic = Topic(
                label=claims.topic_signal,
                sources=[claims.topic_source.model_copy(deep=True)] if claims.topic_source is not None else [],
            )
        medical_case = self.sync_legacy_topic_projection(
            medical_case=medical_case,
            case_topic=case_topic,
        )
        return medical_case, trace_notes

    def apply_write_plan(
        self,
        *,
        medical_case: MedicalCase,
        plan: CaseWritePlan,
    ) -> tuple[MedicalCase, list[str]]:
        return self.case_writer.write_plan(medical_case=medical_case, plan=plan)

    def topic_label(self, *, case_topic: CaseTopic | None) -> str | None:
        return self.case_reader.read_topic_label(case_topic=case_topic)

    def topic_tokens(self, *, case_topic: CaseTopic | None) -> set[str]:
        return self.case_reader.read_topic_tokens(case_topic=case_topic)

    def topic_extension_kinds(self, *, case_topic: CaseTopic | None) -> set[str]:
        return self.case_reader.read_topic_extension_kinds(case_topic=case_topic)

    def topic_extensions(self, *, case_topic: CaseTopic | None):
        return self.case_reader.read_topic_extensions(case_topic=case_topic)

    def topic_initial_label(self, *, case_topic: CaseTopic | None) -> str | None:
        return self.case_reader.read_topic_initial_label(case_topic=case_topic)

    def topic_type(self, *, case_topic: CaseTopic | None):
        return self.case_reader.read_topic_type(case_topic=case_topic)

    def observation_label(
        self,
        *,
        medical_case: MedicalCase,
        observation_id: str,
    ) -> str | None:
        return self.case_reader.read_observation_label(
            medical_case=medical_case,
            observation_id=observation_id,
        )

    def has_active_observations(self, *, medical_case: MedicalCase) -> bool:
        return self.case_reader.read_has_active_observations(medical_case=medical_case)

    def has_observations(self, *, medical_case: MedicalCase) -> bool:
        return self.case_reader.read_has_observations(medical_case=medical_case)

    def first_observation_label(self, *, medical_case: MedicalCase | None) -> str | None:
        return self.case_reader.read_first_observation_label(medical_case=medical_case)

    def active_observations(self, *, medical_case: MedicalCase):
        return self.case_reader.read_active_observations(medical_case=medical_case)

    def central_observations(self, *, medical_case: MedicalCase):
        return self.case_reader.read_central_observations(medical_case=medical_case)

    def central_non_negated_observations(self, *, medical_case: MedicalCase):
        return self.case_reader.read_central_non_negated_observations(medical_case=medical_case)

    def person_relation(self, *, medical_case: MedicalCase):
        return self.case_reader.read_person_relation(medical_case=medical_case)

    def negate_observation(
        self,
        *,
        medical_case: MedicalCase,
        observation_id: str,
    ) -> MedicalCase:
        return self.case_writer.write_observation_negated(
            medical_case=medical_case,
            observation_id=observation_id,
        )

    def update_person(
        self,
        *,
        medical_case: MedicalCase,
        person_update: PersonUpdate,
        case_topic: CaseTopic | None = None,
    ) -> tuple[MedicalCase, CaseTopic | None]:
        return self.case_writer.write_person_relation(
            medical_case=medical_case,
            person_update=self._person_from_update(person_update=person_update),
            case_topic=case_topic,
        )

    def enrich_observation_from_followup(
        self,
        *,
        medical_case: MedicalCase,
        observation_id: str,
        patch: ObservationPatch,
    ) -> MedicalCase:
        return self.case_writer.write_followup_enrichment(
            medical_case=medical_case,
            observation_id=observation_id,
            patch=patch,
        )

    def update_topic_projection(
        self,
        *,
        case_topic: CaseTopic | None,
        extensions: list[CaseExtension],
        current_label: str,
    ) -> CaseTopic | None:
        return self.case_writer.write_topic_projection(
            case_topic=case_topic,
            extensions=extensions,
            current_label=current_label,
        )

    def sync_legacy_topic_projection(
        self,
        *,
        medical_case: MedicalCase,
        case_topic: CaseTopic | None,
    ) -> MedicalCase:
        return self.case_writer.write_legacy_topic_projection(
            medical_case=medical_case,
            case_topic=case_topic,
        )

    @staticmethod
    def _person_from_case_input(*, case_input: ExtractedCaseInput) -> Person | None:
        if case_input.person is None:
            return None
        if case_input.person.relation not in {"self", "child", "other", "unclear"}:
            return None
        return Person(
            relation=case_input.person.relation,
            relation_source=CaseManager._copy_source(case_input.person.relation_source),
        )

    @staticmethod
    def _person_from_update(*, person_update: PersonUpdate) -> Person | None:
        if person_update.relation not in {"self", "child", "other", "unclear"}:
            return None
        return Person(
            relation=person_update.relation,
            relation_source=CaseManager._copy_source(person_update.relation_source),
        )

    @staticmethod
    def _observation_from_input(*, observation_input: ExtractedObservationInput) -> Observation:
        return Observation(
            type=observation_input.type,
            label=observation_input.label,
            label_source=CaseManager._copy_source(observation_input.label_source),
            status=observation_input.status,
            status_source=CaseManager._copy_source(observation_input.status_source),
            person_ref=observation_input.person_ref or "unclear",
            person_ref_source=CaseManager._copy_source(observation_input.person_ref_source),
            onset=observation_input.onset,
            onset_source=CaseManager._copy_source(observation_input.onset_source),
            body_site=observation_input.body_site,
            body_site_source=CaseManager._copy_source(observation_input.body_site_source),
            description=observation_input.description,
            description_sources=(
                [observation_input.description_source.model_copy(deep=True)]
                if observation_input.description_source is not None
                else []
            ),
            severity=observation_input.severity,
            severity_source=CaseManager._copy_source(observation_input.severity_source),
        )

    @staticmethod
    def _copy_source(source: Source | None) -> Source | None:
        if source is None:
            return None
        return source.model_copy(deep=True)
