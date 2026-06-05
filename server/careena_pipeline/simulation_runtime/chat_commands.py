from careena_pipeline.simulation_runtime.models import (
    SimulationRequest,
    SimulationResult,
)
from careena_pipeline.simulation_runtime.prompts import (
    DEFAULT_PARTICIPANT_PROMPT,
    DEFAULT_TESTRUN_SCENARIO,
    SIMULATION_SCENARIOS,
)


def normalized_simulation_request(req: SimulationRequest) -> SimulationRequest:
    if req.participant_prompt:
        return req
    return req.model_copy(update={"participant_prompt": DEFAULT_PARTICIPANT_PROMPT})


def resolve_simulation_prompt(value: str) -> str:
    if not value:
        return DEFAULT_TESTRUN_SCENARIO

    key = value.strip().lower()
    return SIMULATION_SCENARIOS.get(key, value)


def run_simulation_command(*, selector: str, simulation_runner) -> str:
    key = selector.strip().lower()
    if key == "all":
        lines = ["Simulationen abgeschlossen.", ""]
        for scenario_key in SIMULATION_SCENARIOS:
            result = simulation_runner.run(
                SimulationRequest(
                    scenario_prompt=SIMULATION_SCENARIOS[scenario_key],
                    participant_prompt=DEFAULT_PARTICIPANT_PROMPT,
                    max_turns=8,
                )
            )
            lines.append(f"=== Simulation {scenario_key} ===")
            lines.append(format_simulation_transcript(result))
            lines.append("")
        return "\n".join(lines).strip()

    result = simulation_runner.run(
        SimulationRequest(
            scenario_prompt=resolve_simulation_prompt(selector),
            participant_prompt=DEFAULT_PARTICIPANT_PROMPT,
            max_turns=8,
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

    final_summary = result.final_summary or {}
    if final_summary:
        lines.extend(
            [
                "Finale Summary:",
                f"- Hauptfokus: {final_summary.get('focus', 'unklar')}",
                f"- Pending Slot: {final_summary.get('pending', 'keiner')}",
            ]
        )
        for observation in final_summary.get("observations", []):
            details = []
            if observation.get("temporality"):
                details.append(f"Zeit: {observation['temporality']}")
            if observation.get("severity") is not None:
                details.append(f"Staerke: {observation['severity']}/10")
            if observation.get("measurement"):
                details.append(f"Messwert: {observation['measurement']}")
            if observation.get("details"):
                details.append(f"Details: {observation['details']}")
            suffix = f" ({'; '.join(details)})" if details else ""
            lines.append(
                f"- {observation.get('type', 'observation')}: "
                f"{observation.get('label', 'unbekannt')}{suffix}"
            )

    return "\n".join(lines).strip()
