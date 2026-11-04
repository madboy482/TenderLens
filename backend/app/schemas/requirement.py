from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RequirementUpdate(BaseModel):
    normalized_text: str | None = Field(default=None, min_length=1)
    category: str | None = None
    mandatory_status: str | None = None
    confirmed_status: str | None = None
    review_note: str | None = Field(default=None, max_length=2000)


class RequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    source_document_id: str
    source_chunk_id: str | None
    source_page_start: int
    source_page_end: int | None
    source_clause_text: str
    normalized_text: str
    category: str
    requirement_type: str
    mandatory_status: str
    extracted_value: str | None
    normalized_value: str | None
    unit: str | None
    conditions: str | None
    extraction_method: str
    confidence: float | None
    review_required: bool
    suggested_status: str
    confirmed_status: str | None
    review_note: str | None
    created_at: datetime
