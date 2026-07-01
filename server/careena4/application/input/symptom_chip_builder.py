from __future__ import annotations

from careena4.domain.case import CaseManager
from careena4.models.domain import MedicalCase, Observation
from careena4.application.input.symptom_mapping_service import SymptomMappingService
from careena4.models.input.symptom_input_draft import SymptomChip, SymptomInputDraft, _normalized_identity
from careena4.models.turn import ExtractedCaseInput, ExtractedObservationInput


class SymptomChipBuilder:
    """
    Builds editable symptom chips from the current turn extraction claims.

    This component owns the transition from extraction output to input draft.
    It does not write MedicalCase truth and it does not make safety or
    recommendation decisions.
    """

    def __init__(
        self,
        *,
        mapping_service: SymptomMappingService | None = None,
        case_manager: CaseManager | None = None,
    ) -> None:
        self.mapping_service = mapping_service or SymptomMappingService()
        self.case_manager = case_manager or CaseManager()

    def update_from_claims(
        self,
        *,
        draft: SymptomInputDraft,
        claims: ExtractedCaseInput,
    ) -> SymptomInputDraft:
        """
        Merge non-negated symptom claims into the editable input draft.
        """

        updated_draft = draft.model_copy(deep=True)
        updated_draft.merge_extracted_labels(self.symptom_labels_from_claims(claims))
        return self.mapping_service.enrich_draft(updated_draft)

    def update_from_case(
        self,
        *,
        draft: SymptomInputDraft | None,
        medical_case: MedicalCase,
    ) -> SymptomInputDraft:
        """
        Project visible symptom observations from MedicalCase into the input draft.

        The case remains the source of truth. Existing chip-level UI metadata is
        preserved when it still matches the same projected observation identity.
        """

        active_draft = draft.model_copy(deep=True) if draft is not None else SymptomInputDraft()
        existing_by_identity = {
            self._identity_for_chip(chip): chip
            for chip in active_draft.chips
            if chip.status != "user_removed" and self._identity_for_chip(chip) is not None
        }

        projected_chips: list[SymptomChip] = []
        for observation in self.case_manager.central_non_negated_observations(
            medical_case=medical_case
        ):
            if not self._is_visible_observation(observation):
                continue

            identity = self._identity_for_label(observation.normalized_label_de)
            if identity is None:
                continue

            existing_chip = existing_by_identity.get(identity)
            if existing_chip is not None:
                projected_chips.append(
                    existing_chip.model_copy(
                        update={
                            "display_label_de": observation.normalized_label_de,
                            "normalized_label_de": identity,
                            "clinical_term_de": observation.clinical_term_de or existing_chip.clinical_term_de,
                        }
                    )
                )
                continue

            projected_chip = SymptomChip(
                display_label_de=observation.normalized_label_de,
                normalized_label_de=identity,
                clinical_term_de=observation.clinical_term_de,
                status="extracted",
                source="careena4_extraction",
            )
            enriched_chip = self.mapping_service.enrich_chip(projected_chip)
            projected_chips.append(
                enriched_chip.model_copy(
                    update={
                        "clinical_term_de": observation.clinical_term_de or enriched_chip.clinical_term_de,
                    }
                )
            )

        active_draft.chips = projected_chips
        return active_draft

    def symptom_labels_from_claims(self, claims: ExtractedCaseInput) -> list[str]:
        """
        Return frontend-visible labels for non-negated symptom claims.
        """

        return [
            claim.normalized_label_de
            for claim in claims.observations
            if self._is_visible_symptom_claim(claim)
        ]

    @staticmethod
    def _is_visible_symptom_claim(claim: ExtractedObservationInput) -> bool:
        """
        Decide whether an extracted observation should become a symptom chip.
        """

        return (
            claim.type == "symptom"
            and claim.status != "negated"
            and bool(claim.normalized_label_de.strip())
        )

    @staticmethod
    def _is_visible_observation(observation: Observation) -> bool:
        return (
            observation.type == "symptom"
            and not observation.is_negated()
            and bool(observation.normalized_label_de.strip())
        )

    @staticmethod
    def _identity_for_chip(chip: SymptomChip) -> str | None:
        if chip.normalized_label_de:
            return chip.normalized_label_de.casefold().strip()
        if chip.display_label_de:
            return chip.display_label_de.casefold().strip()
        return None

    @staticmethod
    def _identity_for_label(label: str | None) -> str | None:
        if label is None:
            return None
        identity = _normalized_identity(label)
        return identity or None
