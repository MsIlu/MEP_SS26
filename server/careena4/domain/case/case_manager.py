from careena4.domain.case._case_reader import _CaseReader
from careena4.domain.case._case_write_planner import _CaseWritePlanner
from careena4.domain.case._case_writer import _CaseWriter
from careena4.models.domain import CaseExtension, CaseTopic, MedicalCase
from careena4.models.turn import CaseWritePlan, ExtractionClaims


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
        claims: ExtractionClaims,
        case_topic: CaseTopic | None,
    ) -> tuple[MedicalCase, list[str]]:
        topic_id = self.case_reader.read_topic_id(case_topic=case_topic)
        existing_observations = self.case_reader.read_observations(medical_case=medical_case)
        plan = self.case_write_planner.build_write_plan(
            existing_observations=existing_observations,
            claims=claims,
            topic_id=topic_id,
        )
        return self.apply_write_plan(medical_case=medical_case, plan=plan)

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

    def update_person_relation(
        self,
        *,
        medical_case: MedicalCase,
        relation: object,
        case_topic: CaseTopic | None = None,
    ) -> tuple[MedicalCase, CaseTopic | None]:
        return self.case_writer.write_person_relation(
            medical_case=medical_case,
            relation=relation,
            case_topic=case_topic,
        )

    def enrich_observation_from_followup(
        self,
        *,
        medical_case: MedicalCase,
        observation_id: str,
        attributes: dict[str, object],
    ) -> MedicalCase:
        return self.case_writer.write_followup_enrichment(
            medical_case=medical_case,
            observation_id=observation_id,
            attributes=attributes,
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
