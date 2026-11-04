from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.db.models.document import Document
from app.db.session import get_db
from app.schemas.workspace import DocumentDetailResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(document_id: str, db: Session = Depends(get_db)) -> Document:
    document = (
        db.query(Document)
        .options(selectinload(Document.pages), selectinload(Document.chunks))
        .filter(Document.id == document_id)
        .first()
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document
