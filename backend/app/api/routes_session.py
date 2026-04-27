from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.payload import WatermarkPayload
from app.models.session import StreamSession
from app.schemas.forensics import PayloadOut, SessionCreate, SessionOut
from app.services.local_store import write_json_record
from app.services.payload_service import build_payload

router = APIRouter(prefix="/sessions")


@router.post("", response_model=SessionOut)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    ip_hash_payload, signature = build_payload(
        user_id=payload.user_id,
        device_id=payload.device_id,
        session_external_id=payload.session_external_id,
        ip_address=payload.ip_address,
        segment_id=payload.segment_id,
    )

    existing = (
        db.query(StreamSession)
        .filter(StreamSession.session_external_id == payload.session_external_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Session ID already exists")

    session = StreamSession(
        user_id=payload.user_id,
        subscriber_name=payload.subscriber_name,
        device_id=payload.device_id,
        ip_hash=ip_hash_payload["ip_hash"],
        segment_id=payload.segment_id,
        session_external_id=payload.session_external_id,
    )
    db.add(session)
    db.flush()

    wm_payload = WatermarkPayload(
        session_id=session.id,
        payload_json=ip_hash_payload,
        hmac_signature=signature,
    )
    db.add(wm_payload)
    db.commit()
    db.refresh(session)

    write_json_record(
        "sessions",
        session.id,
        {
            "id": session.id,
            "session_external_id": session.session_external_id,
            "user_id": session.user_id,
            "subscriber_name": session.subscriber_name,
            "device_id": session.device_id,
            "ip_hash": session.ip_hash,
            "segment_id": session.segment_id,
            "started_at": session.started_at.isoformat() if session.started_at else None,
        },
    )
    write_json_record(
        "payloads",
        wm_payload.id,
        {
            "id": wm_payload.id,
            "session_id": wm_payload.session_id,
            "payload_json": wm_payload.payload_json,
            "hmac_signature": wm_payload.hmac_signature,
            "created_at": wm_payload.created_at.isoformat() if wm_payload.created_at else None,
        },
    )

    return session


@router.get("", response_model=list[SessionOut])
def list_sessions(limit: int = 100, db: Session = Depends(get_db)):
    safe_limit = max(1, min(limit, 1000))
    sessions = db.query(StreamSession).order_by(StreamSession.started_at.desc()).limit(safe_limit).all()
    return sessions


@router.get("/{session_external_id}/payload", response_model=PayloadOut)
def get_payload(session_external_id: str, db: Session = Depends(get_db)):
    session = (
        db.query(StreamSession)
        .filter(StreamSession.session_external_id == session_external_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    payload_record = (
        db.query(WatermarkPayload)
        .filter(WatermarkPayload.session_id == session.id)
        .order_by(WatermarkPayload.created_at.desc())
        .first()
    )
    if not payload_record:
        raise HTTPException(status_code=404, detail="Payload not found")

    return PayloadOut(
        session_external_id=session_external_id,
        payload=payload_record.payload_json,
        hmac_signature=payload_record.hmac_signature,
    )
