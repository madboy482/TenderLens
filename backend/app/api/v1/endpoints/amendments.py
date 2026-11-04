from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.document import Document
from app.db.session import get_db
from app.schemas.amendment import AmendmentChangeResponse
from app.services.amendment_service import compare_amendment

router = APIRouter(prefix="/workspaces", tags=["amendments"])


@router.post(
    "/{workspace_id}/compare-amendment",
    response_model=list[AmendmentChangeResponse],
)
def compare_workspace_amendment(
    workspace_id: str,
    original_document_id: str,
    amendment_document_id: str,
    db: Session = Depends(get_db),
) -> list[AmendmentChangeResponse]:
    original = db.get(Document, original_document_id)
    amendment = db.get(Document, amendment_document_id)
    if original is None or amendment is None:
        raise HTTPException(status_code=404, detail="Original or amendment document not found.")
    if original.workspace_id != workspace_id or amendment.workspace_id != workspace_id:
        raise HTTPException(status_code=400, detail="Documents must belong to the workspace.")
    if amendment.kind != "amendment":
        raise HTTPException(status_code=400, detail="The selected document is not an amendment.")
    return compare_amendment(db, workspace_id, original, amendment)
