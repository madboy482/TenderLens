from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AmendmentChange(Base):
    __tablename__ = "amendment_changes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    original_document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    amendment_document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    old_chunk_id: Mapped[str | None] = mapped_column(ForeignKey("text_chunks.id"), nullable=True)
    new_chunk_id: Mapped[str | None] = mapped_column(ForeignKey("text_chunks.id"), nullable=True)
    old_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    old_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    new_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    change_type: Mapped[str] = mapped_column(String(30))
    review_status: Mapped[str] = mapped_column(String(30), default="needs_review")
    affected_requirement_ids: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    workspace: Mapped["Workspace"] = relationship()
    original_document: Mapped["Document"] = relationship(foreign_keys=[original_document_id])
    amendment_document: Mapped["Document"] = relationship(foreign_keys=[amendment_document_id])
