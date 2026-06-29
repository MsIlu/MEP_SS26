from pydantic import AliasChoices, Field

from careena4.models.common import PipelineModel
from careena4.models.turn import EntryAssessment, ExtractedCaseInput, QuestionResolution
from careena4.models.understanding import ExtractedSymptomCandidate, StsConsultationReasonCandidate


class TurnUnderstandingSignal(PipelineModel):
    symptoms: list[ExtractedSymptomCandidate] = Field(default_factory=list)
    sts_matches: list[StsConsultationReasonCandidate] = Field(default_factory=list)
    sts_no_match_reason: str | None = Field(
        default=None,
        validation_alias=AliasChoices("sts_no_match_reason", "no_match_reason"),
    )
    trace_notes: list[str] = Field(default_factory=list)


class TurnInterpretation(PipelineModel):
    entry_assessment: EntryAssessment
    question_resolution: QuestionResolution | None = None
    case_input: ExtractedCaseInput | None = None
    current_turn_understanding: TurnUnderstandingSignal | None = None
    trace_notes: list[str] = Field(default_factory=list)
