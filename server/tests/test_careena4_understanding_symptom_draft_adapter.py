
from __future__ import annotations

from careena4.application.input import UnderstandingSymptomDraftAdapter
from careena4.models.input import SymptomInputDraft
from careena4.models.understanding import CurrentTurnUnderstanding, ExtractedSymptomCandidate


def test_understanding_adapter_merges_symptoms_into_input_draft():
    adapter = UnderstandingSymptomDraftAdapter()
    understanding = CurrentTurnUnderstanding(
        raw_message="Mir ist ?bel und ich habe erbrochen.",
        symptoms=[
            ExtractedSymptomCandidate(
                source_label="?bel",
                normalized_label_de="?belkeit",
                clinical_term_de="?belkeit",
                confidence=0.95,
            ),
            ExtractedSymptomCandidate(
                source_label="erbrochen",
                normalized_label_de="Erbrechen",
                clinical_term_de="Erbrechen",
                confidence=0.9,
            ),
        ],
    )

    draft = adapter.update_from_understanding(
        draft=None,
        understanding=understanding,
        session_id="session-1",
    )

    assert draft.symptom_labels() == ["?belkeit", "Erbrechen"]
    assert draft.chips[0].raw_text == "?bel"
    assert draft.chips[0].clinical_term_de == "?belkeit"
    assert draft.chips[0].extraction_confidence == 0.95
    assert draft.chips[0].mapping is None


def test_understanding_adapter_keeps_existing_user_draft_and_enriches_missing_evidence():
    adapter = UnderstandingSymptomDraftAdapter()
    draft = SymptomInputDraft(session_id="session-1")
    draft.replace_from_labels(["?belkeit"])

    understanding = CurrentTurnUnderstanding(
        raw_message="Mir ist ?bel.",
        symptoms=[
            ExtractedSymptomCandidate(
                source_label="?bel",
                normalized_label_de="?belkeit",
                clinical_term_de="?belkeit",
                confidence=0.95,
            ),
        ],
    )

    updated = adapter.update_from_understanding(
        draft=draft,
        understanding=understanding,
        session_id="session-1",
    )

    assert updated.symptom_labels() == ["?belkeit"]
    assert updated.chips[0].raw_text == "?bel"
    assert updated.chips[0].clinical_term_de == "?belkeit"
    assert updated.chips[0].extraction_confidence == 0.95


def test_understanding_adapter_preserves_fever_clinical_term_and_confidence():
    adapter = UnderstandingSymptomDraftAdapter()
    understanding = CurrentTurnUnderstanding(
        raw_message="Ich habe Fieber.",
        symptoms=[
            ExtractedSymptomCandidate(
                source_label="Fieber",
                normalized_label_de="erh?hte K?rpertemperatur",
                clinical_term_de="Pyrexie",
                confidence=0.95,
            ),
        ],
    )

    draft = adapter.update_from_understanding(
        draft=None,
        understanding=understanding,
        session_id="session-1",
    )

    assert draft.symptom_labels() == ["erh?hte K?rpertemperatur"]
    assert draft.chips[0].raw_text == "Fieber"
    assert draft.chips[0].clinical_term_de == "Pyrexie"
    assert draft.chips[0].extraction_confidence == 0.95


def test_understanding_adapter_raises_existing_confidence_when_same_chip_reappears():
    adapter = UnderstandingSymptomDraftAdapter()
    draft = SymptomInputDraft(session_id="session-1")

    first = CurrentTurnUnderstanding(
        raw_message="Mir ist ?bel.",
        symptoms=[
            ExtractedSymptomCandidate(
                source_label="?bel",
                normalized_label_de="?belkeit",
                clinical_term_de="?belkeit",
                confidence=0.7,
            ),
        ],
    )
    second = CurrentTurnUnderstanding(
        raw_message="Immer noch ?bel.",
        symptoms=[
            ExtractedSymptomCandidate(
                source_label="?bel",
                normalized_label_de="?belkeit",
                clinical_term_de="?belkeit",
                confidence=0.95,
            ),
        ],
    )

    draft = adapter.update_from_understanding(
        draft=draft,
        understanding=first,
        session_id="session-1",
    )
    draft = adapter.update_from_understanding(
        draft=draft,
        understanding=second,
        session_id="session-1",
    )

    assert draft.symptom_labels() == ["?belkeit"]
    assert draft.chips[0].extraction_confidence == 0.95


def test_understanding_adapter_does_not_create_chips_from_sts_only():
    adapter = UnderstandingSymptomDraftAdapter()
    understanding = CurrentTurnUnderstanding(
        raw_message="Unklare Nachricht.",
        symptoms=[],
    )

    draft = adapter.update_from_understanding(
        draft=None,
        understanding=understanding,
        session_id="session-1",
    )

    assert draft.symptom_labels() == []
