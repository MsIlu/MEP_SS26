import logging

from careena4.models.domain import (
    ActiveQuestion,
    GuidedInputContract,
    GuidedInputMode,
    GuidedInputOption,
    SafetyQuestionContext,
)
from careena4.models.turn import SafetyState


logger = logging.getLogger(__name__)

_FALLBACK_QUESTION = (
    "Sie haben etwas erwähnt, das ich kurz einordnen möchte. "
    "Sind diese Beschwerden gerade sehr stark oder plötzlich aufgetreten?"
)

_QUESTION_SYSTEM_PROMPT = (
    "Du bist ein medizinisches Assistenzsystem. "
    "Formuliere ausschließlich eine kurze, empathische Rückfrage auf Deutsch. "
    "Die Frage soll klären ob ein Notfall vorliegt: "
    "Frage nach Schwerezeichen wie plötzlichem Beginn, starker Intensität oder begleitenden Warnsymptomen. "
    "Formuliere die Frage so, dass 'Ja' einem ernsthaften Notfall entspricht und 'Nein' einem milden Verlauf. "
    "Keine Diagnose nennen. Maximal 2 Sätze. Mit 'Sie' ansprechen."
)


class SafetyClarificationBuilder:
    def __init__(self, llm_client=None) -> None:
        self._llm_client = llm_client

    def build_active_question(self, *, safety_state: SafetyState) -> ActiveQuestion:
        question_code = safety_state.clarification_question_code or "safety_clarification"
        evidence_terms = list(safety_state.evidence_terms)

        prompt_text = self._generate_question(evidence_terms)
        mapping_status = "medgemma_generated" if self._llm_client and evidence_terms else "fallback"
        source_stage = (
            "raw_message"
            if "raw_message" in (safety_state.checked_sources or [])
            else "case_slice"
        )

        safety_context = SafetyQuestionContext(
            question_code=question_code,
            source_stage=source_stage,
            evidence_terms=evidence_terms,
            source_system="STS",
            catalog_mapping_status=mapping_status,
        )
        return self._base_question(prompt_text=prompt_text, safety_context=safety_context)

    def _generate_question(self, evidence_terms: list[str]) -> str:
        if not self._llm_client or not evidence_terms:
            return _FALLBACK_QUESTION

        terms_str = ", ".join(evidence_terms)
        user_prompt = (
            f"Der Patient hat folgende Beschwerden erwähnt: {terms_str}.\n"
            "Formuliere eine kurze Rückfrage, die klärt ob ein medizinischer Notfall vorliegt. "
            "Frage nach spezifischen Schwerezeichen für diese Beschwerde "
            "(z.B. plötzlicher Beginn, sehr starke Intensität, begleitende Warnsymptome)."
        )
        try:
            response = self._llm_client.complete(
                messages=[
                    {"role": "system", "content": _QUESTION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=120,
                temperature=0.3,
                call_name="safety_clarification_question",
            )
            text = (response or "").strip()
            return text if text else _FALLBACK_QUESTION
        except Exception:
            logger.exception("Safety question generation failed; using fallback.")
            return _FALLBACK_QUESTION

    @staticmethod
    def _base_question(
        *,
        prompt_text: str,
        safety_context: SafetyQuestionContext,
    ) -> ActiveQuestion:
        return ActiveQuestion(
            kind="safety_clarification",
            question_intent="free_description",
            prompt_text=prompt_text,
            blocking=True,
            allows_additional_medical_info=False,
            safety_question_code=safety_context.question_code,
            safety_evidence_terms=list(safety_context.evidence_terms),
            safety_context=safety_context,
            guided_input=GuidedInputContract(
                mode=GuidedInputMode.STRUCTURED_REQUIRED,
                free_text_allowed=False,
                options=[
                    GuidedInputOption(
                        code="yes",
                        label="Ja",
                        effect_code="confirms_red_flag",
                    ),
                    GuidedInputOption(
                        code="no",
                        label="Nein",
                        effect_code="clears_red_flag",
                    ),
                    GuidedInputOption(
                        code="unsure",
                        label="Ich bin unsicher",
                        effect_code="keeps_clarification_open",
                    ),
                    GuidedInputOption(
                        code="immediate_help",
                        label="Ich brauche sofort Hilfe",
                        effect_code="confirms_emergency",
                    ),
                ],
            ),
        )
