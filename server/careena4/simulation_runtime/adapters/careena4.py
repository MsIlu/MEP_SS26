from careena4.application import TurnEngine
from careena4.models.turn import TurnInput
from careena4.simulation_runtime.models import SimulationSystemTurn, SimulationTranscriptEntry


class Careena4Adapter:
    def __init__(self, turn_engine: TurnEngine):
        self.turn_engine = turn_engine

    def respond(
        self,
        *,
        user_message: str,
        transcript: list[SimulationTranscriptEntry],
        state: dict | None,
    ) -> SimulationSystemTurn:
        case_topic = None
        medical_case = None
        conversation_state = None
        recommendation_state = None
        if state is not None:
            case_topic = state.get("case_topic")
            medical_case = state.get("medical_case")
            conversation_state = state.get("conversation_state")
            recommendation_state = state.get("recommendation_state")
        result = self.turn_engine.run_turn(
            TurnInput.from_persisted_state(
                message=user_message,
                conversation_messages=_transcript_to_messages(transcript),
                persisted_case_topic=case_topic,
                persisted_medical_case=medical_case,
                persisted_conversation_state=conversation_state,
                persisted_recommendation_state=recommendation_state,
            )
        )
        next_case_topic = result.case_topic
        next_medical_case = result.medical_case if result.medical_case is not None else medical_case
        next_conversation_state = result.conversation_state
        next_recommendation_state = result.recommendation_state
        return SimulationSystemTurn(
            text=result.response_text,
            response_mode=result.response_mode,
            should_stop=result.response_mode in {"recommend", "emergency", "out_of_scope"},
            stop_reason=result.response_mode,
            summary=_build_summary(
                result=result,
                case_topic=next_case_topic,
                medical_case=next_medical_case,
                conversation_state=next_conversation_state,
                recommendation_state=next_recommendation_state,
            ),
            state={
                "case_topic": next_case_topic,
                "medical_case": next_medical_case,
                "conversation_state": next_conversation_state,
                "recommendation_state": next_recommendation_state,
            },
            raw_result=result,
        )


def _transcript_to_messages(transcript: list[SimulationTranscriptEntry]) -> list[dict[str, str]]:
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
    case_topic,
    medical_case,
    conversation_state,
    recommendation_state,
) -> dict[str, object]:
    summary: dict[str, object] = {"response_mode": result.response_mode}
    if case_topic is not None:
        summary["case_topic"] = case_topic.current_label
    if medical_case is not None:
        summary["observation_count"] = len(medical_case.observations)
        summary["observations"] = [
            {
                "type": observation.type,
                "label": observation.label,
                "negated": observation.negated,
                "attributes": dict(observation.attributes),
            }
            for observation in medical_case.observations[:5]
        ]
    if conversation_state is not None and conversation_state.active_question is not None:
        summary["active_question"] = conversation_state.active_question.kind
    if recommendation_state is not None:
        summary["recommendation_allowed"] = recommendation_state.recommendation_allowed
    return summary
