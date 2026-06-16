from careena4.simulation_runtime.models import (
    SimulationRequest,
    SimulationResult,
    SimulationSystemTurn,
    SimulationTranscriptEntry,
)
from careena4.simulation_runtime.prompts import (
    DEFAULT_SCENARIO_PROMPT,
    DIRECT_ADULT_PERSONA_PROMPT,
    PERSONA_PROMPTS,
    SCENARIO_PROMPTS,
    normalize_scenario_prompt,
)
from careena4.simulation_runtime.runner import SimulationRunner


def normalized_simulation_request(request: SimulationRequest) -> SimulationRequest:
    if request.participant_llm_mode is None:
        request.participant_llm_mode = "env"
    request.scenario_prompt = normalize_scenario_prompt(request.scenario_prompt)
    return request


def run_simulation_command(*, selector: str, simulation_runner: SimulationRunner) -> str:
    scenario = normalize_scenario_prompt(selector or DEFAULT_SCENARIO_PROMPT)
    result = simulation_runner.run(
        normalized_simulation_request(
            SimulationRequest(
                scenario_prompt=scenario,
                participant_prompt=DIRECT_ADULT_PERSONA_PROMPT,
            )
        )
    )
    lines = [f"Stop-Grund: {result.stopped_reason}", ""]
    for entry in result.transcript:
        prefix = "Teilnehmer" if entry.role == "participant" else "System"
        lines.append(f"{prefix}: {entry.content}")
    return "\n".join(lines)


__all__ = [
    "SimulationRequest",
    "SimulationResult",
    "SimulationRunner",
    "SimulationSystemTurn",
    "SimulationTranscriptEntry",
    "DEFAULT_SCENARIO_PROMPT",
    "DIRECT_ADULT_PERSONA_PROMPT",
    "PERSONA_PROMPTS",
    "SCENARIO_PROMPTS",
    "normalized_simulation_request",
    "run_simulation_command",
]
