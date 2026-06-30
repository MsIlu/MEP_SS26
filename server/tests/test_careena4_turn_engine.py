from unittest.mock import MagicMock

from careena4.application.dialogue.safety_clarification_builder import SafetyClarificationBuilder
from careena4.application.dialogue.raw_red_flag_detector import RawRedFlagDetector
from careena4.application.interpretation.turn_interpreter import TurnInterpreter
from careena4.models.interpretation import TurnInterpretation, TurnUnderstandingSignal
from careena4.application.orchestration.turn_engine import TurnEngine
from careena4.models.domain import (
    ActiveQuestion,
    ConversationState,
    GuidedInputContract,
    GuidedInputOption,
    MedicalCase,
    Observation,
)
from careena4.models.domain.safety_catalog import SafetyCatalogMatch
from careena4.models.turn import (
    EntryAssessment,
    ExtractedCaseInput,
    ExtractedObservationInput,
    ExtractedPersonInput,
    QuestionResolution,
    RecommendationRequestInput,
    SafetyState,
    TurnInput,
)
from careena4.models.understanding import ExtractedSymptomCandidate


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
    def extract(self, *, message: str, history_messages=None) -> ExtractedCaseInput:
        return ExtractedCaseInput(
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
    def extract(self, *, message: str, history_messages=None) -> ExtractedCaseInput:
        return ExtractedCaseInput(
            person=ExtractedPersonInput(
                relation="self",
                relation_source={"message_id": None, "source_span": "ich"},
                age=24,
                age_source={"message_id": None, "source_span": "24"},
                sex="female",
                sex_source={"message_id": None, "source_span": "weiblich"},
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


class _StubTurnInterpreter:
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
                topic_label="Kopfschmerzen",
                topic_description="Kopfschmerzen seit gestern",
                person=ExtractedPersonInput(
                    relation="self",
                    relation_source={"message_id": None, "source_span": "ich"},
                    age=24,
                    age_source={"message_id": None, "source_span": "24"},
                    sex="female",
                    sex_source={"message_id": None, "source_span": "weiblich"},
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
            ),
            current_turn_understanding=TurnUnderstandingSignal(
                symptoms=[
                    ExtractedSymptomCandidate(
                        source_label="Kopfschmerzen",
                        normalized_label_de="Kopfschmerzen",
                        clinical_term_de="Kopfschmerz",
                        confidence=0.9,
                    )
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
            no_match_reason=interpretation.current_turn_understanding.sts_no_match_reason,
            trace_notes=list(interpretation.current_turn_understanding.trace_notes),
        )


def _next_input(message: str, result):
    return TurnInput(
        message=message,
        persisted_medical_case=result.medical_case,
        persisted_conversation_state=result.conversation_state,
        persisted_recommendation_state=result.recommendation_state,
    )


def test_sparse_symptom_creates_person_followup_first():
    engine = TurnEngine(medical_extractor=_StubMedicalExtractor())

    result = engine.run_turn(TurnInput(message="Ich habe Bauchschmerzen."))

    assert result.response_mode == "ask_followup"
    assert result.medical_case is not None
    assert result.medical_case.topic is None
    assert len(result.medical_case.observations) == 1
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "person_clarification"


def test_missing_person_can_trigger_person_clarification():
    engine = TurnEngine(medical_extractor=_StubMedicalExtractor())

    result = engine.run_turn(TurnInput(message="Bauchschmerzen seit gestern."))

    assert result.response_mode == "ask_followup"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.kind == "person_clarification"


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

    assert result.response_mode == "ask_followup"
    assert result.conversation_state.active_question is not None
    assert result.conversation_state.active_question.question_intent == "free_description"
    assert "turn:additional_information_requested" in result.trace_notes


def test_turn_engine_uses_single_call_turn_interpreter_before_legacy_split_services():
    class _FailingService:
        def __getattr__(self, _name):
            raise AssertionError("legacy split service should not be used when turn interpreter succeeds")

    engine = TurnEngine(
        turn_interpreter=_StubTurnInterpreter(),
        entry_classifier=_FailingService(),
        medical_extractor=_FailingService(),
        turn_understanding_service=_FailingService(),
    )

    result = engine.run_turn(TurnInput(message="Ich habe seit gestern dumpfe Kopfschmerzen, etwa 5 von 10."))

    assert result.response_mode == "guide_next_step"
    assert result.recommendation_state.recommendation_allowed is True
    assert result.turn_interpretation is not None
    assert "turn_interpretation:primary_used" in result.trace_notes


def test_turn_engine_can_resolve_followup_via_single_call_turn_interpreter():
    class _FollowupTurnInterpreter:
        def interpret(self, *, message: str, active_question=None, medical_case=None, history_messages=None):
            return TurnInterpretation(
                entry_assessment=EntryAssessment(
                    in_scope=True,
                    medical_relevance="medical",
                    answers_active_question=True,
                    contains_new_medical_information=False,
                    message_kind="question_answer",
                ),
                question_resolution=QuestionResolution(
                    status="resolved",
                    answer_kind="duration_provided",
                    clear_active_question=True,
                    resolved_followup_id=active_question.target_followup_id if active_question is not None else None,
                    observation_patch={"onset": "seit gestern", "onset_source": {"message_id": None, "source_span": "seit gestern"}},
                ),
                case_input=None,
                current_turn_understanding=TurnUnderstandingSignal(),
            )

        def to_current_turn_understanding(self, *, raw_message: str, interpretation: TurnInterpretation):
            return None

    persisted_medical_case = MedicalCase(
        observations=[
            Observation(
                observation_id="obs-1",
                type="symptom",
                label="Bauchschmerzen",
                status="active",
            )
        ]
    )
    persisted_conversation_state = ConversationState(
        active_question=ActiveQuestion(
            kind="followup",
            question_intent="duration",
            target_observation_id="obs-1",
            target_followup_id="followup-1",
            prompt_text="Seit wann bestehen die Bauchschmerzen?",
            blocking=True,
        ),
        phase="followup",
    )

    engine = TurnEngine(
        turn_interpreter=_FollowupTurnInterpreter(),
    )
    result = engine.run_turn(
        TurnInput(
            message="Seit gestern.",
            persisted_medical_case=persisted_medical_case,
            persisted_conversation_state=persisted_conversation_state,
        )
    )

    assert result.medical_case is not None
    assert result.medical_case.observations[0].onset == "seit gestern"


def test_turn_engine_updates_symptom_input_draft_from_single_call_turn_interpreter_understanding():
    class _UnderstandingOnlyTurnInterpreter:
        def interpret(self, *, message: str, active_question=None, medical_case=None, history_messages=None):
            return TurnInterpretation(
                entry_assessment=EntryAssessment(
                    in_scope=True,
                    medical_relevance="medical",
                    answers_active_question=False,
                    contains_new_medical_information=False,
                    message_kind="dialogue_only",
                ),
                question_resolution=None,
                case_input=None,
                current_turn_understanding=TurnUnderstandingSignal(
                    symptoms=[
                        ExtractedSymptomCandidate(
                            source_label="Schwindel",
                            normalized_label_de="Schwindel",
                            clinical_term_de="Vertigo",
                            confidence=0.88,
                        )
                    ],
                    trace_notes=["turn_interpretation:understanding_only"],
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
                trace_notes=["turn_interpretation:understanding_only"],
            )

    engine = TurnEngine(turn_interpreter=_UnderstandingOnlyTurnInterpreter())

    result = engine.run_turn(TurnInput(message="Mir ist schwindelig."))

    assert result.symptom_input_draft is not None
    assert result.symptom_input_draft.symptom_labels() == ["Schwindel"]
    assert "symptom_input_draft:updated_from_understanding" in result.trace_notes


def test_turn_engine_resolves_safety_guided_answer_via_single_call_turn_interpreter_without_followup_fallback():
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
                    "question_resolution": None,
                    "case_input": None,
                    "current_turn_understanding": {
                        "symptoms": [],
                        "sts_matches": [],
                        "no_match_reason": None,
                        "trace_notes": [],
                    },
                    "trace_notes": [],
                }
            )

    class _FailingResolver:
        def resolve(self, **_kwargs):
            raise AssertionError("legacy followup resolver should not be used")

    safety_question = SafetyClarificationBuilder().build_active_question(
        safety_state=SafetyState(
            checked_sources=["raw_message"],
            red_flag_detected=True,
            red_flag_status="suspected",
            action="ask_safety_clarification",
            evidence_terms=["Brustschmerzen"],
        )
    )
    conversation_state = ConversationState(active_question=safety_question, phase="followup")
    engine = TurnEngine(
        turn_interpreter=TurnInterpreter(extraction_engine=_FakeExtractionEngine()),
        question_resolver=_FailingResolver(),
    )

    result = engine.run_turn(
        TurnInput(
            message="Nein",
            persisted_conversation_state=conversation_state,
        )
    )

    assert result.conversation_state.active_question is None
    assert "followup:fallback_resolution_used" not in result.trace_notes
    assert "turn_interpretation:guided_safety_resolution_applied" in result.trace_notes


def test_turn_engine_marks_split_fallbacks_when_turn_interpreter_is_missing():
    class _StubUnderstandingService:
        def extract(self, *, message: str):
            from careena4.models.understanding import CurrentTurnUnderstanding

            return CurrentTurnUnderstanding(
                raw_message=message,
                symptoms=[],
                sts_matches=[],
                no_match_reason=None,
            )

    engine = TurnEngine(
        medical_extractor=_ReadyMedicalExtractor(),
        turn_understanding_service=_StubUnderstandingService(),
    )

    result = engine.run_turn(TurnInput(message="Ich habe seit gestern dumpfe Kopfschmerzen, etwa 5 von 10."))

    assert "entry:fallback_classifier_used" in result.trace_notes
    assert "turn_understanding:fallback_service_used" in result.trace_notes
    assert "case_input:fallback_medical_extractor_used" in result.trace_notes


def test_turn_engine_treats_empty_primary_case_input_as_missing_and_uses_marked_fallback():
    class _EmptyCaseInputTurnInterpreter:
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
                    topic_label=None,
                    topic_description=None,
                    person=ExtractedPersonInput(
                        relation="unclear",
                        relation_source=None,
                        age=None,
                        age_source=None,
                        sex=None,
                        sex_source=None,
                    ),
                    observations=[],
                ),
                current_turn_understanding=TurnUnderstandingSignal(
                    symptoms=[
                        ExtractedSymptomCandidate(
                            source_label="Bauchschmerzen",
                            normalized_label_de="Bauchschmerzen",
                            confidence=0.95,
                        )
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

    engine = TurnEngine(
        turn_interpreter=_EmptyCaseInputTurnInterpreter(),
        medical_extractor=_StubMedicalExtractor(),
    )

    result = engine.run_turn(TurnInput(message="Ich habe Bauchschmerzen."))

    assert result.medical_case is not None
    assert len(result.medical_case.observations) == 1
    assert "turn_interpretation:empty_case_input_for_medical_turn" in result.trace_notes
    assert "case_input:fallback_medical_extractor_used" in result.trace_notes


def _make_followup_question_with_guided_input() -> ActiveQuestion:
    return ActiveQuestion(
        kind="followup",
        question_intent="duration",
        prompt_text="Wie lange hast du die Beschwerden schon?",
        guided_input=GuidedInputContract(
            options=[
                GuidedInputOption(code="lt_1d", label="Weniger als 1 Tag"),
                GuidedInputOption(code="1_3d", label="1-3 Tage"),
                GuidedInputOption(code="gt_3d", label="Mehr als 3 Tage"),
            ]
        ),
    )


def _make_safety_question_with_guided_input() -> ActiveQuestion:
    return ActiveQuestion(
        kind="safety_clarification",
        question_intent="free_description",
        prompt_text="Hast du Brustschmerzen?",
        guided_input=GuidedInputContract(
            options=[
                GuidedInputOption(code="yes", label="Ja"),
                GuidedInputOption(code="no", label="Nein"),
            ]
        ),
    )


def test_is_guided_input_answer_matches_exact_label():
    question = _make_followup_question_with_guided_input()
    assert TurnEngine._is_guided_input_answer("1-3 Tage", question) is True


def test_is_guided_input_answer_matches_case_insensitive():
    question = _make_followup_question_with_guided_input()
    assert TurnEngine._is_guided_input_answer("weniger als 1 tag", question) is True


def test_is_guided_input_answer_does_not_match_partial():
    question = _make_followup_question_with_guided_input()
    assert TurnEngine._is_guided_input_answer("1 Tag ungefaehr", question) is False


def test_is_guided_input_answer_no_active_question():
    assert TurnEngine._is_guided_input_answer("Ja", None) is False


def test_is_guided_input_answer_no_guided_input():
    question = ActiveQuestion(kind="followup", question_intent="duration", prompt_text="Wie lange?")
    assert TurnEngine._is_guided_input_answer("Ja", question) is False


def test_guided_input_fast_path_skips_legacy_split_services():
    entry_classifier = MagicMock()
    understanding_service = MagicMock()
    question = _make_followup_question_with_guided_input()
    state = ConversationState(active_question=question)
    engine = TurnEngine(
        entry_classifier=entry_classifier,
        turn_understanding_service=understanding_service,
    )

    result = engine.run_turn(TurnInput(message="1-3 Tage", persisted_conversation_state=state))

    assert "turn:guided_input_fast_path" in result.trace_notes
    entry_classifier.classify.assert_not_called()
    understanding_service.extract.assert_not_called()


def test_non_matching_message_does_not_trigger_fast_path():
    entry_classifier = MagicMock()
    entry_classifier.classify.return_value = MagicMock(
        in_scope=False,
        message_kind="out_of_scope",
        answers_active_question=False,
        contains_new_medical_information=False,
        medical_relevance="non_medical",
    )
    question = _make_followup_question_with_guided_input()
    state = ConversationState(active_question=question)
    engine = TurnEngine(entry_classifier=entry_classifier)

    engine.run_turn(TurnInput(message="Ich weiss es nicht genau", persisted_conversation_state=state))

    entry_classifier.classify.assert_called_once()


def test_safety_guided_input_triggers_fast_path():
    entry_classifier = MagicMock()
    understanding_service = MagicMock()
    question = _make_safety_question_with_guided_input()
    state = ConversationState(active_question=question)
    engine = TurnEngine(
        entry_classifier=entry_classifier,
        turn_understanding_service=understanding_service,
    )

    result = engine.run_turn(TurnInput(message="Nein", persisted_conversation_state=state))

    assert "turn:guided_input_fast_path" in result.trace_notes
    entry_classifier.classify.assert_not_called()
    understanding_service.extract.assert_not_called()

