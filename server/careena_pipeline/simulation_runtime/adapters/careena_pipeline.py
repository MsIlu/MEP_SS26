from careena_pipeline.pipeline import CareenaDecisionPipeline
from careena_pipeline.response import pipeline_result_to_chat_response
from careena_pipeline.simulation_runtime.models import (
    SimulationSystemTurn,
    SimulationTranscriptEntry,
)


class CareenaPipelineAdapter:
    """Adapts the Careena decision pipeline to the generic simulation runtime."""

    def __init__(self, decision_pipeline: CareenaDecisionPipeline):
        self.decision_pipeline = decision_pipeline

    def respond(
        self,
        *,
        user_message: str,
        transcript: list[SimulationTranscriptEntry],
        state: dict | None,
    ) -> SimulationSystemTurn:
        case = None
        dialogue_state = None
        if state is not None:
            case = state.get("case")
            dialogue_state = state.get("dialogue_state")

        result = self.decision_pipeline.run(
            user_message,
            existing_case=case,
            existing_dialogue_state=dialogue_state,
            conversation_messages=_transcript_to_messages(transcript),
        )

        next_case = result.case if result.case is not None else case
        next_dialogue_state = (
            result.dialogue_state
            if result.dialogue_state is not None
            else dialogue_state
        )
        response = pipeline_result_to_chat_response(result)

        return SimulationSystemTurn(
            text=response["response"],
            response_mode=result.response_mode,
            should_stop=result.response_mode in {"recommend", "emergency", "out_of_scope"},
            stop_reason=result.response_mode,
            summary=_build_summary(
                result=result,
                case=next_case,
                dialogue_state=next_dialogue_state,
            ),
            state={
                "case": next_case,
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
    dialogue_state,
) -> dict[str, object]:
    summary: dict[str, object] = {
        "response_mode": result.response_mode,
    }
    if case is None:
        return summary

    case.ensure_primary_problem()
    summary["focus"] = case.primary_focus_label() or "unklar"
    summary["pending"] = (
        dialogue_state.pending_followup
        if dialogue_state is not None and dialogue_state.pending_followup
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
