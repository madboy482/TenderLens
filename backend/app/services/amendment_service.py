import json

from sqlalchemy.orm import Session

from app.db.models.amendment import AmendmentChange
from app.db.models.document import Document
from app.db.models.requirement import Requirement
from app.nlp.amendment_diff import compare_clauses
from app.nlp.retrieval import score_match


def compare_amendment(
    db: Session, workspace_id: str, original: Document, amendment: Document
) -> list[AmendmentChange]:
    original_clauses = [
        (chunk.page_start, chunk.chunk_text)
        for chunk in original.chunks
        if chunk.chunk_type == "candidate_clause"
    ]
    amendment_clauses = [
        (chunk.page_start, chunk.chunk_text)
        for chunk in amendment.chunks
        if chunk.chunk_type == "candidate_clause"
    ]
    requirements = db.query(Requirement).filter(Requirement.workspace_id == workspace_id).all()
    changes: list[AmendmentChange] = []
    for change in compare_clauses(original_clauses, amendment_clauses):
        affected = [
            requirement.id
            for requirement in requirements
            if (
                (change.new_text and score_match(requirement.normalized_text, change.new_text).score >= 0.25)
                or (change.old_text and score_match(requirement.normalized_text, change.old_text).score >= 0.25)
            )
        ]
        if affected:
            for requirement in requirements:
                if requirement.id in affected and change.change_type != "unchanged":
                    requirement.suggested_status = "re_review_required"
                    requirement.review_required = True
        changes.append(
            AmendmentChange(
                workspace_id=workspace_id,
                original_document_id=original.id,
                amendment_document_id=amendment.id,
                old_text=change.old_text,
                new_text=change.new_text,
                old_page=change.old_page,
                new_page=change.new_page,
                change_type=change.change_type,
                review_status="needs_review" if change.change_type != "unchanged" else "reviewed",
                affected_requirement_ids=json.dumps(affected),
            )
        )
    db.add_all(changes)
    db.commit()
    for change in changes:
        db.refresh(change)
    return changes
