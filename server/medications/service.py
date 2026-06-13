# Business logic and authorization checks for profile-scoped medications.

from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import Session, select

from database.models import MedicationEntry, User
from medications.schemas import (
    MedicationCatalogItemRequest,
    MedicationCatalogItemResponse,
    MedicationCreateRequest,
    MedicationDeleteResponse,
    MedicationResponse,
    MedicationUpdateRequest,
)
from profiles.service import EDIT_ROLES, get_profile_access_role, require_profile_role


def list_medications(
        profile_id: int,
        current_user: User,
        session: Session,
) -> list[MedicationResponse]:
    """
    Return all non-deleted medication entries for an accessible profile.
    """
    get_profile_access_role(
        account_id=current_user.id,
        profile_id=profile_id,
        session=session,
    )

    entries = session.exec(
        select(MedicationEntry)
        .where(MedicationEntry.profile_id == profile_id)
        .where(MedicationEntry.deleted_at.is_(None))
        .order_by(
            MedicationEntry.intake_hour,
            MedicationEntry.intake_minute,
            MedicationEntry.id,
        )
    ).all()

    return [_to_response(entry) for entry in entries]


def create_medication(
        profile_id: int,
        request: MedicationCreateRequest,
        current_user: User,
        session: Session,
) -> MedicationResponse:
    """
    Create a medication entry for a profile if the account may edit it.
    """
    require_profile_role(
        account_id=current_user.id,
        profile_id=profile_id,
        allowed_roles=EDIT_ROLES,
        session=session,
    )
    _validate_second_intake_pair(
        request.second_intake_hour,
        request.second_intake_minute,
    )
    _ensure_medication_is_not_duplicate(
        profile_id=profile_id,
        name=request.name,
        dose=request.dose,
        intake_hour=request.intake_hour,
        intake_minute=request.intake_minute,
        second_intake_hour=request.second_intake_hour,
        second_intake_minute=request.second_intake_minute,
        frequency=request.frequency,
        session=session,
    )

    entry = MedicationEntry(
        profile_id=profile_id,
        name=request.name.strip(),
        dose=request.dose.strip(),
        intake_hour=request.intake_hour,
        intake_minute=request.intake_minute,
        second_intake_hour=request.second_intake_hour,
        second_intake_minute=request.second_intake_minute,
        frequency=request.frequency,
        reminders_enabled=request.reminders_enabled,
        taken_date_keys=request.taken_date_keys,
        created_at=request.created_at or datetime.utcnow(),
    )
    _apply_catalog_item(entry, request.catalog_item)

    session.add(entry)
    session.commit()
    session.refresh(entry)

    return _to_response(entry)


def get_medication(
        profile_id: int,
        medication_id: int,
        current_user: User,
        session: Session,
) -> MedicationResponse:
    """
    Return one medication entry from an accessible profile.
    """
    get_profile_access_role(
        account_id=current_user.id,
        profile_id=profile_id,
        session=session,
    )
    entry = _get_existing_medication(
        profile_id=profile_id,
        medication_id=medication_id,
        session=session,
    )

    return _to_response(entry)


def update_medication(
        profile_id: int,
        medication_id: int,
        request: MedicationUpdateRequest,
        current_user: User,
        session: Session,
) -> MedicationResponse:
    """
    Patch one medication entry if the account may edit its profile.
    """
    require_profile_role(
        account_id=current_user.id,
        profile_id=profile_id,
        allowed_roles=EDIT_ROLES,
        session=session,
    )
    entry = _get_existing_medication(
        profile_id=profile_id,
        medication_id=medication_id,
        session=session,
    )

    update_data = request.model_dump(exclude_unset=True, exclude={"catalog_item"})

    for field_name, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(entry, field_name, value)

    if "catalog_item" in request.model_fields_set:
        _apply_catalog_item(entry, request.catalog_item)

    _validate_second_intake_pair(
        entry.second_intake_hour,
        entry.second_intake_minute,
    )
    _ensure_medication_is_not_duplicate(
        profile_id=profile_id,
        name=entry.name,
        dose=entry.dose,
        intake_hour=entry.intake_hour,
        intake_minute=entry.intake_minute,
        second_intake_hour=entry.second_intake_hour,
        second_intake_minute=entry.second_intake_minute,
        frequency=entry.frequency,
        session=session,
        excluded_medication_id=entry.id,
    )

    entry.updated_at = datetime.utcnow()

    session.add(entry)
    session.commit()
    session.refresh(entry)

    return _to_response(entry)


