import sys
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.turn import TurnInput


def test_raw_suspected_dyspnea_opens_safety_question_without_emergency():
    engine = TurnEngine()

    result = engine.run_turn(
        TurnInput(
            message="Ich bekomme schlecht Luft",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    assert result.response_mode == "ask_safety_question"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "safety_clarification"
    assert result.conversation_state.active_question.safety_context is not None
    assert result.conversation_state.active_question.blocking is True
    assert "turn:safety_clarification_opened" in result.trace_notes
    assert result.response_mode != "emergency"


def test_yes_to_open_safety_question_confirms_emergency():
    engine = TurnEngine()

    first = engine.run_turn(
        TurnInput(
            message="Ich bekomme schlecht Luft",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    second = engine.run_turn(
        TurnInput(
            message="yes",
            session_id="test-session",
            turn_id="turn-2",
            persisted_conversation_state=first.conversation_state,
            persisted_medical_case=first.medical_case,
            persisted_case_topic=first.case_topic,
            persisted_recommendation_state=first.recommendation_state,
        )
    )

    assert second.response_mode == "emergency"
    assert "turn:safety_confirmation_emergency" in second.trace_notes


def test_no_to_open_safety_question_clears_question_without_emergency():
    engine = TurnEngine()

    first = engine.run_turn(
        TurnInput(
            message="Ich bekomme schlecht Luft",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    second = engine.run_turn(
        TurnInput(
            message="no",
            session_id="test-session",
            turn_id="turn-2",
            persisted_conversation_state=first.conversation_state,
            persisted_medical_case=first.medical_case,
            persisted_case_topic=first.case_topic,
            persisted_recommendation_state=first.recommendation_state,
        )
    )

    assert second.response_mode != "emergency"
    assert second.conversation_state.active_question is None


def test_unsure_to_open_safety_question_keeps_question_open():
    engine = TurnEngine()

    first = engine.run_turn(
        TurnInput(
            message="Ich bekomme schlecht Luft",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    second = engine.run_turn(
        TurnInput(
            message="unsure",
            session_id="test-session",
            turn_id="turn-2",
            persisted_conversation_state=first.conversation_state,
            persisted_medical_case=first.medical_case,
            persisted_case_topic=first.case_topic,
            persisted_recommendation_state=first.recommendation_state,
        )
    )

    assert second.response_mode == "ask_safety_question"
    assert second.conversation_state.active_question is not None
    assert second.conversation_state.active_question.kind == "safety_clarification"
    assert second.conversation_state.active_question.safety_context is not None
