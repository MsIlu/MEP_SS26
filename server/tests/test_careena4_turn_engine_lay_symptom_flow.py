import pytest

from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.turn import TurnInput


@pytest.mark.parametrize(
    ("message", "expected_label"),
    [
        ("Mir ist schlecht.", "Uebelkeit"),
        ("Mir ist übel.", "Uebelkeit"),
        ("Mir ist komisch.", "Unwohlsein"),
        ("Ich fühle mich schwach.", "Schwaeche"),
    ],
)
def test_lay_symptom_input_creates_visible_medical_case_observation(
    message,
    expected_label,
):
    result = TurnEngine().run_turn(
        TurnInput(
            message=message,
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    labels = {observation.label for observation in result.medical_case.observations}

    assert expected_label in labels
    assert result.response_mode != "out_of_scope"
    assert any(
        note == f"case_write:create:{expected_label}"
        for note in result.trace_notes
    )


def test_lay_symptom_input_keeps_subject_as_self_in_medical_case():
    result = TurnEngine().run_turn(
        TurnInput(
            message="Mir ist schlecht.",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    observation = next(
        observation
        for observation in result.medical_case.observations
        if observation.label == "Uebelkeit"
    )

    assert observation.subject_ref == "self"
    assert result.medical_case.subject.relation == "self"
