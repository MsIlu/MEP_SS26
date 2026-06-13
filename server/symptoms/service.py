from datetime import datetime

from sqlmodel import Session, select

from database.models import SymptomDiaryEntry, User
from profiles.service import EDIT_ROLES, get_profile_access_role, require_profile_role
from symptoms.schemas import SymptomCreateRequest, SymptomResponse


def create_symptom_entry(
        profile_id: int,
        request: SymptomCreateRequest,
        current_user: User,
        session: Session,
) -> SymptomResponse:
    """
    Create one symptom diary entry for a profile the account can edit.
    """
    require_profile_role(
        account_id=current_user.id,
        profile_id=profile_id,
        allowed_roles=EDIT_ROLES,
        session=session,
    )

    entry = SymptomDiaryEntry(
        profile_id=profile_id,
        date=request.date,
        symptom=request.symptom.strip(),
        body_area=request.body_area.strip(),
        intensity=request.intensity,
        note=request.note.strip(),
        created_at=request.created_at or datetime.utcnow(),
    )

    session.add(entry)
    session.commit()
    session.refresh(entry)

    return SymptomResponse.model_validate(entry)


def list_symptom_entries(
        profile_id: int,
        current_user: User,
        session: Session,
) -> list[SymptomResponse]:
    """
    Return all symptom diary entries for a profile the account can access.
    """
    get_profile_access_role(
        account_id=current_user.id,
        profile_id=profile_id,
        session=session,
    )

    entries = session.exec(
        select(SymptomDiaryEntry)
        .where(SymptomDiaryEntry.profile_id == profile_id)
        .order_by(SymptomDiaryEntry.date.desc(), SymptomDiaryEntry.created_at.desc())
    ).all()

    return [SymptomResponse.model_validate(entry) for entry in entries]
