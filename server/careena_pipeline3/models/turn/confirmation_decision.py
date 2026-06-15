from pydantic import Field

from careena_pipeline3.models.common import PipelineModel


class ConfirmationDecision(PipelineModel):
    """
    Small orchestration-facing confirmation result.

    Confirmation remains placeholder-heavy for now, but the turn orchestrator
    should still consume an explicit decision contract instead of a raw bool.
    """

    should_request_confirmation: bool = False
    trace_notes: list[str] = Field(default_factory=list)
