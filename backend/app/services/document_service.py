from pathlib import Path
from uuid import uuid4

import pymupdf
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models.document import Document, DocumentPage
from app.db.models.text_chunk import TextChunk
from app.db.models.requirement import Requirement
from app.db.models.workspace import Workspace
from app.nlp.chunking import split_page_text
from app.nlp.clause_candidates import find_candidate_clauses


class DocumentServiceError(ValueError):
    pass


async def ingest_pdf(
    db: Session,
    workspace: Workspace,
    upload: UploadFile,
    settings: Settings,
    kind: str = "tender",
) -> Document:
    original_name = Path(upload.filename or "").name
    if not original_name.lower().endswith(".pdf"):
        raise DocumentServiceError("Only PDF files are supported for document upload.")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    content = await upload.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise DocumentServiceError(
            f"File exceeds the configured {settings.max_upload_mb} MB limit."
        )
    if not content.startswith(b"%PDF-"):
        raise DocumentServiceError("The uploaded file is not a valid PDF.")

    storage_root = Path(settings.storage_root)
    storage_root.mkdir(parents=True, exist_ok=True)
    storage_key = f"{uuid4()}.pdf"
    storage_path = storage_root / storage_key
    storage_path.write_bytes(content)

    warnings: list[str] = []
    pages: list[DocumentPage] = []
    try:
        pdf = pymupdf.open(stream=content, filetype="pdf")
        if pdf.page_count == 0:
            raise DocumentServiceError("The uploaded PDF contains no pages.")
        for index, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()
            status = "extracted" if text else "needs_ocr"
            if not text:
                warnings.append(f"Page {index} contains little or no extractable text; OCR may be required.")
            pages.append(
                DocumentPage(
                    page_number=index,
                    extracted_text=text,
                    extraction_status=status,
                )
            )
        page_count = pdf.page_count
        pdf.close()
    except DocumentServiceError:
        storage_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        storage_path.unlink(missing_ok=True)
        raise DocumentServiceError("The PDF could not be parsed.") from exc

    document = Document(
        workspace=workspace,
        kind=kind,
        original_name=original_name,
        storage_key=storage_key,
        mime_type="application/pdf",
        page_count=page_count,
        processing_status="completed",
        warnings=warnings,
        pages=pages,
    )
    all_chunks = [
        chunk
        for page in pages
        for chunk in split_page_text(page.page_number, page.extracted_text)
    ]
    candidate_ids = {
        (candidate.page_start, candidate.page_end, candidate.text)
        for candidate in find_candidate_clauses(all_chunks)
    }
    document.chunks = [
        TextChunk(
            page_start=chunk.page_start,
            page_end=chunk.page_end,
            chunk_text=chunk.text,
            chunk_type=(
                "candidate_clause"
                if (chunk.page_start, chunk.page_end, chunk.text) in candidate_ids
                else "page_text"
            ),
        )
        for chunk in all_chunks
    ]
    for chunk in document.chunks:
        if kind != "tender":
            continue
        if chunk.chunk_type != "candidate_clause":
            continue
        from app.nlp.requirement_extraction import extract_requirement

        extracted = extract_requirement(chunk.chunk_text)
        if extracted is not None:
            db.add(
                Requirement(
                    workspace=workspace,
                    source_document=document,
                    source_chunk=chunk,
                    source_page_start=chunk.page_start,
                    source_page_end=chunk.page_end,
                    source_clause_text=chunk.chunk_text,
                    normalized_text=extracted.normalized_text,
                    category=extracted.category,
                    requirement_type=extracted.requirement_type,
                    mandatory_status=extracted.mandatory_status,
                    extracted_value=extracted.extracted_value,
                    normalized_value=extracted.normalized_value,
                    unit=extracted.unit,
                    conditions=extracted.conditions,
                    extraction_method="rule",
                    confidence=extracted.confidence,
                    review_required=True,
                    suggested_status="needs_review",
                )
            )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document
