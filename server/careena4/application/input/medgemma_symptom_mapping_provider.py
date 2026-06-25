from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from careena4.application.input.symptom_mapping_service import (
    LocalSymptomMappingProvider,
)
from careena4.models.input import (
    MedGemmaSymptomMappingCandidate,
    MedGemmaSymptomMappingOutput,
    SymptomMappingCandidate,
)


MEDGEMMA_SYMPTOM_MAPPING_PROMPT = """
You map German lay symptom expressions to standardized medical symptom concepts.

Return JSON only in this exact structure:
{
  "candidates": [
    {
      "source_label": "original user symptom label",
      "is_medical": true,
      "normalized_label_de": "German lay-normalized symptom label",
      "clinical_term_de": "German clinical term",
      "mapping_confidence": 0.0,
      "validation_status": "candidate",
      "reasoning_note": "short mapping note without diagnosis"
    }
  ],
  "trace_notes": ["medgemma_symptom_mapping:v1"]
}

Rules:
- Do not diagnose.
- Do not decide urgency.
- Do not decide emergency handling.
- Map only the symptom terminology.
- Preserve uncertainty with lower confidence.
- If the input is not a medical symptom, return is_medical=false and low confidence.
- Prefer common German clinical terms.
""".strip()


class MedGemmaSymptomMappingProvider:
    """
    MedGemma-backed provider for symptom terminology mapping.

    The provider returns mapping candidates only. It does not write MedicalCase,
    does not evaluate red flags and does not decide the response.
    """

    def __init__(
        self,
        *,
        extraction_engine: Any,
        fallback_provider: LocalSymptomMappingProvider | None = None,
        model: str | None = None,
    ):
        self.extraction_engine = extraction_engine
        self.fallback_provider = fallback_provider or LocalSymptomMappingProvider()
        self.model = model

    def map_label(self, *, label: str, raw_text: str = "") -> SymptomMappingCandidate:
        """
        Map one symptom label to a standardized candidate.

        If MedGemma is unavailable or returns unusable data, the deterministic
        local provider is used as a safe migration fallback.
        """

        clean_label = label.strip()
        if not clean_label:
            return self.fallback_provider.map_label(label=label, raw_text=raw_text)

        try:
            output = self.extraction_engine.extract(
                text=self._user_payload(label=clean_label, raw_text=raw_text),
                system_prompt=MEDGEMMA_SYMPTOM_MAPPING_PROMPT,
                output_schema=MedGemmaSymptomMappingOutput,
                temperature=0.0,
                max_tokens=700,
                model=self.model,
                call_name="medgemma_symptom_mapping",
                prompt_name="careena4_medgemma_symptom_mapping",
                prompt_version="v1",
            )
        except Exception:
            return self.fallback_provider.map_label(label=clean_label, raw_text=raw_text)

        candidate = self._best_medical_candidate(output)
        if candidate is None:
            return self.fallback_provider.map_label(label=clean_label, raw_text=raw_text)

        try:
            return self._to_symptom_mapping_candidate(candidate, fallback_label=clean_label, raw_text=raw_text)
        except (ValidationError, TypeError, ValueError):
            return self.fallback_provider.map_label(label=clean_label, raw_text=raw_text)

    @staticmethod
    def _user_payload(*, label: str, raw_text: str) -> str:
        """
        Return a compact JSON user payload for the mapping call.
        """

        return json.dumps(
            {
                "symptom_label": label,
                "raw_user_message": raw_text,
                "task": "Map symptom label to German clinical term.",
            },
            ensure_ascii=False,
        )

    @staticmethod
    def _best_medical_candidate(
        output: MedGemmaSymptomMappingOutput,
    ) -> MedGemmaSymptomMappingCandidate | None:
        """
        Pick the highest-confidence medical candidate from MedGemma output.
        """

        medical_candidates = [
            candidate
            for candidate in output.candidates
            if candidate.is_medical
        ]
        if not medical_candidates:
            return None
        return max(medical_candidates, key=lambda candidate: candidate.mapping_confidence)

    @staticmethod
    def _to_symptom_mapping_candidate(
        candidate: MedGemmaSymptomMappingCandidate,
        *,
        fallback_label: str,
        raw_text: str = "",
    ) -> SymptomMappingCandidate:
        """
        Convert MedGemma output to the existing symptom mapping candidate model.

        This adapter intentionally writes the current canonical field names used
        by SymptomMappingCandidate. MedGemma remains a terminology mapper only;
        it does not create MedicalCase truth or safety decisions.
        """

        source_label = candidate.source_label.strip() if candidate.source_label else fallback_label
        lay_term = candidate.normalized_label_de or source_label or fallback_label
        confidence = float(candidate.mapping_confidence)

        payload = {
            "raw_text": raw_text,
            "lay_term_de": lay_term,
            "clinical_term_de": candidate.clinical_term_de,
            "confidence": confidence,
            "mapper_name": "medgemma_symptom_mapping",
            "validation_status": candidate.validation_status or "candidate",
        }

        return SymptomMappingCandidate.model_validate(payload)
