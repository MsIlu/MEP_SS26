import pytest

from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.domain import ActiveQuestion, ConversationState, FollowupNeed, MedicalCase, Observation
from careena4.models.turn import TurnInput


def _case_with_open_duration_question():
    medical_case = MedicalCase(
        observations=[
            Observation(
                observation_id="obs-1",
                type="symptom",
                label="Bauchschmerzen",
                normalized_concept="bauchschmerzen",
                subject_ref="self",
                topic_relation="central",
                attributes={},
            )
        ]
    )
    conversation_state = ConversationState(
        phase="followup",
        active_question=ActiveQuestion(
            kind="followup",
            question_intent="duration",
            target_followup_id="followup-1",
            target_observation_id="obs-1",
            prompt_text="Seit wann bestehen die Bauchschmerzen?",
            blocking=True,
            allows_additional_medical_info=True,
        ),
        followup_needs=[
            FollowupNeed(
                followup_id="followup-1",
                observation_id="obs-1",
                reason="duration_missing",
                target_extension_kind="duration_or_onset",
                blocking=True,
                priority="high",
            )
        ],
    )
    return medical_case, conversation_state


@pytest.mark.parametrize(
    "message",
    [
        "Ich bekomme schlecht Luft.",
        "Ich habe Druck auf der Brust.",
        "Er ist sehr verwirrt.",
    ],
)
def test_suspected_red_flag_overrides_open_normal_followup_question(message):
    medical_case, conversation_state = _case_with_open_duration_question()

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


@pytest.mark.parametrize(
    "message",
    [
        "Ich bekomme keine Luft.",
        "Die Person ist bewusstlos und atmet nicht.",
    ],
)
def test_confirmed_red_flag_overrides_open_normal_followup_question_with_emergency(message):
    medical_case, conversation_state = _case_with_open_duration_question()

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
    assert result.conversation_state.active_question.kind == "followup"
    assert any(
        note in result.trace_notes
        for note in (
            "turn:emergency_shortcut",
            "turn:structured_emergency_shortcut",
        )
    )


def test_non_safety_answer_still_resolves_open_normal_followup_question():
    medical_case, conversation_state = _case_with_open_duration_question()

    result = TurnEngine().run_turn(
        TurnInput(
            message="Seit gestern.",
            session_id="test-session",
            turn_id="turn-2",
            persisted_medical_case=medical_case,
            persisted_conversation_state=conversation_state,
        )
    )

    observation = next(
        observation
        for observation in result.medical_case.observations
        if observation.observation_id == "obs-1"
    )

    assert observation.attributes["duration_or_onset"] == "Seit gestern."
    assert result.response_mode != "ask_safety_question"
    assert result.response_mode != "emergency"
