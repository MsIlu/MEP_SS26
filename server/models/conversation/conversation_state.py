from pydantic import Field

from ..base.base import BaseSchema

"""
Data structure to control the conversation within a session
not medical

:param current_phase    current phase of the conversation
:param missing_information  missing information
:param pending_questions  store questions that need to be answered
:param summary_ready    flag to mark enough information gathered
:param summary_confirmed flag to mark summary confirmed by patient
:param assessment_complete flag to end conversation.
"""
class ConversationState(BaseSchema):
    current_phase: str = "information_gathering"

    missing_information: list[str] = Field(default_factory=list)

    pending_questions: list[str] = Field(default_factory=list)

    summary_ready: bool = False

    summary_confirmed: bool = False

    assessment_complete: bool = False