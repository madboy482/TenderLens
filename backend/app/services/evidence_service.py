from sqlalchemy.orm import Session

from app.db.models.document import Document
from app.db.models.evidence_match import EvidenceMatch
from app.db.models.requirement import Requirement
from app.nlp.retrieval import score_match
from app.nlp.rules_engine import evaluate_evidence


def retrieve_evidence(
    db: Session, requirement: Requirement, limit: int = 5
) -> list[EvidenceMatch]:
    candidates: list[tuple[float, Document, object, tuple[str, ...]]] = []
    evidence_documents = (
        db.query(Document)
        .filter(
            Document.workspace_id == requirement.workspace_id,
            Document.kind == "evidence",
        )
        .all()
    )
    for document in evidence_documents:
        for chunk in document.chunks:
            result = score_match(requirement.normalized_text, chunk.chunk_text)
            if result.score > 0:
                candidates.append((result.score, document, chunk, result.matched_terms))
    candidates.sort(key=lambda item: item[0], reverse=True)
    db.query(EvidenceMatch).filter(EvidenceMatch.requirement_id == requirement.id).delete()
    matches = [
        EvidenceMatch(
            requirement=requirement,
            evidence_document=document,
            evidence_chunk=chunk,
            retrieval_score=score,
            matched_terms=", ".join(terms),
            suggested_status=(
                evaluate_evidence(
                    requirement.normalized_text,
                    chunk.chunk_text,
                    required_amount=(
                        float(requirement.normalized_value)
                        if requirement.normalized_value is not None
                        else None
                    ),
                ).status
                if score >= 0.5
                else "needs_review"
            ),
            rule_reason=(
                evaluate_evidence(
                    requirement.normalized_text,
                    chunk.chunk_text,
                    required_amount=(
                        float(requirement.normalized_value)
                        if requirement.normalized_value is not None
                        else None
                    ),
                ).reason
                if score >= 0.5
                else "Retrieval signal is below the confident matching threshold."
            ),
        )
        for score, document, chunk, terms in candidates[:limit]
    ]
    db.add_all(matches)
    db.commit()
    for match in matches:
        db.refresh(match)
    return matches
