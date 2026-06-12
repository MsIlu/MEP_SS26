from pydantic import Field

from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.domain import DialogueState, PendingFollowup
from careena_pipeline3.models.workflow import AssessmentReadiness


class ProcessStateSignals(PipelineModel):
    """
    Small process-local signals derived after case truth updated.

    These signals stay explicitly separate from canonical case truth. They make
    the turn's process progress visible without turning follow-up handling into
    a second truth source.
    """

    answered_pending_followup: bool = False
    answered_requirement_key: str | None = None
    answered_slot: str | None = None
    additional_medical_information_detected: bool = False
    trace_notes: list[str] = Field(default_factory=list)


class ProcessStateUpdate(PipelineModel):
    """
    Small orchestration-facing result for process-state progression.

    This captures dialogue/process effects after case truth changed, without
    forcing the caller to infer them from direct `DialogueState` mutation.
    """

    dialogue_state: DialogueState
    pending_followup: PendingFollowup | None = None
    process_state_signals: ProcessStateSignals = Field(
        default_factory=ProcessStateSignals
    )


class ReadinessStateUpdate(PipelineModel):
    """
    Small orchestration-facing result for recommendation readiness.

    It keeps readiness evaluation separate from the broader process-state
    update so the `DialogueManager` can apply both stages explicitly.
    """

    dialogue_state: DialogueState
    assessment_readiness: AssessmentReadiness
    pending_followup: PendingFollowup | None = None
