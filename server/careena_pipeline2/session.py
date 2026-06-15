from uuid import uuid4

from careena_pipeline2.models import DialogueState, MedicalCase


class CareenaSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.case: MedicalCase | None = None
        self.dialogue_state: DialogueState = DialogueState()
        self.messages: list[dict[str, str]] = []


class CareenaSessionStore:
    def __init__(self):
        self._sessions: dict[str, CareenaSession] = {}

    def create_session(self) -> str:
        session_id = str(uuid4())
        self._sessions[session_id] = CareenaSession(session_id)
        return session_id

    def get(self, session_id: str) -> CareenaSession | None:
        return self._sessions.get(session_id)
