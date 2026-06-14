import re

import config
from inputs.draft_service import get_symptom_draft
from red_flags.detector import detect_medical_red_flags
from topic_filter import (
    OUT_OF_SCOPE_RESPONSE,
    SMALLTALK_GOODBYE_RESPONSE,
    is_health_related,
    is_smalltalk_or_boredom,
)


class ChatLogic:
    """
    Coordinates one chat turn, including filtering, red flags and LLM calls.
    """

    def __init__(self, session_manager, llm_client, symptom_draft_service=None):
        self.sessions = session_manager
        self.llm = llm_client
        self.symptom_draft_service = symptom_draft_service

    def _build_context(
        self,
        messages: list[dict],
        symptom_draft: list[str] | None = None,
    ) -> list[dict]:
        """
        Build a compact LLM context while keeping full history in the session.
        """

        system_messages = [m for m in messages if m["role"] == "system"]
        chat_messages = [m for m in messages if m["role"] != "system"]
        draft_message = self._build_symptom_draft_message(symptom_draft or [])

        return (
            system_messages
            + ([draft_message] if draft_message is not None else [])
            + chat_messages[-config.MAX_HISTORY_MESSAGES:]
        )

    def _build_symptom_draft_message(self, symptoms: list[str]) -> dict | None:
        if not symptoms:
            return None

        symptom_list = ", ".join(symptoms)

        return {
            "role": "system",
            "content": (
                "Aktuell vom Nutzer bearbeiteter Symptom-Entwurf "
                f"(keine Diagnose): {symptom_list}. "
                "Beruecksichtige diese Angaben als vom Nutzer genannte "
                "Beschwerden und frage nach, wenn wichtige Details fehlen."
            ),
        }

    def _last_assistant_message(self, messages: list[dict]) -> str | None:
        """
        Return the previous assistant turn for follow-up symptom confirmation.
        """

        for message in reversed(messages):
            if message.get("role") == "assistant":
                return message.get("content", "")

        return None

    def handle_message(self, session_id: str, user_input: str) -> dict:
        messages = self.sessions.get_messages(session_id)

        if not messages:
            return {"response": "Fehler: Ungültige Session-ID"}

        if not user_input.strip():
            return {"response": "Fehler: Leere Eingabe."}

        # Smalltalk and off-topic replies do not update medical drafts.
        if is_smalltalk_or_boredom(user_input):
            return {"response": SMALLTALK_GOODBYE_RESPONSE}

        if not is_health_related(user_input, messages):
            return {"response": OUT_OF_SCOPE_RESPONSE}

        confirmation_context = self._last_assistant_message(messages)

        self.sessions.append(
            session_id,
            {
                "role": "user",
                "content": user_input,
            },
        )

        if self.symptom_draft_service is not None:
            self.symptom_draft_service.update_from_text(
                session_id,
                user_input,
                confirmation_context=confirmation_context,
            )

        # Red flags are evaluated before the LLM can produce a normal answer.
        red_flag_result = detect_medical_red_flags(user_input)

        if red_flag_result.get("red_flag") and red_flag_result.get(
            "block_ai_response",
            False,
        ):
            print(f"[{session_id}] Red flag detected: {red_flag_result}")

            warning_text = (
                "Wichtiger Hinweis:\n"
                "Ihre Angaben können auf eine akute Notfallsituation hinweisen.\n\n"
                "Nächster Schritt:\n"
                "Bitte wählen Sie sofort den Notruf 112 oder holen Sie umgehend medizinische Hilfe.\n\n"
                "Hinweis:\n"
                "Diese Einschätzung ersetzt keine ärztliche Untersuchung und stellt keine Diagnose dar."
            )

            messages.append(
                {
                    "role": "assistant",
                    "content": warning_text,
                }
            )

            return {
                "response": warning_text,
                "red_flag": True,
                "severity": red_flag_result.get("severity"),
                "action": red_flag_result.get("action"),
                "rule_id": red_flag_result.get("rule_id"),
                "rule_name": red_flag_result.get("rule_name"),
                "category": red_flag_result.get("category"),
                "message_key": red_flag_result.get("message_key"),
                "matched_keywords": red_flag_result.get("matched_keywords", []),
            }

        llm_messages = self._build_context(
            self.sessions.get_messages(session_id),
            symptom_draft=get_symptom_draft(session_id),
        )
        reply = self.llm.complete(messages=llm_messages).strip()

        # Remove accidental role labels generated by the model.
        reply = re.sub(
            r"^\s*#*\s*Assistant\s*:?\s*",
            "",
            reply,
            flags=re.IGNORECASE,
        ).strip()

        if not reply:
            reply = "Keine Antwort vom Modell."

        self.sessions.append(
            session_id,
            {
                "role": "assistant",
                "content": reply,
            },
        )

        return {"response": reply}
