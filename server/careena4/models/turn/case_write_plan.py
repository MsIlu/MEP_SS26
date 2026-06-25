from pydantic import Field

from careena4.models.common import CaseWriteAction, PipelineModel
from careena4.models.domain import Observation, Person


class CaseWriteStep(PipelineModel):
    action: CaseWriteAction
    claim_index: int
    observation: Observation | None = None
    target_observation_id: str | None = None
    note: str | None = None


class CaseWritePlan(PipelineModel):
    person_update: Person | None = None
    steps: list[CaseWriteStep] = Field(default_factory=list)
    trace_notes: list[str] = Field(default_factory=list)
