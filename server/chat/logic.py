import config
from topic_filter import (
    is_health_related,
    is_smalltalk_or_boredom,
    OUT_OF_SCOPE_RESPONSE,
    SMALLTALK_GOODBYE_RESPONSE,
)
from red_flags.detector import detect_medical_red_flags

"""
Author @Freddy
Logic is propably not a good name, its okay for now
"""
class ChatLogic:
    def __init__(self, session_manager, llm_client):
        self.sessions = session_manager
        self.llm = llm_client

    """
    Baut einen kleineren Kontext für das LLM:
    - Systemprompt bleibt immer enthalten
    - nur die letzten Chatnachrichten werden an das Modell geschickt
    - der vollständige Verlauf bleibt trotzdem in sessions gespeichert
    """
    def _build_context(self, messages: list[dict]) -> list[dict]:
        system_messages = [m for m in messages if m["role"] == "system"]
        chat_messages = [m for m in messages if m["role"] != "system"]

        return system_messages + chat_messages[-config.MAX_HISTORY_MESSAGES:]

    def handle_message(self, session_id: str, user_input: str) -> dict:

        messages = self.sessions.get_messages(session_id)

        if not messages:
            return {"response": "Fehler: Ungültige Session-ID"}

        if not user_input.strip():
            return {"response": "Fehler: Leere Eingabe."}

        # 1. Smalltalk
        if is_smalltalk_or_boredom(user_input):
            return {"response": SMALLTALK_GOODBYE_RESPONSE}

        # 2. Topic filter
        if not is_health_related(user_input, messages):
            return {"response": OUT_OF_SCOPE_RESPONSE}

        # 3. store user message
        self.sessions.append(session_id, {
            "role": "user",
            "content": user_input
        })

        # 4. red flags
        # Red-Flag-Prüfung vor der KI-Antwort
        red_flag_result = detect_medical_red_flags(user_input)

        if red_flag_result.get("red_flag") and red_flag_result.get("block_ai_response", False):
            print(f"[{session_id}] Red flag detected: {red_flag_result}")

            warning_text = (
                    "Wichtiger Hinweis:\n"
                    "Ihre Angaben können auf eine akute Notfallsituation hinweisen.\n\n"
                    "Nächster Schritt:\n"
                    "Bitte wählen Sie sofort den Notruf 112 oder holen Sie umgehend medizinische Hilfe.\n\n"
                    "Hinweis:\n"
                    "Diese Einschätzung ersetzt keine ärztliche Untersuchung und stellt keine Diagnose dar."
                    )

            messages.append({
                    "role": "assistant",
                    "content": warning_text
                    })

            return {
                    "response": warning_text,
                    "red_flag": True,
                    "severity": red_flag_result.get("severity"),
                    "action": red_flag_result.get("action"),
                    "rule_id": red_flag_result.get("rule_id"),
                    "rule_name": red_flag_result.get("rule_name"),
                    "category": red_flag_result.get("category"),
                    "message_key": red_flag_result.get("message_key"),
                    "matched_keywords": red_flag_result.get("matched_keywords", [])
                    }

        # 5. LLM call
        llm_messages = self._build_context(self.sessions.get_messages(session_id))
        reply = self.llm.complete(messages=llm_messages).strip()

        if not reply:
            reply = "⚠️ Keine Antwort vom Modell."

        self.sessions.append(session_id, {
            "role": "assistant",
            "content": reply
        })

        return {"response": reply}
