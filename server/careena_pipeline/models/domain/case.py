from uuid import uuid4

from pydantic import Field

from careena_pipeline.models.common.base import PipelineModel
from careena_pipeline.models.domain.observation import CaseObservation
from careena_pipeline.models.domain.subject import Subject


class MedicalCase(PipelineModel):
    case_id: str = Field(default_factory=lambda: str(uuid4()))
    subject: Subject = Field(default_factory=Subject)
    observations: list[CaseObservation] = Field(default_factory=list)
    primary_problem_id: str | None = None

    def active_observations(
        self,
        *,
        include_negated: bool = True,
        include_rejected: bool = False,
    ) -> list[CaseObservation]:
        observations = self.observations
        if not include_rejected:
            observations = [
                observation
                for observation in observations
                if observation.status != "user_rejected"
            ]
        if not include_negated:
            observations = [
                observation
                for observation in observations
                if not observation.negated
            ]
        return observations

    def observations_of_type(
        self,
        *types: str,
        include_negated: bool = False,
        include_rejected: bool = False,
    ) -> list[CaseObservation]:
        allowed = set(types)
        return [
            observation
            for observation in self.active_observations(
                include_negated=include_negated,
                include_rejected=include_rejected,
            )
            if observation.type in allowed
        ]

    def complaint_observations(self) -> list[CaseObservation]:
        return self.observations_of_type("symptom", "injury", "measurement", "concern")

    def problem_observations(self) -> list[CaseObservation]:
        return self.complaint_observations() + self.observations_of_type("diagnosis")

    def active_problem_ids(self) -> list[str]:
        return [observation.id for observation in self.problem_observations()]

    def primary_observation(self) -> CaseObservation | None:
        if self.primary_problem_id:
            for observation in self.active_observations():
                if observation.id == self.primary_problem_id:
                    return observation
        candidates = self.problem_observations()
        return candidates[0] if candidates else None

    def primary_focus_label(self) -> str | None:
        observation = self.primary_observation()
        return observation.patient_label if observation is not None else None

    def set_primary_observation(self, observation: CaseObservation | None) -> None:
        self.primary_problem_id = observation.id if observation is not None else None

    def ensure_primary_problem(self) -> None:
        primary = self.primary_observation()
        self.primary_problem_id = primary.id if primary is not None else None
