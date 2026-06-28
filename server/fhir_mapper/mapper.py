from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import NAMESPACE_URL, uuid5


URGENCY_EXTENSION_URL = (
    "https://careena.local/fhir/StructureDefinition/urgency-level"
)


def map_to_fhir_bundle(data: dict[str, Any]) -> dict[str, Any]:
    """
    Maps internal Careena test/analysis data to a minimal FHIR Bundle.

     generated resources:
    - Patient
    - QuestionnaireResponse
    - Observation
    - ServiceRequest
    - Bundle

    The mapper intentionally does not create Condition resources automatically,
    because the application generates more like a recommendation, not diagnosis.
    """

    patient_data = data.get("patient", {})
    raw_text = data.get("input", {}).get("rawText", "")
    observations = _extract_observations(data)
    recommendation = data.get("recommendation", {})

    patient_id = str(patient_data.get("id", "test-patient"))
    patient_full_url = _urn("Patient", patient_id)

    patient = _map_patient(patient_data, patient_id)
    questionnaire_response = _map_questionnaire_response(
        raw_text=raw_text,
        patient_reference=patient_full_url,
    )
    fhir_observations = [
        _map_observation(event, patient_full_url)
        for event in observations
    ]
    service_request = _map_service_request(
        recommendation=recommendation,
        patient_reference=patient_full_url,
    )

    entries = [
        _bundle_entry(patient_full_url, patient),
        _bundle_entry(
            _urn("QuestionnaireResponse", "raw-user-input"),
            questionnaire_response,
        ),
    ]

    for observation in fhir_observations:
        entries.append(
            _bundle_entry(
                _urn("Observation", observation["id"]),
                observation,
            )
        )

    entries.append(
        _bundle_entry(
            _urn("ServiceRequest", "recommendation"),
            service_request,
        )
    )

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "entry": entries,
    }


def map_pipeline_result_to_fhir_bundle(
    raw_text: str,
    pipeline_result: Any,
    patient: dict[str, Any] | None = None,
    recommendation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Convenience wrapper for the existing extraction pipeline.

    Accepts either a Pydantic model with model_dump() or a plain dict.
    """

    if hasattr(pipeline_result, "model_dump"):
        analysis = pipeline_result.model_dump()
    elif isinstance(pipeline_result, dict):
        analysis = pipeline_result
    else:
        raise TypeError("pipeline_result must be a dict or provide model_dump().")

    return map_to_fhir_bundle(
        {
            "patient": patient or {"id": "test-patient"},
            "input": {"rawText": raw_text},
            "analysis": analysis,
            "recommendation": recommendation or {},
        }
    )


def _map_patient(patient_data: dict[str, Any], patient_id: str) -> dict[str, Any]:
    patient = {
        "resourceType": "Patient",
        "id": _stable_id("Patient", patient_id),
    }

    gender = patient_data.get("gender")
    if gender in {"male", "female", "other", "unknown"}:
        patient["gender"] = gender

    birth_date = patient_data.get("birthDate")
    if birth_date:
        patient["birthDate"] = birth_date

    return patient


def _map_questionnaire_response(
    raw_text: str,
    patient_reference: str,
) -> dict[str, Any]:
    return {
        "resourceType": "QuestionnaireResponse",
        "id": _stable_id("QuestionnaireResponse", "raw-user-input"),
        "status": "completed",
        "questionnaire": "https://careena.local/fhir/Questionnaire/raw-user-input",
        "subject": {
            "reference": patient_reference,
        },
        "item": [
            {
                "linkId": "raw-user-input",
                "text": "Urspruengliche Nutzereingabe",
                "answer": [
                    {
                        "valueString": raw_text,
                    }
                ],
            }
        ],
    }


def _map_observation(
    event: dict[str, Any],
    patient_reference: str,
) -> dict[str, Any]:
    label = str(event.get("label") or "Unbekannte Angabe")
    event_id = str(event.get("id") or _stable_id("Observation", label))
    context = event.get("context", {}) or {}

    note_parts = [
        f"Quelle: {event.get('source_span', '')}",
        f"Interner Typ: {event.get('type', 'unknown')}",
        f"Negiert: {context.get('negated', False)}",
        f"Sicherheit: {context.get('certainty', 'unknown')}",
    ]
    status = context.get("status")
    if status:
        note_parts.append(f"Careena-Status: {status}")

    topic_relation = context.get("topic_relation")
    if topic_relation:
        note_parts.append(f"Themenbezug: {topic_relation}")

    subject_ref = context.get("subject_ref")
    if subject_ref:
        note_parts.append(f"Betroffene Person: {subject_ref}")

    attributes = context.get("attributes")
    if attributes:
        note_parts.append(f"Attribute: {attributes}")

    temporality = context.get("temporality")
    if temporality:
        note_parts.append(f"Zeitlicher Kontext: {temporality}")

    return {
        "resourceType": "Observation",
        "id": event_id,
        "status": "final",
        "subject": {
            "reference": patient_reference,
        },
        "code": {
            "text": label,
        },
        "valueString": label,
        "note": [
            {
                "text": "; ".join(note_parts),
            }
        ],
    }


def _map_service_request(
    recommendation: dict[str, Any],
    patient_reference: str,
) -> dict[str, Any]:
    urgency = recommendation.get("urgency", "unknown")
    recommendation_text = recommendation.get(
        "text",
        "Keine konkrete Handlungsempfehlung vorhanden.",
    )

    return {
        "resourceType": "ServiceRequest",
        "id": _stable_id("ServiceRequest", "recommendation"),
        "status": "draft",
        "intent": "proposal",
        "subject": {
            "reference": patient_reference,
        },
        "code": {
            "concept": {
                "text": "Empfohlener naechster Schritt",
    }
},
        "extension": [
            {
                "url": URGENCY_EXTENSION_URL,
                "valueCode": urgency,
            }
        ],
        "note": [
            {
                "text": recommendation_text,
            }
        ],
    }


def _extract_observations(data: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(data.get("observations"), list):
        return data["observations"]

    analysis = data.get("analysis", {})
    observations = analysis.get("observations")

    if isinstance(observations, dict):
        events = observations.get("events", [])
        return events if isinstance(events, list) else []

    if isinstance(observations, list):
        return observations

    return []


def _bundle_entry(full_url: str, resource: dict[str, Any]) -> dict[str, Any]:
    return {
        "fullUrl": full_url,
        "resource": resource,
    }


def _urn(resource_type: str, value: str) -> str:
    return f"urn:uuid:{_stable_id(resource_type, value)}"


def _stable_id(prefix: str, value: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"careena:{prefix}:{value}"))