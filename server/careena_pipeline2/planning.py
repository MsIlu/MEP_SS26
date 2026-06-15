from __future__ import annotations

from dataclasses import dataclass

from careena_pipeline2.models import AssessmentReadiness, DialogueState, MedicalCase
from careena_pipeline2.text import normalize_text, question_for_requirement


@dataclass
class PlanningDecision:
    action: str
    readiness: AssessmentReadiness
    question: str | None = None


class DecisionPlanner:
    def decide(self, case: MedicalCase, state: DialogueState) -> PlanningDecision:
        case.ensure_primary_problem()
        missing_requirement = self._first_missing_requirement(case, state)
        if missing_requirement is not None:
            state.pending_requirement = missing_requirement
            state.awaiting_confirmation = False
            state.pending_confirmation_observation_ids = []
            state.pending_confirmation_subject = False
            readiness = AssessmentReadiness(
                ready=False,
                missing_requirements=[missing_requirement],
                reason_tags=["missing_information"],
            )
            return PlanningDecision(
                action="ask_followup",
                readiness=readiness,
                question=question_for_requirement(missing_requirement),
            )

        unconfirmed_ids = [observation.id for observation in case.unconfirmed_observations()]
        subject_needs_confirmation = case.subject.needs_confirmation()
        if unconfirmed_ids or subject_needs_confirmation:
            state.pending_requirement = None
            state.awaiting_confirmation = True
            state.pending_confirmation_observation_ids = unconfirmed_ids[:6]
            state.pending_confirmation_subject = subject_needs_confirmation
            readiness = AssessmentReadiness(
                ready=False,
                unconfirmed_observation_ids=unconfirmed_ids[:6],
                subject_needs_confirmation=subject_needs_confirmation,
                reason_tags=["awaiting_confirmation"],
            )
            return PlanningDecision(action="confirm_case", readiness=readiness)

        confirmed_case = case.clone_confirmed_case()
        if not confirmed_case.problem_observations(source="confirmed"):
            state.pending_requirement = "main_complaint"
            readiness = AssessmentReadiness(
                ready=False,
                missing_requirements=["main_complaint"],
                reason_tags=["no_medical_problem"],
            )
            return PlanningDecision(
                action="ask_followup",
                readiness=readiness,
                question=question_for_requirement("main_complaint"),
            )

        state.pending_requirement = None
        state.awaiting_confirmation = False
        state.pending_confirmation_observation_ids = []
        state.pending_confirmation_subject = False
        readiness = AssessmentReadiness(
            ready=True,
            reason_tags=["confirmed_case_ready"],
        )
        return PlanningDecision(action="recommend", readiness=readiness)

    def _first_missing_requirement(self, case: MedicalCase, state: DialogueState) -> str | None:
        if not case.problem_observations():
            return "main_complaint"

        if case.subject.relation == "unknown":
            return "subject.subject_relation"

        focus = case.primary_observation()
        if focus is None:
            return "main_complaint"

        if focus.type in {"symptom", "injury"} and not focus.requirement_value("duration_or_onset"):
            return f"{focus.type}.duration_or_onset"

        if focus.type == "injury" and not focus.requirement_value("injury_context"):
            return "injury.injury_context"

        if focus.type == "measurement" and not focus.requirement_value("kind"):
            return "measurement.kind"

        if focus.type == "measurement" and focus.requirement_value("value") is None:
            return "measurement.value"

        if (
            focus.type in {"symptom", "injury"}
            and state.recommendation_requested
            and focus.requirement_value("severity") is None
        ):
            return f"{focus.type}.severity"

        if (
            focus.type == "injury"
            and _is_lower_body_focus(focus)
            and focus.requirement_value("severity") is not None
            and focus.requirement_value("severity") >= 7
            and not focus.requirement_value("functional_limitation")
        ):
            return "injury.functional_limitation"

        return None


def _is_lower_body_focus(observation) -> bool:
    text = normalize_text(
        " ".join(
            value
            for value in [
                observation.label,
                observation.display_label or "",
                observation.concept or "",
                observation.runtime_value("body_site") or "",
            ]
            if value
        )
    )
    return any(
        marker in text
        for marker in ("hufte", "huefte", "bein", "knie", "fuss", "sprunggelenk")
    )
