
from __future__ import annotations

from careena4.application.understanding import MedGemmaTurnUnderstandingService
from careena4.application.understanding.medgemma_turn_understanding_service import (
    MedGemmaTurnUnderstandingOutput,
    MedGemmaUnderstandingSymptom,
)
from careena4.models.understanding import StsConsultationReasonCandidate


class FakeExtractionEngine:
    def __init__(self, output=None, error: Exception | None = None):
        self.output = output
        self.error = error
        self.calls = []

    def extract(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.output


class FakeCatalog:
    """Minimal catalog stub for unit tests. STS matching is keyword-based post-LLM."""

    def reasons_for_prompt(self):
        return [
            {
                "sts_id": "1304",
                "source_label_de": "Uebelkeit, Erbrechen",
                "source_category_de": "Magen - Darm - Gynaekologie",
                "source_sts_levels_present": [2, 3, 4],
            }
        ]

    def match_by_labels(self, labels: list[str], *, max_results: int = 3) -> list[StsConsultationReasonCandidate]:
        """Return STS candidates if any label contains 'uebelkeit' or 'erbrechen'."""
        for label in labels:
            norm = label.casefold().replace("ü", "ue").replace("ö", "oe")
            if "uebelkeit" in norm or "erbrechen" in norm:
                return [
                    StsConsultationReasonCandidate(
                        sts_id="1304",
                        sts_label_de="Uebelkeit, Erbrechen",
                        source_category_de="Magen - Darm - Gynaekologie",
                        source_sts_levels_present=[2, 3, 4],
                        match_confidence=1.0,
                        match_reason="keyword_match",
                    )
                ]
        return []


def test_understanding_service_keeps_symptoms_even_without_sts_match():
    engine = FakeExtractionEngine(
        MedGemmaTurnUnderstandingOutput(
            symptoms=[
                MedGemmaUnderstandingSymptom(
                    source_label="komisches Flimmern",
                    normalized_label_de="Flimmern",
                    clinical_term_de="Visuelle Wahrnehmungsstörung",
                    confidence=0.8,
                )
            ],
            trace_notes=["fake"],
        )
    )

    service = MedGemmaTurnUnderstandingService(
        extraction_engine=engine,
        sts_catalog=FakeCatalog(),
    )

    result = service.extract(message="Ich habe so ein komisches Flimmern.")

    assert [s.normalized_label_de for s in result.symptoms] == ["Flimmern"]
    # "Flimmern" doesn't match any STS catalog keyword → no STS match
    assert result.sts_matches == []


def test_understanding_service_sts_matched_via_keyword_not_llm():
    """STS candidates now come from deterministic keyword matching, not from LLM output."""
    engine = FakeExtractionEngine(
        MedGemmaTurnUnderstandingOutput(
            symptoms=[
                MedGemmaUnderstandingSymptom(
                    source_label="übel",
                    normalized_label_de="Übelkeit",
                    clinical_term_de="Übelkeit",
                    confidence=0.95,
                )
            ],
            trace_notes=["fake"],
        )
    )

    service = MedGemmaTurnUnderstandingService(
        extraction_engine=engine,
        sts_catalog=FakeCatalog(),
    )

    result = service.extract(message="Mir ist übel.")

    assert result.symptom_labels() == ["Übelkeit"]
    assert len(result.sts_matches) == 1
    assert result.sts_matches[0].sts_id == "1304"
    assert result.sts_matches[0].sts_label_de == "Uebelkeit, Erbrechen"
    assert result.sts_matches[0].source_sts_levels_present == [2, 3, 4]
    assert result.sts_matches[0].match_reason == "keyword_match"


def test_understanding_service_sts_not_influenced_by_wrong_normalization():
    """Even if MedGemma normalizes wrongly, STS is matched on the normalized label."""
    engine = FakeExtractionEngine(
        MedGemmaTurnUnderstandingOutput(
            symptoms=[
                MedGemmaUnderstandingSymptom(
                    source_label="Kompfschmerzen",
                    normalized_label_de="Kopfschmerzen",
                    clinical_term_de="Cephalgie",
                    confidence=0.9,
                )
            ],
            trace_notes=["fake"],
        )
    )

    service = MedGemmaTurnUnderstandingService(
        extraction_engine=engine,
        sts_catalog=FakeCatalog(),
    )

    result = service.extract(message="Ich habe Kompfschmerzen.")

    # "Kopfschmerzen" / "Cephalgie" don't contain "uebelkeit" → FakeCatalog returns []
    assert result.sts_matches == []
    assert result.symptoms[0].normalized_label_de == "Kopfschmerzen"


def test_understanding_service_returns_failed_understanding_without_fallback():
    engine = FakeExtractionEngine(error=RuntimeError("timeout"))

    service = MedGemmaTurnUnderstandingService(
        extraction_engine=engine,
        sts_catalog=FakeCatalog(),
    )

    result = service.extract(message="Mir ist übel.")

    assert result.symptoms == []
    assert result.sts_matches == []
    assert "medgemma_turn_understanding:failed" in result.trace_notes


def test_understanding_service_prompt_does_not_contain_snomed():
    engine = FakeExtractionEngine(
        MedGemmaTurnUnderstandingOutput(
            symptoms=[],
            trace_notes=["fake"],
        )
    )

    service = MedGemmaTurnUnderstandingService(
        extraction_engine=engine,
        sts_catalog=FakeCatalog(),
    )

    service.extract(message="Mir ist übel.")

    call = engine.calls[0]
    assert "SNOMED" not in call["system_prompt"]


def test_understanding_service_prompt_does_not_contain_sts_catalog():
    """STS catalog must NOT be in the Understanding prompt anymore."""
    engine = FakeExtractionEngine(
        MedGemmaTurnUnderstandingOutput(
            symptoms=[],
            trace_notes=["fake"],
        )
    )

    service = MedGemmaTurnUnderstandingService(
        extraction_engine=engine,
        sts_catalog=FakeCatalog(),
    )

    service.extract(message="Ich habe Kopfschmerzen.")

    call = engine.calls[0]
    # STS catalog should no longer be in the prompt payload
    assert "allowed_sts_consultation_reasons" not in call["text"]
    assert "Swiss Triage System" not in call["system_prompt"]
