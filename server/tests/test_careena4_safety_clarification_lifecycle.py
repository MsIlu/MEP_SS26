from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.turn import TurnInput


def test_cleared_safety_clarification_allows_next_medical_message():
    engine = TurnEngine()

    first_result = engine.run_turn(
        TurnInput(
            message="Ich bekomme schlecht Luft.",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    assert first_result.response_mode == "ask_safety_question"
    assert first_result.conversation_state.active_question is not None
    assert first_result.conversation_state.active_question.kind == "safety_clarification"

    second_result = engine.run_turn(
        TurnInput(
            message="Nein",
            session_id="test-session",
            turn_id="turn-2",
            persisted_medical_case=first_result.medical_case,
            persisted_conversation_state=first_result.conversation_state,
            persisted_case_topic=first_result.case_topic,
        )
    )

    assert second_result.response_mode != "emergency"
    assert second_result.response_mode != "ask_safety_question"
    assert second_result.conversation_state.active_question is None
    assert "safety_clarification:cleared_red_flag" in second_result.trace_notes

    third_result = engine.run_turn(
        TurnInput(
            message="Ich habe Husten seit gestern.",
            session_id="test-session",
            turn_id="turn-3",
            persisted_medical_case=second_result.medical_case,
            persisted_conversation_state=second_result.conversation_state,
            persisted_case_topic=second_result.case_topic,
        )
    )

    labels = {observation.label for observation in third_result.medical_case.observations}

    assert "Husten" in labels
    assert third_result.response_mode != "emergency"
    assert third_result.response_mode != "ask_safety_question"
    assert "turn:safety_clarification_opened" not in third_result.trace_notes


def test_confirmed_safety_clarification_routes_to_emergency():
    engine = TurnEngine()

    first_result = engine.run_turn(
        TurnInput(
            message="Ich bekomme schlecht Luft.",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    second_result = engine.run_turn(
        TurnInput(
            message="Ja",
            session_id="test-session",
            turn_id="turn-2",
            persisted_medical_case=first_result.medical_case,
            persisted_conversation_state=first_result.conversation_state,
            persisted_case_topic=first_result.case_topic,
        )
    )

    assert second_result.response_mode == "emergency"
    assert "safety_clarification:confirmed_red_flag" in second_result.trace_notes
