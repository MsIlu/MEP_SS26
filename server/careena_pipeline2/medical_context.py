from topic_filter import is_health_related, is_smalltalk_or_boredom

from careena_pipeline2.models import MedicalContextStatus

"""
Medical context gate for Careena Pipeline 2.

This module separates obvious non-medical input from potentially medical or
safety-relevant input. It is intentionally conservative: unclear messages may
still continue into the structured pipeline.
"""

from topic_filter import is_health_related, is_smalltalk_or_boredom

from careena_pipeline2.models import MedicalContextStatus


class MedicalContextGate:
    """Checks whether a message belongs to Careena's medical scope."""

    def evaluate_raw_text(self, text: str) -> MedicalContextStatus:
        """Run a fast rule-based context check on the raw user message."""
        normalized = (text or "").strip()

        if not normalized:
            return MedicalContextStatus(
                raw_status="unclear",
                final_status="unclear",
                confidence=0.0,
                reason_tags=["empty_input"],
            )

        if is_smalltalk_or_boredom(normalized):
            return MedicalContextStatus(
                raw_status="smalltalk",
                final_status="smalltalk",
                confidence=0.8,
                reason_tags=["smalltalk_or_boredom"],
            )

        if is_health_related(normalized):
            return MedicalContextStatus(
                raw_status="in_scope",
                final_status="in_scope",
                confidence=0.8,
                reason_tags=["health_related_keyword"],
            )

        return MedicalContextStatus(
            raw_status="out_of_scope",
            final_status="out_of_scope",
            confidence=0.7,
            reason_tags=["no_health_context_detected"],
        )

    def evaluate_structured_case(self, case) -> MedicalContextStatus:
        """Check medical context based on the structured case object."""
        # Keep this simple for now. We only need the interface.
        # Later we can inspect symptoms, observations, profile context and diary data.
        has_problem = bool(getattr(case, "chief_complaint", None)) or bool(
            getattr(case, "symptoms", None)
        )

        if has_problem:
            return MedicalContextStatus(
                raw_status="not_checked",
                structured_status="in_scope",
                final_status="in_scope",
                confidence=0.8,
                reason_tags=["structured_case_contains_medical_problem"],
            )

        return MedicalContextStatus(
            raw_status="not_checked",
            structured_status="unclear",
            final_status="unclear",
            confidence=0.3,
            reason_tags=["structured_case_without_clear_problem"],
        )