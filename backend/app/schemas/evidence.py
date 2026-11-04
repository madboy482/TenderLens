from datetime import datetime

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EvidenceMatchUpdate(BaseModel):
    user_status: Literal["accepted", "rejected", "needs_review"] | None = None
    review_note: str | None = Field(default=None, max_length=2000)


class EvidenceMatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    requirement_id: str
    evidence_document_id: str
    evidence_chunk_id: str
    retrieval_score: float
    matched_terms: str | None
    suggested_status: str
    rule_reason: str | None
    user_status: str | None
    review_note: str | None
    created_at: datetime
    evidence_document_name: str
    evidence_page_start: int
    evidence_snippet: str
