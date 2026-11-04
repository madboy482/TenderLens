import csv
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.report import ComplianceSummary
from app.services.report_service import build_summary, render_pdf

router = APIRouter(prefix="/workspaces", tags=["reports"])


@router.get("/{workspace_id}/report", response_model=ComplianceSummary)
def get_report(workspace_id: str, db: Session = Depends(get_db)) -> ComplianceSummary:
    report = build_summary(db, workspace_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    return report


@router.get("/{workspace_id}/report.csv")
def download_report_csv(workspace_id: str, db: Session = Depends(get_db)) -> StreamingResponse:
    report = build_summary(db, workspace_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    output = StringIO()
    fields = [
        "requirement_id", "source_page", "category", "requirement_text",
        "mandatory_status", "requirement_status", "evidence_status",
        "evidence_document", "evidence_page", "rule_reason",
        "review_required", "review_note",
    ]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(row.model_dump() for row in report.rows)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{workspace_id}-compliance-report.csv"'
        },
    )


@router.get("/{workspace_id}/report.pdf")
def download_report_pdf(workspace_id: str, db: Session = Depends(get_db)) -> Response:
    report = build_summary(db, workspace_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    return Response(
        content=render_pdf(report),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{workspace_id}-compliance-report.pdf"'
        },
    )
