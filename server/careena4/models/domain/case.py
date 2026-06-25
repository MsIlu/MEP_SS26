from uuid import uuid4

from pydantic import Field

from careena4.models.common import PipelineModel
from careena4.models.domain.case_issue import CaseIssue
from careena4.models.domain.observation import Observation
from careena4.models.domain.subject import Subject


class MedicalCase(PipelineModel):
    case_id: str = Field(default_factory=lambda: str(uuid4()))
    topic_id: str | None = None
    subject: Subject = Field(default_factory=Subject)
    observations: list[Observation] = Field(default_factory=list)
    issues: list[CaseIssue] = Field(default_factory=list)

    def central_observations(self) -> list[Observation]:
        return [
            observation
            for observation in self.observations
            if observation.topic_relation == "central" and not observation.negated
        ]

    def active_observations(self) -> list[Observation]:
        return [
            observation
            for observation in self.observations
            if observation.status != "rejected" and not observation.negated
        ]
