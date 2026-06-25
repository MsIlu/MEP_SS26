from careena4.application.input import SymptomMappingService
from careena4.models.input import SymptomChip, SymptomInputDraft


def test_symptom_mapping_service_enriches_known_symptom_with_candidate_mapping():
    draft = SymptomInputDraft(
        session_id="session-1",
        chips=[
            SymptomChip(
                display_label_de="Atemnot",
                status="extracted",
                source="careena4_extraction",
            )
        ],
    )
    service = SymptomMappingService()

    updated_draft = service.enrich_draft(draft)

    chip = updated_draft.chips[0]
    assert chip.display_label_de == "Atemnot"
    assert chip.clinical_term_de == "Dyspnoe"
    assert chip.snomed_code == "267036007"
    assert chip.mapping_confidence == 0.94
    assert chip.mapping is not None
    assert chip.mapping.validation_status == "mapping_candidate"
    assert chip.status == "extracted"


def test_symptom_mapping_service_marks_unknown_extracted_symptom_as_low_confidence():
    draft = SymptomInputDraft(
        session_id="session-1",
        chips=[
            SymptomChip(
                display_label_de="Ganz komisches Gefuehl",
                status="extracted",
                source="careena4_extraction",
            )
        ],
    )
    service = SymptomMappingService()

    updated_draft = service.enrich_draft(draft)

    chip = updated_draft.chips[0]
    assert chip.snomed_code is None
    assert chip.mapping_confidence == 0.35
    assert chip.mapping is not None
    assert chip.mapping.validation_status == "fallback_low_confidence"
    assert chip.status == "low_confidence_needs_review"


def test_symptom_mapping_service_preserves_user_edited_status_for_low_confidence_chip():
    draft = SymptomInputDraft(session_id="session-1")
    draft.replace_from_labels(["Eigenes Symptom"])

    service = SymptomMappingService()
    updated_draft = service.enrich_draft(draft)

    chip = updated_draft.chips[0]
    assert chip.status == "user_edited"
    assert chip.mapping_confidence == 0.35
    assert chip.snomed_code is None
