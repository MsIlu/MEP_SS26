from careena_pipeline.models.common.base import PipelineModel
from careena_pipeline.models.common.types import (
    ExtractionProfile,
    IntentCategory,
    MessageRole,
)


class IntentGateway(PipelineModel):
    category: IntentCategory
    message_role: MessageRole
    extraction_required: bool = False
    extraction_profile: ExtractionProfile = "default"

    @property
    def is_medical(self) -> bool:
        return self.category not in {"smalltalk", "not_medical"}
