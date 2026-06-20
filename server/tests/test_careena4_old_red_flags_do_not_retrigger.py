from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.domain import MedicalCase, Observation
from careena4.models.turn import TurnInput


def test_old_dyspnea_observation_does_not_retrigger_emergency_on_harmless_message():
    medical_case = MedicalCase(
        observations=[
            Observation(
                observation_id="obs-old-dyspnea",
                type="symptom",
                label="Atemnot",
                normalized_concept="atemnot",
                subject_ref="self",
                attributes={"duration_or_onset": "seit gestern"},
            )
        ]
    )

    result = TurnEngine().run_turn(
        TurnInput(
            message="Danke.",
            session_id="test-session",
            turn_id="turn-2",
            persisted_medical_case=medical_case,
        )
    )

    assert result.response_mode != "emergency"
    assert "turn:emergency_shortcut" not in result.trace_notes
    assert "turn:structured_emergency_shortcut" not in result.trace_notes
    assert "turn:safety_clarification_opened" not in result.trace_notes
    assert "turn:structured_safety_clarification_opened" not in result.trace_notes


def test_old_dyspnea_observation_does_not_retrigger_safety_question_when_user_reports_improvement():
    medical_case = MedicalCase(
        observations=[
            Observation(
                observation_id="obs-old-dyspnea",
                type="symptom",
                label="Atemnot",
                normalized_concept="atemnot",
                subject_ref="self",
                attributes={"duration_or_onset": "seit gestern"},
            )
        ]
    )

    result = TurnEngine().run_turn(
        TurnInput(
            message="Mir geht es besser.",
            session_id="test-session",
            turn_id="turn-2",
            persisted_medical_case=medical_case,
        )
    )

    assert result.response_mode != "emergency"
    assert result.response_mode != "ask_safety_question"
    assert "turn:emergency_shortcut" not in result.trace_notes
    assert "turn:structured_emergency_shortcut" not in result.trace_notes
    assert "turn:safety_clarification_opened" not in result.trace_notes
    assert "turn:structured_safety_clarification_opened" not in result.trace_notes
