from dataclasses import dataclass
from uuid import uuid4

from careena4.models.domain import ConversationState, MedicalCase, RecommendationState
from careena4.models.input import SymptomInputDraft


@dataclass
class PendingReplayContext:
    medical_case: MedicalCase | None
    conversation_state: ConversationState
    recommendation_state: RecommendationState
    symptom_input_draft: SymptomInputDraft | None
    messages: list[dict[str, str]]


class Careena4Session:
    def __init__(self, session_id: str, profile_id: int | None = None):
        self.session_id = session_id
        self.profile_id: int | None = profile_id
        self.medical_case: MedicalCase | None = None
        self.conversation_state: ConversationState = ConversationState()
        self.recommendation_state: RecommendationState = RecommendationState()
        self.symptom_input_draft: SymptomInputDraft = SymptomInputDraft(session_id=session_id)
        self.messages: list[dict[str, str]] = []
        self.last_turn_interpretation = None
        self.last_turn_understanding = None
        self.pending_replay_context: PendingReplayContext | None = None


class Careena4SessionStore:
    def __init__(self):
        self._sessions: dict[str, Careena4Session] = {}

    def create_session(self, profile_id: int | None = None) -> str:
        session_id = str(uuid4())
        self._sessions[session_id] = Careena4Session(session_id, profile_id=profile_id)
        return session_id

    def get(self, session_id: str) -> Careena4Session | None:
        return self._sessions.get(session_id)
