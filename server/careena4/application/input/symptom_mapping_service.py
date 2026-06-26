from __future__ import annotations

import re
from typing import Protocol

from careena4.models.input import (
    SymptomChip,
    SymptomInputDraft,
    SymptomMappingCandidate,
)


class SymptomMappingProvider(Protocol):
    """
    Maps user-facing symptom labels to terminology candidates.

    Implementations may use local catalogs, MedGemma, Gemini or test doubles.
    Returned mappings are candidates, not canonical medical truth.
    """

    def map_label(self, label: str, raw_text: str | None = None) -> SymptomMappingCandidate:
        """
        Return one mapping candidate for a symptom label.
        """


class LocalSymptomMappingProvider:
    """
    Small deterministic provider for tests and migration safety.

    This provider is not intended to replace MedGemma or a terminology catalog.
    It gives the pipeline stable behavior while the real provider is introduced
    behind the same interface.
    """

    def __init__(self) -> None:
        self._mapping_by_identity: dict[str, SymptomMappingCandidate] = {
            "kopfschmerzen": SymptomMappingCandidate(
                raw_text="Kopfschmerzen",
                lay_term_de="Kopfschmerzen",
                clinical_term_de="Kopfschmerzen",
                confidence=0.95,
                mapper_name="local_symptom_mapping",
                validation_status="mapping_candidate",
            ),
            "schwindel": SymptomMappingCandidate(
                raw_text="Schwindel",
                lay_term_de="Schwindel",
                clinical_term_de="Vertigo / Schwindel",
                confidence=0.92,
                mapper_name="local_symptom_mapping",
                validation_status="mapping_candidate",
            ),
            "uebelkeit": SymptomMappingCandidate(
                raw_text="Uebelkeit",
                lay_term_de="?belkeit",
                clinical_term_de="Nausea / ?belkeit",
                confidence=0.93,
                mapper_name="local_symptom_mapping",
                validation_status="mapping_candidate",
            ),
            "ubelkeit": SymptomMappingCandidate(
                raw_text="?belkeit",
                lay_term_de="?belkeit",
                clinical_term_de="Nausea / ?belkeit",
                confidence=0.93,
                mapper_name="local_symptom_mapping",
                validation_status="mapping_candidate",
            ),
            "atemnot": SymptomMappingCandidate(
                raw_text="Atemnot",
                lay_term_de="Atemnot",
                clinical_term_de="Dyspnoe",
                confidence=0.94,
                mapper_name="local_symptom_mapping",
                validation_status="mapping_candidate",
            ),
            "brustschmerzen": SymptomMappingCandidate(
                raw_text="Brustschmerzen",
                lay_term_de="Brustschmerzen",
                clinical_term_de="Thoraxschmerz",
                confidence=0.93,
                mapper_name="local_symptom_mapping",
                validation_status="mapping_candidate",
            ),
        }

    def map_label(self, label: str, raw_text: str | None = None) -> SymptomMappingCandidate:
        """
        Return a deterministic mapping candidate or a low-confidence fallback.
        """

        identity = _normalized_identity(label)
        candidate = self._mapping_by_identity.get(identity)
        if candidate is not None:
            return candidate.model_copy(
                update={
                    "raw_text": raw_text or label,
                }
            )

        return SymptomMappingCandidate(
            raw_text=raw_text or label,
            lay_term_de=label.strip(),
            clinical_term_de=None,
            confidence=0.35,
            mapper_name="local_symptom_mapping",
            validation_status="fallback_low_confidence",
        )


class SymptomMappingService:
    """
    Enriches editable symptom chips with terminology mapping candidates.

    This service does not make safety, case-writing or recommendation decisions.
    """

    def __init__(
        self,
        *,
        provider: SymptomMappingProvider | None = None,
        low_confidence_threshold: float = 0.70,
    ) -> None:
        self.provider = provider or LocalSymptomMappingProvider()
        self.low_confidence_threshold = low_confidence_threshold

    def enrich_draft(self, draft: SymptomInputDraft) -> SymptomInputDraft:
        """
        Enrich all visible draft chips with mapping candidates.
        """

        updated_draft = draft.model_copy(deep=True)
        updated_draft.chips = [self.enrich_chip(chip) for chip in updated_draft.chips]
        return updated_draft

    def enrich_chip(self, chip: SymptomChip) -> SymptomChip:
        """
        Enrich one chip while preserving user edit state.
        """

        if chip.status == "user_removed":
            return chip

        candidate = self.provider.map_label(
            label=chip.display_label_de,
            raw_text=chip.raw_text,
        )

        new_status = chip.status
        if (
            candidate.confidence < self.low_confidence_threshold
            and chip.status == "extracted"
        ):
            new_status = "low_confidence_needs_review"

        return chip.model_copy(
            update={
                "raw_text": chip.raw_text or candidate.raw_text,
                "normalized_label_de": _normalized_identity(candidate.lay_term_de),
                "clinical_term_de": candidate.clinical_term_de,
                "mapping_confidence": candidate.confidence,
                "mapping": candidate,
                "status": new_status,
            }
        )


_GERMAN_CHAR_REPLACEMENTS = str.maketrans(
    {
        "?": "ae",
        "?": "oe",
        "?": "ue",
        "?": "ss",
    }
)


def _normalized_identity(value: str) -> str:
    """
    Normalize labels for deterministic mapping and comparison.
    """

    normalized = value.casefold().translate(_GERMAN_CHAR_REPLACEMENTS)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return " ".join(normalized.split())
