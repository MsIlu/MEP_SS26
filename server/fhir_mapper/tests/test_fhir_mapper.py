from types import SimpleNamespace

import httpx

from fhir_mapper.mapper import map_to_fhir_bundle
from fhir_mapper.validator import validate_fhir_bundle
from careena4.models.domain import MedicalCase
from careena4.models.domain.observation import Observation
from careena4.models.domain.recommendation import RecommendationState
from careena4.models.workflow.recommendation_result import RecommendationResult
from fhir_mapper.careena4_adapter import build_fhir_bundle_from_careena4_session
from fhir_mapper.hapi_client import (
    BOOKED_BY_ACCOUNT_EXTENSION_URL,
    HapiFhirClient,
    POSTAL_CODE_EXTENSION_URL,
    PROFILE_EXTENSION_URL,
    SESSION_EXTENSION_URL,
    _parse_datetime,
    build_recommendation_appointment_resources,
)


def test_parse_datetime_treats_missing_offset_as_utc():
    parsed = _parse_datetime("2026-07-10T08:30:00")

    assert parsed is not None
    assert parsed.utcoffset().total_seconds() == 0


def _sample_internal_data():
    return {
        "patient": {
            "id": "test-patient-1",
            "birthDate": "1998-05-12",
            "gender": "male",
        },
        "input": {
            "rawText": "Ich habe seit gestern Kopfschmerzen und Halsschmerzen.",
        },
        "analysis": {
            "observations": {
                "events": [
                    {
                        "id": "obs-1",
                        "type": "symptom",
                        "label": "Kopfschmerzen",
                        "source_span": "Kopfschmerzen",
                        "context": {
                            "negated": False,
                            "certainty": "confirmed",
                            "temporality": "seit gestern",
                        },
                    },
                    {
                        "id": "obs-2",
                        "type": "symptom",
                        "label": "Halsschmerzen",
                        "source_span": "Halsschmerzen",
                        "context": {
                            "negated": False,
                            "certainty": "confirmed",
                            "temporality": None,
                        },
                    },
                ]
            }
        },
        "recommendation": {
            "urgency": "non_urgent",
            "text": "Selbstbeobachtung. Bei Verschlechterung ärztliche Hilfe suchen.",
        },
    }


def test_map_to_fhir_bundle_creates_expected_resources():
    bundle = map_to_fhir_bundle(_sample_internal_data())

    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "collection"

    resources = [entry["resource"] for entry in bundle["entry"]]
    resource_types = [resource["resourceType"] for resource in resources]

    assert "Patient" in resource_types
    assert "QuestionnaireResponse" in resource_types
    assert "Observation" in resource_types
    assert "ServiceRequest" in resource_types

    observations = [
        resource
        for resource in resources
        if resource["resourceType"] == "Observation"
    ]

    assert len(observations) == 2
    assert observations[0]["code"]["text"] == "Kopfschmerzen"
    assert observations[1]["code"]["text"] == "Halsschmerzen"


def test_service_request_contains_urgency_extension():
    bundle = map_to_fhir_bundle(_sample_internal_data())

    resources = [entry["resource"] for entry in bundle["entry"]]
    service_request = next(
        resource
        for resource in resources
        if resource["resourceType"] == "ServiceRequest"
    )

    assert service_request["status"] == "draft"
    assert service_request["intent"] == "proposal"
    assert service_request["extension"][0]["valueCode"] == "non_urgent"


def test_generated_bundle_passes_fhir_resources_validation():
    bundle = map_to_fhir_bundle(_sample_internal_data())

    validated = validate_fhir_bundle(bundle)

    assert validated["resourceType"] == "Bundle"
    assert validated["type"] == "collection"

class DummyCareena4Session:
    def __init__(self):
        self.session_id = "test-session"
        self.messages = [
            {
                "role": "user",
                "content": "Ich habe seit gestern starke Kopfschmerzen.",
            }
        ]
        self.medical_case = MedicalCase(
            observations=[
                Observation(
                    type="symptom",
                    label="Kopfschmerzen",
                    status="active",
                    person_ref="self",
                    onset="seit gestern",
                ),
                Observation(
                    type="symptom",
                    label="Kein Fieber",
                    status="negated",
                    person_ref="self",
                ),
            ]
        )
        self.recommendation_state = RecommendationState(
            recommendation_result=RecommendationResult(
                allowed=True,
                summary="Kopfschmerzen sollten beobachtet werden.",
                urgency_level="medium",
                next_step="Bei anhaltenden Beschwerden bitte hausärztlich abklären lassen.",
                reasons=["Beschwerden bestehen seit gestern."],
            )
        )


