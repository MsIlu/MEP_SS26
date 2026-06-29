from unittest.mock import MagicMock

from careena4.application.dialogue.raw_red_flag_detector import RawRedFlagDetector
from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.domain import TopicEntry
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


def test_chat_turn_with_sufficient_information_returns_guide_next_step_without_closing_choice():
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
