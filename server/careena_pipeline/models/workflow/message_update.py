from pydantic import Field

from careena_pipeline.state.module_registry import ModuleName, RequirementRef
from careena_pipeline.models.common.base import PipelineModel
from careena_pipeline.models.common.types import (
    MessageRole,
    PlannerModule,
)
from careena_pipeline.models.domain.observation import CaseObservation
from careena_pipeline.models.domain.subject import Subject


class MessageUpdate(PipelineModel):
    raw_text: str
    intent_category: str | None = None
    is_medical: bool = False
    extraction_required: bool = False
    intent_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    subject: Subject | None = None
    observations_added: list[CaseObservation] = Field(default_factory=list)
    negated_observations_added: list[CaseObservation] = Field(default_factory=list)
    user_requests_recommendation: bool = False
    possible_new_topic: bool = False
    notes: list[str] = Field(default_factory=list)
    message_role: MessageRole = "new_information"
    active_modules: list[ModuleName] = Field(default_factory=list)
    required_fields: list[RequirementRef] = Field(default_factory=list)
    resolved_fields: list[RequirementRef] = Field(default_factory=list)
    recommended_modules: list[PlannerModule] = Field(default_factory=list)

    @property
    def subject_update(self) -> Subject | None:
        return self.subject

    @property
    def extracted_requirements(self) -> list[RequirementRef]:
        return self.required_fields

    @property
    def resolved_requirements(self) -> list[RequirementRef]:
        return self.resolved_fields
