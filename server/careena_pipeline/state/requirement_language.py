from careena_pipeline.state.module_registry import MODULE_REGISTRY, RequirementRef


LEGACY_SLOT_ALIASES: dict[str, tuple[str, str]] = {
    "main_complaint": ("case", "main_complaint"),
    "subject": ("subject", "subject_relation"),
    "subject_age": ("subject", "age"),
    "duration_or_onset": ("symptom", "duration_or_onset"),
    "injury_context": ("injury", "injury_context"),
    "severity": ("symptom", "severity"),
    "functional_limitation": ("injury", "functional_limitation"),
}


def requirement_ref(module: str, field: str) -> RequirementRef:
    return RequirementRef(module=module, field=field)


def parse_requirement(
    value: RequirementRef | dict | str | None,
) -> RequirementRef | None:
    if value is None:
        return None
    if isinstance(value, RequirementRef):
        return value
    if isinstance(value, dict):
        module = value.get("module")
        field = value.get("field")
        if not module or not field:
            return None
        try:
            return RequirementRef(module=str(module), field=str(field))
        except ValueError:
            return None
    if not isinstance(value, str):
        return None
    if value in LEGACY_SLOT_ALIASES:
        module, field = LEGACY_SLOT_ALIASES[value]
        return RequirementRef(module=module, field=field)
    if "." in value:
        module, field = value.split(".", 1)
        try:
            return RequirementRef(module=module, field=field)
        except ValueError:
            return None
    if value == "main_complaint":
        return RequirementRef(module="case", field="main_complaint")
    return None


def parse_requirements(
    values: list[RequirementRef | dict | str] | tuple[RequirementRef | dict | str, ...] | None,
) -> list[RequirementRef]:
    if not values:
        return []
    seen: set[str] = set()
    result: list[RequirementRef] = []
    for value in values:
        ref = parse_requirement(value)
        if ref is None or ref.key in seen:
            continue
        seen.add(ref.key)
        result.append(ref)
    return result


def requirement_to_string(value: RequirementRef | dict | str | None) -> str | None:
    ref = parse_requirement(value)
    return ref.key if ref is not None else None


def requirement_strings(
    values: list[RequirementRef | dict | str] | tuple[RequirementRef | dict | str, ...] | None,
) -> list[str]:
    return [item.key for item in parse_requirements(values)]


def followup_slot_for_requirement(
    value: RequirementRef | dict | str | None,
) -> str | None:
    ref = parse_requirement(value)
    if ref is None:
        return None
    module_def = MODULE_REGISTRY[ref.module]
    for item in module_def.requirements:
        if item.field == ref.field:
            return item.followup_slot or ref.key
    return ref.key
