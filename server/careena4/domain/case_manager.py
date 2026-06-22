from careena4.domain.case_write.case_write_planner import CaseWritePlanner
from careena4.domain.case_write.case_writer import CaseWriter
from careena4.models.domain import CaseTopic, MedicalCase, Observation
from careena4.models.turn import CaseWritePlan, ExtractionClaims


class CaseManager:
    """
    Minimal access boundary for MedicalCase mutations.

    This first cut intentionally keeps existing write semantics and
    mainly removes direct case mutations from orchestration code.
    """

    def __init__(
        self,
        *,
        case_write_planner: CaseWritePlanner | None = None,
        case_writer: CaseWriter | None = None,
    ) -> None:
        self.case_write_planner = case_write_planner or CaseWritePlanner()
        self.case_writer = case_writer or CaseWriter()

    def apply_claims(
        self,
        *,
        medical_case: MedicalCase,
        claims: ExtractionClaims,
        case_topic: CaseTopic | None,
    ) -> tuple[MedicalCase, list[str]]:
        topic_id = case_topic.topic_id if case_topic is not None else None
        if topic_id is not None:
            medical_case.topic_id = topic_id
        plan = self.case_write_planner.build(
            medical_case=medical_case,
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
        return self.case_writer.apply(medical_case=medical_case, plan=plan)

    def negate_observation(
        self,
        *,
        medical_case: MedicalCase,
        observation_id: str,
    ) -> MedicalCase:
        observation = self._find_observation(
            medical_case=medical_case,
            observation_id=observation_id,
        )
        if observation is None:
            return medical_case
        observation.negated = True
        observation.status = "negated"
        return medical_case

    def update_person_relation(
        self,
        *,
        medical_case: MedicalCase,
        relation: object,
        case_topic: CaseTopic | None = None,
    ) -> tuple[MedicalCase, CaseTopic | None]:
        medical_case.subject.relation = relation  # type: ignore[assignment]
        if case_topic is not None:
            case_topic.subject_scope = medical_case.subject.relation
        return medical_case, case_topic

    def enrich_observation_from_followup(
        self,
        *,
        medical_case: MedicalCase,
        observation_id: str,
        attributes: dict[str, object],
    ) -> MedicalCase:
        observation = self._find_observation(
            medical_case=medical_case,
            observation_id=observation_id,
        )
        if observation is None:
            return medical_case
        observation.attributes.update(attributes)
        if observation.status == "reported":
            observation.status = "enriched"
        return medical_case

    @staticmethod
    def _find_observation(
        *,
        medical_case: MedicalCase,
        observation_id: str,
    ) -> Observation | None:
        return next(
            (
                observation
                for observation in medical_case.observations
                if observation.observation_id == observation_id
            ),
            None,
        )
