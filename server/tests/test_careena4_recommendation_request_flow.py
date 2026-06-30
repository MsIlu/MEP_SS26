from unittest.mock import MagicMock

from careena4.application.dialogue.raw_red_flag_detector import RawRedFlagDetector
from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.domain.safety_catalog import SafetyCatalogMatch
from careena4.models.turn import (
    ExtractedCaseInput,
    ExtractedObservationInput,
    ExtractedPersonInput,
    RecommendationRequestInput,
    TurnInput,
)


class _SparseMedicalExtractor:
    def extract(self, *, message: str, history_messages=None) -> ExtractedCaseInput:
        return ExtractedCaseInput(
            observations=[
                ExtractedObservationInput(
                    type="symptom",
                    label="Bauchschmerzen",
                    status="active",
                )
            ],
        )


class _ReadyMedicalExtractor:
    def extract(self, *, message: str, history_messages=None) -> ExtractedCaseInput:
        return ExtractedCaseInput(
            person=ExtractedPersonInput(
                relation="self",
                relation_source={"message_id": None, "source_span": "ich"},
                age=24,
                age_source={"message_id": None, "source_span": "24"},
                sex="male",
                sex_source={"message_id": None, "source_span": "männlich"},
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


def _request_input_from_result(result) -> RecommendationRequestInput:
    return RecommendationRequestInput(
        persisted_medical_case=result.medical_case,
        persisted_conversation_state=result.conversation_state,
        persisted_recommendation_state=result.recommendation_state,
    )


def _safety_engine() -> TurnEngine:
    match = SafetyCatalogMatch(
        evidence_term="atemnot",
        matched_lay_term="Atemnot",
        consultation_reason_source_id="1008",
        criterion_key="dyspnea_test",
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
    return TurnEngine(raw_red_flag_detector=RawRedFlagDetector(catalog_cache=cache))


def test_recommendation_request_requests_additional_information_without_case():
    engine = TurnEngine()

    result = engine.request_recommendation(RecommendationRequestInput())

    assert result.response_mode == "ask_followup"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.question_intent == "free_description"


def test_recommendation_request_keeps_active_followup_block():
    engine = TurnEngine(medical_extractor=_SparseMedicalExtractor())
    first = engine.run_turn(TurnInput(message="Ich habe Bauchschmerzen."))

    result = engine.request_recommendation(_request_input_from_result(first))

    assert result.response_mode == "ask_followup"
    assert result.conversation_state.active_question is not None


def test_recommendation_request_keeps_active_safety_block():
    engine = _safety_engine()
    first = engine.run_turn(TurnInput(message="Ich bekomme schlecht Luft."))

    result = engine.request_recommendation(_request_input_from_result(first))

    assert result.response_mode == "ask_safety_question"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "safety_clarification"


def test_recommendation_request_delivers_recommendation_when_case_is_ready():
    engine = TurnEngine(medical_extractor=_ReadyMedicalExtractor())
    first = engine.run_turn(TurnInput(message="Ich habe seit gestern dumpfe Kopfschmerzen, etwa 5 von 10."))

    result = engine.request_recommendation(_request_input_from_result(first))

    assert result.response_mode == "recommend"
    assert result.recommendation_result is not None
