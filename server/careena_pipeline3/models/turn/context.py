from pydantic import Field

from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.domain import (
    ConcernRelation,
    ConcernState,
    ConcernTurnRole,
    DialogueState,
    MedicalCase,
)
from careena_pipeline3.models.turn.state_updates import ProcessStateSignals
from careena_pipeline3.models.turn.state_updates import RecommendationGateDecision
from careena_pipeline3.models.workflow import AssessmentReadiness
from careena_pipeline3.models.turn.safety_state import SafetyState


class TurnContext(PipelineModel):
    """
    Internal turn work context.

    Field groups:
    - persisted truth mirrored into the turn:
      `medical_case`, `dialogue_state`, `concern_state`
    - turn work / orchestration signals:
      `active_modules`,
      `process_state_signals`,
      `case_update_dialogue_consequences`,
      person and concern relation signals
    - derived assessments:
      `assessment_readiness`, `gate_decision`
    - observability:
      `trace_notes`, safety states

    Intentionally excluded:
    - boundary output fields now belong in `TurnResult`
    - active next-step truth is read directly from `gate_decision`
    - current follow-up truth stays in `dialogue_state.pending_followup`
    """

    active_modules: list[str] = Field(default_factory=list)
    process_state_signals: ProcessStateSignals = Field(
        default_factory=ProcessStateSignals
    )
    case_update_dialogue_consequences: list[str] = Field(default_factory=list)
    person_reference_present: bool = False
    multi_person_context: bool = False
    subject_relation_unclear: bool = False
    concern_relation: ConcernRelation = "unclear"
    latest_turn_role: ConcernTurnRole = "unclear"
    gate_decision: RecommendationGateDecision | None = None
    trace_notes: list[str] = Field(default_factory=list)
    raw_safety: SafetyState = Field(default_factory=SafetyState)
    extraction_safety: SafetyState = Field(default_factory=SafetyState)
    case_safety: SafetyState = Field(default_factory=SafetyState)
    medical_case: MedicalCase | None = None
    concern_state: ConcernState = Field(default_factory=ConcernState)
    dialogue_state: DialogueState = Field(default_factory=DialogueState)
    assessment_readiness: AssessmentReadiness = Field(default_factory=AssessmentReadiness)
