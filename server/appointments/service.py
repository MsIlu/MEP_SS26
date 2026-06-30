from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from appointments.schemas import (
    AppointmentRecommendationSummary,
    AppointmentSearchResponse,
    SimulatedAppointment,
)


SPECIALTY_LABELS = {
    "general_practice": "Allgemeinmedizin",
    "dermatology": "Dermatologie",
    "orthopedics": "Orthopädie",
    "neurology": "Neurologie",
    "ent": "HNO",
    "emergency_medicine": "Notfallmedizin",
    "unknown": "Allgemeinmedizin",
}


def search_simulated_appointments(
        *,
        session_id: str,
        profile_id: int,
        postal_code: str,
        recommendation_result: Any,
) -> AppointmentSearchResponse:
    urgency = getattr(recommendation_result, "urgency_level", "unclear")
    care_level = getattr(recommendation_result, "care_level", "unknown")
    specialty = getattr(recommendation_result, "specialty", "unknown")
    next_step = getattr(recommendation_result, "next_step", None)

    summary = AppointmentRecommendationSummary(
        specialty=specialty,
        care_level=care_level,
        urgency=urgency,
        next_step=next_step,
    )

    if care_level in {"112", "emergency_department"} or urgency == "emergency":
        return AppointmentSearchResponse(
            session_id=session_id,
            profile_id=profile_id,
            postal_code=postal_code,
            message=(
                "Für diese Empfehlung werden keine regulären Termine simuliert. "
                "Bitte folgen Sie der Notfall-Empfehlung aus Careena."
            ),
            recommendation_summary=summary,
            appointments=[],
        )

    appointment_offsets = _appointment_offsets_for_urgency(urgency)
    provider_type = _provider_type_for_care_level(care_level)
    specialty_label = SPECIALTY_LABELS.get(specialty, "Allgemeinmedizin")
    location = _location_for_postal_code(postal_code)

    appointments = [
        SimulatedAppointment(
            id=f"apt_{session_id[:8]}_{index}",
            provider_name=f"{provider_type} {provider_name}",
            specialty=specialty_label,
            address=f"{street}, {postal_code} {location}",
            distance_km=distance_km,
            date=(date.today() + timedelta(days=offset_days)).isoformat(),
            time=time,
            care_type=care_type,
            urgency_match=True,
        )
        for index, (provider_name, street, distance_km, offset_days, time, care_type)
        in enumerate(
            [
                (
                    "Dr. Schneider",
                    "Musterstraße 12",
                    2.4,
                    appointment_offsets[0],
                    "09:30",
                    "Vor-Ort-Termin",
                ),
                (
                    "Care Praxiszentrum",
                    "Bahnhofstraße 8",
                    4.1,
                    appointment_offsets[1],
                    "14:00",
                    "Vor-Ort-Termin",
                ),
                (
                    "Videosprechstunde CareConnect",
                    "Online",
                    0.0,
                    appointment_offsets[2],
                    "16:30",
                    "Videosprechstunde",
                ),
            ],
            start=1,
        )
    ]

    return AppointmentSearchResponse(
        session_id=session_id,
        profile_id=profile_id,
        postal_code=postal_code,
        message="Es wurden simulierte Termine passend zur Careena-Empfehlung gefunden.",
        recommendation_summary=summary,
        appointments=appointments,
    )


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