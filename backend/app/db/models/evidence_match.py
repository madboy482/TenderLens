from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EvidenceMatch(Base):
    __tablename__ = "evidence_matches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    requirement_id: Mapped[str] = mapped_column(ForeignKey("requirements.id"), index=True)
    evidence_document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    evidence_chunk_id: Mapped[str] = mapped_column(ForeignKey("text_chunks.id"), index=True)
    retrieval_score: Mapped[float] = mapped_column(Float)
    matched_terms: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_status: Mapped[str] = mapped_column(String(30), default="needs_review")
    rule_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    requirement: Mapped["Requirement"] = relationship(back_populates="evidence_matches")
    evidence_document: Mapped["Document"] = relationship()
    evidence_chunk: Mapped["TextChunk"] = relationship()
