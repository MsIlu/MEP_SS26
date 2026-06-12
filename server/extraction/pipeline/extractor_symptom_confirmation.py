from extraction.core.extraction_engine import ExtractionEngine
from extraction.models.llm.symptom_confirmation import SymptomConfirmationResult
from extraction.prompts.symptom_confirmation_prompt import (
    SYMPTOM_CONFIRMATION_SYSTEM_PROMPT,
)


class SymptomConfirmationExtractor:
    """
    Resolves symptoms from an assistant follow-up question and the user's reply.
    """

    def __init__(self, engine: ExtractionEngine):
        self.engine = engine

    def extract(
        self,
        *,
        assistant_question: str,
        user_answer: str,
    ) -> SymptomConfirmationResult:
        text = (
            "assistant_question:\n"
            f"{assistant_question}\n\n"
            "user_answer:\n"
            f"{user_answer}"
        )

        return self.engine.extract(
            text=text,
            system_prompt=SYMPTOM_CONFIRMATION_SYSTEM_PROMPT,
            output_schema=SymptomConfirmationResult,
        )
