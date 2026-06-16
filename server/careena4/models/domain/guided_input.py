from enum import Enum

from pydantic import Field

from careena4.models.common import PipelineModel


class GuidedInputMode(str, Enum):
    FREE_TEXT_ALLOWED = "free_text_allowed"
    STRUCTURED_PREFERRED = "structured_preferred"
    STRUCTURED_REQUIRED = "structured_required"


class GuidedInputOption(PipelineModel):
    code: str
    label: str
    effect_code: str | None = None


class GuidedInputContract(PipelineModel):
    mode: GuidedInputMode = GuidedInputMode.FREE_TEXT_ALLOWED
    free_text_allowed: bool = True
    options: list[GuidedInputOption] = Field(default_factory=list)
