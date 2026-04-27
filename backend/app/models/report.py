from __future__ import annotations

import uuid

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ForensicReport(Base):
    __tablename__ = "forensic_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("stream_sessions.id"), index=True)
    detection_id: Mapped[str] = mapped_column(String(36), ForeignKey("detection_events.id"), index=True)
    report_path: Mapped[str] = mapped_column(String(512))
    generated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session = relationship("StreamSession", back_populates="reports")
