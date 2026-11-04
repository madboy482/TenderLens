from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AmendmentChangeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_document_id: str
    amendment_document_id: str
    old_text: str | None
    new_text: str | None
    old_page: int | None
    new_page: int | None
    change_type: str
    review_status: str
    affected_requirement_ids: str | None
    created_at: datetime
