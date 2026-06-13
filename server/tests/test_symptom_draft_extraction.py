from inputs.draft_service import cancel_symptom_draft, get_symptom_draft
from inputs.symptom_draft_extraction import SymptomDraftExtractionService
from extraction.models.llm.observation_event import (
    ObservationContext,
    ObservationEvent,
)
from extraction.models.llm.observation_event_list import ObservationEventList
from extraction.models.llm.symptom_confirmation import (
    SymptomConfirmation,
    SymptomConfirmationResult,
)

# These tests keep context-based symptom confirmation independent from the real LLM.

def test_context_confirmation_adds_only_confirmed_symptoms():
    session_id = "confirmation-symptom-session"
    cancel_symptom_draft(session_id)

    confirmation_extractor = _FakeConfirmationExtractor(
        symptoms=[
            SymptomConfirmation(
                label="Bauchschmerzen",
                status="confirmed",
                evidence="Ja, Bauchschmerzen habe ich.",
            ),
            SymptomConfirmation(
                label="Fieber",
                status="denied",
                evidence="Fieber nicht.",
            ),
            SymptomConfirmation(
                label="Schwindel",
                status="uncertain",
                evidence="Nicht sicher.",
            ),
        ]
    )
    service = SymptomDraftExtractionService(
        _FakeObservationExtractor(),
        confirmation_extractor=confirmation_extractor,
    )

    symptoms = service.update_from_text(
        session_id=session_id,
        text="Ja, Bauchschmerzen habe ich. Fieber nicht.",
        confirmation_context="Haben Sie Bauchschmerzen, Fieber oder Schwindel?",
    )

    assert symptoms == ["Bauchschmerzen"]
    assert get_symptom_draft(session_id) == ["Bauchschmerzen"]
    assert confirmation_extractor.last_assistant_question == (
        "Haben Sie Bauchschmerzen, Fieber oder Schwindel?"
    )
    assert confirmation_extractor.last_user_answer == (
        "Ja, Bauchschmerzen habe ich. Fieber nicht."
    )

    cancel_symptom_draft(session_id)


def test_without_confirmation_extractor_only_direct_user_symptoms_are_saved():
    session_id = "direct-symptom-session"
    cancel_symptom_draft(session_id)

    service = SymptomDraftExtractionService(_FakeObservationExtractor())

    symptoms = service.update_from_text(
        session_id=session_id,
        text="Ich habe Bauchschmerzen.",
        confirmation_context="Haben Sie Bauchschmerzen?",
    )

    assert symptoms == ["Bauchschmerzen"]
    assert get_symptom_draft(session_id) == ["Bauchschmerzen"]

    cancel_symptom_draft(session_id)


def test_context_confirmation_failure_keeps_direct_symptoms():
    session_id = "confirmation-failure-session"
    cancel_symptom_draft(session_id)

    service = SymptomDraftExtractionService(
        _FakeObservationExtractor(),
        confirmation_extractor=_FailingConfirmationExtractor(),
    )

    symptoms = service.update_from_text(
        session_id=session_id,
        text="Ich habe Bauchschmerzen.",
        confirmation_context="Haben Sie Fieber?",
    )

    assert symptoms == ["Bauchschmerzen"]
    assert get_symptom_draft(session_id) == ["Bauchschmerzen"]

    cancel_symptom_draft(session_id)


class _FakeObservationExtractor:
    def extract(self, text: str) -> ObservationEventList:
        events = []
        lowered_text = text.casefold()

        if "bauchschmerzen" in lowered_text:
            events.append(_event("event-bauchschmerzen", "Bauchschmerzen"))

        if "fieber" in lowered_text and "fieber nicht" not in lowered_text:
            events.append(_event("event-fieber", "Fieber"))

        return ObservationEventList(events=events)


class _FakeConfirmationExtractor:
    def __init__(self, symptoms: list[SymptomConfirmation]):
        self.symptoms = symptoms
        self.last_assistant_question = None
        self.last_user_answer = None

    def extract(
        self,
        *,
        assistant_question: str,
        user_answer: str,
    ) -> SymptomConfirmationResult:
        self.last_assistant_question = assistant_question
        self.last_user_answer = user_answer

        return SymptomConfirmationResult(symptoms=self.symptoms)


class _FailingConfirmationExtractor:
    def extract(self, *, assistant_question: str, user_answer: str):
        raise RuntimeError("confirmation unavailable")


def _event(
    event_id: str,
    label: str,
    negated: bool = False,
) -> ObservationEvent:
    return ObservationEvent(
        id=event_id,
        type="symptom",
        label=label,
        source_span=label,
        context=ObservationContext(negated=negated),
    )
