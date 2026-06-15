from __future__ import annotations

from pydantic import Field

from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.domain import (
    ConcernAllowedNextStep,
    DialogueState,
)
from careena_pipeline3.models.workflow import AssessmentReadiness


class ResolvedFollowup(PipelineModel):
    """
    Turn-local visibility contract for one follow-up resolved by this turn.

    This is intentionally not persisted dialogue truth. The canonical open
    follow-up state still lives in `DialogueState.pending_followup`.
    """

    requirement_key: str
    slot: str
    kind: str = "requirement"
    focus_observation_id: str | None = None
    focus_label: str | None = None


class ProcessStateSignals(PipelineModel):
    """
    Small process-local signals derived after case truth updated.

    These signals stay explicitly separate from canonical case truth. They make
    the turn's process progress visible without turning follow-up handling into
    a second truth source.
    """

    resolved_followup: ResolvedFollowup | None = None
    additional_medical_information_detected: bool = False
    trace_notes: list[str] = Field(default_factory=list)


class ProcessStateUpdate(PipelineModel):
    """
    Small orchestration-facing result for process-state progression.

    This captures dialogue/process effects after case truth changed, without
    forcing the caller to infer them from direct `DialogueState` mutation.
    """

    dialogue_state: DialogueState
    process_state_signals: ProcessStateSignals = Field(
        default_factory=ProcessStateSignals
    )


class ReadinessStateUpdate(PipelineModel):
    """
    Small orchestration-facing result for recommendation readiness.

    It keeps readiness evaluation separate from the broader process-state
    update so the `DialogueManager` can apply both stages explicitly.

    Field groups:
    - persisted truth update:
      `dialogue_state`
    - derived assessment:
      `assessment_readiness`, `gate_decision`
    """

    dialogue_state: DialogueState
    assessment_readiness: AssessmentReadiness
    gate_decision: RecommendationGateDecision | None = None


class RecommendationGateDecision(PipelineModel):
    """
    Explicit small gate contract after readiness/process state settled.

    It keeps the policy question "which next move is actually allowed now"
    separate from raw readiness and separate from final response wording.
    """

    gate_status: str
    allowed_next_step: ConcernAllowedNextStep
    active_prompt_kind: str | None = None
    reason_tags: list[str] = Field(default_factory=list)
