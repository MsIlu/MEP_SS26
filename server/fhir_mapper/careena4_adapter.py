from __future__ import annotations

from typing import Any

from fhir_mapper.mapper import map_to_fhir_bundle


def build_fhir_bundle_from_careena4_session(careena4_session: Any) -> dict[str, Any]:
    """
    Builds a FHIR Bundle from the extracted Careena4 backend session data.

    The adapter intentionally keeps Careena4-specific model handling separate
    from the generic FHIR mapper.
    """

    medical_case = getattr(careena4_session, "medical_case", None)
    recommendation_state = getattr(careena4_session, "recommendation_state", None)
    recommendation_result = getattr(
        recommendation_state,
        "recommendation_result",
        None,
    )

    observations = _map_medical_case_observations(medical_case)
    recommendation = _map_recommendation_result(recommendation_result)
    raw_text = _build_raw_text_from_messages(
        getattr(careena4_session, "messages", []),
    )

    patient_id = (
        getattr(medical_case, "case_id", None)
        or getattr(careena4_session, "session_id", None)
        or "careena-session"
    )

    return map_to_fhir_bundle(
        {
            "patient": {
                "id": patient_id,
            },
            "input": {
                "rawText": raw_text,
            },
            "observations": observations,
            "recommendation": recommendation,
        }
    )


def _map_medical_case_observations(medical_case: Any) -> list[dict[str, Any]]:
    if medical_case is None:
        return []

    if hasattr(medical_case, "active_observations"):
        observations = medical_case.active_observations()
    else:
        observations = getattr(medical_case, "observations", [])

    return [
        _map_observation(observation)
        for observation in observations
    ]


def _map_observation(observation: Any) -> dict[str, Any]:
    attributes = getattr(observation, "attributes", {}) or {}

    return {
        "id": getattr(observation, "observation_id", None),
        "label": getattr(observation, "label", "Unbekannte Angabe"),
        "type": getattr(observation, "type", "unknown"),
        "source_span": _build_source_span(observation),
        "context": {
            "negated": getattr(observation, "negated", False),
            "certainty": getattr(observation, "status", "unknown"),
            "status": getattr(observation, "status", "unknown"),
            "topic_relation": getattr(observation, "topic_relation", "unclear"),
            "subject_ref": getattr(observation, "subject_ref", "unclear"),
            "attributes": attributes,
        },
    }


def _map_recommendation_result(recommendation_result: Any) -> dict[str, Any]:
    if recommendation_result is None:
        return {}

    next_step = getattr(recommendation_result, "next_step", None)
    summary = getattr(recommendation_result, "summary", None)

    return {
        "urgency": getattr(recommendation_result, "urgency_level", "unclear"),
        "text": next_step or summary or "Keine konkrete Handlungsempfehlung vorhanden.",
        "summary": summary,
        "care_level": getattr(recommendation_result, "care_level", "unknown"),
        "specialty": getattr(recommendation_result, "specialty", "unknown"),
        "reasons": list(getattr(recommendation_result, "reasons", []) or []),
        "limitations": list(getattr(recommendation_result, "limitations", []) or []),
    }


def _build_raw_text_from_messages(messages: list[dict[str, str]]) -> str:
    user_messages = [
        message.get("content", "")
        for message in messages
        if message.get("role") == "user" and message.get("content")
    ]

    return "\n".join(user_messages)


def _build_source_span(observation: Any) -> str:
    provenance = getattr(observation, "provenance", []) or []

    if not provenance:
        return ""

    return "; ".join(str(item) for item in provenance)