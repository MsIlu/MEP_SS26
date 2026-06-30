from pydantic import Field

from careena4.models.common import PipelineModel
from careena4.models.turn import EntryAssessment, ExtractedCaseInput, QuestionResolution
from careena4.models.understanding import ExtractedSymptomCandidate


class TurnUnderstandingSignal(PipelineModel):
    symptoms: list[ExtractedSymptomCandidate] = Field(default_factory=list)
    trace_notes: list[str] = Field(default_factory=list)


class TurnInterpretation(PipelineModel):
    entry_assessment: EntryAssessment
    question_resolution: QuestionResolution | None = None
    case_input: ExtractedCaseInput | None = None
    current_turn_understanding: TurnUnderstandingSignal | None = None
    trace_notes: list[str] = Field(default_factory=list)
