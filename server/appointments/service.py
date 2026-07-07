"""Business logic for FHIR-based appointment search and booking."""

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
    RecommendedAppointmentRescheduleRequest,
    RecommendedAppointmentResponse,
)
from database.models import RecommendedAppointment, User, utc_now
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
                "Für Notfall-Empfehlungen werden keine regulären Termine "
                "bereitgestellt. Bitte folge den angezeigten Notfallhinweisen."
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
        "Der simulierte 116117-Terminservice hat passende Termine bereitgestellt."
        if appointments
        else "Der simulierte 116117-Terminservice hat aktuell keine passenden Termine."
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
        .where(RecommendedAppointment.status == "booked")
        .order_by(RecommendedAppointment.starts_at, RecommendedAppointment.id)
    ).all()

    return [_to_recommended_response(entry) for entry in _deduplicate_entries(entries)]


def save_recommended_appointment(
        *,
        profile_id: int,
        request: RecommendedAppointmentCreateRequest,
        current_user: User,
        session: Session,
        fhir_client: HapiFhirClient | None = None,
) -> RecommendedAppointmentResponse:
    require_profile_role(
        account_id=current_user.id,
        profile_id=profile_id,
        allowed_roles=EDIT_ROLES,
        session=session,
    )

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

    client = fhir_client or HapiFhirClient()

    try:
        booked_resource = client.book_appointment(
            appointment_id=request.fhir_appointment_id.strip(),
            booked_by_account_id=current_user.id,
        )
    except HapiFhirError as exc:
        raise _hapi_booking_exception(exc) from exc

    appointment_data = appointment_resource_to_result(booked_resource)
    starts_at = _parse_hapi_appointment_start(
        booked_resource,
        date_value=appointment_data["date"],
        time_value=appointment_data["time"],
    )

    entry = RecommendedAppointment(
        profile_id=profile_id,
        booked_by_account_id=current_user.id,
        session_id=request.session_id.strip(),
        fhir_appointment_id=appointment_data["id"],
        provider_name=appointment_data["provider_name"].strip(),
        specialty=appointment_data["specialty"].strip(),
        address=appointment_data["address"].strip(),
        distance_km=appointment_data["distance_km"],
        starts_at=starts_at,
        care_type=appointment_data["care_type"].strip(),
        note=(request.note or "").strip() or None,
        status="booked",
    )

    session.add(entry)
    session.commit()
    session.refresh(entry)

    return _to_recommended_response(entry)


def cancel_recommended_appointment(
        *,
        profile_id: int,
        appointment_id: int,
        current_user: User,
        session: Session,
        fhir_client: HapiFhirClient | None = None,
) -> None:
    require_profile_role(
        account_id=current_user.id,
        profile_id=profile_id,
        allowed_roles=EDIT_ROLES,
        session=session,
    )
    entry = _active_recommended_appointment(
        profile_id=profile_id,
        appointment_id=appointment_id,
        session=session,
    )
    client = fhir_client or HapiFhirClient()
    try:
        _cancel_fhir_appointment(
            client=client,
            appointment_id=entry.fhir_appointment_id,
            profile_id=profile_id,
            booked_by_account_id=entry.booked_by_account_id,
        )
    except HapiFhirError as exc:
        raise _hapi_booking_exception(exc) from exc

    now = utc_now()
    entry.status = "cancelled"
    entry.deleted_at = now
    entry.updated_at = now
    session.add(entry)
    session.commit()


def reschedule_recommended_appointment(
        *,
        profile_id: int,
        appointment_id: int,
        request: RecommendedAppointmentRescheduleRequest,
        current_user: User,
        session: Session,
        fhir_client: HapiFhirClient | None = None,
) -> RecommendedAppointmentResponse:
    require_profile_role(
        account_id=current_user.id,
        profile_id=profile_id,
        allowed_roles=EDIT_ROLES,
        session=session,
    )
    entry = _active_recommended_appointment(
        profile_id=profile_id,
        appointment_id=appointment_id,
        session=session,
    )
    replacement_id = request.replacement_fhir_appointment_id.strip()
    if replacement_id == entry.fhir_appointment_id:
        return _to_recommended_response(entry)

    client = fhir_client or HapiFhirClient()
    try:
        replacement = client.book_appointment(
            appointment_id=replacement_id,
            booked_by_account_id=current_user.id,
        )
        try:
            _cancel_fhir_appointment(
                client=client,
                appointment_id=entry.fhir_appointment_id,
                profile_id=profile_id,
                booked_by_account_id=entry.booked_by_account_id,
            )
        except HapiFhirError as original_cancellation_error:
            # Best-effort compensation: keep the original booking when its
            # cancellation failed and release the newly selected slot.
            try:
                _cancel_fhir_appointment(
                    client=client,
                    appointment_id=replacement_id,
                    profile_id=profile_id,
                    booked_by_account_id=current_user.id,
                )
            except HapiFhirError as compensation_error:
                # Never leave a successfully booked replacement invisible.
                # If both remote cancellations fail, persist it as a second
                # manageable appointment so the user can cancel either slot.
                _persist_replacement_booking(
                    profile_id=profile_id,
                    session_id=request.session_id.strip(),
                    current_user=current_user,
                    replacement=replacement,
                    note=request.note,
                    session=session,
                )
                raise HapiFhirError(
                    "Alter und neuer Termin sind weiterhin gebucht und werden "
                    "beide in der Terminplanung angezeigt. Bitte storniere "
                    "den nicht gewünschten Termin erneut."
                ) from compensation_error
            raise original_cancellation_error
    except HapiFhirError as exc:
        raise _hapi_booking_exception(exc) from exc

    data = appointment_resource_to_result(replacement)
    entry.session_id = request.session_id.strip()
    entry.booked_by_account_id = current_user.id
    entry.fhir_appointment_id = data["id"]
    entry.provider_name = data["provider_name"].strip()
    entry.specialty = data["specialty"].strip()
    entry.address = data["address"].strip()
    entry.distance_km = data["distance_km"]
    entry.starts_at = _parse_hapi_appointment_start(
        replacement,
        date_value=data["date"],
        time_value=data["time"],
    )
    entry.care_type = data["care_type"].strip()
    if request.note is not None:
        entry.note = request.note.strip() or None
    entry.status = "booked"
    entry.updated_at = utc_now()
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return _to_recommended_response(entry)


