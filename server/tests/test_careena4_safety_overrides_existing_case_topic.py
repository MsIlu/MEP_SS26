import pytest

from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.domain import MedicalCase, Observation
from careena4.models.turn import TurnInput


def _existing_belly_pain_case():
    return MedicalCase(
        observations=[
            Observation(
                observation_id="obs-1",
                type="symptom",
                label="Bauchschmerzen",
                normalized_concept="bauchschmerzen",
                subject_ref="self",
                topic_relation="central",
                attributes={
                    "duration_or_onset": "seit gestern",
                    "description": "krampfartig",
                },
            )
        ]
    )


@pytest.mark.parametrize(
    "message",
    [
        "Mein Mundwinkel hängt plötzlich.",
        "Ich habe Druck auf der Brust.",
        "Ich bekomme schlecht Luft.",
        "Ich bin plötzlich sehr verwirrt.",
    ],
)
def test_suspected_red_flag_overrides_existing_case_topic(message):
    result = TurnEngine().run_turn(
        TurnInput(
            message=message,
            session_id="test-session",
            turn_id="turn-2",
            persisted_medical_case=_existing_belly_pain_case(),
        )
    )

    assert result.response_mode == "ask_safety_question"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "safety_clarification"
    assert "turn:topic_mismatch" not in result.trace_notes
    assert "turn:out_of_scope" not in result.trace_notes


@pytest.mark.parametrize(
    "message",
    [
        "Ich bekomme keine Luft.",
        "Die Person ist bewusstlos und atmet nicht.",
    ],
)
def test_confirmed_red_flag_overrides_existing_case_topic_with_emergency(message):
    result = TurnEngine().run_turn(
        TurnInput(
            message=message,
            session_id="test-session",
            turn_id="turn-2",
            persisted_medical_case=_existing_belly_pain_case(),
        )
    )

    assert result.response_mode == "emergency"
    assert "turn:topic_mismatch" not in result.trace_notes
    assert "turn:out_of_scope" not in result.trace_notes
