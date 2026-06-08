from uuid import uuid4

from careena_pipeline3.models.domain import DialogueState, MedicalCase


class CareenaPipeline3Session:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.case: MedicalCase | None = None
        self.dialogue_state: DialogueState = DialogueState()
        self.messages: list[dict[str, str]] = []


class CareenaPipeline3SessionStore:
    def __init__(self):
        self._sessions: dict[str, CareenaPipeline3Session] = {}

    def create_session(self) -> str:
        session_id = str(uuid4())
        self._sessions[session_id] = CareenaPipeline3Session(session_id)
        return session_id

    def get(self, session_id: str) -> CareenaPipeline3Session | None:
        return self._sessions.get(session_id)