def _cancel_fhir_appointment(
        *,
        client: HapiFhirClient,
        appointment_id: str,
        profile_id: int,
        booked_by_account_id: int,
        attempts: int = 2,
) -> dict[str, Any]:
    """Retry a cancellation once to absorb short-lived HAPI conflicts."""
    last_error: HapiFhirError | None = None
    for _ in range(attempts):
        try:
            return client.cancel_appointment(
                appointment_id=appointment_id,
                profile_id=profile_id,
                booked_by_account_id=booked_by_account_id,
            )
        except HapiFhirError as exc:
            last_error = exc

    assert last_error is not None
    raise last_error


def _persist_replacement_booking(
        *,
        profile_id: int,
        session_id: str,
        current_user: User,
        replacement: dict[str, Any],
        note: str | None,
        session: Session,
) -> None:
    data = appointment_resource_to_result(replacement)
    existing = session.exec(
        select(RecommendedAppointment)
        .where(RecommendedAppointment.profile_id == profile_id)
        .where(RecommendedAppointment.fhir_appointment_id == data["id"])
        .where(RecommendedAppointment.deleted_at.is_(None))
    ).first()
    if existing is not None:
        return

    session.add(
        RecommendedAppointment(
            profile_id=profile_id,
            booked_by_account_id=current_user.id,
            session_id=session_id,
            fhir_appointment_id=data["id"],
            provider_name=data["provider_name"].strip(),
            specialty=data["specialty"].strip(),
            address=data["address"].strip(),
            distance_km=data["distance_km"],
            starts_at=_parse_hapi_appointment_start(
                replacement,
                date_value=data["date"],
                time_value=data["time"],
            ),
            care_type=data["care_type"].strip(),
            note=(note or "").strip() or None,
            status="booked",
        )
    )
    session.commit()


def _active_recommended_appointment(
        *,
        profile_id: int,
        appointment_id: int,
        session: Session,
) -> RecommendedAppointment:
    entry = session.exec(
        select(RecommendedAppointment)
        .where(RecommendedAppointment.id == appointment_id)
        .where(RecommendedAppointment.profile_id == profile_id)
        .where(RecommendedAppointment.deleted_at.is_(None))
        .where(RecommendedAppointment.status == "booked")
    ).first()
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Der gebuchte Termin wurde nicht gefunden.",
        )
    return entry


def _deduplicate_entries(
        entries: list[RecommendedAppointment],
) -> list[RecommendedAppointment]:
    """Return each booked appointment once, even if stale duplicate rows exist."""

    result: list[RecommendedAppointment] = []
    seen_keys: set[tuple[Any, ...]] = set()

    for entry in entries:
        key = (
            entry.profile_id,
            (entry.fhir_appointment_id or "").strip().lower(),
        )
        fallback_key = (
            entry.profile_id,
            entry.provider_name.strip().lower(),
            entry.starts_at,
        )

        if key in seen_keys or fallback_key in seen_keys:
            continue

        seen_keys.add(key)
        seen_keys.add(fallback_key)
        result.append(entry)

    return result


def _parse_hapi_appointment_start(
        resource: dict[str, Any],
        *,
        date_value: str,
        time_value: str,
) -> datetime:
    start_value = resource.get("start")

    if start_value:
        try:
            return datetime.fromisoformat(str(start_value).replace("Z", "+00:00"))
        except ValueError:
            pass

    return _parse_appointment_start(date_value, time_value)


def _parse_appointment_start(date_value: str, time_value: str) -> datetime:
    try:
        return datetime.fromisoformat(f"{date_value}T{time_value}:00")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Der Terminzeitpunkt ist ungueltig.",
        ) from exc


def _hapi_booking_exception(exc: HapiFhirError) -> HTTPException:
    detail = str(exc)
    status_code = (
        status.HTTP_503_SERVICE_UNAVAILABLE
        if (
            "nicht erreichbar" in detail
            or "keine gueltige JSON-Antwort" in detail
            or "keine FHIR-Resource" in detail
        )
        else status.HTTP_409_CONFLICT
    )
    return HTTPException(status_code=status_code, detail=detail)


def _to_recommended_response(
        entry: RecommendedAppointment,
) -> RecommendedAppointmentResponse:
    return RecommendedAppointmentResponse(
        id=entry.id,
        profile_id=entry.profile_id,
        session_id=entry.session_id,
        booked_by_account_id=entry.booked_by_account_id,
        fhir_appointment_id=entry.fhir_appointment_id,
        provider_name=entry.provider_name,
        specialty=entry.specialty,
        address=entry.address,
        distance_km=entry.distance_km,
        starts_at=entry.starts_at,
        care_type=entry.care_type,
        note=entry.note,
        status=entry.status,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )
