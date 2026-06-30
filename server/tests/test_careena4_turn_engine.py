from unittest.mock import MagicMock

from careena4.application.dialogue.raw_red_flag_detector import RawRedFlagDetector
from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.domain import ActiveQuestion, ConversationState, GuidedInputContract, GuidedInputOption, TopicEntry
from careena4.models.domain.safety_catalog import SafetyCatalogMatch
from careena4.models.turn import (
    ExtractedCaseInput,
    ExtractedObservationInput,
    ExtractedPersonInput,
    ExtractedTopicEntryInput,
    RecommendationRequestInput,
    TurnInput,
)


def _make_cache_with_signal() -> MagicMock:
    match = SafetyCatalogMatch(
        evidence_term="brustschmerzen",
        matched_lay_term="Brustschmerzen",
        consultation_reason_source_id="1002",
        criterion_key="chest_pain_test",
        criterion_role="primary_criterion",
        urgency_effect="requires_safety_clarification",
        careena_decision_role="safety_relevant",
        is_safety_relevant=True,
        is_red_flag_candidate=True,
    )
    cache = MagicMock()
    cache.is_loaded = True
    cache.scan_text.return_value = [match]
    cache.scan_labels.return_value = []
    return cache


class _StubMedicalExtractor:
    def extract(self, *, message: str, topic_context: str | None = None, history_messages=None) -> ExtractedCaseInput:
        return ExtractedCaseInput(
            topic_entries_to_add=[
                ExtractedTopicEntryInput(
                    topic_part="Bauchschmerzen",
                    source={"message_id": None, "source_span": "Bauchschmerzen"},
                )
            ],
            observations=[
                ExtractedObservationInput(
                    type="symptom",
                    label="Bauchschmerzen",
                    status="active",
                    onset="seit gestern" if "seit gestern" in message.casefold() else None,
                )
            ]
        )


class _ReadyMedicalExtractor:
    def extract(self, *, message: str, topic_context: str | None = None, history_messages=None) -> ExtractedCaseInput:
        return ExtractedCaseInput(
            topic_entries_to_add=[
                ExtractedTopicEntryInput(
                    topic_part="Kopfschmerzen",
                    source={"message_id": None, "source_span": "Kopfschmerzen"},
                )
            ],
            person=ExtractedPersonInput(
                relation="self",
                relation_source={"message_id": None, "source_span": "ich"},
            ),
            observations=[
                ExtractedObservationInput(
                    type="symptom",
                    label="Kopfschmerzen",
                    status="active",
                    person_ref="self",
                    onset="seit gestern",
                    severity="5/10",
                    description="dumpf",
                )
            ],
        )


def _next_input(message: str, result):
    return TurnInput(
        message=message,
        persisted_medical_case=result.medical_case,
        persisted_conversation_state=result.conversation_state,
        persisted_recommendation_state=result.recommendation_state,
    )


def test_sparse_symptom_creates_subject_followup_first():
    engine = TurnEngine(medical_extractor=_StubMedicalExtractor())

    result = engine.run_turn(TurnInput(message="Ich habe Bauchschmerzen."))

    assert result.response_mode == "ask_followup"
    assert result.medical_case is not None
    assert result.medical_case.topic is not None
    assert result.medical_case.topic.label == "Bauchschmerzen"
    assert result.medical_case.topic.entries == [
        TopicEntry(
            topic_part="Bauchschmerzen",
            source={"message_id": None, "source_span": "Bauchschmerzen"},
        )
    ]
    assert len(result.medical_case.observations) == 1
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "subject_clarification"


def test_missing_subject_can_trigger_subject_clarification():
    engine = TurnEngine(medical_extractor=_StubMedicalExtractor())

    result = engine.run_turn(TurnInput(message="Bauchschmerzen seit gestern."))

    assert result.response_mode == "ask_followup"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "subject_clarification"


def test_safety_signal_opens_safety_question():
    cache = _make_cache_with_signal()
    engine = TurnEngine(raw_red_flag_detector=RawRedFlagDetector(catalog_cache=cache))

    result = engine.run_turn(TurnInput(message="Ich habe Brustschmerzen und bekomme schlecht Luft."))

    assert result.response_mode == "ask_safety_question"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "safety_clarification"


def test_chat_turn_with_sufficient_information_returns_guide_next_step_when_case_is_ready():
    engine = TurnEngine(medical_extractor=_ReadyMedicalExtractor())

    result = engine.run_turn(TurnInput(message="Ich habe seit gestern dumpfe Kopfschmerzen, etwa 5 von 10."))

    assert result.response_mode == "guide_next_step"
    assert result.conversation_state.active_question is None
    assert result.recommendation_state.recommendation_allowed is True


