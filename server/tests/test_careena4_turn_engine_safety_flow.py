import sys
from pathlib import Path
from unittest.mock import MagicMock

SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


from careena4.application.dialogue.raw_red_flag_detector import RawRedFlagDetector
from careena4.application.interpretation.turn_interpreter import TurnInterpreter
from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.application.safety.case_safety_evaluator import CaseSafetyEvaluator
from careena4.models.domain.safety_catalog import SafetyCatalogMatch
from careena4.models.interpretation import TurnInterpretation, TurnUnderstandingSignal
from careena4.models.turn import EntryAssessment, ExtractedCaseInput, ExtractedObservationInput, TurnInput
from careena4.models.understanding import ExtractedSymptomCandidate


def _safety_match(term: str = "atemnot") -> SafetyCatalogMatch:
    return SafetyCatalogMatch(
        evidence_term=term,
        matched_lay_term=term.capitalize(),
        consultation_reason_source_id="1008",
        criterion_key="dyspnea_test",
        criterion_role="primary_criterion",
        urgency_effect="requires_safety_clarification",
        careena_decision_role="safety_relevant",
        is_safety_relevant=True,
        is_red_flag_candidate=True,
    )


def _engine_with_cache(*, terms: list[str]) -> TurnEngine:
    """Build a TurnEngine with a mocked catalog cache that fires for the given terms."""
    cache = MagicMock()
    cache.is_loaded = True
    cache.scan_text.return_value = [_safety_match(t) for t in terms]
    cache.scan_labels.return_value = []
    return TurnEngine(raw_red_flag_detector=RawRedFlagDetector(catalog_cache=cache))


class _SafetyCaseTurnInterpreter:
    def interpret(self, *, message: str, active_question=None, medical_case=None, history_messages=None):
        return TurnInterpretation(
            entry_assessment=EntryAssessment(
                in_scope=True,
                medical_relevance="medical",
                answers_active_question=False,
                contains_new_medical_information=True,
                message_kind="new_case_report",
            ),
            question_resolution=None,
            case_input=ExtractedCaseInput(
                topic_label="Atemnot",
                topic_description="Atemnot und Brustschmerzen",
                observations=[
                    ExtractedObservationInput(
                        type="symptom",
                        normalized_label_de="Atemnot",
                        status="active",
                        person_ref="self",
                    ),
                    ExtractedObservationInput(
                        type="symptom",
                        normalized_label_de="Brustschmerzen",
                        status="active",
                        person_ref="self",
                    ),
                ],
            ),
            current_turn_understanding=TurnUnderstandingSignal(
                symptoms=[
                    ExtractedSymptomCandidate(
                        source_label="Atemnot",
                        normalized_label_de="Atemnot",
                        confidence=0.95,
                    ),
                    ExtractedSymptomCandidate(
                        source_label="Brustschmerzen",
                        normalized_label_de="Brustschmerzen",
                        confidence=0.95,
                    ),
                ],
            ),
        )

    def to_current_turn_understanding(self, *, raw_message: str, interpretation: TurnInterpretation):
        from careena4.models.understanding import CurrentTurnUnderstanding

        assert interpretation.current_turn_understanding is not None
        return CurrentTurnUnderstanding(
            raw_message=raw_message,
            symptoms=[symptom.model_copy(deep=True) for symptom in interpretation.current_turn_understanding.symptoms],
            sts_matches=[],
            no_match_reason=None,
            trace_notes=[],
        )


