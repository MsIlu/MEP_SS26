from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from uuid import NAMESPACE_URL, uuid5

import httpx

from appointments.simulator_catalog import (
    SPECIALTY_LABELS,
    providers_for,
    simulated_location,
)
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

class HapiFhirError(RuntimeError):
    """Raised when the local HAPI FHIR adapter cannot be reached or parsed."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


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
            specialty=getattr(recommendation_result, "specialty", "unknown"),
        )

        if existing_appointments:
            return existing_appointments

        existing_resources = self.search_appointments(
            session_id=session_id,
            profile_id=profile_id,
            postal_code=postal_code,
            specialty=getattr(recommendation_result, "specialty", "unknown"),
            allowed_statuses={"proposed", "pending", "booked", "cancelled"},
        )
        existing_by_id = {
            str(resource.get("id")): resource for resource in existing_resources
        }
        written_appointments: list[dict[str, Any]] = []
        new_resources: list[dict[str, Any]] = []

        for resource in build_recommendation_appointment_resources(
            session_id=session_id,
            profile_id=profile_id,
            postal_code=postal_code,
            recommendation_result=recommendation_result,
            bundle_id=bundle_id,
        ):
            existing = existing_by_id.get(str(resource["id"]))
            if existing is not None and existing.get("status") in {
                "proposed",
                "pending",
                "booked",
            }:
                written_appointments.append(existing)
                continue
            new_resources.append(resource)

        if new_resources:
            self._put_appointments_transaction(new_resources)
            written_appointments.extend(new_resources)

        indexed_appointments = self.search_appointments(
            session_id=session_id,
            profile_id=profile_id,
            postal_code=postal_code,
            specialty=getattr(recommendation_result, "specialty", "unknown"),
        )
        if indexed_appointments:
            return indexed_appointments

        confirmed_appointments = self._read_appointments_by_id(
            [appointment["id"] for appointment in written_appointments],
            session_id=session_id,
            profile_id=profile_id,
            postal_code=postal_code,
            specialty=getattr(recommendation_result, "specialty", "unknown"),
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
                    specialty=getattr(recommendation_result, "specialty", "unknown"),
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
            specialty: str | None = None,
            allowed_statuses: set[str] | None = None,
    ) -> list[dict[str, Any]]:
        allowed_statuses = allowed_statuses or {"proposed"}
        params: dict[str, str] = {"_count": "500"}
        if len(allowed_statuses) == 1:
            params["status"] = next(iter(allowed_statuses))
        bundle = self._request(
            "GET",
            "/Appointment",
            params=params,
        )

        appointments: list[dict[str, Any]] = []

        for entry in bundle.get("entry", []) or []:
            resource = entry.get("resource", {})
            if not _appointment_matches_search(
                resource,
                session_id=session_id,
                profile_id=profile_id,
                postal_code=postal_code,
                specialty=specialty,
                allowed_statuses=allowed_statuses,
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
            booked_by_account_id: int,
    ) -> dict[str, Any]:
        """Book one global simulator slot for the authenticated account.

        Free slots intentionally have no session/profile owner, mirroring a
        shared 116117 catalog. Profile authorization and persistence happen in
        the appointment service before this HAPI operation; the booked account
        extension protects the slot after booking.
        """
        appointment = self.get_appointment(appointment_id)

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
            headers=_versioned_update_headers(appointment),
        )

        if updated_resource.get("resourceType") == "Appointment":
            return updated_resource

        return self.get_appointment(str(appointment["id"]))

    def cancel_appointment(
            self,
            *,
            appointment_id: str,
            profile_id: int,
            booked_by_account_id: int,
    ) -> dict[str, Any]:
        try:
            appointment = self.get_appointment(appointment_id)
        except HapiFhirError as exc:
            if exc.status_code == 404:
                # PostgreSQL can outlive a non-persistent/recreated HAPI
                # instance. Nothing remains to release remotely, so allow the
                # owned local booking to be marked as cancelled.
                return {
                    "resourceType": "Appointment",
                    "id": appointment_id,
                    "status": "cancelled",
                }
            raise

        booked_by_account = _extension_value(
            appointment,
            BOOKED_BY_ACCOUNT_EXTENSION_URL,
        )
        if (
            appointment.get("status") == "proposed"
            and booked_by_account is None
        ):
            # A previous cancellation may have released the FHIR slot before
            # the local database row could be marked as cancelled. Treat that
            # retry as successful so the local record can still be removed.
            return appointment
        if str(booked_by_account) != str(booked_by_account_id):
            raise HapiFhirError("Der HAPI-Termin wurde von einem anderen Account gebucht.")

        if appointment.get("status") != "booked":
            raise HapiFhirError("Nur ein gebuchter HAPI-Termin kann storniert werden.")

        # A cancellation removes the user's booking but releases the simulated
        # 116117 slot immediately so another search can book it again.
        appointment["status"] = "proposed"
        appointment["comment"] = (
            "Stornierter Termin wurde im simulierten 116117-Terminservice "
            "wieder freigegeben."
        )
        appointment["extension"] = [
            extension
            for extension in appointment.get("extension", []) or []
            if extension.get("url") != BOOKED_BY_ACCOUNT_EXTENSION_URL
        ]
        for index, participant in enumerate(appointment.get("participant", []) or []):
            participant["status"] = "needs-action" if index == 0 else "accepted"

        updated_resource = self._request(
            "PUT",
            f"/Appointment/{appointment['id']}",
            json=appointment,
            headers=_versioned_update_headers(appointment),
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

    def _put_appointments_transaction(
            self,
            resources: list[dict[str, Any]],
    ) -> None:
        """Write simulator slots with one atomic FHIR transaction request."""
        self._request(
            "POST",
            "",
            json={
                "resourceType": "Bundle",
                "type": "transaction",
                "entry": [
                    {
                        "resource": resource,
                        "request": {
                            "method": "PUT",
                            "url": f"Appointment/{resource['id']}",
                        },
                    }
                    for resource in resources
                ],
            },
        )

    def list_all_appointments(self) -> list[dict[str, Any]]:
        bundle = self._request(
            "GET",
            "/Appointment",
            params={"_count": "500"},
        )
        return [
            entry.get("resource", {})
            for entry in bundle.get("entry", []) or []
            if entry.get("resource", {}).get("resourceType") == "Appointment"
        ]

    def ensure_simulator_catalog(self, postal_code: str = "68159") -> None:
        """Seed one shared set of slots for every supported medical specialty."""
        existing_by_id = {
            str(resource.get("id")): resource
            for resource in self.list_all_appointments()
        }
        resources_to_write: list[dict[str, Any]] = []

        for specialty in SPECIALTY_LABELS:
            if specialty in {"unknown", "emergency_medicine"}:
                continue

            recommendation = type(
                "SimulatorRecommendation",
                (),
                {
                    "urgency_level": "medium",
                    "care_level": (
                        "general_practice"
                        if specialty == "general_practice"
                        else "specialist"
                    ),
                    "specialty": specialty,
                    "next_step": "Termin im simulierten 116117-Terminservice",
                    "summary": None,
                },
            )()

            for resource in build_recommendation_appointment_resources(
                session_id="simulator-catalog",
                profile_id=0,
                postal_code=postal_code,
                recommendation_result=recommendation,
                bundle_id=None,
            ):
                existing = existing_by_id.get(str(resource["id"]))
                if existing is not None:
                    if existing.get("status") == "booked":
                        continue
                    if (
                        existing.get("status") in {"proposed", "pending"}
                        and _provider_display(existing)
                        == _provider_display(resource)
                    ):
                        continue
                resources_to_write.append(resource)

        if resources_to_write:
            self._put_appointments_transaction(resources_to_write)

    def _read_appointments_by_id(
            self,
            appointment_ids: list[str],
            *,
            session_id: str,
            profile_id: int,
            postal_code: str,
            specialty: str | None = None,
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
                specialty=specialty,
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
        except httpx.HTTPStatusError as exc:
            raise HapiFhirError(
                "Der lokale HAPI-FHIR-Server hat die FHIR-Anfrage abgelehnt.",
                status_code=exc.response.status_code,
            ) from exc
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
    specialty = getattr(recommendation_result, "specialty", "unknown")
    next_step = getattr(recommendation_result, "next_step", None)
    summary = getattr(recommendation_result, "summary", None)

    specialty_label = SPECIALTY_LABELS.get(specialty, "Allgemeinmedizin")
    provider_type = _provider_type_for_specialty(specialty)
    location = simulated_location(postal_code)
    offsets = _appointment_offsets_for_urgency(urgency)
    providers = providers_for(postal_code, specialty)
    slot_times = (time(8, 30), time(10, 15), time(14, 0), time(16, 30))

    appointment_templates: list[tuple[str, str, float, int, time, str]] = []
    for provider_index, provider in enumerate(providers):
        for slot_index in range(3):
            is_video = provider.supports_video and slot_index == 2
            appointment_templates.append(
                (
                    provider.name,
                    "Online" if is_video else provider.street,
                    0.0 if is_video else provider.base_distance_km + slot_index * 0.4,
                    offsets[(provider_index + slot_index) % len(offsets)] + provider_index,
                    slot_times[(provider_index + slot_index) % len(slot_times)],
                    "Videosprechstunde" if is_video else "Vor-Ort-Termin",
                )
            )

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
            f"{postal_code}:{provider_name}:{start.isoformat()}:{care_type}",
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
        specialty: str | None,
        allowed_statuses: set[str],
) -> bool:
    if resource.get("resourceType") != "Appointment":
        return False

    if str(resource.get("status") or "") not in allowed_statuses:
        return False

    resource_session = _extension_value(resource, SESSION_EXTENSION_URL)
    resource_profile = _extension_value(resource, PROFILE_EXTENSION_URL)
    if resource_session is not None and str(resource_session) != str(session_id):
        return False
    if resource_profile is not None and str(resource_profile) != str(profile_id):
        return False
    if str(_extension_value(resource, POSTAL_CODE_EXTENSION_URL)) != str(postal_code):
        return False

    if specialty is not None:
        expected_specialty = SPECIALTY_LABELS.get(specialty, "Allgemeinmedizin")
        if (_first_text(resource.get("specialty")) or "") != expected_specialty:
            return False

    start = _parse_datetime(resource.get("start"))
    return start is not None and start >= datetime.now(timezone.utc)


def _sort_appointments(appointments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(appointments, key=lambda item: item.get("start") or "")


def _versioned_update_headers(resource: dict[str, Any]) -> dict[str, str]:
    headers = {"Prefer": "return=representation"}
    version_id = resource.get("meta", {}).get("versionId")
    if version_id:
        headers["If-Match"] = f'W/"{version_id}"'
    return headers


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
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return (
            parsed
            if parsed.tzinfo is not None
            else parsed.replace(tzinfo=timezone.utc)
        )
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


def _provider_type_for_specialty(specialty: str) -> str:
    return {
        "general_practice": "Hausarztpraxis",
        "dentistry": "Zahnarztpraxis",
        "ophthalmology": "Augenarztpraxis",
        "gynecology": "Frauenarztpraxis",
        "pediatrics": "Kinderarztpraxis",
        "ent": "HNO-Praxis",
    }.get(specialty, "Facharztpraxis")


def _stable_id(prefix: str, value: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"careena:{prefix}:{value}"))
