from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from uuid import NAMESPACE_URL, uuid5

import httpx

from config import FHIR_BASE_URL, FHIR_TIMEOUT_SECONDS


SESSION_EXTENSION_URL = (
    "https://careena.local/fhir/StructureDefinition/careena-session-id"
)
PROFILE_EXTENSION_URL = (
    "https://careena.local/fhir/StructureDefinition/careena-profile-id"
)
POSTAL_CODE_EXTENSION_URL = (
    "https://careena.local/fhir/StructureDefinition/careena-postal-code"
)
ADDRESS_EXTENSION_URL = (
    "https://careena.local/fhir/StructureDefinition/careena-appointment-address"
)
DISTANCE_EXTENSION_URL = (
    "https://careena.local/fhir/StructureDefinition/careena-distance-km"
)
URGENCY_MATCH_EXTENSION_URL = (
    "https://careena.local/fhir/StructureDefinition/careena-urgency-match"
)
CARE_TYPE_EXTENSION_URL = (
    "https://careena.local/fhir/StructureDefinition/careena-care-type"
)
BUNDLE_REFERENCE_EXTENSION_URL = (
    "https://careena.local/fhir/StructureDefinition/careena-source-bundle-id"
)
BOOKED_BY_ACCOUNT_EXTENSION_URL = (
    "https://careena.local/fhir/StructureDefinition/careena-booked-by-account-id"
)

SPECIALTY_LABELS = {
    "general_practice": "Allgemeinmedizin",
    "pediatrics": "Kinderheilkunde",
    "gynecology": "Gynaekologie",
    "dermatology": "Dermatologie",
    "orthopedics": "Orthopaedie",
    "neurology": "Neurologie",
    "ent": "HNO",
    "ophthalmology": "Augenheilkunde",
    "urology": "Urologie",
    "cardiology": "Kardiologie",
    "gastroenterology": "Gastroenterologie",
    "psychiatry": "Psychiatrie",
    "emergency_medicine": "Notfallmedizin",
    "unknown": "Allgemeinmedizin",
}


class HapiFhirError(RuntimeError):
    """Raised when the local HAPI FHIR adapter cannot be reached or parsed."""


