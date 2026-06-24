from careena4.simulation_runtime.models import SimulationRequest, SimulationResult
from careena4.simulation_runtime.prompts import (
    DEFAULT_SCENARIO_PROMPT,
    DIRECT_ADULT_PERSONA_PROMPT,
    SCENARIO_PROMPTS,
    normalize_scenario_prompt,
)


DEFAULT_SIMRUN_MAX_TURNS = 4


def normalized_simulation_request(request: SimulationRequest) -> SimulationRequest:
    participant_llm_mode = request.participant_llm_mode or "env"
    scenario_prompt = normalize_scenario_prompt(request.scenario_prompt)
    return request.model_copy(
        update={
            "participant_llm_mode": participant_llm_mode,
            "scenario_prompt": scenario_prompt,
        }
    )


def run_simulation_command(*, selector: str, simulation_runner) -> str:
    key = selector.strip().lower()
    if key == "all":
        return _run_all_simulations(simulation_runner=simulation_runner)

    result = simulation_runner.run(
        normalized_simulation_request(
            SimulationRequest(
                scenario_prompt=selector or DEFAULT_SCENARIO_PROMPT,
                participant_prompt=DIRECT_ADULT_PERSONA_PROMPT,
                max_turns=DEFAULT_SIMRUN_MAX_TURNS,
            )
        )
    )
    return format_simulation_transcript(result)


def format_simulation_transcript(result: SimulationResult) -> str:
    lines = [
        "Simulation abgeschlossen.",
        f"Stop-Grund: {result.stopped_reason}",
        "",
        "Transcript:",
    ]
    for entry in result.transcript:
        if entry.role == "participant":
            speaker = "Teilnehmer"
        elif entry.role == "system":
            speaker = "System"
        else:
            speaker = "Meta"
        lines.append(f"{speaker}: {entry.content}")
        lines.append("")
    return "\n".join(lines).strip()


def _run_all_simulations(*, simulation_runner) -> str:
    lines = ["Simulationen abgeschlossen.", ""]
    for scenario_key, scenario_prompt in SCENARIO_PROMPTS.items():
        result = simulation_runner.run(
            normalized_simulation_request(
                SimulationRequest(
                    scenario_prompt=scenario_prompt,
                    participant_prompt=DIRECT_ADULT_PERSONA_PROMPT,
                    max_turns=DEFAULT_SIMRUN_MAX_TURNS,
                )
            )
        )
        lines.append(f"=== Simulation {scenario_key} ===")
        lines.append(format_simulation_transcript(result))
        lines.append("")
    return "\n".join(lines).strip()
