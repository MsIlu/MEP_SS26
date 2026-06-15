from dataclasses import dataclass

from careena_pipeline.state.module_registry import (
    RequirementRef,
)
from careena_pipeline.models import AssessmentReadiness, DialogueState, MedicalCase, MessageUpdate
from careena_pipeline.planning.requirement_state import (
    build_requirement_state,
    confidence_gaps_for_requirements,
    has_mixed_subject_signal,
    requirement_keys,
)


class AssessmentReadinessEvaluator:
    """
    Evaluates whether the current case state is informationally sufficient.

    This layer should answer readiness questions, not own the final next-step
    decision.
    """

    def evaluate(
        self,
        case: MedicalCase,
        *,
        dialogue_state: DialogueState | None = None,
        message_update: MessageUpdate | None = None,
    ) -> AssessmentReadiness:
        case.ensure_primary_problem()
        facts = _collect_readiness_facts(
            case=case,
            dialogue_state=dialogue_state,
            message_update=message_update,
        )

        if not facts.has_medical_problem:
            return _blocked(["main_complaint"], reason_tags=["no_main_medical_problem"])

        if facts.concern_only_case:
            if facts.blocking_requirements:
                return _blocked(
                    facts.blocking_requirements,
                    disambiguation_needed=facts.disambiguation_needed,
                    reason_tags=["missing_subject"],
                )
            return _ready(
                confirmation_needed=facts.confirmation_needed,
                reason_tags=["low_acuity_concern"],
            )

        if facts.blocking_requirements:
            return _blocked(
                facts.blocking_requirements,
                disambiguation_needed=facts.disambiguation_needed,
            )

        return _ready(
            confirmation_needed=facts.confirmation_needed,
            reason_tags=["minimum_information_present"],
        )


@dataclass
class _ReadinessFacts:
    has_medical_problem: bool
    concern_only_case: bool
    blocking_requirements: list[RequirementRef]
    disambiguation_needed: bool
    confirmation_needed: bool


def _collect_readiness_facts(
    *,
    case: MedicalCase,
    dialogue_state: DialogueState | None,
    message_update: MessageUpdate | None,
) -> _ReadinessFacts:
    symptoms = _focused_problem_observations(
        case=case,
        dialogue_state=dialogue_state,
        types=("symptom",),
    )
    injuries = _focused_problem_observations(
        case=case,
        dialogue_state=dialogue_state,
        types=("injury",),
    )
    diagnoses = _focused_problem_observations(
        case=case,
        dialogue_state=dialogue_state,
        types=("diagnosis",),
    )
    measurements = _focused_problem_observations(
        case=case,
        dialogue_state=dialogue_state,
        types=("measurement",),
        include_negated=True,
    )
    concerns = _focused_problem_observations(
        case=case,
        dialogue_state=dialogue_state,
        types=("concern",),
        include_negated=True,
    )
    complaint_observations = symptoms + injuries + measurements + concerns

    requirement_state = build_requirement_state(
        case=case,
        dialogue_state=dialogue_state,
        message_update=message_update,
    )

    return _ReadinessFacts(
        has_medical_problem=bool(complaint_observations or diagnoses),
        concern_only_case=bool(
            concerns and not symptoms and not injuries and not measurements and not diagnoses
        ),
        blocking_requirements=requirement_state.blocking_requirements,
        disambiguation_needed=has_mixed_subject_signal(case),
        confirmation_needed=_confirmation_needed(
            dialogue_state=dialogue_state,
            message_update=message_update,
        ),
    )


def _blocked(
    blocking_requirements: list[RequirementRef | dict | str],
    *,
    disambiguation_needed: bool = False,
    reason_tags: list[str] | None = None,
) -> AssessmentReadiness:
    missing_information = requirement_keys(blocking_requirements)
    return AssessmentReadiness(
        ready=False,
        missing_information=missing_information,
        reason_tags=reason_tags or ["missing_information"],
        blocking_requirements=missing_information,
        confidence_gaps=confidence_gaps_for_requirements(blocking_requirements),
        disambiguation_needed=disambiguation_needed,
    )


def _ready(
    *,
    confirmation_needed: bool,
    reason_tags: list[str],
) -> AssessmentReadiness:
    return AssessmentReadiness(
        ready=True,
        missing_information=[],
        reason_tags=reason_tags,
        blocking_requirements=[],
        confirmation_needed=confirmation_needed,
    )


def _confirmation_needed(
    *,
    dialogue_state: DialogueState | None,
    message_update: MessageUpdate | None,
) -> bool:
    # Confirmation is currently not an active chat product path.
    # Keep the field in the contract for compatibility, but do not let a
    # dormant state flag steer readiness until the confirmation workflow is
    # defined end-to-end again.
    return False


def _focused_problem_observation(
    *,
    case: MedicalCase,
    dialogue_state: DialogueState | None,
    include_negated: bool = True,
):
    focus_id = (
        dialogue_state.focus_observation_id
        if dialogue_state is not None and dialogue_state.focus_observation_id is not None
        else case.primary_problem_id
    )
    if focus_id is None:
        return None

    for observation in case.active_observations(include_negated=include_negated):
        if observation.id == focus_id:
            return observation
    return None


def _focused_problem_observations(
    *,
    case: MedicalCase,
    dialogue_state: DialogueState | None,
    types: tuple[str, ...],
    include_negated: bool = False,
):
    focused = _focused_problem_observation(
        case=case,
        dialogue_state=dialogue_state,
        include_negated=include_negated,
    )
    if focused is not None and focused.type in set(types):
        return [focused]

    return case.observations_of_type(
        *types,
        include_negated=include_negated,
    )
