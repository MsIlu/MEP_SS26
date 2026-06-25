from __future__ import annotations

import re
from typing import Iterable, Literal
from uuid import uuid4

from pydantic import Field

from careena4.models.common import PipelineModel


SymptomChipStatus = Literal[
    "extracted",
    "user_confirmed",
    "user_edited",
    "user_added",
    "user_removed",
    "low_confidence_needs_review",
]

SymptomChipSource = Literal[
    "careena4_extraction",
    "medgemma_mapping",
    "user",
    "legacy_input_draft",
]


class SymptomMappingCandidate(PipelineModel):
    """
    Candidate mapping returned by a terminology or LLM mapping provider.

    This is not canonical medical truth. Codes and labels must be validated
    against our own catalog before they drive safety, case writing or
    recommendations.
    """

    raw_text: str
    lay_term_de: str
    clinical_term_de: str | None = None
    snomed_code: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    mapper_name: str = "unknown"
    validation_status: str = "llm_candidate"


class SymptomChip(PipelineModel):
    """
    Editable symptom chip for the current Careena4 input draft.

    A chip is current input evidence for the user interface. It is deliberately
    separate from MedicalCase observations, because the MedicalCase represents
    stabilized medical case truth.
    """

    chip_id: str = Field(default_factory=lambda: str(uuid4()))
    raw_text: str | None = None
    display_label_de: str
    normalized_label_de: str | None = None
    clinical_term_de: str | None = None
    snomed_code: str | None = None
    extraction_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    mapping_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    status: SymptomChipStatus = "extracted"
    source: SymptomChipSource = "careena4_extraction"
    mapping: SymptomMappingCandidate | None = None


class SymptomInputDraft(PipelineModel):
    """
    Editable symptom input draft stored inside a Careena4 session.

    This is the migration target for the existing frontend symptom-chip flow.
    It keeps the current editable input layer separate from MedicalCase,
    ConversationState and RecommendationState.
    """

    session_id: str = ""
    chips: list[SymptomChip] = Field(default_factory=list)

    def symptom_labels(self) -> list[str]:
        """
        Return frontend-compatible symptom labels.

        Removed chips are intentionally hidden from the legacy frontend contract.
        """

        return [
            chip.display_label_de
            for chip in self.chips
            if chip.status != "user_removed"
        ]

    def replace_from_labels(self, labels: Iterable[str]) -> None:
        """
        Replace the draft with user-edited labels from the frontend.

        The current frontend contract only sends a list of strings. We keep the
        richer internal chip model while returning the legacy list format.
        """

        self.chips = [
            SymptomChip(
                display_label_de=label,
                normalized_label_de=_normalized_identity(label),
                status="user_edited",
                source="user",
            )
            for label in _merge_symptom_labels([], labels)
        ]

    def replace_from_chips(self, chips: Iterable[SymptomChip]) -> None:
        """
        Replace the draft with rich chips returned by the frontend.

        Rich chips are still editable input evidence, not MedicalCase truth.
        If the user edited or added a chip, stale terminology mapping is cleared
        so a later mapping provider can remap the new label safely.
        """

        merged_chips: list[SymptomChip] = []
        known_identities: set[str] = set()

        for chip in chips:
            if chip.status == "user_removed":
                continue

            cleaned_label = _clean_label(chip.display_label_de)
            if cleaned_label is None:
                continue

            normalized_identity = _normalized_identity(cleaned_label)
            if not normalized_identity or normalized_identity in known_identities:
                continue

            known_identities.add(normalized_identity)

            if chip.status in {"user_edited", "user_added"}:
                merged_chips.append(
                    chip.model_copy(
                        update={
                            "display_label_de": cleaned_label,
                            "normalized_label_de": normalized_identity,
                            "clinical_term_de": None,
                            "snomed_code": None,
                            "mapping_confidence": None,
                            "mapping": None,
                            "source": "user",
                        }
                    )
                )
                continue

            merged_chips.append(
                chip.model_copy(
                    update={
                        "display_label_de": cleaned_label,
                        "normalized_label_de": chip.normalized_label_de
                        or normalized_identity,
                    }
                )
            )

        self.chips = merged_chips

    def merge_extracted_labels(self, labels: Iterable[str]) -> None:
        """
        Merge newly extracted symptom labels into the editable draft.

        This method is intentionally not wired into TurnEngine yet. It exists so
        the next migration slice can reuse the same draft model.
        """

        merged_labels = _merge_symptom_labels(self.symptom_labels(), labels)
        existing_by_label = {
            _normalized_identity(chip.display_label_de): chip
            for chip in self.chips
            if chip.status != "user_removed"
        }

        merged_chips: list[SymptomChip] = []
        for label in merged_labels:
            normalized = _normalized_identity(label)
            existing_chip = existing_by_label.get(normalized)
            if existing_chip is not None:
                merged_chips.append(existing_chip)
                continue

            merged_chips.append(
                SymptomChip(
                    display_label_de=label,
                    normalized_label_de=normalized,
                    status="extracted",
                    source="careena4_extraction",
                )
            )

        self.chips = merged_chips


class SymptomDraftUpdateRequest(PipelineModel):
    """
    Frontend-compatible request body for updating symptom chips.

    `symptoms` preserves the legacy frontend contract. `chips` allows the
    migrated frontend to send the richer Careena4 chip model.
    """

    symptoms: list[str] = Field(default_factory=list)
    chips: list[SymptomChip] | None = None


    symptoms: list[str] = Field(default_factory=list)


class SymptomDraftResponse(PipelineModel):
    """
    Frontend-compatible response body for the current symptom draft.

    The `symptoms` field preserves the legacy frontend contract. The `chips`
    field exposes the richer Careena4 input model for the frontend/backend
    migration path.
    """

    session_id: str
    symptoms: list[str] = Field(default_factory=list)
    chips: list[SymptomChip] = Field(default_factory=list)


    session_id: str
    symptoms: list[str] = Field(default_factory=list)


class CancelDraftResponse(PipelineModel):
    """
    Frontend-compatible response body after cancelling a draft.
    """

    message: str
    session_id: str


_GERMAN_CHAR_REPLACEMENTS = str.maketrans(
    {
        "?": "ae",
        "?": "oe",
        "?": "ue",
        "?": "ss",
    }
)


def _clean_label(value: str) -> str | None:
    cleaned = " ".join(str(value).strip().split())
    return cleaned or None


def _normalized_identity(value: str) -> str:
    normalized = value.casefold().translate(_GERMAN_CHAR_REPLACEMENTS)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return " ".join(normalized.split())


def _merge_symptom_labels(
    existing_labels: Iterable[str],
    incoming_labels: Iterable[str],
) -> list[str]:
    """
    Merge labels with stable cleanup and simple specificity handling.

    Example:
    - "Bauchschmerzen" and "Schmerzen" should not both be shown as chips.
    - If a more specific label arrives later, it replaces the generic one.
    """

    merged: list[str] = []

    for value in [*existing_labels, *incoming_labels]:
        cleaned = _clean_label(str(value))
        if cleaned is None:
            continue

        candidate_identity = _normalized_identity(cleaned)
        if not candidate_identity:
            continue

        skip_candidate = False
        replaced_existing = False

        for index, existing in enumerate(list(merged)):
            existing_identity = _normalized_identity(existing)

            if existing_identity == candidate_identity:
                skip_candidate = True
                break

            if existing_identity and existing_identity in candidate_identity:
                merged[index] = cleaned
                replaced_existing = True
                break

            if candidate_identity in existing_identity:
                skip_candidate = True
                break

        if skip_candidate or replaced_existing:
            continue

        merged.append(cleaned)

    return merged
