# Test case references: documents/Testfaelle_Backend.md#t05-chat-logic-und-session-kontext

from chat.logic import ChatLogic
from inputs.draft_service import cancel_symptom_draft, get_symptom_draft
from inputs.symptom_draft_extraction import SymptomDraftExtractionService
from extraction.models.llm.observation_event import (
    ObservationContext,
    ObservationEvent,
)
from extraction.models.llm.observation_event_list import ObservationEventList


def test_chat_logic_merges_llm_extracted_symptoms_into_draft():
    session_id = "chat-logic-symptom-session"
    cancel_symptom_draft(session_id)

    sessions = _FakeSessionManager(session_id)
    chat_logic = ChatLogic(
        sessions,
        _FakeLLMClient(),
        symptom_draft_service=SymptomDraftExtractionService(
            _FakeObservationExtractor(),
        ),
    )

    response = chat_logic.handle_message(
        session_id,
        "Ich habe Kopfschmerzen und Angst, aber keinen Husten.",
    )

    assert response == {"response": "Danke, ich habe das verstanden."}
    assert get_symptom_draft(session_id) == ["Kopfschmerzen", "Angst"]

    cancel_symptom_draft(session_id)


def test_chat_logic_includes_manually_edited_symptoms_in_llm_context():
    session_id = "chat-logic-manual-symptom-session"
    cancel_symptom_draft(session_id)

    from inputs.draft_service import update_symptom_draft

    update_symptom_draft(session_id, ["Bauchschmerzen"])

    sessions = _FakeSessionManager(session_id)
    llm = _FakeLLMClient()
    chat_logic = ChatLogic(sessions, llm)

    response = chat_logic.handle_message(
        session_id,
        "Ich brauche medizinische Hilfe. Was soll ich jetzt tun?",
    )

    assert response == {"response": "Danke, ich habe das verstanden."}
    assert any(
        message["role"] == "system" and "Bauchschmerzen" in message["content"]
        for message in llm.messages
    )

    cancel_symptom_draft(session_id)


class _FakeSessionManager:
    def __init__(self, session_id: str):
        self.messages = {
            session_id: [
                {
                    "role": "system",
                    "content": "System prompt",
                }
            ]
        }

    def get_messages(self, session_id: str) -> list[dict]:
        return self.messages.get(session_id, [])

    def append(self, session_id: str, message: dict) -> None:
        self.messages[session_id].append(message)


class _FakeLLMClient:
    def __init__(self):
        self.messages = []

    def complete(self, *, messages: list[dict], **kwargs) -> str:
        self.messages = messages
        return "Danke, ich habe das verstanden."


class _FakeObservationExtractor:
    def extract(self, text: str) -> ObservationEventList:
        return ObservationEventList(
            events=[
                ObservationEvent(
                    id="event-1",
                    type="symptom",
                    label="Kopfschmerzen",
                    source_span="Kopfschmerzen",
                    context=ObservationContext(negated=False),
                ),
                ObservationEvent(
                    id="event-2",
                    type="symptom",
                    label="Angst",
                    source_span="Angst",
                    context=ObservationContext(negated=False),
                ),
                ObservationEvent(
                    id="event-3",
                    type="symptom",
                    label="Husten",
                    source_span="keinen Husten",
                    context=ObservationContext(negated=True),
                ),
            ]
        )
