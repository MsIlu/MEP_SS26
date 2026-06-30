"""HTTP routes for profile-scoped document entries."""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from auth.security import get_current_account, get_session
from database.models import User
from documents.schemas import (
    DocumentCreateRequest,
    DocumentDeleteResponse,
    DocumentResponse,
    DocumentUpdateRequest,
)
from documents.service import (
    create_document,
    delete_document,
    get_document,
    list_documents,
    update_document,
)


router = APIRouter(
    prefix="/profiles/{profile_id}/documents",
    tags=["documents"],
)


@router.get("", response_model=list[DocumentResponse])
def get_profile_documents(
        profile_id: int,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """Return documents for one accessible medical profile."""
    return list_documents(
        profile_id=profile_id,
        current_user=current_user,
        session=session,
    )


@router.post("", response_model=DocumentResponse)
def post_profile_document(
        profile_id: int,
        request: DocumentCreateRequest,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """Create one document for a medical profile."""
    return create_document(
        profile_id=profile_id,
        request=request,
        current_user=current_user,
        session=session,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_profile_document_by_id(
        profile_id: int,
        document_id: int,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """Return one document from a medical profile."""
    return get_document(
        profile_id=profile_id,
        document_id=document_id,
        current_user=current_user,
        session=session,
    )


@router.patch("/{document_id}", response_model=DocumentResponse)
def patch_profile_document(
        profile_id: int,
        document_id: int,
        request: DocumentUpdateRequest,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """Update one document from a medical profile."""
    return update_document(
        profile_id=profile_id,
        document_id=document_id,
        request=request,
        current_user=current_user,
        session=session,
    )


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
def remove_profile_document(
        profile_id: int,
        document_id: int,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """Soft-delete one document from a medical profile."""
    return delete_document(
        profile_id=profile_id,
        document_id=document_id,
        current_user=current_user,
        session=session,
    )
