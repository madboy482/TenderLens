from pydantic import BaseModel, ConfigDict


class ReportRequirement(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    requirement_id: str
    source_page: int
    category: str
    requirement_text: str
    mandatory_status: str
    requirement_status: str
    evidence_status: str
    evidence_document: str | None
    evidence_page: int | None
    rule_reason: str | None
    review_required: bool
    review_note: str | None


class ComplianceSummary(BaseModel):
    workspace_id: str
    workspace_title: str
    total_requirements: int
    compliant: int
    needs_review: int
    gaps: int
    not_assessed: int
    rows: list[ReportRequirement]
