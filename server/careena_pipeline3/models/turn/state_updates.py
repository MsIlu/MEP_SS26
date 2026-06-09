from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.domain import DialogueState, PendingFollowup
from careena_pipeline3.models.workflow import AssessmentReadiness


class ProcessStateUpdate(PipelineModel):
    """
    Small orchestration-facing result for process-state progression.

    This captures dialogue/process effects after case truth changed, without
    forcing the caller to infer them from direct `DialogueState` mutation.
    """

    dialogue_state: DialogueState
    pending_followup: PendingFollowup | None = None


class ReadinessStateUpdate(PipelineModel):
    """
    Small orchestration-facing result for recommendation readiness.

    It keeps readiness evaluation separate from the broader process-state
    update so the `DialogueManager` can apply both stages explicitly.
    """

    dialogue_state: DialogueState
    assessment_readiness: AssessmentReadiness
    pending_followup: PendingFollowup | None = None
