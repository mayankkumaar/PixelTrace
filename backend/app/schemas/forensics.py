from datetime import datetime

from pydantic import BaseModel


class SessionCreate(BaseModel):
    user_id: str
    subscriber_name: str
    device_id: str
    session_external_id: str
    ip_address: str
    segment_id: str


class SessionOut(BaseModel):
    session_external_id: str
    user_id: str
    subscriber_name: str
    device_id: str
    ip_hash: str
    segment_id: str
    started_at: datetime

    class Config:
        from_attributes = True


class PayloadOut(BaseModel):
    session_external_id: str
    payload: dict
    hmac_signature: str


class ViewerEncodeResponse(BaseModel):
    session_external_id: str
    viewer_login_id: str
    subscriber_name: str
    device_id: str
    source_video_used: str
    encoded_video_name: str
    encoded_video_download_url: str
    embedding_summary: dict


class DetectionResponse(BaseModel):
    subscriber_name: str | None
    user_id: str | None
    device_id: str | None
    ip_hash: str | None
    leak_timestamp: str
    session_external_id: str | None
    verification_status: str
    confidence_score: float
    decoded_payload: dict
    report_path: str | None = None
