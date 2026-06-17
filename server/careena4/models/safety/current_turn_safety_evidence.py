from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from careena4.models.common import PipelineModel


SafetyEvidenceSource = Literal[
    "symptom_input_draft",
    "medgemma_mapping",
    "local_mapping",
    "raw_message",
    "extraction_claim",
    "turn_understanding",
]


class SymptomSafetyEvidence(PipelineModel):
    """
    Structured symptom evidence available for safety evaluation in one turn.

    This is current-turn evidence only. It is not MedicalCase truth and it does
    not make a safety decision by itself.
    """

    source_label: str
    normalized_label_de: str | None = None
    clinical_term_de: str | None = None
    snomed_code: str | None = None
    mapping_confidence: float | None = None
    validation_status: str | None = None
    chip_status: str | None = None
    source: SafetyEvidenceSource = "symptom_input_draft"
    trace_notes: list[str] = Field(default_factory=list)

    @property
    def searchable_text(self) -> str:
        """
        Return normalized text used for deterministic structured safety matching.
        """

        values = [
            self.source_label,
            self.normalized_label_de,
            self.clinical_term_de,
            self.snomed_code,
        ]
        return _normalize(" ".join(value for value in values if value))


class CurrentTurnSafetyEvidence(PipelineModel):
    """
    Safety-relevant evidence collected for the current turn.

    This model deliberately avoids reading the full long-lived MedicalCase, so
    old red flags cannot silently dominate later harmless user messages.
    """

    raw_message: str = ""
    symptom_evidence: list[SymptomSafetyEvidence] = Field(default_factory=list)
    trace_notes: list[str] = Field(default_factory=list)

    @classmethod
    def from_turn_understanding(
        cls,
        *,
        understanding: Any,
        raw_message: str = "",
    ) -> "CurrentTurnSafetyEvidence":
        """
        Build current-turn safety evidence from MedGemma turn understanding.

        This method intentionally reads only the understanding of the current
        user message. It does not read MedicalCase and does not read the full
        persisted symptom draft, so old red-flag evidence cannot dominate later
        harmless turns.
        """

        symptom_evidence: list[SymptomSafetyEvidence] = []

        for symptom in getattr(understanding, "symptoms", []):
            is_medical = getattr(symptom, "is_medical", True)
            if is_medical is False:
                continue

            source_label = (
                _optional_str(getattr(symptom, "source_label", None))
                or _optional_str(getattr(symptom, "normalized_label_de", None))
                or _optional_str(getattr(symptom, "clinical_term_de", None))
            )
            normalized_label_de = _optional_str(
                getattr(symptom, "normalized_label_de", None)
            )
            clinical_term_de = _optional_str(
                getattr(symptom, "clinical_term_de", None)
            )
            confidence = _optional_float(getattr(symptom, "confidence", None))

            if not any([source_label, normalized_label_de, clinical_term_de]):
                continue

            symptom_evidence.append(
                SymptomSafetyEvidence(
                    source_label=source_label or "unknown_symptom",
                    normalized_label_de=normalized_label_de,
                    clinical_term_de=clinical_term_de,
                    mapping_confidence=confidence,
                    source="turn_understanding",
                    trace_notes=[
                        "current_turn_evidence:from_turn_understanding_symptom"
                    ],
                )
            )

        return cls(
            raw_message=raw_message or getattr(understanding, "raw_message", ""),
            symptom_evidence=symptom_evidence,
            trace_notes=["current_turn_safety_evidence:from_turn_understanding"],
        )

    @classmethod
    def from_symptom_input_draft(
        cls,
        *,
        draft: Any,
        raw_message: str = "",
    ) -> "CurrentTurnSafetyEvidence":
        """
        Build current-turn safety evidence from an editable symptom draft.

        The method uses attribute access defensively because the draft/chip model
        is still a migration boundary between frontend input state and backend
        medical logic.
        """

        symptom_evidence: list[SymptomSafetyEvidence] = []

        for chip in getattr(draft, "chips", []):
            chip_status = str(getattr(chip, "status", "") or "")
            if chip_status == "user_removed":
                continue

            source_label = str(
                getattr(chip, "label", "")
                or getattr(chip, "display_label", "")
                or ""
            ).strip()

            candidates = cls._candidate_items(chip)
            if not candidates:
                if source_label:
                    symptom_evidence.append(
                        SymptomSafetyEvidence(
                            source_label=source_label,
                            chip_status=chip_status or None,
                            trace_notes=["current_turn_evidence:chip_without_mapping"],
                        )
                    )
                continue

            for candidate in candidates:
                symptom_evidence.append(
                    SymptomSafetyEvidence(
                        source_label=source_label,
                        normalized_label_de=_optional_str(
                            getattr(candidate, "normalized_label_de", None)
                        ),
                        clinical_term_de=_optional_str(
                            getattr(candidate, "clinical_term_de", None)
                        ),
                        snomed_code=_optional_str(
                            getattr(candidate, "snomed_code", None)
                        ),
                        mapping_confidence=_optional_float(
                            getattr(candidate, "mapping_confidence", None)
                        ),
                        validation_status=_optional_str(
                            getattr(candidate, "validation_status", None)
                        ),
                        chip_status=chip_status or None,
                        source="symptom_input_draft",
                        trace_notes=["current_turn_evidence:chip_mapping_candidate"],
                    )
                )

        return cls(
            raw_message=raw_message,
            symptom_evidence=symptom_evidence,
            trace_notes=["current_turn_safety_evidence:from_symptom_input_draft"],
        )

    def searchable_text(self) -> str:
        """
        Return normalized text for current-turn structured safety matching.
        """

        parts = [self.raw_message]
        parts.extend(item.searchable_text for item in self.symptom_evidence)
        return _normalize(" ".join(part for part in parts if part))

    @staticmethod
    def _candidate_items(chip: Any) -> list[Any]:
        """
        Return mapping candidates from known transitional chip shapes.
        """

        single_candidate_attrs = (
            "mapping_candidate",
            "selected_mapping_candidate",
            "mapping",
        )
        for attr in single_candidate_attrs:
            candidate = getattr(chip, attr, None)
            if candidate is not None:
                return [candidate]

        candidates = getattr(chip, "mapping_candidates", None)
        if candidates:
            return list(candidates)

        return []


def _optional_str(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_float(value: object | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize(text: str) -> str:
    """
    Normalize German lay and mojibake variants for deterministic matching.
    """

    normalized = (
        text.casefold()
        .replace("?", "ae")
        .replace("?", "oe")
        .replace("?", "ue")
        .replace("?", "ss")
        .replace("??", "ae")
        .replace("??", "oe")
        .replace("??", "ue")
        .replace("??", "ss")
    )
    return " ".join(normalized.split())
