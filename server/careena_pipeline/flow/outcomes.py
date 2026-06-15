from dataclasses import dataclass

from careena_pipeline.models import (
    AssessmentReadiness,
    DialogueState,
    MedicalCase,
    MessageUpdate,
    RecommendationGateDecision,
    SafetyResult,
)


@dataclass
class MessageParsingOutcome:
    raw_safety: SafetyResult
    dialogue_state: DialogueState
    case: MedicalCase | None = None
    message_update: MessageUpdate | None = None
    request_recommendation: bool = False
    force_deterministic_gate: bool = False
    early_response_mode: str | None = None


@dataclass
class ActionPlanningOutcome:
    dialogue_state: DialogueState
    readiness: AssessmentReadiness
    gate: RecommendationGateDecision
