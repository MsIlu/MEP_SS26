from pydantic import Field

from careena4.models.common import CaseWriteAction, PipelineModel
from careena4.models.domain import Observation, Subject


class CaseWriteStep(PipelineModel):
    action: CaseWriteAction
    claim_index: int
    observation: Observation | None = None
    target_observation_id: str | None = None
    note: str | None = None


class CaseWritePlan(PipelineModel):
    topic_id_update: str | None = None
    subject_update: Subject | None = None
    steps: list[CaseWriteStep] = Field(default_factory=list)
    trace_notes: list[str] = Field(default_factory=list)
