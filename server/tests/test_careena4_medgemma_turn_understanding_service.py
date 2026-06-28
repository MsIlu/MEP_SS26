
from __future__ import annotations

from careena4.application.understanding import MedGemmaTurnUnderstandingService
from careena4.application.understanding.medgemma_turn_understanding_service import (
    MedGemmaTurnUnderstandingOutput,
    MedGemmaUnderstandingStsMatch,
    MedGemmaUnderstandingSymptom,
)


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
    def reasons_for_prompt(self):
        return [
            {
                "sts_id": "1304",
                "source_label_de": "Uebelkeit, Erbrechen",
                "source_category_de": "Magen - Darm - Gynaekologie",
                "source_sts_levels_present": [2, 3, 4],
            }
        ]

    def hydrate_match(self, match):
        if match.get("sts_id") == "1304":
            hydrated = dict(match)
            hydrated["sts_label_de"] = hydrated.get("sts_label_de") or "Uebelkeit, Erbrechen"
            hydrated["source_category_de"] = (
                hydrated.get("source_category_de") or "Magen - Darm - Gynaekologie"
            )
            hydrated["source_sts_levels_present"] = (
                hydrated.get("source_sts_levels_present") or [2, 3, 4]
            )
            return hydrated
        return match


def test_understanding_service_keeps_symptoms_even_without_sts_match():
    engine = FakeExtractionEngine(
        MedGemmaTurnUnderstandingOutput(
            symptoms=[
                MedGemmaUnderstandingSymptom(
                    source_label="komisches Flimmern",
                    normalized_label_de="Flimmern",
                    clinical_term_de="Visuelle Wahrnehmungsst?rung",
                    confidence=0.8,
                )
            ],
            sts_matches=[],
            no_match_reason="No direct STS match.",
            trace_notes=["fake"],
        )
    )

    service = MedGemmaTurnUnderstandingService(
        extraction_engine=engine,
        sts_catalog=FakeCatalog(),
    )

    result = service.extract(message="Ich habe so ein komisches Flimmern.")

    assert [symptom.normalized_label_de for symptom in result.symptoms] == ["Flimmern"]
    assert result.sts_matches == []
    assert result.no_match_reason == "No direct STS match."


def test_understanding_service_hydrates_partial_sts_match_from_catalog():
    engine = FakeExtractionEngine(
        MedGemmaTurnUnderstandingOutput(
            symptoms=[
                MedGemmaUnderstandingSymptom(
                    source_label="?bel",
                    normalized_label_de="?belkeit",
                    clinical_term_de="?belkeit",
                    confidence=0.95,
                )
            ],
            sts_matches=[
                MedGemmaUnderstandingStsMatch(
                    sts_id="1304",
                    match_confidence=0.95,
                    match_reason="Nausea and vomiting.",
                )
            ],
            trace_notes=["fake"],
        )
    )

    service = MedGemmaTurnUnderstandingService(
        extraction_engine=engine,
        sts_catalog=FakeCatalog(),
    )

    result = service.extract(message="Mir ist ?bel.")

    assert result.symptom_labels() == ["?belkeit"]
    assert result.sts_matches[0].sts_id == "1304"
    assert result.sts_matches[0].sts_label_de == "Uebelkeit, Erbrechen"
    assert result.sts_matches[0].source_sts_levels_present == [2, 3, 4]


def test_understanding_service_returns_failed_understanding_without_fallback():
    engine = FakeExtractionEngine(error=RuntimeError("timeout"))

    service = MedGemmaTurnUnderstandingService(
        extraction_engine=engine,
        sts_catalog=FakeCatalog(),
    )

    result = service.extract(message="Mir ist ?bel.")

    assert result.symptoms == []
    assert result.sts_matches == []
    assert "medgemma_turn_understanding:failed" in result.trace_notes


def test_understanding_service_prompt_does_not_contain_snomed():
    engine = FakeExtractionEngine(
        MedGemmaTurnUnderstandingOutput(
            symptoms=[],
            sts_matches=[],
            trace_notes=["fake"],
        )
    )

    service = MedGemmaTurnUnderstandingService(
        extraction_engine=engine,
        sts_catalog=FakeCatalog(),
    )

    service.extract(message="Mir ist ?bel.")

    call = engine.calls[0]
    assert "SNOMED" not in call["system_prompt"]
