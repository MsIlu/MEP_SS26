from pydantic import Field

from careena4.models.common import PipelineModel, ResponseMode, TurnDecisionKind
from careena4.models.domain import ActiveQuestion


class TurnDecision(PipelineModel):
    kind: TurnDecisionKind
    response_mode: ResponseMode
    active_question: ActiveQuestion | None = None
    trace_notes: list[str] = Field(default_factory=list)
