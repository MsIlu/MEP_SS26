from careena4.application.input import SymptomChipBuilder
from careena4.models.input import SymptomInputDraft
from careena4.models.turn import ExtractedCaseInput, ExtractedObservationInput


def test_symptom_chip_builder_enriches_extracted_chip_with_mapping_candidate():
    builder = SymptomChipBuilder()
    draft = SymptomInputDraft(session_id="session-1")
    claims = ExtractedCaseInput(
        observations=[
            ExtractedObservationInput(
                type="symptom",
                normalized_label_de="Schwindel",
                status="active",
            )
        ]
    )

    updated_draft = builder.update_from_claims(draft=draft, claims=claims)

    chip = updated_draft.chips[0]
    assert chip.display_label_de == "Schwindel"
    assert chip.mapping_confidence == 0.92
    assert chip.mapping is not None
    assert chip.mapping.mapper_name == "local_symptom_mapping"
