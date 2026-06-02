"""
Transitional requirement grammar for Careena.

This module currently centralizes:
- known planner modules
- their requirement fields
- follow-up slot aliases
- lightweight inference helpers

It is intentionally treated as a working grammar layer, not as the medical
domain model itself. The surrounding architecture should be free to replace or
redistribute parts of this file later without redefining the core Case/State
truths.
"""

from dataclasses import dataclass
from typing import Literal

from pydantic import model_validator

from careena_pipeline.models.common.base import PipelineModel


ModuleName = Literal[
    "case",
    "subject",
    "symptom",
    "injury",
    "measurement",
    "medication",
    "risk_factor",
    "concern",
    "administrative",
]


@dataclass(frozen=True)
class RequirementDef:
    field: str
    followup_slot: str | None = None
    required: bool = True


@dataclass(frozen=True)
class ModuleDef:
    name: ModuleName
    requirements: tuple[RequirementDef, ...]


class RequirementRef(PipelineModel):
    module: str
    field: str

    @model_validator(mode="after")
    def validate_known_requirement(self):
        module_def = MODULE_REGISTRY.get(self.module)
        if module_def is None:
            raise ValueError(f"Unknown requirement module: {self.module}")
        allowed_fields = {item.field for item in module_def.requirements}
        if self.field not in allowed_fields:
            raise ValueError(
                f"Unknown requirement field '{self.field}' for module '{self.module}'"
            )
        return self

    @property
    def key(self) -> str:
        if self.module == "case":
            return self.field
        return f"{self.module}.{self.field}"


MODULE_REGISTRY: dict[ModuleName, ModuleDef] = {
    "case": ModuleDef(
        name="case",
        requirements=(
            RequirementDef("main_complaint", followup_slot="main_complaint"),
        ),
    ),
    "subject": ModuleDef(
        name="subject",
        requirements=(
            RequirementDef("subject_relation", followup_slot="subject"),
            RequirementDef("age", followup_slot="subject_age", required=False),
        ),
    ),
    "symptom": ModuleDef(
        name="symptom",
        requirements=(
            RequirementDef("duration_or_onset", followup_slot="duration_or_onset"),
            RequirementDef("body_site", required=False),
            RequirementDef("severity", followup_slot="severity", required=False),
            RequirementDef("course", required=False),
        ),
    ),
    "injury": ModuleDef(
        name="injury",
        requirements=(
            RequirementDef("duration_or_onset", followup_slot="duration_or_onset"),
            RequirementDef("body_site", required=False),
            RequirementDef("injury_context", followup_slot="injury_context"),
            RequirementDef(
                "functional_limitation",
                followup_slot="functional_limitation",
                required=False,
            ),
            RequirementDef("severity", followup_slot="severity", required=False),
        ),
    ),
    "measurement": ModuleDef(
        name="measurement",
        requirements=(
            RequirementDef("kind"),
            RequirementDef("value"),
        ),
    ),
    "medication": ModuleDef(
        name="medication",
        requirements=(
            RequirementDef("name"),
            RequirementDef("use_context", required=False),
        ),
    ),
    "risk_factor": ModuleDef(
        name="risk_factor",
        requirements=(RequirementDef("kind"),),
    ),
    "concern": ModuleDef(
        name="concern",
        requirements=(RequirementDef("main_concern"),),
    ),
    "administrative": ModuleDef(
        name="administrative",
        requirements=(),
    ),
}


OBSERVATION_TYPE_TO_MODULE: dict[str, ModuleName] = {
    "symptom": "symptom",
    "injury": "injury",
    "measurement": "measurement",
    "medication": "medication",
    "risk_factor": "risk_factor",
    "concern": "concern",
    "administrative": "administrative",
}

def normalize_modules(
    values: list[str] | tuple[str, ...] | None,
) -> list[ModuleName]:
    if not values:
        return []
    seen: set[str] = set()
    normalized: list[ModuleName] = []
    for value in values:
        if value not in MODULE_REGISTRY or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def infer_active_modules(
    *,
    has_subject_update: bool = False,
    observation_types: list[str] | None = None,
) -> list[ModuleName]:
    modules: list[ModuleName] = []
    if has_subject_update:
        modules.append("subject")
    for observation_type in observation_types or []:
        module = OBSERVATION_TYPE_TO_MODULE.get(observation_type)
        if module and module not in modules:
            modules.append(module)
    return modules


def required_fields_for_modules(
    modules: list[str] | tuple[str, ...] | None,
) -> list[RequirementRef]:
    seen: set[str] = set()
    result: list[RequirementRef] = []
    for module in normalize_modules(modules):
        for item in MODULE_REGISTRY[module].requirements:
            if not item.required:
                continue
            ref = RequirementRef(module=module, field=item.field)
            if ref.key in seen:
                continue
            seen.add(ref.key)
            result.append(ref)
    return result
