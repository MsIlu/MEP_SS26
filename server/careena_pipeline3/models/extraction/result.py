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


class ExtractionResult(PipelineModel):
    raw_text: str
    medical: bool = True
    case_payload: ExtractedCasePayload = Field(default_factory=ExtractedCasePayload)
    trace_notes: list[str] = Field(default_factory=list)
