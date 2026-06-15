from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from careena_pipeline3.models.domain import CaseObservation, MedicalCase


ObservationMatchStatus = Literal["no_match", "single_match", "ambiguous_match"]
ObservationChangeKind = Literal[
    "enrichment",
    "correction",
    "confirmation",
    "contradiction",
    "new_instance",
]
CaseUpdateAction = Literal[
    "create_observation",
    "enrich_observation",
    "correct_observation",
    "confirm_observation",
    "flag_conflict",
    "defer_update",
]
DialogueConsequence = Literal[
    "none",
    "ask_conflict_followup",
    "ask_disambiguation_followup",
    "request_confirmation",
]


"""
Date: 2026-06-08
Last changed: 2026-06-08
Author: workbench@freddy

Short description:
Represents the result of matching an incoming observation against the current medical case.
It keeps candidate targets and trace notes for later update decisions.
"""
@dataclass(slots=True)
class ObservationMatchResult:
    status: ObservationMatchStatus
    candidates: list[CaseObservation] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def single_candidate(self) -> CaseObservation | None:
        if self.status != "single_match" or len(self.candidates) != 1:
            return None
        return self.candidates[0]


"""
Date: 2026-06-08
Last changed: 2026-06-08
Author: workbench@freddy

Short description:
Represents the explicit update decision for one incoming observation.
It captures match status, change kind, action, and any dialogue consequence.
"""
@dataclass(slots=True)
class ObservationUpdateDecision:
    match_status: ObservationMatchStatus
    change_kind: ObservationChangeKind
    action: CaseUpdateAction
    target: CaseObservation | None = None
    dialogue_consequence: DialogueConsequence = "none"
    notes: list[str] = field(default_factory=list)


"""
Date: 2026-06-08
Last changed: 2026-06-08
Author: workbench@freddy

Short description:
Carries the result of applying one message delta to canonical case truth.
It returns the updated case plus trace, decision, and dialogue consequence information.
"""
@dataclass(slots=True)
class CaseUpdateOutcome:
    medical_case: MedicalCase
    trace_notes: list[str] = field(default_factory=list)
    dialogue_consequences: list[DialogueConsequence] = field(default_factory=list)
    decision_log: list[ObservationUpdateDecision] = field(default_factory=list)
