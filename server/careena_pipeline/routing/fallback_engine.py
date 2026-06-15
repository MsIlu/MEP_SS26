from careena_pipeline.models import MedicalCase, Recommendation
from careena_pipeline.pipeline_rules import normalize_text


class RecommendationEngine:
    """
    First deterministic routing layer.

    This is intentionally simple. It gives the pipeline a traceable decision
    point that can later be replaced or extended by richer rules.
    """

    def recommend(self, case: MedicalCase) -> Recommendation:
        text = self._case_text(case)
        tags: list[str] = []

        if self._contains(text, ["blood_pressure", "blutdruck", "185", "180"]):
            tags.append("blood_pressure_signal")
            return Recommendation(
                care_level="general_practice",
                urgency_level="medium",
                specialty="general_practice",
                urgency="soon",
                confidence=0.5,
                reasoning_tags=tags,
                explanation="Blood pressure related concern detected.",
            )

        if self._contains(text, ["concern", "graue_haare", "falten", "haarausfall"]):
            tags.append("low_acuity_concern")
            return Recommendation(
                care_level="self_care",
                urgency_level="low",
                specialty="general_practice",
                urgency="self_observation",
                confidence=0.45,
                reasoning_tags=tags,
                explanation="Low-acuity health concern detected.",
            )

        if self._contains(text, ["knie", "hufte", "gelenk", "sturz", "verletz", "prell"]):
            tags.append("musculoskeletal_signal")
            return Recommendation(
                care_level="general_practice",
                urgency_level="medium",
                specialty="orthopedics",
                urgency="soon",
                confidence=0.55,
                reasoning_tags=tags,
                explanation="Musculoskeletal complaint detected.",
            )

        if self._contains(text, ["haut", "ausschlag", "juck", "fleck"]):
            tags.append("skin_signal")
            return Recommendation(
                care_level="general_practice",
                urgency_level="low",
                specialty="dermatology",
                urgency="routine",
                confidence=0.55,
                reasoning_tags=tags,
                explanation="Skin-related complaint detected.",
            )

        if self._contains(text, ["kopf", "schwindel", "migraene"]):
            tags.append("head_or_neuro_signal")
            return Recommendation(
                care_level="general_practice",
                urgency_level="medium",
                specialty="general_practice",
                urgency="soon",
                confidence=0.5,
                reasoning_tags=tags,
                explanation="Head-related complaint detected.",
            )

        tags.append("default_primary_care")
        return Recommendation(
            care_level="general_practice",
            urgency_level="unclear",
            specialty="general_practice",
            urgency="routine",
            confidence=0.4,
            reasoning_tags=tags,
            explanation="No specific specialty signal detected.",
        )

    @staticmethod
    def _case_text(case: MedicalCase) -> str:
        parts = []
        for observation in case.observations:
            parts.append(observation.searchable_text)
        return normalize_text(" ".join(parts))

    @staticmethod
    def _contains(text: str, markers: list[str]) -> bool:
        return any(marker in text for marker in markers)
