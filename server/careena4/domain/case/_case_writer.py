from careena4.models.domain import CaseExtension, CaseTopic, MedicalCase
from careena4.models.turn import CaseWritePlan


class _CaseWriter:
    def write_plan(self, *, medical_case: MedicalCase, plan: CaseWritePlan) -> tuple[MedicalCase, list[str]]:
        trace_notes = list(plan.trace_notes)
        if plan.topic_id_update is not None:
            medical_case.topic_id = plan.topic_id_update
            trace_notes.append(f"case_write:topic_id:{plan.topic_id_update}")
        if plan.subject_update is not None and plan.subject_update.relation != "unclear":
            medical_case.subject = plan.subject_update
            trace_notes.append(f"case_write:subject:{plan.subject_update.relation}")
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
                target.attributes.update(step.observation.attributes)
                if step.observation.subject_ref != "unclear":
                    target.subject_ref = step.observation.subject_ref
                target.status = "enriched"
                trace_notes.append(f"case_write:enrich:{target.label}")
            elif step.action == "negate" and target is not None:
                target.negated = True
                target.status = "negated"
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
        target.negated = True
        target.status = "negated"
        return medical_case

    def write_person_relation(
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

    def write_followup_enrichment(
        self,
        *,
        medical_case: MedicalCase,
        observation_id: str,
        attributes: dict[str, object],
    ) -> MedicalCase:
        target = self._find_target_observation(medical_case=medical_case, observation_id=observation_id)
        if target is None:
            return medical_case
        target.attributes.update(attributes)
        if target.status == "reported":
            target.status = "enriched"
        return medical_case

    @staticmethod
    def write_topic_projection(
        *,
        case_topic: CaseTopic | None,
        extensions: list[CaseExtension],
        current_label: str,
    ) -> CaseTopic | None:
        if case_topic is None:
            return None
        case_topic.extensions = extensions
        case_topic.current_label = current_label
        return case_topic

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
