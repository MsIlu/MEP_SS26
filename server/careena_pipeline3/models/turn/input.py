from pydantic import Field

from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.domain import ConcernState, DialogueState, MedicalCase


ENTRY_HISTORY_LIMIT = 4
EXTRACTION_HISTORY_LIMIT = 4
TRANSITION_HISTORY_LIMIT = 4
RESPONSE_HISTORY_LIMIT = 6


class TurnInput(PipelineModel):
    """
    Boundary contract for one runtime turn.

    Field groups:
    - persisted truth:
      `persisted_case`, `persisted_dialogue_state`, `persisted_concern_state`
    - turn work input:
      `message`, `session_id`
    - purpose-specific recent history slices:
      `entry_history_messages`,
      `extraction_history_messages`,
      `transition_history_messages`,
      `response_history_messages`
    """

    message: str
    session_id: str | None = None
    entry_history_messages: list[dict[str, str]] = Field(default_factory=list)
    extraction_history_messages: list[dict[str, str]] = Field(default_factory=list)
    transition_history_messages: list[dict[str, str]] = Field(default_factory=list)
    response_history_messages: list[dict[str, str]] = Field(default_factory=list)
    persisted_case: MedicalCase | None = None
    persisted_dialogue_state: DialogueState | None = None
    persisted_concern_state: ConcernState | None = None

    @classmethod
    def from_persisted_state(
        cls,
        *,
        message: str,
        session_id: str | None = None,
        conversation_messages: list[dict[str, str]] | None = None,
        persisted_case: MedicalCase | None = None,
        persisted_dialogue_state: DialogueState | None = None,
        persisted_concern_state: ConcernState | None = None,
    ) -> "TurnInput":
        history = list(conversation_messages or [])
        return cls(
            message=message,
            session_id=session_id,
            entry_history_messages=_recent_history(history, ENTRY_HISTORY_LIMIT),
            extraction_history_messages=_recent_history(
                history,
                EXTRACTION_HISTORY_LIMIT,
            ),
            transition_history_messages=_recent_history(
                history,
                TRANSITION_HISTORY_LIMIT,
            ),
            response_history_messages=_recent_history(history, RESPONSE_HISTORY_LIMIT),
            persisted_case=persisted_case,
            persisted_dialogue_state=persisted_dialogue_state,
            persisted_concern_state=persisted_concern_state,
        )


def _recent_history(
    messages: list[dict[str, str]],
    limit: int,
) -> list[dict[str, str]]:
    if limit <= 0:
        return []
    return list(messages[-limit:])
