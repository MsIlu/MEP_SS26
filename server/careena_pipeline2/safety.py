from careena_pipeline2.models import MedicalCase, RedFlagStatus, SafetyResult
from red_flags.detector import detect_medical_red_flags


class SafetyGate:
    """Runs rule-based red flag checks on raw text and structured case data."""

    def evaluate_raw_text(self, raw_text: str) -> SafetyResult:
        """Check the original user message for possible red flags."""
        return self._evaluate_text(source_name="raw_text", source_text=raw_text)

    def evaluate_structured_case(self, case: MedicalCase | None) -> SafetyResult:
        """Check structured case data for possible red flags."""
        if case is None:
            return SafetyResult(
                red_flag_detected=False,
                confidence=0.0,
                matched_flags=[],
                checked_sources=[],
                action="continue",
            )

        return self._evaluate_text(source_name="structured_case", source_text=self._case_text(case))

    def evaluate(
        self,
        *,
        raw_text: str,
        case: MedicalCase | None = None,
    ) -> SafetyResult:
        """
        Backward-compatible safety check.

        This method keeps the old contract alive for existing pipeline code.
        New orchestration should use evaluate_raw_text(), evaluate_structured_case()
        and SafetyDecisionMerger instead.
        """
        raw_result = self.evaluate_raw_text(raw_text)

        if raw_result.red_flag_detected or case is None:
            return raw_result

        structured_result = self.evaluate_structured_case(case)

        if structured_result.red_flag_detected:
            return structured_result

        checked_sources = raw_result.checked_sources + structured_result.checked_sources

        return SafetyResult(
            red_flag_detected=False,
            confidence=0.0,
            matched_flags=[],
            checked_sources=checked_sources,
            action="continue",
        )

    def _evaluate_text(self, *, source_name: str, source_text: str) -> SafetyResult:
        """Run the existing hardcoded red flag detector against one text source."""
        normalized_text = (source_text or "").strip()

        if not normalized_text:
            return SafetyResult(
                red_flag_detected=False,
                confidence=0.0,
                matched_flags=[],
                checked_sources=[],
                action="continue",
            )

        result = detect_medical_red_flags(normalized_text)

        if result.get("red_flag"):
            return SafetyResult(
                red_flag_detected=True,
                confidence=1.0,
                matched_flags=self._matched_flags(result),
                checked_sources=[source_name],
                action=(
                    "interrupt_emergency_flow"
                    if result.get("block_ai_response", True)
                    else "continue"
                ),
                severity=result.get("severity"),
                rule_id=result.get("rule_id"),
                rule_name=result.get("rule_name"),
                category=result.get("category"),
                message_key=result.get("message_key"),
                matched_keywords=[
                    str(item) for item in result.get("matched_keywords", [])
                ],
            )

        return SafetyResult(
            red_flag_detected=False,
            confidence=0.0,
            matched_flags=[],
            checked_sources=[source_name],
            action="continue",
        )

    @staticmethod
    def _case_text(case: MedicalCase) -> str:
        """Create searchable text from active structured observations."""
        parts = [
            observation.searchable_text
            for observation in case.active_observations()
            if observation.searchable_text
        ]
        return " ".join(parts)

    @staticmethod
    def _matched_flags(result: dict) -> list[str]:
        """Build a compact list of matched red flag identifiers and keywords."""
        flags: list[str] = []

        rule_id = result.get("rule_id")
        if rule_id:
            flags.append(str(rule_id))

        rule_name = result.get("rule_name")
        if rule_name:
            flags.append(str(rule_name))

        flags.extend(str(item) for item in result.get("matched_keywords", []))
        return flags


class SafetyDecisionMerger:
    """Combines raw and structured red flag checks into one final status."""

    def merge(
        self,
        *,
        raw_result: SafetyResult,
        structured_result: SafetyResult | None = None,
    ) -> RedFlagStatus:
        """Merge raw-text and structured safety checks."""
        raw_red_flag = raw_result.red_flag_detected
        structured_red_flag = (
            structured_result.red_flag_detected
            if structured_result is not None
            else None
        )

        matched_keywords = list(raw_result.matched_keywords or [])
        reason_tags: list[str] = []

        if raw_red_flag:
            reason_tags.append("raw_text_red_flag_candidate")

        if structured_red_flag is True:
            reason_tags.append("structured_red_flag_confirmed")
            if structured_result:
                matched_keywords.extend(structured_result.matched_keywords or [])

        if structured_red_flag is True:
            return RedFlagStatus(
                raw_red_flag=raw_red_flag,
                structured_red_flag=True,
                final_status="confirmed",
                red_flag=True,
                requires_safety_question=False,
                safety_question=None,
                reason_tags=reason_tags,
                matched_keywords=self._dedupe(matched_keywords),
            )

        if raw_red_flag and structured_red_flag is None:
            return RedFlagStatus(
                raw_red_flag=True,
                structured_red_flag=None,
                final_status="candidate",
                red_flag=False,
                requires_safety_question=True,
                safety_question=(
                    "Bestehen zusätzlich Atemnot, Brustschmerzen, "
                    "Bewusstseinsstörungen, Lähmungen oder sehr starke Beschwerden?"
                ),
                reason_tags=reason_tags,
                matched_keywords=self._dedupe(matched_keywords),
            )
        
        if raw_red_flag and structured_red_flag is False:
            return RedFlagStatus(
                raw_red_flag=True,
                structured_red_flag=False,
                final_status="candidate",
                red_flag=False,
                requires_safety_question=True,
                safety_question=(
                    "Bestehen zusätzlich Atemnot, Brustschmerzen, "
                    "Bewusstseinsstörungen, Lähmungen oder sehr starke Beschwerden?"
                ),
                reason_tags=reason_tags + ["raw_candidate_not_confirmed_structurally"],
                matched_keywords=self._dedupe(matched_keywords),
            )

        return RedFlagStatus(
            raw_red_flag=False,
            structured_red_flag=structured_red_flag,
            final_status="none",
            red_flag=False,
            requires_safety_question=False,
            safety_question=None,
            reason_tags=["no_red_flag_detected"],
            matched_keywords=[],
        )

    @staticmethod
    def _dedupe(values: list[str]) -> list[str]:
        """Remove duplicates while preserving order."""
        seen: set[str] = set()
        result: list[str] = []

        for value in values:
            normalized = value.strip().lower()
            if not normalized or normalized in seen:
                continue

            seen.add(normalized)
            result.append(value)

        return result