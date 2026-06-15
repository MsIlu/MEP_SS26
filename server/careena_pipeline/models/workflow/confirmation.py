from pydantic import Field

from careena_pipeline.models.common.base import PipelineModel
from careena_pipeline.models.domain.observation import CaseObservation


class ConfirmationUpdate(PipelineModel):
    confirmed_observation_ids: list[str] = Field(default_factory=list)
    rejected_observation_ids: list[str] = Field(default_factory=list)
    corrected_observations: list[CaseObservation] = Field(default_factory=list)
    added_observations: list[CaseObservation] = Field(default_factory=list)