def delete_medication(
        profile_id: int,
        medication_id: int,
        current_user: User,
        session: Session,
) -> MedicationDeleteResponse:
    """
    Soft-delete one medication entry if the account may edit its profile.
    """
    require_profile_role(
        account_id=current_user.id,
        profile_id=profile_id,
        allowed_roles=EDIT_ROLES,
        session=session,
    )
    entry = _get_existing_medication(
        profile_id=profile_id,
        medication_id=medication_id,
        session=session,
    )

    entry.deleted_at = datetime.utcnow()
    entry.updated_at = datetime.utcnow()

    session.add(entry)
    session.commit()

    return MedicationDeleteResponse(message="Medication deleted successfully.")


def _get_existing_medication(
        profile_id: int,
        medication_id: int,
        session: Session,
) -> MedicationEntry:
    """
    Return a non-deleted medication entry scoped to the requested profile.
    """
    entry = session.exec(
        select(MedicationEntry)
        .where(MedicationEntry.id == medication_id)
        .where(MedicationEntry.profile_id == profile_id)
        .where(MedicationEntry.deleted_at.is_(None))
    ).first()

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found.",
        )

    return entry


def _validate_second_intake_pair(
        second_intake_hour: int | None,
        second_intake_minute: int | None,
) -> None:
    """
    Ensure second intake time is either complete or entirely absent.
    """
    if (second_intake_hour is None) != (second_intake_minute is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Second intake time must include both hour and minute.",
        )


def _ensure_medication_is_not_duplicate(
        profile_id: int,
        name: str,
        dose: str,
        intake_hour: int,
        intake_minute: int,
        second_intake_hour: int | None,
        second_intake_minute: int | None,
        frequency: str,
        session: Session,
        excluded_medication_id: int | None = None,
) -> None:
    """
    Prevent duplicate active medication schedules within one profile.
    """
    normalized_name = name.strip().casefold()
    normalized_dose = dose.strip().casefold()

    entries = session.exec(
        select(MedicationEntry)
        .where(MedicationEntry.profile_id == profile_id)
        .where(MedicationEntry.deleted_at.is_(None))
    ).all()

    for entry in entries:
        if excluded_medication_id is not None and entry.id == excluded_medication_id:
            continue

        if (
            entry.name.strip().casefold() == normalized_name
            and entry.dose.strip().casefold() == normalized_dose
            and entry.intake_hour == intake_hour
            and entry.intake_minute == intake_minute
            and entry.second_intake_hour == second_intake_hour
            and entry.second_intake_minute == second_intake_minute
            and entry.frequency == frequency
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Medication already exists for this profile.",
            )


def _apply_catalog_item(
        entry: MedicationEntry,
        catalog_item: MedicationCatalogItemRequest | None,
) -> None:
    """
    Copy optional catalog metadata onto the flat database model.
    """
    if catalog_item is None:
        entry.catalog_item_id = None
        entry.catalog_item_name = None
        entry.catalog_active_substance = None
        entry.catalog_strength = None
        entry.catalog_dosage_form = None
        return

    entry.catalog_item_id = catalog_item.id
    entry.catalog_item_name = catalog_item.name
    entry.catalog_active_substance = catalog_item.active_substance
    entry.catalog_strength = catalog_item.strength
    entry.catalog_dosage_form = catalog_item.dosage_form


def _to_response(entry: MedicationEntry) -> MedicationResponse:
    """
    Map the database row to the public API shape.
    """
    catalog_item = None

    if entry.catalog_item_id is not None:
        catalog_item = MedicationCatalogItemResponse(
            id=entry.catalog_item_id,
            name=entry.catalog_item_name or "",
            active_substance=entry.catalog_active_substance or "",
            strength=entry.catalog_strength or "",
            dosage_form=entry.catalog_dosage_form or "",
        )

    return MedicationResponse(
        id=entry.id,
        profile_id=entry.profile_id,
        name=entry.name,
        dose=entry.dose,
        intake_hour=entry.intake_hour,
        intake_minute=entry.intake_minute,
        second_intake_hour=entry.second_intake_hour,
        second_intake_minute=entry.second_intake_minute,
        frequency=entry.frequency,
        reminders_enabled=entry.reminders_enabled,
        taken_date_keys=entry.taken_date_keys,
        catalog_item=catalog_item,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )
