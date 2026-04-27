from __future__ import annotations

import uuid

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class DetectionEvent(Base):
    __tablename__ = "detection_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("stream_sessions.id"), nullable=True, index=True)
    source_clip_name: Mapped[str] = mapped_column(String(255))
    decoded_payload: Mapped[dict] = mapped_column(JSON)
    verification_status: Mapped[str] = mapped_column(String(64), index=True)
    confidence_score: Mapped[float] = mapped_column(Float)
    detected_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session = relationship("StreamSession", back_populates="detections")
