from io import BytesIO
from pathlib import Path

import pymupdf
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from starlette.datastructures import UploadFile

from app.core.config import Settings
from app.db.base import Base
from app.db.models.requirement import Requirement
from app.db.models.workspace import Workspace
from app.services.document_service import ingest_pdf
from app.services.evidence_service import retrieve_evidence
from app.services.report_service import build_summary, render_pdf


def make_pdf(text: str) -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


@pytest.mark.asyncio
async def test_report_preserves_reviewable_compliance_statuses(tmp_path: Path) -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    settings = Settings(storage_root=str(tmp_path), database_url="sqlite://")

    with Session(engine) as db:
        workspace = Workspace(title="Report test")
        db.add(workspace)
        db.flush()
        tender = await ingest_pdf(
            db,
            workspace,
            UploadFile(BytesIO(make_pdf("The bidder must submit a valid GST certificate.")), filename="tender.pdf"),
            settings,
            kind="tender",
        )
        await ingest_pdf(
            db,
            workspace,
            UploadFile(BytesIO(make_pdf("GST certificate number GST-123 is valid.")), filename="gst.pdf"),
            settings,
            kind="evidence",
        )
        requirement = db.query(Requirement).filter(Requirement.source_document_id == tender.id).one()
        match = retrieve_evidence(db, requirement)[0]
        match.user_status = "accepted"
        requirement.review_required = False
        db.commit()

        report = build_summary(db, workspace.id)

        assert report is not None
        assert report.total_requirements == 1
        assert report.compliant == 1
        assert report.rows[0].evidence_status == "accepted"
        assert report.rows[0].evidence_document == "gst.pdf"
        pdf = render_pdf(report)
        assert pdf.startswith(b"%PDF-")
