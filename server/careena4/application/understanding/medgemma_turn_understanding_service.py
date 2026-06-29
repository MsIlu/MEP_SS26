from __future__ import annotations

import json
from typing import Any

from pydantic import Field

from careena4.application.understanding.sts_consultation_reason_catalog import (
    StsConsultationReasonCatalog,
)
from careena4.models.common import PipelineModel
from careena4.models.understanding import (
    CurrentTurnUnderstanding,
    ExtractedSymptomCandidate,
)


class MedGemmaUnderstandingSymptom(PipelineModel):
    """Raw MedGemma output symptom for current-turn understanding."""

    source_label: str
    is_medical: bool = True
    is_negated: bool = False
    normalized_label_de: str | None = None
    clinical_term_de: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning_note: str | None = None


class MedGemmaTurnUnderstandingOutput(PipelineModel):
    """Structured MedGemma output for current-turn understanding."""

    symptoms: list[MedGemmaUnderstandingSymptom] = Field(default_factory=list)
    trace_notes: list[str] = Field(default_factory=list)


MEDGEMMA_TURN_UNDERSTANDING_PROMPT = """
You extract and normalize medical symptoms from German user sentences.

Return JSON only in this exact structure:
{
  "symptoms": [
    {
      "source_label": "exact symptom phrase from the user sentence",
      "is_medical": true,
      "is_negated": false,
      "normalized_label_de": "German lay-normalized symptom label derived from user wording",
      "clinical_term_de": "German clinical term",
      "confidence": 0.0,
      "reasoning_note": "short explanation without diagnosis"
    }
  ],
  "trace_notes": ["medgemma_turn_understanding:v1"]
}

Rules:
- Do not diagnose.
- Do not decide urgency or emergency handling.
- Do not output care recommendations.
- If the sentence contains no medical symptom, return an empty symptoms list.
- If multiple symptoms are present, return multiple symptom objects.
- normalized_label_de must reflect the user's own wording, corrected for spelling only.
  Do NOT replace the user's symptom with a different concept to fit any external catalog.
- clinical_term_de is the standard German medical term for what the user described.
- confidence is your own estimate and is not externally validated.
- Set is_negated to true when the user explicitly denies a symptom:
  "kein Fieber", "keine Atemnot", "nicht schwindelig", "keine Schmerzen".
- Set is_negated to false for all actively present symptoms.
- Still extract negated symptoms — they are clinically relevant context — but mark them correctly.
""".strip()


class MedGemmaTurnUnderstandingService:
    """
    Extract current-turn symptoms and STS consultation reason candidates.

    This service creates understanding candidates only. It does not write
    MedicalCase, does not mutate DialogueState and does not decide safety or
    recommendations.
    """

    def __init__(
        self,
        *,
        extraction_engine: Any,
        sts_catalog: StsConsultationReasonCatalog | None = None,
        model: str | None = None,
    ):
        self.extraction_engine = extraction_engine
        self.sts_catalog = sts_catalog or StsConsultationReasonCatalog()
        self.model = model

    def extract(self, *, message: str) -> CurrentTurnUnderstanding:
        """Run MedGemma understanding for one current user message."""

        raw_message = message.strip()
        if not raw_message:
            return CurrentTurnUnderstanding(
                raw_message=message,
                trace_notes=["medgemma_turn_understanding:empty_message"],
            )

        try:
            output = self.extraction_engine.extract(
                text=self._payload(raw_message),
                system_prompt=MEDGEMMA_TURN_UNDERSTANDING_PROMPT,
                output_schema=MedGemmaTurnUnderstandingOutput,
                temperature=0.0,
                max_tokens=1600,
                model=self.model,
                call_name="medgemma_turn_understanding",
                prompt_name="careena4_medgemma_turn_understanding",
                prompt_version="v1",
            )
        except Exception as error:
            return CurrentTurnUnderstanding(
                raw_message=message,
                trace_notes=[
                    "medgemma_turn_understanding:failed",
                    f"medgemma_turn_understanding:error:{error.__class__.__name__}",
                ],
            )

        return self._to_current_turn_understanding(raw_message=message, output=output)

    def _payload(self, raw_message: str) -> str:
        return json.dumps(
            {
                "raw_user_sentence": raw_message,
                "task": (
                    "Extract all medical symptoms. For each, provide a normalized German lay label "
                    "derived strictly from the user's wording and the standard clinical term."
                ),
            },
            ensure_ascii=False,
        )

    def _to_current_turn_understanding(
        self,
        *,
        raw_message: str,
        output: MedGemmaTurnUnderstandingOutput,
    ) -> CurrentTurnUnderstanding:
        """Convert raw MedGemma output into the internal current-turn model."""

        symptoms = [
            ExtractedSymptomCandidate(
                source_label=symptom.source_label,
                is_medical=symptom.is_medical,
                is_negated=symptom.is_negated,
                normalized_label_de=symptom.normalized_label_de,
                clinical_term_de=symptom.clinical_term_de,
                confidence=symptom.confidence,
                reasoning_note=symptom.reasoning_note,
            )
            for symptom in output.symptoms
        ]

        # STS matching is done deterministically after normalization so that the
        # STS catalog cannot bias the normalized_label_de assigned by MedGemma.
        candidate_labels = [
            label
            for s in symptoms
            if s.is_medical and not s.is_negated
            for label in (s.normalized_label_de, s.clinical_term_de)
            if label
        ]
        sts_matches = self.sts_catalog.match_by_labels(candidate_labels)

        trace_notes = list(output.trace_notes)
        trace_notes.append(f"medgemma_turn_understanding:symptoms:{len(symptoms)}")
        trace_notes.append(f"medgemma_turn_understanding:sts_matches:{len(sts_matches)}")

        return CurrentTurnUnderstanding(
            raw_message=raw_message,
            symptoms=symptoms,
            sts_matches=sts_matches,
            trace_notes=trace_notes,
        )