def test_raw_suspected_dyspnea_opens_safety_question_without_emergency():
    engine = _engine_with_cache(terms=["atemnot"])

    result = engine.run_turn(
        TurnInput(
            message="Ich bekomme schlecht Luft",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    assert result.response_mode == "ask_safety_question"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "safety_clarification"
    assert result.conversation_state.active_question.safety_context is not None
    assert result.conversation_state.active_question.blocking is True
    assert "turn:safety_clarification_opened" in result.trace_notes
    assert result.response_mode != "emergency"


def test_raw_safety_question_opens_after_case_truth_and_symptom_draft_are_kept():
    cache = MagicMock()
    cache.is_loaded = True
    cache.scan_text.return_value = [_safety_match("atemnot")]
    cache.scan_labels.return_value = []
    engine = TurnEngine(
        raw_red_flag_detector=RawRedFlagDetector(catalog_cache=cache),
        turn_interpreter=_SafetyCaseTurnInterpreter(),
    )

    result = engine.run_turn(
        TurnInput(
            message="Ich habe Atemnot und Brustschmerzen.",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    assert result.response_mode == "ask_safety_question"
    assert result.medical_case.topic is not None
    assert result.medical_case.topic.label == "Atemnot"
    assert len(result.medical_case.observations) == 2
    assert result.symptom_input_draft is not None
    assert result.symptom_input_draft.symptom_labels() == ["Atemnot", "Brustschmerzen"]
    assert "turn:safety_clarification_opened" in result.trace_notes


def test_yes_to_open_safety_question_confirms_emergency():
    engine = _engine_with_cache(terms=["atemnot"])

    first = engine.run_turn(
        TurnInput(
            message="Ich bekomme schlecht Luft",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    second = engine.run_turn(
        TurnInput(
            message="yes",
            session_id="test-session",
            turn_id="turn-2",
            persisted_conversation_state=first.conversation_state,
            persisted_medical_case=first.medical_case,
            persisted_recommendation_state=first.recommendation_state,
        )
    )

    assert second.response_mode == "emergency"
    assert "turn:safety_confirmation_emergency" in second.trace_notes


def test_no_to_open_safety_question_clears_question_without_emergency():
    engine = _engine_with_cache(terms=["atemnot"])

    first = engine.run_turn(
        TurnInput(
            message="Ich bekomme schlecht Luft",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    second = engine.run_turn(
        TurnInput(
            message="no",
            session_id="test-session",
            turn_id="turn-2",
            persisted_conversation_state=first.conversation_state,
            persisted_medical_case=first.medical_case,
            persisted_recommendation_state=first.recommendation_state,
        )
    )

    assert second.response_mode != "emergency"
    assert second.conversation_state.active_question is None


def test_unsure_to_open_safety_question_keeps_question_open():
    engine = _engine_with_cache(terms=["atemnot"])

    first = engine.run_turn(
        TurnInput(
            message="Ich bekomme schlecht Luft",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    second = engine.run_turn(
        TurnInput(
            message="unsure",
            session_id="test-session",
            turn_id="turn-2",
            persisted_conversation_state=first.conversation_state,
            persisted_medical_case=first.medical_case,
            persisted_recommendation_state=first.recommendation_state,
        )
    )

    assert second.response_mode == "ask_safety_question"
    assert second.conversation_state.active_question is not None
    assert second.conversation_state.active_question.kind == "safety_clarification"
    assert second.conversation_state.active_question.safety_context is not None


def test_structured_safety_answer_does_not_create_new_symptom_from_yes_no_text():
    cache = MagicMock()
    cache.is_loaded = True
    cache.scan_text.return_value = [_safety_match("atemnot")]
    cache.scan_labels.return_value = []
    cache.scan_lay_terms.return_value = [_safety_match("atemnot")]
    cache.scan_clinical_terms.return_value = []
    first_engine = TurnEngine(
        raw_red_flag_detector=RawRedFlagDetector(catalog_cache=cache),
        case_safety_evaluator=CaseSafetyEvaluator(catalog_cache=cache),
        turn_interpreter=_SafetyCaseTurnInterpreter(),
    )
    first = first_engine.run_turn(
        TurnInput(
            message="Ich habe Atemnot und Brustschmerzen.",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    class _FakeExtractionEngine:
        def extract(self, **kwargs):
            return kwargs["output_schema"].model_validate(
                {
                    "entry_assessment": {
                        "in_scope": True,
                        "medical_relevance": "medical",
                        "answers_active_question": True,
                        "contains_new_medical_information": False,
                        "message_kind": "question_answer",
                    },
                    "question_resolution": {
                        "status": "cleared_red_flag",
                        "answer_kind": "cleared_red_flag",
                        "clear_active_question": True,
                        "resolved_followup_id": None,
                        "person_update": None,
                        "observation_patch": None,
                        "additional_medical_information": False,
                        "extra_case_input": None,
                        "next_question_text": None,
                        "trace_notes": [],
                    },
                    "case_input": None,
                    "current_turn_understanding": {
                        "symptoms": [
                            {
                                "source_label": "Nein",
                                "is_medical": True,
                                "is_negated": False,
                                "normalized_label_de": "keine anderen Symptome",
                                "clinical_term_de": None,
                                "confidence": 1.0,
                                "reasoning_note": "falsch als neues Symptom verstanden",
                            }
                        ],
                        "trace_notes": [],
                    },
                    "trace_notes": [],
                }
            )

    second_engine = TurnEngine(
        turn_interpreter=TurnInterpreter(extraction_engine=_FakeExtractionEngine()),
        case_safety_evaluator=CaseSafetyEvaluator(catalog_cache=cache),
    )
    second = second_engine.run_turn(
        TurnInput(
            message="Nein",
            session_id="test-session",
            turn_id="turn-2",
            persisted_conversation_state=first.conversation_state,
            persisted_medical_case=first.medical_case,
            persisted_recommendation_state=first.recommendation_state,
            persisted_symptom_input_draft=first.symptom_input_draft,
        )
    )

    assert second.symptom_input_draft is not None
    assert second.symptom_input_draft.symptom_labels() == ["Atemnot", "Brustschmerzen"]
    assert "symptom_input_draft:projected_from_case" in second.trace_notes
    assert second.response_mode != "ask_safety_question"
    assert (
        second.conversation_state.active_question is None
        or second.conversation_state.active_question.kind != "safety_clarification"
    )
    assert len(second.conversation_state.cleared_safety_clarifications) == 1
    assert "safety_clarification:case_candidate_already_cleared" in second.trace_notes


def test_case_safety_can_reopen_after_case_slice_changes():
    cache = MagicMock()
    cache.is_loaded = True
    cache.scan_text.return_value = []
    cache.scan_labels.return_value = []
    cache.scan_lay_terms.side_effect = lambda labels: (
        [_safety_match("atemnot")] if "Atemnot" in labels else []
    )
    cache.scan_clinical_terms.return_value = []

    first_engine = TurnEngine(
        raw_red_flag_detector=RawRedFlagDetector(catalog_cache=cache),
        case_safety_evaluator=CaseSafetyEvaluator(catalog_cache=cache),
        turn_interpreter=_SafetyCaseTurnInterpreter(),
    )
    first = first_engine.run_turn(
        TurnInput(
            message="Ich habe Atemnot und Brustschmerzen.",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    class _ClearingExtractionEngine:
        def extract(self, **kwargs):
            return kwargs["output_schema"].model_validate(
                {
                    "entry_assessment": {
                        "in_scope": True,
                        "medical_relevance": "medical",
                        "answers_active_question": True,
                        "contains_new_medical_information": False,
                        "message_kind": "question_answer",
                    },
                    "question_resolution": {
                        "status": "cleared_red_flag",
                        "answer_kind": "cleared_red_flag",
                        "clear_active_question": True,
                        "resolved_followup_id": None,
                        "person_update": None,
                        "observation_patch": None,
                        "additional_medical_information": False,
                        "extra_case_input": None,
                        "next_question_text": None,
                        "trace_notes": [],
                    },
                    "case_input": None,
                    "current_turn_understanding": {"symptoms": [], "trace_notes": []},
                    "trace_notes": [],
                }
            )

    second_engine = TurnEngine(
        turn_interpreter=TurnInterpreter(extraction_engine=_ClearingExtractionEngine()),
        case_safety_evaluator=CaseSafetyEvaluator(catalog_cache=cache),
    )
    second = second_engine.run_turn(
        TurnInput(
            message="Nein",
            session_id="test-session",
            turn_id="turn-2",
            persisted_conversation_state=first.conversation_state,
            persisted_medical_case=first.medical_case,
            persisted_recommendation_state=first.recommendation_state,
            persisted_symptom_input_draft=first.symptom_input_draft,
        )
    )

    class _AdditionalSymptomTurnInterpreter:
        def interpret(self, *, message: str, active_question=None, medical_case=None, history_messages=None):
            return TurnInterpretation(
                entry_assessment=EntryAssessment(
                    in_scope=True,
                    medical_relevance="medical",
                    answers_active_question=False,
                    contains_new_medical_information=True,
                    message_kind="same_case_update",
                ),
                question_resolution=None,
                case_input=ExtractedCaseInput(
                    observations=[
                        ExtractedObservationInput(
                            type="symptom",
                            normalized_label_de="Schwindel",
                            status="active",
                            person_ref="self",
                        )
                    ]
                ),
                current_turn_understanding=TurnUnderstandingSignal(
                    symptoms=[
                        ExtractedSymptomCandidate(
                            source_label="Schwindel",
                            normalized_label_de="Schwindel",
                            confidence=0.9,
                        )
                    ]
                ),
            )

    third_state = second.conversation_state.model_copy(deep=True)
    third_state.active_question = None
    third_state.followup_needs = []
    third = TurnEngine(
        turn_interpreter=_AdditionalSymptomTurnInterpreter(),
        case_safety_evaluator=CaseSafetyEvaluator(catalog_cache=cache),
    ).run_turn(
        TurnInput(
            message="Jetzt ist mir auch schwindelig.",
            session_id="test-session",
            turn_id="turn-3",
            persisted_conversation_state=third_state,
            persisted_medical_case=second.medical_case,
            persisted_recommendation_state=second.recommendation_state,
            persisted_symptom_input_draft=second.symptom_input_draft,
        )
    )

    assert len(second.conversation_state.cleared_safety_clarifications) == 1
    assert third.response_mode == "ask_safety_question"
    assert third.conversation_state.active_question is not None
    assert third.conversation_state.active_question.kind == "safety_clarification"
    assert "turn:case_safety_clarification_selected" in third.trace_notes


def test_live_style_resolved_negated_safety_answer_persists_cleared_state():
    cache = MagicMock()
    cache.is_loaded = True
    cache.scan_text.return_value = [_safety_match("atemnot")]
    cache.scan_labels.return_value = []
    cache.scan_lay_terms.return_value = [_safety_match("atemnot")]
    cache.scan_clinical_terms.return_value = []

    first = TurnEngine(
        raw_red_flag_detector=RawRedFlagDetector(catalog_cache=cache),
        case_safety_evaluator=CaseSafetyEvaluator(catalog_cache=cache),
        turn_interpreter=_SafetyCaseTurnInterpreter(),
    ).run_turn(
        TurnInput(
            message="Ich habe Atemnot und Brustschmerzen.",
            session_id="test-session",
            turn_id="turn-1",
        )
    )

    class _LiveStyleSafetyAnswerEngine:
        def extract(self, **kwargs):
            return kwargs["output_schema"].model_validate(
                {
                    "entry_assessment": {
                        "in_scope": True,
                        "medical_relevance": "medical",
                        "answers_active_question": True,
                        "contains_new_medical_information": False,
                        "message_kind": "question_answer",
                    },
                    "question_resolution": {
                        "status": "resolved",
                        "answer_kind": "negated",
                        "clear_active_question": True,
                        "resolved_followup_id": None,
                        "person_update": None,
                        "observation_patch": None,
                        "additional_medical_information": False,
                        "extra_case_input": None,
                        "next_question_text": None,
                        "trace_notes": [],
                    },
                    "case_input": None,
                    "current_turn_understanding": None,
                    "trace_notes": [],
                }
            )

    second = TurnEngine(
        turn_interpreter=TurnInterpreter(extraction_engine=_LiveStyleSafetyAnswerEngine()),
        case_safety_evaluator=CaseSafetyEvaluator(catalog_cache=cache),
    ).run_turn(
        TurnInput(
            message="Nein",
            session_id="test-session",
            turn_id="turn-2",
            persisted_conversation_state=first.conversation_state,
            persisted_medical_case=first.medical_case,
            persisted_recommendation_state=first.recommendation_state,
            persisted_symptom_input_draft=first.symptom_input_draft,
        )
    )

    assert second.response_mode != "ask_safety_question"
    assert len(second.conversation_state.cleared_safety_clarifications) == 1
    assert "safety_clarification:cleared_state_persisted" in second.trace_notes
    assert "safety_clarification:case_candidate_already_cleared" in second.trace_notes
