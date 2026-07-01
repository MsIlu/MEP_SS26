"""Business logic and authorization checks for profile-scoped documents."""

import base64
import binascii
from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import Session, select

from database.models import DocumentEntry, User
from documents.schemas import (
    DocumentCreateRequest,
    DocumentDeleteResponse,
    DocumentMetadataResponse,
    DocumentResponse,
    DocumentUpdateRequest,
)
from profiles.service import EDIT_ROLES, get_profile_access_role, require_profile_role

MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png"}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def list_documents(
        profile_id: int,
        current_user: User,
        session: Session,
) -> list[DocumentMetadataResponse]:
    """Return all non-deleted documents for an accessible profile."""
    get_profile_access_role(
        account_id=current_user.id,
        profile_id=profile_id,
        session=session,
    )

    entries = session.exec(
        select(DocumentEntry)
        .where(DocumentEntry.profile_id == profile_id)
        .where(DocumentEntry.deleted_at.is_(None))
        .order_by(DocumentEntry.created_at.desc(), DocumentEntry.id.desc())
    ).all()

    return [_to_metadata_response(entry) for entry in entries]


def create_document(
        profile_id: int,
        request: DocumentCreateRequest,
        current_user: User,
        session: Session,
) -> DocumentResponse:
    """Create a document entry for a profile if the account may edit it."""
    require_profile_role(
        account_id=current_user.id,
        profile_id=profile_id,
        allowed_roles=EDIT_ROLES,
        session=session,
    )
    file_data_base64, decoded_size = _validate_file_payload(request)

    entry = DocumentEntry(
        profile_id=profile_id,
        name=request.name.strip(),
        category=request.category,
        source=request.source,
        size_in_bytes=decoded_size,
        mime_type=request.mime_type.strip(),
        file_data_base64=file_data_base64,
        created_at=request.created_at or datetime.utcnow(),
    )

    session.add(entry)
    session.commit()
    session.refresh(entry)

    return _to_response(entry)


def get_document(
        profile_id: int,
        document_id: int,
        current_user: User,
        session: Session,
) -> DocumentResponse:
    """Return one document from an accessible profile."""
    get_profile_access_role(
        account_id=current_user.id,
        profile_id=profile_id,
        session=session,
    )
    entry = _get_existing_document(
        profile_id=profile_id,
        document_id=document_id,
        session=session,
    )

    return _to_response(entry)


def update_document(
        profile_id: int,
        document_id: int,
        request: DocumentUpdateRequest,
        current_user: User,
        session: Session,
) -> DocumentResponse:
    """Patch editable document metadata if the account may edit its profile."""
    require_profile_role(
        account_id=current_user.id,
        profile_id=profile_id,
        allowed_roles=EDIT_ROLES,
        session=session,
    )
    entry = _get_existing_document(
        profile_id=profile_id,
        document_id=document_id,
        session=session,
    )

    update_data = request.model_dump(exclude_unset=True)

    for field_name, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(entry, field_name, value)

    entry.updated_at = datetime.utcnow()

    session.add(entry)
    session.commit()
    session.refresh(entry)

    return _to_response(entry)


def delete_document(
        profile_id: int,
        document_id: int,
        current_user: User,
        session: Session,
) -> DocumentDeleteResponse:
    """Soft-delete one document if the account may edit its profile."""
    require_profile_role(
        account_id=current_user.id,
        profile_id=profile_id,
        allowed_roles=EDIT_ROLES,
        session=session,
    )
    entry = _get_existing_document(
        profile_id=profile_id,
        document_id=document_id,
        session=session,
    )

    entry.deleted_at = datetime.utcnow()
    entry.updated_at = datetime.utcnow()

    session.add(entry)
    session.commit()

    return DocumentDeleteResponse(message="Das Dokument wurde erfolgreich entfernt.")


def _get_existing_document(
        profile_id: int,
        document_id: int,
        session: Session,
) -> DocumentEntry:
    """Return a non-deleted document scoped to the requested profile."""
    entry = session.exec(
        select(DocumentEntry)
        .where(DocumentEntry.id == document_id)
        .where(DocumentEntry.profile_id == profile_id)
        .where(DocumentEntry.deleted_at.is_(None))
    ).first()

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dieses Dokument wurde nicht gefunden.",
        )

    return entry


def _to_response(entry: DocumentEntry) -> DocumentResponse:
    """Map the database row to the public API shape."""
    return DocumentResponse(
        id=entry.id,
        profile_id=entry.profile_id,
        name=entry.name,
        category=entry.category,
        source=entry.source,
        size_in_bytes=entry.size_in_bytes,
        mime_type=entry.mime_type,
        file_data_base64=entry.file_data_base64,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


def _to_metadata_response(entry: DocumentEntry) -> DocumentMetadataResponse:
    """Map the database row to metadata without the stored file body."""
    return DocumentMetadataResponse(
        id=entry.id,
        profile_id=entry.profile_id,
        name=entry.name,
        category=entry.category,
        source=entry.source,
        size_in_bytes=entry.size_in_bytes,
        mime_type=entry.mime_type,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


def _validate_file_payload(request: DocumentCreateRequest) -> tuple[str, int]:
    """Validate base64 payload and enforce backend file size rules."""
    mime_type = request.mime_type.strip().lower()

    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dieser Dateityp wird nicht unterstützt.",
        )

    file_data_base64 = request.file_data_base64.strip()
    if not file_data_base64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Die Datei enthält keine gültigen Daten.",
        )

    try:
        decoded = base64.b64decode(file_data_base64, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Die Datei enthält keine gültigen Daten.",
        ) from None

    decoded_size = len(decoded)
    if decoded_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Die Datei enthält keine gültigen Daten.",
        )

    if not _matches_mime_type(decoded, mime_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Die Datei enthält keine gültigen Daten.",
        )

    if decoded_size > MAX_DOCUMENT_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Die Datei darf maximal 10 MB groß sein.",
        )

    if request.size_in_bytes != decoded_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Die angegebene Dateigröße stimmt nicht mit den Dateidaten überein.",
        )

    return file_data_base64, decoded_size


def _matches_mime_type(decoded: bytes, mime_type: str) -> bool:
    if mime_type == "application/pdf":
        return decoded.startswith(b"%PDF-")
    if mime_type == "image/jpeg":
        return decoded.startswith(b"\xff\xd8\xff")
    if mime_type == "image/png":
        return decoded.startswith(PNG_SIGNATURE)
    return False
