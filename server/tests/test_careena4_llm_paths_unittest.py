import unittest

from careena4.application.dialogue.question_resolver import QuestionResolver
from careena4.application.entry.entry_classifier import EntryClassifier
from careena4.application.extraction.medical_extractor import MedicalExtractor
from careena4.application.response.response_builder import ResponseBuilder
from careena4.llm.call_control import CallModelConfig, ENTRY_CALL, EXTRACTION_CALL
from careena4.llm.prompt_registry import load_prompt
from careena4.models.domain import ActiveQuestion
from careena4.models.turn import EntryAssessment, ExtractionClaims, QuestionResolution, TurnDecision


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


class Careena4LlmPathTests(unittest.TestCase):
    def test_entry_classifier_prefers_llm_schema_result(self):
        classifier = EntryClassifier(
            extraction_engine=_FakeExtractionEngine(
                {
                    "in_scope": True,
                    "medical_relevance": "medical",
                    "answers_active_question": False,
                    "contains_new_medical_information": True,
                    "possible_topic_shift": False,
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
                    "extracted_answer_attributes": {"duration_or_onset": "seit gestern"},
                    "additional_medical_information": False,
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
        self.assertEqual(result.extracted_answer_attributes["duration_or_onset"], "seit gestern")

    def test_question_resolver_canonicalizes_duration_key_from_llm(self):
        resolver = QuestionResolver(
            extraction_engine=_FakeExtractionEngine(
                {
                    "status": "resolved",
                    "answer_kind": "duration_provided",
                    "clear_active_question": True,
                    "resolved_followup_id": "followup-1",
                    "extracted_answer_attributes": {"duration": "seit gestern"},
                    "additional_medical_information": False,
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

        self.assertEqual(result.extracted_answer_attributes["duration_or_onset"], "seit gestern")
        self.assertNotIn("duration", result.extracted_answer_attributes)

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

    def test_medical_extractor_prefers_llm_schema_result(self):
        extractor = MedicalExtractor(
            extraction_engine=_FakeExtractionEngine(
                {
                    "topic_signal": "bauchschmerzen",
                    "subject_claims": {"relation": "self"},
                    "observations": [
                        {
                            "type": "symptom",
                            "label": "Bauchschmerzen",
                            "normalized_concept": "bauchschmerzen",
                            "subject_ref": "self",
                            "negated": False,
                            "attributes": {"duration_or_onset": "seit gestern"},
                            "source_span": "Bauchschmerzen",
                        }
                    ],
                }
            ),
            call_model_config=CallModelConfig(default_model="default", overrides={}),
        )

        result = extractor.extract(message="Ich habe seit gestern Bauchschmerzen.")

        self.assertIsInstance(result, ExtractionClaims)
        self.assertEqual(result.observations[0].label, "Bauchschmerzen")
        self.assertEqual(extractor.extraction_engine.calls[0]["call_name"], EXTRACTION_CALL)
        self.assertEqual(extractor.extraction_engine.calls[0]["prompt_name"], EXTRACTION_CALL)
        self.assertIn('"subject_claims": {', load_prompt(EXTRACTION_CALL).system_prompt)
        self.assertIn('"observations": [', load_prompt(EXTRACTION_CALL).system_prompt)

    def test_medical_extractor_canonicalizes_duration_key_from_llm(self):
        extractor = MedicalExtractor(
            extraction_engine=_FakeExtractionEngine(
                {
                    "topic_signal": "bauchschmerzen",
                    "subject_claims": {"relation": "self"},
                    "observations": [
                        {
                            "type": "symptom",
                            "label": "Bauchschmerzen",
                            "normalized_concept": "bauchschmerzen",
                            "subject_ref": "self",
                            "negated": False,
                            "attributes": {"duration": "seit gestern"},
                            "source_span": "Bauchschmerzen",
                        }
                    ],
                }
            ),
            call_model_config=CallModelConfig(default_model="default", overrides={}),
        )

        result = extractor.extract(message="Ich habe seit gestern Bauchschmerzen.")

        self.assertEqual(result.observations[0].attributes["duration_or_onset"], "seit gestern")
        self.assertNotIn("duration", result.observations[0].attributes)

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
