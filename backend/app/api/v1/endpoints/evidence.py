from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.evidence_match import EvidenceMatch
from app.db.models.requirement import Requirement
from app.db.session import get_db
from app.schemas.evidence import EvidenceMatchResponse, EvidenceMatchUpdate
from app.services.evidence_service import retrieve_evidence

router = APIRouter(prefix="/requirements", tags=["evidence"])
match_router = APIRouter(prefix="/evidence-matches", tags=["evidence"])


def to_response(match: EvidenceMatch) -> EvidenceMatchResponse:
    return EvidenceMatchResponse(
        id=match.id,
        requirement_id=match.requirement_id,
        evidence_document_id=match.evidence_document_id,
        evidence_chunk_id=match.evidence_chunk_id,
        retrieval_score=match.retrieval_score,
        matched_terms=match.matched_terms,
        suggested_status=match.suggested_status,
        rule_reason=match.rule_reason,
        user_status=match.user_status,
        review_note=match.review_note,
        created_at=match.created_at,
        evidence_document_name=match.evidence_document.original_name,
        evidence_page_start=match.evidence_chunk.page_start,
        evidence_snippet=match.evidence_chunk.chunk_text,
    )


@router.post("/{requirement_id}/match-evidence", response_model=list[EvidenceMatchResponse])
def match_evidence(requirement_id: str, db: Session = Depends(get_db)) -> list[EvidenceMatchResponse]:
    requirement = db.get(Requirement, requirement_id)
    if requirement is None:
        raise HTTPException(status_code=404, detail="Requirement not found.")
    matches = retrieve_evidence(db, requirement)
    return [to_response(match) for match in matches]


@match_router.patch("/{match_id}", response_model=EvidenceMatchResponse)
def update_evidence_match(
    match_id: str,
    payload: EvidenceMatchUpdate,
    db: Session = Depends(get_db),
) -> EvidenceMatchResponse:
    match = db.get(EvidenceMatch, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Evidence match not found.")
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="At least one review field is required.")
    for field, value in changes.items():
        setattr(match, field, value)
    db.commit()
    db.refresh(match)
    return to_response(match)
