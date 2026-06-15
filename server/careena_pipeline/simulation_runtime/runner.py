from careena_pipeline.core.client import LLMClient
from careena_pipeline.core.exceptions import (
    EmptyLLMResponseError,
    InvalidJSONError,
    SchemaValidationError,
)
from careena_pipeline.simulation_runtime.adapters.base import (
    ConversationSystemAdapter,
)
from careena_pipeline.simulation_runtime.models import (
    SimulationRequest,
    SimulationResult,
    SimulationTranscriptEntry,
)


class SimulationRunner:
    """Runs a chat simulation between a participant LLM and a system adapter."""

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

        participant_message = request.opening_message or self._generate_opening(request)

        for _ in range(request.max_turns):
            transcript.append(
                SimulationTranscriptEntry(role="participant", content=participant_message)
            )
            try:
                system_turn = self.system_adapter.respond(
                    user_message=participant_message,
                    transcript=transcript,
                    state=system_state,
                )
            except (EmptyLLMResponseError, InvalidJSONError, SchemaValidationError) as exc:
                transcript.append(
                    SimulationTranscriptEntry(
                        role="meta",
                        content=f"System adapter failed: {exc}",
                        response_mode="error",
                    )
                )
                return SimulationResult(
                    transcript=transcript,
                    final_summary=final_summary,
                    final_system_state=system_state,
                    final_system_result=final_system_result,
                    stopped_reason="system_error",
                )

            system_state = system_turn.state
            final_system_result = system_turn.raw_result
            final_summary = system_turn.summary

            transcript.append(
                SimulationTranscriptEntry(
                    role="system",
                    content=system_turn.text,
                    response_mode=system_turn.response_mode,
                )
            )
            if system_turn.should_stop:
                return SimulationResult(
                    transcript=transcript,
                    final_summary=final_summary,
                    final_system_state=system_state,
                    final_system_result=final_system_result,
                    stopped_reason=system_turn.stop_reason or "stop_requested",
                )

            participant_message = self._generate_participant_reply(
                request=request,
                transcript=transcript,
            )
            participant_message = self._repair_empty_participant_reply(
                request=request,
                transcript=transcript,
                participant_message=participant_message,
            )

        return SimulationResult(
            transcript=transcript,
            final_summary=final_summary,
            final_system_state=system_state,
            final_system_result=final_system_result,
            stopped_reason="max_turns_reached",
        )

    def _generate_opening(self, request: SimulationRequest) -> str:
        return self._complete_participant(
            request=request,
            instruction=(
                "Formuliere die erste Chat-Nachricht dieser Person an das Assistenzsystem.\n"
                "Schreibe natuerlich, alltagssprachlich und nicht wie ein Testfall.\n"
                "Starte realistisch unvollstaendig: nenne das Hauptproblem und "
                "hoechstens ein bis zwei spontane Zusatzinformationen.\n"
                "Keine Aufzaehlung, keine Analyse, kein vollstaendiger Fact-Dump."
            ),
        )

    def _generate_participant_reply(
        self,
        *,
        request: SimulationRequest,
        transcript: list[SimulationTranscriptEntry],
    ) -> str:
        transcript_text = "\n".join(f"{entry.role}: {entry.content}" for entry in transcript)
        return self._complete_participant(
            request=request,
            instruction=(
                "Bisheriger Chat:\n"
                f"{transcript_text}\n\n"
                "Antworte jetzt als dieselbe Person auf die letzte System-Nachricht.\n"
                "Antworte kurz, natuerlich und nur mit den Informationen, die gerade "
                "wirklich zur letzten Frage passen.\n"
                "Keine Listen, keine Meta-Erklaerung, keine komplette Wiederholung des Szenarios."
            ),
        )

    def _repair_empty_participant_reply(
        self,
        *,
        request: SimulationRequest,
        transcript: list[SimulationTranscriptEntry],
        participant_message: str,
    ) -> str:
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
                "Antworte jetzt kurz, direkt und menschlich mit der passenden Information "
                "aus dem Szenario."
            )
        )

    def _complete_participant(
        self,
        *,
        request: SimulationRequest,
        instruction: str,
    ) -> str:
        participant_llm = (
            self.participant_llms.get(request.participant_llm_mode)
            or self.default_participant_llm
        )
        messages = [
            {"role": "system", "content": request.participant_prompt},
            {
                "role": "user",
                "content": (
                    "Szenario:\n"
                    f"{request.scenario_prompt}\n\n"
                    f"{instruction}"
                ),
            },
        ]
        try:
            reply = participant_llm.complete(
                messages=messages,
                temperature=request.participant_temperature,
                max_tokens=300,
                model=request.participant_model,
                json_mode=False,
            )
        except EmptyLLMResponseError:
            return "Ich weiss nicht genau."
        return _clean_participant_reply(reply)


def _clean_participant_reply(reply: str) -> str:
    cleaned = reply.strip().strip('"')
    prefixes = ["patient:", "patientin:", "angehoerige:", "angehoeriger:", "teilnehmer:"]
    lowered = cleaned.lower()
    for prefix in prefixes:
        if lowered.startswith(prefix):
            return cleaned[len(prefix) :].strip()
    return cleaned


def _last_content(transcript: list[SimulationTranscriptEntry], *, role: str) -> str | None:
    for entry in reversed(transcript):
        if entry.role == role:
            return entry.content
    return None
