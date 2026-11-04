from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.workspace import Workspace
from app.db.session import get_db
from app.schemas.workspace import (
    DocumentDetailResponse,
    DocumentResponse,
    WorkspaceCreate,
    WorkspaceResponse,
)
from app.services.document_service import DocumentServiceError, ingest_pdf

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(payload: WorkspaceCreate, db: Session = Depends(get_db)) -> Workspace:
    workspace = Workspace(**payload.model_dump())
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


@router.get("", response_model=list[WorkspaceResponse])
def list_workspaces(db: Session = Depends(get_db)) -> list[Workspace]:
    return list(db.query(Workspace).order_by(Workspace.created_at.desc()).all())


@router.post(
    "/{workspace_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_tender(
    workspace_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    workspace = db.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    try:
        return await ingest_pdf(db, workspace, file, get_settings(), kind="tender")
    except DocumentServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/{workspace_id}/evidence",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_evidence(
    workspace_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    workspace = db.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    try:
        return await ingest_pdf(db, workspace, file, get_settings(), kind="evidence")
    except DocumentServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/{workspace_id}/amendments",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_amendment(
    workspace_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    workspace = db.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    try:
        return await ingest_pdf(db, workspace, file, get_settings(), kind="amendment")
    except DocumentServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
