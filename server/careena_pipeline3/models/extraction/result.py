from __future__ import annotations

from pydantic import Field, model_validator

from careena_pipeline3.models.common import PipelineModel


class ExtractionSignal(PipelineModel):
    code: str
    value: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    source_span: str | None = None
    note: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_simple_signal(cls, value):
        if isinstance(value, str):
            return {
                "code": "text_evidence",
                "value": value,
                "source_span": value,
            }
        return value


class ExtractedSubject(PipelineModel):
    relation: str | None = None
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    signals: list[ExtractionSignal] = Field(default_factory=list)


class ExtractedObservation(PipelineModel):
    observation_id: str | None = None
    raw_label: str
    observation_type: str | None = None
    normalized_concept: str | None = None
    negated: bool = False
    certainty: str | None = None
    subject_ref: str | None = None
    source_span: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    attributes: dict[str, object] = Field(default_factory=dict)
    signals: list[ExtractionSignal] = Field(default_factory=list)


class ExtractedCasePayload(PipelineModel):
    subject: ExtractedSubject | None = None
    observations: list[ExtractedObservation] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    extraction_notes: list[str] = Field(default_factory=list)


class Call2ExtractionResult(PipelineModel):
    """
    Role:
    - smaller primary Call-2 output contract before the legacy pipeline
      adapter rebuilds the transitional `ExtractionResult`.

    Input contract:
    - produced by the primary Call-2 LLM step from a reduced,
      mode-sensitive context.

    Output contract:
    - separates `focus_update` from additional `new_items`
    - keeps subject updates and open questions small

    Does not decide:
    - canonical case truth
    - merge/conflict semantics
    - readiness, response, or requirement policy

    Transitional:
    - yes; this contract is immediately adapted back into `ExtractionResult`
      until downstream Block-4/5 cuts are ready.
    """

    subject_update: ExtractedSubject | None = None
    focus_update: ExtractedObservation | None = None
    new_items: list[ExtractedObservation] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    extraction_notes: list[str] = Field(default_factory=list)
    trace_notes: list[str] = Field(default_factory=list)

    def to_extraction_result(
        self,
        *,
        raw_text: str,
        medical: bool = True,
    ) -> ExtractionResult:
        observations = []
        if self.focus_update is not None:
            observations.append(self.focus_update)
        observations.extend(self.new_items)
        return ExtractionResult(
            raw_text=raw_text,
            medical=medical,
            case_payload=ExtractedCasePayload(
                subject=self.subject_update,
                observations=observations,
                unresolved_questions=list(self.open_questions),
                extraction_notes=list(self.extraction_notes),
            ),
            trace_notes=list(self.trace_notes),
        )


class ExtractionResult(PipelineModel):
    raw_text: str
    medical: bool = True
    case_payload: ExtractedCasePayload = Field(default_factory=ExtractedCasePayload)
    trace_notes: list[str] = Field(default_factory=list)
