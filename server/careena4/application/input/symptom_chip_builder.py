from __future__ import annotations

from careena4.application.input.symptom_mapping_service import SymptomMappingService
from careena4.models.input import SymptomInputDraft
from careena4.models.turn import ExtractionClaims, ObservationClaim


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
    ) -> None:
        self.mapping_service = mapping_service or SymptomMappingService()

    def update_from_claims(
        self,
        *,
        draft: SymptomInputDraft,
        claims: ExtractionClaims,
    ) -> SymptomInputDraft:
        """
        Merge non-negated symptom claims into the editable input draft.
        """

        updated_draft = draft.model_copy(deep=True)
        updated_draft.merge_extracted_labels(self.symptom_labels_from_claims(claims))
        return self.mapping_service.enrich_draft(updated_draft)

    def symptom_labels_from_claims(self, claims: ExtractionClaims) -> list[str]:
        """
        Return frontend-visible labels for non-negated symptom claims.
        """

        return [
            claim.label
            for claim in claims.observations
            if self._is_visible_symptom_claim(claim)
        ]

    @staticmethod
    def _is_visible_symptom_claim(claim: ObservationClaim) -> bool:
        """
        Decide whether an extracted observation should become a symptom chip.
        """

        return claim.type == "symptom" and claim.status != "negated" and bool(claim.label.strip())
