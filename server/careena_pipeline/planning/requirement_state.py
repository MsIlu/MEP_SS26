from dataclasses import dataclass

from careena_pipeline.state.module_registry import (
    RequirementRef,
    infer_active_modules,
    normalize_modules,
    required_fields_for_modules,
)
from careena_pipeline.state.requirement_language import (
    followup_slot_for_requirement,
    parse_requirement,
    parse_requirements,
    requirement_ref,
)
from careena_pipeline.models import DialogueState, MedicalCase, MessageUpdate


CONFIDENCE_GAP_KEYS = {
    "symptom.duration_or_onset",
    "injury.duration_or_onset",
    "injury.injury_context",
    "symptom.severity",
    "injury.severity",
    "injury.functional_limitation",
}


@dataclass
class RequirementState:
    active_modules: list[str]
    required_fields: list[RequirementRef]
    resolved_fields: dict[str, RequirementRef]
    blocking_requirements: list[RequirementRef]
    confidence_gaps: list[str]


@dataclass
class PendingFollowupContext:
    normalized_slot: str | None
    resolved_field: RequirementRef | None
    active_modules: list[str]
    required_fields: list[RequirementRef]


def build_requirement_state(
    *,
    case: MedicalCase,
    dialogue_state: DialogueState | None,
    message_update: MessageUpdate | None,
) -> RequirementState:
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
    )
    blocking_requirements = _blocking_requirements(
        case=case,
        required_fields=required_fields,
        resolved_fields=resolved_fields,
    )
    confidence_gaps = _confidence_gaps(blocking_requirements)
    return RequirementState(
        active_modules=active_modules,
        required_fields=required_fields,
        resolved_fields=resolved_fields,
        blocking_requirements=blocking_requirements,
        confidence_gaps=confidence_gaps,
    )


def confidence_gaps_for_requirements(
    requirements: list[RequirementRef | dict | str],
) -> list[str]:
    return _confidence_gaps(parse_requirements(requirements))


def requirement_key(
    value: RequirementRef | dict | str | None,
) -> str | None:
    item = parse_requirement(value)
    return item.key if item is not None else None


def requirement_keys(
    values: list[RequirementRef | dict | str] | tuple[RequirementRef | dict | str, ...] | None,
) -> list[str]:
    return [item.key for item in parse_requirements(values)]


def merge_requirements(
    existing: list[RequirementRef | dict | str] | tuple[RequirementRef | dict | str, ...] | None,
    additions: list[RequirementRef | dict | str] | tuple[RequirementRef | dict | str, ...] | None,
) -> list[RequirementRef]:
    return parse_requirements(list(existing or []) + list(additions or []))


def remove_requirements(
    values: list[RequirementRef | dict | str] | tuple[RequirementRef | dict | str, ...] | None,
    removals: list[RequirementRef | dict | str] | tuple[RequirementRef | dict | str, ...] | None,
) -> list[RequirementRef]:
    removal_keys = set(requirement_keys(removals))
    return [
        item
        for item in parse_requirements(values)
        if item.key not in removal_keys
    ]


def first_requirement(
    values: list[RequirementRef | dict | str] | tuple[RequirementRef | dict | str, ...] | None,
) -> RequirementRef | None:
    items = parse_requirements(values)
    return items[0] if items else None


def resolve_active_modules(
    *,
    explicit_modules: list[str] | tuple[str, ...] | None,
    has_subject_update: bool = False,
    observation_types: list[str] | None = None,
) -> list[str]:
    modules = normalize_modules(explicit_modules)
    if modules:
        return modules
    return infer_active_modules(
        has_subject_update=has_subject_update,
        observation_types=observation_types,
    )


def resolve_required_fields(
    *,
    explicit_fields: list[RequirementRef | dict | str] | tuple[RequirementRef | dict | str, ...] | None,
    active_modules: list[str],
) -> list[RequirementRef]:
    # Requirement policy should come from the module contract, not from an LLM
    # claiming a case is already "complete enough".
    #
    # We still keep `explicit_fields` in the interface for compatibility with
    # current call sites and logs, but the authoritative field set is derived
    # from the active modules.
    return required_fields_for_modules(active_modules)


def normalized_followup_slot(
    value: str | RequirementRef | None,
) -> str | None:
    return followup_slot_for_requirement(value) or value


