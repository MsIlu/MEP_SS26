from pydantic import Field

from careena4.models.common import PipelineModel
from careena4.models.turn.extraction_claims import ExtractionClaims


class QuestionResolution(PipelineModel):
    status: str
    answer_kind: str | None = None
    clear_active_question: bool = False
    resolved_followup_id: str | None = None
    extracted_answer_attributes: dict[str, object] = Field(default_factory=dict)
    additional_medical_information: bool = False
    extra_claims: ExtractionClaims | None = None
    recommendation_choice: str | None = None
    next_question_text: str | None = None
    trace_notes: list[str] = Field(default_factory=list)
