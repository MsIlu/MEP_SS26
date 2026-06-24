import sys
import unittest
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


from careena4.simulation_runtime.chat_commands import (
    DEFAULT_SIMRUN_MAX_TURNS,
    normalized_simulation_request,
    run_simulation_command,
)
from careena4.simulation_runtime.models import (
    SimulationRequest,
    SimulationResult,
    SimulationTranscriptEntry,
)
from careena4.simulation_runtime.prompts import DEFAULT_SCENARIO_PROMPT, SCENARIO_PROMPTS


class Careena4SimulationChatCommandsTests(unittest.TestCase):
    def test_normalized_request_sets_env_mode_without_mutating_input(self):
        request = SimulationRequest(scenario_prompt="", participant_llm_mode=None)

        normalized = normalized_simulation_request(request)

        self.assertIsNone(request.participant_llm_mode)
        self.assertEqual(normalized.participant_llm_mode, "env")
        self.assertEqual(normalized.scenario_prompt, DEFAULT_SCENARIO_PROMPT)

    def test_simrun_uses_short_default_run_and_formats_transcript(self):
        runner = _FakeSimulationRunner()

        response_text = run_simulation_command(selector="", simulation_runner=runner)

        self.assertIn("Simulation abgeschlossen.", response_text)
        self.assertIn("Stop-Grund: recommend", response_text)
        self.assertIn("Teilnehmer: Ich habe Beschwerden.", response_text)
        self.assertEqual(len(runner.requests), 1)
        request = runner.requests[0]
        self.assertEqual(request.max_turns, DEFAULT_SIMRUN_MAX_TURNS)
        self.assertEqual(request.participant_llm_mode, "env")
        self.assertEqual(request.scenario_prompt, DEFAULT_SCENARIO_PROMPT)

    def test_simrun_numeric_selector_maps_to_named_scenario(self):
        runner = _FakeSimulationRunner()

        run_simulation_command(selector="1", simulation_runner=runner)

        self.assertEqual(len(runner.requests), 1)
        self.assertEqual(runner.requests[0].scenario_prompt, SCENARIO_PROMPTS["1"])

    def test_simrun_all_runs_each_named_scenario_with_short_runs(self):
        runner = _FakeSimulationRunner()

        response_text = run_simulation_command(selector="all", simulation_runner=runner)

        self.assertIn("Simulationen abgeschlossen.", response_text)
        self.assertEqual(len(runner.requests), len(SCENARIO_PROMPTS))
        self.assertTrue(all(request.max_turns == DEFAULT_SIMRUN_MAX_TURNS for request in runner.requests))
        self.assertTrue(all(request.participant_llm_mode == "env" for request in runner.requests))
        for scenario_key in SCENARIO_PROMPTS:
            self.assertIn(f"=== Simulation {scenario_key} ===", response_text)


class _FakeSimulationRunner:
    def __init__(self):
        self.requests: list[SimulationRequest] = []

    def run(self, request: SimulationRequest) -> SimulationResult:
        self.requests.append(request)
        return SimulationResult(
            transcript=[
                SimulationTranscriptEntry(role="participant", content="Ich habe Beschwerden."),
                SimulationTranscriptEntry(role="system", content="Seit wann denn?"),
            ],
            stopped_reason="recommend",
        )


if __name__ == "__main__":
    unittest.main()
