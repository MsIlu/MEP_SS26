from careena_pipeline.models import MedicalCase, SafetyResult
from red_flags.detector import detect_medical_red_flags


class SafetyGate:
    """
    Minimal safety hook.

    It already accepts raw text, extracted understanding, and the internal case
    so the later red-flag system can check all three without changing the
    orchestration contract.
    """

    def evaluate(
        self,
        *,
        raw_text: str,
        case: MedicalCase | None = None,
    ) -> SafetyResult:
        sources = [("raw_text", raw_text)]

        if case is not None:
            sources.append(("case", self._case_text(case)))

        checked_sources = []

        for source_name, source_text in sources:
            if not source_text.strip():
                continue

            checked_sources.append(source_name)
            result = detect_medical_red_flags(source_text)

            if result.get("red_flag"):
                return SafetyResult(
                    red_flag_detected=True,
                    confidence=1.0,
                    matched_flags=self._matched_flags(result),
                    checked_sources=checked_sources,
                    action="interrupt_emergency_flow"
                    if result.get("block_ai_response", True)
                    else "continue",
                    severity=result.get("severity"),
                    rule_id=result.get("rule_id"),
                    rule_name=result.get("rule_name"),
                    category=result.get("category"),
                    message_key=result.get("message_key"),
                    matched_keywords=[
                        str(item)
                        for item in result.get("matched_keywords", [])
                    ],
                )

        return SafetyResult(
            red_flag_detected=False,
            confidence=0.0,
            matched_flags=[],
            checked_sources=checked_sources,
            action="continue",
        )

    @staticmethod
    def _case_text(case: MedicalCase) -> str:
        parts = []
        for observation in case.observations:
            parts.append(observation.searchable_text)
        return " ".join(parts)

    @staticmethod
    def _matched_flags(result: dict) -> list[str]:
        flags = []

        rule_id = result.get("rule_id")
        if rule_id:
            flags.append(str(rule_id))

        rule_name = result.get("rule_name")
        if rule_name:
            flags.append(str(rule_name))

        flags.extend(str(item) for item in result.get("matched_keywords", []))
        return flags
