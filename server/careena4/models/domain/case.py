from uuid import uuid4

from pydantic import Field

from careena4.models.common import PipelineModel
from careena4.models.domain.case_issue import CaseIssue
from careena4.models.domain.observation import Observation
from careena4.models.domain.subject import Person
from careena4.models.domain.topic import Topic


class MedicalCase(PipelineModel):
    case_id: str = Field(default_factory=lambda: str(uuid4()))
    topic: Topic | None = None
    person: Person = Field(default_factory=Person)
    observations: list[Observation] = Field(default_factory=list)
    issues: list[CaseIssue] = Field(default_factory=list)

    def central_observations(self) -> list[Observation]:
        return [
            observation
            for observation in self.observations
            if observation.is_central() and not observation.is_negated()
        ]

    def active_observations(self) -> list[Observation]:
        return [
            observation
            for observation in self.observations
            if observation.is_active()
        ]

    @property
    def subject(self) -> Person:
        return self.person

    @subject.setter
    def subject(self, person: Person) -> None:
        self.person = person
