from careena_pipeline.state.module_registry import (
    RequirementRef,
    followup_slot_for_requirement,
    infer_active_modules,
    parse_requirements,
    requirement_ref,
    requirement_strings,
    required_fields_for_modules,
)
from careena_pipeline.models import AssessmentReadiness, DialogueState, MedicalCase, MessageUpdate
from careena_pipeline.pipeline_rules import FOLLOWUP_QUESTIONS, question_for_slot


class AssessmentReadinessEvaluator:
    """
    Checks whether the case has enough concrete information for a first
    recommendation or whether Careena should ask one focused follow-up.
    """

    def evaluate(
        self,
        case: MedicalCase,
        *,
        dialogue_state: DialogueState | None = None,
        message_update: MessageUpdate | None = None,
    ) -> AssessmentReadiness:
        case.ensure_primary_problem()

        symptoms = case.observations_of_type("symptom")
        injuries = case.observations_of_type("injury")
        diagnoses = case.observations_of_type("diagnosis")
        measurements = case.observations_of_type("measurement", include_negated=True)
        concerns = case.observations_of_type("concern", include_negated=True)
        complaint_observations = symptoms + injuries + measurements + concerns

        if not complaint_observations and not diagnoses:
            return _blocked(["main_complaint"], reason_tags=["no_main_medical_problem"])

        active_modules = _active_modules(
            case=case,
            dialogue_state=dialogue_state,
            message_update=message_update,
        )
        required_fields = _required_fields(
            case=case,
            active_modules=active_modules,
            message_update=message_update,
        )
        resolved_fields = _resolved_fields(
            case=case,
            message_update=message_update,
        )
        blocking_requirements: list[RequirementRef] = [
            field
            for field in required_fields
            if field.key not in resolved_fields
        ]
        disambiguation_needed = _has_mixed_subject_signal(case)

        if disambiguation_needed or case.subject.relation == "unknown":
            blocking_requirements.append(
                requirement_ref("subject", "subject_relation")
            )

        if concerns and not symptoms and not injuries and not measurements:
            if blocking_requirements:
                return _blocked(
                    blocking_requirements,
                    disambiguation_needed=disambiguation_needed,
                    reason_tags=["missing_subject"],
                )
            return _ready(
                confirmation_needed=_confirmation_needed(
                    dialogue_state=dialogue_state,
                    message_update=message_update,
                ),
                reason_tags=["low_acuity_concern"],
            )

        if blocking_requirements:
            return _blocked(
                blocking_requirements,
                disambiguation_needed=disambiguation_needed,
            )

        return _ready(
            confirmation_needed=_confirmation_needed(
                dialogue_state=dialogue_state,
                message_update=message_update,
            ),
            reason_tags=["minimum_information_present"],
        )


def _blocked(
    blocking_requirements: list[RequirementRef | dict | str],
    *,
    disambiguation_needed: bool = False,
    reason_tags: list[str] | None = None,
) -> AssessmentReadiness:
    missing_information = requirement_strings(blocking_requirements)
    return AssessmentReadiness(
        ready=False,
        missing_information=missing_information,
        next_question=_question_for(missing_information[0]),
        reason_tags=reason_tags or ["missing_information"],
        blocking_requirements=missing_information,
        confidence_gaps=[
            item
            for item in missing_information
            if item in {
                "symptom.duration_or_onset",
                "injury.duration_or_onset",
                "injury.injury_context",
                "symptom.severity",
                "injury.severity",
                "injury.functional_limitation",
            }
        ],
        disambiguation_needed=disambiguation_needed,
        recommended_modules=_recommended_modules(
            missing_information=missing_information,
            disambiguation_needed=disambiguation_needed,
            ready=False,
        ),
    )


def _ready(
    *,
    confirmation_needed: bool,
    reason_tags: list[str],
) -> AssessmentReadiness:
    return AssessmentReadiness(
        ready=True,
        missing_information=[],
        next_question=None,
        reason_tags=reason_tags,
        blocking_requirements=[],
        confirmation_needed=confirmation_needed,
        recommended_modules=_recommended_modules(
            missing_information=[],
            disambiguation_needed=False,
            ready=True,
        ),
    )


def _question_for(slot: RequirementRef | dict | str) -> str:
    normalized = followup_slot_for_requirement(slot) or slot
    return FOLLOWUP_QUESTIONS.get(normalized, question_for_slot(normalized))


def _confirmation_needed(
    *,
    dialogue_state: DialogueState | None,
    message_update: MessageUpdate | None,
) -> bool:
    if message_update is not None and message_update.message_role in {"confirmation", "correction"}:
        return False
    return bool(dialogue_state and dialogue_state.awaiting_confirmation)


def _needs_severity(symptoms, injuries) -> bool:
    if injuries:
        return True
    return any(_looks_like_pain(observation) for observation in symptoms)


def _needs_functional_limitation(injuries) -> bool:
    return any(
        observation.severity is not None and observation.severity >= 7
        or _is_lower_body_injury(observation)
        for observation in injuries
    )


