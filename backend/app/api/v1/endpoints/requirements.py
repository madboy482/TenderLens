from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.requirement import Requirement
from app.db.models.workspace import Workspace
from app.db.session import get_db
from app.schemas.requirement import RequirementResponse, RequirementUpdate

router = APIRouter(prefix="/workspaces", tags=["requirements"])
requirement_router = APIRouter(prefix="/requirements", tags=["requirements"])


@router.get("/{workspace_id}/requirements", response_model=list[RequirementResponse])
def list_requirements(workspace_id: str, db: Session = Depends(get_db)) -> list[Requirement]:
    if db.get(Workspace, workspace_id) is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    return list(
        db.query(Requirement)
        .filter(Requirement.workspace_id == workspace_id)
        .order_by(Requirement.source_page_start, Requirement.created_at)
        .all()
    )


@requirement_router.patch("/{requirement_id}", response_model=RequirementResponse)
def update_requirement(
    requirement_id: str,
    payload: RequirementUpdate,
    db: Session = Depends(get_db),
) -> Requirement:
    requirement = db.get(Requirement, requirement_id)
    if requirement is None:
        raise HTTPException(status_code=404, detail="Requirement not found.")
    changes = payload.model_dump(exclude_unset=True)
    if "confirmed_status" in changes and changes["confirmed_status"] is not None:
        requirement.review_required = False
    for field, value in changes.items():
        setattr(requirement, field, value)
    db.commit()
    db.refresh(requirement)
    return requirement