def test_careena4_session_bundle_can_include_profile_identifier():
    bundle = build_fhir_bundle_from_careena4_session(
        DummyCareena4Session(),
        profile_id=42,
    )

    patient = next(
        entry["resource"]
        for entry in bundle["entry"]
        if entry["resource"]["resourceType"] == "Patient"
    )

    assert patient["identifier"][0]["system"] == (
        "https://careena.local/fhir/NamingSystem/profile-id"
    )
    assert patient["identifier"][0]["value"] == "42"


def test_careena4_session_is_mapped_to_fhir_bundle():
    bundle = build_fhir_bundle_from_careena4_session(DummyCareena4Session())

    resources = [entry["resource"] for entry in bundle["entry"]]
    resource_types = [resource["resourceType"] for resource in resources]

    assert bundle["resourceType"] == "Bundle"
    assert "Patient" in resource_types
    assert "QuestionnaireResponse" in resource_types
    assert "Observation" in resource_types
    assert "ServiceRequest" in resource_types
    assert "Condition" not in resource_types

    observations = [
        resource
        for resource in resources
        if resource["resourceType"] == "Observation"
    ]

    assert len(observations) == 1
    assert observations[0]["code"]["text"] == "Kopfschmerzen"

    service_request = next(
        resource
        for resource in resources
        if resource["resourceType"] == "ServiceRequest"
    )

    assert service_request["extension"][0]["valueCode"] == "medium"
    assert "hausärztlich" in service_request["note"][0]["text"]


class FakeHapiResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FakeHapiHttpClient:
    def __init__(self):
        self.appointment = {
            "resourceType": "Appointment",
            "id": "appointment-1",
            "status": "proposed",
            "meta": {"versionId": "7"},
            "participant": [
                {
                    "actor": {"display": "Hausarztpraxis Dr. Schneider"},
                    "status": "needs-action",
                }
            ],
            "extension": [
                {"url": SESSION_EXTENSION_URL, "valueString": "session-1"},
                {"url": PROFILE_EXTENSION_URL, "valueInteger": 10},
            ],
        }
        self.put_payload = None
        self.put_headers = None

    def request(self, method, url, **kwargs):
        if method == "GET":
            return FakeHapiResponse(self.appointment)

        if method == "PUT":
            self.put_payload = kwargs["json"]
            self.put_headers = kwargs.get("headers")
            self.appointment = self.put_payload
            return FakeHapiResponse({"resourceType": "OperationOutcome"})

        raise AssertionError(f"Unexpected method {method}")


class SearchLagHapiHttpClient:
    def __init__(self):
        self.resources = {}
        self.collection_searches = 0

    def request(self, method, url, **kwargs):
        path = url.removeprefix("http://hapi.test/fhir")

        if method == "GET" and path == "/Appointment":
            self.collection_searches += 1
            return FakeHapiResponse(
                {
                    "resourceType": "Bundle",
                    "type": "searchset",
                    "entry": [],
                }
            )

        if method == "GET" and path.startswith("/Appointment/"):
            appointment_id = path.rsplit("/", 1)[-1]
            return FakeHapiResponse(self.resources[appointment_id])

        if method == "PUT" and path.startswith("/Appointment/"):
            resource = kwargs["json"]
            self.resources[resource["id"]] = resource
            return FakeHapiResponse({"resourceType": "OperationOutcome"})

        if method == "POST" and path == "":
            for entry in kwargs["json"].get("entry", []):
                resource = entry["resource"]
                self.resources[resource["id"]] = resource
            return FakeHapiResponse(
                {"resourceType": "Bundle", "type": "transaction-response"}
            )

        raise AssertionError(f"Unexpected HAPI call {method} {url}")


def test_hapi_client_returns_written_appointments_when_search_index_lags():
    http_client = SearchLagHapiHttpClient()
    client = HapiFhirClient(
        base_url="http://hapi.test/fhir",
        client=http_client,
    )

    appointments = client.ensure_recommendation_appointments(
        session_id="session-1",
        profile_id=10,
        postal_code="68159",
        recommendation_result=SimpleNamespace(
            urgency_level="medium",
            care_level="general_practice",
            specialty="general_practice",
            next_step="Bitte hausarztlich abklaren lassen.",
        ),
        bundle_id="bundle-1",
    )

    assert len(appointments) == 3
    assert http_client.collection_searches == 2
    assert all(appointment["status"] == "proposed" for appointment in appointments)
    assert not any(
        extension["url"] in {SESSION_EXTENSION_URL, PROFILE_EXTENSION_URL}
        for extension in appointments[0]["extension"]
    )
    assert {
        "url": POSTAL_CODE_EXTENSION_URL,
        "valueString": "68159",
    } in appointments[0]["extension"]


