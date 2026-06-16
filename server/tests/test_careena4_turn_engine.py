from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.turn import TurnInput


def _next_input(message: str, result):
    return TurnInput(
        message=message,
        persisted_case_topic=result.case_topic,
        persisted_medical_case=result.medical_case,
        persisted_conversation_state=result.conversation_state,
        persisted_recommendation_state=result.recommendation_state,
    )


def test_sparse_symptom_creates_followup_question():
    engine = TurnEngine()

    result = engine.run_turn(TurnInput(message="Ich habe Bauchschmerzen."))

    assert result.response_mode == "ask_followup"
    assert result.case_topic is not None
    assert result.case_topic.current_label == "Bauchschmerzen"
    assert result.medical_case is not None
    assert len(result.medical_case.observations) == 1
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "followup"
    assert result.conversation_state.active_question.question_intent == "duration"


def test_followup_answer_enriches_existing_observation():
    engine = TurnEngine()
    first = engine.run_turn(TurnInput(message="Ich habe Bauchschmerzen."))

    second = engine.run_turn(_next_input("Seit gestern Abend.", first))

    assert second.response_mode == "ask_followup"
    assert second.medical_case is not None
    assert second.medical_case.observations[0].attributes["duration_or_onset"] == "Seit gestern Abend."
    assert second.conversation_state.active_question is not None
    assert second.conversation_state.active_question.question_intent == "description"

    third = engine.run_turn(_next_input("Es ist eher ein dumpfer, dauernder Schmerz.", second))

    assert third.response_mode == "guide_next_step"
    assert third.medical_case is not None
    assert third.medical_case.observations[0].attributes["description"] == "Es ist eher ein dumpfer, dauernder Schmerz."
    assert third.conversation_state.active_question is not None
    assert third.conversation_state.active_question.kind == "closing_choice"


def test_recommendation_request_opens_closing_choice_and_then_recommendation():
    engine = TurnEngine()
    first = engine.run_turn(
        TurnInput(message="Ich bin seit gestern auf die Huefte gefallen, kann kaum auftreten und moechte eine Empfehlung.")
    )

    assert first.response_mode == "ask_followup"
    assert first.conversation_state.active_question is not None
    assert first.conversation_state.active_question.kind == "followup"
    assert first.conversation_state.active_question.question_intent == "description"

    second = engine.run_turn(_next_input("Es tut links an der Huefte stark weh und ich kann kaum auftreten.", first))

    assert second.response_mode == "guide_next_step"
    assert second.conversation_state.active_question is not None
    assert second.conversation_state.active_question.kind == "closing_choice"

    third = engine.run_turn(_next_input("Ja, Empfehlung.", second))

    assert third.response_mode == "recommend"
    assert third.recommendation_result is not None
    assert third.recommendation_result.allowed is True
    assert third.recommendation_result.summary is not None
    assert third.recommendation_result.next_step is not None


def test_open_followup_takes_precedence_over_topic_shift_text():
    engine = TurnEngine()
    first = engine.run_turn(TurnInput(message="Ich bin seit gestern auf die Huefte gefallen und kann kaum auftreten."))

    second = engine.run_turn(_next_input("Ausserdem habe ich jetzt Knieschmerzen.", first))

    assert second.response_mode == "guide_next_step"
    assert second.conversation_state.active_question is not None
    assert second.conversation_state.active_question.kind == "closing_choice"


def test_safety_signal_opens_safety_question():
    engine = TurnEngine()

    result = engine.run_turn(TurnInput(message="Ich habe Brustschmerzen und bekomme schlecht Luft."))

    assert result.response_mode == "ask_safety_question"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "safety_clarification"


def test_missing_subject_can_trigger_subject_clarification():
    engine = TurnEngine()

    result = engine.run_turn(TurnInput(message="Bauchschmerzen seit gestern."))

    assert result.response_mode == "ask_followup"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "subject_clarification"


def test_rich_injury_duration_answer_does_not_repeat_same_duration_question():
    engine = TurnEngine()

    first = engine.run_turn(TurnInput(message="Ich bin auf die Huefte gefallen und kann kaum auftreten."))

    assert first.response_mode == "ask_followup"
    assert first.conversation_state.active_question is not None
    assert first.conversation_state.active_question.question_intent == "duration"

    second = engine.run_turn(_next_input("Seit etwa zwei Stunden.", first))

    assert second.medical_case is not None
    assert second.medical_case.observations[0].attributes["duration_or_onset"] == "Seit etwa zwei Stunden."
    if second.conversation_state.active_question is not None:
        assert second.conversation_state.active_question.question_intent != "duration"
