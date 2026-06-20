import pytest

from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.domain import (
    ActiveQuestion,
    ConversationState,
    GuidedInputContract,
    GuidedInputMode,
    GuidedInputOption,
    MedicalCase,
    Observation,
)
from careena4.models.turn import TurnInput


def _case_with_open_closing_choice():
    medical_case = MedicalCase(
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
    conversation_state = ConversationState(
        phase="closing_check",
        active_question=ActiveQuestion(
            kind="closing_choice",
            question_intent="free_description",
            prompt_text="Möchten Sie jetzt eine Versorgungsempfehlung erhalten?",
            blocking=False,
            allows_additional_medical_info=True,
            guided_input=GuidedInputContract(
                mode=GuidedInputMode.STRUCTURED_PREFERRED,
                free_text_allowed=True,
                options=[
                    GuidedInputOption(
                        code="recommendation_now",
                        label="Ja, Empfehlung",
                        effect_code="recommendation_now",
                    ),
                    GuidedInputOption(
                        code="add_more_information",
                        label="Nein, weitere Angaben",
                        effect_code="add_more_information",
                    ),
                ],
            ),
        ),
    )
    return medical_case, conversation_state


@pytest.mark.parametrize(
    "message",
    [
        "Ich bekomme schlecht Luft.",
        "Ich habe Druck auf der Brust.",
        "Mein Mundwinkel hängt plötzlich.",
    ],
)
def test_suspected_red_flag_overrides_open_closing_choice(message):
    medical_case, conversation_state = _case_with_open_closing_choice()

    result = TurnEngine().run_turn(
        TurnInput(
            message=message,
            session_id="test-session",
            turn_id="turn-2",
            persisted_medical_case=medical_case,
            persisted_conversation_state=conversation_state,
        )
    )

    assert result.response_mode == "ask_safety_question"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "safety_clarification"
    assert "turn:safety_clarification_opened" in result.trace_notes
    assert "turn:recommendation_committed" not in result.trace_notes


@pytest.mark.parametrize(
    "message",
    [
        "Ich bekomme keine Luft.",
        "Die Person ist bewusstlos und atmet nicht.",
    ],
)
def test_confirmed_red_flag_overrides_open_closing_choice_with_emergency(message):
    medical_case, conversation_state = _case_with_open_closing_choice()

    result = TurnEngine().run_turn(
        TurnInput(
            message=message,
            session_id="test-session",
            turn_id="turn-2",
            persisted_medical_case=medical_case,
            persisted_conversation_state=conversation_state,
        )
    )

    assert result.response_mode == "emergency"
    assert "turn:recommendation_committed" not in result.trace_notes
    assert any(
        note in result.trace_notes
        for note in (
            "turn:emergency_shortcut",
            "turn:structured_emergency_shortcut",
        )
    )
