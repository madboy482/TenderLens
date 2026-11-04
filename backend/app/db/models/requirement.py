from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Requirement(Base):
    __tablename__ = "requirements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    source_document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    source_chunk_id: Mapped[str | None] = mapped_column(
        ForeignKey("text_chunks.id"), nullable=True, index=True
    )
    source_page_start: Mapped[int] = mapped_column(Integer)
    source_page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_clause_text: Mapped[str] = mapped_column(Text)
    normalized_text: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(40), default="other")
    requirement_type: Mapped[str] = mapped_column(String(40), default="documentary")
    mandatory_status: Mapped[str] = mapped_column(String(20), default="unknown")
    extracted_value: Mapped[str | None] = mapped_column(String(200), nullable=True)
    normalized_value: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(40), nullable=True)
    conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_method: Mapped[str] = mapped_column(String(20), default="rule")
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    review_required: Mapped[bool] = mapped_column(Boolean, default=True)
    suggested_status: Mapped[str] = mapped_column(String(30), default="needs_review")
    confirmed_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    workspace: Mapped["Workspace"] = relationship(back_populates="requirements")
    source_document: Mapped["Document"] = relationship()
    source_chunk: Mapped["TextChunk | None"] = relationship()
    evidence_matches: Mapped[list["EvidenceMatch"]] = relationship(
        back_populates="requirement", cascade="all, delete-orphan"
    )
