from pydantic import Field

from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.domain import DialogueState, MedicalCase


class TurnInput(PipelineModel):
    message: str
    session_id: str | None = None
    conversation_messages: list[dict[str, str]] = Field(default_factory=list)
    existing_case: MedicalCase | None = None
    existing_dialogue_state: DialogueState | None = None
