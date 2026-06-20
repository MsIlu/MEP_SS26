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
        "Was ist los?",
        "Was könnte das sein?",
        "Was soll ich machen?",
        "Ich weiß nicht.",
    ],
)
def test_short_context_messages_are_not_out_of_scope_when_medical_case_exists(message):
    result = TurnEngine().run_turn(
        TurnInput(
            message=message,
            session_id="test-session",
            turn_id="turn-2",
            persisted_medical_case=_existing_belly_pain_case(),
        )
    )

    assert result.response_mode != "out_of_scope"
    assert "turn:out_of_scope" not in result.trace_notes


def test_clear_non_medical_topic_can_still_be_out_of_scope_without_open_question():
    result = TurnEngine().run_turn(
        TurnInput(
            message="Kannst du mir Python-Code für eine Wetter-App schreiben?",
            session_id="test-session",
            turn_id="turn-2",
            persisted_medical_case=_existing_belly_pain_case(),
        )
    )

    assert result.response_mode == "out_of_scope"
    assert "turn:out_of_scope" in result.trace_notes
