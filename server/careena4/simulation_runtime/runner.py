from careena4.core.client import LLMClient
from careena4.core.exceptions import EmptyLLMResponseError, InvalidJSONError, SchemaValidationError
from careena4.server_log import log_simulation_json, log_simulation_text
from careena4.simulation_runtime.adapters.base import ConversationSystemAdapter
from careena4.simulation_runtime.models import SimulationRequest, SimulationResult, SimulationTranscriptEntry
from careena4.simulation_runtime.prompts import build_participant_prompt, normalize_scenario_prompt


class SimulationRunner:
    def __init__(
        self,
        *,
        participant_llm: LLMClient | None = None,
        participant_llms: dict[str, LLMClient] | None = None,
        default_participant_llm_mode: str = "local",
        system_adapter: ConversationSystemAdapter,
    ):
        llm_map = dict(participant_llms or {})
        if participant_llm is not None:
            llm_map.setdefault(default_participant_llm_mode, participant_llm)
            llm_map.setdefault("default", participant_llm)
        if not llm_map:
            raise ValueError("SimulationRunner requires at least one participant LLM client.")
        self.participant_llms = llm_map
        self.default_participant_llm_mode = default_participant_llm_mode
        self.system_adapter = system_adapter
        self.default_participant_llm = (
            self.participant_llms.get(self.default_participant_llm_mode)
            or self.participant_llms.get("default")
            or next(iter(self.participant_llms.values()))
        )

    def run(self, request: SimulationRequest) -> SimulationResult:
        transcript: list[SimulationTranscriptEntry] = []
        system_state = None
        final_system_result = None
        final_summary = None
        log_simulation_json("SIMULATION REQUEST", request)
        participant_message = request.opening_message or self._generate_opening(request)
        for _ in range(request.max_turns):
            transcript.append(SimulationTranscriptEntry(role="participant", content=participant_message))
            try:
                system_turn = self.system_adapter.respond(
                    user_message=participant_message,
                    transcript=transcript,
                    state=system_state,
                )
            except (EmptyLLMResponseError, InvalidJSONError, SchemaValidationError) as exc:
                transcript.append(SimulationTranscriptEntry(role="meta", content=f"System adapter failed: {exc}", response_mode="error"))
                result = SimulationResult(
                    transcript=transcript,
                    final_summary=final_summary,
                    final_system_state=system_state,
                    final_system_result=final_system_result,
                    stopped_reason="system_error",
                )
                self._log_result(result)
                return result
            system_state = system_turn.state
            final_system_result = system_turn.raw_result
            final_summary = system_turn.summary
            transcript.append(SimulationTranscriptEntry(role="system", content=system_turn.text, response_mode=system_turn.response_mode))
            if system_turn.should_stop:
                result = SimulationResult(
                    transcript=transcript,
                    final_summary=final_summary,
                    final_system_state=system_state,
                    final_system_result=final_system_result,
                    stopped_reason=system_turn.stop_reason or "stop_requested",
                )
                self._log_result(result)
                return result
            participant_message = self._generate_participant_reply(request=request, transcript=transcript)
            participant_message = self._repair_empty_participant_reply(
                request=request,
                transcript=transcript,
                participant_message=participant_message,
            )
        result = SimulationResult(
            transcript=transcript,
            final_summary=final_summary,
            final_system_state=system_state,
            final_system_result=final_system_result,
            stopped_reason="max_turns_reached",
        )
        self._log_result(result)
        return result

    def _generate_opening(self, request: SimulationRequest) -> str:
        return self._complete_participant(
            request=request,
            instruction=(
                "Formuliere die erste Chat-Nachricht dieser Person an das Assistenzsystem.\n"
                "Schreibe natuerlich, alltagssprachlich und realistisch unvollstaendig."
            ),
        )

    def _generate_participant_reply(self, *, request: SimulationRequest, transcript: list[SimulationTranscriptEntry]) -> str:
        transcript_text = "\n".join(f"{entry.role}: {entry.content}" for entry in transcript)
        return self._complete_participant(
            request=request,
            instruction=(
                "Bisheriger Chat:\n"
                f"{transcript_text}\n\n"
                "Antworte kurz und nur mit den Informationen, die gerade zur letzten Frage passen."
            ),
        )

    def _repair_empty_participant_reply(self, *, request: SimulationRequest, transcript: list[SimulationTranscriptEntry], participant_message: str) -> str:
        if participant_message.strip():
            return participant_message
        last_system_message = _last_content(transcript, role="system")
        if not last_system_message:
            return participant_message
        return self._complete_participant(
            request=request,
            instruction=(
                "Deine letzte Antwort war leer.\n\n"
                f"Das System fragte oder sagte:\n{last_system_message}\n\n"
                "Antworte jetzt kurz, direkt und menschlich mit der passenden Information aus dem Szenario."
            ),
        )

    def _complete_participant(self, *, request: SimulationRequest, instruction: str) -> str:
        participant_llm = self.participant_llms.get(request.participant_llm_mode) or self.default_participant_llm
        try:
            reply = participant_llm.complete(
                messages=[
                    {"role": "system", "content": build_participant_prompt(request.participant_prompt)},
                    {"role": "user", "content": f"Szenario:\n{normalize_scenario_prompt(request.scenario_prompt)}\n\n{instruction}"},
                ],
                temperature=request.participant_temperature,
                max_tokens=300,
                model=request.participant_model,
                json_mode=False,
            )
        except EmptyLLMResponseError:
            return "Ich weiss nicht genau."
        return _clean_participant_reply(reply)

    def _log_result(self, result: SimulationResult) -> None:
        lines = [f"Stop-Grund: {result.stopped_reason}", "", "Transcript:"]
        for entry in result.transcript:
            speaker = "Teilnehmer" if entry.role == "participant" else "System" if entry.role == "system" else "Meta"
            lines.append(f"{speaker}: {entry.content}")
            lines.append("")
        log_simulation_text("SIMULATION TRANSCRIPT", "\n".join(lines).strip())
        log_simulation_json("SIMULATION RESULT", result)


def _clean_participant_reply(reply: str) -> str:
    cleaned = reply.strip().strip('"')
    prefixes = ["patient:", "patientin:", "angehoerige:", "angehoeriger:", "teilnehmer:"]
    lowered = cleaned.lower()
    for prefix in prefixes:
        if lowered.startswith(prefix):
            return cleaned[len(prefix):].strip()
    return cleaned


def _last_content(transcript: list[SimulationTranscriptEntry], *, role: str) -> str | None:
    for entry in reversed(transcript):
        if entry.role == role:
            return entry.content
    return None
