from uuid import uuid4

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
        state = state or {}
        session_id: str = state.get("session_id") or str(uuid4())
        medical_case = state.get("medical_case")
        conversation_state = state.get("conversation_state")
        recommendation_state = state.get("recommendation_state")
        symptom_input_draft = state.get("symptom_input_draft")
        result = self.turn_engine.run_turn(
            TurnInput.from_persisted_state(
                message=user_message,
                session_id=session_id,
                conversation_messages=_transcript_to_messages(transcript),
                persisted_medical_case=medical_case,
                persisted_conversation_state=conversation_state,
                persisted_recommendation_state=recommendation_state,
                persisted_symptom_input_draft=symptom_input_draft,
            )
        )
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
                medical_case=next_medical_case,
                conversation_state=next_conversation_state,
                recommendation_state=next_recommendation_state,
            ),
            state={
                "session_id": session_id,
                "medical_case": next_medical_case,
                "conversation_state": next_conversation_state,
                "recommendation_state": next_recommendation_state,
                "symptom_input_draft": result.symptom_input_draft,
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
    medical_case,
    conversation_state,
    recommendation_state,
) -> dict[str, object]:
    summary: dict[str, object] = {"response_mode": result.response_mode}
    if medical_case is not None:
        if medical_case.topic is not None and medical_case.topic.label:
            summary["topic"] = medical_case.topic.label
        summary["observation_count"] = len(medical_case.observations)
        summary["observations"] = [_observation_summary(observation=observation) for observation in medical_case.observations[:5]]
    if conversation_state is not None and conversation_state.active_question is not None:
        summary["active_question"] = conversation_state.active_question.kind
    if recommendation_state is not None:
        summary["recommendation_allowed"] = recommendation_state.recommendation_allowed
    return summary


def _observation_summary(*, observation) -> dict[str, object]:
    summary: dict[str, object] = {
        "type": observation.type,
        "normalized_label_de": observation.normalized_label_de,
        "status": observation.status,
        "person_ref": observation.person_ref,
    }
    for field_name in (
        "onset",
        "body_site",
        "description",
        "severity",
    ):
        value = getattr(observation, field_name)
        if value not in (None, "", []):
            summary[field_name] = value
    return summary
