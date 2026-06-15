from careena_pipeline2.models import MedicalCase, Recommendation
from careena_pipeline2.text import normalize_text


class RecommendationRouter:
    def recommend(self, case: MedicalCase) -> Recommendation:
        case.ensure_primary_problem(source="confirmed")
        text = self._case_text(case)
        tags: list[str] = []

        if self._blood_pressure_signal(case, text):
            tags.append("blood_pressure_signal")
            recommendation = Recommendation(
                care_level="general_practice",
                urgency_level="medium",
                specialty="general_practice",
                urgency="soon",
                confidence=0.55,
                reasoning_tags=tags,
                explanation="Blood pressure related concern detected.",
            )
            recommendation.reasons = self._build_reasons(case, recommendation)
            return recommendation

        if self._contains(text, ["concern", "graue haare", "falten", "haarausfall"]):
            tags.append("low_acuity_concern")
            recommendation = Recommendation(
                care_level="self_care",
                urgency_level="low",
                specialty="general_practice",
                urgency="self_observation",
                confidence=0.45,
                reasoning_tags=tags,
                explanation="Low-acuity health concern detected.",
            )
            recommendation.reasons = self._build_reasons(case, recommendation)
            return recommendation

        if self._contains(text, ["knie", "hufte", "huefte", "gelenk", "sturz", "verletz", "prell"]):
            tags.append("musculoskeletal_signal")
            recommendation = Recommendation(
                care_level="general_practice",
                urgency_level="medium",
                specialty="orthopedics",
                urgency="soon",
                confidence=0.55,
                reasoning_tags=tags,
                explanation="Musculoskeletal complaint detected.",
            )
            recommendation = self._apply_case_safety_overrides(case, recommendation)
            recommendation.reasons = self._build_reasons(case, recommendation)
            return recommendation

        if self._contains(text, ["haut", "ausschlag", "juck", "fleck"]):
            tags.append("skin_signal")
            recommendation = Recommendation(
                care_level="general_practice",
                urgency_level="low",
                specialty="dermatology",
                urgency="routine",
                confidence=0.55,
                reasoning_tags=tags,
                explanation="Skin-related complaint detected.",
            )
            recommendation.reasons = self._build_reasons(case, recommendation)
            return recommendation

        if self._contains(text, ["kopf", "schwindel", "migraene", "migrane"]):
            tags.append("head_or_neuro_signal")
            recommendation = Recommendation(
                care_level="general_practice",
                urgency_level="medium",
                specialty="general_practice",
                urgency="soon",
                confidence=0.5,
                reasoning_tags=tags,
                explanation="Head-related complaint detected.",
            )
            recommendation.reasons = self._build_reasons(case, recommendation)
            return recommendation

        tags.append("default_primary_care")
        recommendation = Recommendation(
            care_level="general_practice",
            urgency_level="unclear",
            specialty="general_practice",
            urgency="routine",
            confidence=0.4,
            reasoning_tags=tags,
            explanation="No specific specialty signal detected.",
        )
        recommendation = self._apply_case_safety_overrides(case, recommendation)
        recommendation.reasons = self._build_reasons(case, recommendation)
        return recommendation

    def _apply_case_safety_overrides(
        self,
        case: MedicalCase,
        recommendation: Recommendation,
    ) -> Recommendation:
        if self._has_severe_lower_body_injury_with_limited_weight_bearing(case):
            recommendation.care_level = "emergency_department"
            recommendation.urgency_level = "high"
            recommendation.specialty = "emergency_medicine"
            recommendation.urgency = "today"
            recommendation.confidence = max(recommendation.confidence, 0.65)
            if "severe_lower_body_injury_limited_weight_bearing" not in recommendation.reasoning_tags:
                recommendation.reasoning_tags.append(
                    "severe_lower_body_injury_limited_weight_bearing"
                )
            return recommendation

        if self._has_severe_injury(case):
            recommendation.care_level = self._at_least_care_level(
                recommendation.care_level,
                minimum="116117",
            )
            recommendation.urgency_level = self._at_least_urgency_level(
                recommendation.urgency_level,
                minimum="high",
            )
            recommendation.urgency = self._at_least_urgency(
                recommendation.urgency,
                minimum="today",
            )
            recommendation.confidence = max(recommendation.confidence, 0.6)
            if "severe_injury" not in recommendation.reasoning_tags:
                recommendation.reasoning_tags.append("severe_injury")
        return recommendation

    def _has_severe_lower_body_injury_with_limited_weight_bearing(self, case: MedicalCase) -> bool:
        if not self._has_severe_lower_body_complaint(case):
            return False
        limitation = self._first_detail(case, "functional_limitation")
        if not limitation:
            return False
        limitation_text = normalize_text(limitation)
        return any(
            marker in limitation_text
            for marker in (
                "kaum",
                "nicht",
                "schlecht",
                "unmoeglich",
                "unmoglich",
                "nicht auftreten",
                "nicht belasten",
            )
        )

    def _has_severe_injury(self, case: MedicalCase) -> bool:
        return any(
            observation.type == "injury"
            for observation in case.active_observations(source="confirmed")
        ) and self._has_severe_complaint(case)

    def _has_severe_lower_body_complaint(self, case: MedicalCase) -> bool:
        return self._has_severe_complaint(case) and self._has_lower_body_complaint(case)

    def _has_severe_complaint(self, case: MedicalCase) -> bool:
        return any(
            (severity := observation.runtime_value("severity")) is not None and severity >= 8
            for observation in case.observations_of_type(
                "symptom",
                "injury",
                source="confirmed",
            )
        )

    def _has_lower_body_complaint(self, case: MedicalCase) -> bool:
        text = self._case_text(case)
        return any(
            marker in text
            for marker in ("hufte", "huefte", "hip", "bein", "knie", "fuss", "sprunggelenk")
        )

    def _blood_pressure_signal(self, case: MedicalCase, text: str) -> bool:
        if self._contains(text, ["blood_pressure", "blutdruck", "185", "180"]):
            return True
        for observation in case.observations_of_type("measurement", source="confirmed", include_negated=True):
            if observation.runtime_measurement_value("kind") == "blood_pressure":
                return True
        return False

    def _case_text(self, case: MedicalCase) -> str:
        parts = [observation.searchable_text for observation in case.active_observations(source="confirmed")]
        return normalize_text(" ".join(parts))

    @staticmethod
    def _contains(text: str, markers: list[str]) -> bool:
        return any(marker in text for marker in markers)

    @staticmethod
    def _first_detail(case: MedicalCase, key: str) -> str | None:
        for observation in case.observations_of_type("symptom", "injury", source="confirmed"):
            value = observation.runtime_detail_value(key)
            if value:
                return value
        return None

    @staticmethod
    def _at_least_care_level(value: str, *, minimum: str) -> str:
        order = [
            "self_care",
            "pharmacy",
            "general_practice",
            "specialist",
            "116117",
            "emergency_department",
            "112",
        ]
        return RecommendationRouter._at_least(value, minimum, order)

    @staticmethod
    def _at_least_urgency_level(value: str, *, minimum: str) -> str:
        order = ["low", "medium", "high", "emergency"]
        return RecommendationRouter._at_least(value, minimum, order)

    @staticmethod
    def _at_least_urgency(value: str, *, minimum: str) -> str:
        order = ["self_observation", "routine", "soon", "today", "emergency"]
        return RecommendationRouter._at_least(value, minimum, order)

    @staticmethod
    def _at_least(value: str, minimum: str, order: list[str]) -> str:
        if value not in order:
            return minimum
        if order.index(value) < order.index(minimum):
            return minimum
        return value

    def _build_reasons(self, case: MedicalCase, recommendation: Recommendation) -> list[str]:
        reasons: list[str] = []
        focus = case.primary_focus_label(source="confirmed")
        if focus:
            reasons.append(f"Im Vordergrund steht die geschilderte Beschwerde: {focus}.")

        if case.subject.age is not None:
            reasons.append(f"Die betroffene Person ist {case.subject.age} Jahre alt.")

        temporality = self._first_value(case, "temporality")
        if temporality:
            reasons.append(f"Die Beschwerden bestehen laut Angabe: {temporality.strip().rstrip('.!?')}.")

        context = self._first_detail(case, "context")
        if context:
            reasons.append(f"Zum Hergang wurde angegeben: {context.strip().rstrip('.!?')}.")

        severity = self._first_value(case, "severity")
        if severity is not None:
            reasons.append(f"Die Staerke wurde mit {severity} von 10 angegeben.")

        functional_limitation = self._first_detail(case, "functional_limitation")
        if functional_limitation:
            reasons.append(
                "Zur Belastbarkeit wurde angegeben: "
                f"{functional_limitation.strip().rstrip('.!?')}."
            )

        care_level = recommendation.care_level
        if care_level == "general_practice":
            reasons.append(
                "Eine hausaerztliche Ersteinschaetzung ist dafuer ein vorsichtiger naechster Schritt."
            )
        elif care_level == "specialist":
            reasons.append("Eine fachaerztliche Abklaerung passt zur geschilderten Beschwerde.")
        elif care_level == "116117":
            reasons.append(
                "Der aerztliche Bereitschaftsdienst ist passend, wenn zeitnah Hilfe benoetigt wird und kein Notfallzeichen vorliegt."
            )
        elif care_level == "emergency_department":
            reasons.append("Wegen moeglicher Dringlichkeit sollte eine Notaufnahme erwogen werden.")
        elif care_level == "112":
            reasons.append("Wegen moeglicher Notfallzeichen sollte der Notruf gewaehlt werden.")

        return self._dedupe(reasons)

    @staticmethod
    def _first_value(case: MedicalCase, attribute: str):
        for observation in case.active_observations(source="confirmed", include_negated=True):
            value = observation.runtime_value(attribute)
            if value is not None:
                return value
        return None

    @staticmethod
    def _dedupe(values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            normalized = " ".join(value.lower().split())
            if normalized in seen:
                continue
            seen.add(normalized)
            result.append(value)
        return result
