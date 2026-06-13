from typing import Dict, List
import uuid
import config

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, List[dict]] = {}
        self.session_profiles: Dict[str, int | None] = {}

    def create_session(self, profile_id: int | None = None) -> str:
        session_id = str(uuid.uuid4())

        self.sessions[session_id] = [
            {
                "role": "system",
                "content": config.MASTER_PROMPT
            }
        ]
        self.session_profiles[session_id] = profile_id

        return session_id

    def session_exists(self, session_id: str) -> bool:
        return session_id in self.sessions

    def get_profile_id(self, session_id: str) -> int | None:
        return self.session_profiles.get(session_id)

    def bind_profile(self, session_id: str, profile_id: int | None) -> None:
        if session_id not in self.sessions:
            raise ValueError("Invalid session")

        self.session_profiles[session_id] = profile_id

    def get_messages(self, session_id: str) -> List[dict]:
        return self.sessions.get(session_id, [])

    def append(self, session_id: str, message: dict):
        if session_id not in self.sessions:
            raise ValueError("Invalid session")

        self.sessions[session_id].append(message)
