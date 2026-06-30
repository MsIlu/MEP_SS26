import unittest
import json

from careena4.application.dialogue.question_builder import QuestionBuilder
from careena4.application.dialogue.question_resolver import QuestionResolver
from careena4.application.dialogue.safety_clarification_builder import SafetyClarificationBuilder
from careena4.application.entry.entry_classifier import EntryClassifier
from careena4.application.extraction.medical_extractor import MedicalExtractor
from careena4.application.interpretation.turn_interpreter import TurnInterpreter
from careena4.application.recommendation.recommendation_builder import RecommendationBuilder
from careena4.application.response.response_builder import ResponseBuilder
from careena4.application.understanding.sts_consultation_reason_catalog import StsConsultationReasonCatalog
from careena4.llm.call_control import CallModelConfig, ENTRY_CALL, EXTRACTION_CALL, TURN_INTERPRETATION_CALL
from careena4.llm.prompt_registry import load_prompt
from careena4.models.domain import ActiveQuestion, FollowupNeed, MedicalCase
from careena4.models.turn import SafetyState
from careena4.models.interpretation import TurnInterpretation
from careena4.models.turn import EntryAssessment, ExtractedCaseInput, QuestionResolution, TurnDecision


class _FakeExtractionEngine:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def extract(self, **kwargs):
        self.calls.append(kwargs)
        schema = kwargs["output_schema"]
        return schema.model_validate(self.payload)


class _FakeLLMClient:
    def __init__(self, text: str):
        self.client = object()
        self.default_model = "fake-model"
        self.text = text
        self.calls = []

    def complete(self, **kwargs):
        self.calls.append(kwargs)
        return self.text


