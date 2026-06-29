
from __future__ import annotations

from re import sub

from careena4.models.input import SymptomChip, SymptomInputDraft
from careena4.models.understanding import CurrentTurnUnderstanding


class UnderstandingSymptomDraftAdapter:
    """
    Bridges current-turn understanding into editable symptom input draft chips.

    This adapter preserves MedGemma evidence on the chip level. It does not write
    MedicalCase truth and does not decide safety or recommendations.
    """

    def update_from_understanding(
        self,
        *,
        draft: SymptomInputDraft | None,
        understanding: CurrentTurnUnderstanding,
        session_id: str | None,
    ) -> SymptomInputDraft:
        """Merge understood current-turn symptoms into the editable draft."""

        active_draft = draft or SymptomInputDraft(session_id=session_id or "")

        for symptom in understanding.symptoms:
            if not symptom.is_medical or symptom.is_negated:
                continue

            display_label = (symptom.normalized_label_de or symptom.source_label or "").strip()
            if not display_label:
                continue

            chip = SymptomChip(
                raw_text=symptom.source_label or None,
                display_label_de=display_label,
                normalized_label_de=self._identity(display_label),
                clinical_term_de=symptom.clinical_term_de,
                extraction_confidence=symptom.confidence,
                mapping_confidence=None,
                status="extracted",
                source="careena4_extraction",
                mapping=None,
            )

            self._merge_chip(active_draft, chip)

        return active_draft

    def _merge_chip(self, draft: SymptomInputDraft, new_chip: SymptomChip) -> None:
        """
        Merge a chip by stable identity candidates and enrich missing evidence.

        Existing user-edited or manually added draft chips must not be duplicated
        when MedGemma later extracts the same symptom concept.
        """

        new_identities = self._chip_identity_keys(new_chip)

        for existing_chip in draft.chips:
            existing_identities = self._chip_identity_keys(existing_chip)

            if not existing_identities.intersection(new_identities):
                continue

            if existing_chip.raw_text is None and new_chip.raw_text is not None:
                existing_chip.raw_text = new_chip.raw_text

            if existing_chip.clinical_term_de is None and new_chip.clinical_term_de is not None:
                existing_chip.clinical_term_de = new_chip.clinical_term_de

            if existing_chip.extraction_confidence is None:
                existing_chip.extraction_confidence = new_chip.extraction_confidence
            elif new_chip.extraction_confidence is not None:
                existing_chip.extraction_confidence = max(
                    existing_chip.extraction_confidence,
                    new_chip.extraction_confidence,
                )

            if existing_chip.mapping_confidence is None:
                existing_chip.mapping_confidence = new_chip.mapping_confidence

            if existing_chip.mapping is None:
                existing_chip.mapping = new_chip.mapping

            return

        draft.chips.append(new_chip)

    def _chip_identity_keys(self, chip: SymptomChip) -> set[str]:
        """Return normalized identity candidates for deduplicating chips."""

        raw_values = [
            chip.raw_text,
            chip.display_label_de,
            chip.normalized_label_de,
            chip.clinical_term_de,
        ]

        identities = {
            self._identity(value)
            for value in raw_values
            if value is not None and self._identity(value)
        }

        concept_aliases: set[str] = set()
        for identity in identities:
            if "belkeit" in identity or "uebel" in identity or "ubel" in identity:
                concept_aliases.add("uebelkeit")
            if "erbrechen" in identity or "erbrochen" in identity or "emesis" in identity:
                concept_aliases.add("erbrechen")
            if "atemnot" in identity or "dyspnoe" in identity or "luftnot" in identity:
                concept_aliases.add("atemnot")
            if "fieber" in identity or "pyrexie" in identity or "koerpertemperatur" in identity:
                concept_aliases.add("fieber")
            if "kopfschmerz" in identity or "kopfweh" in identity:
                concept_aliases.add("kopfschmerzen")
            if "bauchschmerz" in identity or "bauchweh" in identity or "abdominal" in identity:
                concept_aliases.add("bauchschmerzen")
            if "schwindel" in identity:
                concept_aliases.add("schwindel")

        return identities.union(concept_aliases)

    @staticmethod
    def _identity(value: str) -> str:
        """Normalize a string for stable chip comparison."""

        normalized = value.casefold()
        normalized = (
            normalized.replace("?", "ae")
            .replace("?", "oe")
            .replace("?", "ue")
            .replace("?", "ss")
        )
        normalized = sub(r"[^a-z0-9]+", " ", normalized)
        return " ".join(normalized.split())
