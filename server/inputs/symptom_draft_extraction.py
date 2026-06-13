import logging

from inputs.draft_service import get_symptom_draft, merge_extracted_symptoms

logger = logging.getLogger(__name__)


class SymptomDraftExtractionService:
    """
    Updates the editable symptom draft from structured extraction.

    The regular observation extractor reads symptoms directly from the user's
    message. The optional confirmation extractor resolves follow-up answers
    such as "yes, but only slightly" against Careena's previous question.
    """

    def __init__(self, observation_extractor, confirmation_extractor=None):
        self.observation_extractor = observation_extractor
        self.confirmation_extractor = confirmation_extractor

    def update_from_text(
        self,
        session_id: str,
        text: str,
        confirmation_context: str | None = None,
    ) -> list[str]:
        symptom_labels = self._extract_direct_symptoms(
            session_id=session_id,
            text=text,
        )

        if confirmation_context and self.confirmation_extractor is not None:
            symptom_labels.extend(
                self._extract_confirmed_context_symptoms(
                    session_id=session_id,
                    confirmation_context=confirmation_context,
                    user_answer=text,
                )
            )

        return merge_extracted_symptoms(session_id, symptom_labels)

    def _extract_direct_symptoms(self, session_id: str, text: str) -> list[str]:
        try:
            observations = self.observation_extractor.extract(text)
        except Exception:
            logger.exception(
                "Symptom draft extraction failed for session_id=%s",
                session_id,
            )
            return get_symptom_draft(session_id)

        return [
            event.label
            for event in observations.events
            if event.type == "symptom" and not event.context.negated
        ]

    def _extract_confirmed_context_symptoms(
        self,
        session_id: str,
        confirmation_context: str,
        user_answer: str,
    ) -> list[str]:
        try:
            result = self.confirmation_extractor.extract(
                assistant_question=confirmation_context,
                user_answer=user_answer,
            )
        except Exception:
            logger.exception(
                "Symptom confirmation extraction failed for session_id=%s",
                session_id,
            )
            return []

        return [
            symptom.label
            for symptom in result.symptoms
            if symptom.status == "confirmed"
        ]
