import unittest

from careena4.application.dialogue.question_resolver import QuestionResolver
from careena4.application.entry.entry_classifier import EntryClassifier
from careena4.application.extraction.medical_extractor import MedicalExtractor
from careena4.application.response.response_builder import ResponseBuilder
from careena4.application.topic import TopicLabelBuilder
from careena4.llm.call_control import CallModelConfig, ENTRY_CALL, EXTRACTION_CALL, TOPIC_LABELING_CALL
from careena4.llm.prompt_registry import load_prompt
from careena4.models.domain import ActiveQuestion, MedicalCase, Source, Topic, TopicEntry
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
                    "recommendation_requested": True,
                }
            ),
            call_model_config=CallModelConfig(default_model="default", overrides={}),
        )

        result = classifier.classify(message="Ich habe seit gestern Bauchschmerzen.")

        self.assertIsInstance(result, EntryAssessment)
        self.assertEqual(result.message_kind, "new_case_report")
        self.assertTrue(result.recommendation_requested)
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
                        "topic_entries_to_add": [
                            {
                                "topic_part": "Bauchschmerzen mit Uebelkeit",
                                "source": {"message_id": None, "source_span": "Bauchschmerzen und Uebelkeit"},
                            }
                        ],
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
        self.assertEqual(result.extra_case_input.topic_entries_to_add[0].topic_part, "Bauchschmerzen mit Uebelkeit")

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

    def test_question_resolver_maps_closing_choice_no_to_more_information(self):
        resolver = QuestionResolver()
        question = ActiveQuestion(
            kind="closing_choice",
            question_intent="free_description",
            prompt_text="Moechten Sie jetzt eine Versorgungsempfehlung erhalten?",
        )

        result = resolver.resolve(question=question, message="Nein, weitere Angaben.")

        self.assertEqual(result.status, "resolved")
        self.assertEqual(result.recommendation_choice, "add_more_information")

    def test_question_resolver_maps_closing_choice_no_more_input_to_recommendation(self):
        resolver = QuestionResolver()
        question = ActiveQuestion(
            kind="closing_choice",
            question_intent="free_description",
            prompt_text="Moechten Sie jetzt eine Versorgungsempfehlung erhalten?",
        )

        result = resolver.resolve(question=question, message="Nein, mehr faellt mir gerade nicht ein.")

        self.assertEqual(result.status, "resolved")
        self.assertEqual(result.recommendation_choice, "recommendation_now")

    def test_question_resolver_keeps_topic_only_extra_case_input_for_closing_choice(self):
        resolver = QuestionResolver(
            medical_extractor=_FakeMedicalExtractor(
                ExtractedCaseInput(
                    topic_entries_to_add=[
                        {
                            "topic_part": "Fahrradsturz mit Arztfrage",
                            "source": {"message_id": None, "source_span": "Fahrradsturz, zu welchem Arzt"},
                        }
                    ]
                )
            )
        )
        question = ActiveQuestion(
            kind="closing_choice",
            question_intent="free_description",
            prompt_text="Moechten Sie jetzt eine Versorgungsempfehlung erhalten?",
            allows_additional_medical_info=True,
        )

        result = resolver.resolve(
            question=question,
            message="Nein, ich hatte ausserdem einen Fahrradsturz und will wissen zu welchem Arzt ich soll.",
        )

        self.assertEqual(result.status, "resolved")
        self.assertTrue(result.additional_medical_information)
        self.assertEqual(result.recommendation_choice, "add_more_information")
        assert result.extra_case_input is not None
        self.assertEqual(result.extra_case_input.observations, [])
        self.assertEqual(result.extra_case_input.topic_entries_to_add[0].topic_part, "Fahrradsturz mit Arztfrage")

    def test_medical_extractor_prefers_llm_schema_result(self):
        extractor = MedicalExtractor(
            extraction_engine=_FakeExtractionEngine(
                {
                    "topic_entries_to_add": [
                        {
                            "topic_part": "Bauchschmerzen",
                            "source": {"message_id": None, "source_span": "Bauchschmerzen"},
                        }
                    ],
                    "person": {
                        "relation": "self",
                        "relation_source": {"message_id": None, "source_span": "ich"},
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
        self.assertEqual(result.topic_entries_to_add[0].topic_part, "Bauchschmerzen")
        self.assertEqual(extractor.extraction_engine.calls[0]["call_name"], EXTRACTION_CALL)
        self.assertEqual(extractor.extraction_engine.calls[0]["prompt_name"], EXTRACTION_CALL)
        self.assertIn('"person": {', load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertIn('observation.type: "symptom"', load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertNotIn("injury", load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertIn('"observations": [', load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertIn('"topic_entries_to_add": [', load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertIn('"label_source": {', load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertNotIn('"topic_signal"', load_prompt(EXTRACTION_CALL).system_prompt)

    def test_medical_extractor_returns_empty_case_input_when_llm_is_unavailable(self):
        extractor = MedicalExtractor(
            call_model_config=CallModelConfig(default_model="default", overrides={}),
        )

        result = extractor.extract(message="Ich habe seit gestern Bauchschmerzen.")

        self.assertIsInstance(result, ExtractedCaseInput)
        self.assertEqual(result.observations, [])
        self.assertIsNone(result.person)
        self.assertEqual(result.topic_entries_to_add, [])

    def test_topic_label_builder_prefers_llm_schema_result(self):
        builder = TopicLabelBuilder(
            extraction_engine=_FakeExtractionEngine(
                {
                    "label": "Fahrradsturz mit Arztfrage",
                }
            ),
            call_model_config=CallModelConfig(default_model="default", overrides={}),
        )
        medical_case = MedicalCase(
            topic=Topic(
                label="",
                entries=[
                    TopicEntry(
                        topic_part="Fahrradsturz",
                        source=Source(source_span="Sturz mit dem Fahrrad"),
                    ),
                    TopicEntry(
                        topic_part="Welcher Arzt ist zustaendig",
                        source=Source(source_span="zu welchem Arzt ich soll"),
                    ),
                ],
            )
        )

        result = builder.build(medical_case=medical_case)

        self.assertEqual(result, "Fahrradsturz mit Arztfrage")
        self.assertEqual(builder.extraction_engine.calls[0]["call_name"], TOPIC_LABELING_CALL)
        self.assertEqual(builder.extraction_engine.calls[0]["prompt_name"], TOPIC_LABELING_CALL)
        self.assertEqual(
            builder.extraction_engine.calls[0]["prompt_version"],
            load_prompt(TOPIC_LABELING_CALL).version,
        )

    def test_response_builder_renders_explicit_closing_choice_options(self):
        builder = ResponseBuilder()
        question = ActiveQuestion(
            kind="closing_choice",
            question_intent="free_description",
            prompt_text="Moechten Sie jetzt eine Versorgungsempfehlung erhalten?",
            guided_input={
                "mode": "structured_preferred",
                "free_text_allowed": True,
                "options": [
                    {"code": "recommendation_now", "label": "Ja, Empfehlung", "effect_code": "recommendation_now"},
                    {"code": "add_more_information", "label": "Nein, weitere Angaben", "effect_code": "add_more_information"},
                ],
            },
        )
        decision = TurnDecision(kind="guide_next_step", response_mode="guide_next_step")

        text = builder.build(
            decision=decision,
            active_question=question,
        )

        self.assertEqual(
            text,
            "Moechten Sie jetzt eine Versorgungsempfehlung erhalten? Bitte antworten Sie mit: Ja, Empfehlung, Nein, weitere Angaben.",
        )


if __name__ == "__main__":
    unittest.main()
