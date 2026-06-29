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
    StsConsultationReasonCandidate,
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


class MedGemmaUnderstandingStsMatch(PipelineModel):
    """Raw MedGemma output STS match. Metadata may be hydrated after validation."""

    sts_id: str
    sts_label_de: str | None = None
    source_category_de: str | None = None
    source_sts_levels_present: list[int] = Field(default_factory=list)
    match_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    match_reason: str | None = None


class MedGemmaTurnUnderstandingOutput(PipelineModel):
    """Structured MedGemma output for current-turn understanding."""

    symptoms: list[MedGemmaUnderstandingSymptom] = Field(default_factory=list)
    sts_matches: list[MedGemmaUnderstandingStsMatch] = Field(default_factory=list)
    no_match_reason: str | None = None
    trace_notes: list[str] = Field(default_factory=list)


MEDGEMMA_TURN_UNDERSTANDING_PROMPT = """
You extract medical symptoms from German user sentences and match the case to possible Swiss Triage System (STS) consultation reasons.

Return JSON only in this exact structure:
{
  "symptoms": [
    {
      "source_label": "exact symptom phrase from the user sentence",
      "is_medical": true,
      "is_negated": false,
      "normalized_label_de": "German lay-normalized symptom label",
      "clinical_term_de": "German clinical term",
      "confidence": 0.0,
      "reasoning_note": "short explanation without diagnosis"
    }
  ],
  "sts_matches": [
    {
      "sts_id": "1008",
      "sts_label_de": "Atemsymptome (...)",
      "source_category_de": "Kardiovaskulaer und respiratorisch",
      "source_sts_levels_present": [1, 2, 3],
      "match_confidence": 0.0,
      "match_reason": "why this STS consultation reason fits the user sentence"
    }
  ],
  "no_match_reason": null,
  "trace_notes": ["medgemma_turn_understanding:v1"]
}

Rules:
- Do not diagnose.
- Do not decide urgency.
- Do not decide emergency handling.
- Do not output care recommendations.
- Always extract symptoms when symptoms are present, even if no STS consultation reason fits.
- STS matching must never suppress symptom extraction.
- If symptoms are present but no STS reason fits, return symptoms and an empty sts_matches list.
- If the sentence contains no medical symptom, return an empty symptoms list and an empty sts_matches list.
- If multiple symptoms are present, return multiple symptoms.
- Select up to 3 possible STS consultation reasons from the provided STS reason list only.
- The STS reason list uses the format "sts_id: label". Use only sts_id values present in that list.
- The STS levels are source metadata only. They are not a final triage result.
- Prefer direct matches over speculative matches.
- Avoid weak differential guesses unless the user text explicitly supports them.
- clinical_term_de should be German whenever possible.
- Confidence is your own estimate and is not externally validated.
- Set is_negated to true when the user explicitly denies a symptom: "kein Fieber", "keine Atemnot", "nicht schwindelig", "bekomme gut Luft", "keine Schmerzen".
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
        """Build the LLM payload with a compact STS id-to-label list."""

        return json.dumps(
            {
                "raw_user_sentence": raw_message,
                "task": (
                    "Extract symptoms first. Then map to possible STS consultation reasons. "
                    "If no STS reason fits, keep the extracted symptoms and return no STS match."
                ),
                "sts_reasons": self.sts_catalog.reasons_for_prompt(),
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

        sts_matches: list[StsConsultationReasonCandidate] = []
        for match in output.sts_matches:
            hydrated = self.sts_catalog.hydrate_match(match.model_dump())
            sts_matches.append(StsConsultationReasonCandidate.model_validate(hydrated))

        trace_notes = list(output.trace_notes)
        trace_notes.append(f"medgemma_turn_understanding:symptoms:{len(symptoms)}")
        trace_notes.append(f"medgemma_turn_understanding:sts_matches:{len(sts_matches)}")

        return CurrentTurnUnderstanding(
            raw_message=raw_message,
            symptoms=symptoms,
            sts_matches=sts_matches,
            no_match_reason=output.no_match_reason,
            trace_notes=trace_notes,
        )
