from __future__ import annotations

import uuid

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class StreamSession(Base):
    __tablename__ = "stream_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    subscriber_name: Mapped[str] = mapped_column(String(255))
    device_id: Mapped[str] = mapped_column(String(128), index=True)
    ip_hash: Mapped[str] = mapped_column(String(255), index=True)
    segment_id: Mapped[str] = mapped_column(String(128), index=True)
    session_external_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    started_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    payloads = relationship("WatermarkPayload", back_populates="session", cascade="all, delete-orphan")
    detections = relationship("DetectionEvent", back_populates="session", cascade="all, delete-orphan")
    reports = relationship("ForensicReport", back_populates="session", cascade="all, delete-orphan")
