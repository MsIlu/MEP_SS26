from types import SimpleNamespace

from sqlmodel import select

from appointments.service import (
    AppointmentProviderUnavailable,
    search_fhir_appointments,
)
from database.models import RecommendedAppointment
from fhir_mapper.hapi_client import HapiFhirError


def register_user(client, email="appointments@example.com"):
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "12345678",
            "display_name": "Anna",
            "date_of_birth": "2000-04-12",
            "biological_sex": "female",
        },
    )

    assert response.status_code == 200

    data = response.json()

    return {
        "profile_id": data["profiles"][0]["id"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
    }


class FakeHapiClient:
    def __init__(self):
        self.submitted_bundle = None
        self.ensure_calls = []

    def submit_bundle(self, bundle):
        self.submitted_bundle = bundle
        return "bundle-1"

    def ensure_recommendation_appointments(self, **kwargs):
        self.ensure_calls.append(kwargs)
        return [
            {
                "resourceType": "Appointment",
                "id": "hapi-appointment-1",
                "identifier": [
                    {
                        "system": "https://careena.local/fhir/appointments",
                        "value": "hapi-appointment-1",
                    }
                ],
                "status": "proposed",
                "start": "2026-07-02T09:30:00+00:00",
                "end": "2026-07-02T10:00:00+00:00",
                "specialty": [{"text": "Allgemeinmedizin"}],
                "serviceType": [{"text": "Vor-Ort-Termin"}],
                "participant": [
                    {
                        "actor": {"display": "Hausarztpraxis Dr. Schneider"},
                        "status": "needs-action",
                    }
                ],
                "extension": [
                    {
                        "url": "https://careena.local/fhir/StructureDefinition/careena-appointment-address",
                        "valueString": "Musterstrasse 12, 68159 Mannheim",
                    },
                    {
                        "url": "https://careena.local/fhir/StructureDefinition/careena-distance-km",
                        "valueDecimal": 2.4,
                    },
                    {
                        "url": "https://careena.local/fhir/StructureDefinition/careena-urgency-match",
                        "valueBoolean": True,
                    },
                    {
                        "url": "https://careena.local/fhir/StructureDefinition/careena-care-type",
                        "valueString": "Vor-Ort-Termin",
                    },
                ],
            }
        ]


class FailingHapiClient:
    def submit_bundle(self, bundle):
        raise HapiFhirError("HAPI down")


def test_search_fhir_appointments_submits_bundle_and_reads_hapi_resources():
    hapi_client = FakeHapiClient()

    response = search_fhir_appointments(
        session_id="session-1",
        profile_id=10,
        postal_code="68159",
        recommendation_result=SimpleNamespace(
            urgency_level="medium",
            care_level="general_practice",
            specialty="general_practice",
            next_step="Bitte hausarztlich abklaren lassen.",
        ),
        fhir_bundle={"resourceType": "Bundle", "type": "collection", "entry": []},
        fhir_client=hapi_client,
    )

    assert hapi_client.submitted_bundle["resourceType"] == "Bundle"
    assert hapi_client.ensure_calls[0]["bundle_id"] == "bundle-1"
    assert response.message.startswith("HAPI-FHIR")
    assert response.appointments[0].id == "hapi-appointment-1"
    assert response.appointments[0].provider_name == "Hausarztpraxis Dr. Schneider"
    assert response.appointments[0].source == "hapi-fhir"


def test_search_fhir_appointments_reports_provider_unavailable():
    try:
        search_fhir_appointments(
            session_id="session-1",
            profile_id=10,
            postal_code="68159",
            recommendation_result=SimpleNamespace(
                urgency_level="medium",
                care_level="general_practice",
                specialty="general_practice",
            ),
            fhir_bundle={"resourceType": "Bundle", "type": "collection"},
            fhir_client=FailingHapiClient(),
        )
    except AppointmentProviderUnavailable as exc:
        assert "HAPI down" in str(exc)
    else:
        raise AssertionError("Expected AppointmentProviderUnavailable")


def test_save_recommended_appointment_persists_profile_scoped_entry(client, db_session):
    auth = register_user(client)

    response = client.post(
        f"/profiles/{auth['profile_id']}/appointments/recommended",
        headers=auth["headers"],
        json={
            "session_id": "session-1",
            "fhir_appointment_id": "hapi-appointment-1",
            "provider_name": "Hausarztpraxis Dr. Schneider",
            "specialty": "Allgemeinmedizin",
            "address": "Musterstrasse 12, 68159 Mannheim",
            "distance_km": 2.4,
            "date": "2026-07-02",
            "time": "09:30",
            "care_type": "Vor-Ort-Termin",
            "note": "Von Careena empfohlen",
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["profile_id"] == auth["profile_id"]
    assert payload["fhir_appointment_id"] == "hapi-appointment-1"
    assert payload["provider_name"] == "Hausarztpraxis Dr. Schneider"

    entries = db_session.exec(select(RecommendedAppointment)).all()
    assert len(entries) == 1
    assert entries[0].profile_id == auth["profile_id"]
    assert entries[0].fhir_appointment_id == "hapi-appointment-1"


def test_save_recommended_appointment_is_idempotent_for_same_fhir_id(
        client,
        db_session,
):
    auth = register_user(client)
    payload = {
        "session_id": "session-1",
        "fhir_appointment_id": "hapi-appointment-1",
        "provider_name": "Hausarztpraxis Dr. Schneider",
        "specialty": "Allgemeinmedizin",
        "address": "Musterstrasse 12, 68159 Mannheim",
        "distance_km": 2.4,
        "date": "2026-07-02",
        "time": "09:30",
        "care_type": "Vor-Ort-Termin",
    }

    first = client.post(
        f"/profiles/{auth['profile_id']}/appointments/recommended",
        headers=auth["headers"],
        json=payload,
    )
    second = client.post(
        f"/profiles/{auth['profile_id']}/appointments/recommended",
        headers=auth["headers"],
        json=payload,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]

    entries = db_session.exec(select(RecommendedAppointment)).all()
    assert len(entries) == 1


def test_recommended_appointments_require_profile_access(client):
    first_user = register_user(client, email="first-appointments@example.com")
    second_user = register_user(client, email="second-appointments@example.com")

    response = client.get(
        f"/profiles/{first_user['profile_id']}/appointments/recommended",
        headers=second_user["headers"],
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this profile."
