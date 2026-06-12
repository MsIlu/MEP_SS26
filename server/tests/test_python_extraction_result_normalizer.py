import sys
import types
import unittest
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

sys.modules.setdefault("openai", types.SimpleNamespace(OpenAI=object))


from careena_pipeline3.application.services.python_extraction_result_normalizer import (
    PythonExtractionResultNormalizer,
)
from careena_pipeline3.models.domain import CaseObservation, MedicalCase
from careena_pipeline3.models.extraction import (
    Call2ExtractionResult,
    ExtractedObservation,
)


class PythonExtractionResultNormalizerTest(unittest.TestCase):
    def test_mixed_update_and_new_info_keeps_focus_update_separate_from_new_items(self):
        normalizer = PythonExtractionResultNormalizer()
        focus = CaseObservation(
            type="symptom",
            label="Husten",
            display_label="Husten",
            source_span="Husten",
        )
        existing_case = MedicalCase(
            observations=[focus],
            primary_problem_id=focus.id,
        )
        call2_result = Call2ExtractionResult(
            focus_update=ExtractedObservation(
                raw_label="Husten",
                observation_type="symptom",
                normalized_concept="cough",
                source_span="seit gestern",
                attributes={"temporality": "seit gestern"},
            ),
            new_items=[
                ExtractedObservation(
                    raw_label="Fieber",
                    observation_type="symptom",
                    normalized_concept="fever",
                    source_span="fieber hab ich auch",
                    attributes={},
                )
            ],
        )

        normalized = normalizer.normalize(
            call2_result.to_extraction_result(
                raw_text="seit gestern und fieber hab ich auch"
            ),
            text="seit gestern und fieber hab ich auch",
            existing_case=existing_case,
            pending_slot="duration_or_onset",
            call2_tasks=["extract_symptoms"],
            operation_mode="mixed_update_and_new_info",
        )

        self.assertEqual(len(normalized.case_payload.observations), 2)
        focus_update = normalized.case_payload.observations[0]
        additional = normalized.case_payload.observations[1]

        self.assertEqual(focus_update.raw_label, "Husten")
        self.assertEqual(focus_update.observation_type, "symptom")
        self.assertEqual(focus_update.attributes.get("temporality"), "seit gestern")
        self.assertEqual(additional.raw_label, "Fieber")
        self.assertIn(
            "python_normalized_mixed_update_and_new_info:duration_or_onset",
            normalized.case_payload.extraction_notes,
        )
        self.assertIn(
            "python_normalized_mixed_update_and_new_info:symptom:duration_or_onset",
            normalized.trace_notes,
        )


if __name__ == "__main__":
    unittest.main()
