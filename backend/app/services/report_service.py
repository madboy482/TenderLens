from sqlalchemy.orm import Session
import pymupdf

from app.db.models.requirement import Requirement
from app.db.models.workspace import Workspace
from app.schemas.report import ComplianceSummary, ReportRequirement


def _status(requirement: Requirement) -> tuple[str, str, str | None, str | None, int | None]:
    matches = list(requirement.evidence_matches)
    accepted = next((match for match in matches if match.user_status == "accepted"), None)
    selected = accepted or (matches[0] if matches else None)
    evidence_status = selected.user_status or selected.suggested_status if selected else "not_assessed"
    if accepted:
        requirement_status = "compliant"
    elif requirement.suggested_status == "re_review_required":
        requirement_status = "needs_review"
    elif selected and selected.suggested_status == "evidence_found":
        requirement_status = "compliant" if not requirement.review_required else "needs_review"
    elif selected and selected.user_status == "rejected":
        requirement_status = "gap"
    elif selected:
        requirement_status = "needs_review"
    else:
        requirement_status = "needs_review" if requirement.review_required else "not_assessed"
    return (
        requirement_status,
        evidence_status,
        selected.rule_reason if selected else None,
        selected.evidence_document.original_name if selected else None,
        selected.evidence_chunk.page_start if selected else None,
    )


def build_summary(db: Session, workspace_id: str) -> ComplianceSummary | None:
    workspace = db.get(Workspace, workspace_id)
    if workspace is None:
        return None
    requirements = (
        db.query(Requirement)
        .filter(Requirement.workspace_id == workspace_id)
        .order_by(Requirement.source_page_start, Requirement.created_at)
        .all()
    )
    rows: list[ReportRequirement] = []
    for requirement in requirements:
        status, evidence_status, reason, document_name, evidence_page = _status(requirement)
        rows.append(
            ReportRequirement(
                requirement_id=requirement.id,
                source_page=requirement.source_page_start,
                category=requirement.category,
                requirement_text=requirement.normalized_text,
                mandatory_status=requirement.mandatory_status,
                requirement_status=status,
                evidence_status=evidence_status,
                evidence_document=document_name,
                evidence_page=evidence_page,
                rule_reason=reason,
                review_required=requirement.review_required,
                review_note=requirement.review_note,
            )
        )
    counts = {status: sum(row.requirement_status == status for row in rows) for status in (
        "compliant", "needs_review", "gap", "not_assessed"
    )}
    return ComplianceSummary(
        workspace_id=workspace.id,
        workspace_title=workspace.title,
        total_requirements=len(rows),
        compliant=counts["compliant"],
        needs_review=counts["needs_review"],
        gaps=counts["gap"],
        not_assessed=counts["not_assessed"],
        rows=rows,
    )


def render_pdf(report: ComplianceSummary) -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    margin = 48
    width = page.rect.width - (margin * 2)
    y = margin

    def add_text(text: str, size: float = 10, bold: bool = False) -> None:
        nonlocal page, y
        font = "hebo" if bold else "helv"
        for line in text.splitlines() or [""]:
            if y > page.rect.height - 55:
                page = document.new_page()
                y = margin
            page.insert_text((margin, y), line[:140], fontsize=size, fontname=font)
            y += size + 6

    add_text("TenderLens Compliance Report", size=18, bold=True)
    add_text(report.workspace_title, size=12)
    add_text(
        f"Compliant: {report.compliant} | Needs review: {report.needs_review} | "
        f"Gaps: {report.gaps} | Not assessed: {report.not_assessed}",
        size=10,
    )
    y += 8
    for index, row in enumerate(report.rows, start=1):
        add_text(f"{index}. {row.requirement_status.upper()} | Page {row.source_page} | {row.category}", bold=True)
        add_text(row.requirement_text)
        evidence = row.evidence_document or "No evidence selected"
        add_text(f"Evidence: {evidence} | Status: {row.evidence_status}")
        if row.rule_reason:
            add_text(f"Reason: {row.rule_reason}")
        if row.review_note:
            add_text(f"Review note: {row.review_note}")
        y += 6
    content = document.tobytes()
    document.close()
    return content
