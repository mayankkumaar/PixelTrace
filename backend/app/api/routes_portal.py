from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.detection import DetectionEvent
from app.models.payload import WatermarkPayload
from app.models.report import ForensicReport
from app.models.session import StreamSession
from app.schemas.forensics import DetectionResponse, ViewerEncodeResponse
from app.services.detection_service import detect_from_video, embed_video
from app.services.local_store import write_json_record
from app.services.payload_service import build_payload, compact_payload
from app.services.report_service import create_forensic_report

router = APIRouter(prefix="/portal")

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}


def _safe_video_ext(file_name: str) -> str:
    ext = Path(file_name or "").suffix.lower()
    return ext if ext in ALLOWED_VIDEO_EXTENSIONS else ".mp4"


def _safe_video_name(file_name: str) -> str:
    return Path(file_name).name


def _raw_video_path(file_name: str) -> Path:
    return settings.samples_dir / "uploads" / _safe_video_name(file_name)


def _save_session_records(session: StreamSession, payload: WatermarkPayload) -> None:
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
        payload.id,
        {
            "id": payload.id,
            "session_id": payload.session_id,
            "payload_json": payload.payload_json,
            "hmac_signature": payload.hmac_signature,
            "created_at": payload.created_at.isoformat() if payload.created_at else None,
        },
    )


