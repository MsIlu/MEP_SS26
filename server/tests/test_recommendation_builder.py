"""Unit tests for RecommendationBuilder prompt enrichment and provenance."""

from unittest.mock import MagicMock

from careena4.application.recommendation.recommendation_builder import RecommendationBuilder
from careena4.models.domain import MedicalCase, Observation
from careena4.models.turn.input import DiaryEntry, MedicationEntry


def _case_manager_with_observations(labels: list[str]) -> MagicMock:
    """Fake CaseManager exposing the methods the builder relies on."""
    observations = [Observation(type="symptom", normalized_label_de=label) for label in labels]
    manager = MagicMock()
    manager.central_non_negated_observations.return_value = observations
    manager.topic_label.return_value = labels[0] if labels else None
    return manager


def _diary() -> list[DiaryEntry]:
    return [DiaryEntry(date="2026-06-30", symptom="Kopfschmerzen", intensity=6)]


def _medications() -> list[MedicationEntry]:
    return [
        MedicationEntry(
            name="Ibuprofen",
            dose="400 mg",
            frequency="zweimal täglich",
            schedule="08:00, 20:00",
            active_substance="Ibuprofen",
        )
    ]


def test_fallback_result_carries_deterministic_data_sources():
    builder = RecommendationBuilder(
        case_manager=_case_manager_with_observations(["Kopfschmerzen"]),
        llm_client=None,  # forces fallback
    )

    result = builder.build(
        medical_case=MedicalCase(),
        diary_history=_diary(),
        medication_history=_medications(),
    )

    assert "Angaben aus dem Chat" in result.data_sources
    assert any("Symptom-Tagebuch" in source for source in result.data_sources)
    assert any("Medikamentenplan" in source for source in result.data_sources)


def test_llm_prompt_includes_diary_and_medications():
    captured = {}

    class _FakeLlm:
        def complete(self, *, messages, **kwargs):
            captured["user_prompt"] = messages[-1]["content"]
            return (
                '{"urgency": "self_observation", "urgency_level": "low", '
                '"care_level": "self_care", "specialty": "general_practice", '
                '"summary": "Leichte Beschwerden.", "next_step": "Ruhe.", '
                '"reasons": ["leichte Intensität"]}'
            )

    builder = RecommendationBuilder(
        case_manager=_case_manager_with_observations(["Kopfschmerzen"]),
        llm_client=_FakeLlm(),
    )

    result = builder.build(
        medical_case=MedicalCase(),
        diary_history=_diary(),
        medication_history=_medications(),
    )

    # The prompt must surface both diaries so the model can reason over them.
    assert "Symptomtagebuch" in captured["user_prompt"]
    assert "Medikamentenplan" in captured["user_prompt"]
    assert "Ibuprofen" in captured["user_prompt"]

    # care_level is differentiated (not the generic general_practice default).
    assert result.care_level == "self_care"
    assert any("Medikamentenplan" in source for source in result.data_sources)