def test_recommendation_request_builds_recommendation_when_case_is_ready():
    engine = TurnEngine(medical_extractor=_ReadyMedicalExtractor())
    first = engine.run_turn(TurnInput(message="Ich habe seit gestern dumpfe Kopfschmerzen, etwa 5 von 10."))

    result = engine.request_recommendation(
        RecommendationRequestInput(
            persisted_medical_case=first.medical_case,
            persisted_conversation_state=first.conversation_state,
            persisted_recommendation_state=first.recommendation_state,
        )
    )

    assert result.response_mode == "recommend"
    assert result.recommendation_result is not None
    assert result.recommendation_state.recommendation_allowed is True


def test_free_text_recommendation_question_does_not_trigger_recommendation_path():
    engine = TurnEngine()

    result = engine.run_turn(TurnInput(message="Was soll ich tun?"))

    assert result.response_mode == "request_case_description"


# --- Guided-input fast-path tests ---

def _make_followup_question_with_guided_input() -> ActiveQuestion:
    return ActiveQuestion(
        kind="followup",
        question_intent="duration",
        prompt_text="Wie lange haben Sie die Beschwerden schon?",
        guided_input=GuidedInputContract(
            options=[
                GuidedInputOption(code="lt_1d", label="Weniger als 1 Tag"),
                GuidedInputOption(code="1_3d", label="1–3 Tage"),
                GuidedInputOption(code="gt_3d", label="Mehr als 3 Tage"),
            ]
        ),
    )


def _make_safety_question_with_guided_input() -> ActiveQuestion:
    return ActiveQuestion(
        kind="safety_clarification",
        question_intent="free_description",
        prompt_text="Haben Sie Brustschmerzen?",
        guided_input=GuidedInputContract(
            options=[
                GuidedInputOption(code="yes", label="Ja"),
                GuidedInputOption(code="no", label="Nein"),
            ]
        ),
    )


def test_is_guided_input_answer_matches_exact_label():
    question = _make_followup_question_with_guided_input()
    assert TurnEngine._is_guided_input_answer("1–3 Tage", question) is True


def test_is_guided_input_answer_matches_case_insensitive():
    question = _make_followup_question_with_guided_input()
    assert TurnEngine._is_guided_input_answer("weniger als 1 tag", question) is True


def test_is_guided_input_answer_does_not_match_partial():
    question = _make_followup_question_with_guided_input()
    assert TurnEngine._is_guided_input_answer("1 Tag ungefähr", question) is False


def test_is_guided_input_answer_no_active_question():
    assert TurnEngine._is_guided_input_answer("Ja", None) is False


def test_is_guided_input_answer_no_guided_input():
    question = ActiveQuestion(kind="followup", question_intent="duration", prompt_text="Wie lange?")
    assert TurnEngine._is_guided_input_answer("Ja", question) is False


def test_guided_input_fast_path_skips_entry_classifier():
    entry_classifier = MagicMock()
    understanding_service = MagicMock()
    question = _make_followup_question_with_guided_input()
    state = ConversationState(active_question=question)
    engine = TurnEngine(entry_classifier=entry_classifier, turn_understanding_service=understanding_service)

    engine.run_turn(TurnInput(message="1–3 Tage", persisted_conversation_state=state))

    entry_classifier.classify.assert_not_called()
    understanding_service.extract.assert_not_called()


def test_guided_input_fast_path_trace_note_present():
    question = _make_followup_question_with_guided_input()
    state = ConversationState(active_question=question)
    engine = TurnEngine()

    result = engine.run_turn(TurnInput(message="Mehr als 3 Tage", persisted_conversation_state=state))

    assert "turn:guided_input_fast_path" in result.trace_notes


def test_non_matching_message_does_not_trigger_fast_path():
    entry_classifier = MagicMock()
    entry_classifier.classify.return_value = MagicMock(
        in_scope=False, message_kind="out_of_scope", answers_active_question=False,
        contains_new_medical_information=False, medical_relevance="non_medical",
    )
    question = _make_followup_question_with_guided_input()
    state = ConversationState(active_question=question)
    engine = TurnEngine(entry_classifier=entry_classifier)

    engine.run_turn(TurnInput(message="Ich weiß es nicht genau", persisted_conversation_state=state))

    entry_classifier.classify.assert_called_once()


def test_safety_guided_input_triggers_fast_path():
    entry_classifier = MagicMock()
    understanding_service = MagicMock()
    question = _make_safety_question_with_guided_input()
    state = ConversationState(active_question=question)
    engine = TurnEngine(entry_classifier=entry_classifier, turn_understanding_service=understanding_service)

    result = engine.run_turn(TurnInput(message="Nein", persisted_conversation_state=state))

    assert "turn:guided_input_fast_path" in result.trace_notes
    entry_classifier.classify.assert_not_called()
    understanding_service.extract.assert_not_called()
