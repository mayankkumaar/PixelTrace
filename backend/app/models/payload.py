from __future__ import annotations

import uuid

from sqlalchemy import DateTime, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class WatermarkPayload(Base):
    __tablename__ = "watermark_payloads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("stream_sessions.id"), index=True)
    payload_json: Mapped[dict] = mapped_column(JSON)
    hmac_signature: Mapped[str] = mapped_column(String(255), index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session = relationship("StreamSession", back_populates="payloads")
