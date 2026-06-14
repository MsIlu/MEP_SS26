from enum import Enum

from pydantic import Field

from careena_pipeline3.models.common import PipelineModel


class GuidedInputMode(str, Enum):
    """Defines how constrained the next user input should be."""

    FREE_TEXT_ALLOWED = "free_text_allowed"
    STRUCTURED_PREFERRED = "structured_preferred"
    STRUCTURED_REQUIRED = "structured_required"


class GuidedInputOption(PipelineModel):
    """Structured answer option for guided user input."""

    code: str
    label: str
    effect_code: str | None = None


class GuidedInputContract(PipelineModel):
    """Backend-driven input contract for the next user response."""

    mode: GuidedInputMode = GuidedInputMode.FREE_TEXT_ALLOWED
    free_text_allowed: bool = True
    options: list[GuidedInputOption] = Field(default_factory=list)