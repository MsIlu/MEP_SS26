import pytest

from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.turn import TurnInput


@pytest.mark.parametrize(
    "message",
    [
        "Die Person ist bewusstlos und atmet nicht.",
        "Ich bekomme keine Luft.",
    ],
)
def test_confirmed_red_flags_trigger_emergency(message):
    result = TurnEngine().run_turn(
        TurnInput(
            message=message,
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    assert result.response_mode == "emergency"
    assert result.conversation_state.active_question is None
    assert any(
        note in result.trace_notes
        for note in (
            "turn:emergency_shortcut",
            "turn:structured_emergency_shortcut",
        )
    )


@pytest.mark.parametrize(
    "message",
    [
        "Ich bekomme schlecht Luft.",
        "Ich habe Druck auf der Brust.",
        "Mein Mundwinkel hängt plötzlich.",
        "Er ist sehr verwirrt.",
    ],
)
def test_suspected_red_flags_open_safety_clarification(message):
    result = TurnEngine().run_turn(
        TurnInput(
            message=message,
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    assert result.response_mode == "ask_safety_question"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "safety_clarification"
    assert any(
        note in result.trace_notes
        for note in (
            "turn:safety_clarification_opened",
            "turn:structured_safety_clarification_opened",
        )
    )


@pytest.mark.parametrize(
    "message",
    [
        "Ich bekomme normal Luft.",
        "Ich habe keine Atemnot.",
        "Ich habe keine Brustschmerzen.",
        "Ich fühle mich schwach.",
    ],
)
def test_non_red_flag_or_negated_red_flag_messages_do_not_open_safety_question(message):
    result = TurnEngine().run_turn(
        TurnInput(
            message=message,
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    assert result.response_mode != "emergency"
    assert result.response_mode != "ask_safety_question"
    assert "turn:emergency_shortcut" not in result.trace_notes
    assert "turn:structured_emergency_shortcut" not in result.trace_notes
    assert "turn:safety_clarification_opened" not in result.trace_notes
    assert "turn:structured_safety_clarification_opened" not in result.trace_notes
