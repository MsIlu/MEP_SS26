from careena4.application.input import SymptomChipBuilder
from careena4.models.input import SymptomInputDraft
from careena4.models.turn import ExtractedCaseInput, ExtractedObservationInput


def test_symptom_chip_builder_adds_non_negated_symptom_claims():
    builder = SymptomChipBuilder()
    draft = SymptomInputDraft(session_id="session-1")
    claims = ExtractedCaseInput(
        observations=[
            ExtractedObservationInput(
                type="symptom",
                normalized_label_de="Kopfschmerzen",
                status="active",
            ),
            ExtractedObservationInput(
                type="symptom",
                normalized_label_de="Husten",
                status="negated",
            ),
        ]
    )

    updated_draft = builder.update_from_claims(draft=draft, claims=claims)

    assert updated_draft.symptom_labels() == ["Kopfschmerzen"]
    assert draft.symptom_labels() == []


def test_symptom_chip_builder_merges_with_existing_user_edited_labels():
    builder = SymptomChipBuilder()
    draft = SymptomInputDraft(session_id="session-1")
    draft.replace_from_labels(["Kopfschmerzen"])

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

    assert updated_draft.symptom_labels() == ["Kopfschmerzen", "Schwindel"]
    assert updated_draft.chips[0].status == "user_edited"
    assert updated_draft.chips[1].status == "extracted"


def test_symptom_chip_builder_deduplicates_existing_labels():
    builder = SymptomChipBuilder()
    draft = SymptomInputDraft(session_id="session-1")
    draft.replace_from_labels(["Kopfschmerzen"])

    claims = ExtractedCaseInput(
        observations=[
            ExtractedObservationInput(
                type="symptom",
                normalized_label_de="kopfschmerzen",
                status="active",
            )
        ]
    )

    updated_draft = builder.update_from_claims(draft=draft, claims=claims)

    assert updated_draft.symptom_labels() == ["Kopfschmerzen"]
