from uuid import uuid4

from careena4.models.domain import CaseTopic, ConversationState, MedicalCase, RecommendationState


class Careena4Session:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.case_topic: CaseTopic | None = None
        self.medical_case: MedicalCase | None = None
        self.conversation_state: ConversationState = ConversationState()
        self.recommendation_state: RecommendationState = RecommendationState()
        self.messages: list[dict[str, str]] = []


class Careena4SessionStore:
    def __init__(self):
        self._sessions: dict[str, Careena4Session] = {}

    def create_session(self) -> str:
        session_id = str(uuid4())
        self._sessions[session_id] = Careena4Session(session_id)
        return session_id

    def get(self, session_id: str) -> Careena4Session | None:
        return self._sessions.get(session_id)