@router.post("/viewer/encode", response_model=ViewerEncodeResponse)
async def encode_for_viewer(
    viewer_login_id: str = Form(...),
    source_video: UploadFile | None = File(default=None),
    use_project_raw_video: bool = Form(default=True),
    project_raw_video_name: str = Form(default="pirated_match.mp4"),
    subscriber_name: str | None = Form(default=None),
    device_id: str | None = Form(default=None),
    ip_address: str = Form(default="127.0.0.1"),
    segment_id: str = Form(default="seg_01"),
    db: Session = Depends(get_db),
):
    login_id = viewer_login_id.strip()
    if not login_id:
        raise HTTPException(status_code=400, detail="viewer_login_id is required")

    source_video_label = ""
    source_path: Path | None = None

    session_external_id = f"sess_{uuid.uuid4().hex[:12]}"
    final_subscriber_name = (subscriber_name or login_id).strip() or login_id
    final_device_id = (device_id or f"web_{uuid.uuid4().hex[:8]}").strip() or f"web_{uuid.uuid4().hex[:8]}"
    final_ip_address = ip_address.strip() or "127.0.0.1"
    final_segment_id = segment_id.strip() or "seg_01"

    payload_json, signature = build_payload(
        user_id=login_id,
        device_id=final_device_id,
        session_external_id=session_external_id,
        ip_address=final_ip_address,
        segment_id=final_segment_id,
    )

    session = StreamSession(
        user_id=login_id,
        subscriber_name=final_subscriber_name,
        device_id=final_device_id,
        ip_hash=payload_json["ip_hash"],
        segment_id=final_segment_id,
        session_external_id=session_external_id,
    )
    db.add(session)
    db.flush()

    wm_payload = WatermarkPayload(
        session_id=session.id,
        payload_json=payload_json,
        hmac_signature=signature,
    )
    db.add(wm_payload)
    db.flush()

    uploads_dir = settings.samples_dir / "uploads" / "viewer_source"
    encoded_dir = settings.samples_dir / "encoded"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    encoded_dir.mkdir(parents=True, exist_ok=True)

    if use_project_raw_video or source_video is None:
        selected_raw_name = _safe_video_name(project_raw_video_name) or "pirated_match.mp4"
        candidate_path = _raw_video_path(selected_raw_name)
        if not candidate_path.exists():
            db.rollback()
            raise HTTPException(
                status_code=404,
                detail=f"Project raw video not found: {candidate_path}",
            )
        source_path = candidate_path
        source_video_label = selected_raw_name
        ext = _safe_video_ext(selected_raw_name)
    else:
        source_bytes = await source_video.read()
        if not source_bytes:
            db.rollback()
            raise HTTPException(status_code=400, detail="Uploaded source video is empty")
        ext = _safe_video_ext(source_video.filename or "")
        source_name = f"source_{session_external_id}{ext}"
        source_path = uploads_dir / source_name
        source_path.write_bytes(source_bytes)
        source_video_label = source_video.filename or source_name

    encoded_name = f"encoded_{session_external_id}.mp4"
    encoded_path = encoded_dir / encoded_name

    compact = compact_payload(payload_json, signature)
    try:
        embedding_summary = embed_video(
            input_path=str(source_path),
            output_path=str(encoded_path),
            compact_payload_str=compact,
            window_size=settings.watermark_window,
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to encode video: {exc}") from exc

    db.commit()
    db.refresh(session)
    db.refresh(wm_payload)
    _save_session_records(session, wm_payload)

    return ViewerEncodeResponse(
        session_external_id=session_external_id,
        viewer_login_id=login_id,
        subscriber_name=final_subscriber_name,
        device_id=final_device_id,
        source_video_used=source_video_label,
        encoded_video_name=encoded_name,
        encoded_video_download_url=f"/api/v1/portal/viewer/encoded/{encoded_name}",
        embedding_summary=embedding_summary,
    )


@router.get("/viewer/raw-videos")
def list_raw_videos():
    raw_dir = settings.samples_dir / "uploads"
    raw_dir.mkdir(parents=True, exist_ok=True)
    videos = sorted(
        [p.name for p in raw_dir.iterdir() if p.is_file() and p.suffix.lower() in ALLOWED_VIDEO_EXTENSIONS]
    )
    return {"videos": videos}


@router.get("/viewer/raw/{video_name}")
def get_raw_video(video_name: str):
    raw_path = _raw_video_path(video_name)
    if not raw_path.exists():
        raise HTTPException(status_code=404, detail="Raw video not found")
    return FileResponse(path=str(raw_path), media_type="video/mp4", filename=raw_path.name)


@router.get("/viewer/encoded/{video_name}")
def download_encoded_video(video_name: str):
    encoded_path = settings.samples_dir / "encoded" / video_name
    if not encoded_path.exists():
        raise HTTPException(status_code=404, detail="Encoded video not found")
    return FileResponse(
        path=str(encoded_path),
        media_type="video/mp4",
        filename=video_name,
    )


@router.post("/broadcaster/decode", response_model=DetectionResponse)
async def decode_for_broadcaster(
    encoded_video: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    clip_bytes = await encoded_video.read()
    if not clip_bytes:
        raise HTTPException(status_code=400, detail="Uploaded encoded video is empty")

    # Limiting to latest session to avoid false matches.
    # Previously, detection ran against ALL sessions, which caused
    # cross-session payload collisions and degraded confidence (~50%).
    # Now we only match against the most recent viewer session.
    source_row = (
        db.query(StreamSession, WatermarkPayload)
        .join(WatermarkPayload, WatermarkPayload.session_id == StreamSession.id)
        .order_by(StreamSession.started_at.desc(), WatermarkPayload.created_at.desc())
        .first()
    )
    if not source_row:
        raise HTTPException(status_code=404, detail="No viewer sessions found to match against")

    uploads_dir = settings.samples_dir / "uploads" / "broadcaster_uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    ext = _safe_video_ext(encoded_video.filename or "")
    clip_name = f"broadcaster_{uuid.uuid4().hex[:16]}{ext}"
    clip_path = uploads_dir / clip_name
    clip_path.write_bytes(clip_bytes)

    # Unpack the single most-recent session + payload
    session, payload = source_row
    compact = compact_payload(payload.payload_json, payload.hmac_signature)
    result = detect_from_video(str(clip_path), known_compact_payload=compact, sample_stride=1)
    verified = result["verification_status"] == "verified"
    score = float(result["confidence_score"])

    best_match = {
        "session": session,
        "payload": payload,
        "result": result,
        "verified": verified,
        "score": score,
    }


    matched_session: StreamSession = best_match["session"]
    matched_payload: WatermarkPayload = best_match["payload"]
    result = best_match["result"]
    decoded_payload = result["decoded_payload"] or matched_payload.payload_json
    # Exact session match ensures correct attribution.
    # Confidence indicates signal strength, not correctness.
    decoded_session = decoded_payload.get("session_id") if isinstance(decoded_payload, dict) else None
    confidence_score = float(result["confidence_score"])

    if decoded_session and decoded_session == matched_session.session_external_id:
        # Session ID extracted from watermark matches the stored session
        if confidence_score >= 0.8:
            verification_status = "verified_high"
        elif confidence_score >= 0.5:
            verification_status = "verified_medium"
        else:
            verification_status = "verified_low"
    elif result["verification_status"] == "verified":
        # HMAC verification passed (payload integrity confirmed)
        if confidence_score >= 0.8:
            verification_status = "verified_high"
        else:
            verification_status = "verified_medium"
    else:
        verification_status = "unverified"

    detection = DetectionEvent(
        session_id=matched_session.id,
        source_clip_name=clip_name,
        decoded_payload=decoded_payload,
        verification_status=verification_status,
        confidence_score=float(result["confidence_score"]),
    )
    db.add(detection)
    db.flush()

    report_dir = settings.samples_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"forensic_report_{detection.id}.pdf"

    response_data = {
        "subscriber_name": matched_session.subscriber_name,
        "user_id": matched_session.user_id,
        "device_id": matched_session.device_id,
        "ip_hash": matched_session.ip_hash,
        "leak_timestamp": datetime.now(timezone.utc).isoformat(),
        "session_external_id": matched_session.session_external_id,
        "verification_status": verification_status,
        "confidence_score": float(result["confidence_score"]),
        "decoded_payload": decoded_payload,
    }
    create_forensic_report(str(report_path), response_data)

    report_entry = ForensicReport(
        session_id=matched_session.id,
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
            "session_external_id": matched_session.session_external_id,
        },
    )

    return DetectionResponse(
        **response_data,
        report_path=str(report_path),
    )
