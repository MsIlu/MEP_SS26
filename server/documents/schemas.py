"""Request and response schemas for profile-scoped documents."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


DocumentCategory = Literal["findings", "laboratory", "recommendations", "other"]
DocumentSource = Literal["uploaded", "careena"]


class DocumentCreateRequest(BaseModel):
    """Request body for creating a document entry."""

    name: str = Field(min_length=1, max_length=255)
    category: DocumentCategory = "other"
    source: DocumentSource = "uploaded"
    size_in_bytes: int = Field(default=0, ge=0)
    mime_type: str = Field(default="application/pdf", min_length=1, max_length=120)
    file_data_base64: str = ""
    created_at: Optional[datetime] = None


class DocumentUpdateRequest(BaseModel):
    """Request body for updating editable document metadata."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    category: Optional[DocumentCategory] = None


class DocumentResponse(BaseModel):
    """Document entry returned to the frontend."""

    id: int
    profile_id: int
    name: str
    category: DocumentCategory
    source: DocumentSource
    size_in_bytes: int
    mime_type: str
    file_data_base64: str
    created_at: datetime
    updated_at: datetime


class DocumentMetadataResponse(BaseModel):
    """Document metadata returned in list views without file payload."""

    id: int
    profile_id: int
    name: str
    category: DocumentCategory
    source: DocumentSource
    size_in_bytes: int
    mime_type: str
    created_at: datetime
    updated_at: datetime


class DocumentDeleteResponse(BaseModel):
    """Response body returned after a document has been soft-deleted."""

    message: str