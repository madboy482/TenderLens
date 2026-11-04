from io import BytesIO
from pathlib import Path

import pymupdf
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from starlette.datastructures import UploadFile

from app.core.config import Settings
from app.db.session import get_db
from app.db.base import Base
from app.db.models.requirement import Requirement
from app.db.models.workspace import Workspace
from app.services.document_service import ingest_pdf
from app.services.evidence_service import retrieve_evidence
from app.main import app


def make_pdf(text: str) -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


@pytest.mark.asyncio
async def test_evidence_upload_and_retrieval_preserve_source_page(tmp_path: Path) -> None:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    settings = Settings(storage_root=str(tmp_path), database_url="sqlite://")

    with Session(engine) as db:
        workspace = Workspace(title="Evidence test")
        db.add(workspace)
        db.flush()
        tender = await ingest_pdf(
            db,
            workspace,
            UploadFile(
                BytesIO(make_pdf("The bidder must submit a valid GST certificate.")),
                filename="tender.pdf",
            ),
            settings,
            kind="tender",
        )
        evidence = await ingest_pdf(
            db,
            workspace,
            UploadFile(
                BytesIO(make_pdf("GST certificate number GST-123 is valid.")),
                filename="gst.pdf",
            ),
            settings,
            kind="evidence",
        )
        requirement = db.query(Requirement).filter(Requirement.source_document_id == tender.id).one()

        matches = retrieve_evidence(db, requirement)

        assert evidence.kind == "evidence"
        assert len(matches) == 1
        assert matches[0].evidence_document_id == evidence.id
        assert matches[0].evidence_chunk.page_start == 1
        assert matches[0].suggested_status == "evidence_found"


@pytest.mark.asyncio
async def test_evidence_match_can_be_reviewed(tmp_path: Path) -> None:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'evidence-review.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    settings = Settings(storage_root=str(tmp_path), database_url="sqlite://")

    with Session(engine) as db:
        workspace = Workspace(title="Evidence review test")
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

        def override_db():
            yield db

        app.dependency_overrides[get_db] = override_db
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.patch(
                    f"/api/v1/evidence-matches/{match.id}",
                    json={"user_status": "accepted", "review_note": "Verified against certificate."},
                )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        assert response.json()["user_status"] == "accepted"
        assert response.json()["review_note"] == "Verified against certificate."
        assert response.json()["suggested_status"] == "evidence_found"
