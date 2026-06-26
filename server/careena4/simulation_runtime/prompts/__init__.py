from careena4.simulation_runtime.prompts.personas import (
    DEFAULT_PARTICIPANT_PERSONA_PROMPT,
    DIRECT_ADULT_PERSONA_PROMPT,
    MOTHER_PERSONA_PROMPT,
    PERSONA_PROMPTS,
)
from careena4.simulation_runtime.prompts.scenarios import (
    DEFAULT_SCENARIO_PROMPT,
    HIGH_BLOOD_PRESSURE_SCENARIO,
    HIP_FALL_SCENARIO,
    MOTHER_AND_CHILD_SCENARIO,
    SCENARIO_PROMPTS,
)


def build_participant_prompt(participant_prompt: str | None = None) -> str:
    extra_prompt = (participant_prompt or "").strip()
    if not extra_prompt:
        return DEFAULT_PARTICIPANT_PERSONA_PROMPT.strip()
    return (
        f"{DEFAULT_PARTICIPANT_PERSONA_PROMPT.strip()}\n\n"
        "Zusaetzliche Persona- oder Stilvorgaben fuer diesen Lauf:\n"
        f"{extra_prompt}"
    )


def normalize_scenario_prompt(scenario_prompt: str | None) -> str:
    raw_prompt = scenario_prompt or ""
    normalized = raw_prompt.strip()
    if not normalized:
        return DEFAULT_SCENARIO_PROMPT
    mapped_prompt = SCENARIO_PROMPTS.get(normalized)
    if mapped_prompt is not None:
        return mapped_prompt
    if raw_prompt in SCENARIO_PROMPTS.values():
        return raw_prompt
    return normalized


__all__ = [
    "DEFAULT_PARTICIPANT_PERSONA_PROMPT",
    "DIRECT_ADULT_PERSONA_PROMPT",
    "MOTHER_PERSONA_PROMPT",
    "PERSONA_PROMPTS",
    "DEFAULT_SCENARIO_PROMPT",
    "HIP_FALL_SCENARIO",
    "HIGH_BLOOD_PRESSURE_SCENARIO",
    "MOTHER_AND_CHILD_SCENARIO",
    "SCENARIO_PROMPTS",
    "build_participant_prompt",
    "normalize_scenario_prompt",
]
