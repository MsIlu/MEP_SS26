from typing import Dict, List
import uuid
import config

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, List[dict]] = {}

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())

        self.sessions[session_id] = [
            {
                "role": "system",
                "content": config.MASTER_PROMPT
            }
        ]

        return session_id

    def get_messages(self, session_id: str) -> List[dict]:
        return self.sessions.get(session_id, [])

    def append(self, session_id: str, message: dict):
        if session_id not in self.sessions:
            raise ValueError("Invalid session")

        self.sessions[session_id].append(message)