def _has_mixed_subject_signal(case: MedicalCase) -> bool:
    refs = {
        observation.subject_ref
        for observation in case.observations
        if observation.subject_ref and observation.subject_ref != "unknown"
    }
    return len(refs) > 1


def _looks_like_pain(observation) -> bool:
    text = " ".join(
        value
        for value in (
            observation.concept or "",
            observation.label or "",
            observation.display_label or "",
            observation.source_span or "",
        )
        if value
    ).lower()
    return "pain" in text or "schmerz" in text or "weh" in text


def _is_lower_body_injury(observation) -> bool:
    text = " ".join(
        value
        for value in (
            observation.body_site or "",
            observation.label or "",
            observation.display_label or "",
            observation.source_span or "",
            observation.concept or "",
        )
        if value
    ).lower()
    return any(
        marker in text
        for marker in (
            "huefte",
            "hufte",
            "hip",
            "bein",
            "leg",
            "knie",
            "knee",
            "fuss",
            "foot",
            "sprunggelenk",
            "ankle",
        )
    )


def _recommended_modules(
    *,
    missing_information: list[str],
    disambiguation_needed: bool,
    ready: bool,
) -> list[str]:
    modules: list[str] = []
    if disambiguation_needed:
        modules.append("topic_disambiguation")
    if missing_information:
        modules.extend(["requirement_resolution", "single_followup_generation"])
    if ready:
        modules.extend(["recommendation_readiness", "routing_recommendation"])

    seen: set[str] = set()
    return [module for module in modules if not (module in seen or seen.add(module))]


def _active_modules(
    *,
    case: MedicalCase,
    dialogue_state: DialogueState | None,
    message_update: MessageUpdate | None,
) -> list[str]:
    modules = list(dialogue_state.active_modules) if dialogue_state is not None else []
    if message_update is not None and message_update.active_modules:
        modules = list(message_update.active_modules)
    if modules:
        return modules
    return infer_active_modules(
        has_subject_update=case.subject.relation != "unknown" or case.subject.age is not None,
        observation_types=[observation.type for observation in case.observations],
    )


def _required_fields(
    *,
    case: MedicalCase,
    active_modules: list[str],
    message_update: MessageUpdate | None,
) -> list[RequirementRef]:
    fields = list(message_update.required_fields) if message_update is not None else []
    if not fields:
        fields = required_fields_for_modules(active_modules)
    if case.subject.age is None and "injury" in active_modules:
        fields.append(requirement_ref("subject", "age"))
    if _needs_severity(case.observations_of_type("symptom"), case.observations_of_type("injury")):
        if "injury" in active_modules:
            fields.append(requirement_ref("injury", "severity"))
        elif "symptom" in active_modules:
            fields.append(requirement_ref("symptom", "severity"))
    if _needs_functional_limitation(case.observations_of_type("injury")):
        fields.append(requirement_ref("injury", "functional_limitation"))
    return parse_requirements(fields)


def _resolved_fields(
    *,
    case: MedicalCase,
    message_update: MessageUpdate | None,
) -> dict[str, RequirementRef]:
    resolved = {
        item.key: item
        for item in parse_requirements(
            message_update.resolved_fields if message_update is not None else []
        )
    }
    if case.subject.relation != "unknown":
        item = requirement_ref("subject", "subject_relation")
        resolved[item.key] = item
    if case.subject.age is not None:
        item = requirement_ref("subject", "age")
        resolved[item.key] = item
    for observation in case.observations_of_type("symptom", "injury", include_negated=True):
        if observation.temporality:
            item = requirement_ref(observation.type, "duration_or_onset")
            resolved[item.key] = item
        if observation.body_site:
            item = requirement_ref(observation.type, "body_site")
            resolved[item.key] = item
        if observation.severity is not None:
            item = requirement_ref(observation.type, "severity")
            resolved[item.key] = item
        if observation.type == "symptom" and observation.course:
            item = requirement_ref(observation.type, "course")
            resolved[item.key] = item
        if observation.type == "injury" and observation.details.get("context"):
            item = requirement_ref("injury", "injury_context")
            resolved[item.key] = item
        if observation.type == "injury" and observation.details.get("functional_limitation"):
            item = requirement_ref("injury", "functional_limitation")
            resolved[item.key] = item
    for observation in case.observations_of_type("measurement", include_negated=True):
        if observation.measurement.get("kind"):
            item = requirement_ref("measurement", "kind")
            resolved[item.key] = item
        if observation.measurement:
            item = requirement_ref("measurement", "value")
            resolved[item.key] = item
    for observation in case.observations_of_type("medication", include_negated=True):
        if observation.label or observation.concept:
            item = requirement_ref("medication", "name")
            resolved[item.key] = item
        if observation.details:
            item = requirement_ref("medication", "use_context")
            resolved[item.key] = item
    for observation in case.observations_of_type("risk_factor", include_negated=True):
        if observation.label or observation.concept:
            item = requirement_ref("risk_factor", "kind")
            resolved[item.key] = item
    for observation in case.observations_of_type("concern", include_negated=True):
        if observation.label or observation.display_label:
            item = requirement_ref("concern", "main_concern")
            resolved[item.key] = item
    return resolved
