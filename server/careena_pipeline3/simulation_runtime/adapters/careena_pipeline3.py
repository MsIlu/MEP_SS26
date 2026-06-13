from careena_pipeline3.application.managers import DialogueManager
from careena_pipeline3.models.turn import TurnInput
from careena_pipeline3.simulation_runtime.models import (
    SimulationSystemTurn,
    SimulationTranscriptEntry,
)


class CareenaPipeline3Adapter:
    """Adapts careena_pipeline3 to the generic simulation runtime."""

    def __init__(self, dialogue_manager: DialogueManager):
        self.dialogue_manager = dialogue_manager

    def respond(
        self,
        *,
        user_message: str,
        transcript: list[SimulationTranscriptEntry],
        state: dict | None,
    ) -> SimulationSystemTurn:
        case = None
        concern_state = None
        dialogue_state = None
        if state is not None:
            case = state.get("case")
            concern_state = state.get("concern_state")
            dialogue_state = state.get("dialogue_state")

        result = self.dialogue_manager.run_turn(
            TurnInput(
                message=user_message,
                conversation_messages=_transcript_to_messages(transcript),
                existing_case=case,
                existing_concern_state=concern_state,
                existing_dialogue_state=dialogue_state,
            )
        )

        next_case = result.context.medical_case if result.context.medical_case is not None else case
        next_concern_state = result.context.concern_state
        next_dialogue_state = (
            result.context.dialogue_state
            if result.context.dialogue_state is not None
            else dialogue_state
        )

        return SimulationSystemTurn(
            text=result.response_text or "",
            response_mode=result.response_mode,
            should_stop=result.response_mode in {"recommend", "emergency", "out_of_scope"},
            stop_reason=result.response_mode,
            summary=_build_summary(
                result=result,
                case=next_case,
                concern_state=next_concern_state,
                dialogue_state=next_dialogue_state,
            ),
            state={
                "case": next_case,
                "concern_state": next_concern_state,
                "dialogue_state": next_dialogue_state,
            },
            raw_result=result,
        )


def _transcript_to_messages(
    transcript: list[SimulationTranscriptEntry],
) -> list[dict[str, str]]:
    role_map = {"participant": "user", "system": "assistant", "meta": "system"}
    messages: list[dict[str, str]] = []
    for entry in transcript:
        role = role_map.get(entry.role)
        if role is not None:
            messages.append({"role": role, "content": entry.content})
    return messages


def _build_summary(
    *,
    result,
    case,
    concern_state,
    dialogue_state,
) -> dict[str, object]:
    summary: dict[str, object] = {
        "response_mode": result.response_mode,
    }
    if concern_state is not None:
        summary["concern_summary"] = concern_state.summary or "unklar"
    if case is None:
        return summary

    case.ensure_primary_problem()
    summary["case_frame"] = case.current_case_frame_label() or "unklar"
    summary["focus"] = case.primary_focus_label() or "unklar"
    summary["pending"] = (
        dialogue_state.pending_followup.slot
        if dialogue_state is not None and dialogue_state.pending_followup is not None
        else "keiner"
    )

    observations: list[dict[str, object]] = []
    for observation in case.observations[:5]:
        observations.append(
            {
                "type": observation.type,
                "label": observation.patient_label,
                "temporality": observation.temporality,
                "severity": observation.severity,
                "measurement": dict(observation.measurement),
                "details": dict(observation.details),
            }
        )
    summary["observations"] = observations
    return summary
