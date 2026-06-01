from careena_pipeline.models import MedicalCase, Recommendation


def normalize_confidence(value: float | None) -> float:
    if value is None or value <= 0.0:
        return 0.5
    return max(0.0, min(value, 1.0))


def apply_case_based_routing_safety(
    case: MedicalCase,
    recommendation: Recommendation,
) -> Recommendation:
    case.ensure_primary_problem()
    if _has_severe_lower_body_injury_with_limited_weight_bearing(case):
        recommendation.care_level = "emergency_department"
        recommendation.urgency_level = "high"
        recommendation.specialty = "emergency_medicine"
        recommendation.urgency = "today"
        recommendation.confidence = max(recommendation.confidence, 0.65)
        _append_tag(recommendation, "severe_lower_body_injury_limited_weight_bearing")
        return recommendation

    if _has_severe_injury(case):
        recommendation.care_level = _at_least_care_level(
            recommendation.care_level,
            minimum="116117",
        )
        recommendation.urgency_level = _at_least_urgency_level(
            recommendation.urgency_level,
            minimum="high",
        )
        recommendation.urgency = _at_least_urgency(
            recommendation.urgency,
            minimum="today",
        )
        recommendation.confidence = max(recommendation.confidence, 0.6)
        _append_tag(recommendation, "severe_injury")

    return recommendation


def _has_severe_lower_body_injury_with_limited_weight_bearing(case: MedicalCase) -> bool:
    if not _has_severe_lower_body_complaint(case):
        return False

    lower_body_text = _case_text(case)
    lower_body_markers = [
        "huefte",
        "hüfte",
        "bein",
        "knie",
        "fuss",
        "fuß",
        "sprunggelenk",
    ]
    if not any(marker in lower_body_text for marker in lower_body_markers):
        return False

    limitation = _first_detail(case, "functional_limitation")
    if not limitation:
        return False

    limitation_text = limitation.lower()
    limitation_markers = [
        "kaum",
        "nicht",
        "schlecht",
        "unmoeglich",
        "unmöglich",
        "nicht auftreten",
        "nicht belasten",
    ]
    return any(marker in limitation_text for marker in limitation_markers)


def _has_severe_injury(case: MedicalCase) -> bool:
    return any(
        observation.type == "injury" for observation in case.observations
    ) and _has_severe_complaint(case)


def _has_severe_lower_body_complaint(case: MedicalCase) -> bool:
    return _has_severe_complaint(case) and _has_lower_body_complaint(case)


def _has_severe_complaint(case: MedicalCase) -> bool:
    return any(
        observation.severity is not None and observation.severity >= 8
        for observation in case.observations_of_type("symptom", "injury")
    )


def _has_lower_body_complaint(case: MedicalCase) -> bool:
    lower_body_text = _case_text(case)
    return any(
        marker in lower_body_text
        for marker in [
            "huefte",
            "hüfte",
            "hip",
            "bein",
            "knie",
            "fuss",
            "fuß",
            "sprunggelenk",
        ]
    )


def _case_text(case: MedicalCase) -> str:
    parts = []
    for observation in case.observations:
        parts.append(observation.searchable_text)
    return " ".join(parts).lower()


def _first_detail(case: MedicalCase, key: str) -> str | None:
    for observation in case.observations_of_type("symptom", "injury"):
        value = observation.details.get(key)
        if value:
            return value
    return None


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
    return _at_least(value, minimum, order)


def _at_least_urgency_level(value: str, *, minimum: str) -> str:
    order = ["low", "medium", "high", "emergency"]
    return _at_least(value, minimum, order)


def _at_least_urgency(value: str, *, minimum: str) -> str:
    order = ["self_observation", "routine", "soon", "today", "emergency"]
    return _at_least(value, minimum, order)


def _at_least(value: str, minimum: str, order: list[str]) -> str:
    if value not in order:
        return minimum
    if order.index(value) < order.index(minimum):
        return minimum
    return value


def _append_tag(recommendation: Recommendation, tag: str) -> None:
    if tag not in recommendation.reasoning_tags:
        recommendation.reasoning_tags.append(tag)
