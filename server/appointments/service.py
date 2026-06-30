from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import Session, select

from appointments.schemas import (
    AppointmentRecommendationSummary,
    AppointmentSearchResponse,
    FhirAppointment,
    RecommendedAppointmentCreateRequest,
    RecommendedAppointmentResponse,
)
from database.models import RecommendedAppointment, User
from fhir_mapper.hapi_client import (
    HapiFhirClient,
    HapiFhirError,
    appointment_resource_to_result,
)
from profiles.service import EDIT_ROLES, get_profile_access_role, require_profile_role


class AppointmentProviderUnavailable(RuntimeError):
    """Raised when the local FHIR appointment provider cannot be reached."""


def search_fhir_appointments(
        *,
        session_id: str,
        profile_id: int,
        postal_code: str,
        recommendation_result: Any,
        fhir_bundle: dict[str, Any],
        fhir_client: HapiFhirClient | None = None,
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

    client = fhir_client or HapiFhirClient()

    try:
        bundle_id = client.submit_bundle(fhir_bundle)
    except HapiFhirError as exc:
        raise AppointmentProviderUnavailable(str(exc)) from exc

    if care_level in {"112", "emergency_department"} or urgency == "emergency":
        return AppointmentSearchResponse(
            session_id=session_id,
            profile_id=profile_id,
            postal_code=postal_code,
            message=(
                "Die Careena-Empfehlung wurde als FHIR-Bundle an HAPI uebertragen. "
                "Fuer Notfall-Empfehlungen werden keine regulaeren Termine bereitgestellt."
            ),
            recommendation_summary=summary,
            appointments=[],
        )

    try:
        resources = client.ensure_recommendation_appointments(
            session_id=session_id,
            profile_id=profile_id,
            postal_code=postal_code,
            recommendation_result=recommendation_result,
            bundle_id=bundle_id,
        )
    except HapiFhirError as exc:
        raise AppointmentProviderUnavailable(str(exc)) from exc

    appointments = [
        FhirAppointment(**appointment_resource_to_result(resource))
        for resource in resources
    ]

    message = (
        "HAPI-FHIR hat passende Termine zur Careena-Empfehlung bereitgestellt."
        if appointments
        else "HAPI-FHIR hat aktuell keine passenden Termine bereitgestellt."
    )

    return AppointmentSearchResponse(
        session_id=session_id,
        profile_id=profile_id,
        postal_code=postal_code,
        message=message,
        recommendation_summary=summary,
        appointments=appointments,
    )


def list_recommended_appointments(
        *,
        profile_id: int,
        current_user: User,
        session: Session,
) -> list[RecommendedAppointmentResponse]:
    get_profile_access_role(
        account_id=current_user.id,
        profile_id=profile_id,
        session=session,
    )

    entries = session.exec(
        select(RecommendedAppointment)
        .where(RecommendedAppointment.profile_id == profile_id)
        .where(RecommendedAppointment.deleted_at.is_(None))
        .order_by(RecommendedAppointment.starts_at, RecommendedAppointment.id)
    ).all()

    return [_to_recommended_response(entry) for entry in entries]


def save_recommended_appointment(
        *,
        profile_id: int,
        request: RecommendedAppointmentCreateRequest,
        current_user: User,
        session: Session,
) -> RecommendedAppointmentResponse:
    require_profile_role(
        account_id=current_user.id,
        profile_id=profile_id,
        allowed_roles=EDIT_ROLES,
        session=session,
    )

    starts_at = _parse_appointment_start(request.date, request.time)

    existing = session.exec(
        select(RecommendedAppointment)
        .where(RecommendedAppointment.profile_id == profile_id)
        .where(
            RecommendedAppointment.fhir_appointment_id
            == request.fhir_appointment_id.strip()
        )
        .where(RecommendedAppointment.deleted_at.is_(None))
    ).first()

    if existing is not None:
        return _to_recommended_response(existing)

    entry = RecommendedAppointment(
        profile_id=profile_id,
        session_id=request.session_id,
        fhir_appointment_id=request.fhir_appointment_id.strip(),
        provider_name=request.provider_name.strip(),
        specialty=request.specialty.strip(),
        address=request.address.strip(),
        distance_km=request.distance_km,
        starts_at=starts_at,
        care_type=request.care_type.strip(),
        note=(request.note or "").strip() or None,
    )

    session.add(entry)
    session.commit()
    session.refresh(entry)

    return _to_recommended_response(entry)


def _parse_appointment_start(date_value: str, time_value: str) -> datetime:
    try:
        return datetime.fromisoformat(f"{date_value}T{time_value}:00")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Der Terminzeitpunkt ist ungueltig.",
        ) from exc


def _to_recommended_response(
        entry: RecommendedAppointment,
) -> RecommendedAppointmentResponse:
    return RecommendedAppointmentResponse(
        id=entry.id,
        profile_id=entry.profile_id,
        session_id=entry.session_id,
        fhir_appointment_id=entry.fhir_appointment_id,
        provider_name=entry.provider_name,
        specialty=entry.specialty,
        address=entry.address,
        distance_km=entry.distance_km,
        starts_at=entry.starts_at,
        care_type=entry.care_type,
        note=entry.note,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )
