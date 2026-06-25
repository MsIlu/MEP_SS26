from __future__ import annotations

from careena_pipeline3.models.turn import TurnContext
from careena_pipeline3.models.workflow import RecommendationResult


class RecommendationResultBuilder:
    """Builds the structured Call-3 recommendation contract from canonical state."""

    def build(self, *, context: TurnContext) -> RecommendationResult:
        focus_label = (
            context.medical_case.current_case_frame_label()
            if context.medical_case is not None
            else None
        )
        summary = (
            f"Es liegen ausreichend Angaben zum aktuellen Fallrahmen {focus_label} vor."
            if focus_label
            else "Es liegen ausreichend Angaben zum aktuellen medizinischen Fall vor."
        )

        reasons = ["Die Empfehlung wurde angefordert."]
        if context.assessment_readiness.ready:
            reasons.append("Es sind aktuell keine blockierenden Pflichtangaben offen.")

        limitations = [
            "Die eigentliche Recommendation-Engine ist in careena_pipeline3 noch nicht umgesetzt.",
            "Dringlichkeit, Versorgungsstufe und Fachrichtung bleiben bis zur spaeteren Call-3-Logik offen.",
        ]

        return RecommendationResult(
            allowed=True,
            summary=summary,
            reasons=reasons,
            limitations=limitations,
        )
