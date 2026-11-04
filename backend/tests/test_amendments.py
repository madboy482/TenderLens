from io import BytesIO
from pathlib import Path

import pymupdf
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from starlette.datastructures import UploadFile

from app.core.config import Settings
from app.db.base import Base
from app.db.models.amendment import AmendmentChange
from app.db.models.requirement import Requirement
from app.db.models.workspace import Workspace
from app.services.amendment_service import compare_amendment
from app.services.document_service import ingest_pdf


def make_pdf(text: str) -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


@pytest.mark.asyncio
async def test_amendment_marks_changed_requirement_for_rereview(tmp_path: Path) -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    settings = Settings(storage_root=str(tmp_path), database_url="sqlite://")

    with Session(engine) as db:
        workspace = Workspace(title="Amendment test")
        db.add(workspace)
        db.flush()
        original = await ingest_pdf(
            db,
            workspace,
            UploadFile(
                BytesIO(make_pdf("The bidder must have turnover INR 5 lakh.")),
                filename="original.pdf",
            ),
            settings,
        )
        amendment = await ingest_pdf(
            db,
            workspace,
            UploadFile(
                BytesIO(make_pdf("The bidder must have turnover INR 10 lakh.")),
                filename="amendment.pdf",
            ),
            settings,
            kind="amendment",
        )
        requirement = db.query(Requirement).filter(Requirement.source_document_id == original.id).one()

        changes = compare_amendment(db, workspace.id, original, amendment)

        assert any(change.change_type == "changed" for change in changes)
        assert requirement.suggested_status == "re_review_required"
        assert requirement.review_required is True
        assert db.query(AmendmentChange).count() == 1
