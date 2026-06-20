import pytest

from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.domain import (
    ActiveQuestion,
    ConversationState,
    FollowupNeed,
    MedicalCase,
    Observation,
)
from careena4.models.turn import TurnInput


def _case_with_duration_question() -> tuple[MedicalCase, ConversationState]:
    observation = Observation(
        observation_id="obs-1",
        type="symptom",
        label="Bauchschmerzen",
        topic_relation="central",
    )
    medical_case = MedicalCase(observations=[observation])
    conversation_state = ConversationState(
        phase="followup",
        active_question=ActiveQuestion(
            kind="followup",
            question_intent="duration",
            target_followup_id="followup-1",
            target_observation_id="obs-1",
            prompt_text="Seit wann bestehen die Beschwerden?",
            blocking=True,
        ),
        followup_needs=[
            FollowupNeed(
                followup_id="followup-1",
                observation_id="obs-1",
                reason="duration_missing",
                blocking=True,
            )
        ],
    )
    return medical_case, conversation_state


@pytest.mark.parametrize(
    "answer",
    [
        "seit gestern",
        "seit heute Morgen",
        "vor drei Tagen",
        "seit zwei Wochen",
        "ungefähr seit einer Stunde",
        "seit dem Unfall",
        "seit letzter Nacht",
    ],
)
def test_duration_followup_answers_are_stored_as_raw_duration_or_onset(answer):
    medical_case, conversation_state = _case_with_duration_question()

    result = TurnEngine().run_turn(
        TurnInput(
            message=answer,
            session_id="test-session",
            turn_id="turn-1",
            persisted_medical_case=medical_case,
            persisted_conversation_state=conversation_state,
        )
    )

    enriched = next(
        observation
        for observation in result.medical_case.observations
        if observation.observation_id == "obs-1"
    )

    assert enriched.attributes["duration_or_onset"] == answer
    assert enriched.status == "enriched"
    assert "followup:resolved:duration_or_onset" in result.trace_notes
    assert result.response_mode != "out_of_scope"


def test_localization_followup_answer_is_stored_as_body_site():
    observation = Observation(
        observation_id="obs-1",
        type="symptom",
        label="Bauchschmerzen",
        topic_relation="central",
    )
    medical_case = MedicalCase(observations=[observation])
    conversation_state = ConversationState(
        phase="followup",
        active_question=ActiveQuestion(
            kind="followup",
            question_intent="localization",
            target_followup_id="followup-1",
            target_observation_id="obs-1",
            prompt_text="Wo genau spüren Sie das?",
            blocking=True,
        ),
        followup_needs=[
            FollowupNeed(
                followup_id="followup-1",
                observation_id="obs-1",
                reason="location_unclear",
                blocking=True,
            )
        ],
    )

    result = TurnEngine().run_turn(
        TurnInput(
            message="rechts unten",
            session_id="test-session",
            turn_id="turn-1",
            persisted_medical_case=medical_case,
            persisted_conversation_state=conversation_state,
        )
    )

    enriched = next(
        observation
        for observation in result.medical_case.observations
        if observation.observation_id == "obs-1"
    )

    assert enriched.attributes["body_site"] == "rechts unten"
    assert enriched.status == "enriched"
    assert "followup:resolved:body_site" in result.trace_notes
    assert result.response_mode != "out_of_scope"