class _FakeMedicalExtractor:
    def __init__(self, result: ExtractedCaseInput):
        self.result = result
        self.calls = []

    def extract(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


class _RawLlmBackedExtractionEngine:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def extract(self, **kwargs):
        raise AssertionError("partial-turn-interpreter path should bypass full-schema extraction")


class Careena4LlmPathTests(unittest.TestCase):
    def test_entry_classifier_prefers_llm_schema_result(self):
        classifier = EntryClassifier(
            extraction_engine=_FakeExtractionEngine(
                {
                    "in_scope": True,
                    "medical_relevance": "medical",
                    "answers_active_question": False,
                    "contains_new_medical_information": True,
                    "message_kind": "new_case_report",
                }
            ),
            call_model_config=CallModelConfig(default_model="default", overrides={}),
        )

        result = classifier.classify(message="Ich habe seit gestern Bauchschmerzen.")

        self.assertIsInstance(result, EntryAssessment)
        self.assertEqual(result.message_kind, "new_case_report")
        self.assertEqual(classifier.extraction_engine.calls[0]["call_name"], ENTRY_CALL)
        self.assertEqual(classifier.extraction_engine.calls[0]["prompt_name"], ENTRY_CALL)
        self.assertEqual(classifier.extraction_engine.calls[0]["prompt_version"], load_prompt(ENTRY_CALL).version)

    def test_question_resolver_prefers_llm_resolution(self):
        resolver = QuestionResolver(
            extraction_engine=_FakeExtractionEngine(
                {
                    "status": "resolved",
                    "answer_kind": "duration_provided",
                    "clear_active_question": True,
                    "resolved_followup_id": "followup-1",
                    "person_update": None,
                    "observation_patch": {
                        "onset": "seit gestern",
                        "onset_source": {"message_id": None, "source_span": "seit gestern"},
                        "body_site": None,
                        "body_site_source": None,
                        "description": None,
                        "description_source": None,
                        "severity": None,
                        "severity_source": None,
                    },
                    "additional_medical_information": False,
                    "extra_case_input": None,
                    "next_question_text": None,
                    "trace_notes": ["llm:resolved"],
                }
            ),
            call_model_config=CallModelConfig(default_model="default", overrides={}),
        )
        question = ActiveQuestion(
            kind="followup",
            question_intent="duration",
            target_followup_id="followup-1",
            target_observation_id="obs-1",
            prompt_text="Seit wann besteht das?",
            blocking=True,
        )

        result = resolver.resolve(question=question, message="Seit gestern.")

        self.assertIsInstance(result, QuestionResolution)
        self.assertEqual(result.status, "resolved")
        assert result.observation_patch is not None
        self.assertEqual(result.observation_patch.onset, "seit gestern")
        assert result.observation_patch.onset_source is not None
        self.assertEqual(result.observation_patch.onset_source.source_span, "seit gestern")

    def test_question_resolver_accepts_additional_case_input_from_llm(self):
        resolver = QuestionResolver(
            extraction_engine=_FakeExtractionEngine(
                {
                    "status": "resolved",
                    "answer_kind": "duration_plus_more",
                    "clear_active_question": True,
                    "resolved_followup_id": "followup-1",
                    "person_update": None,
                    "observation_patch": {
                        "onset": "seit gestern",
                        "onset_source": {"message_id": None, "source_span": "seit gestern"},
                        "body_site": None,
                        "body_site_source": None,
                        "description": None,
                        "description_source": None,
                        "severity": None,
                        "severity_source": None,
                    },
                    "additional_medical_information": True,
                    "extra_case_input": {
                        "topic_label": "Bauchschmerzen mit Uebelkeit",
                        "topic_description": "Bauchschmerzen zusaetzlich mit Uebelkeit",
                        "person": None,
                        "observations": [
                            {
                                "type": "symptom",
                                "label": "Uebelkeit",
                                "label_source": {"message_id": None, "source_span": "Uebelkeit"},
                                "status": "active",
                                "status_source": {"message_id": None, "source_span": "Uebelkeit"},
                                "person_ref": "self",
                                "person_ref_source": {"message_id": None, "source_span": "ich"},
                                "onset": None,
                                "onset_source": None,
                                "body_site": None,
                                "body_site_source": None,
                                "description": None,
                                "description_source": None,
                                "severity": None,
                                "severity_source": None,
                            }
                        ],
                    },
                    "next_question_text": None,
                    "trace_notes": ["llm:resolved"],
                }
            ),
            call_model_config=CallModelConfig(default_model="default", overrides={}),
        )
        question = ActiveQuestion(
            kind="followup",
            question_intent="duration",
            target_followup_id="followup-1",
            target_observation_id="obs-1",
            prompt_text="Seit wann besteht das?",
            blocking=True,
        )

        result = resolver.resolve(question=question, message="Seit gestern.")

        self.assertTrue(result.additional_medical_information)
        assert result.extra_case_input is not None
        self.assertEqual(result.extra_case_input.observations[0].label, "Uebelkeit")
        self.assertEqual(result.extra_case_input.topic_label, "Bauchschmerzen mit Uebelkeit")

    def test_question_resolver_accepts_severity_resolution_from_llm(self):
        resolver = QuestionResolver(
            extraction_engine=_FakeExtractionEngine(
                {
                    "status": "resolved",
                    "answer_kind": "severity_provided",
                    "clear_active_question": True,
                    "resolved_followup_id": "followup-1",
                    "person_update": None,
                    "observation_patch": {
                        "severity": "8/10",
                        "severity_source": {"message_id": None, "source_span": "8/10"},
                    },
                    "additional_medical_information": False,
                    "extra_case_input": None,
                    "next_question_text": None,
                    "trace_notes": ["llm:resolved"],
                }
            ),
            call_model_config=CallModelConfig(default_model="default", overrides={}),
        )
        question = ActiveQuestion(
            kind="followup",
            question_intent="severity",
            target_followup_id="followup-1",
            target_observation_id="obs-1",
            prompt_text="Wie stark ist das?",
            blocking=True,
        )

        result = resolver.resolve(question=question, message="8/10.")

        self.assertEqual(result.status, "resolved")
        assert result.observation_patch is not None
        self.assertEqual(result.observation_patch.severity, "8/10")

    def test_question_resolver_rejects_free_description_without_description_value(self):
        resolver = QuestionResolver(
            extraction_engine=_FakeExtractionEngine(
                {
                    "status": "resolved",
                    "answer_kind": "free_description_provided",
                    "clear_active_question": True,
                    "resolved_followup_id": "followup-1",
                    "person_update": None,
                    "observation_patch": {},
                    "additional_medical_information": False,
                    "extra_case_input": None,
                    "next_question_text": None,
                    "trace_notes": ["llm:resolved"],
                }
            ),
            call_model_config=CallModelConfig(default_model="default", overrides={}),
        )
        question = ActiveQuestion(
            kind="followup",
            question_intent="free_description",
            target_followup_id="followup-1",
            target_observation_id="obs-1",
            prompt_text="Bitte beschreiben Sie das genauer.",
            blocking=True,
        )

        result = resolver.resolve(question=question, message="Es ist irgendwie komisch.")

        self.assertEqual(result.status, "invalid")
        self.assertEqual(result.answer_kind, "invalid")

    def test_medical_extractor_prefers_llm_schema_result(self):
        extractor = MedicalExtractor(
            extraction_engine=_FakeExtractionEngine(
                {
                    "person": {
                        "relation": "self",
                        "relation_source": {"message_id": None, "source_span": "ich"},
                        "age": 24,
                        "age_source": {"message_id": None, "source_span": "24"},
                        "sex": "female",
                        "sex_source": {"message_id": None, "source_span": "weiblich"},
                    },
                    "observations": [
                        {
                            "type": "symptom",
                            "label": "Bauchschmerzen",
                            "label_source": {"message_id": None, "source_span": "Bauchschmerzen"},
                            "status": "active",
                            "status_source": {"message_id": None, "source_span": "Bauchschmerzen"},
                            "person_ref": "self",
                            "person_ref_source": {"message_id": None, "source_span": "ich"},
                            "onset": "seit gestern",
                            "onset_source": {"message_id": None, "source_span": "seit gestern"},
                            "body_site": "Bauch",
                            "body_site_source": {"message_id": None, "source_span": "Bauch"},
                            "description": None,
                            "description_source": None,
                            "severity": None,
                            "severity_source": None,
                        }
                    ],
                }
            ),
            call_model_config=CallModelConfig(default_model="default", overrides={}),
        )

        result = extractor.extract(message="Ich habe seit gestern Bauchschmerzen.")

        self.assertIsInstance(result, ExtractedCaseInput)
        self.assertEqual(result.observations[0].label, "Bauchschmerzen")
        self.assertIsNone(result.topic_label)
        self.assertIsNone(result.topic_description)
        assert result.person is not None
        self.assertEqual(result.person.age, 24)
        self.assertEqual(result.person.sex, "female")
        self.assertEqual(extractor.extraction_engine.calls[0]["call_name"], EXTRACTION_CALL)
        self.assertEqual(extractor.extraction_engine.calls[0]["prompt_name"], EXTRACTION_CALL)
        self.assertIn('"person": {', load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertIn('observation.type: "symptom"', load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertNotIn("injury", load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertIn('"observations": [', load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertIn('"topic_label": "<string|null>"', load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertIn('"topic_description": "<string|null>"', load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertIn('bleibt immer null', load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertIn('"label_source": {', load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertNotIn('"topic_signal"', load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertNotIn("Aktuelles Chat-Thema", extractor.extraction_engine.calls[0]["text"])

    def test_medical_extractor_returns_empty_case_input_when_llm_is_unavailable(self):
        extractor = MedicalExtractor(
            call_model_config=CallModelConfig(default_model="default", overrides={}),
        )

        result = extractor.extract(message="Ich habe seit gestern Bauchschmerzen.")

        self.assertIsInstance(result, ExtractedCaseInput)
        self.assertEqual(result.observations, [])
        self.assertIsNone(result.person)
        self.assertIsNone(result.topic_label)
        self.assertIsNone(result.topic_description)

    def test_turn_interpreter_prefers_single_call_schema_result(self):
        class _StubCatalog(StsConsultationReasonCatalog):
            def reasons_for_prompt(self):
                return "1001: Kopfschmerzen"

            def hydrate_match(self, match):
                hydrated = dict(match)
                hydrated["sts_label_de"] = hydrated.get("sts_label_de") or "Kopfschmerzen"
                hydrated["source_category_de"] = hydrated.get("source_category_de") or "Allgemein"
                hydrated["source_sts_levels_present"] = hydrated.get("source_sts_levels_present") or [3]
                return hydrated

        interpreter = TurnInterpreter(
            extraction_engine=_FakeExtractionEngine(
                {
                    "entry_assessment": {
                        "in_scope": True,
                        "medical_relevance": "medical",
                        "answers_active_question": False,
                        "contains_new_medical_information": True,
                        "message_kind": "new_case_report",
                    },
                    "question_resolution": None,
                    "case_input": {
                        "topic_label": "Kopfschmerzen",
                        "topic_description": "Kopfschmerzen seit gestern",
                        "person": None,
                        "observations": [
                            {
                                "type": "symptom",
                                "label": "Kopfschmerzen",
                                "label_source": {"message_id": None, "source_span": "Kopfschmerzen"},
                                "status": "active",
                                "status_source": {"message_id": None, "source_span": "Kopfschmerzen"},
                                "person_ref": "self",
                                "person_ref_source": {"message_id": None, "source_span": "ich"},
                                "onset": "seit gestern",
                                "onset_source": {"message_id": None, "source_span": "seit gestern"},
                                "body_site": None,
                                "body_site_source": None,
                                "description": "dumpf",
                                "description_source": {"message_id": None, "source_span": "dumpf"},
                                "severity": "5/10",
                                "severity_source": {"message_id": None, "source_span": "5/10"},
                            }
                        ],
                    },
                    "current_turn_understanding": {
                        "symptoms": [
                            {
                                "source_label": "Kopfschmerzen",
                                "is_medical": True,
                                "is_negated": False,
                                "normalized_label_de": "Kopfschmerzen",
                                "clinical_term_de": "Kopfschmerz",
                                "confidence": 0.91,
                                "reasoning_note": "direkt genannt",
                            }
                        ],
                        "sts_matches": [
                            {
                                "sts_id": "1001",
                                "match_confidence": 0.73,
                                "match_reason": "Symptom passt direkt",
                            }
                        ],
                        "no_match_reason": None,
                        "trace_notes": ["turn_interpreter:v1"],
                    },
                    "trace_notes": ["turn_interpretation:ok"],
                }
            ),
            call_model_config=CallModelConfig(default_model="default", overrides={}),
            sts_catalog=_StubCatalog(),
        )

        result = interpreter.interpret(message="Ich habe seit gestern dumpfe Kopfschmerzen.")

        self.assertIsInstance(result, TurnInterpretation)
        self.assertEqual(result.entry_assessment.message_kind, "new_case_report")
        assert result.case_input is not None
        self.assertEqual(result.case_input.topic_label, "Kopfschmerzen")
        assert result.current_turn_understanding is not None
        self.assertEqual(result.current_turn_understanding.sts_matches[0].sts_label_de, "Kopfschmerzen")
        self.assertEqual(interpreter.extraction_engine.calls[0]["call_name"], TURN_INTERPRETATION_CALL)
        self.assertEqual(interpreter.extraction_engine.calls[0]["prompt_name"], TURN_INTERPRETATION_CALL)
        self.assertEqual(
            interpreter.extraction_engine.calls[0]["prompt_version"],
            load_prompt(TURN_INTERPRETATION_CALL).version,
        )
        payload = json.loads(interpreter.extraction_engine.calls[0]["text"])
        self.assertEqual(payload["allowed_sts_consultation_reasons"], "1001: Kopfschmerzen")
        self.assertNotIn("sts_reasons", payload)

    def test_turn_interpreter_bridges_guided_safety_answer_without_legacy_followup_llm(self):
        interpreter = TurnInterpreter(
            extraction_engine=_FakeExtractionEngine(
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
            ),
            call_model_config=CallModelConfig(default_model="default", overrides={}),
        )
        question = SafetyClarificationBuilder().build_active_question(
            safety_state=SafetyState(
                checked_sources=["raw_message"],
                red_flag_detected=True,
                red_flag_status="suspected",
                action="ask_safety_clarification",
                evidence_terms=["Brustschmerzen"],
            )
        )

        result = interpreter.interpret(
            message="Nein",
            active_question=question,
        )

        assert result is not None
        assert result.question_resolution is not None
        self.assertEqual(result.question_resolution.status, "cleared_red_flag")
        self.assertEqual(result.question_resolution.answer_kind, "cleared_red_flag")
        self.assertTrue(result.question_resolution.clear_active_question)
        self.assertIn("turn_interpretation:guided_safety_resolution_applied", result.trace_notes)
        payload = json.loads(interpreter.extraction_engine.calls[0]["text"])
        self.assertEqual(payload["active_question"]["guided_input"]["mode"], "structured_required")
        self.assertEqual(payload["active_question"]["guided_input"]["options"][1]["code"], "no")

    def test_turn_interpreter_keeps_understanding_when_case_input_section_is_invalid(self):
        llm_client = _FakeLLMClient(
            json.dumps(
                {
                    "entry_assessment": {
                        "in_scope": True,
                        "medical_relevance": "medical",
                        "answers_active_question": False,
                        "contains_new_medical_information": True,
                        "message_kind": "new_case_report",
                    },
                    "question_resolution": None,
                    "case_input": {
                        "topic_label": None,
                        "topic_description": None,
                        "person": None,
                        "observations": [
                            {
                                "type": "symptom",
                                "status": "active",
                            }
                        ],
                    },
                    "current_turn_understanding": {
                        "symptoms": [
                            {
                                "source_label": "Bauchschmerzen",
                                "is_medical": True,
                                "is_negated": False,
                                "normalized_label_de": "Bauchschmerzen",
                                "clinical_term_de": "Abdominalsymptom",
                                "confidence": 0.94,
                                "reasoning_note": "direkt genannt",
                            }
                        ],
                        "sts_matches": [],
                        "no_match_reason": None,
                        "trace_notes": ["understanding:preserved"],
                    },
                    "trace_notes": ["turn_interpretation:partial_ok"],
                }
            )
        )
        interpreter = TurnInterpreter(
            extraction_engine=_RawLlmBackedExtractionEngine(llm_client),
            call_model_config=CallModelConfig(default_model="default", overrides={}),
        )

        result = interpreter.interpret(message="Ich habe Bauchschmerzen.")

        assert result is not None
        self.assertIsNone(result.case_input)
        assert result.current_turn_understanding is not None
        self.assertEqual(result.current_turn_understanding.symptoms[0].normalized_label_de, "Bauchschmerzen")
        self.assertIn("turn_interpretation:partial_ok", result.trace_notes)
        self.assertEqual(llm_client.calls[0]["call_name"], TURN_INTERPRETATION_CALL)
        self.assertTrue(llm_client.calls[0]["json_mode"])

    def test_response_builder_renders_recommendation_button_hint_for_guide_next_step(self):
        builder = ResponseBuilder()
        decision = TurnDecision(kind="guide_next_step", response_mode="guide_next_step")

        text = builder.build(
            decision=decision,
        )

        self.assertEqual(
            text,
            "Es liegen ausreichend Angaben für eine Handlungsempfehlung vor. Wenn du eine Handlungsempfehlung möchtest, nutze bitte den Empfehlungs-Button.",
        )

    def test_question_builder_uses_german_umlauts(self):
        builder = QuestionBuilder()

        description_question = builder.build_for_need(
            need=FollowupNeed(reason="description_missing"),
            focus_label="Hueftschmerzen",
        )
        additional_question = builder.build_additional_information_request()

        self.assertEqual(
            description_question.prompt_text,
            "Kannst du die Hueftschmerzen bitte etwas genauer beschreiben?",
        )
        self.assertIn("hinzufuegen", additional_question.prompt_text)

    def test_recommendation_builder_uses_german_umlauts(self):
        result = RecommendationBuilder().build(medical_case=MedicalCase())

        self.assertIn("für", result.summary)
        self.assertIn("fühlst", result.next_step)
        self.assertIn("ärztliche", result.limitations[1])


if __name__ == "__main__":
    unittest.main()

