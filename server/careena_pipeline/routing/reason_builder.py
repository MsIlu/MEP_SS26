from typing import Any

from careena_pipeline.models import MedicalCase


def build_reasons(case: MedicalCase, recommendation: Any) -> list[str]:
    case.ensure_primary_problem()
    reasons: list[str] = []
    focus = _focus_label(case)
    if focus:
        reasons.append(f"Im Vordergrund steht die geschilderte Beschwerde: {focus}.")

    measurement_reason = _measurement_reason(case)
    if measurement_reason:
        reasons.append(measurement_reason)

    if case.subject.age is not None:
        reasons.append(f"Die betroffene Person ist {case.subject.age} Jahre alt.")

    temporality = _first_value(
        case,
        "temporality",
        preferred_types=("symptom", "injury", "measurement", "concern"),
    )
    if temporality:
        reasons.append(
            f"Die Beschwerden bestehen laut Angabe: {_clean_sentence_value(temporality)}."
        )

    context = _first_detail(
        case,
        "context",
        preferred_types=("injury", "symptom", "measurement", "concern"),
    )
    if context:
        reasons.append(f"Zum Hergang wurde angegeben: {_clean_sentence_value(context)}.")

    severity = _first_value(
        case,
        "severity",
        preferred_types=("symptom", "injury", "measurement", "concern"),
    )
    if severity is not None:
        reasons.append(f"Die Schmerzstärke wurde mit {severity} von 10 angegeben.")

    functional_limitation = _first_detail(
        case,
        "functional_limitation",
        preferred_types=("injury", "symptom", "measurement", "concern"),
    )
    if functional_limitation:
        reasons.append(
            "Zur Belastbarkeit wurde angegeben: "
            f"{_clean_sentence_value(functional_limitation)}."
        )

    care_level = getattr(recommendation, "care_level", None)
    if care_level == "general_practice":
        reasons.append(
            "Eine hausärztliche Ersteinschätzung ist dafür ein vorsichtiger nächster Schritt."
        )
    elif care_level == "specialist":
        reasons.append("Eine fachärztliche Abklärung passt zur geschilderten Beschwerde.")
    elif care_level == "116117":
        reasons.append(
            "Der ärztliche Bereitschaftsdienst ist passend, wenn zeitnah Hilfe benötigt "
            "wird und kein Notfallzeichen vorliegt."
        )
    elif care_level == "emergency_department":
        reasons.append("Wegen möglicher Dringlichkeit sollte eine Notaufnahme erwogen werden.")
    elif care_level == "112":
        reasons.append("Wegen möglicher Notfallzeichen sollte der Notruf gewählt werden.")

    return _dedupe(reasons)


def _first_value(
    case: MedicalCase,
    attribute: str,
    *,
    preferred_types: tuple[str, ...] | None = None,
):
    for observation in _ordered_routing_observations(
        case,
        preferred_types=preferred_types,
    ):
        value = getattr(observation, attribute, None)
        if value is not None:
            return value
    return None


def _first_detail(
    case: MedicalCase,
    key: str,
    *,
    preferred_types: tuple[str, ...] | None = None,
) -> str | None:
    for observation in _ordered_routing_observations(
        case,
        preferred_types=preferred_types,
    ):
        value = observation.details.get(key)
        if value:
            return value
    return None


def _routing_observations(case: MedicalCase):
    return case.observations_of_type(
        "symptom",
        "injury",
        "measurement",
        "concern",
        include_negated=True,
    )


def _ordered_routing_observations(
    case: MedicalCase,
    *,
    preferred_types: tuple[str, ...] | None = None,
):
    observations = _routing_observations(case)
    if not preferred_types:
        return observations

    type_rank = {value: index for index, value in enumerate(preferred_types)}
    return sorted(
        observations,
        key=lambda observation: type_rank.get(observation.type, len(type_rank)),
    )


def _focus_label(case: MedicalCase) -> str | None:
    return case.primary_focus_label()


def _measurement_reason(case: MedicalCase) -> str | None:
    for observation in _routing_observations(case):
        if observation.type != "measurement" or not observation.measurement:
            continue

        kind = observation.measurement.get("kind") or observation.concept
        if kind == "blood_pressure":
            systolic = observation.measurement.get("systolic")
            diastolic = observation.measurement.get("diastolic")
            if systolic and diastolic:
                return f"Als Blutdruckmesswert wurde {systolic}/{diastolic} angegeben."
        if kind == "temperature":
            value = observation.measurement.get("value")
            unit = observation.measurement.get("unit", "Grad")
            if value:
                return f"Als Temperatur wurde {value} {unit} angegeben."

        return f"Genannt wurde: {observation.patient_label}."

    return None


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


def _clean_sentence_value(value: str) -> str:
    return value.strip().rstrip(".!?")
