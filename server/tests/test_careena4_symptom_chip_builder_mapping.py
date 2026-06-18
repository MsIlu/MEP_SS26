from careena4.application.input import SymptomChipBuilder
from careena4.models.input import SymptomInputDraft
from careena4.models.turn import ExtractionClaims, ObservationClaim


def test_symptom_chip_builder_enriches_extracted_chip_with_mapping_candidate():
    builder = SymptomChipBuilder()
    draft = SymptomInputDraft(session_id="session-1")
    claims = ExtractionClaims(
        observations=[
            ObservationClaim(
                type="symptom",
                label="Schwindel",
                normalized_concept="schwindel",
                negated=False,
            )
        ]
    )

    updated_draft = builder.update_from_claims(draft=draft, claims=claims)

    chip = updated_draft.chips[0]
    assert chip.display_label_de == "Schwindel"
    assert chip.snomed_code == "404640003"
    assert chip.mapping_confidence == 0.92
    assert chip.mapping is not None
    assert chip.mapping.mapper_name == "local_symptom_mapping"
