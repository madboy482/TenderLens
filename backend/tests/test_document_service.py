from pathlib import Path

import pymupdf
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.base import Base
from app.db.models.workspace import Workspace
from app.services.document_service import DocumentServiceError, ingest_pdf


def pdf_bytes(*texts: str) -> bytes:
    document = pymupdf.open()
    for text in texts:
        page = document.new_page()
        page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


@pytest.mark.asyncio
async def test_ingest_pdf_persists_pages_and_source_metadata(tmp_path: Path) -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    settings = Settings(storage_root=str(tmp_path), database_url="sqlite://")

    from starlette.datastructures import UploadFile
    from io import BytesIO

    with Session(engine) as db:
        workspace = Workspace(title="Test tender")
        db.add(workspace)
        db.flush()
        upload = UploadFile(
            BytesIO(pdf_bytes("Eligibility: GST certificate required.")),
            filename="tender.pdf",
        )

        document = await ingest_pdf(db, workspace, upload, settings)

        assert document.original_name == "tender.pdf"
        assert document.page_count == 1
        assert document.pages[0].page_number == 1
        assert "GST certificate" in document.pages[0].extracted_text
        assert document.processing_status == "completed"
        assert (tmp_path / document.storage_key).exists()
        assert len(document.chunks) == 1
        assert document.chunks[0].chunk_type == "candidate_clause"


@pytest.mark.asyncio
async def test_ingest_pdf_rejects_non_pdf(tmp_path: Path) -> None:
    from io import BytesIO
    from starlette.datastructures import UploadFile

    settings = Settings(storage_root=str(tmp_path), database_url="sqlite://")
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        workspace = Workspace(title="Test tender")
        db.add(workspace)
        db.flush()

        with pytest.raises(DocumentServiceError, match="Only PDF"):
            await ingest_pdf(
                db,
                workspace,
                UploadFile(BytesIO(b"not a pdf"), filename="evidence.txt"),
                settings,
            )


def test_candidate_chunk_detection_preserves_source_page() -> None:
    from app.nlp.chunking import split_page_text
    from app.nlp.clause_candidates import find_candidate_clauses

    chunks = split_page_text(
        4,
        "General information.\n\nThe bidder must submit a valid GST certificate.",
    )

    candidates = find_candidate_clauses(chunks)

    assert len(candidates) == 1
    assert candidates[0].page_start == 4
    assert "GST certificate" in candidates[0].text


def test_requirement_extraction_normalizes_clear_financial_clause() -> None:
    from app.nlp.requirement_extraction import extract_requirement

    requirement = extract_requirement(
        "The bidder must have an annual turnover of INR 5 lakh."
    )

    assert requirement is not None
    assert requirement.category == "financial"
    assert requirement.mandatory_status == "mandatory"
    assert requirement.normalized_value == "500000"
    assert requirement.unit == "INR"
