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

def test_safety_question_disables_free_text_contract():
    engine = TurnEngine()

    result = engine.run_turn(
        TurnInput(
            message="Ich bekomme schlecht Luft",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    active_question = result.conversation_state.active_question

    assert result.response_mode == "ask_safety_question"
    assert active_question is not None
    assert active_question.kind == "safety_clarification"
    assert active_question.blocking is True
    assert active_question.allows_additional_medical_info is False
    assert active_question.guided_input is not None
    assert active_question.guided_input.free_text_allowed is False
    assert {option.code for option in active_question.guided_input.options} == {
        "yes",
        "no",
        "unsure",
        "immediate_help",
    }


def test_free_text_during_safety_question_is_invalid_and_keeps_question_open():
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
            message="Nein, aber ich habe seit gestern Husten.",
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
    assert "safety_clarification:invalid_answer" in second.trace_notes
    assert "turn:repeat_active_question" in second.trace_notes
    assert "turn:early_safety_clarification_cleared" not in second.trace_notes
    assert second.response_mode != "emergency"


def test_visible_label_yes_to_open_safety_question_confirms_emergency():
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
            message="Ja",
            session_id="test-session",
            turn_id="turn-2",
            persisted_conversation_state=first.conversation_state,
            persisted_medical_case=first.medical_case,
            persisted_case_topic=first.case_topic,
            persisted_recommendation_state=first.recommendation_state,
        )
    )

    assert second.response_mode == "emergency"
    assert "safety_clarification:confirmed_red_flag" in second.trace_notes
    assert "turn:safety_confirmation_emergency" in second.trace_notes


def test_visible_label_no_to_open_safety_question_clears_question():
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
            message="Nein",
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
    assert "safety_clarification:cleared_red_flag" in second.trace_notes
