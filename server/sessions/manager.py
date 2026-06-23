from uuid import uuid4


class SessionManager:
    """
    In-memory chat session store used by the legacy FastAPI chat flow.

    Sessions are process-local and reset when the backend restarts.
    """

    def __init__(self):
        self._sessions: dict[str, dict] = {}

    def create_session(self, profile_id: int | None = None) -> str:
        session_id = str(uuid4())
        self._sessions[session_id] = {
            "profile_id": profile_id,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Du bist Careena, eine vorsichtige medizinische "
                        "Orientierungshilfe. Stelle Rückfragen, wenn Angaben "
                        "fehlen, und gib keine Diagnose."
                    ),
                }
            ],
        }
        return session_id

    def session_exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def get_profile_id(self, session_id: str) -> int | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None

        return session.get("profile_id")

    def bind_profile(self, session_id: str, profile_id: int) -> None:
        session = self._sessions.get(session_id)
        if session is None:
            return

        session["profile_id"] = profile_id

    def get_messages(self, session_id: str) -> list[dict]:
        session = self._sessions.get(session_id)
        if session is None:
            return []

        return session["messages"]

    def append(self, session_id: str, message: dict) -> None:
        messages = self.get_messages(session_id)
        if not messages:
            return

        messages.append(message)
