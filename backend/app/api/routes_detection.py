from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.models.detection import DetectionEvent
from app.models.payload import WatermarkPayload
from app.models.report import ForensicReport
from app.models.session import StreamSession
from app.schemas.forensics import DetectionResponse
from app.services.detection_service import detect_from_video
from app.services.local_store import write_json_record
from app.services.payload_service import compact_payload
from app.services.report_service import create_forensic_report

router = APIRouter(prefix="/detection")


@router.post("/clip", response_model=DetectionResponse)
async def detect_clip(
    session_external_id: str = Form(...),
    clip: UploadFile = File(...),
    db: Session = Depends(get_db),
):
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

    compact = compact_payload(payload_record.payload_json, payload_record.hmac_signature)

    uploads_dir = settings.samples_dir / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    clip_path = uploads_dir / clip.filename
    clip_bytes = await clip.read()
    clip_path.write_bytes(clip_bytes)

    result = detect_from_video(str(clip_path), known_compact_payload=compact, sample_stride=30)

    detection = DetectionEvent(
        session_id=session.id,
        source_clip_name=clip.filename,
        decoded_payload=result["decoded_payload"],
        verification_status=result["verification_status"],
        confidence_score=result["confidence_score"],
    )
    db.add(detection)
    db.flush()

    report_dir = settings.samples_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"forensic_report_{detection.id}.pdf"

    response_data = {
        "subscriber_name": session.subscriber_name,
        "user_id": session.user_id,
        "device_id": session.device_id,
        "ip_hash": session.ip_hash,
        "leak_timestamp": datetime.now(timezone.utc).isoformat(),
        "session_external_id": session.session_external_id,
        "verification_status": result["verification_status"],
        "confidence_score": result["confidence_score"],
        "decoded_payload": result["decoded_payload"],
    }
    create_forensic_report(str(report_path), response_data)

    report_entry = ForensicReport(
        session_id=session.id,
        detection_id=detection.id,
        report_path=str(report_path),
    )
    db.add(report_entry)
    db.commit()

    write_json_record(
        "detections",
        detection.id,
        {
            "id": detection.id,
            "session_id": detection.session_id,
            "source_clip_name": detection.source_clip_name,
            "decoded_payload": detection.decoded_payload,
            "verification_status": detection.verification_status,
            "confidence_score": detection.confidence_score,
            "detected_at": detection.detected_at.isoformat() if detection.detected_at else None,
            "report_path": str(report_path),
        },
    )

    return DetectionResponse(**response_data, report_path=str(report_path))