def test_hapi_client_books_appointment_with_account_extension():
    http_client = FakeHapiHttpClient()
    client = HapiFhirClient(
        base_url="http://hapi.test/fhir",
        client=http_client,
    )

    booked = client.book_appointment(
        appointment_id="appointment-1",
        booked_by_account_id=3,
    )

    assert booked["status"] == "booked"
    assert booked["participant"][0]["status"] == "accepted"
    assert {
        "url": BOOKED_BY_ACCOUNT_EXTENSION_URL,
        "valueInteger": 3,
    } in booked["extension"]
    assert http_client.put_headers["If-Match"] == 'W/"7"'


def test_hapi_client_releases_cancelled_appointment_for_rebooking():
    http_client = FakeHapiHttpClient()
    client = HapiFhirClient(
        base_url="http://hapi.test/fhir",
        client=http_client,
    )
    client.book_appointment(
        appointment_id="appointment-1",
        booked_by_account_id=3,
    )

    released = client.cancel_appointment(
        appointment_id="appointment-1",
        profile_id=10,
        booked_by_account_id=3,
    )

    assert released["status"] == "proposed"
    assert released["participant"][0]["status"] == "needs-action"
    assert not any(
        extension["url"] == BOOKED_BY_ACCOUNT_EXTENSION_URL
        for extension in released["extension"]
    )


def test_hapi_client_cancel_is_idempotent_after_slot_was_released():
    http_client = FakeHapiHttpClient()
    client = HapiFhirClient(
        base_url="http://hapi.test/fhir",
        client=http_client,
    )

    released = client.cancel_appointment(
        appointment_id="appointment-1",
        profile_id=10,
        booked_by_account_id=3,
    )

    assert released["status"] == "proposed"


def test_hapi_client_cancel_succeeds_when_resource_was_lost():
    class MissingAppointmentHttpClient:
        def request(self, method, url, **kwargs):
            return httpx.Response(
                404,
                request=httpx.Request(method, url),
                json={"resourceType": "OperationOutcome"},
            )

    client = HapiFhirClient(
        base_url="http://hapi.test/fhir",
        client=MissingAppointmentHttpClient(),
    )

    released = client.cancel_appointment(
        appointment_id="lost-appointment",
        profile_id=10,
        booked_by_account_id=3,
    )

    assert released["status"] == "cancelled"


def test_simulated_slots_are_shared_between_sessions():
    recommendation = SimpleNamespace(
        urgency_level="medium",
        care_level="general_practice",
        specialty="general_practice",
    )
    first = build_recommendation_appointment_resources(
        session_id="session-1",
        profile_id=10,
        postal_code="68159",
        recommendation_result=recommendation,
        bundle_id=None,
    )
    second = build_recommendation_appointment_resources(
        session_id="session-2",
        profile_id=20,
        postal_code="68159",
        recommendation_result=recommendation,
        bundle_id=None,
    )

    assert [item["id"] for item in first] == [item["id"] for item in second]


def test_simulator_catalog_contains_all_supported_specialties():
    class CatalogClient(HapiFhirClient):
        def __init__(self):
            self.written = []

        def list_all_appointments(self):
            return []

        def _put_appointments_transaction(self, resources):
            self.written.extend(resources)

    client = CatalogClient()
    client.ensure_simulator_catalog()

    specialties = {
        appointment["specialty"][0]["text"] for appointment in client.written
    }
    assert len(client.written) == 96
    assert {
        "Allgemeinmedizin",
        "HNO",
        "Zahnmedizin",
        "Augenheilkunde",
        "Orthopädie",
    }.issubset(specialties)


def test_specialist_provider_prefix_is_not_hausarztpraxis():
    resources = build_recommendation_appointment_resources(
        session_id="session-1",
        profile_id=10,
        postal_code="68159",
        recommendation_result=SimpleNamespace(
            urgency_level="medium",
            care_level="general_practice",
            specialty="orthopedics",
        ),
        bundle_id=None,
    )

    assert resources[0]["participant"][0]["actor"]["display"].startswith(
        "Facharztpraxis"
    )
