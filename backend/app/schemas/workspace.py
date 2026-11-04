from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    tender_reference: str | None = Field(default=None, max_length=200)
    organization_label: str | None = Field(default=None, max_length=200)


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    tender_reference: str | None
    organization_label: str | None
    created_at: datetime
    updated_at: datetime


class DocumentPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    page_number: int
    extracted_text: str
    extraction_status: str


class TextChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    page_start: int
    page_end: int
    chunk_text: str
    chunk_type: str


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    kind: str
    original_name: str
    mime_type: str
    page_count: int
    processing_status: str
    warnings: list[str]
    created_at: datetime


class DocumentDetailResponse(DocumentResponse):
    pages: list[DocumentPageResponse]
    chunks: list[TextChunkResponse]
