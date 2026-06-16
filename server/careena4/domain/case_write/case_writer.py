from careena4.models.domain import MedicalCase
from careena4.models.turn import CaseWritePlan


class CaseWriter:
    def apply(self, *, medical_case: MedicalCase, plan: CaseWritePlan) -> tuple[MedicalCase, list[str]]:
        trace_notes = list(plan.trace_notes)
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
