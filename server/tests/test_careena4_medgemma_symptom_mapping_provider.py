from __future__ import annotations

import json

from careena4.application.input import MedGemmaSymptomMappingProvider
from careena4.models.input import (
    MedGemmaSymptomMappingCandidate,
    MedGemmaSymptomMappingOutput,
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


def _confidence(candidate) -> float | None:
    return getattr(candidate, "mapping_confidence", getattr(candidate, "confidence", None))


def _mapping_source(candidate) -> str | None:
    return getattr(candidate, "mapper_name", getattr(candidate, "source", getattr(candidate, "mapping_source", None)))


def test_medgemma_provider_maps_lay_dyspnea_to_snomed_candidate():
    engine = FakeExtractionEngine(
        MedGemmaSymptomMappingOutput(
            candidates=[
                MedGemmaSymptomMappingCandidate(
                    source_label="keine Luft",
                    normalized_label_de="Atemnot",
                    clinical_term_de="Dyspnoe",
                    snomed_code="267036007",
                    snomed_display_de="Dyspnoe",
                    mapping_confidence=0.91,
                    validation_status="candidate",
                )
            ],
            trace_notes=["fake_medgemma"],
        )
    )

    provider = MedGemmaSymptomMappingProvider(extraction_engine=engine)

    candidate = provider.map_label(
        label="keine Luft",
        raw_text="Ich bekomme keine Luft.",
    )

    assert getattr(candidate, "snomed_code", None) == "267036007"
    assert getattr(candidate, "clinical_term_de", None) == "Dyspnoe"
    assert _confidence(candidate) == 0.91
    assert _mapping_source(candidate) == "medgemma_symptom_mapping"

    call = engine.calls[0]
    assert call["output_schema"] is MedGemmaSymptomMappingOutput
    assert call["call_name"] == "medgemma_symptom_mapping"
    assert call["prompt_name"] == "careena4_medgemma_symptom_mapping"
    assert call["prompt_version"] == "v1"

    payload = json.loads(call["text"])
    assert payload["symptom_label"] == "keine Luft"
    assert payload["raw_user_message"] == "Ich bekomme keine Luft."


def test_medgemma_provider_selects_highest_confidence_medical_candidate():
    engine = FakeExtractionEngine(
        MedGemmaSymptomMappingOutput(
            candidates=[
                MedGemmaSymptomMappingCandidate(
                    source_label="komisch",
                    is_medical=False,
                    normalized_label_de="unklar",
                    mapping_confidence=0.99,
                ),
                MedGemmaSymptomMappingCandidate(
                    source_label="Brustdruck",
                    normalized_label_de="Brustschmerzen",
                    clinical_term_de="Thoraxschmerzen",
                    snomed_code="29857009",
                    snomed_display_de="Chest pain",
                    mapping_confidence=0.88,
                ),
                MedGemmaSymptomMappingCandidate(
                    source_label="Brustdruck",
                    normalized_label_de="Druckgef?hl in der Brust",
                    clinical_term_de="Thorakales Druckgef?hl",
                    snomed_code=None,
                    mapping_confidence=0.61,
                ),
            ]
        )
    )

    provider = MedGemmaSymptomMappingProvider(extraction_engine=engine)

    candidate = provider.map_label(label="Brustdruck", raw_text="Druck auf der Brust")

    assert getattr(candidate, "snomed_code", None) == "29857009"
    assert getattr(candidate, "clinical_term_de", None) == "Thoraxschmerzen"
    assert _confidence(candidate) == 0.88


def test_medgemma_provider_falls_back_to_local_mapping_on_engine_error():
    engine = FakeExtractionEngine(error=RuntimeError("LLM unavailable"))

    provider = MedGemmaSymptomMappingProvider(extraction_engine=engine)

    candidate = provider.map_label(label="Atemnot", raw_text="Atemnot")

    assert getattr(candidate, "snomed_code", None) == "267036007"
    assert _confidence(candidate) is not None


def test_medgemma_provider_falls_back_to_local_mapping_when_no_medical_candidate():
    engine = FakeExtractionEngine(
        MedGemmaSymptomMappingOutput(
            candidates=[
                MedGemmaSymptomMappingCandidate(
                    source_label="Hallo",
                    is_medical=False,
                    normalized_label_de=None,
                    mapping_confidence=0.2,
                )
            ]
        )
    )

    provider = MedGemmaSymptomMappingProvider(extraction_engine=engine)

    candidate = provider.map_label(label="Hallo", raw_text="Hallo")

    assert getattr(candidate, "snomed_code", None) is None
    assert _confidence(candidate) is not None
