from pydantic import Field

from careena_pipeline3.models.common import (
    Call2Task,
    ExtractionProfile,
    IntentCategory,
    MessageRole,
    PipelineModel,
)


class IntentGatewaySignals(PipelineModel):
    person_reference_present: bool = False
    multi_person_context: bool = False
    subject_relation_unclear: bool = False
    additional_medical_information: bool = False
    symptom_present: bool = False
    injury_present: bool = False
    measurement_present: bool = False
    medication_present: bool = False
    recommendation_request: bool = False


class IntentGateway(PipelineModel):
    category: IntentCategory
    message_role: MessageRole
    extraction_required: bool = False
    extraction_profile: ExtractionProfile = "default"
    signals: IntentGatewaySignals = Field(default_factory=IntentGatewaySignals)
    call2_tasks: list[Call2Task] = Field(default_factory=list)

    @property
    def is_medical(self) -> bool:
        return self.category not in {"smalltalk", "not_medical"}