class HapiFhirClient:
    """
    Thin adapter around the local HAPI FHIR REST API.

    The project does not have a productive 116117 FHIR endpoint. This client
    therefore uses local HAPI resources as the integration point: Careena
    bundles are stored in HAPI, appointment candidates are represented as FHIR
    Appointment resources, and the search endpoint reads those resources back.
    """

    def __init__(
            self,
            *,
            base_url: str = FHIR_BASE_URL,
            timeout_seconds: float = FHIR_TIMEOUT_SECONDS,
            client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._client = client

    def submit_bundle(self, bundle: dict[str, Any]) -> str:
        response = self._request(
            "POST",
            "/Bundle",
            json=bundle,
        )

        return str(response.get("id") or "")

    def ensure_recommendation_appointments(
            self,
            *,
            session_id: str,
            profile_id: int,
            postal_code: str,
            recommendation_result: Any,
            bundle_id: str | None,
    ) -> list[dict[str, Any]]:
        existing_appointments = self.search_appointments(
            session_id=session_id,
            profile_id=profile_id,
            postal_code=postal_code,
        )

        if existing_appointments:
            return existing_appointments

        written_appointments: list[dict[str, Any]] = []

        for resource in build_recommendation_appointment_resources(
            session_id=session_id,
            profile_id=profile_id,
            postal_code=postal_code,
            recommendation_result=recommendation_result,
            bundle_id=bundle_id,
        ):
            written_appointments.append(self._put_appointment(resource))

        indexed_appointments = self.search_appointments(
            session_id=session_id,
            profile_id=profile_id,
            postal_code=postal_code,
        )
        if indexed_appointments:
            return indexed_appointments

        confirmed_appointments = self._read_appointments_by_id(
            [appointment["id"] for appointment in written_appointments],
            session_id=session_id,
            profile_id=profile_id,
            postal_code=postal_code,
        )
        if confirmed_appointments:
            return confirmed_appointments

        return _sort_appointments(
            [
                appointment
                for appointment in written_appointments
                if _appointment_matches_search(
                    appointment,
                    session_id=session_id,
                    profile_id=profile_id,
                    postal_code=postal_code,
                    allowed_statuses={"proposed"},
                )
            ]
        )

    def search_appointments(
            self,
            *,
            session_id: str,
            profile_id: int,
            postal_code: str,
    ) -> list[dict[str, Any]]:
        bundle = self._request(
            "GET",
            "/Appointment",
            params={
                "status": "proposed",
                "_count": "50",
            },
        )

        appointments: list[dict[str, Any]] = []

        for entry in bundle.get("entry", []) or []:
            resource = entry.get("resource", {})
            if not _appointment_matches_search(
                resource,
                session_id=session_id,
                profile_id=profile_id,
                postal_code=postal_code,
                allowed_statuses={"proposed"},
            ):
                continue

            appointments.append(resource)

        return _sort_appointments(appointments)

    def get_appointment(self, appointment_id: str) -> dict[str, Any]:
        resource = self._request("GET", f"/Appointment/{appointment_id}")

        if resource.get("resourceType") != "Appointment":
            raise HapiFhirError("HAPI hat keine Appointment-Resource geliefert.")

        return resource

    def book_appointment(
            self,
            *,
            appointment_id: str,
            session_id: str,
            profile_id: int,
            booked_by_account_id: int,
    ) -> dict[str, Any]:
        appointment = self.get_appointment(appointment_id)

        if _extension_value(appointment, SESSION_EXTENSION_URL) != session_id:
            raise HapiFhirError("Der HAPI-Termin gehoert nicht zu dieser Session.")

        if _extension_value(appointment, PROFILE_EXTENSION_URL) != profile_id:
            raise HapiFhirError("Der HAPI-Termin gehoert nicht zu diesem Profil.")

        status = str(appointment.get("status") or "")
        if status not in {"proposed", "pending", "booked"}:
            raise HapiFhirError("Der HAPI-Termin kann nicht gebucht werden.")

        booked_by_account = _extension_value(
            appointment,
            BOOKED_BY_ACCOUNT_EXTENSION_URL,
        )
        if status == "booked" and str(booked_by_account) != str(booked_by_account_id):
            raise HapiFhirError("Der HAPI-Termin ist bereits gebucht.")

        appointment["status"] = "booked"
        appointment["comment"] = (
            "Aus einer Careena-Handlungsempfehlung gebuchter lokaler HAPI-Termin."
        )

        appointment["extension"] = [
            extension
            for extension in appointment.get("extension", []) or []
            if extension.get("url") != BOOKED_BY_ACCOUNT_EXTENSION_URL
        ]
        appointment["extension"].append(
            {
                "url": BOOKED_BY_ACCOUNT_EXTENSION_URL,
                "valueInteger": booked_by_account_id,
            }
        )

        for participant in appointment.get("participant", []) or []:
            participant["status"] = "accepted"

        updated_resource = self._request(
            "PUT",
            f"/Appointment/{appointment['id']}",
            json=appointment,
            headers={"Prefer": "return=representation"},
        )

        if updated_resource.get("resourceType") == "Appointment":
            return updated_resource

        return self.get_appointment(str(appointment["id"]))

    def _put_appointment(self, resource: dict[str, Any]) -> dict[str, Any]:
        updated_resource = self._request(
            "PUT",
            f"/Appointment/{resource['id']}",
            json=resource,
            headers={"Prefer": "return=representation"},
        )

        if updated_resource.get("resourceType") == "Appointment":
            return updated_resource

        return resource

    def _read_appointments_by_id(
            self,
            appointment_ids: list[str],
            *,
            session_id: str,
            profile_id: int,
            postal_code: str,
    ) -> list[dict[str, Any]]:
        appointments: list[dict[str, Any]] = []

        for appointment_id in appointment_ids:
            try:
                resource = self.get_appointment(appointment_id)
            except HapiFhirError:
                continue

            if _appointment_matches_search(
                resource,
                session_id=session_id,
                profile_id=profile_id,
                postal_code=postal_code,
                allowed_statuses={"proposed"},
            ):
                appointments.append(resource)

        return _sort_appointments(appointments)

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        headers = kwargs.pop("headers", {})
        headers.setdefault("Accept", "application/fhir+json")
        if "json" in kwargs:
            headers.setdefault("Content-Type", "application/fhir+json")

        try:
            if self._client is not None:
                response = self._client.request(
                    method,
                    f"{self.base_url}{path}",
                    headers=headers,
                    **kwargs,
                )
            else:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    response = client.request(
                        method,
                        f"{self.base_url}{path}",
                        headers=headers,
                        **kwargs,
                    )

            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            raise HapiFhirError(
                "Der lokale HAPI-FHIR-Server ist nicht erreichbar oder hat die "
                "FHIR-Anfrage abgelehnt."
            ) from exc
        except ValueError as exc:
            raise HapiFhirError(
                "Der lokale HAPI-FHIR-Server hat keine gueltige JSON-Antwort geliefert."
            ) from exc

        if not isinstance(data, dict):
            raise HapiFhirError(
                "Der lokale HAPI-FHIR-Server hat keine FHIR-Resource geliefert."
            )

        return data


def build_recommendation_appointment_resources(
        *,
        session_id: str,
        profile_id: int,
        postal_code: str,
        recommendation_result: Any,
        bundle_id: str | None,
) -> list[dict[str, Any]]:
    urgency = getattr(recommendation_result, "urgency_level", "unclear")
    care_level = getattr(recommendation_result, "care_level", "unknown")
    specialty = getattr(recommendation_result, "specialty", "unknown")
    next_step = getattr(recommendation_result, "next_step", None)
    summary = getattr(recommendation_result, "summary", None)

    specialty_label = SPECIALTY_LABELS.get(specialty, "Allgemeinmedizin")
    provider_type = _provider_type_for_care_level(care_level)
    location = _location_for_postal_code(postal_code)
    offsets = _appointment_offsets_for_urgency(urgency)

    appointment_templates = [
        (
            "Dr. Schneider",
            "Musterstrasse 12",
            2.4,
            offsets[0],
            time(9, 30),
            "Vor-Ort-Termin",
        ),
        (
            "Care Praxiszentrum",
            "Bahnhofstrasse 8",
            4.1,
            offsets[1],
            time(14, 0),
            "Vor-Ort-Termin",
        ),
        (
            "Videosprechstunde CareConnect",
            "Online",
            0.0,
            offsets[2],
            time(16, 30),
            "Videosprechstunde",
        ),
    ]

    resources: list[dict[str, Any]] = []

    for index, (
        provider_name,
        street,
        distance_km,
        offset_days,
        starts_at,
        care_type,
    ) in enumerate(appointment_templates, start=1):
        start = datetime.combine(
            date.today() + timedelta(days=offset_days),
            starts_at,
            tzinfo=timezone.utc,
        )
        end = start + timedelta(minutes=30)
        appointment_id = _stable_id(
            "Appointment",
            f"{session_id}:{profile_id}:{postal_code}:{index}",
        )
        provider_display = f"{provider_type} {provider_name}"
        address = (
            "Online"
            if street == "Online"
            else f"{street}, {postal_code} {location}"
        )

        resources.append(
            {
                "resourceType": "Appointment",
                "id": appointment_id,
                "identifier": [
                    {
                        "system": "https://careena.local/fhir/appointments",
                        "value": appointment_id,
                    }
                ],
                "status": "proposed",
                "description": next_step or summary or "Careena Terminempfehlung",
                "comment": "Aus einer Careena-Handlungsempfehlung erzeugter lokaler HAPI-Termin.",
                "created": datetime.now(timezone.utc).isoformat(),
                "start": start.isoformat(),
                "end": end.isoformat(),
                "minutesDuration": 30,
                "specialty": [
                    {
                        "text": specialty_label,
                    }
                ],
                "serviceType": [
                    {
                        "text": care_type,
                    }
                ],
                "participant": [
                    {
                        "actor": {
                            "display": provider_display,
                        },
                        "status": "needs-action",
                    },
                    {
                        "actor": {
                            "display": address,
                        },
                        "status": "accepted",
                    },
                ],
                "extension": [
                    {"url": SESSION_EXTENSION_URL, "valueString": session_id},
                    {"url": PROFILE_EXTENSION_URL, "valueInteger": profile_id},
                    {"url": POSTAL_CODE_EXTENSION_URL, "valueString": postal_code},
                    {"url": ADDRESS_EXTENSION_URL, "valueString": address},
                    {"url": DISTANCE_EXTENSION_URL, "valueDecimal": distance_km},
                    {"url": URGENCY_MATCH_EXTENSION_URL, "valueBoolean": True},
                    {"url": CARE_TYPE_EXTENSION_URL, "valueString": care_type},
                    *(
                        [
                            {
                                "url": BUNDLE_REFERENCE_EXTENSION_URL,
                                "valueString": bundle_id,
                            }
                        ]
                        if bundle_id
                        else []
                    ),
                ],
            }
        )

    return resources


def appointment_resource_to_result(resource: dict[str, Any]) -> dict[str, Any]:
    start = _parse_datetime(resource.get("start"))
    appointment_date = start.date().isoformat() if start is not None else ""
    appointment_time = start.strftime("%H:%M") if start is not None else ""

    return {
        "id": str(
            _first_identifier_value(resource)
            or resource.get("id")
            or ""
        ),
        "provider_name": _provider_display(resource),
        "specialty": _first_text(resource.get("specialty")) or "Allgemeinmedizin",
        "address": str(_extension_value(resource, ADDRESS_EXTENSION_URL) or ""),
        "distance_km": float(
            _extension_value(resource, DISTANCE_EXTENSION_URL) or 0
        ),
        "date": appointment_date,
        "time": appointment_time,
        "care_type": str(
            _extension_value(resource, CARE_TYPE_EXTENSION_URL)
            or _first_text(resource.get("serviceType"))
            or "Termin"
        ),
        "urgency_match": bool(
            _extension_value(resource, URGENCY_MATCH_EXTENSION_URL)
        ),
        "source": "hapi-fhir",
    }


def _appointment_matches_search(
        resource: dict[str, Any],
        *,
        session_id: str,
        profile_id: int,
        postal_code: str,
        allowed_statuses: set[str],
) -> bool:
    if resource.get("resourceType") != "Appointment":
        return False

    if str(resource.get("status") or "") not in allowed_statuses:
        return False

    return (
        str(_extension_value(resource, SESSION_EXTENSION_URL)) == str(session_id)
        and str(_extension_value(resource, PROFILE_EXTENSION_URL)) == str(profile_id)
        and str(_extension_value(resource, POSTAL_CODE_EXTENSION_URL))
        == str(postal_code)
    )


def _sort_appointments(appointments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(appointments, key=lambda item: item.get("start") or "")


def _extension_value(resource: dict[str, Any], url: str) -> Any:
    for extension in resource.get("extension", []) or []:
        if extension.get("url") != url:
            continue

        for key, value in extension.items():
            if key.startswith("value"):
                return value

    return None


def _first_identifier_value(resource: dict[str, Any]) -> str | None:
    for identifier in resource.get("identifier", []) or []:
        value = identifier.get("value")
        if value:
            return str(value)

    return None


def _first_text(items: Any) -> str | None:
    if not isinstance(items, list):
        return None

    for item in items:
        if isinstance(item, dict):
            text = item.get("text")
            if text:
                return str(text)

            coding = item.get("coding")
            if isinstance(coding, list):
                for code in coding:
                    display = code.get("display")
                    if display:
                        return str(display)

    return None


def _provider_display(resource: dict[str, Any]) -> str:
    for participant in resource.get("participant", []) or []:
        actor = participant.get("actor", {})
        display = actor.get("display")
        if display and display != _extension_value(resource, ADDRESS_EXTENSION_URL):
            return str(display)

    return "FHIR-Termin"


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None

    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _appointment_offsets_for_urgency(urgency: str) -> list[int]:
    if urgency == "high":
        return [0, 1, 2]

    if urgency == "medium":
        return [2, 4, 6]

    if urgency == "low":
        return [7, 14, 21]

    return [5, 10, 15]


def _provider_type_for_care_level(care_level: str) -> str:
    if care_level == "general_practice":
        return "Hausarztpraxis"

    if care_level == "specialist":
        return "Facharztpraxis"

    if care_level == "116117":
        return "Terminservicestelle"

    return "Praxis"


def _location_for_postal_code(postal_code: str) -> str:
    if postal_code.startswith("68"):
        return "Mannheim"

    if postal_code.startswith("69"):
        return "Heidelberg"

    if postal_code.startswith("70"):
        return "Stuttgart"

    if postal_code.startswith("10"):
        return "Berlin"

    return "Ihre Umgebung"


def _stable_id(prefix: str, value: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"careena:{prefix}:{value}"))