def build_pending_followup_context(
    pending_slot: str | RequirementRef | None,
) -> PendingFollowupContext:
    resolved_field = parse_requirement(pending_slot)
    normalized_slot = normalized_followup_slot(pending_slot)
    active_modules = resolve_active_modules(
        explicit_modules=(
            [resolved_field.module]
            if resolved_field is not None and resolved_field.module != "case"
            else None
        ),
        has_subject_update=bool(
            resolved_field is not None and resolved_field.module == "subject"
        ),
        observation_types=None,
    )
    required_fields = (
        [resolved_field]
        if resolved_field is not None
        else resolve_required_fields(
            explicit_fields=None,
            active_modules=active_modules,
        )
    )
    return PendingFollowupContext(
        normalized_slot=normalized_slot,
        resolved_field=resolved_field,
        active_modules=active_modules,
        required_fields=required_fields,
    )


def _confidence_gaps(requirements: list[RequirementRef]) -> list[str]:
    return [
        item.key
        for item in requirements
        if item.key in CONFIDENCE_GAP_KEYS
    ]


def _blocking_requirements(
    *,
    case: MedicalCase,
    required_fields: list[RequirementRef],
    resolved_fields: dict[str, RequirementRef],
) -> list[RequirementRef]:
    blocking_requirements = [
        field
        for field in required_fields
        if field.key not in resolved_fields
    ]
    disambiguation_needed = has_mixed_subject_signal(case)
    if disambiguation_needed or case.subject.relation == "unknown":
        blocking_requirements.append(requirement_ref("subject", "subject_relation"))
    return parse_requirements(blocking_requirements)


def has_mixed_subject_signal(case: MedicalCase) -> bool:
    refs = {
        observation.subject_ref
        for observation in case.observations
        if observation.subject_ref and observation.subject_ref != "unknown"
    }
    return len(refs) > 1


def _active_modules(
    *,
    case: MedicalCase,
    dialogue_state: DialogueState | None,
    message_update: MessageUpdate | None,
) -> list[str]:
    modules = list(dialogue_state.active_modules) if dialogue_state is not None else []
    if message_update is not None and message_update.active_modules:
        modules = list(message_update.active_modules)
    return resolve_active_modules(
        explicit_modules=modules,
        has_subject_update=case.subject.relation != "unknown" or case.subject.age is not None,
        observation_types=[observation.type for observation in case.observations],
    )


def _required_fields(
    *,
    case: MedicalCase,
    active_modules: list[str],
    message_update: MessageUpdate | None,
) -> list[RequirementRef]:
    return resolve_required_fields(
        explicit_fields=(
            list(message_update.required_fields)
            if message_update is not None
            else None
        ),
        active_modules=active_modules,
    )


def _resolved_fields(
    *,
    case: MedicalCase,
) -> dict[str, RequirementRef]:
    # Phase-3 rule: requirement fulfillment should come from information that
    # is visibly anchored in the case, not directly from raw message signals.
    resolved: dict[str, RequirementRef] = {}
    if case.subject.relation != "unknown":
        item = requirement_ref("subject", "subject_relation")
        resolved[item.key] = item
    if case.subject.age is not None:
        item = requirement_ref("subject", "age")
        resolved[item.key] = item
    for observation in case.observations_of_type("symptom", "injury", include_negated=True):
        if observation.requirement_value("duration_or_onset"):
            item = requirement_ref(observation.type, "duration_or_onset")
            resolved[item.key] = item
        if observation.requirement_value("body_site"):
            item = requirement_ref(observation.type, "body_site")
            resolved[item.key] = item
        if observation.requirement_value("severity") is not None:
            item = requirement_ref(observation.type, "severity")
            resolved[item.key] = item
        if observation.type == "symptom" and observation.requirement_value("course"):
            item = requirement_ref(observation.type, "course")
            resolved[item.key] = item
        if observation.type == "injury" and observation.requirement_value("injury_context"):
            item = requirement_ref("injury", "injury_context")
            resolved[item.key] = item
        if observation.type == "injury" and observation.requirement_value("functional_limitation"):
            item = requirement_ref("injury", "functional_limitation")
            resolved[item.key] = item
    for observation in case.observations_of_type("measurement", include_negated=True):
        if observation.requirement_value("kind"):
            item = requirement_ref("measurement", "kind")
            resolved[item.key] = item
        if observation.requirement_value("value"):
            item = requirement_ref("measurement", "value")
            resolved[item.key] = item
    for observation in case.observations_of_type("medication", include_negated=True):
        if observation.requirement_value("name"):
            item = requirement_ref("medication", "name")
            resolved[item.key] = item
        if observation.requirement_value("use_context"):
            item = requirement_ref("medication", "use_context")
            resolved[item.key] = item
    for observation in case.observations_of_type("risk_factor", include_negated=True):
        if observation.requirement_value("kind"):
            item = requirement_ref("risk_factor", "kind")
            resolved[item.key] = item
    for observation in case.observations_of_type("concern", include_negated=True):
        if observation.requirement_value("main_concern"):
            item = requirement_ref("concern", "main_concern")
            resolved[item.key] = item
    return resolved
